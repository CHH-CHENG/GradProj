# 数据目录

存放项目全部数据，按数据类型分目录管理。

## 子目录说明
| 目录 | 说明 |
|------|------|
| `Sentinel2/` | Sentinel-2 遥感数据（下载压缩包 / SAFE 产品 / ROI 裁剪影像 / 植被指数） |
| `DEM/` | 地形高程数据（原始 / 裁剪） |
| `inventory/` | 样地调查数据（混交林 / 纯林） |
| `feature/` | 特征工程产物（样本表 samples.csv） |
| `result/` | 模型训练与预测结果输出 |

## 数据总览
| 数据 | 类型 | 格式 | 位置 |
|------|------|------|------|
| Sentinel-2 原始压缩包 | 遥感影像 | ZIP | `Sentinel2/zip/` |
| SAFE 产品目录 | 遥感影像 | SAFE（JP2 波段） | `Sentinel2/SAFE/` |
| ROI 裁剪影像 | 遥感栅格 | GeoTIFF | `Sentinel2/roi/` |
| 植被指数 | 遥感栅格 | GeoTIFF | `Sentinel2/indices/` |
| DEM 原始数据 | 地形栅格 | GeoTIFF | `DEM/raw/` |
| DEM 裁剪数据 | 地形栅格 | GeoTIFF | `DEM/roi/` |
| 混交林样地调查 | 表格 | XLSX | `inventory/mingledforest/` |
| 纯林样地调查 | 数据库 | ACCDB | `inventory/pureforest/` |
| 样本表（特征） | 表格 | CSV | `feature/` |
| 结果输出 | 模型/图表/栅格 | 多种 | `result/` |
