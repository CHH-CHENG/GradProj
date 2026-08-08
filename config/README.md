# 配置目录

存放项目运行所需的配置文件。

## 放置的数据（配置项）
| 文件 | 作用 |
|------|------|
| `copernicus.yaml` | Copernicus Data Space（CDSE）账号配置，用于 Sentinel-2 数据下载 |
| `preprocess.yaml` | 预处理配置：波段读取 / 重采样 / ROI 裁剪 参数 |

## 数据类型
- YAML 配置文件

## 数据内部格式

### copernicus.yaml（下载账号）
```yaml
username: "xxx"   # CDSE 账号
password: "xxx"   # CDSE 密码
```

### preprocess.yaml（预处理参数）
```yaml
product_type: L2A        # 产品类型（L1C / L2A）
target_resolution: 10    # 统一重采样分辨率（m）
bands: [B02, ...]        # 参与建模的波段
research_center: {lon: ..., lat: ...}
research_half_size_m: 5000
plots: data/inventory/plots.geojson
plot_buffer_m: 20
```

> ⚠️ `copernicus.yaml` 含账号密码，已被 `.gitignore` 排除，请勿提交到仓库。
