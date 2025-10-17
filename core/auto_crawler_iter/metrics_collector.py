import os, json, re, time
from typing import Dict, Any, List
from datetime import datetime

class MetricsCollector:
    def __init__(self, data_dir="data", log_file="scraper.log"):
        self.data_dir = data_dir
        self.log_file = log_file

    def collect(self) -> Dict[str, Any]:
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_items": 0,
            "zero_files": 0,
            "avg_items_per_file": 0.0,
            "files_scanned": 0,
            "captcha_hits": 0,
            "error_lines": 0,
            "avg_list_time": None,
            "recent_errors": [],
        }
        items_acc = []
        if os.path.isdir(self.data_dir):
            files = sorted([
                f for f in os.listdir(self.data_dir) if f.endswith(".json")
            ], key=lambda x: os.path.getmtime(os.path.join(self.data_dir, x)), reverse=True)[:30]
            for f in files:
                path = os.path.join(self.data_dir, f)
                try:
                    data = json.load(open(path, "r", encoding="utf-8"))
                    if isinstance(data, list):
                        cnt = len(data)
                        items_acc.append(cnt)
                        if cnt == 0:
                            metrics["zero_files"] += 1
                except:
                    continue
            metrics["files_scanned"] = len(items_acc)
            metrics["total_items"] = sum(items_acc)
            if items_acc:
                metrics["avg_items_per_file"] = metrics["total_items"] / len(items_acc)

        # 日志解析
        if os.path.exists(self.log_file):
            list_times = []
            err_capture = []
            with open(self.log_file, "r", encoding="utf-8") as rf:
                for line in rf:
                    low = line.lower()
                    if "captcha" in low:
                        metrics["captcha_hits"] += 1
                    if "[exception]" in low or "[error]" in low:
                        metrics["error_lines"] += 1
                        if len(err_capture) < 10:
                            err_capture.append(line.strip())
                    # 可在你的 amazon_scraper 中打印如 [LIST_TIME] secs=1.23
                    mt = re.search(r"\[LIST_TIME\]\s+secs=(\d+\.\d+)", line)
                    if mt:
                        try:
                            list_times.append(float(mt.group(1)))
                        except:
                            pass
            if list_times:
                metrics["avg_list_time"] = round(sum(list_times)/len(list_times), 3)
            metrics["recent_errors"] = err_capture
        return metrics