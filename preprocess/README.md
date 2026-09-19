# preprocess 模块（数据预处理）

负责将下载的 Sentinel-2 原始数据转换为**可建模的统一 ROI 影像**。

处理链路：`zip → SAFE → 波段读取/重采样 → ROI 裁剪`

## 脚本说明

### unzip.py（解压）
| 函数 | 作用 |
|------|------|
| `get_safe_name(zip_path)` | 从 zip 内部读取真实 SAFE 产品名（顶层目录），避免 UUID 命名陷阱 |
| `unzip_all(zip_dir, out_dir, delete_zip)` | 批量解压（默认 `zip/` → `SAFE/`）；**递归扫描子目录**（支持 `zip/Spain_IFN4/<省>/` 组织），已解压自动跳过 |

### read_bands.py（波段读取 + 重采样）
| 函数 | 作用 |
|------|------|
| `find_granule(safe_dir)` | 定位 SAFE 产品的 GRANULE 目录 |
| `build_band_path_map(img_data_dir)` | 构建波段名 → 波段文件路径映射（兼容 L2A 的 R10m/R20m/R60m 分目录与 L1C 平铺） |
| `read_bands(safe_dir, bands, target_res)` | 读取指定波段并按目标分辨率重采样（默认 10m）；支持按 ROI 窗口读取节省内存；L2A 反射率 DN(0~10000)→0~1 |

### crop_roi.py（ROI 裁剪）
| 函数 | 作用 |
|------|------|
| `process_research_area(safe_dir, out_path, cfg)` | 研究区整幅裁剪：按配置中心点 + 半宽在影像 CRS 下方形缓冲，输出多波段 GeoTIFF |
| `process_plots(safe_dir, plots_path, out_dir, cfg)` | 按样地矢量裁剪（点自动按 `plot_buffer_m` 缓冲；样地数据未就位时跳过） |
| `process_sentinel2()` | 主流程：遍历 SAFE 下所有 L2A 产品，已处理自动跳过 |

- **输入**：`data/Sentinel2/SAFE/`、`config/preprocess.yaml`
- **输出**：`data/Sentinel2/roi/*_roi.tif`（10 波段 B02~B12，10m，影像自带 CRS（西班牙为 ETRS89/UTM），0~1 反射率）

### 研究区整幅数据准备（西班牙 IFN4，⏳ 待实现）

原芬兰阶段的 `finland_study.py`（研究区重投影对齐 + 标签/DEM 裁剪）已随研究区更换移除。
西班牙版本需在数据就绪后实现，职责：
- 跨 tile / 跨 UTM 带重投影到统一网格（逐块重投影 + 均值融合）
- 裁剪 IFN4 样地蓄积量标签（由 `PCMayores` 计算）与 DEM，与 S2 特征像元对齐
