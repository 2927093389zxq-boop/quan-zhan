import json
import os

def _safe_filename(key: str) -> str:
    return key.replace("/", "_").replace(":", "_").replace("?", "_")

def save_data(key: str, data):
    fname = f"data/{_safe_filename(key)}.json"
    os.makedirs(os.path.dirname(fname), exist_ok=True)
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_checkpoint(key: str):
    fname = f"checkpoint/{_safe_filename(key)}.json"
    if not os.path.exists(fname):
        return None
    with open(fname, "r", encoding="utf-8") as f:
        return json.load(f)

def save_checkpoint(key: str, data):
    fname = f"checkpoint/{_safe_filename(key)}.json"
    os.makedirs(os.path.dirname(fname), exist_ok=True)
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)