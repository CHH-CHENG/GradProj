# Sentinel-2 遥感数据目录

存放芬兰典型研究区（**纯林 + 混交林**）的 Sentinel-2 遥感数据及各级处理产物。

## 子目录结构

```text
Sentinel2/
├── README.md
├── zip/Finland_PureMixed/       # 原始压缩包（8 个 L2A zip）
├── SAFE/Finland_PureMixed/      # 解压后的 SAFE 产品（8 个）
├── roi/Finland_PureMixed/       # 研究区 ROI 裁剪影像（⏳ 待生成）
└── indices/                     # 植被指数（⏳ 待生成）
```

> `Finland_PureMixed`：芬兰**纯林/混交林对比研究**的遥感数据集合（2023 生长季）。

## 影像文件明细（逐文件）

两个典型研究区（基于 MS-NFI 树种分析识别），时间窗 2023-07-01~08-10、云量<30%、每 tile 取云量最少一期。

### 🌲 纯林区（pure）— 拉普兰纯松林，中心 (27.20E, 68.76N)，成像 2023-08-08

| Tile | SAFE 产品名 | 成像日期 | 云量 | zip ID（前8位） | 大小 |
|------|------------|---------|------|----------------|------|
| T35WMR | `S2A_MSIL2A_20230808T100031_N0510_R122_T35WMR_20241021T205631.SAFE` | 2023-08-08 | ~0% | a7d03c44 | 934.3 MB |
| T35WMS | `S2A_MSIL2A_20230808T100031_N0510_R122_T35WMS_20241021T205631.SAFE` | 2023-08-08 | ~0% | 9c5b60b0 | 517.6 MB |
| T35WNR | `S2A_MSIL2A_20230808T100031_N0510_R122_T35WNR_20241021T205631.SAFE` | 2023-08-08 | 6.8% | 0affa3d7 | 1087.3 MB |
| T35WNS | `S2A_MSIL2A_20230808T100031_N0510_R122_T35WNS_20241021T205631.SAFE` | 2023-08-08 | 0.2% | ea32a917 | 1083.6 MB |

### 🌳 混交区（mixed）— 中心 (24.97E, 66.06N)，成像 2023-07-10

| Tile | SAFE 产品名 | 成像日期 | 云量 | zip ID（前8位） | 大小 |
|------|------------|---------|------|----------------|------|
| T34WFT | `S2B_MSIL2A_20230710T101609_N0510_R065_T34WFT_20240913T122821.SAFE` | 2023-07-10 | 0.1% | b3bd74d5 | 382.2 MB |
| T34WFU | `S2B_MSIL2A_20230710T101609_N0510_R065_T34WFU_20240913T122821.SAFE` | 2023-07-10 | ~0% | 4cf07a31 | 306.1 MB |
| T35WMN | `S2B_MSIL2A_20230710T101609_N0510_R065_T35WMN_20240913T122821.SAFE` | 2023-07-10 | 0% | f0e29719 | 29.1 MB |
| T35WMP | `S2B_MSIL2A_20230710T101609_N0510_R065_T35WMP_20241014T005947.SAFE` | 2023-07-10 | 0% | f0356f50 | 322.5 MB |

> - 文件位置：`zip/Finland_PureMixed/<zipID>.zip` 与 `SAFE/Finland_PureMixed/<SAFE产品名>/`
> - `T35WMN` 仅 29MB：该 tile 多为云/水体，JP2 压缩率高，属正常
> - 均为 **L2A** 地表反射率产品（10m/20m/60m 波段齐备）

## 数据类型与内部格式

### zip/Finland_PureMixed/ — 原始压缩包
- 类型：遥感影像压缩包；格式：ZIP
- 命名：`<产品ID(UUID)>.zip`；内部为 SAFE 产品目录

### SAFE/Finland_PureMixed/ — SAFE 产品目录
- 格式：SAFE（Sentinel-2 标准），命名 `S2A/S2B_MSIL2A_<日期>_N<...>_R<...>_T<编号>_<...>.SAFE`
- 内部格式：
  - `MTD_MSIL2A.xml`：产品元数据
  - `GRANULE/<tile>/IMG_DATA/`：波段（JP2），L2A 按分辨率分目录 `R10m/`（B02 B03 B04 B08）、`R20m/`（B05 B06 B07 B8A B11 B12 等）、`R60m/`，另含 `SCL/AOT/WVP`
  - `GRANULE/<tile>/QI_DATA/`：质量标识图层

### roi/Finland_PureMixed/ — ROI 裁剪影像
- 格式：GeoTIFF（`.tif`），多波段（B02~B12，10m）
- 状态：✅ 已生成 2 个研究区（EPSG:3067、2000×2000、10m）：
  - `pure_pine_lapland_S2_10m_3067.tif`（纯林区）
  - `mixed_central_S2_10m_3067.tif`（混交区）
- 说明：由 `preprocess/finland_study.py` 从覆盖研究区的 SAFE 裁剪拼接（逐块重投影 + 均值融合），0~1 反射率

### indices/ — 植被指数
- 状态：⏳ 待生成（NDVI/EVI 等）

## 输入来源 / 输出去向
- **输入来源**：`download_finland.py` 从 Copernicus Data Space 自动采集（矩形范围查询 + 按 tile 取云量最少一期）
- **输出去向**：`roi/Finland_PureMixed/` 裁剪 → `feature/` 特征提取（与 MS-NFI 蓄积量标签、DEM 对齐）
  - 数值：0~1 地表反射率（float32），nodata = 0

### indices/ — 植被指数
- 类型：遥感栅格
- 格式：GeoTIFF（`.tif`）
- 内部格式：（待补充，计划生成 NDVI/EVI 等）
