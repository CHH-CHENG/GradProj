from downloader.copernicus import search_products, download_batch

def main():
    lon, lat = 107.0, 34.3
    start_date = "2023-06-01"
    end_date = "2023-08-01"

    product_ids = search_products(lon, lat, start_date, end_date)

    download_batch(product_ids)


if __name__ == "__main__":
    main()