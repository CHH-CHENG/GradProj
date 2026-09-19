# 结果输出目录

放置模型训练、评估与预测结果。

## 放置的数据（⏳ 待生成）

| 输出 | 说明 | 产生位置 |
|------|------|---------|
| `metrics_summary.csv` | 各模型精度汇总（R² / RMSE / RMSE% / MAE / n） | `model/rf.py` |
| `importance_{province}.csv` | 分省模型特征重要性（leon / burgos / lugo） | `model/rf.py` |
| `importance_global.csv` | 全局模型特征重要性 | `model/rf.py` |
| `rf_{province}.joblib`、`rf_global.joblib` | 训练好的随机森林模型 | `model/rf.py` |
| 消融实验指标 | 去掉纹理 / 邻域后的精度对比（研究方案 v1 的 E 节） | ⏳ 待实现 |
| SHAP 解释图 | 特征贡献 / 依赖关系图 | ⏳ 待实现（计划 `model/shap.py`） |
| 蓄积量预测栅格 | 研究区空间预测结果（GeoTIFF） | ⏳ 待实现 |

## 数据类型
- CSV（指标 / 重要性）、joblib（模型）、PNG（图）、GeoTIFF（预测栅格）

## 数据内部格式
（随产物生成后补充）
