# 配置目录

存放项目运行所需的配置文件。

## 文件清单

| 文件 | 作用 |
|------|------|
| `copernicus.yaml` | Copernicus Data Space（CDSE）账号配置，用于 Sentinel-2 下载（**已被 `.gitignore` 排除**） |
| `copernicus.example.yaml` | 上述文件的模板（无真实凭据），复制后填写即可 |
| `preprocess.yaml` | 预处理配置：波段读取 / 重采样 / ROI 裁剪参数、研究区中心 |
| `spain_study.yaml` | **西班牙 IFN4 研究区配置**：三省（León/Burgos/Lugo）信息、采样参数、数据路径 |

## 数据类型
- YAML 配置文件

## 文件内部格式

### copernicus.yaml（下载账号）
```yaml
username: "your_email@example.com"
password: "your_password"
```

> 也可改用环境变量 `CDSE_USER` / `CDSE_PASS`（优先级更高，见 `downloader/copernicus.py`）。

### preprocess.yaml（预处理参数）
```yaml
product_type: L2A           # 产品类型（L1C / L2A）
target_resolution: 10       # 统一重采样分辨率（m）
bands: [B02, ..., B12]      # 参与建模的波段
scale_reflectance: true     # L2A DN(0~10000) → 0~1 反射率
research_center: { lon: -6.17, lat: 42.87 }   # 研究区中心（西班牙 León）
research_half_size_m: 10000 # 研究区半宽（m）
plots: data/inventory/IFN4/plots_spain.geojson
plot_buffer_m: 20           # 样地点缓冲半径（m）
```

### spain_study.yaml（西班牙研究区）
```yaml
output_crs: EPSG:25830      # ETRS89 / UTM 30N
provinces:                  # leon / burgos / lugo：调查年、S2 年份、EPSG、bbox、样地数
sampling: { window_m: 30, step_m: 30 }
paths:                      # zip / SAFE / roi / study / inventory / dem 路径
```

## 注意事项

> ⚠️ `copernicus.yaml` 含账号密码，已被 `.gitignore` 排除，**请勿提交到仓库**；
> 需要共享时请使用 `copernicus.example.yaml` 模板。

- `preprocess.yaml` 中 `research_center` 为**初步占位**（León 省北部林区），
  待样地分布统计后确定最终范围。
