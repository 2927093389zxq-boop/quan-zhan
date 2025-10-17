import json, os, requests, datetime

CONFIG_PATH = "config/policy_sources.json"

def load_policy_sources():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {"country": "US", "agency": "U.S. Customs and Border Protection", "endpoint": "https://www.cbp.gov"},
        {"country": "UK", "agency": "Department for International Trade", "endpoint": "https://www.gov.uk"}
    ]

def fetch_latest_policies():
    """获取全球政策更新并做来源权威验证"""
    out = []
    for src in load_policy_sources():
        try:
            r = requests.get(src["endpoint"], timeout=10)
            r.raise_for_status() # Raise an exception for bad status codes
            out.append({
                "source": src,
                "http_status": r.status_code,
                "credibility": 0.97 if "gov" in src["endpoint"] else 0.85,
                "fetched_at": datetime.datetime.utcnow().isoformat(),
                "snippet": r.text[:600]
            })
        except Exception as e:
            out.append({
                "source": src,
                "error": str(e),
                "credibility": 0.4
            })
    return out