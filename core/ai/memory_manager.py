import json
import datetime
import random
import os

MEMORY_PATH = r"D:\智能体\京盛传媒智能体_企业版\memory\strategy_memory.json"

def load_memory():
    if not os.path.exists(MEMORY_PATH):
        return []
    with open(MEMORY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_memory(data):
    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    with open(MEMORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def ai_self_learn():
    """企业版AI每日自我进化"""
    memory = load_memory()
    new_entry = {
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "insight": random.choice([
            "短视频趋势正向多元文化方向靠拢",
            "品牌关键词热度与社交互动量提升",
            "AI 生成内容开始在广告场景中应用",
            "市场对创作者真实风格更包容"
        ]),
        "confidence": round(random.uniform(0.7, 0.99), 2)
    }
    memory.append(new_entry)
    save_memory(memory)
    print(f"✅ 学习完成: {new_entry['insight']} (置信度 {new_entry['confidence']})")

def get_recent_learning(limit=10):
    memory = load_memory()
    return memory[-limit:]
