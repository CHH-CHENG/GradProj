"""随机森林建模：纯林 vs 混交林精度对比 + 空间分块交叉验证

数据：data/feature/samples_sampled.csv（抽样后训练集，默认 9.2 万样本）
特征：10 光谱波段 + NDVI/EVI/NDWI/NDRE + DEM 高程/坡度/坡向（17 个）
标签：GSV（m³/ha，窗口中心 MS-NFI 蓄积量）

模型矩阵（回答"纯林 vs 混交林"研究问题）：
  ① mixed_model   : 混交样本训练 → 混交空间分块 CV 评估
  ② pure_model    : 纯林样本训练 → 纯林空间分块 CV 评估
  ③ global_model  : 全样本训练 → 空间分块 CV，按 label 分别评估（对比分开/合并建模）

CV 方法：空间分块（KMeans 按坐标聚类成 5 个空间块 + GroupKFold 5 折），
  保证同一空间块的样本不跨训练/测试，避免空间自相关导致精度虚高。

指标：R² / RMSE / RMSE%（=RMSE/均值） / MAE，固定随机种子
输出：data/result/（指标汇总、特征重要性、模型文件）

用法：python -m model.rf
"""
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True)   # 实时输出训练进度

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

FEATURES = ["B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B11", "B12",
            "NDVI", "EVI", "NDWI", "NDRE", "DEM_elev", "DEM_slope", "DEM_aspect"]
SEED = 42
N_SPLITS = 5
SMOKE = os.environ.get("RF_SMOKE") == "1"
N_ESTIMATORS = 30 if SMOKE else 200

RESULT_DIR = Path(r"data/result")


def metrics(y, p):
    r2 = float(r2_score(y, p))
    rmse = float(np.sqrt(mean_squared_error(y, p)))
    mae = float(mean_absolute_error(y, p))
    rrmse = rmse / float(np.mean(y)) * 100.0
    return {"R2": round(r2, 4), "RMSE": round(rmse, 3),
            "RMSE_pct": round(rrmse, 2), "MAE": round(mae, 3),
            "n": int(len(y)), "mean_y": round(float(np.mean(y)), 2)}


def spatial_block_cv(df, n_estimators=N_ESTIMATORS, n_splits=N_SPLITS, seed=SEED):
    """空间分块交叉验证：KMeans 坐标聚类分块 + GroupKFold

    返回 (oof 预测, 总体指标, 每折指标, 特征重要性均值, 模型列表)
    """
    X = df[FEATURES].to_numpy()
    y = df["GSV"].to_numpy()
    coords = df[["x_3067", "y_3067"]].to_numpy()

    km = KMeans(n_clusters=n_splits, random_state=seed, n_init=10).fit(coords)
    blocks = km.labels_
    print(f"    空间分块样本分布: {np.bincount(blocks).tolist()}")

    gkf = GroupKFold(n_splits=n_splits)
    oof = np.full(len(df), np.nan)
    importance = np.zeros(len(FEATURES))
    fold_metrics, models = [], []
    for fold, (tr, te) in enumerate(gkf.split(X, y, groups=blocks)):
        rf = RandomForestRegressor(n_estimators=n_estimators,
                                   random_state=seed, n_jobs=-1)
        rf.fit(X[tr], y[tr])
        oof[te] = rf.predict(X[te])
        importance += rf.feature_importances_
        fm = metrics(y[te], oof[te])
        fold_metrics.append(fm)
        models.append(rf)
        print(f"    fold{fold}: 训练{len(tr)} 测试{len(te)}  R2={fm['R2']} RMSE%={fm['RMSE_pct']}")
    importance /= n_splits
    return oof, metrics(y, oof), fold_metrics, importance, models


def main():
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(r"data/feature/samples_sampled.csv")
    if SMOKE:
        df = (df.groupby("label", group_keys=False)
                .apply(lambda g: g.sample(3000, random_state=SEED)))
        print(f"[SMOKE] 样本抽样至 {len(df)}")
    print(f"样本总数: {len(df)}  特征数: {len(FEATURES)}")

    summary = {}
    oof_store = {}

    # ① 混交模型
    print("\n=== 模型① mixed_model（混交样本）===")
    sub = df[df["label"] == "mixed"].reset_index(drop=True)
    oof, overall, _, imp, models = spatial_block_cv(sub)
    summary["mixed_model"] = overall
    oof_store["mixed_model"] = (sub, oof)
    pd.DataFrame({"feature": FEATURES, "importance": imp}).to_csv(
        RESULT_DIR / "importance_mixed.csv", index=False, float_format="%.5f")
    joblib.dump(models[-1], RESULT_DIR / "rf_mixed.joblib")

    # ② 纯林模型
    print("\n=== 模型② pure_model（纯林样本）===")
    sub = df[df["label"] == "pure"].reset_index(drop=True)
    oof, overall, _, imp, models = spatial_block_cv(sub)
    summary["pure_model"] = overall
    oof_store["pure_model"] = (sub, oof)
    pd.DataFrame({"feature": FEATURES, "importance": imp}).to_csv(
        RESULT_DIR / "importance_pure.csv", index=False, float_format="%.5f")
    joblib.dump(models[-1], RESULT_DIR / "rf_pure.joblib")

    # ③ 全局模型（按 label 分别评估）
    print("\n=== 模型③ global_model（全样本）===")
    oof_all, overall_all, _, imp_all, models = spatial_block_cv(df)
    summary["global_model_all"] = overall_all
    pd.DataFrame({"feature": FEATURES, "importance": imp_all}).to_csv(
        RESULT_DIR / "importance_global.csv", index=False, float_format="%.5f")
    joblib.dump(models[-1], RESULT_DIR / "rf_global.joblib")
    for label in ["pure", "mixed"]:
        mask = (df["label"] == label).to_numpy()
        summary[f"global_model_on_{label}"] = metrics(
            df.loc[mask, "GSV"].to_numpy(), oof_all[mask])

    # 汇总
    print("\n================ 结果汇总 ================")
    cols = ["n", "mean_y", "R2", "RMSE", "RMSE_pct", "MAE"]
    sdf = pd.DataFrame(summary).T[cols]
    print(sdf.to_string())
    sdf.to_csv(RESULT_DIR / "metrics_summary.csv", float_format="%.4f")
    print(f"\n结果已保存至 {RESULT_DIR}/")


if __name__ == "__main__":
    main()
