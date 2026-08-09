# 蓄积量标签数据目录

放置**蓄积量标签数据**（Ground Truth）。按数据来源分类，每个来源一个独立文件夹。

> 📌 历史说明：早期秦岭混交林（角规调查 xlsx）与西班牙纯林（accdb）样地数据已因不符合研究需求移除，本目录现聚焦芬兰 MS-NFI 2023 蓄积量栅格。

## 子目录结构

```text
inventory/
├── README.md
└── Finland_NFI_2023_GSV/   # 芬兰多源国家森林清查（MS-NFI）2023 栅格数据
```

## 数据总览

| 数据 | 来源 | 类型 | 格式 | 位置 | 状态 |
|------|------|------|------|------|------|
| 芬兰 MS-NFI 2023 蓄积量栅格 | Luke（芬兰自然资源研究所） | 森林清查栅格（蓄积量标签） | GeoTIFF | `Finland_NFI_2023_GSV/` | ✅ 已下载 4 个主题 |

---

## Finland_NFI_2023_GSV（芬兰多源国家森林清查 2023）

### 1. 数据简介

**Multi-source national forest inventory (MS-NFI) raster maps of 2023**
（芬兰多源国家森林清查 2023 栅格地图），由 **Luke**（Natural Resources Institute Finland / 芬兰自然资源研究所）基于遥感 + 地面样地生产的**森林蓄积量等变量的空间分布栅格**。

- 数据集 ID：`682679e9-0e42-4e0e-a9b2-c53fc319623d`
- 下载平台：Paituli（CSC）/ Etsin Fairdata
- 许可协议：**CC BY 4.0**（使用需注明 `©Luonnonvarakeskus, 2023` 与数据集名称）
- 发布/更新时间：2025-08-05

### 2. 生产方法（简述）

- 地面样地：2019–2023 年 **VMI13** 清查，共 **51051 个**样地（森林/低产林地/无立木地）
- 遥感影像：Sentinel-2 **L2A 地表反射率（SR）** 自动镶嵌影像（2021–2023 生长季），CloudScore+ 去云
- 方法：**增强 k-NN（ik-NN，5 最近邻）**，特征权重用遗传算法优化
- 数据时点：野外数据更新至 **2023-07-31**

#### 2.1 时间信息

| 时间要素 | 值 |
|----------|-----|
| 清查/数据年份 | **2023**（野外数据更新至 2023-07-31） |
| 地面样地来源年份 | 2019–2023（VMI13，第 13 次国家森林清查） |
| 遥感影像时段 | 2021–2023 生长季（北部拉普兰地区 2021–2023） |
| 数据时间范围（temporal） | 2023-01-01 ~ 2023-12-31 |
| 发布于 Paituli/Etsin（issued） | **2025-08-05** |
| 元数据最后修改（modified） | 2026-05-29 |
| 数据集版本 | v1 |
| 官方说明文档（LUETAMA-2023.txt）日期 | 2025-03-17 |

### 3. 目录结构与命名规则

```text
Finland_NFI_2023_GSV/
├── metadata.json               # Etsin Fairdata 数据集元数据（原始导出）
├── LUETAMA-2023.txt            # 官方产品说明（芬兰语，含方法/精度/主题清单）
├── 临时叙述.txt                # 下载来源备注
├── paituli_<批次ID>.zip        # Paituli 分主题下载的压缩包
└── paituli_<批次ID>/
    └── luke/
        ├── luke_ehdot.txt      # 许可与使用条款
        └── vmi/2023/
            └── <主题>_vmi1x_1923.tif
```

**命名规则**：`<主题英文名>_vmi1x_1923.tif`（`vmi1x` 表示 1km 格网分块交货；本批次为全国整幅）。

**文件格式说明**

| 文件 | 格式 | 说明 |
|------|------|------|
| `metadata.json` | JSON（UTF-8） | Etsin Fairdata 数据集元数据原始导出（含 ID/许可/空间范围/远程资源等） |
| `LUETAMA-2023.txt` | 纯文本（UTF-8） | 官方产品说明（芬兰语）：方法、精度误差表、45 主题清单与文件名对照 |
| `临时叙述.txt` | 纯文本（UTF-8） | 下载来源备注（数据集名称 + Paituli 链接） |
| `luke_ehdot.txt` | 纯文本（UTF-8） | 许可与使用条款（CC BY 4.0，芬英双语） |
| `paituli_<批次ID>.zip` | ZIP 压缩包 | 每包含 1 个主题 tif + `luke_ehdot.txt` |
| `<主题>_vmi1x_1923.tif` | GeoTIFF | 全国整幅蓄积量栅格（详见第 5 节） |

### 4. 数据清单（本次已下载 4 个主题）

| 文件名 | 主题 | 单位 | 大小 |
|--------|------|------|------|
| `tilavuus_vmi1x_1923.tif` | 立木蓄积量（总，全部树种） | m³/ha | 1907.6 MB |
| `manty_vmi1x_1923.tif` | 蓄积量 — 松树（Mänty） | m³/ha | 1707.1 MB |
| `kuusi_vmi1x_1923.tif` | 蓄积量 — 云杉（Kuusi） | m³/ha | 1371.0 MB |
| `koivu_vmi1x_1923.tif` | 蓄积量 — 桦木（Koivu） | m³/ha | 1319.6 MB |

> 完整产品含 45 个主题（另有各树种按材种分级的蓄积量、7 类生物量、平均树高/胸径/林龄/胸高断面积/郁闭度、地类/立地类型等），本次仅下载蓄积量相关 4 个。

### 5. 栅格内部格式（已用 rasterio 验证）

| 属性 | 值 |
|------|-----|
| 格式 / Driver | GeoTIFF（`GTiff`） |
| 波段 / 数据类型 | 单波段，`uint16` |
| 投影 | **EPSG:3067（ETRS-TM35FIN）** |
| 尺寸（width × height） | 42240 × 73472 |
| 像元 | 16m × 16m（transform 左上角起点 `(57632, 7778304)`，向北为负 y） |
| 压缩 | **LZW**（无损压缩） |
| 分块 | **tiled，512 × 512 块**，band 顺序（interleave=band） |
| 金字塔 | 内部 overviews：2/4/8/16/32/64/128/256（8 级，无外部 `.ovr`） |
| 像元参考 | `AREA_OR_POINT=Area`（面元，中心点代表 16m×16m 区域） |
| nodata | 32767 |
| 辅助文件 | 无外部 `.aux.xml` / `.ovr` / `.msk`（信息内嵌） |
| 值域 | 总蓄积量约 **0 ~ 750 m³/ha**（全国），分类间隔 1 m³/ha |

- 特殊值：
  - `32766`：应为林地但因云等未计算出结果
  - `32767`（nodata）：非林地（水域、其他地类）

#### 5.1 空间坐标范围（实测）

4 个主题栅格为同一幅全国镶嵌图，**坐标范围完全一致**。

**投影坐标边界（EPSG:3067，单位 m）**

| 边界 | 值 |
|------|-----|
| X 最小（left） | 57,632 |
| Y 最小（bottom） | 6,602,752 |
| X 最大（right） | 733,472 |
| Y 最大（top） | 7,778,304 |

**地理坐标范围（WGS84 经纬度）**

```
经度 lon：15.50°E  ~  33.13°E
纬度 lat：59.33°N  ~  70.11°N
```

**图幅跨度**

- 东西跨度：733472 − 57632 = **675,840 m**（约 676 km）
- 南北跨度：7778304 − 6602752 = **1,175,552 m**（约 1176 km）

> ⚠️ 上述为**矩形包围盒**，包含芬兰周边海域；真正的林区有效值仅出现在陆地上，非林地/水域像素均为 nodata（32767）。

### 6. 输入来源 / 输出去向

- **输入来源**：Paituli 平台分主题下载，解压后即为全国整幅栅格
- **输出去向**：供 `feature/` 特征提取或 `model/` 建模作为**蓄积量标签/真值**；使用前需按研究区（ROI）裁剪，并与 Sentinel-2 特征栅格重采样对齐（16m → 目标分辨率）

### 7. 参考引用

- Mäkisara, K., Katila, M. & Peräsaari, J. 2022. *The Multi-Source National Forest Inventory of Finland – methods and results 2017 and 2019.* Natural resources and bioeconomy studies 90/2022.
- Tomppo, E., Haakana, M., Katila, M. & Peräsaari, J. 2008. *Multi-source national forest inventory - Methods and applications.* Springer.
