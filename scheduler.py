# scheduler.py
import time, json, os
from apscheduler.schedulers.background import BackgroundScheduler
from core.collectors.spider_engine import SpiderEngine
from core.collectors.market_collector import fetch_all_trends
from core.processing.recommender import ai_recommendation
from publishers.mail_sender import send_email
from core.ai.evolution_engine import analyze_logs_with_gpt
from core.ai.auto_patch import generate_autopatch
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

CONFIG_PATH = "config/config.json"

def load_cfg():
    if os.path.exists(CONFIG_PATH):
        return json.load(open(CONFIG_PATH, "r", encoding="utf-8"))
    return {"report_time":"08:00","poll_interval_minutes":60,"evolution_check_interval_hours":2}

cfg = load_cfg()

def job_collect_and_update():
    print("[Job] 收集市场权威数据")
    trends = fetch_all_trends()
    # 这里可插入保存到 DB 的逻辑
    print("[Job] 权威数据采集结果：", trends)

def job_daily_report():
    print("[Job] 生成并发送每日报告")
    # 模拟摘要，真实应从DB与指标计算
    summary = "示例摘要：北美GMV上升，欧洲下滑"
    ai_text = ai_recommendation(summary) if os.getenv("OPENAI_API_KEY") else "未配置 OpenAI Key"
    html = f"<h3>京盛传媒智能体 每日报告</h3><p>{summary}</p><h4>AI建议</h4><pre>{ai_text}</pre>"
    try:
        send_email("京盛传媒智能体 每日报告", html)
    except Exception as e:
        print("邮件发送失败：", e)

def job_evolution_check():
    print("[Job] 自我进化检查（AI 分析日志）")
    try:
        suggestion = analyze_logs_with_gpt()
        patch_path, _ = generate_autopatch()
        print("[Job] 已生成演化建议与补丁：", patch_path)
    except Exception as e:
        print("自我进化失败：", e)

def start_scheduler():
    sched = BackgroundScheduler()
    # 每小时抓取一次数据
    sched.add_job(job_collect_and_update, 'interval', minutes=cfg.get("poll_interval_minutes",60))
    # 每日固定时刻发送日报（config内report_time 格式 HH:MM）
    hh, mm = cfg.get("report_time","08:00").split(":")
    sched.add_job(job_daily_report, 'cron', hour=int(hh), minute=int(mm))
    # 每 N 小时自我进化检查
    sched.add_job(job_evolution_check, 'interval', hours=cfg.get("evolution_check_interval_hours",2))
    sched.start()
    print("[Scheduler] 启动完成")
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()