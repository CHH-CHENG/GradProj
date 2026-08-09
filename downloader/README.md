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

### download_finland.py（项目根，芬兰典型区采集脚本）

- 功能：按**纯林/混交林典型区域**采集 Sentinel-2 L2A 影像（整 tile，每 tile 取云量最少一期，避免重复时相）
- 区域：纯林区（拉普兰 27.20E/68.76N）、混交区（24.97E/66.06N）
- 参数：时间窗 2023-07-01~08-10，云量<30%，L2A
- 用法：
  - `python download_finland.py --dry-run`（仅查询预览）
  - `python download_finland.py`（执行下载 → `data/Sentinel2/zip/Finland_PureMixed/`）
- 注：脚本下载到 `zip/` 根后需自行移入 `zip/Finland_PureMixed/`（当前已手动整理）
