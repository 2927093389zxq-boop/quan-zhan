import os, difflib, time, shutil
from typing import Dict

class PatchStore:
    def __init__(self, patch_dir="auto_patches"):
        self.patch_dir = patch_dir
        os.makedirs(self.patch_dir, exist_ok=True)

    def build_patch(self, original: str, variant: str, tag: str) -> str:
        diff = list(difflib.unified_diff(
            original.splitlines(keepends=True),
            variant.splitlines(keepends=True),
            fromfile="amazon_scraper.py",
            tofile=f"amazon_scraper_{tag}.py"
        ))
        patch_path = os.path.join(self.patch_dir, f"{tag}.patch")
        with open(patch_path, "w", encoding="utf-8") as f:
            f.writelines(diff)
        return patch_path

    def list_patches(self):
        files = [f for f in os.listdir(self.patch_dir) if f.endswith(".patch")]
        data = []
        for f in files:
            full = os.path.join(self.patch_dir, f)
            data.append({
                "file": f,
                "size": os.path.getsize(full),
                "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(full)))
            })
        return sorted(data, key=lambda x: x["mtime"], reverse=True)

    def apply_patch_direct(self, patch_path: str, production_file: str, variant_code: str):
        backup = production_file + ".bak"
        shutil.copy2(production_file, backup)
        with open(production_file, "w", encoding="utf-8") as f:
            f.write(variant_code)
        return backup