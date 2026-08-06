from downloader.copernicus import search_products, download_batch
from preprocess.unzip import unzip_all

def download_and_unzip():
    lon, lat = 107.0, 34.3
    start_date = "2023-06-01"
    end_date = "2023-08-01"
    product_ids = search_products(lon, lat, start_date, end_date)
    download_batch(product_ids)
    unzip_all()# 批量解压




if __name__ == "__main__":
    print(1)