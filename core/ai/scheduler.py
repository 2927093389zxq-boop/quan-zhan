import schedule
import time
import datetime
from core.ai.memory_manager import ai_self_learn

def job():
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 智能体开始学习...")
    try:
        ai_self_learn()
        print("✅ 本轮学习完成\n")
    except Exception as e:
        print("❌ 学习出错:", e)

# 每天执行10次（0, 2, 5, 8, 11, 14, 17, 20, 22, 23点）
for hour in [0, 2, 5, 8, 11, 14, 17, 20, 22, 23]:
    schedule.every().day.at(f"{hour:02d}:00").do(job)

print("📘 京盛传媒智能体 企业版 - 自学习调度已启动（每日10次）")

while True:
    schedule.run_pending()
    time.sleep(60)
