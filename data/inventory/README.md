# 蓄积量标签数据目录

放置**蓄积量标签数据**（Ground Truth）。按数据来源分类，每个来源一个独立文件夹。

> 📌 历史说明：早期测试/临时数据（秦岭角规调查、芬兰 MS-NFI 栅格）已因研究方案调整移除；**当前研究全面聚焦西班牙 IFN4**。

## 子目录结构

```text
inventory/
├── README.md
└── IFN4（Cuarto Inventario Forestal Nacional de España）/
    ├── 1~3. *.pdf                              # 官方手册（采集/处理/评估）
    ├── Bases de datos de campo/                # 野外数据库（Ifn4p*.accdb）
    ├── Bases de datos Sig/                     # GIS 数据库（Sig_*.accdb）
    └── Tablas de resultados IFN4/              # 结果统计表（xlsx 集 zip）
```

## 数据总览

| 数据 | 来源 | 类型 | 格式 | 位置 | 状态 |
|------|------|------|------|------|------|
| IFN4 三省野外数据库 | MITECO（西班牙生态转型部） | 样地/树木调查 | ACCDB | `.../Bases de datos de campo/` | ✅ 已就位 |
| IFN4 三省 GIS 数据库 | MITECO | 样地空间/地块 | ACCDB | `.../Bases de datos Sig/` | ✅ 已就位 |
| IFN4 三省结果统计表 | MITECO | 统计表 | XLSX/XLS | `.../Tablas de resultados IFN4/` | ✅ 已就位 |

---

## IFN4（Cuarto Inventario Forestal Nacional de España）

### 1. 数据简介

**IFN4（Cuarto Inventario Forestal Nacional de España）**——西班牙第四次国家森林清查，由 **MITECO**（生态转型与人口挑战部）组织实施。本目录包含**三个省份**的野外调查数据库、GIS 数据库与结果统计表：

| 省份 | 代码 | 野外数据库 | GIS 数据库 | IFN4 调查年 | 样地数 |
|------|------|-----------|-----------|------------|--------|
| Burgos（布尔戈斯） | 09 | `Ifn4p09-burgos.accdb` | `Sig_Burgos.accdb` | **2018**（+2019 少量） | 2076 |
| León（莱昂） | 24 | `Ifn4p24-leon.accdb` | `Sig_León.accdb` | **2019**（+2005/2013 少量） | 1401 |
| Lugo（卢戈） | 27 | `Ifn4p27-lugo.accdb` | `Sig_Lugo.accdb` | **2009**（日期 2009-05~09） | 2452 |

- 下载来源：MITECO 官方公开数据（territorio 服务，`tcm30-*` 编号）
- 研究优先级：**León 优先**（第一步重点），其余省份可更换或暂缓

### 2. 时间信息（与 Sentinel-2 匹配）

| 省份 | IFN4 调查年 | 调查日期范围 | 拟用 S2 时间窗 |
|------|------------|-------------|---------------|
| León | 2019 | —（待查） | 2019-06-01 ~ 09-15 |
| Burgos | 2018 | 2018-02 ~ 2019-01 | 2018-06-01 ~ 09-15 |
| Lugo | 2009 | 2009-05-26 ~ 09-24 | ⚠️ **2009 无 S2**（2015 年起才有）→ 暂定 2016 生长季 |

> ⚠️ 时间差异说明：Sentinel-2 自 2015 年 6 月起可用；Lugo 的 IFN4（2009）无同期影像，
> 经研究确认为可接受（自然生长差异有限），暂用 2016 年生长季影像替代。

### 3. 目录结构与文件清单

```text
IFN4（Cuarto Inventario Forestal Nacional de España）/
├── 1.MANUAL_TOMA_DATOS_CAMPO_IFN4.pdf       # 野外数据采集手册
├── 2.MANUAL_PROCESO_DATOS_IFN4.pdf          # 数据处理手册（含材积公式）
├── 3.MANUAL_VALORACIÓN_IFN4.pdf             # 木材价值评估手册
├── Bases de datos de campo/                 # 野外调查数据库（已解压）
│   ├── Ifn4p09-burgos.accdb (+zip)          # Burgos 2018
│   ├── Ifn4p24-leon.accdb (+zip)            # León 2019（重点）
│   └── Ifn4p27-lugo.accdb (+zip)            # Lugo 2009
├── Bases de datos Sig/                      # GIS 数据库（已解压）
│   ├── Sig_Burgos.accdb (+zip)
│   ├── Sig_León.accdb (+zip)
│   └── Sig_Lugo.accdb (+zip)
└── Tablas de resultados IFN4/               # 省级统计结果表（zip 未解压）
    ├── burgos_tcm30-545832.zip（130 项 xlsx）
    ├── leon_tcm30-545838.zip（127 项）
    └── lugo_tcm30-545839.zip（104 项 xls）
```

### 4. 野外数据库结构（已解析，以 Burgos 为例）

**表清单（9 张）**：

| 表 | 行数（Burgos） | 内容 |
|----|--------------|------|
| **PCParcelas** | 2076 | 样地核心表（48 字段：省份/样地号 `Estadillo`/年份 `Ano`/调查日期 `FechaIni`·`FechaFin`/郁闭度/土壤/地形…） |
| **PCDatosMap** | 2079 | 样地定位表（**坐标 `CoorX`/`CoorY` + `Huso` 分区 + 50k 图幅 `Hoja50`**） |
| **PCMayores** | 48332 | 大树数据（22 字段：树种 `Especie`/胸径 `Dn1`·`Dn2`(mm)/树高 `Ht`(m)/方位 `Rumbo`/距离 `Distanci` 等） |
| PCMayores3 | 36341 | 大树补充表（19 字段） |
| PCRegenera | 12980 | 更新/幼苗 |
| PCEspParc / PCEspMapa | 3793 / 4368 | 样地/地图物种组成 |
| PCMatorral | 10895 | 灌木 |
| PCNueEsp | 8973 | 新记录物种 |

> ⚠️ **蓄积量无现成字段**：需从 `PCMayores`（树种 × 胸径 × 树高 + 样地统计扩展系数）按 IFN4 官方材积公式计算样地级蓄积量。

### 5. 坐标系（⚠️ 重要）

- **Burgos**：样地坐标为 UTM zone 30（`Huso=30`）→ 对应 **EPSG:25830**（ETRS89 / UTM 30N）
- **Lugo**：`Huso=29` → 对应 **EPSG:25829**
- **León**：`Huso` 字段存在错误（661 条标为 29），经核验**全部坐标实为 EPSG:25830**（按 25830 转换后 100% 落在 León 省合理范围内：lon[-7.05, -4.78]，lat[42.11, 43.21]）

> 使用样地坐标时：**León 统一按 EPSG:25830 处理**；Burgos 按 25830；Lugo 按 25829。

#### 5.1 三省空间范围（WGS84，供 S2 下载用）

| 省份 | 经度范围 | 纬度范围 | 样地数 | S2 tile 数（去重后） |
|------|---------|---------|--------|---------------------|
| León | -7.10 ~ -4.72 | 42.05 ~ 43.26 | 1401 | 10 |
| Burgos | -4.34 ~ -2.52 | 41.46 ~ 43.19 | 2076 | 9 |
| Lugo | -7.98 ~ -6.80 | 42.33 ~ 43.74 | 2452 | 6 |

### 6. 输入来源 / 输出去向

- **输入来源**：MITECO 官方公开数据（`tcm30-*` 编号），三省份 IFN4 数据包
- **输出去向**：
  - 样地坐标 + **样地蓄积量**（从 `PCMayores` 计算的 m³/ha）→ `feature/` 的**标签 y**
  - GIS 数据库 → 样地空间分布、研究区范围确定
  - 与 Sentinel-2 特征按样地位置匹配（样地缓冲窗口内取特征）

### 7. 参考

- `1.MANUAL_TOMA_DATOS_CAMPO_IFN4.pdf`（野外采集规范）
- `2.MANUAL_PROCESO_DATOS_IFN4.pdf`（数据处理规范，含材积公式）
- `3.MANUAL_VALORACIÓN_IFN4.pdf`（价值评估规范）

### 8. Sentinel-2 影像（配套下载）

三省的 S2 影像由 `python -m downloader.spain` 采集（下载记录见 `data/Sentinel2/README.md`）：
- **León（重点）**：2019 生长季，10 个 tile，约 10.0 GB
- Burgos：2018 生长季，9 个 tile，约 7.9 GB
- Lugo：2016 生长季（替代 2009），6 个 tile，约 5.5 GB
