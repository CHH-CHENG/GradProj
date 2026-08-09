"""训练样本空间均匀抽样

从 samples.csv 中按 label（纯林/混交）分别抽样，采用**空间分箱抽样**：
将研究区按目标样本数划分为粗网格，每个空间箱内随机取 1 个样本，
既控制样本量，又降低相邻 30m 窗口的空间自相关。

输出：data/feature/samples_sampled.csv（默认每区 50000，共 100000）
用法：python -m feature.subsample [每区样本数]
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def spatial_subsample(df, n_target, seed=42):
    """按空间 2D 分箱，每箱随机取 1 个样本，约得 n_target 个"""
    if len(df) <= n_target:
        return df.copy()
    x = df["x_3067"].to_numpy()
    y = df["y_3067"].to_numpy()
    span = max(float(x.max() - x.min()), float(y.max() - y.min()))
    cell = span / max(int(np.sqrt(n_target)), 1)
    bx = ((x - x.min()) / cell).astype(int)
    by = ((y - y.min()) / cell).astype(int)
    key = by * (bx.max() + 1) + bx
    tmp = df.copy()
    tmp["_key"] = key
    rng = np.random.default_rng(seed)
    # 每箱随机取 1 个
    sampled = tmp.groupby("_key", sort=False).apply(
        lambda g: g.iloc[rng.integers(0, len(g))], include_groups=False
    ).reset_index(drop=True)
    return sampled


def main(n_per_region=None):
    if n_per_region is None:
        n_per_region = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
    src = Path(r"data/feature/samples.csv")
    out = Path(r"data/feature/samples_sampled.csv")
    df = pd.read_csv(src)

    parts = []
    for label, g in df.groupby("label", sort=False):
        s = spatial_subsample(g, n_per_region)
        parts.append(s)
        print(f"  {label}: {len(g)} → {len(s)}（目标 {n_per_region}）")
    out_df = pd.concat(parts, ignore_index=True)
    out_df.to_csv(out, index=False, float_format="%.4f")
    print(f"\n抽样后样本总数: {len(out_df)} → {out}")


if __name__ == "__main__":
    main()
