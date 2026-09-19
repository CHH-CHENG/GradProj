"""估算西班牙省份 Sentinel-2 下载量（L2A，按 tile 去重，每 tile 一期）

查询 CDSE 目录服务（公开，无需认证），统计指定区域/时间窗/云量下
L2A 产品按 tile 去重后的总文件大小（GB）。

用法（在项目根运行）：python -m downloader.estimate
"""
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    sys.stdout.reconfigure(errors="replace")   # 兼容 Windows GBK 控制台
except Exception:
    pass

from downloader.copernicus import CATALOG_URL, _extract_cloud, _extract_tile


def query_region(lon_min, lat_min, lon_max, lat_max, start, end, cloud=30, top=1000):
    wkt = (f"POLYGON(({lon_min} {lat_min},{lon_max} {lat_min},"
           f"{lon_max} {lat_max},{lon_min} {lat_max},{lon_min} {lat_min}))")
    q = (
        f"$filter=Collection/Name eq 'SENTINEL-2' "
        f"and OData.CSC.Intersects(area=geography'SRID=4326;{wkt}') "
        f"and ContentDate/Start ge {start}T00:00:00.000Z "
        f"and ContentDate/Start le {end}T23:59:59.999Z "
        f"and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' "
        f"and att/OData.CSC.DoubleAttribute/Value lt {cloud})"
        f"&$orderby=ContentDate/Start asc&$top={top}&$expand=Attributes"
    )
    r = requests.get(f"{CATALOG_URL}?{q}")
    r.raise_for_status()
    products = []
    for item in r.json().get("value", []):
        name = item.get("Name", "")
        if "MSIL2A" not in name:
            continue
        products.append({
            "tile": _extract_tile(item),
            "date": (item.get("ContentDate") or {}).get("Start", "")[:10],
            "cloud": _extract_cloud(item),
            "size": item.get("ContentLength") or 0,
            "name": name,
        })
    return products


def dedup(products):
    best = {}
    for p in products:
        k = p["tile"]
        if k not in best or (p["cloud"] or 999) < (best[k]["cloud"] or 999):
            best[k] = p
    return best


REGIONS = [
    ("León 全省 (2019)",   -7.10, 42.05, -4.72, 43.26, "2019-06-01", "2019-09-15"),
    ("Burgos 全省 (2018)", -4.40, 41.40, -2.47, 43.24, "2018-06-01", "2018-09-15"),
    ("Lugo 全省 (2016*)",  -8.03, 42.28, -6.75, 43.79, "2016-06-01", "2016-09-15"),
]


def main():
    grand_total = 0
    for name, lo1, la1, lo2, la2, s, e in REGIONS:
        prods = query_region(lo1, la1, lo2, la2, s, e)
        sel = dedup(prods)
        total = sum(p["size"] for p in sel.values())
        grand_total += total
        print(f"=== {name} ===  查询到 {len(prods)} 个 L2A 产品，去重后 {len(sel)} 个 tile")
        for k in sorted(sel):
            p = sel[k]
            cl = f"{p['cloud']:.1f}%" if p["cloud"] is not None else "?"
            print(f"    {k:8s} {p['date']}  云量 {cl:>6s}  {p['size']/1e9:.2f} GB")
        print(f"  小计: {total/1e9:.2f} GB\n")
    print(f"三省合计: {grand_total/1e9:.2f} GB")
    print("* Lugo 其 IFN4 调查年为 2009（无同期 S2），此处仅按 2016 年估算体量")


if __name__ == "__main__":
    main()
