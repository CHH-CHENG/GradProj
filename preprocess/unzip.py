import zipfile
from pathlib import Path


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

        safe_name = zip_file.stem + ".SAFE"

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