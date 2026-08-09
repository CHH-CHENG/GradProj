"""特征提取与样本构建：从研究区对齐栅格生成 samples.csv

样本单元：30m×30m 窗口（10m 网格下 3×3 像元），步长 30m（不重叠）
特征 X：S2 光谱（10 波段窗口均值）+ 植被指数（NDVI/EVI/NDWI/NDRE）+
        地形（高程/坡度/坡向，窗口均值）
标签 y：窗口中心 MS-NFI 蓄积量 GSV（m³/ha）
过滤：窗口中心 GSV 为 nodata（非林地）剔除；窗口内 S2 无有效像元剔除

输出：data/feature/samples.csv
用法：python -m feature.extract
"""
import sys
from pathlib import Path

import numpy as np
import rasterio
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from preprocess.finland_study import load_config, output_grid

BAND_NAMES = ["B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B11", "B12"]
GSV_NODATA = 32767.0
DEM_NODATA = -9999.0


def calc_indices(win):  # win: (n, 10) 窗口均值
    b2, b3, b4, b5, b6, b7, b8, b8a, b11, b12 = [win[:, i] for i in range(10)]
    eps = 1e-8
    ndvi = (b8 - b4) / (b8 + b4 + eps)
    evi = 2.5 * (b8 - b4) / (b8 + 6 * b4 - 7.5 * b2 + 1 + eps)
    ndwi = (b3 - b8) / (b3 + b8 + eps)
    ndre = (b8a - b5) / (b8a + b5 + eps)
    return ndvi, evi, ndwi, ndre


def compute_slope_aspect(dem, res=10.0):
    """由 DEM 计算坡度(°)与坡向(°)"""
    dzdy, dzdx = np.gradient(dem, res, res)   # axis0=y, axis1=x
    slope = np.degrees(np.arctan(np.hypot(dzdx, dzdy)))
    aspect = np.degrees(np.arctan2(-dzdx, dzdy)) % 360.0
    return slope, aspect


def window_mean_3x3(a):
    """a:(H,W) → 每 3×3 块均值 (nw, nw)；nan 敏感用 nanmean"""
    H, W = a.shape
    nw = H // 3
    blk = a[:nw * 3, :nw * 3].reshape(nw, 3, nw, 3)
    with np.errstate(all="ignore"):
        return np.nanmean(blk, axis=(1, 3))


def load_region_data(cfg, region):
    study_root = Path(cfg["paths"]["study_root"])
    roi_root = Path(cfg["paths"]["roi_root"])
    rid = region["id"]

    with rasterio.open(roi_root / f"{rid}_S2_10m_3067.tif") as ds:
        s2 = ds.read().astype(np.float32)          # (10, H, W)
        transform = ds.transform
    with rasterio.open(study_root / f"{rid}_GSV_10m_3067.tif") as ds:
        gsv = ds.read(1).astype(np.float32)
    with rasterio.open(study_root / f"{rid}_DEM_10m_3067.tif") as ds:
        dem = ds.read(1).astype(np.float32)

    # DEM nodata → nan（用于坡度/均值计算）
    dem[dem == DEM_NODATA] = np.nan

    H, W = gsv.shape
    nw = H // 3
    H3, W3 = nw * 3, nw * 3            # 截到 3 的倍数（30m 窗口可整除）
    s2 = s2[:, :H3, :W3]
    gsv = gsv[:H3, :W3]
    dem = dem[:H3, :W3]

    # ---- 窗口聚合 ----
    s2w = np.stack([window_mean_3x3(s2[i]) for i in range(s2.shape[0])], axis=0)  # (10,nw,nw)
    gsv_center = gsv.reshape(nw, 3, nw, 3)[:, 1, :, 1]                            # 窗口中心像元
    dem_w = window_mean_3x3(dem)
    slope_deg, aspect = compute_slope_aspect(dem)
    slope_w = window_mean_3x3(slope_deg)
    aspect_w = window_mean_3x3(aspect)

    # ---- 有效掩膜 ----
    gsv_ok = gsv_center != GSV_NODATA
    s2_ok = np.all(s2w != 0, axis=0)     # 所有波段窗口均有有效值
    valid = gsv_ok & s2_ok

    yy, xx = np.where(valid)
    n = len(yy)
    if n == 0:
        print(f"  {rid}: 无有效样本")
        return None

    feats = s2w[:, yy, xx].T                                   # (n, 10)
    ndvi, evi, ndwi, ndre = calc_indices(feats)
    demv = dem_w[yy, xx]
    slopev = slope_w[yy, xx]
    aspectv = aspect_w[yy, xx]
    y_label = gsv_center[yy, xx]
    rid_arr = np.full(n, rid)
    label_arr = np.full(n, region["label"])

    # 窗口中心坐标（EPSG:3067）
    cx = np.full(n, np.nan)
    cy = np.full(n, np.nan)
    for k in range(n):
        r, c = 3 * yy[k] + 1, 3 * xx[k] + 1
        cx[k], cy[k] = rasterio.transform.xy(transform, r, c)

    df = pd.DataFrame({
        "sample_id": [f"{rid}_{i}" for i in range(n)],
        "region_id": rid_arr,
        "label": label_arr,
        "x_3067": cx, "y_3067": cy,
        **{BAND_NAMES[i]: feats[:, i] for i in range(10)},
        "NDVI": ndvi, "EVI": evi, "NDWI": ndwi, "NDRE": ndre,
        "DEM_elev": demv, "DEM_slope": slopev, "DEM_aspect": aspectv,
        "GSV": y_label,
    })
    print(f"  {rid}: 有效样本 {n} 个")
    return df


def build_all(cfg=None):
    cfg = cfg or load_config()
    dfs = []
    for region in cfg["regions"]:
        df = load_region_data(cfg, region)
        if df is not None:
            dfs.append(df)
    if not dfs:
        raise RuntimeError("无样本生成")
    out = pd.concat(dfs, ignore_index=True)
    out_path = Path(cfg["paths"]["study_root"]).parent / "samples.csv"
    out.to_csv(out_path, index=False, float_format="%.4f")
    print(f"\n样本总数 {len(out)}，已写出 {out_path}")
    print(f"列: {list(out.columns)}")
    print(out["label"].value_counts().to_string())
    print(out["GSV"].describe().round(2).to_string())


if __name__ == "__main__":
    build_all()
