"""
Amazon Scraper (Unified Enhanced Version)

特性综述:
- 可自迭代配置区块 (# === AUTO_TUNING_CONFIG_START/END ===) 供迭代引擎替换
- 多结构列表选择器 (搜索 / Bestseller / data-asin 兜底)
- 动态 User-Agent (桌面 / 移动 / 混合) 由 UA_MODE 控制
- 滚动次数 / 等待时间参数化 (SCROLL_CYCLES, WAIT_MIN, WAIT_MAX)
- 二次重试 ENABLE_SECOND_PASS
- data-asin 兜底 ENABLE_FALLBACK_ASIN
- 验证码 / 反机器人简单检测 (_looks_like_captcha)
- 断点续爬 (checkpoint) 与本地数据保存 (data/)
- 详情页采集 (标题 / 价格 / 描述) 与缺失字段回填
- 调试 HTML 保存 (debug_*.html)
- 统一异常日志 (类型 / repr / traceback)
- Fallback requests 抓取(可选)避免完全空洞 (在 Playwright失败时)
- 迭代可注入 metrics: 列表页耗时 [LIST_TIME] secs=...
"""

import time
import random
import traceback
import os
from typing import List, Dict, Any, Optional
import platform
import asyncio

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import requests

from .proxy_manager import get_random_proxy
from .storage_manager import save_checkpoint, load_checkpoint, save_data
from .logger import log_info, log_error

# ===== Windows 事件循环修复（确保使用 Proactor，避免 NotImplementedError）=====
if platform.system() == "Windows":
    try:
        if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception as _loop_e:
        log_error(f"[LOOP] 设置 ProactorEventLoop 失败: {repr(_loop_e)}")

# === AUTO_TUNING_CONFIG_START ===
# 此区块由自迭代系统替换; 引擎只修改这里的变量而不动下面逻辑。
LIST_SELECTORS = [
    "div.s-result-item",
    "div.zg-grid-general-faceout",
    "div.p13n-sc-uncoverable-faceout",
    "div.a-section.a-spacing-none.p13n-asin",
    "div[data-asin]"
]
TITLE_SELECTORS = [
    "span.a-size-medium",
    "div.p13n-sc-truncated",
    "span.a-size-base-plus.a-color-base.a-text-normal",
    "h2 a span",
    "img"
]
PRICE_SELECTORS = [
    "span.a-price-whole",
    "span.p13n-sc-price",
    "span.a-offscreen"
]

UA_MODE = "desktop"            # 可为: desktop / hybrid
SCROLL_CYCLES = 3              # 列表页初次滚动次数
WAIT_MIN = 1.0                 # 滚动后最小随机等待
WAIT_MAX = 1.6                 # 滚动后最大随机等待
ENABLE_SECOND_PASS = True      # 是否允许二次重试
ENABLE_FALLBACK_ASIN = True    # 是否使用 data-asin 兜底解析
# === AUTO_TUNING_CONFIG_END ===

# User-Agent 集合
DESKTOP_UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]
MOBILE_UA_LIST = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S9060) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Mobile Safari/537.36",
]

# ================== 工具函数 ==================
def _safe_text(node) -> str:
    if not node:
        return ""
    if getattr(node, "name", "") == "img":
        return node.get("alt", "").strip()
    return node.get_text(strip=True)

def _choose_user_agent(mode: str) -> str:
    if mode == "hybrid":
        return random.choice(DESKTOP_UA_LIST + MOBILE_UA_LIST)
    return random.choice(DESKTOP_UA_LIST)

def _looks_like_captcha(html: str) -> bool:
    if not html:
        return False
    marks = ["captcha", "verify you are a human", "/errors/validatecaptcha", "enter the characters", "robot check"]
    low = html.lower()
    return any(m in low for m in marks)

def _dump_html(fname: str, html: str):
    try:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(html)
        log_info(f"[DEBUG] Saved HTML -> {fname} (len={len(html)})")
    except Exception as e:
        log_error(f"[DEBUG] Save HTML failed: {e}")

def _fallback_fetch(url: str) -> str:
    """
    Fallback: 在 Playwright 无法启动时使用 requests 简单获取页面 (可能被反爬裁剪，效果有限)。
    """
    headers = {
        "User-Agent": random.choice(DESKTOP_UA_LIST),
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200 and len(r.text) > 5000:
            return r.text
        log_error(f"[FALLBACK] 状态码={r.status_code} 内容长度={len(r.text)}")
    except Exception as e:
        log_error(f"[FALLBACK] requests 异常: {e}")
    return ""

# ================== 主入口 ==================
def scrape_amazon(
    url: str,
    max_items: int = 50,
    resume: bool = True,
    use_proxy: bool = True,
    deep_detail: bool = True,
    storage_mode: str = "local",
    headless: bool = True,
    second_pass: bool = True
) -> List[Dict[str, Any]]:
    """
    列表页爬取的统一入口。
    second_pass 参数与 ENABLE_SECOND_PASS 联合作用。
    """
    second_pass = second_pass and ENABLE_SECOND_PASS

    checkpoint = load_checkpoint(url) if (resume and storage_mode == "local") else None
    scraped = set(checkpoint["scraped"]) if checkpoint else set()
    results = list(checkpoint["results"]) if checkpoint else []

    proxy = get_random_proxy() if use_proxy else None
    ua = _choose_user_agent(UA_MODE)
    log_info(f"[INIT] URL={url} proxy={proxy} ua={ua} scraped={len(scraped)}")

    try:
        list_start = time.time()
        html = _load_page(url, proxy, ua, headless)
        list_elapsed = time.time() - list_start
        log_info(f"[LIST_TIME] secs={round(list_elapsed,3)}")

        if _looks_like_captcha(html):
            log_error("[CAPTCHA] 检测到验证码/人机验证页面。请启用 headless=False 或更换代理。")
            _dump_html("debug_captcha.html", html)
            raise RuntimeError("CAPTCHA detected")

        items = _parse_list(html, url, proxy, ua, headless, second_pass)
        if not items:
            _dump_html("debug_list_empty.html", html)
            raise RuntimeError("No items parsed from list page")

        for raw in items:
            if len(results) >= max_items:
                break
            detail_url = raw["detail_url"]
            if detail_url in scraped:
                continue

            if deep_detail:
                detail_data = scrape_detail_page(
                    detail_url,
                    proxy=proxy if use_proxy else None,
                    headless=headless
                )
                if not detail_data.get("title"):
                    detail_data["title"] = raw.get("title", "")
                if not detail_data.get("price"):
                    detail_data["price"] = raw.get("price", "")
                product = detail_data
            else:
                product = {
                    "title": raw.get("title", ""),
                    "url": detail_url,
                    "price": raw.get("price", "")
                }

            results.append(product)
            scraped.add(detail_url)
            if resume and storage_mode == "local":
                save_checkpoint(url, {"scraped": list(scraped), "results": results})
            log_info(f"[COLLECT] {product.get('title','(no-title)')} (total={len(results)})")

        if storage_mode == "local":
            save_data(url, results)
        log_info(f"[DONE] Collected={len(results)} (max_items={max_items})")
        return results

    except RuntimeError as re:
        # 尝试 fallback
        log_error(f"[RUNTIME] {re}")
        fb_html = _fallback_fetch(url)
        if fb_html:
            _dump_html("fallback_list.html", fb_html)
            log_info("[FALLBACK] 已保存 fallback_list.html 供手动分析。")
        return []
    except Exception as e:
        log_error(f"[EXCEPTION] scrape_amazon失败: type={type(e)} repr={repr(e)}")
        log_error(traceback.format_exc())
        return []

# ================== 页面加载 ==================
def _load_page(url: str, proxy: Optional[str], ua: str, headless: bool) -> str:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=headless,
                proxy={"server": proxy} if proxy else None
            )
            context = browser.new_context(user_agent=ua)
            page = context.new_page()
            page.goto(url, timeout=90000)

            # 同意 Cookie / 地区弹窗
            for sel in ['input#sp-cc-accept', 'button[name="accept"]', 'input[name="accept"]']:
                try:
                    page.click(sel, timeout=3000)
                    log_info(f"[CONSENT] Clicked {sel}")
                    break
                except Exception:
                    pass

            # 等待任意商品选择器
            try:
                page.wait_for_selector(", ".join(LIST_SELECTORS), timeout=60000)
            except PlaywrightTimeout:
                log_error("[WAIT] 列表选择器等待超时，进入滚动阶段。")

            for _ in range(SCROLL_CYCLES):
                page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                time.sleep(random.uniform(WAIT_MIN, WAIT_MAX))

            html = page.content()
            log_info(f"[PAGE] title={page.title()} final_url={page.url}")
            browser.close()
        return html
    except NotImplementedError as ne:
        raise RuntimeError(
            "NotImplementedError: 可能是 Windows 上事件循环策略错误 (SelectorEventLoopPolicy)。"
            "请确保使用 ProactorEventLoopPolicy 并已安装 Playwright 浏览器组件。"
        ) from ne
    except Exception as e:
        raise RuntimeError(f"Playwright 启动失败: {repr(e)}") from e

# ================== 列表解析 ==================
def _parse_list(html: str, url: str, proxy: Optional[str], ua: str, headless: bool, second_pass: bool) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "lxml")
    nodes: List[Any] = []
    for sel in LIST_SELECTORS:
        found = soup.select(sel)
        if found:
            log_info(f"[PARSE] {sel} -> {len(found)}")
            nodes.extend(found)
    nodes = list(dict.fromkeys(nodes))

    if not nodes and second_pass:
        log_info("[PARSE] 首次为空，触发二次重试。")
        html2 = _load_page(url, proxy, ua, headless)
        soup2 = BeautifulSoup(html2, "lxml")
        for sel in LIST_SELECTORS:
            found2 = soup2.select(sel)
            if found2:
                log_info(f"[PARSE-2] {sel} -> {len(found2)}")
                nodes.extend(found2)
        nodes = list(dict.fromkeys(nodes))

        if not nodes and ENABLE_FALLBACK_ASIN:
            fb_nodes = soup2.select("div[data-asin]")
            if fb_nodes:
                log_info(f"[FALLBACK] data-asin 兜底 -> {len(fb_nodes)}")
                nodes.extend(fb_nodes)
        nodes = list(dict.fromkeys(nodes))

        if not nodes:
            _dump_html("debug_second_pass_empty.html", html2)
            return []

    parsed: List[Dict[str, Any]] = []
    for node in nodes:
        link = node.select_one("a.a-link-normal[href*='/dp/']") or node.select_one("a.a-link-normal")
        if not link or not link.has_attr("href"):
            continue
        href = link["href"]
        if not href.startswith("/"):
            continue
        detail_url = "https://www.amazon.com" + href.split("?", 1)[0]

        # 标题
        title_text = ""
        for tsel in TITLE_SELECTORS:
            cand = node.select_one(tsel)
            if cand:
                title_text = _safe_text(cand)
                if title_text:
                    break

        # 价格
        price_text = ""
        for psel in PRICE_SELECTORS:
            candp = node.select_one(psel)
            if candp:
                price_text = _safe_text(candp)
                if price_text:
                    break

        parsed.append({
            "detail_url": detail_url,
            "title": title_text,
            "price": price_text
        })

    log_info(f"[PARSE] Parsed items={len(parsed)}")
    return parsed

# ================== 详情页采集 ==================
def scrape_detail_page(detail_url: str, proxy: Optional[str] = None, headless: bool = True) -> Dict[str, Any]:
    try:
        ua = _choose_user_agent(UA_MODE)
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=headless,
                proxy={"server": proxy} if proxy else None
            )
            context = browser.new_context(user_agent=ua)
            page = context.new_page()
            page.goto(detail_url, timeout=90000)
            try:
                page.wait_for_selector("#productTitle, #title, h1", timeout=45000)
            except PlaywrightTimeout:
                log_error(f"[DETAIL] 标题等待超时: {detail_url}")
            time.sleep(random.uniform(WAIT_MIN, WAIT_MAX))
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "lxml")
        title = soup.select_one("#productTitle") or soup.select_one("#title") or soup.select_one("h1")
        price = soup.select_one("span.a-price-whole") or soup.select_one("span.a-offscreen")
        desc = soup.select_one("#productDescription") or soup.select_one("#featurebullets_feature_div")

        data = {
            "title": _safe_text(title),
            "url": detail_url,
            "price": _safe_text(price),
            "desc": _safe_text(desc),
        }
        if not data["title"]:
            _dump_html("debug_detail_no_title.html", html)
        log_info(f"[DETAIL] Parsed: {data.get('title','(no-title)')}")
        return data
    except NotImplementedError as ne:
        log_error(f"[DETAIL-LOOP] NotImplementedError: {repr(ne)}")
        return {"url": detail_url, "error": "LoopPolicy/Playwright Issue"}
    except Exception as e:
        log_error(f"[DETAIL-EXCEPTION] {detail_url} type={type(e)} repr={repr(e)}")
        log_error(traceback.format_exc())
        return {"url": detail_url, "error": repr(e)}

# ================== 兼容旧入口 ==================
def scrape_amazon_bestsellers(**kwargs) -> List[Dict[str, Any]]:
    return scrape_amazon(url="https://www.amazon.com/bestsellers", **kwargs)

# ================== 简单自测入口（可选） ==================
if __name__ == "__main__":
    test_url = "https://www.amazon.com/bestsellers"
    data = scrape_amazon(test_url, max_items=10, resume=False, deep_detail=False, headless=True)
    print(f"Test collected {len(data)} items")
    if data:
        print(data[0])