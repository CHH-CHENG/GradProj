# preprocess 模块（数据预处理）

负责将下载的 Sentinel-2 原始数据转换为**可建模的统一 ROI 影像**。

处理链路：`zip → SAFE → 波段读取/重采样 → ROI 裁剪`

## 脚本说明

### unzip.py（解压）
| 函数 | 作用 |
|------|------|
| `get_safe_name(zip_path)` | 从 zip 内部读取真实 SAFE 产品名（顶层目录），避免 UUID 命名陷阱 |
| `unzip_all()` | 批量解压 `data/Sentinel2/zip/` → `data/Sentinel2/SAFE/`，已解压自动跳过 |

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

- **输入**：`data/Sentinel2/SAFE/*.SAFE/`、`config/preprocess.yaml`
- **输出**：`data/Sentinel2/roi/*_roi.tif`（10 波段 B02~B12，10m，EPSG:32648，0~1 反射率）

### finland_study.py（芬兰研究区数据准备）
| 函数 | 作用 |
|------|------|
| `prepare_region_s2(region, cfg, safe_dirs)` | 从覆盖研究区的 SAFE 读取波段，逐块重投影到统一 EPSG:3067 网格（10m），重叠区均值融合 |
| `prepare_region_label(region, cfg)` | 从 MS-NFI 全国蓄积量栅格裁剪标签（16m→10m 最近邻） |
| `prepare_region_dem(region, cfg)` | 从 MML 10m DEM 分块裁剪拼接（EPSG:3067） |
| `prepare_all()` | 主流程：遍历两个研究区（纯林/混交）生成对齐栅格 |

- **配置**：`config/finland_study.yaml`（两个研究区中心/范围、采样参数、数据路径）
- **输出**：`data/Sentinel2/roi/Finland_PureMixed/<id>_S2_10m_3067.tif`、`data/feature/finland_study/<id>_GSV_10m_3067.tif`、`..._DEM_10m_3067.tif`（均 2000×2000、10m、EPSG:3067）
