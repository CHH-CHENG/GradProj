"""项目主流程控制入口（西班牙 IFN4 研究：省份间森林蓄积量估测）

步骤（各步尽量幂等，已生成的数据自动跳过）：
  download  Sentinel-2 下载（downloader/spain.py；省份 leon/burgos/lugo 或 all）
  unzip     解压 SAFE 产品（preprocess/unzip.py）
  roi       研究区裁剪（preprocess/crop_roi.py，依赖 config/preprocess.yaml）
  extract   特征提取 → data/feature/samples.csv（feature/extract.py，⏳ 待实现）
  subsample 空间均匀抽样（feature/subsample.py）
  train     随机森林建模 + 空间分块 CV（model/rf.py；--smoke 冒烟测试）
  all       依次执行 download → unzip → roi → extract → subsample → train

用法：
  python main.py download all                    # 下载三省 S2（约 21.3 GB，已完成）
  python main.py download leon --dry-run         # 仅查询预览
  python main.py unzip
  python main.py roi
  python main.py subsample 50000
  python main.py train --smoke
"""
import os
import sys
from pathlib import Path

# Windows 控制台编码兼容：无法编码的符号（如 ⏳）替换为 ?，避免 UnicodeEncodeError
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

# 西班牙研究数据根目录（SAFE / roi 均在 Spain_IFN4 子目录下）
S2_ZIP = "data/Sentinel2/zip/Spain_IFN4"
S2_SAFE = "data/Sentinel2/SAFE/Spain_IFN4"
S2_ROI = "data/Sentinel2/roi/Spain_IFN4"


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


def run_download(targets, dry_run=False):
    """Sentinel-2 下载（downloader/spain.py）：targets 为省份名列表或 ['all']"""
    from downloader import spain

    if not targets or targets[0] == "all":
        keys = list(spain.REGIONS)
    else:
        keys = [t for t in targets if t in spain.REGIONS]
        unknown = [t for t in targets if t not in spain.REGIONS]
        if unknown:
            print(f"未知区域: {unknown}  可选: {list(spain.REGIONS)} 或 all")
    for k in keys:
        spain.run_region(k, dry_run)


def run_unzip():
    """解压 SAFE 产品（preprocess/unzip.py）"""
    from preprocess.unzip import unzip_all
    unzip_all(zip_dir=S2_ZIP, out_dir=S2_SAFE)


def run_roi():
    """研究区裁剪（preprocess/crop_roi.py；研究区范围由 config/preprocess.yaml 控制）"""
    from preprocess.crop_roi import process_sentinel2
    process_sentinel2(safe_root=S2_SAFE, out_root=S2_ROI)


def run_extract():
    """特征提取：窗口聚合 → samples.csv（feature/extract.py，⏳ 待实现）"""
    from feature.extract import build_all
    build_all()


def run_subsample(n=None):
    """空间均匀抽样（feature/subsample.py）"""
    from feature.subsample import main as subsample_main
    subsample_main(n)


def run_train(smoke=False):
    """随机森林建模 + 空间分块 CV（model/rf.py）"""
    if smoke:
        os.environ["RF_SMOKE"] = "1"
        print(">>> 冒烟测试模式（小样本 + 少量树），仅验证流程")
    from model.rf import main as rf_main
    rf_main()


def main():
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return

    if argv[0] == "all":
        run_download(["all"])
        run_unzip()
        run_roi()
        run_extract()
        run_subsample(None)
        run_train(False)
        return

    step = argv[0]
    if step == "download":
        targets = [a for a in argv[1:] if not a.startswith("-")]
        run_download(targets or ["all"], "--dry-run" in argv)
    elif step == "unzip":
        run_unzip()
    elif step == "roi":
        run_roi()
    elif step == "extract":
        run_extract()
    elif step == "subsample":
        n = int(argv[1]) if len(argv) > 1 and argv[1].isdigit() else None
        run_subsample(n)
    elif step == "train":
        run_train("--smoke" in argv)
    else:
        print(f"未知步骤: {step}\n")
        print(__doc__)


if __name__ == "__main__":
    main()
