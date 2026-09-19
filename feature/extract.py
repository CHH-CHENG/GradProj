"""特征提取与样本构建（西班牙 IFN4 研究）

⏳ **待实现**：西班牙流程的输入数据尚未就绪（DEM 待获取、样地蓄积量待计算），
本文件提供**可复用的通用函数**与特征规划，待数据就绪后补充数据加载与样本组装。

## 特征体系（研究方案 v1，详见 `项目开发文档.md` 8.11）

共 23 个特征：

   ① 基础光谱   B02 B03 B04 B05 B06 B07 B08 B8A B11 B12 （30m=3×3 窗口均值，10 个）
   ② 植被指数   NDVI NDWI NDRE                           （同上，3 个）
   ③ 多尺度     NDVI_std50 NDRE_std50 B8_std50           （50m=5×5 窗口 std，3 个）
   ④ 结构-纹理  GLCM_contrast GLCM_entropy               （NDVI → GLCM 7×7 / 16 级 / 4 方向均值，2 个）
   ⑤ 结构-邻域  NDVI_mean100 NDVI_std100                 （100m=10×10 窗口，2 个）
   ⑥ 地形       DEM_elev DEM_slope DEM_aspect            （30m 窗口，DEM 就绪后启用，3 个）

- 尺度依据：IFN4 样地为同心圆、最大半径 25m → 30m ≈ 样地核心，50m = 样地边界，
  100m 属"景观背景"（论文需论证其合理性）
- SWIR 决策（2026-09-19）：**纳入 B11/B12**（文献中 SWIR 对生物量/蓄积量贡献显著）
  → 基础光谱由 8 → 10 个，特征总数 21 → 23

## 输入 / 输出

- **输入**：`data/Sentinel2/roi/Spain_IFN4/`（研究区 S2 栅格）、IFN4 样地蓄积量 CSV、`data/DEM/roi/`
- **样本单元**：样地中心缓冲窗口
- **标签**：样地蓄积量 GSV（m³/ha，由 `PCMayores` 按 IFN4 官方材积公式计算）
- **输出**：`data/feature/samples.csv`
  - 列：`sample_id` / `province` / `plot_id` / `x` / `y` / 上述 23 特征 / `GSV`

> 注：原芬兰阶段实现已随研究区更换移除；下列通用函数可直接复用。
"""
import numpy as np

# --- 特征定义（研究方案 v1；本文件为全项目特征定义的**单一来源**）---
SPECTRAL_BANDS = ["B02", "B03", "B04", "B05", "B06", "B07", "B08", "B8A", "B11", "B12"]
INDEX_FEATURES = ["NDVI", "NDWI", "NDRE"]
MULTISCALE_FEATURES = ["NDVI_std50", "NDRE_std50", "B8_std50"]
TEXTURE_FEATURES = ["GLCM_contrast", "GLCM_entropy"]
NEIGHBOR_FEATURES = ["NDVI_mean100", "NDVI_std100"]
TERRAIN_FEATURES = ["DEM_elev", "DEM_slope", "DEM_aspect"]

FEATURES = (SPECTRAL_BANDS + INDEX_FEATURES + MULTISCALE_FEATURES
            + TEXTURE_FEATURES + NEIGHBOR_FEATURES + TERRAIN_FEATURES)   # 23 个


def calc_indices(win):
    """由窗口波段均值计算植被指数，返回 (NDVI, NDWI, NDRE)

    波段顺序须与 `SPECTRAL_BANDS` 一致（指数仅用前三列中的 B02/B03/B04/B08/B8A/B05）
    """
    b2, b3, b4, b5, b6, b7, b8, b8a = [win[:, i] for i in range(8)]
    eps = 1e-8
    ndvi = (b8 - b4) / (b8 + b4 + eps)
    ndwi = (b3 - b8) / (b3 + b8 + eps)
    ndre = (b8a - b5) / (b8a + b5 + eps)
    return ndvi, ndwi, ndre


def compute_slope_aspect(dem, res=10.0):
    """由 DEM 计算坡度(°)与坡向(°)"""
    dzdy, dzdx = np.gradient(dem, res, res)
    slope = np.degrees(np.arctan(np.hypot(dzdx, dzdy)))
    aspect = np.degrees(np.arctan2(-dzdx, dzdy)) % 360.0
    return slope, aspect


def build_all():
    """主流程（待实现）"""
    raise NotImplementedError(
        "西班牙特征提取待实现：需先完成 ①西班牙 DEM 获取、②IFN4 样地蓄积量计算、"
        "③研究区 S2 裁剪对齐。"
    )


if __name__ == "__main__":
    build_all()
