# Sentinel-2 遥感数据目录

存放 Sentinel-2 卫星遥感数据及各级处理产物。

## 子目录说明
| 目录 | 内容 | 状态 |
|------|------|------|
| `zip/` | Copernicus 下载的原始压缩包 | ✅ 20 个 |
| `SAFE/` | 解压后的 SAFE 产品目录（L1C 11 个 + L2A 9 个） | ✅ 20 个 |
| `roi/` | 研究区 ROI 裁剪影像（10m 多波段） | ✅ 9 个（L2A） |
| `indices/` | 植被指数栅格 | ⏳ 待生成 |

## 数据类型与内部格式

### zip/ — 原始压缩包
- 类型：遥感影像压缩包
- 格式：ZIP
- 命名：`<产品ID(UUID)>.zip`
- 内部格式：压缩包内为 SAFE 产品目录（解压后放入 `SAFE/`）

### SAFE/ — SAFE 产品目录
- 类型：遥感影像产品
- 格式：SAFE（Sentinel-2 标准产品格式）
- 命名：`S2A/S2B_MSIL1C/2A_<日期>_N<...>_R<...>_T<编号>_<...>.SAFE`
- 内部格式：
  - `MTD_MSIL1C.xml` 或 `MTD_MSIL2A.xml`：产品元数据
  - `GRANULE/<tile>/IMG_DATA/`：波段影像（JP2）
    - **L2A**：按分辨率分目录 `R10m/`（B02 B03 B04 B08）、`R20m/`（B05 B06 B07 B8A B11 B12 等）、`R60m/`，另含 `SCL/AOT/WVP` 辅助图层
    - **L1C**：`IMG_DATA/` 平铺存放 13 个波段（B01~B12、B8A、TCI）
  - `GRANULE/<tile>/QI_DATA/`：质量标识图层

### roi/ — ROI 裁剪影像
- 类型：多波段遥感栅格
- 格式：GeoTIFF（`.tif`）
- 命名：`<SAFE产品名>_roi.tif`
- 内部格式：
  - 波段：B02 B03 B04 B05 B06 B07 B08 B8A B11 B12（10 个，按此顺序写入）
  - 分辨率：10m（20m 波段已重采样）
  - 投影：EPSG:32648（UTM 48N）
  - 范围：以 `(107.0, 34.3)` 为中心，约 10km × 10km
  - 数值：0~1 地表反射率（float32），nodata = 0

### indices/ — 植被指数
- 类型：遥感栅格
- 格式：GeoTIFF（`.tif`）
- 内部格式：（待补充，计划生成 NDVI/EVI 等）
