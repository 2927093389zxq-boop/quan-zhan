"""
可选：快速打包与检查爬虫组件。
运行：python tools/build_scraper_bundle.py
"""
import os
import zipfile

FILES = [
    "scrapers/__init__.py",
    "scrapers/amazon_scraper.py",
    "scrapers/proxy_manager.py",
    "scrapers/storage_manager.py",
    "scrapers/logger.py",
    "core/data_fetcher.py",
    "ui/amazon_crawl_options.py",
    "run_launcher.py",
]

def build_zip(output="scraper_bundle.zip"):
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        for f in FILES:
            if os.path.exists(f):
                z.write(f)
            else:
                print(f"[WARN] 文件不存在：{f}")
    print(f"[OK] 打包完成：{output}")

if __name__ == "__main__":
    build_zip()