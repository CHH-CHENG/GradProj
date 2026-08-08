"""ROI 裁剪：研究区整幅 + 按样地（预留接口）

- 研究区：以配置中心点在影像 CRS 下做方形缓冲，裁剪整幅多波段栈
- 按样地：读取 plots 矢量（点自动缓冲 / 面直接用），逐个裁剪；文件未就位时跳过
- 主流程 process_sentinel2()：遍历 SAFE 下所有 L2A 产品
"""
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
import yaml
from rasterio.features import geometry_mask
from rasterio.warp import transform as warp_transform
from shapely.geometry import box

from .read_bands import DEFAULT_BANDS, build_band_path_map, BAND_RES, find_granule, read_bands

# 配置路径：基于本文件位置定位，避免依赖运行目录
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "preprocess.yaml"


def load_config(path=None):
    path = Path(path) if path else CONFIG_PATH
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def lonlat_to_crs(lon, lat, crs):
    """把经纬度点转换到目标 CRS（返回 x, y）"""
    x, y = warp_transform("EPSG:4326", crs, [lon], [lat])
    return x[0], y[0]


def make_research_polygon(lon, lat, half_size_m, crs):
    """研究区：以中心点(经纬度)在影像 CRS 下做方形缓冲"""
    cx, cy = lonlat_to_crs(lon, lat, crs)
    return box(cx - half_size_m, cy - half_size_m,
               cx + half_size_m, cy + half_size_m)


def crop_array(data, transform, crs, polygon, nodata=0.0):
    """
    对已读取的波段栈 (n, H, W) 按 polygon 做窗口裁剪 + 掩膜。

    polygon 需与影像位于同一 CRS。
    Returns (cropped, new_transform)
    """
    H, W = data.shape[1], data.shape[2]
    mask = geometry_mask([polygon], out_shape=(H, W), transform=transform, invert=True)

    rows, cols = np.where(mask)
    if len(rows) == 0:
        raise ValueError("多边形与影像无交集")

    r0, r1, c0, c1 = rows.min(), rows.max(), cols.min(), cols.max()
    cropped = np.where(mask[r0:r1 + 1, c0:c1 + 1],
                       data[:, r0:r1 + 1, c0:c1 + 1], nodata).astype(data.dtype)

    left, top = rasterio.transform.xy(transform, r0, c0, offset="ul")
    new_transform = rasterio.transform.from_origin(
        left, top, transform.a, abs(transform.e))

    return cropped, new_transform


def write_tif(data, transform, crs, names, out_path, nodata=0.0):
    """写出多波段 GeoTIFF（float32, deflate 压缩）"""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    profile = {
        "driver": "GTiff",
        "height": data.shape[1],
        "width": data.shape[2],
        "count": data.shape[0],
        "dtype": data.dtype,
        "crs": crs,
        "transform": transform,
        "nodata": nodata,
        "compress": "deflate",
    }
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(data)
        dst.descriptions = tuple(names)
    print(f"  写出: {out_path.name}  波段={len(names)}  shape={data.shape}")


def _get_reference_crs(safe_dir, bands, target_res):
    """轻量读取参考 CRS（用于构造研究区多边形），避免重复读整幅数据"""
    granule = find_granule(safe_dir)
    img_data = granule / "IMG_DATA"
    mapping = build_band_path_map(img_data)
    ref = next((b for b in bands
                if BAND_RES.get(b) == target_res and b in mapping), None) \
        or next((b for b in bands if b in mapping), None)
    if ref is None:
        raise FileNotFoundError(f"所需波段 {bands} 在 {safe_dir.name} 中均不存在")
    with rasterio.open(mapping[ref]) as src:
        return src.crs


def process_research_area(safe_dir, out_path, cfg):
    """研究区整幅：按研究区窗口读取波段 + 重采样 + 多边形裁剪并写出"""
    bands = cfg.get("bands", DEFAULT_BANDS)
    target_res = cfg.get("target_resolution", 10)
    scale = cfg.get("scale_reflectance", True)
    lon = cfg["research_center"]["lon"]
    lat = cfg["research_center"]["lat"]
    half = cfg.get("research_half_size_m", 5000)

    crs = _get_reference_crs(safe_dir, bands, target_res)
    polygon = make_research_polygon(lon, lat, half, crs)

    # 只读研究区范围，避免读取整个 tile
    data, transform, _, names = read_bands(safe_dir, bands, target_res, scale,
                                           bounds=tuple(polygon.bounds))
    cropped, new_transform = crop_array(data, transform, crs, polygon)
    write_tif(cropped, new_transform, crs, names, out_path)


def process_plots(safe_dir, plots_path, out_dir, cfg):
    """
    按样地逐个裁剪（预留接口）。

    样地矢量未就位时打印提示并跳过；就位后对每个样地
    （点 → 按 plot_buffer_m 缓冲，面 → 直接用）裁剪小图。
    """
    plots_path = Path(plots_path)
    if not plots_path.exists():
        print(f"  样地文件不存在，跳过按样地裁剪: {plots_path}")
        return []

    bands = cfg.get("bands", DEFAULT_BANDS)
    target_res = cfg.get("target_resolution", 10)
    scale = cfg.get("scale_reflectance", True)
    buffer_m = cfg.get("plot_buffer_m", 20)

    gdf = gpd.read_file(plots_path)
    data, transform, crs, names = read_bands(safe_dir, bands, target_res, scale)

    out_dir = Path(out_dir)
    out_paths = []
    for idx, row in gdf.iterrows():
        geom = row.geometry
        if geom is None:
            continue
        if geom.geom_type == "Point":
            geom = geom.buffer(buffer_m)
        geom = gpd.GeoSeries([geom], crs=gdf.crs).to_crs(crs).iloc[0]

        plot_id = row.get("plot_id", idx)
        try:
            cropped, new_transform = crop_array(data, transform, crs, geom)
            out_path = out_dir / f"{Path(safe_dir).name}_{plot_id}.tif"
            write_tif(cropped, new_transform, crs, names, out_path)
            out_paths.append(out_path)
        except ValueError as e:
            print(f"  样地 {plot_id} 裁剪失败: {e}")

    return out_paths


def process_sentinel2(safe_root="data/Sentinel2/SAFE",
                      out_root="data/Sentinel2/roi",
                      cfg=None):
    """主流程：遍历 SAFE 下所有 L2A 产品，执行研究区裁剪 + 按样地裁剪(预留)"""
    safe_root = Path(safe_root)
    out_root = Path(out_root)
    cfg = cfg or load_config()

    plots_path = cfg.get("plots", "data/inventory/plots.geojson")

    l2a_dirs = sorted(p for p in safe_root.glob("*/") if "MSIL2A" in p.name)
    print(f"发现 {len(l2a_dirs)} 个 L2A 产品")

    for safe_dir in l2a_dirs:
        out_path = out_root / f"{safe_dir.name}_roi.tif"
        if out_path.exists():
            print(f"跳过已处理: {safe_dir.name}")
            continue

        print(f"处理: {safe_dir.name}")
        try:
            process_research_area(safe_dir, out_path, cfg)
            process_plots(safe_dir, plots_path, out_root / safe_dir.name, cfg)
        except Exception as e:
            print(f"  失败: {safe_dir.name} - {e}")


if __name__ == "__main__":
    process_sentinel2()
