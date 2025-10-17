import os
import openai
import json
import datetime

LOG_PATH = "logs/runtime.log"
EVOLUTION_REPORT = "logs/evolution_suggestions.json"

def read_logs(n_chars=5000):
    """读取日志文件的最后n个字符"""
    if not os.path.exists(LOG_PATH):
        return "无日志"
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            return content[-n_chars:] if len(content) > n_chars else content
    except Exception as e:
        return f"读取日志出错: {e}"

def analyze_logs_with_gpt():
    """使用OpenAI分析日志并生成改进建议"""
    logs = read_logs()
    
    # 如果没有日志，提供友好的提示
    if logs == "无日志":
        return "系统尚未生成任何日志。请先运行其他功能，产生一些日志记录。"
    
    prompt = f"""你是系统工程师。请阅读下面运行日志，给出：
1) 问题总结
2) 改进建议（按优先级）
3) 需要修改的文件与示例代码片段（不直接覆盖）
日志：
{logs}
请用中文输出。"""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "未配置 OPENAI_API_KEY 环境变量，请在.env文件中添加。"
    
    openai.api_key = api_key
    
    try:
        # 使用最新的API调用方式
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            max_tokens=800
        )
        suggestions = response.choices[0].message.content
        
        # 确保logs目录存在
        os.makedirs("logs", exist_ok=True)
        
        # 保存结果到JSON文件
        with open(EVOLUTION_REPORT, "w", encoding="utf-8") as f:
            json.dump({
                "time": datetime.datetime.now().isoformat(),
                "suggestions": suggestions
            }, f, ensure_ascii=False, indent=2)
            
        return suggestions
    except Exception as e:
        return f"调用OpenAI API时出错: {e}"