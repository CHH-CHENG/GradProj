import zipfile
from pathlib import Path


def get_safe_name(zip_path):
    """
    从 zip 内部读取真实的顶层目录名（SAFE 产品名）。

    Copernicus 下载的 zip 文件名是 UUID，内部顶层目录才是
    S2A_MSIL1C_...SAFE 这样的产品名，因此不能依赖 zip 文件名判断。
    """
    with zipfile.ZipFile(zip_path, "r") as z:
        for name in z.namelist():
            if "/" in name:
                return name.split("/")[0]
    return None


def unzip_all(
        zip_dir="data/Sentinel2/zip",
        out_dir="data/Sentinel2/SAFE",
        delete_zip=False
):
    """
    解压 data/raw 下所有 Sentinel-2 zip 文件

    Parameters
    ----------
    zip_dir : str
        zip目录

    out_dir : str
        解压目录

    delete_zip : bool
        是否删除zip
    """

    zip_dir = Path(zip_dir)
    out_dir = Path(out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    zip_files = list(zip_dir.glob("*.zip"))

    print(f"发现 {len(zip_files)} 个zip文件")

    for zip_file in zip_files:

        # 真实 SAFE 目录名（来自 zip 内部，而非 zip 文件名）
        safe_name = get_safe_name(zip_file)

        if safe_name is None:
            print(f"无法识别 zip 内部结构，跳过: {zip_file.name}")
            continue

        safe_path = out_dir / safe_name

        # 已解压
        if safe_path.exists():
            print(f"跳过：{safe_name}")
            continue

        print(f"解压：{zip_file.name}")

        try:

            with zipfile.ZipFile(zip_file, "r") as z:
                z.extractall(out_dir)

            print("完成")

            if delete_zip:
                zip_file.unlink()

        except Exception as e:
            print(f"失败：{e}")