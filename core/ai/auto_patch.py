import os, datetime, openai
openai.api_key = os.getenv("OPENAI_API_KEY")
PATCH_DIR = "patches"

def generate_autopatch():
    logpath = "logs/runtime.log"
    if not os.path.exists(logpath):
        return None, "无日志，无法生成补丁"
    with open(logpath, "r", encoding="utf-8") as f:
        tail = f.read()[-4000:]
    prompt = f"基于以下日志生成修复补丁建议（包含文件名和修改片段），不直接执行：\n{tail}"
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        max_tokens=900
    )
    suggestion = resp["choices"][0]["message"]["content"]
    os.makedirs(PATCH_DIR, exist_ok=True)
    fname = os.path.join(PATCH_DIR, f"patch_{datetime.date.today().isoformat()}.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write(suggestion)
    return fname, suggestion

def list_patches():
    if not os.path.exists(PATCH_DIR):
        return []
    return sorted([os.path.join(PATCH_DIR,f) for f in os.listdir(PATCH_DIR)])
