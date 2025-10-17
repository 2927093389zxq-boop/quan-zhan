"""
批量爬取调度器
用于管理多个URL的批量采集任务
"""
import streamlit as st
from typing import List
from scrapers.logger import log_info, log_error

def run_batch(urls: List[str], storage_mode: str = "local", **kwargs):
    """
    批量运行爬取任务
    
    参数:
        urls: URL 列表
        storage_mode: 存储模式 (local, mongo, mysql, cloud)
        **kwargs: 其他可选参数
    """
    log_info(f"[BATCH] 开始批量任务，共 {len(urls)} 个URL")
    
    results = []
    success_count = 0
    fail_count = 0
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, url in enumerate(urls):
        try:
            status_text.text(f"正在处理 {idx+1}/{len(urls)}: {url[:50]}...")
            
            # 根据URL类型选择合适的爬虫
            if "amazon" in url.lower():
                from scrapers.amazon_scraper import scrape_amazon
                data = scrape_amazon(
                    url=url,
                    max_items=kwargs.get("max_items", 50),
                    deep_detail=kwargs.get("deep_detail", True),
                    storage_mode=storage_mode,
                    headless=True
                )
                if data:
                    results.extend(data)
                    success_count += 1
                    log_info(f"[BATCH] 成功采集 {url}: {len(data)} 条")
                else:
                    fail_count += 1
                    log_error(f"[BATCH] 采集失败 {url}")
            else:
                log_info(f"[BATCH] 跳过不支持的URL: {url}")
                fail_count += 1
            
        except Exception as e:
            fail_count += 1
            log_error(f"[BATCH] 处理 {url} 时出错: {str(e)}")
        
        # 更新进度条
        progress = (idx + 1) / len(urls)
        progress_bar.progress(progress)
    
    # 完成
    status_text.text(f"批量任务完成！成功: {success_count}, 失败: {fail_count}")
    log_info(f"[BATCH] 批量任务完成，共采集 {len(results)} 条数据")
    
    return results


def schedule_recurring_batch(urls: List[str], interval_hours: int = 24, **kwargs):
    """
    调度周期性批量任务
    
    参数:
        urls: URL 列表
        interval_hours: 执行间隔（小时）
        **kwargs: 其他参数
    """
    log_info(f"[SCHEDULE] 添加周期性任务，间隔 {interval_hours} 小时")
    
    # 这里可以与 APScheduler 集成
    # 暂时返回提示信息
    return {
        "status": "scheduled",
        "urls": len(urls),
        "interval_hours": interval_hours,
        "message": "周期性任务已添加到调度器"
    }
