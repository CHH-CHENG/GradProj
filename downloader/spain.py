"""西班牙省份 Sentinel-2 采集（IFN4 研究）

省份与时间窗（与 IFN4 野外调查年匹配或最接近可用年份）：
  leon   : IFN4 2019 → S2 2019 生长季（第一步重点优先）
  burgos : IFN4 2018 → S2 2018 生长季
  lugo   : IFN4 2009（无同期 S2，2015 年才有）→ 暂用 2016 生长季

策略：全省矩形范围查询 → 按 tile 去重（每 tile 取云量最少一期）→ 下载 L2A
输出：data/Sentinel2/zip/Spain_IFN4/<省>/<UUID>.zip

用法（在项目根运行）：
  python -m downloader.spain --dry-run leon    # 仅查询预览
  python -m downloader.spain leon              # 下载 León（优先）
  python -m downloader.spain all               # 下载三省（约 23 GB）
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(errors="replace")   # 兼容 Windows GBK 控制台
except Exception:
    pass

from downloader.copernicus import (dedup_by_tile, download_product, get_token,
                                   search_products_bbox)

# 省份定义：bbox = (lon_min, lat_min, lon_max, lat_max)，时间窗按 IFN4 调查年
REGIONS = {
    "leon": {"name": "León (IFN4 2019)",
             "bbox": (-7.10, 42.05, -4.72, 43.26),
             "start": "2019-06-01", "end": "2019-09-15"},
    "burgos": {"name": "Burgos (IFN4 2018)",
               "bbox": (-4.40, 41.40, -2.47, 43.24),
               "start": "2018-06-01", "end": "2018-09-15"},
    "lugo": {"name": "Lugo (IFN4 2009；S2 用 2016)",
             "bbox": (-8.03, 42.28, -6.75, 43.79),
             "start": "2016-06-01", "end": "2016-09-15"},
}

OUT_ROOT = ROOT / "data" / "Sentinel2" / "zip" / "Spain_IFN4"
CLOUD = 30


def run_region(key, dry_run=False):
    reg = REGIONS[key]
    lo1, la1, lo2, la2 = reg["bbox"]
    print(f"\n{'=' * 72}")
    print(f"区域: {reg['name']}  范围 [{lo1},{la1}]-[{lo2},{la2}]  时间 {reg['start']} ~ {reg['end']}")
    products = search_products_bbox(lo1, la1, lo2, la2, reg["start"], reg["end"], CLOUD)
    selected = dedup_by_tile(products)
    print(f"按 tile 去重后选择 {len(selected)} 个产品：")
    for p in sorted(selected, key=lambda x: x["tile"]):
        cl = f"{p['cloud']:.1f}%" if p["cloud"] is not None else "?"
        print(f"  {p['tile']:8s} {p['date']}  云量 {cl:>6s}  {p['name']}")

    if dry_run:
        print("[DRY-RUN] 未下载")
        return selected

    out_dir = OUT_ROOT / key
    for p in selected:
        download_product(p["id"], get_token, out_dir=str(out_dir))
    print(f"区域 {key} 下载完成 -> {out_dir}")
    return selected


def main():
    argv = sys.argv[1:]
    dry = "--dry-run" in argv
    targets = [a for a in argv if not a.startswith("-")]
    if not targets:
        print(__doc__)
        return
    if targets[0] == "all":
        keys = list(REGIONS)
    else:
        keys = [t for t in targets if t in REGIONS]
        if not keys:
            print(f"未知区域: {targets}  可选: {list(REGIONS)} 或 all\n")
            print(__doc__)
            return
    for k in keys:
        run_region(k, dry)


if __name__ == "__main__":
    main()
