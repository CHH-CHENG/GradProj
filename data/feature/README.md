# 特征数据目录

放置特征工程产物（模型训练样本）及研究区中间数据。

> ⏳ **当前为空**：早期芬兰特征数据（samples.csv 等）已随研究区域更换移除，待西班牙流程重建。

## 子目录结构

```text
feature/
├── README.md
└── （⏳ 待生成）
```

## 规划数据

| 数据 | 说明 | 状态 |
|------|------|------|
| 样地蓄积量（IFN4） | 从 `PCMayores` 树木数据计算的样地级蓄积量（m³/ha） | ⏳ 待生成 |
| `samples.csv` | 训练样本表（每行一个样地/窗口：S2 光谱+植被指数+地形特征 + GSV 标签） | ⏳ 待生成 |
| `samples_sampled.csv` | 抽样后训练集（空间均匀抽样降自相关） | ⏳ 待生成 |

## 数据类型

- 表格数据（CSV）/ GeoTIFF（研究区对齐栅格）

## 数据内部格式（待补充）

- `samples.csv` 列规划（**23 特征** + 标识/标签，详见 `项目开发文档.md` 8.11）：
  - 标识：`sample_id` / `province` / `plot_id` / `x` / `y`
  - 基础光谱（10）：`B02` `B03` `B04` `B05` `B06` `B07` `B08` `B8A` `B11` `B12`
  - 植被指数（3）：`NDVI` `NDWI` `NDRE`
  - 多尺度（3）：`NDVI_std50` `NDRE_std50` `B8_std50`
  - 结构-纹理（2）：`GLCM_contrast` `GLCM_entropy`
  - 结构-邻域（2）：`NDVI_mean100` `NDVI_std100`
  - 地形（3）：`DEM_elev` `DEM_slope` `DEM_aspect`
  - 标签：`GSV`（m³/ha，IFN4 样地蓄积量）
