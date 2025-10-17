import time
from .logger import log_info, log_error

def detect_captcha(html: str) -> bool:
    """
    简单检测页面是否可能是验证码/反机器人页面。
    可根据实际 Amazon 返回的 HTML 再补关键词。
    """
    if not html:
        return False
    markers = [
        "captcha", "verify you are a human", "enter the characters",
        "/errors/validateCaptcha", "robot check"
    ]
    low = html.lower()
    return any(m in low for m in markers)

def solve_captcha_manual(page) -> bool:
    """
    人工处理模式占位：
    - 如果 headless=False，会弹出真实浏览器。
    - 给操作者 60 秒时间手动完成验证码。
    """
    log_info("[CAPTCHA] 检测到验证码，暂停 60 秒等待人工处理...")
    time.sleep(60)
    log_info("[CAPTCHA] 人工处理阶段结束，将继续执行。")
    return True

# 如果未来接入打码平台（如 2Captcha），可扩展此函数：
def solve_captcha_api(image_bytes: bytes, api_key: str) -> str:
    """
    占位：接入 2Captcha 或其他服务。
    返回识别出的文字；当前未实现，直接返回空字符串。
    """
    log_error("[CAPTCHA] API solver 未实现，使用人工模式。")
    return ""