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
│   ├── inventory/               # 样地调查数据
│   │
│   ├── Sentinel2/               # 遥感数据
│   │   ├── zip/                 # 原始压缩包
│   │   ├── SAFE/                # 解压产品
│   │   ├── roi/                 # 裁剪影像
│   │   └── indices/             # 植被指数
│   │
│   ├── DEM/                     # 地形数据
│   │   ├── raw/                 # 原始DEM
│   │   └── roi/                 # 裁剪DEM
│   │
│   ├── feature/                 # 特征数据（samples.csv）
│   │
│   └── result/                  # 模型输出结果
│
├── downloader/                  # 数据下载模块
│   └── copernicus.py
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
├── 项目开发文档.docx             # 项目开发详细信息
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

### 4.1 样地数据（Ground Truth）

- **来源**：导师提供/通过互联网获取
- **类型**：
  - 混交林（xlsx）
  - 纯林（accdb）
- **内容**：
  - 样地位置（经纬度）
  - 森林蓄积量（标签）

### 4.2 遥感数据（Sentinel-2）

- **来源**：Copernicus Data Space
- **获取方式**：自动下载（API）
- **数据结构**：
  - SAFE 格式
  - 多光谱波段（10m / 20m / 60m）

### 4.3 地形数据（DEM）

- **用途**：提供地形特征（高程、坡度等）
- **来源**：
  - SRTM / ASTER GDEM / Copernicus DEM
- **当前策略**：
  - 手动下载 + 项目内使用

---

## 5. 运行方法

### 5.1 环境准备

```bash
conda env create -f environment.yml
conda activate GradProj
```

### 5.2 配置账号

在 `config/copernicus.yaml` 中填写：

```yaml
username: your_email
password: your_password
```

### 5.3 运行主程序

```bash
python main.py
```

---

## 6. 结果展示（待补充）

---

## 7. 开发文档说明（重要）

本项目包含四类核心文档：

### 根目录 README.md（当前文件）

### 项目开发文档.docx

- 项目的详细信息、正确引导、开发/维护规则位于[项目开发文档.docx](./项目开发文档.docx)

### 模块目录和data子目录 README.md

- 介绍数据信息、模块信息

### DEVELOP_LOG.md（开发日志）

- 开发过程与修改记录
- 当前实现状态
- 下一步开发计划
- 开发日志

### 使用建议与要求（针对 AI ）

当接手本项目时：

1. 如果ai是首次接手该项目，应先读取**项目开发推进文档.docx**，了解本项目开发和维护规则
2. 不应在未先尝试使用系统已有的conda环境下，直接创建新临时conda环境，系统conda环境命名为**GradProj**

---
