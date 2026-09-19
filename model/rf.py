"""随机森林建模：省份间精度对比 + 空间分块交叉验证（西班牙 IFN4）

数据：data/feature/samples_sampled.csv（抽样后训练集；西班牙三省样本）
特征：研究方案 v1 的 **23 个特征**（定义见 `feature/extract.py` 的 `FEATURES`；
      详见 `项目开发文档.md` 8.11）—— 10 光谱波段 + NDVI/NDWI/NDRE
      + 3 个 50m std + 2 个 GLCM 纹理 + 2 个 100m 邻域 + 3 个地形
标签：GSV（m³/ha，IFN4 样地蓄积量）

模型矩阵（回答“省份间差异 + 分省/合并建模”研究问题）：
  ① {prov}_model : 单省样本训练 → 该省空间分块 CV 评估（leon / burgos / lugo）
  ② global_model : 全样本训练 → 空间分块 CV，按省份分别评估（对比分省/合并建模）

CV 方法：空间分块（KMeans 按坐标聚类成 5 个空间块 + GroupKFold 5 折），
  保证同一空间块的样本不跨训练/测试，避免空间自相关导致精度虚高。

指标：R² / RMSE / RMSE%（=RMSE/均值） / MAE，固定随机种子
输出：data/result/（指标汇总、特征重要性、模型文件）

用法：python -m model.rf [--smoke]
"""
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(line_buffering=True,     # 实时输出训练进度
                       errors="replace")        # 无法编码的符号替换，避免崩溃

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from feature.extract import FEATURES   # 特征定义单一来源（研究方案 v1，21 个；详见 项目开发文档.md 8.11）

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
    coords = df[["x", "y"]].to_numpy()

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


PROVINCES = ["leon", "burgos", "lugo"]


def main():
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(r"data/feature/samples_sampled.csv")
    if SMOKE:
        df = (df.groupby("province", group_keys=False)
                .apply(lambda g: g.sample(3000, random_state=SEED)))
        print(f"[SMOKE] 样本抽样至 {len(df)}")
    print(f"样本总数: {len(df)}  特征数: {len(FEATURES)}")

    summary = {}

    # ① 分省模型（每省独立建模/评估）
    for prov in PROVINCES:
        sub = df[df["province"] == prov].reset_index(drop=True)
        if len(sub) == 0:
            print(f"\n（跳过 {prov}：无样本）")
            continue
        print(f"\n=== 模型: {prov}_model ===")
        oof, overall, _, imp, models = spatial_block_cv(sub)
        summary[f"{prov}_model"] = overall
        pd.DataFrame({"feature": FEATURES, "importance": imp}).to_csv(
            RESULT_DIR / f"importance_{prov}.csv", index=False, float_format="%.5f")
        joblib.dump(models[-1], RESULT_DIR / f"rf_{prov}.joblib")

    # ② 全局模型（按省份分别评估，对比分省/合并建模）
    print("\n=== 模型: global_model（全样本）===")
    oof_all, overall_all, _, imp_all, models = spatial_block_cv(df)
    summary["global_model_all"] = overall_all
    pd.DataFrame({"feature": FEATURES, "importance": imp_all}).to_csv(
        RESULT_DIR / "importance_global.csv", index=False, float_format="%.5f")
    joblib.dump(models[-1], RESULT_DIR / "rf_global.joblib")
    for prov in PROVINCES:
        mask = (df["province"] == prov).to_numpy()
        if mask.sum():
            summary[f"global_on_{prov}"] = metrics(
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
