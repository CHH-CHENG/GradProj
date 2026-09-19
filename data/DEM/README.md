# DEM 地形数据目录

放置 DEM（数字高程模型）数据，用于提取地形特征（高程、坡度、坡向）。

## 数据来源

**CNIG / IDEE WCS-INSPIRE 服务**（西班牙国家地理信息中心）

- 服务地址：`https://servicios.idee.es/wcs-inspire/mdt`（WCS 2.0.1，**免账号**）
- 产品：PNOA-LiDAR 派生 MDT（Modelos Digitales del Terreno）
- Coverage：`Elevacion25830_{5|25|...}`（ETRS89 / UTM 30N，覆盖西班牙全境）
- 获取脚本：`downloader/dem.py`（批量、分块、幂等、带清单校验）

## 子目录结构

```text
DEM/
├── README.md
├── raw/                          # 原始 DEM（✅ 已下载）
│   └── Spain_DEM/
│       ├── leon/  (mdt05: 88 块 / mdt25: 6 块)
│       ├── burgos/ (mdt05: 99 块 / mdt25: 6 块)
│       └── lugo/   (mdt05: 54 块 / mdt25: 4 块)
│           └── mdt{05|25}/
│               ├── <省>_MDT{05|25}_EPSG25830_x{minx}_y{miny}.tif
│               └── _manifest.csv
└── roi/                          # 按研究区裁剪的 DEM（⏳ 待生成）
```

## 数据总览（✅ 已下载，2026-09-19）

| 分辨率 | 覆盖范围 | 块数 | 大小 | 状态 |
|--------|---------|------|------|------|
| **25m**（MDT25） | 三省全域 bbox | 16 | 0.26 GB | ✅ |
| **5m**（MDT05） | 三省全域 bbox | 241 | ~7.7 GB | ✅ |

- 投影：**EPSG:25830**（ETRS89 / UTM 30N）；像元类型 **int16**；单位：米
- 覆盖范围：按 `config/spain_study.yaml` 的三省 bbox（外接矩形，含 200m 缓冲）

## 数据内部格式

### `mdt{05|25}/<省>_MDT{05|25}_EPSG25830_x{minx}_y{miny}.tif`
- 格式：GeoTIFF（WCS 直接返回，无二次处理）
- CRS：EPSG:25830；分辨率：5m / 25m；像元：int16（高程，m）
- 块大小：4000×4000 像元（边缘块按 bbox 截断，可能很小）
- ⚠️ **无 nodata 声明**（越界/无数据区域可能以 0 填充，使用时需注意）

### `mdt{05|25}/_manifest.csv`
- 列：`block, x0, y0, x1, y1, file, status, bytes`
- 作用：块清单与下载状态（**防缺漏核对**；`status` 非 `ok`/`skip` 即为失败块）

## 输入来源 / 输出去向

- **输入来源**：`python -m downloader.dem`（CNIG WCS-INSPIRE）
- **输出去向**：按研究区裁剪 → `DEM/roi/`；与 Sentinel-2 特征对齐后进入 `feature/`
  （地形特征：`DEM_elev` / `DEM_slope` / `DEM_aspect`）

> 📌 历史说明：早期芬兰 MML 10m DEM（`Finland_DEM_10m_2019/`）已随研究区域更换移除。

## 备注

- ⚠️ WCS **无 EPSG:25829** 覆盖；本项目统一使用 **25830**（含 Lugo，UTM30 网格在 Lugo 处形变 <0.4%）
  - 备选：`python -m downloader.dem --lonlat --res 25 lugo`（取经纬度版后重投影）
- **分块而非拼接**：便于按研究区窗口读取（避免加载整省）；后续裁剪到 `DEM/roi/` 时用 `rasterio.merge` 合并所需块
- 两种分辨率（5m / 25m）均已下载，可按需选用（5m 用于精细坡度/坡向，25m 与 30m 特征窗口更匹配）
