# feature 模块（特征工程）

从研究区对齐栅格（S2 + MS-NFI 标签 + DEM）提取建模特征，生成训练样本表 `samples.csv`。

> ✅ **已实现**：`extract.py` 已打通，生成 76.3 万样本。

## 脚本说明

### extract.py（特征提取与样本构建）
- 功能：
  - 从 `data/Sentinel2/roi/Finland_PureMixed/<id>_S2_10m_3067.tif` 提取特征
  - 关联 MS-NFI 蓄积量标签（`data/feature/finland_study/<id>_GSV_10m_3067.tif`）与 DEM
  - 生成训练数据 `data/feature/samples.csv`
- 样本单元：**30m×30m 窗口**（10m 网格下 3×3 像元，步长 30m 不重叠），标签取窗口中心 GSV
- 特征类型：
  - 光谱特征（B02~B12，窗口均值，10 个）
  - 植被指数：NDVI / EVI / NDWI / NDRE
  - 地形特征：DEM 高程 / 坡度 / 坡向（窗口均值）
- 过滤：窗口中心 GSV 为 nodata（非林地）剔除；窗口内 S2 无有效值剔除
- **输入**：`config/finland_study.yaml` 定义的区域数据
- **输出**：`data/feature/samples.csv`（每行一个 30m 样本，含特征 X + 标签 GSV + region/label 分组列）
- **规模**：76.3 万样本（纯林 38.8 万 + 混交 37.5 万），0 NaN

### subsample.py（训练样本空间均匀抽样）
- 功能：从 `samples.csv` 按 label 分别**空间分箱抽样**（研究区按目标样本数划分粗网格，每箱随机取 1 个），既控制样本量又降低相邻 30m 窗口的空间自相关
- 用法：`python -m feature.subsample [每区样本数]`（默认 50000）
- 输出：`data/feature/samples_sampled.csv`（默认约 9.2 万样本）
- 验证：抽样后 GSV 分布与完整集一致（纯林 mean 77.8 vs 77.9；混交 81.4 vs 82.9），空间覆盖完整
