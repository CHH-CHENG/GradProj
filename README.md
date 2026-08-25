# 基于 Sentinel-2 多源遥感特征与随机森林的森林蓄积量估测研究

**（本科毕业设计）**

---

## 1. 项目简介

本项目基于 **Sentinel-2 多源遥感数据** 与 **机器学习方法（Random Forest）**，构建森林蓄积量估测模型，实现从遥感影像到森林蓄积量空间分布的自动化建模流程。

项目核心目标：

- 构建 **遥感数据 → 特征 → 模型 → 预测** 的完整工程化流程
- 对比 **不同数据类型 / 不同区域（纯林 vs 混交林）模型效果**
- 引入 **SHAP解释模型机制**
- 实现 **自动化数据获取 + 标准化处理 + 可复现建模**

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
特征提取
├── 光谱特征
├── 植被指数（NDVI/EVI 等）
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
│   ├── copernicus.yaml          # Copernicus 下载配置
│   └── preprocess.yaml          # 预处理参数配置
│
├── data/                        # 数据目录（不上传核心数据）
│   ├── inventory/               # 蓄积量标签数据
│   │   └── Finland_NFI_2023_GSV/  # 芬兰 MS-NFI 2023 蓄积量栅格（总/松/云/桦）
│   │
│   ├── Sentinel2/               # 遥感数据（芬兰典型区：纯林+混交）
│   │   ├── zip/Finland_PureMixed/   # 原始压缩包（8 个 L2A）
│   │   ├── SAFE/Finland_PureMixed/  # 解压产品（8 个 SAFE）
│   │   ├── roi/Finland_PureMixed/   # 裁剪影像（待生成）
│   │   └── indices/             # 植被指数
│   │
│   ├── DEM/                     # 地形数据
│   │   ├── raw/Finland_DEM_10m_2019/  # 芬兰 MML 10m DEM
│   │   └── roi/                 # 裁剪DEM
│   │
│   ├── feature/                 # 特征数据（samples.csv）
│   │
│   └── result/                  # 模型输出结果
│
├── downloader/                  # 数据下载模块
│   └── copernicus.py            # Copernicus 下载（矩形查询/按 tile 去重）
│
├── download_finland.py          # 芬兰典型区（纯林/混交）影像采集脚本
│
├── preprocess/                  # 数据预处理模块
│   ├── unzip.py                 # 解压 SAFE
│   ├── read_bands.py            # 波段读取 + 重采样
│   └── crop_roi.py              # ROI 裁剪
│
├── feature/                     # 特征工程模块（待实现）
│
├── model/                       # 模型训练模块（待实现）
│
├── utils/                       # 工具函数
│
├── DEVELOP_LOG.md               # 开发日志
│
├── 项目开发文档.docx.md          # 项目开发详细信息（含研究决策记录）
│
├── README.md                    # 当前文件
│
├── environment.yaml             # conda环境配置文件
│
└── main.py                      # 主入口
```

---

## 4. 数据说明

本项目使用三类核心数据：

### 4.1 蓄积量标签数据（Ground Truth）

- **来源**：Paituli / Etsin Fairdata 开放平台（芬兰 Luke）
- **当前已就位**：
  - **芬兰 MS-NFI 2023 蓄积量栅格**（`inventory/Finland_NFI_2023_GSV/`）：Luke 发布的全国蓄积量空间分布图（总蓄积量 + 松/云/桦分树种，m³/ha，16m 栅格，CC BY 4.0），作为蓄积量标签/参考
- **内容**：全国 16m 栅格（2023 年度，数据时点 2023-07-31），4 个主题（总/松/云/桦）
- **说明**：MS-NFI 为遥感估计值（参考标签），存在同源偏差；详细说明见研究决策记录 8.8

### 4.2 遥感数据（Sentinel-2）

- **来源**：Copernicus Data Space（CDSE）
- **获取方式**：自动下载（API），`download_finland.py` 按典型区采集，每 tile 取云量最少一期
- **当前数据（芬兰典型区）**：8 个 L2A 整 tile（2023 生长季），按研究用途分为：
  - **纯林区**（拉普兰纯松林，27.20E/68.76N）：`T35WMR/WMS/WNR/WNS`（2023-08-08）
  - **混交区**（24.97E/66.06N）：`T34WFT/WFU`、`T35WMN/WMP`（2023-07-10）
- **数据结构**：SAFE 格式，多光谱波段（10m/20m/60m）

### 4.3 地形数据（DEM）

- **用途**：提供地形特征（高程、坡度、坡向等）
- **当前已就位**：
  - **芬兰 MML 10m DEM 2019**（`DEM/raw/Finland_DEM_10m_2019/`）：芬兰全国最精确 DEM，10m、N2000、EPSG:3067、垂直精度约 1.4m，1523 个分块 GeoTIFF
- **策略**：按研究区裁剪（`DEM/roi/`），与 Sentinel-2 特征对齐

---

## 5. 运行方法

### 5.1 环境准备

```bash
conda env create -f environment.yml
conda activate GradProj
```

> ⚠️ 需安装 JP2 解码插件（读取 Sentinel-2 L2A 必需）：`conda install -c conda-forge libgdal-jp2openjpeg`

### 5.2 配置账号

在 `config/copernicus.yaml` 中填写（仅下载影像时需要）：

```yaml
username: your_email
password: your_password
```

### 5.3 运行主程序（芬兰工作流，`main.py` 统一入口）

各步骤幂等（已生成自动跳过），可单独执行或一键全流程：

```bash
python main.py all                  # 全流程：prepare → extract → subsample → train
python main.py prepare              # 研究区数据准备（S2/标签/DEM 对齐，EPSG:3067 10m）
python main.py extract              # 特征提取（30m 窗口 → samples.csv）
python main.py subsample 50000      # 空间均匀抽样（每区 5 万 → samples_sampled.csv）
python main.py train                # 模型训练（三模型矩阵 + 空间分块 CV）
python main.py train --smoke        # 冒烟测试（小样本 + 少量树，验证流程）
```

也可直接运行模块：`python -m preprocess.finland_study`、`python -m feature.extract`、`python -m feature.subsample [N]`、`python -m model.rf`


---

## 6. 结果展示（待补充）

---

## 7. 开发文档说明（重要）

本项目包含四类核心文档：

### 1.根目录 README.md（当前文件）

### 2.项目开发文档.docx.md

- 项目的详细信息、正确引导、开发/维护规则位于[项目开发文档.docx.md](./项目开发文档.docx.md)

### 3.模块目录和data子目录 README.md

- 介绍数据信息、模块信息

### 4.DEVELOP_LOG.md（开发日志）

- 开发过程与修改记录
- 当前实现状态
- 下一步开发计划
- 开发日志

## 8.使用建议与要求（针对 AI ）

当接手本项目时：

1. 如果ai是首次接手该项目，应先读取**项目开发文档.docx.md**，了解本项目开发和维护规则
2. 不应在未先尝试使用系统已有的conda环境下，直接创建新临时conda环境，系统conda环境命名为**GradProj**

---
