import random

# 在这里配置你的代理池（可改为从文件或远程服务动态加载）
PROXY_LIST = [
    # 示例（需替换为真实可用代理）
    # "http://user:pass@ip:port",
    # "http://ip:port",
]

def get_random_proxy():
    if not PROXY_LIST:
        return None
    return random.choice(PROXY_LIST)