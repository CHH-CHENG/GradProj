# DEM 地形数据目录

放置 DEM（数字高程模型）数据，用于提取地形特征（高程、坡度、坡向等）。

## 子目录结构

```text
DEM/
├── README.md
├── raw/                        # 原始 DEM 数据
│   └── Finland_DEM_10m_2019/   # 芬兰 MML 10m 高程模型 2019（全芬兰）
└── roi/                        # 按研究区裁剪的 DEM（⏳ 待生成）
```

## 数据总览

| 数据 | 来源 | 类型 | 格式 | 位置 | 状态 |
|------|------|------|------|------|------|
| 芬兰 MML 10m DEM 2019 | MML（芬兰国家土地测量局） | 地形高程栅格 | GeoTIFF | `raw/Finland_DEM_10m_2019/` | ✅ 已下载 |

---

## Finland_DEM_10m_2019（芬兰 10m 高程模型 2019）

### 1. 数据简介

**Elevation model 2019, 10 m x 10 m**（芬兰语：Korkeusmalli 2019, 10 m x 10 m），由 **MML**（芬兰国家土地测量局，National Land Survey of Finland / Maanmittauslaitos）发布，是**芬兰全国最精确的高程模型**（官方描述：*the most accurate DEM available for whole Finland*）。

- 数据集 ID：`16bb1329-1632-4559-919e-1cd1cd969296`
- 下载平台：Paituli（CSC）/ Etsin Fairdata
- 许可协议：**CC BY 4.0**（另见 `mml/NLS_terms_of_use.pdf`）
- 数据年份：2019；发布于 2016-04-05

### 2. 关键特性

| 特性 | 值 |
|------|-----|
| 分辨率 | **10m × 10m** |
| 垂直精度 | 约 **1.4 m** |
| 高程基准 | **N2000**（芬兰国家高程系统） |
| 投影 | **EPSG:3067（ETRS-TM35FIN）** |
| 覆盖范围 | 全芬兰国土（海岸低地 ~0m 至北部山地） |

### 3. 目录结构与命名规则

```text
Finland_DEM_10m_2019/
├── metadata.json                    # Etsin Fairdata 数据集元数据（原始导出）
├── MML_10mDEM_description.pdf       # 官方数据集说明（英文）
├── MML_10mDEM_kuvaus.pdf            # 官方数据集说明（芬兰语）
├── paituli_<批次ID>.zip             # Paituli 分片下载压缩包（共 5 个）
└── mml/
    ├── NLS_terms_of_use.pdf         # 使用条款（许可）
    └── dem10m/2019/
        ├── K2/ K3/ ... X5/          # 38 个顶层图幅（TM35 图幅编号）
        │   └── K31/ K32/ ...        # 子图幅（每图幅 4 块）
        │       └── K3122.tif        # DEM 分块栅格
        └── ...
```

**命名规则**：`<图幅><子图幅><块>.tif`（如 `K3122.tif` = 图幅 K3 + 子图幅 K31 + 块 22）。每个 tif 对应约 24km × 12km 的一块。

### 4. 文件格式说明

| 文件 | 格式 | 说明 |
|------|------|------|
| `metadata.json` | JSON（UTF-8） | 数据集元数据（ID/许可/描述/空间范围/远程资源） |
| `MML_10mDEM_*.pdf` | PDF | 官方数据说明（英文 / 芬兰语） |
| `NLS_terms_of_use.pdf` | PDF | 使用条款（CC BY 4.0） |
| `paituli_<批次ID>.zip` | ZIP | 分片压缩包（每片含若干图幅的 tif） |
| `<图幅><子图幅><块>.tif` | GeoTIFF | DEM 分块栅格（详见第 5 节） |

### 5. 栅格内部格式（已用 rasterio 验证）

| 属性 | 值 |
|------|-----|
| 格式 / Driver | GeoTIFF（`GTiff`） |
| 波段 / 数据类型 | 单波段，`float32` |
| 投影 | **EPSG:3067（ETRS-TM35FIN）** |
| 尺寸（width × height） | 2400 × 1200（每块约 24km × 12km） |
| 像元 | 10m × 10m |
| 压缩 | **LZW**（无损压缩） |
| 高程基准 | N2000 |
| nodata | **-9999** |
| 值域 | 海岸低地 ~0 m；内陆丘陵约 100~380 m；芬兰最高点 Halti 约 1324 m |

### 6. 空间范围（官方元数据）

- **经度**：18.71°E ~ 31.77°E
- **纬度**：59.35°N ~ 70.14°N
- 覆盖整个芬兰国土（与 MS-NFI 2023 蓄积量数据同一国家范围）

### 7. 数据规模

- tif 总数：**1523 个**，总大小约 **10.29 GB**
- 顶层图幅：38 个（K2 ~ X5）
- 下载分片：5 个 zip（`paituli_*`，已全部解压到 `mml/`）

### 8. 输入来源 / 输出去向

- **输入来源**：Paituli 平台分片下载，解压后为按图幅组织的分块栅格
- **输出去向**：
  - `roi/`：按研究区裁剪后的 DEM（与 Sentinel-2 特征栅格重采样对齐，10m）
  - 供 `feature/` 特征提取使用：高程、坡度、坡向等地形特征
  - 使用前需拼接/裁剪所需图幅块，并统一 CRS 与分辨率

### 9. 参考

- MML 官方说明：`MML_10mDEM_description.pdf`（英文）
- 元数据：`metadata.json`
