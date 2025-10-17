from core.crawl.dispatcher import run_batch

if __name__ == "__main__":
    urls = [
        "https://www.amazon.com/bestsellers",
        "https://www.amazon.com/s?k=mouse",
        "https://www.amazon.com/s?k=keyboard",
    ]
    run_batch(urls, storage_mode="local")