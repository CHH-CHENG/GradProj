# downloader 模块（数据下载）

负责从 **Copernicus Data Space（CDSE）** 自动下载 Sentinel-2 数据。

## 脚本说明

### copernicus.py

| 函数 | 作用 |
|------|------|
| `get_credentials()` | 从 `config/copernicus.yaml`（或环境变量 `CDSE_USER`/`CDSE_PASS`）读取账号 |
| `get_token()` | 获取 CDSE 认证 token（并处理过期刷新） |
| `search_products(lon, lat, start_date, end_date, cloud=20)` | 按中心经纬度 + 时间范围 + 云量查询产品 ID（单点，按时间倒序） |
| `search_products_bbox(lon_min, lat_min, lon_max, lat_max, ...)` | **按 WGS84 矩形范围查询**（POLYGON），返回完整产品信息 `{id,name,tile,date,cloud,online}`；支持 L2A/L1C/ALL 过滤；`$expand=Attributes` 获取云量/tileId |
| `dedup_by_tile(products)` | **按 tile 去重**，每个 tile 只保留云量最少的一期（避免重复时相） |
| `search_and_download_region(lon_min, ..., cloud)` | 区域一站式：查询 → 按 tile 去重 → 批量下载 |
| `download_product(product_id, get_token_func, out_dir)` | 下载单个产品（支持 401 自动刷新 token、重试、断点续传 `.part`、zip 完整性校验） |
| `download_batch(product_ids)` | 批量下载产品到 `data/Sentinel2/zip/` |

- **输入**：`config/copernicus.yaml`（账号、查询参数）
- **输出**：`data/Sentinel2/zip/<产品ID>.zip`
- **关键要求**：断点续传（`.part`）、完整性校验（`zipfile.is_zipfile`）、禁止重复下载、401 自动刷新 token
- **说明**：Copernicus OData 为 v4 语法，`$expand=Attributes` 才返回 cloudCover/tileId；字符串筛选需在 Python 端过滤（`substringof` 不支持）

### spain.py（西班牙 IFN4 采集脚本）

- 功能：按省份采集 Sentinel-2 L2A 影像（整省矩形范围 → 按 tile 去重 → 下载）
- 省份与时间窗（与 IFN4 调查年匹配）：
  - **leon**（重点）：IFN4 2019 → S2 2019-06-01~09-15，10 tile ≈ 10.0 GB
  - **burgos**：IFN4 2018 → S2 2018-06-01~09-15，9 tile ≈ 7.9 GB
  - **lugo**：IFN4 2009（无同期 S2）→ 暂用 2016-06-01~09-15，6 tile ≈ 5.5 GB
- 输出：`data/Sentinel2/zip/Spain_IFN4/<省>/<UUID>.zip`（共 25 个，约 21.3 GB）
- 用法（在项目根运行）：
  - `python -m downloader.spain --dry-run leon`（仅查询预览）
  - `python -m downloader.spain leon`（下载 León）/ `python -m downloader.spain all`（三省）

### estimate.py（下载量估算）

- 功能：查询指定区域/时间窗/云量下的 L2A 产品，按 tile 去重后统计总大小（GB）
- 用途：下载前评估数据量（避免超预算）
- 用法：`python -m downloader.estimate`

### dem.py（西班牙 DEM 批量下载）—— ✅ 已实现

- **数据源**：CNIG / IDEE **WCS-INSPIRE** 服务（`https://servicios.idee.es/wcs-inspire/mdt`，WCS 2.0.1）——**免账号**
  - Coverage：`Elevacion25830_{5|25|200|500|1000}`（ETRS89/UTM 30N，覆盖西班牙全境）
  - 备选：`Elevacion4258_*`（经纬度，用 `--lonlat` 切换）
- **功能**：按省份 bbox（`config/spain_study.yaml`）自动切块（每块 4000×4000 像元）并逐块下载 GeoTIFF
  - **幂等**：已存在的块自动跳过，可反复运行补齐
  - **防缺漏**：每省输出 `_manifest.csv`（块清单/状态/字节数），失败块在汇总中提示
  - 网络失败自动重试（3 次，退避）
- **输出**：`data/DEM/raw/Spain_DEM/<省>/mdt{05|25}/`
- **用法**：
  - `python -m downloader.dem --dry-run`（仅预览块数与估算体积）
  - `python -m downloader.dem --res 25 all` / `--res 5 all`
  - `python -m downloader.dem all`（5m + 25m）
  - `python -m downloader.dem --lonlat --res 25 lugo`（经纬度 coverage，备选）
- **实测**（2026-09-19）：返回 GeoTIFF / int16 / 无 nodata；单次请求 4000×4000 像元可行（32 MB）
