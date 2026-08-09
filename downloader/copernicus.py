import requests
import os
import time
import zipfile
import yaml
from pathlib import Path

AUTH_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
CATALOG_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
DOWNLOAD_URL = "https://download.dataspace.copernicus.eu/odata/v1/Products({})/$value"

# 配置文件基于本文件位置定位，避免依赖当前运行目录
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "copernicus.yaml"


# =========================
# 读取账号密码
# =========================
def get_credentials():
    user = os.getenv("CDSE_USER")
    pwd = os.getenv("CDSE_PASS")

    if user and pwd:
        return user, pwd

    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    return cfg["username"], cfg["password"]


# =========================
# 获取token
# =========================
def get_token():
    username, password = get_credentials()

    data = {
        "client_id": "cdse-public",
        "grant_type": "password",
        "username": username,
        "password": password
    }

    r = requests.post(AUTH_URL, data=data)
    r.raise_for_status()

    return r.json()["access_token"]


# =========================
# 查询产品ID
# =========================
def search_products(lon, lat, start_date, end_date, cloud=20):

    query = (
        f"$filter=Collection/Name eq 'SENTINEL-2' "
        f"and OData.CSC.Intersects(area=geography'SRID=4326;POINT({lon} {lat})') "
        f"and ContentDate/Start ge {start_date}T00:00:00.000Z "
        f"and ContentDate/Start le {end_date}T23:59:59.999Z "
        f"and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' "
        f"and att/OData.CSC.DoubleAttribute/Value lt {cloud})"
        f"&$orderby=ContentDate/Start desc"
        f"&$top=20"
    )

    url = f"{CATALOG_URL}?{query}"

    r = requests.get(url)
    r.raise_for_status()

    data = r.json()["value"]

    ids = []

    for item in data:
        online = item.get("Online", False)

        if online:
            ids.append(item["Id"])
        else:
            print(f"跳过（离线）: {item['Id']}")

    print(f"找到 {len(ids)} 个产品")
    return ids


# =========================
# 下载单个产品
# =========================
def download_product(product_id, get_token_func, out_dir="data/Sentinel2/zip"):
    import os
    import requests
    import time

    os.makedirs(out_dir, exist_ok=True)

    final_path = os.path.join(out_dir, f"{product_id}.zip")
    part_path = final_path + ".part"

    # =========================
    # 1️⃣ 已完成 → 跳过
    # =========================
    if os.path.exists(final_path):
        print(f"已完成，跳过: {product_id}")
        return

    url = DOWNLOAD_URL.format(product_id)
    token = get_token_func()

    for attempt in range(10):
        try:
            headers = {"Authorization": f"Bearer {token}"}

            # =========================
            # 2️⃣ 断点续传
            # =========================
            if os.path.exists(part_path):
                downloaded = os.path.getsize(part_path)
                headers["Range"] = f"bytes={downloaded}-"
                mode = "ab"
                print(f"续传: {product_id} 已下载 {downloaded/1024/1024:.2f} MB")
            else:
                mode = "wb"

            with requests.get(url, headers=headers, stream=True, timeout=60) as r:

                # =========================
                # 3️⃣ token过期处理
                # =========================
                if r.status_code == 401:
                    print(f"[{product_id}] token过期，刷新...")
                    token = get_token_func()
                    continue

                if r.status_code not in [200, 206]:
                    raise Exception(f"HTTP {r.status_code}")

                # =========================
                # 4️⃣ 写入 .part 文件
                # =========================
                with open(part_path, mode) as f:
                    for chunk in r.iter_content(8192):
                        if chunk:
                            f.write(chunk)

            # ====完整性校验 + 改名
            # =========================
            if not zipfile.is_zipfile(part_path):
                print(f"完整性校验失败，删除后重下: {product_id}")
                os.remove(part_path)
                raise Exception("下载文件不是有效的zip")

            # =========================
            os.rename(part_path, final_path)
            print(f"下载完成: {product_id}")
            return

        except Exception as e:
            print(f"重试 {attempt+1}: {product_id} - {e}")
            time.sleep(5)

    print(f"下载失败: {product_id}")


# =========================
# 批量下载
# =========================
def download_batch(product_ids):
    for pid in product_ids:
        download_product(pid, get_token)


# =========================
# 从产品 Attributes 中鲁棒提取云量
# =========================
def _extract_cloud(item):
    """兼容 Copernicus OData 扁平结构（{"Name","Value","ValueType"}）与旧嵌套结构"""
    for att in item.get("Attributes") or []:
        if att.get("Name") == "cloudCover":
            if "Value" in att:                  # 扁平结构
                return att.get("Value")
            vals = att.get("value")             # 兼容嵌套结构
            if isinstance(vals, dict):
                return vals.get("Value")
            for v in vals or []:
                if isinstance(v, dict) and "Value" in v:
                    return v["Value"]
    return None


# =========================
# 提取 tile（优先用 Attributes.tileId，回退文件名解析）
# =========================
def _extract_tile(item):
    for att in item.get("Attributes") or []:
        if att.get("Name") == "tileId" and att.get("Value"):
            return str(att.get("Value"))
    name = item.get("Name", "")
    return next((p for p in name.split("_") if p.startswith("T") and len(p) == 6), "")


# =========================
# 按矩形范围查询（返回完整产品信息，用于按 tile 去重）
# =========================
def search_products_bbox(lon_min, lat_min, lon_max, lat_max, start_date, end_date, cloud=20, max_items=300, product_type="L2A"):
    """按 WGS84 矩形范围查询 Sentinel-2 产品，返回产品信息字典列表。

    每个产品信息：{id, name, tile, date, cloud, online}
    - tile 优先取自 Attributes.tileId，回退从产品名解析
    - 默认仅返回 L2A（product_type="L2A"），可传 "L1C" 或 "ALL"
    """
    type_token = {"L1C": "MSIL1C", "L2A": "MSIL2A"}.get(product_type, product_type)
    wkt = (f"POLYGON(({lon_min} {lat_min},{lon_max} {lat_min},"
           f"{lon_max} {lat_max},{lon_min} {lat_max},{lon_min} {lat_min}))")
    query = (
        f"$filter=Collection/Name eq 'SENTINEL-2' "
        f"and OData.CSC.Intersects(area=geography'SRID=4326;{wkt}') "
        f"and ContentDate/Start ge {start_date}T00:00:00.000Z "
        f"and ContentDate/Start le {end_date}T23:59:59.999Z "
        f"and Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' "
        f"and att/OData.CSC.DoubleAttribute/Value lt {cloud})"
        f"&$orderby=ContentDate/Start desc"
        f"&$top={max_items}&$expand=Attributes"
    )
    url = f"{CATALOG_URL}?{query}"
    r = requests.get(url)
    r.raise_for_status()

    products = []
    for item in r.json().get("value", []):
        name = item.get("Name", "")
        if product_type != "ALL" and type_token not in name:   # Python 端按产品类型过滤
            continue
        date = (item.get("ContentDate") or {}).get("Start", "")[:10]
        products.append({
            "id": item["Id"],
            "name": name,
            "tile": _extract_tile(item),
            "date": date,
            "cloud": _extract_cloud(item),
            "online": item.get("Online", False),
        })
    print(f"[{start_date}~{end_date}] 范围 [{lon_min},{lat_min}]-[{lon_max},{lat_max}] "
          f"查询到 {len(products)} 个 {product_type} 产品（云量<{cloud}）")
    return products


# =========================
# 按 tile 去重：每个 tile 只保留云量最少的一期（避免重复时相）
# =========================
def dedup_by_tile(products, keep="min_cloud"):
    best = {}
    for p in products:
        if not p.get("online"):
            print(f"  跳过离线: {p['name']}")
            continue
        key = p["tile"] or p["id"]
        cur = best.get(key)
        cur_cloud = cur.get("cloud") if cur else None
        p_cloud = p.get("cloud")
        if cur is None or (p_cloud is not None and (cur_cloud is None or p_cloud < cur_cloud)):
            best[key] = p
    return list(best.values())


# =========================
# 区域一站式：查询 -> 去重 -> 下载（每 tile 一期）
# =========================
def search_and_download_region(lon_min, lat_min, lon_max, lat_max, start_date, end_date, cloud=20):
    products = search_products_bbox(lon_min, lat_min, lon_max, lat_max, start_date, end_date, cloud)
    selected = dedup_by_tile(products)
    print(f"按 tile 去重后选择 {len(selected)} 个产品：")
    for p in sorted(selected, key=lambda x: x["tile"]):
        print(f"  {p['date']} | {p['tile']} | 云量 {p['cloud']} | {p['name']}")
    if not selected:
        print("  无可用产品，跳过下载")
        return []
    ids = [p["id"] for p in selected]
    download_batch(ids)
    return selected