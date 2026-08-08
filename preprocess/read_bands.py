"""Sentinel-2 SAFE 波段读取与重采样（统一空间分辨率）

- 支持 L2A（IMG_DATA 下按 R10m/R20m/R60m 分目录）与 L1C（平铺）
- 将 20m/60m 波段双线性重采样到目标分辨率（默认 10m）
- 输出内存中的多波段栈 (bands, H, W)，float32
"""
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling

# 各波段原始空间分辨率（m）
BAND_RES = {
    "B01": 60, "B02": 10, "B03": 10, "B04": 10, "B05": 20,
    "B06": 20, "B07": 20, "B08": 10, "B8A": 20, "B09": 60,
    "B10": 60, "B11": 20, "B12": 20,
}

DEFAULT_BANDS = ["B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B11", "B12"]


def find_granule(safe_dir: Path) -> Path:
    """定位 SAFE 内的第一个 GRANULE 目录"""
    granules = sorted((Path(safe_dir) / "GRANULE").glob("*/"))
    if not granules:
        raise FileNotFoundError(f"未找到 GRANULE 目录: {safe_dir}")
    return granules[0]


def build_band_path_map(img_data_dir: Path) -> dict:
    """
    扫描 IMG_DATA，返回 {band: 文件路径}。

    L2A 文件名形如 T48SXD_20230605T033541_B02_10m.jp2（分 R10m/R20m/R60m 目录），
    L1C 文件名形如 T48SXC_20230605T033541_B02.jp2（平铺）。
    同一波段存在多分辨率版本时优先取高分辨率（目录字母序靠前）。
    """
    mapping = {}
    img_data_dir = Path(img_data_dir)
    search_dirs = [img_data_dir] + sorted(p for p in img_data_dir.iterdir() if p.is_dir())
    for d in search_dirs:
        for f in d.glob("*.jp2"):
            parts = f.stem.split("_")
            band = parts[-2] if len(parts) >= 2 else parts[-1]
            if band.startswith("B") and band not in mapping:
                mapping[band] = f
    return mapping


def read_bands(safe_dir, bands=DEFAULT_BANDS, target_res=10,
               scale_reflectance=True, bounds=None):
    """
    读取 SAFE 指定波段，并统一重采样到 target_res。

    Parameters
    ----------
    safe_dir : str / Path
        SAFE 产品目录
    bands : list[str]
        要读取的波段（如 B02, B8A）
    target_res : int
        统一重采样分辨率（m）
    scale_reflectance : bool
        是否将反射率 DN(0~10000) 缩放为 0~1
    bounds : tuple / None
        只读该地理范围 (minx, miny, maxx, maxy)（影像 CRS 下）。
        遥感 tile 很大，按研究区窗口读取可大幅节省内存与时间；
        None 表示读取整个 tile。

    Returns
    -------
    data : np.ndarray, shape (n_bands, H, W), dtype float32
    transform : rasterio.Affine
    crs : rasterio.crs.CRS
    names : list[str]  # 实际读取到的波段名（与 data 第一维对应）
    """
    safe_dir = Path(safe_dir)
    granule = find_granule(safe_dir)
    img_data = granule / "IMG_DATA"
    if not img_data.exists():
        raise FileNotFoundError(f"无 IMG_DATA 目录: {img_data}")

    mapping = build_band_path_map(img_data)

    # 参考网格：目标分辨率的第一个可用波段；否则回退到任一可用波段
    ref_band = next((b for b in bands
                     if BAND_RES.get(b) == target_res and b in mapping), None)
    if ref_band is None:
        ref_band = next((b for b in bands if b in mapping), None)
    if ref_band is None:
        raise FileNotFoundError(f"所需波段 {bands} 在 {safe_dir.name} 中均不存在")

    with rasterio.open(mapping[ref_band]) as ref:
        out_crs = ref.crs
        if bounds is not None:
            # 参考波段上的窗口（整数像素）
            wnd = rasterio.windows.from_bounds(*bounds, transform=ref.transform)
            wnd = wnd.round_lengths().round_offsets()
            out_transform = rasterio.windows.transform(wnd, ref.transform)
            out_shape = (int(wnd.height), int(wnd.width))
        else:
            out_transform = ref.transform
            out_shape = (ref.height, ref.width)

    arrays, names = [], []
    for b in bands:
        if b not in mapping:
            print(f"  跳过缺失波段: {b}")
            continue
        with rasterio.open(mapping[b]) as src:
            if bounds is not None:
                # 每个源波段按其自身 transform 计算同一地理范围的窗口
                src_wnd = rasterio.windows.from_bounds(*bounds, transform=src.transform)
                src_wnd = src_wnd.round_lengths().round_offsets()
                src_wnd = src_wnd.intersection(
                    rasterio.windows.Window(0, 0, src.width, src.height))
                if src_wnd.width <= 0 or src_wnd.height <= 0:
                    print(f"  跳过（与研究区无交集）: {b}")
                    continue
                arr = src.read(1, window=src_wnd, out_shape=out_shape,
                               resampling=Resampling.bilinear)
            elif (src.height, src.width) == out_shape:
                arr = src.read(1)
            else:
                arr = src.read(1, out_shape=out_shape, resampling=Resampling.bilinear)
        arrays.append(arr.astype(np.float32))
        names.append(b)

    data = np.stack(arrays, axis=0)

    if scale_reflectance:
        # L2A 反射率 DN 范围 0~10000 → 反射率 0~1
        data = data / 10000.0

    return data, out_transform, out_crs, names
