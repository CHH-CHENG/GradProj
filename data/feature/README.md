# 特征数据目录

放置特征工程产物（模型训练样本）及研究区中间数据。

## 子目录结构

```text
feature/
├── README.md
├── samples.csv               # 训练样本表（✅ 76.3 万样本）
├── samples_sampled.csv       # 抽样后训练集（✅ 约 9.2 万样本，空间均匀抽样）
├── finland_study/            # 研究区对齐栅格（MS-NFI 标签 / DEM）
│   ├── pure_pine_lapland_GSV_10m_3067.tif   # 纯林区蓄积量标签（m³/ha）
│   ├── pure_pine_lapland_DEM_10m_3067.tif   # 纯林区高程（m，N2000）
│   ├── mixed_central_GSV_10m_3067.tif       # 混交区蓄积量标签
│   └── mixed_central_DEM_10m_3067.tif       # 混交区高程
└── _cls1km.npy / _t1km.npy    # 典型区识别分析临时中间结果（可复现）
```

## 放置的数据

- `samples.csv`：**训练样本表**（✅ 已生成，76.3 万样本，0 NaN），每行一个 30m×30m 窗口样本
- `samples_sampled.csv`：**抽样后训练集**（✅ 空间均匀抽样，默认每区 5 万、共约 9.2 万），用于建模控制规模
- `finland_study/`：研究区对齐栅格（MS-NFI 蓄积量标签 16m→10m、DEM 高程，均 EPSG:3067、10m、2000×2000）
- `_cls1km.npy` / `_t1km.npy`：MS-NFI 典型区识别分析临时中间结果（1km 网格分类 + 仿射变换）

## 数据类型

- 表格数据（CSV）/ numpy 数组（NPY）/ GeoTIFF

## samples.csv 内部格式

| 列 | 说明 |
|----|------|
| `sample_id` / `region_id` / `label` | 样本 ID / 研究区 / 分组（pure 纯林 / mixed 混交） |
| `x_3067` / `y_3067` | 窗口中心坐标（EPSG:3067） |
| `B02`~`B12`（10 列） | S2 光谱窗口均值（0~1 反射率） |
| `NDVI` / `EVI` / `NDWI` / `NDRE` | 植被指数（窗口均值） |
| `DEM_elev` / `DEM_slope` / `DEM_aspect` | 地形特征：高程（m）/ 坡度（°）/ 坡向（°） |
| `GSV` | 蓄积量标签（m³/ha，窗口中心 MS-NFI 值） |
