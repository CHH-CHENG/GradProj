# 数据目录

存放项目全部数据，按数据类型分目录管理。当前项目聚焦 **芬兰** 研究（纯林/混交林对比）。

## 子目录说明
| 目录 | 说明 |
|------|------|
| `Sentinel2/` | 芬兰典型区 Sentinel-2 遥感数据（纯林区 + 混交区） |
| `DEM/` | 芬兰 MML 10m 高程模型 |
| `inventory/` | 芬兰 MS-NFI 2023 蓄积量标签栅格 |
| `feature/` | 特征工程产物（样本表 samples.csv） |
| `result/` | 模型训练与预测结果输出 |

> 📌 历史说明：早期用于测试的中国（秦岭）20 个 Sentinel-2 影像、秦岭混交林与西班牙纯林样地数据已因不符合研究需求移除，项目现全部聚焦芬兰。

## 数据总览
| 数据 | 类型 | 格式 | 位置 | 状态 |
|------|------|------|------|------|
| 芬兰典型区 S2 原始压缩包（8 个 L2A） | 遥感影像 | ZIP | `Sentinel2/zip/Finland_PureMixed/` | ✅ |
| 芬兰典型区 S2 SAFE 产品（8 个） | 遥感影像 | SAFE（JP2 波段） | `Sentinel2/SAFE/Finland_PureMixed/` | ✅ |
| 芬兰典型区 ROI 裁剪影像 | 遥感栅格 | GeoTIFF | `Sentinel2/roi/Finland_PureMixed/` | ⏳ 待生成 |
| 植被指数 | 遥感栅格 | GeoTIFF | `Sentinel2/indices/` | ⏳ 待生成 |
| 芬兰 MML 10m DEM 2019（1523 块） | 地形栅格 | GeoTIFF | `DEM/raw/Finland_DEM_10m_2019/` | ✅ |
| DEM 裁剪数据 | 地形栅格 | GeoTIFF | `DEM/roi/` | ⏳ 待生成 |
| 芬兰 MS-NFI 2023 蓄积量栅格（4 主题） | 森林清查栅格（标签） | GeoTIFF | `inventory/Finland_NFI_2023_GSV/` | ✅ |
| 样本表（特征） | 表格 | CSV | `feature/` | ⏳ 待生成 |
| 结果输出 | 模型/图表/栅格 | 多种 | `result/` | ⏳ 待生成 |

## 各数据源详细说明
- **Sentinel-2**：见 `Sentinel2/README.md`（逐文件明细：位置/时间/用途）
- **DEM**：见 `DEM/README.md`
- **蓄积量标签**：见 `inventory/README.md`
- **特征**：见 `feature/README.md`
- **结果**：见 `result/README.md`
