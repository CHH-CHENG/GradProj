# 数据目录

存放项目全部数据，按数据类型分目录管理。当前研究区域为**西班牙**（IFN4 三省：**León（优先）/ Burgos / Lugo**）。

## 子目录说明
| 目录 | 说明 |
|------|------|
| `inventory/` | IFN4（西班牙第四次国家森林清查）三省样地/树木数据（蓄积量标签来源） |
| `Sentinel2/` | 三省 Sentinel-2 遥感影像（下载/解压/裁剪） |
| `DEM/` | 地形数据（⏳ 待获取西班牙 DEM） |
| `feature/` | 特征工程产物（样本表 samples.csv、样地蓄积量） |
| `result/` | 模型训练与预测结果输出 |

> 📌 历史说明：早期测试数据（中国秦岭影像、芬兰 MS-NFI/DEM/影像等）已全面移除，项目现聚焦西班牙 IFN4。

## 数据总览
| 数据 | 类型 | 格式 | 位置 | 状态 |
|------|------|------|------|------|
| IFN4 三省野外数据库 | 样地/树木调查 | ACCDB | `inventory/IFN4.../Bases de datos de campo/` | ✅ |
| IFN4 三省 GIS 数据库 | GIS 空间数据 | ACCDB | `inventory/IFN4.../Bases de datos Sig/` | ✅ |
| IFN4 三省结果统计表 | 统计表 | XLSX/XLS | `inventory/IFN4.../Tablas de resultados IFN4/` | ✅ |
| 西班牙 S2 原始压缩包（三省 25 tile） | 遥感影像 | ZIP | `Sentinel2/zip/Spain_IFN4/<省>/` | ✅ |
| S2 SAFE 产品 | 遥感影像 | SAFE（JP2 波段） | `Sentinel2/SAFE/Spain_IFN4/` | ✅ |
| ROI 裁剪影像 | 遥感栅格 | GeoTIFF | `Sentinel2/roi/` | ⏳ 待生成 |
| 植被指数 | 遥感栅格 | GeoTIFF | `Sentinel2/indices/` | ⏳ 待生成 |
| 西班牙 DEM | 地形栅格 | GeoTIFF | `DEM/raw/` | ⏳ 待获取 |
| 样地蓄积量（PCMayores 计算） | 表格 | CSV | `feature/` | ⏳ 待生成 |
| 样本表（特征+标签） | 表格 | CSV | `feature/` | ⏳ 待生成 |
| 结果输出 | 模型/图表/栅格 | 多种 | `result/` | ⏳ 待生成 |

## 各数据源详细说明
- **IFN4 标签数据**：见 `inventory/README.md`（三省结构/调查年/坐标/字段详解）
- **Sentinel-2**：见 `Sentinel2/README.md`（逐 tile 明细）
- **DEM / 特征 / 结果**：见各子目录 README
