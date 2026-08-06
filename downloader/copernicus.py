import requests
import os
import time
import yaml

AUTH_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
CATALOG_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
DOWNLOAD_URL = "https://download.dataspace.copernicus.eu/odata/v1/Products({})/$value"


# =========================
# 读取账号密码
# =========================
def get_credentials():
    user = os.getenv("CDSE_USER")
    pwd = os.getenv("CDSE_PASS")

    if user and pwd:
        return user, pwd

    with open("config/copernicus.yaml") as f:
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

            # =========================
            # 5️⃣ 下载完成 → 改名
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