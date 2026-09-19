"""西班牙 DEM 批量下载（CNIG / IDEE · WCS-INSPIRE，**免账号**）

## 数据源

`https://servicios.idee.es/wcs-inspire/mdt`（WCS 2.0.1，PNOA-LiDAR 派生 MDT）

可用 coverage（网格步长）：
    Elevacion25830_{5|25|200|500|1000}   ← ETRS89 / UTM 30N（**覆盖西班牙全境**，含 Lugo）
    Elevacion4258_{5|25|200|500|1000}    ← 经纬度（EPSG:4326 声明）

> 实测结论（2026-09-19）：
> - `subset=x(..)` / `y(..)` 为轴别名（= long / lat），与 `lat/long` 等价；
> - 单次请求 4000×4000 像元可行（32 MB 响应）；
> - 返回 GeoTIFF、int16、无 nodata 声明；UTM 版为原生投影网格（无重采样）。
> - **本项目统一使用 `Elevacion25830_*`**（三省一致，避免跨投影差异）。

## 策略（防缺漏）

1. 按省份 bbox（`config/spain_study.yaml`）→ 转 UTM30 → 按块（默认 4000×4000 像元）切分
2. 逐块请求并**直接落盘**为 GeoTIFF；**已存在则跳过**（幂等，可反复运行补齐）
3. 每省写出 `_manifest.csv`（块清单 / 状态 / 字节数），失败块会汇总提示
4. `--dry-run` 仅列出计划（块数 + 估算体积），不下载

## 输出

    data/DEM/raw/Spain_DEM/<province>/mdt{05|25}/<province>_MDT{05|25}_EPSG25830_x{minx}_y{miny}.tif
    data/DEM/raw/Spain_DEM/<province>/mdt{05|25}/_manifest.csv

## 用法（在项目根运行）

    python -m downloader.dem --dry-run            # 预览三省 5m + 25m 计划
    python -m downloader.dem --res 25 all         # 下载三省 25m
    python -m downloader.dem --res 5 leon         # 下载 León 5m
    python -m downloader.dem all                  # 5m + 25m 全部（三省）
    python -m downloader.dem --lonlat --res 25 lugo   # 选经纬度 coverage 取 Lugo（备选）
"""
import csv
import math
import sys
import time
from pathlib import Path

import requests
import yaml
from rasterio.warp import transform as warp_transform

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout.reconfigure(errors="replace")   # 兼容 Windows GBK 控制台
except Exception:
    pass

WCS_URL = "https://servicios.idee.es/wcs-inspire/mdt"
CONFIG_PATH = ROOT / "config" / "spain_study.yaml"
OUT_ROOT = ROOT / "data" / "DEM" / "raw" / "Spain_DEM"

BLOCK_PX = 4000            # 单次请求像元数（实测 4000x4000 可行）
MAX_RETRY = 3
TIMEOUT = 300

# 分辨率(m) → coverage 名（默认 UTM30；--lonlat 时用经纬度版）
UTM_COVERAGE = {5: "Elevacion25830_5", 25: "Elevacion25830_25"}
LONLAT_COVERAGE = {5: "Elevacion4258_5", 25: "Elevacion4258_25"}


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def bbox_to_utm(bbox, dst="EPSG:25830", margin=200.0):
    """经纬度 bbox → 目标 CRS 外接矩形（含 margin 缓冲，米）"""
    lons = [bbox["lon_min"], bbox["lon_max"], bbox["lon_min"], bbox["lon_max"]]
    lats = [bbox["lat_min"], bbox["lat_min"], bbox["lat_max"], bbox["lat_max"]]
    xs, ys = warp_transform("EPSG:4326", dst, lons, lats)
    return (min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin)


def bbox_to_lonlat(bbox, margin_deg=0.002):
    """经纬度 bbox（直接使用，含 margin 缓冲）"""
    return (bbox["lon_min"] - margin_deg, bbox["lat_min"] - margin_deg,
            bbox["lon_max"] + margin_deg, bbox["lat_max"] + margin_deg)


def plan_blocks(x0, y0, x1, y1, res, block_px=BLOCK_PX):
    """矩形 → 块清单 [(i, j, bx0, by0, bx1, by1), ...]"""
    span = res * block_px
    nx = max(1, math.ceil((x1 - x0) / span))
    ny = max(1, math.ceil((y1 - y0) / span))
    blocks = []
    for j in range(ny):
        for i in range(nx):
            bx0 = x0 + i * span
            by0 = y0 + j * span
            blocks.append((i, j, round(bx0, 3), round(by0, 3),
                           round(min(bx0 + span, x1), 3), round(min(by0 + span, y1), 3)))
    return blocks


def fetch_block(coverage, bx0, by0, bx1, by1):
    """请求单块，返回 GeoTIFF bytes；失败抛异常"""
    params = [("service", "WCS"), ("version", "2.0.1"), ("request", "GetCoverage"),
              ("coverageId", coverage), ("format", "image/tiff"),
              ("subset", f"x({bx0},{bx1})"), ("subset", f"y({by0},{by1})")]
    last = None
    for attempt in range(1, MAX_RETRY + 1):
        try:
            r = requests.get(WCS_URL, params=params, timeout=TIMEOUT)
            ct = r.headers.get("content-type", "").lower()
            if r.status_code == 200 and "tiff" in ct:
                return r.content
            last = f"HTTP {r.status_code} {r.text[:150]}"
        except Exception as e:                    # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
        if attempt < MAX_RETRY:
            time.sleep(2 * attempt)
    raise RuntimeError(last or "unknown error")


def download_province(key, prov, res, use_lonlat=False, dry_run=False):
    """下载单个省份的指定分辨率 DEM，返回统计 dict"""
    coverage = (LONLAT_COVERAGE if use_lonlat else UTM_COVERAGE)[res]
    tag = f"mdt{res:02d}"
    out_dir = OUT_ROOT / key / tag
    out_dir.mkdir(parents=True, exist_ok=True)

    bbox = prov["bbox"]
    if use_lonlat:
        x0, y0, x1, y1 = bbox_to_lonlat(bbox)
        unit = "deg"
    else:
        x0, y0, x1, y1 = bbox_to_utm(bbox)
        unit = "m"

    blocks = plan_blocks(x0, y0, x1, y1, res)
    est_mb = len(blocks) * (BLOCK_PX ** 2 * 2) / 1e6      # int16 未压缩估算

    print(f"\n{'=' * 74}")
    print(f"[{key}] {prov['name']}  {res}m  coverage={coverage}")
    print(f"  范围({unit}): x {x0:.1f} ~ {x1:.1f} | y {y0:.1f} ~ {y1:.1f}")
    print(f"  块数: {len(blocks)} (每块 {BLOCK_PX}x{BLOCK_PX} 像元) | 未压缩估算 {est_mb:.0f} MB")

    if dry_run:
        for b in blocks[:5]:
            print(f"    block({b[0]},{b[1]}) x({b[2]},{b[4]}) y({b[3]},{b[5]})")
        if len(blocks) > 5:
            print(f"    ... 其余 {len(blocks) - 5} 块")
        return {"province": key, "res": res, "blocks": len(blocks),
                "ok": 0, "skip": 0, "fail": 0, "bytes": 0, "dry_run": True}

    manifest_path = out_dir / "_manifest.csv"
    rows, ok, skip, fail = [], 0, 0, 0
    for n, (i, j, bx0, by0, bx1, by1) in enumerate(blocks, 1):
        fname = f"{key}_MDT{res:02d}_EPSG25830_x{int(bx0)}_y{int(by0)}.tif"
        fpath = out_dir / fname
        status, nbytes = "ok", 0
        if fpath.exists() and fpath.stat().st_size > 0:
            status, nbytes = "skip", fpath.stat().st_size
            skip += 1
        else:
            try:
                content = fetch_block(coverage, bx0, by0, bx1, by1)
                fpath.write_bytes(content)
                nbytes, ok = len(content), ok + 1
            except Exception as e:                # noqa: BLE001
                status, fail = f"fail: {e}"[:180], fail + 1
                print(f"  [{n}/{len(blocks)}] 失败: {fname} -> {e}")
        if status == "ok":
            print(f"  [{n}/{len(blocks)}] ok  {fname}  {nbytes / 1e6:.2f} MB")
        rows.append({"block": f"{i}_{j}", "x0": bx0, "y0": by0, "x1": bx1, "y1": by1,
                     "file": fname, "status": status, "bytes": nbytes})

    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["block", "x0", "y0", "x1", "y1",
                                          "file", "status", "bytes"])
        w.writeheader()
        w.writerows(rows)

    total = sum(r["bytes"] for r in rows)
    print(f"  → 完成: ok={ok} skip={skip} fail={fail} | 合计 {total / 1e6:.1f} MB | 清单 {manifest_path.name}")
    return {"province": key, "res": res, "blocks": len(blocks),
            "ok": ok, "skip": skip, "fail": fail, "bytes": total, "dry_run": False}


def main():
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return

    dry_run = "--dry-run" in argv
    use_lonlat = "--lonlat" in argv

    res_arg = None
    if "--res" in argv:
        k = argv.index("--res")
        if k + 1 < len(argv):
            res_arg = int(argv[k + 1])
    resolutions = [5, 25] if res_arg is None else [res_arg]
    if any(r not in (5, 25) for r in resolutions):
        print(f"不支持的分辨率: {resolutions}（可选 5 / 25）")
        return

    targets = [a for a in argv if not a.startswith("-")
               and a not in ("all", "5", "25")]
    cfg = load_config()
    provinces = cfg["provinces"]
    if not targets or "all" in argv:
        keys = list(provinces)
    else:
        keys = [t for t in targets if t in provinces]
        unknown = [t for t in targets if t not in provinces]
        if unknown:
            print(f"未知省份: {unknown}  可选: {list(provinces)} 或 all")

    summ = []
    for res in resolutions:
        for k in keys:
            summ.append(download_province(k, provinces[k], res, use_lonlat, dry_run))

    print(f"\n{'=' * 74}\n汇总")
    for s in summ:
        if s["dry_run"]:
            print(f"  [{s['province']}] {s['res']}m: 计划 {s['blocks']} 块（dry-run）")
        else:
            print(f"  [{s['province']}] {s['res']}m: {s['blocks']} 块 "
                  f"(ok {s['ok']} / skip {s['skip']} / fail {s['fail']}) "
                  f"{s['bytes'] / 1e6:.1f} MB")
    tot_fail = sum(s["fail"] for s in summ)
    tot_bytes = sum(s["bytes"] for s in summ)
    print(f"  合计: {tot_bytes / 1e9:.2f} GB | 失败 {tot_fail} 块"
          + ("（重新运行同一命令即可补齐）" if tot_fail else ""))


if __name__ == "__main__":
    main()
