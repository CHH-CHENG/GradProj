# model 模块（模型训练与评估）

基于特征样本训练森林蓄积量估测模型，并输出精度评估与模型解释结果。

> ⏳ **当前状态**：`rf.py` 逻辑已就绪（分省 + 全局模型矩阵 + 空间分块 CV），
> 待西班牙 `samples_sampled.csv` 生成后即可运行。

## 脚本说明

### rf.py（随机森林建模）
- 功能：
  - 随机森林回归训练
  - **模型矩阵**：①分省模型（leon / burgos / lugo 各自独立建模）、②全局模型（全样本训练，按省份分别评估 —— 对比分省/合并建模）
  - **空间分块交叉验证**：KMeans 按坐标聚成 5 个空间块 + GroupKFold 5 折（避免空间自相关虚高精度）
  - 精度评估（R² / RMSE / RMSE% / MAE）+ 特征重要性
  - SHAP 解释（可选，后续）
- **输入**：`data/feature/samples_sampled.csv`（**23 特征**（研究方案 v1）+ `GSV` 标签）
- **输出**：`data/result/`（`metrics_summary.csv`、`importance_{省份|global}.csv`、`rf_{省份|global}.joblib`）
- 用法：`python -m model.rf`（加 `--smoke` 冒烟测试）
- **要求**：固定随机种子（42）、可复现

## 评估指标
- R²：决定系数
- RMSE：均方根误差（m³/ha）
- RMSE%：相对均方根误差（RMSE / 均值 × 100%）
- MAE：平均绝对误差（m³/ha）
