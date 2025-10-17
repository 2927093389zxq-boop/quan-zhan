import os, importlib.util, time, shutil
from typing import Dict, List
from scrapers.logger import log_info, log_error

class SandboxExecutor:
    def __init__(self, sandbox_dir="sandbox"):
        self.sandbox_dir = sandbox_dir
        os.makedirs(self.sandbox_dir, exist_ok=True)

    def write_variant(self, variant_code: str, tag: str) -> str:
        path = os.path.join(self.sandbox_dir, f"amazon_scraper_{tag}.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(variant_code)
        return path

    def _dynamic_import(self, path: str):
        spec = importlib.util.spec_from_file_location("amazon_variant", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def run_test(self, scraper_module, test_urls: List[str], max_items=20) -> Dict:
        stats = {
            "items": 0,
            "zero_pages": 0,
            "errors": 0,
            "captcha_hits": 0,
            "avg_time": None
        }
        times = []
        for u in test_urls:
            start = time.time()
            try:
                data = scraper_module.scrape_amazon(
                    url=u,
                    max_items=max_items,
                    resume=False,
                    use_proxy=False,
                    deep_detail=False,
                    storage_mode="local",
                    headless=True,
                    second_pass=True
                )
                if not data:
                    stats["zero_pages"] += 1
                else:
                    stats["items"] += len(data)
            except Exception as e:
                stats["errors"] += 1
            elapsed = time.time() - start
            times.append(elapsed)
        if times:
            stats["avg_time"] = round(sum(times)/len(times), 3)
        return stats

    def cleanup(self):
        # 可保留沙箱文件以供调试，也可在此实现自动清理
        pass