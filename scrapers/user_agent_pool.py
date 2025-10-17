import random
import time

DESKTOP_UA = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

MOBILE_UA = [
    "Mozilla/5.0 (Linux; Android 13; SM-S9060) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
]

def get_dynamic_user_agent(strategy: str = "hybrid") -> str:
    """
    strategy 可选：
      - desktop 只使用桌面
      - mobile 只使用移动
      - hybrid 混合（默认）
      - random 随机（与 hybrid 类似）
    """
    if strategy == "desktop":
        return random.choice(DESKTOP_UA)
    if strategy == "mobile":
        return random.choice(MOBILE_UA)
    if strategy in ("hybrid", "random"):
        pool = DESKTOP_UA + MOBILE_UA
        random.seed(time.time())
        return random.choice(pool)
    # 默认 fallback
    return random.choice(DESKTOP_UA)