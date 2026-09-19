# 基于 Sentinel-2 多源遥感特征与随机森林的森林蓄积量估测研究

**（本科毕业设计）**

---

## 1. 项目简介

本项目基于 **Sentinel-2 多源遥感数据** 与 **机器学习方法（Random Forest）**，构建森林蓄积量估测模型，实现从遥感影像到森林蓄积量空间分布的自动化建模流程。

项目核心目标：

- 构建 **遥感数据 → 特征 → 模型 → 预测** 的完整工程化流程
- 对比 **不同省份（León / Burgos / Lugo）森林蓄积量估测效果**
- 引入 **SHAP解释模型机制**
- 实现 **自动化数据获取 + 标准化处理 + 可复现建模**

> 📌 **当前研究区（2026-09 起）**：全面更换为**西班牙 IFN4**（第四次国家森林清查），使用 **León（主实验）/ Burgos（过渡区）/ Lugo（域外测试）** 三省数据（详见 `data/inventory/README.md`）。
>
> 🧩 **研究方案与创新点**：见 `项目开发文档.md` 第 **8.11 节**（23 特征体系 / 3 条创新点 / 实验设计）。

---

## 2. 科研/项目路线

```text
样地调查数据
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
      自动解压 SAFE
        │
        ▼
      波段读取
        │
        ▼
      重采样（统一 10m）
        │
        ▼
      ROI 裁剪（按样地）
        │
        ▼
特征提取（研究方案 v1，共 23 特征）
├── 基础光谱（B02~B12、B8A）
├── 植被指数（NDVI/NDWI/NDRE）
├── 多尺度统计（50m std）
├── 结构-纹理（NDVI GLCM）
├── 结构-邻域（100m NDVI 统计）
└── 地形特征（DEM）
        │
        ▼
特征选择
        │
        ▼
Random Forest
        │
        ▼
SHAP 解释
        │
        ▼
蓄积量空间预测
```

---

## 3. 项目文件/目录结构

```text
ProjCode/
│
├── config/                      # 配置文件（路径 / 参数 / 账号等）
│   ├── copernicus.yaml          # Copernicus 下载账号（.gitignore 排除）
│   ├── copernicus.example.yaml  # 账号配置模板
│   ├── preprocess.yaml          # 预处理参数（波段 / 重采样 / ROI）
│   └── spain_study.yaml         # 西班牙 IFN4 研究区配置（三省）
│
├── data/                        # 数据目录（核心数据不上传）
│   ├── inventory/               # IFN4 三省数据（蓄积量标签来源）
│   │   └── IFN4（...）/
│   │       ├── Bases de datos de campo/   # 野外数据库（样地/树木 accdb）
│   │       ├── Bases de datos Sig/        # GIS 数据库
│   │       └── Tablas de resultados IFN4/ # 统计结果表
│   │
│   ├── Sentinel2/               # 遥感数据（西班牙三省）
│   │   ├── zip/Spain_IFN4/<省>/ # 原始压缩包（25 个，已完成）
│   │   ├── SAFE/Spain_IFN4/     # 解压产品（25 个，已完成）
│   │   ├── roi/                 # 裁剪影像（⏳ 待生成）
│   │   └── indices/             # 植被指数（⏳ 待生成）
│   │
│   ├── DEM/                     # 地形数据（西班牙 DEM ⏳ 待获取）
│   │   ├── raw/
│   │   └── roi/
│   │
│   ├── feature/                 # 特征数据（⏳ 待生成 samples.csv）
│   │
│   └── result/                  # 模型输出结果
│
├── downloader/                  # 数据下载模块
│   ├── copernicus.py            # CDSE 通用下载（矩形查询 / 按 tile 去重 / 断点续传）
│   ├── spain.py                 # 西班牙三省 S2 采集脚本
│   ├── estimate.py              # S2 下载量估算脚本
│   └── dem.py                   # 西班牙 DEM 批量下载（CNIG WCS-INSPIRE，免账号）
│
├── preprocess/                  # 数据预处理模块
│   ├── unzip.py                 # 解压 SAFE（支持递归子目录）
│   ├── read_bands.py            # 波段读取 + 重采样
│   └── crop_roi.py              # ROI 裁剪
│
├── feature/                     # 特征工程模块
│   ├── extract.py               # 特征提取与样本构建（⏳ 西班牙版待实现）
│   └── subsample.py             # 空间均匀抽样
│
├── model/                       # 模型训练模块
│   └── rf.py                    # 随机森林建模 + 空间分块 CV
│
├── utils/                       # 工具函数（⏳ 待补充）
│
├── docs/                        # 研究文档
│   └── 研究方案_探讨记录.md       # 研究方案探讨过程（收敛稿；结论见 项目开发文档.md 8.11）
│
├── DEVELOP_LOG.md               # 开发日志（当前）
├── DEVELOP_LOG_ARCHIVE.md       # 历史开发日志归档（初始化 / 秦岭 / 芬兰阶段）
│
├── 项目开发文档.md               # 项目开发详细信息（含研究决策记录）
│
├── README.md                    # 当前文件
│
├── environment.yaml             # conda 环境配置文件
│
└── main.py                      # 主入口
```

---

## 4. 数据说明

本项目使用三类核心数据：

### 4.1 蓄积量标签数据（Ground Truth）

- **来源**：MITECO（西班牙生态转型部）IFN4 公开数据
- **当前已就位**：`inventory/IFN4（...）/` 三省（**León 优先** / Burgos / Lugo）的：
  - 野外数据库（样地/树木，accdb；蓄积量需从树木数据 `PCMayores` 计算）
  - GIS 数据库（`Sig_*.accdb`）、结果统计表
- **调查年**：León 2019 / Burgos 2018 / Lugo 2009（详见 `data/inventory/README.md`）

### 4.2 遥感数据（Sentinel-2）

- **来源**：Copernicus Data Space（CDSE）
- **获取方式**：`python -m downloader.spain` 按省采集（全省矩形查询 → 按 tile 去重，每 tile 取云量最少一期）
- **当前数据（西班牙三省，✅ 已就绪）**：25 个 L2A 整 tile（约 21.3 GB）
  - **León（优先）**：2019 生长季，10 tile ≈ 10 GB
  - Burgos：2018 生长季，9 tile ≈ 7.9 GB
  - Lugo：2016 生长季（替代无同期影像的 2009），6 tile ≈ 5.5 GB

### 4.3 地形数据（DEM）

- **来源**：CNIG / IDEE WCS-INSPIRE（`https://servicios.idee.es/wcs-inspire/mdt`，免账号）
- **获取方式**：`python -m downloader.dem`（按省 bbox 自动分块、幂等、带清单校验）
- **当前数据（✅ 已下载，2026-09-19）**：三省全域 bbox，EPSG:25830 / int16
  - **25m**（MDT25）：16 块，0.26 GB
  - **5m**（MDT05）：241 块，约 7.7 GB
- **策略**：按研究区裁剪到 `DEM/roi/`，与 Sentinel-2 特征对齐（详见 `data/DEM/README.md`）

---

## 5. 运行方法

### 5.1 环境准备

项目使用**本地 conda 环境** `.conda`（与代码同目录，自包含）：

```bash
conda activate E:\GradProj\ProjCode\.conda
```

或在其他机器上复现：

```bash
conda env create -f environment.yaml
```

依赖清单见 `environment.yaml`（Python 3.13 + numpy/pandas/scipy/scikit-learn/rasterio/geopandas/shapely/pyproj/pyodbc/xgboost/lightgbm/shap/scikit-image 等）。

> ✅ **无需另装 JP2 解码插件**：`rasterio` 官方 wheel 自带 GDAL 3.12.4 与 `JP2OpenJPEG` 驱动，已实测可解码 Sentinel-2 JP2 波段。

### 5.2 配置账号

复制模板并填写（仅下载影像时需要）：

```bash
Copy-Item config\copernicus.example.yaml config\copernicus.yaml
```

```yaml
username: your_email
password: your_password
```

> 也可用环境变量 `CDSE_USER` / `CDSE_PASS`（优先级更高）。

### 5.3 数据采集与主程序

**① 西班牙 Sentinel-2 下载（✅ 已完成 25/25）**：

```bash
python -m downloader.estimate             # 下载量估算（查询产品总大小）
python -m downloader.spain --dry-run leon # 预览 León 待下载产品
python -m downloader.spain leon           # 下载 León（优先）
python -m downloader.spain all            # 下载三省（约 21.3 GB）
```

**② 主程序（`main.py`）**：

```bash
python main.py download all   # Sentinel-2 下载
python main.py unzip          # 解压 SAFE
python main.py roi            # 研究区裁剪（需 config/preprocess.yaml 研究区确定）
python main.py extract        # 特征提取（⏳ 待实现）
python main.py subsample      # 空间均匀抽样
python main.py train --smoke  # 建模（冒烟测试）
```

> ⏳ 西班牙流程中 `roi`（研究区范围待定）、`extract`（依赖 DEM 与样地蓄积量）尚未就绪，
> 详见 `项目开发文档.md`。


---

## 6. 结果展示（待补充）

---

## 7. 开发文档说明（重要）

本项目包含四类核心文档：

### 1.根目录 README.md（当前文件）

### 2.项目开发文档.md

- 项目的详细信息、正确引导、开发/维护规则位于[项目开发文档.md](./项目开发文档.md)

### 3.模块目录和data子目录 README.md

- 介绍数据信息、模块信息

### 4.DEVELOP_LOG.md（开发日志）

- 开发过程与修改记录
- 当前实现状态
- 下一步开发计划
- 开发日志

## 8.使用建议与要求（针对 AI ）

当接手本项目时：

1. 如果ai是首次接手该项目，应先读取**项目开发文档.md**，了解本项目开发和维护规则
2. 项目解释器环境为**项目本地 `.conda`**（`E:\GradProj\ProjCode\.conda`，Python 3.13；依赖见 `environment.yaml`）；不应在未先尝试使用该环境的情况下，另行创建新的临时 conda 环境

---
