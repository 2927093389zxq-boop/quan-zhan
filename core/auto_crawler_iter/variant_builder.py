import os, hashlib
from typing import Dict

TEMPLATE_HEADER = """# AUTO-GENERATED VARIANT
# strategies: {strategies}
# Do not edit manually; apply via patch system.
"""

def build_variant(patch_conf: Dict, base_source: str, strategies: list) -> str:
    """
    在原始 amazon_scraper.py 源码中，替换或追加配置区块。
    要求原文件中存在一个标记：# === AUTO_TUNING_CONFIG_START === / END
    如果不存在，就在文件头插入一个配置代码块。
    """
    config_block = f'''
# === AUTO_TUNING_CONFIG_START ===
LIST_SELECTORS = {patch_conf["list_selectors"]}
TITLE_SELECTORS = {patch_conf["title_selectors"]}
PRICE_SELECTORS = {patch_conf["price_selectors"]}

UA_MODE = "{patch_conf["ua_mode"]}"
SCROLL_CYCLES = {patch_conf["scroll_cycles"]}
WAIT_MIN = {patch_conf["wait_min"]}
WAIT_MAX = {patch_conf["wait_max"]}
ENABLE_SECOND_PASS = {patch_conf["enable_second_pass"]}
ENABLE_FALLBACK_ASIN = {patch_conf["enable_fallback_asin"]}
# === AUTO_TUNING_CONFIG_END ===
'''
    if "# === AUTO_TUNING_CONFIG_START ===" in base_source:
        # 简单替换
        import re
        new_source = re.sub(
            r"# === AUTO_TUNING_CONFIG_START ===.*?# === AUTO_TUNING_CONFIG_END ===",
            config_block.strip(),
            base_source,
            flags=re.S
        )
    else:
        new_source = TEMPLATE_HEADER.format(strategies=",".join(strategies)) + config_block + "\n" + base_source
    return new_source

def variant_hash(content: str) -> str:
    return hashlib.md5(content.encode("utf-8")).hexdigest()[:8]