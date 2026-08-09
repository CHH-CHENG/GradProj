"""芬兰典型区域 Sentinel-2 影像采集

两个典型区域（基于 MS-NFI 树种蓄积量分析识别）：
- pure_pine_lapland : 纯林典型区（拉普兰纯松林）   中心 (27.20E, 68.76N)
- mixed_central     : 混交林典型区               中心 (24.97E, 66.06N)

时间窗：2023-07-01 ~ 2023-08-10（与 MS-NFI 2023 标签时点匹配）
云量  ：<30%（芬兰多云）
策略  ：整 tile 下载原始 SAFE，每 tile 取云量最少一期（无重复时相）

用法：
  python download_finland.py --dry-run   # 仅查询并预览待下载产品
  python download_finland.py             # 执行下载
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from downloader.copernicus import search_and_download_region, search_products_bbox, dedup_by_tile

START_DATE = "2023-07-01"
END_DATE = "2023-08-10"
CLOUD = 30

# 每个区域：中心经纬度 + 查询半宽（度）-> 生成 WGS84 矩形
REGIONS = [
    {
        "name": "pure_pine_lapland",   # 纯林典型区（拉普兰纯松林）
        "lon": 27.20, "lat": 68.76,
        "half": 0.35,
    },
    {
        "name": "mixed_central",       # 混交林典型区
        "lon": 24.97, "lat": 66.06,
        "half": 0.35,
    },
]


def main():
    dry_run = "--dry-run" in sys.argv
    for reg in REGIONS:
        print("=" * 72)
        print(f"区域: {reg['name']}  中心 ({reg['lon']}E, {reg['lat']}N)  矩形 ±{reg['half']}°")
        lon_min = reg["lon"] - reg["half"]
        lon_max = reg["lon"] + reg["half"]
        lat_min = reg["lat"] - reg["half"]
        lat_max = reg["lat"] + reg["half"]
        if dry_run:
            products = search_products_bbox(lon_min, lat_min, lon_max, lat_max,
                                            START_DATE, END_DATE, CLOUD)
            selected = dedup_by_tile(products)
            print(f"[DRY-RUN] 按 tile 去重后 {len(selected)} 个产品：")
            for p in sorted(selected, key=lambda x: x["tile"]):
                print(f"  {p['date']} | {p['tile']} | 云量 {p['cloud']} | {p['name']}")
        else:
            search_and_download_region(lon_min, lat_min, lon_max, lat_max,
                                       START_DATE, END_DATE, CLOUD)


if __name__ == "__main__":
    main()
