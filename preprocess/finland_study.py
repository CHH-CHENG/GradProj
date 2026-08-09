"""芬兰研究区数据准备：Sentinel-2 / MS-NFI 标签 / DEM 裁剪对齐

对每个研究区（纯林/混交），输出统一 EPSG:3067、10m 分辨率的研究区栅格：
  roi/Finland_PureMixed/<id>_S2_10m_3067.tif    多波段（B02~B12）反射率 0~1
  feature/finland_study/<id>_GSV_10m_3067.tif    蓄积量标签（m³/ha，MS-NFI 总蓄积量）
  feature/finland_study/<id>_DEM_10m_3067.tif    高程（m，N2000）

用法：python -m preprocess.finland_study
"""
import os
import sys
from pathlib import Path


def _ensure_gdal_env():
    """GDAL 运行环境自愈（JP2 解码插件 / GDAL_DATA / PATH），必须在 import rasterio 前调用"""
    prefix = Path(sys.prefix)
    if not os.environ.get("GDAL_DATA"):
        for p in (prefix / "Library/share/gdal", prefix / "etc/gdal", prefix / "share/gdal"):
            if p.is_dir():
                os.environ["GDAL_DATA"] = str(p)
                break
    plugins = prefix / "Library/lib/gdalplugins"
    if plugins.is_dir() and not os.environ.get("GDAL_DRIVER_PATH"):
        os.environ["GDAL_DRIVER_PATH"] = str(plugins)
    lib_bin = prefix / "Library/bin"
    if lib_bin.is_dir():
        cur = os.environ.get("PATH", "")
        if str(lib_bin) not in cur:
            os.environ["PATH"] = str(lib_bin) + os.pathsep + cur


_ensure_gdal_env()

import numpy as np
import rasterio
import yaml
from rasterio.crs import CRS
from rasterio.io import MemoryFile
from rasterio.merge import merge
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject, transform_bounds
from rasterio.warp import transform as warp_transform
from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from preprocess.read_bands import (DEFAULT_BANDS, BAND_RES, build_band_path_map,
                                   find_granule, read_bands)

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "finland_study.yaml"
OUT_CRS = "EPSG:3067"


def load_config(path=None):
    path = Path(path) if path else CONFIG_PATH
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def lonlat_to_crs(lon, lat, crs):
    x, y = warp_transform("EPSG:4326", crs, [lon], [lat])
    return x[0], y[0]


def region_rect_3067(region, half):
    """研究区矩形（EPSG:3067）"""
    cx, cy = lonlat_to_crs(region["center"]["lon"], region["center"]["lat"],
                           CRS.from_epsg(3067))
    return box(cx - half, cy - half, cx + half, cy + half)


def output_grid(polygon, res):
    minx, miny, maxx, maxy = polygon.bounds
    width = int(round((maxx - minx) / res))
    height = int(round((maxy - miny) / res))
    transform = from_origin(minx, maxy, res, res)
    return transform, width, height


def _write_tif(data, transform, names, out_path, nodata=0.0):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(names, str):
        names = [names]
    if data.ndim == 2:
        data = data[None, ...]
    if len(names) != data.shape[0]:
        names = names[:data.shape[0]]
    profile = dict(driver="GTiff", height=data.shape[1], width=data.shape[2],
                   count=data.shape[0], dtype=data.dtype, crs=CRS.from_epsg(3067),
                   transform=transform, nodata=nodata, compress="deflate")
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(data)
        dst.descriptions = tuple(names)
    print(f"  写出: {out_path.name}  shape={data.shape}  nodata={nodata}")


def _get_reference_crs(safe_dir, bands, target_res):
    granule = find_granule(safe_dir)
    mapping = build_band_path_map(granule / "IMG_DATA")
    ref = next((b for b in bands if BAND_RES.get(b) == target_res and b in mapping), None) \
        or next((b for b in bands if b in mapping), None)
    with rasterio.open(mapping[ref]) as src:
        return src.crs


# ---------------- Sentinel-2：多 tile 裁剪 + 拼接 ----------------
def prepare_region_s2(region, cfg, safe_dirs):
    """从覆盖研究区的 SAFE 读取波段，逐块重投影到统一 3067 网格，重叠区均值融合"""
    roi_root = Path(cfg["paths"]["roi_root"])
    out_path = roi_root / f"{region['id']}_S2_10m_3067.tif"
    if out_path.exists():
        print(f"  S2 已存在，跳过: {out_path.name}")
        return out_path

    bands = cfg.get("bands", DEFAULT_BANDS)
    target_res = cfg.get("target_resolution", 10)
    scale = cfg.get("scale_reflectance", True)
    poly = region_rect_3067(region, region["half_size_m"])
    dst_transform, dst_w, dst_h = output_grid(poly, target_res)

    out = np.zeros((len(bands), dst_h, dst_w), dtype=np.float32)
    count = np.zeros((dst_h, dst_w), dtype=np.uint8)
    names = None
    nblocks = 0

    for safe in safe_dirs:
        try:
            crs_src = _get_reference_crs(safe, bands, target_res)
            bounds_src = transform_bounds(OUT_CRS, crs_src, *poly.bounds)
            data, transform, _, names = read_bands(safe, bands, target_res, scale,
                                                   bounds=bounds_src)
            if data is None or data.size == 0 or data.shape[1] == 0:
                continue
            nb = data.shape[0]
            tmp = np.zeros((nb, dst_h, dst_w), dtype=np.float32)
            for i in range(nb):
                reproject(data[i], tmp[i],
                          src_transform=transform, src_crs=crs_src,
                          dst_transform=dst_transform, dst_crs=OUT_CRS,
                          src_nodata=0, dst_nodata=0,
                          resampling=Resampling.bilinear)
            valid = np.any(tmp != 0, axis=0)
            out[:, valid] += tmp[:, valid]
            count[valid] += 1
            nblocks += 1
            print(f"    读取块: {safe.name}  shape={data.shape}  有效{int(valid.sum())}px")
        except Exception as e:
            print(f"    跳过 {safe.name}: {e}")

    if nblocks == 0:
        raise RuntimeError(f"{region['id']} 无 SAFE 覆盖研究区")

    np.divide(out, count[None, ...], out=out, where=count[None, ...] > 0)
    out[:, count == 0] = 0.0   # 无覆盖区 → nodata 0
    _write_tif(out, dst_transform, names, out_path)
    return out_path


# ---------------- MS-NFI 蓄积量标签（16m → 10m）----------------
def prepare_region_label(region, cfg):
    src_path = Path(cfg["paths"]["msnfi_total"])
    study_root = Path(cfg["paths"]["study_root"])
    out_path = study_root / f"{region['id']}_GSV_10m_3067.tif"
    if out_path.exists():
        print(f"  标签已存在，跳过: {out_path.name}")
        return out_path

    target_res = cfg.get("target_resolution", 10)
    poly = region_rect_3067(region, region["half_size_m"])
    dst_transform, dst_w, dst_h = output_grid(poly, target_res)

    with rasterio.open(src_path) as src:
        wnd = rasterio.windows.from_bounds(*poly.bounds, transform=src.transform)
        wnd = wnd.round_offsets().round_lengths().intersection(
            rasterio.windows.Window(0, 0, src.width, src.height))
        data = src.read(1, window=wnd).astype(np.float32)
        src_transform = rasterio.windows.transform(wnd, src.transform)
        out = np.full((dst_h, dst_w), src.nodata, dtype=np.float32)
        reproject(data, out,
                  src_transform=src_transform, src_crs=src.crs,
                  dst_transform=dst_transform, dst_crs=OUT_CRS,
                  src_nodata=src.nodata, dst_nodata=src.nodata,
                  resampling=Resampling.nearest)
        nodata = src.nodata
    _write_tif(out, dst_transform, "GSV_m3_per_ha", out_path, nodata=nodata)
    return out_path


# ---------------- DEM：分块裁剪 + 拼接 ----------------
def prepare_region_dem(region, cfg):
    dem_root = Path(cfg["paths"]["dem_root"])
    study_root = Path(cfg["paths"]["study_root"])
    out_path = study_root / f"{region['id']}_DEM_10m_3067.tif"
    if out_path.exists():
        print(f"  DEM 已存在，跳过: {out_path.name}")
        return out_path

    target_res = cfg.get("target_resolution", 10)
    poly = region_rect_3067(region, region["half_size_m"])
    dem_nodata = -9999.0

    mems = []
    for tif in sorted(dem_root.rglob("*.tif")):
        with rasterio.open(tif) as src:
            sb = src.bounds
            pb = poly.bounds
            if (sb.right < pb[0] or sb.left > pb[2] or
                    sb.top < pb[1] or sb.bottom > pb[3]):
                continue   # 与研究区无交集
            wnd = rasterio.windows.from_bounds(*poly.bounds, transform=src.transform)
            wnd = wnd.round_offsets().round_lengths().intersection(
                rasterio.windows.Window(0, 0, src.width, src.height))
            if wnd.width <= 0 or wnd.height <= 0:
                continue
            data = src.read(1, window=wnd).astype(np.float32)
            src_transform = rasterio.windows.transform(wnd, src.transform)
            mem = MemoryFile()
            dst = mem.open(driver="GTiff", height=data.shape[0], width=data.shape[1],
                           count=1, dtype=data.dtype, crs=src.crs,
                           transform=src_transform, nodata=src.nodata)
            dst.write(data, 1)
            mems.append((mem, dst))
            print(f"    DEM 块: {tif.name}")

    if not mems:
        raise RuntimeError(f"{region['id']} 无 DEM 覆盖")
    dest, transform = merge([d for _, d in mems], bounds=poly.bounds, res=target_res,
                            nodata=dem_nodata, method="first")
    _write_tif(dest, transform, "elevation_m", out_path, nodata=dem_nodata)
    for m, _ in mems:
        m.close()
    return out_path


def prepare_all(cfg=None):
    cfg = cfg or load_config()
    safe_root = Path(cfg["paths"]["safe_root"])
    safe_dirs = sorted(p for p in safe_root.glob("*/") if "MSIL2A" in p.name)
    print(f"发现 {len(safe_dirs)} 个 L2A SAFE")
    for region in cfg["regions"]:
        print(f"\n=== 研究区: {region['id']} ({region['name']}) ===")
        prepare_region_s2(region, cfg, safe_dirs)
        prepare_region_label(region, cfg)
        prepare_region_dem(region, cfg)
    print("\n全部完成")


if __name__ == "__main__":
    prepare_all()
