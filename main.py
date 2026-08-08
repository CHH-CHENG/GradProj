import os
import sys
from pathlib import Path


def _ensure_gdal_env():
    """配置 conda 环境下 GDAL 运行所需的环境变量（必须在导入 rasterio 之前调用）：

    - GDAL_DATA       ：GDAL 数据文件目录（消除 gdalvrt.xsd 等告警）
    - GDAL_DRIVER_PATH：GDAL 插件目录（如 JP2OpenJPEG 解码插件）
    - PATH 追加 Library/bin：保证插件依赖的 dll（如 openjp2.dll）能被加载
    """
    prefix = Path(sys.prefix)

    if not os.environ.get("GDAL_DATA"):
        for p in (prefix / "Library/share/gdal",
                  prefix / "etc/gdal",
                  prefix / "share/gdal"):
            if p.is_dir():
                os.environ["GDAL_DATA"] = str(p)
                break

    plugins = prefix / "Library/lib/gdalplugins"
    if plugins.is_dir() and not os.environ.get("GDAL_DRIVER_PATH"):
        os.environ["GDAL_DRIVER_PATH"] = str(plugins)

    lib_bin = prefix / "Library/bin"
    if lib_bin.is_dir():
        cur = os.environ.get("PATH", "")
        if str(lib_bin) not in cur:
            os.environ["PATH"] = str(lib_bin) + os.pathsep + cur


_ensure_gdal_env()

from downloader.copernicus import search_products, download_batch
from preprocess.unzip import unzip_all
from preprocess.crop_roi import process_sentinel2

def download_and_unzip():
    lon, lat = 107.0, 34.3
    start_date = "2023-06-01"
    end_date = "2023-08-01"
    product_ids = search_products(lon, lat, start_date, end_date)
    download_batch(product_ids)
    unzip_all()  # 批量解压


def run_preprocess():
    """波段读取 + 重采样 + ROI 裁剪（研究区整幅 + 按样地预留）"""
    process_sentinel2()


if __name__ == "__main__":
    run_preprocess()