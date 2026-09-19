# feature 模块（特征工程）

从研究区对齐栅格（S2 + 蓄积量标签 + DEM）提取建模特征，生成训练样本表 `samples.csv`。

> ⏳ **当前状态**：`extract.py` 为西班牙版**骨架**（通用函数就绪，数据加载待实现）；
> `subsample.py` 已就绪（按省份分组抽样）。

## 脚本说明

### extract.py（特征提取与样本构建）—— ⏳ 待实现
- 规划：
  - 从 `data/Sentinel2/roi/Spain_IFN4/` 研究区栅格提取光谱特征
  - 关联 IFN4 样地蓄积量标签（由 `PCMayores` 树木表按官方材积公式计算）与 DEM
  - 生成 `data/feature/samples.csv`
- 样本单元：**样地缓冲窗口**（如 20~30m），标签取样地蓄积量
- 特征（23 个，研究方案 v1 —— 详见 `项目开发文档.md` 8.11）：

  | 组 | 计算方式 | 特征 |
  |---|---|---|
  | ① 基础光谱 | 30m 窗口（3×3）均值 | B02 B03 B04 B05 B06 B07 B08 B8A B11 B12 |
  | ② 植被指数 | 同上 | NDVI NDWI NDRE |
  | ③ 多尺度（受控） | 50m 窗口（5×5）std，仅关键变量 | NDVI_std50 NDRE_std50 B8_std50 |
  | ④ 结构-纹理 | NDVI → GLCM 7×7 / 16 灰度级 / 4 方向均值 | GLCM_contrast GLCM_entropy |
  | ⑤ 结构-邻域 | 100m 窗口（10×10） | NDVI_mean100 NDVI_std100 |
  | ⑥ 地形 | 30m 窗口（DEM 就绪后启用） | DEM_elev DEM_slope DEM_aspect |

- 尺度依据：IFN4 样地最大半径 25m（50m = 样地边界；100m 属景观背景，需论证）
- SWIR：**已纳入 B11/B12**（2026-09-19 决策；文献中对生物量/蓄积量贡献显著）
- 特征定义在代码中为**单一来源**（`feature/extract.py` 的 `FEATURES`）
- 已提供通用函数：`calc_indices()`、`compute_slope_aspect()`
- **输入**（待就绪）：研究区 S2 栅格、IFN4 样地蓄积量 CSV、DEM
- **输出**：`data/feature/samples.csv`
  - 列：`sample_id` / `province` / `plot_id` / `x` / `y` / 上述 23 特征 / `GSV`

### subsample.py（训练样本空间均匀抽样）—— ✅ 已就绪
- 功能：从 `samples.csv` 按 `province`（省份）分别**空间分箱抽样**（研究区按目标样本数划分粗网格，每箱随机取 1 个），既控制样本量又降低相邻窗口的空间自相关
- 用法：`python -m feature.subsample [每省样本数]`（默认 50000）
- 输出：`data/feature/samples_sampled.csv`
