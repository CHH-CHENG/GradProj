"""项目主流程控制入口（芬兰研究：纯林/混交林对比）

步骤（各步幂等，已生成自动跳过）：
  prepare   研究区数据准备（Sentinel-2 拼接 / MS-NFI 标签 / DEM，统一 EPSG:3067 10m）
  extract   特征提取（30m 窗口 → data/feature/samples.csv）
  subsample 空间均匀抽样（默认每区 50000 → samples_sampled.csv）
  train     模型训练（三模型矩阵 + 空间分块 CV；--smoke 冒烟测试）
  all       依次执行 prepare → extract → subsample → train

用法：
  python main.py all
  python main.py prepare
  python main.py subsample 30000
  python main.py train
  python main.py train --smoke
"""
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


def run_prepare():
    """研究区数据准备：S2 拼接 + MS-NFI 标签 + DEM（preprocess/finland_study.py）"""
    from preprocess.finland_study import prepare_all
    prepare_all()


def run_extract():
    """特征提取：30m 窗口 → samples.csv（feature/extract.py）"""
    from feature.extract import build_all
    build_all()


def run_subsample(n=None):
    """空间均匀抽样（feature/subsample.py）"""
    from feature.subsample import main as subsample_main
    subsample_main(n)


def run_train(smoke=False):
    """模型训练：三模型矩阵 + 空间分块 CV（model/rf.py）"""
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
        run_prepare()
        run_extract()
        run_subsample(None)
        run_train(False)
        return

    step = argv[0]
    if step == "prepare":
        run_prepare()
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
