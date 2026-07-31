import importlib
import sys
import subprocess

print("=" * 60)
print("Python Environment Check")
print("=" * 60)

# ======================
# 1. Python 基本信息
# ======================
print("\n[Python Info]")
print("Version:", sys.version)
print("Executable:", sys.executable)

# ======================
# 2. 要检测的库
# ======================
libs = [
    "numpy",
    "pandas",
    "matplotlib",
    "sklearn",
    "rasterio",
    "geopandas",
    "osgeo",        # gdal
    "shapely",
    "fiona",
    "pyproj",
    "torch"
]

# ======================
# 3. 导入检查
# ======================
print("\n[Library Import Check]")
results = {}

for lib in libs:
    try:
        module = importlib.import_module(lib)
        version = getattr(module, "__version__", "Unknown")
        print(f"[OK] {lib} - {version}")
        results[lib] = ("OK", version)
    except Exception as e:
        print(f"[FAIL] {lib} - {e}")
        results[lib] = ("FAIL", str(e))

# ======================
# 4. 关键兼容性检查
# ======================
print("\n[Compatibility Checks]")

# ---- numpy 版本检查 ----
try:
    import numpy as np
    ver = tuple(map(int, np.__version__.split('.')[:2]))

    if ver >= (2, 0):
        print("[WARN] numpy >= 2.0 可能导致 gdal / rasterio 不兼容")
    else:
        print("[OK] numpy version seems safe")
except:
    pass

# ---- gdal / rasterio 兼容 ----
try:
    import rasterio
    from osgeo import gdal

    print("[INFO] rasterio GDAL version:", rasterio.__gdal_version__)
    print("[INFO] system GDAL version:", gdal.VersionInfo())

    if rasterio.__gdal_version__ not in gdal.VersionInfo():
        print("[WARN] rasterio 和 gdal 版本可能不一致")
    else:
        print("[OK] rasterio / gdal matched")
except Exception as e:
    print("[WARN] GDAL compatibility check failed:", e)

# ---- geopandas 依赖链 ----
try:
    import geopandas as gpd
    import shapely
    import fiona
    import pyproj

    print("[OK] geopandas dependency chain loaded")
except Exception as e:
    print("[FAIL] geopandas dependency issue:", e)

# ---- sklearn ----
try:
    import sklearn
    print("[OK] sklearn works")
except Exception as e:
    print("[FAIL] sklearn issue:", e)

# ---- PyTorch GPU ----
try:
    import torch

    print("\n[PyTorch Check]")
    print("CUDA available:", torch.cuda.is_available())

    if torch.cuda.is_available():
        print("CUDA version:", torch.version.cuda)
        print("GPU:", torch.cuda.get_device_name(0))
    else:
        print("[INFO] GPU not available (this is OK for your project)")

except Exception as e:
    print("[INFO] torch not installed or error:", e)

# ======================
# 5. pip 依赖冲突检查
# ======================
print("\n[Dependency Conflict Check (pip check)]")

try:
    result = subprocess.run(
        ["pip", "check"],
        capture_output=True,
        text=True
    )

    if result.stdout.strip() == "":
        print("[OK] No dependency conflicts")
    else:
        print("[WARN] Dependency conflicts found:")
        print(result.stdout)

except Exception as e:
    print("[WARN] pip check failed:", e)

print("\n" + "=" * 60)
print("Check Complete")
print("=" * 60)