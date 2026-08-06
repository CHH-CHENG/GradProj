基于Sentinel-2多源遥感特征与随机森林的森林蓄积量估测研究
---
（本科毕设）
# 1.项目简介：
# 2.科研路线：
```text
样地调查数据\
        │
        │（蓄积量）
        ▼
  建立样地数据库
        │
        │
────────────────────────────────────────
        │
Sentinel-2 自动下载（Copernicus API）
        │
        ▼
      自动解压SAFE
        │
        ▼
      波段读取
        │
        ▼
      重采样（统一10m）
        │
        ▼
      ROI裁剪（按样地）
        │
        ▼
特征提取
├── 光谱特征
├── 植被指数
├── 纹理特征
└── 地形特征（DEM）
        │
        ▼
特征选择
        │
        ▼
Random Forest
        │
        ▼
SHAP解释
        │
        ▼
蓄积量空间预测
```
# 3.项目结构：
```text
ProjCode/
│
├── config/
│
├── data/
│   │
│   ├── inventory/                 
│   │      inventory.xlsx
│   │      plots.shp
│   │      plots.geojson
│   │
│   ├── Sentinel2/
│   │      zip/
│   │      SAFE/
│   │      roi/
│   │      indices/
│   │
│   ├── DEM/
│   │      dem.tif
│   │
│   ├── feature/
│   │      samples.csv
│   │
│   └── result/
│
├── downloader/
│
├── preprocess/
│
├── feature/
│
├── model/
│
├── utils/
│
└── main.py
```
# 4.数据说明：
# 5.运行方法：
# 6.结果展示：
