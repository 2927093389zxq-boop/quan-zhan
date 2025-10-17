import streamlit as st
import json
import os

CONF_PATH = "config/api_keys.json"

def save_apis(apis):
    """Saves the list of APIs to the JSON file."""
    os.makedirs(os.path.dirname(CONF_PATH), exist_ok=True)
    with open(CONF_PATH, "w", encoding="utf-8") as f:
        json.dump(apis, f, ensure_ascii=False, indent=2)

def load_apis():
    """Loads the list of APIs from the JSON file."""
    if not os.path.exists(CONF_PATH):
        return []
    try:
        with open(CONF_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def render_api_admin():
    """Renders the API administration page."""
    st.header("🔗 第三方 API 管理")
    
    apis = load_apis()

    st.markdown("#### 当前已配置接口")
    if not apis:
        st.info("暂无接口，请在下方添加。")
    else:
        for i, api in enumerate(apis):
            st.write(f"{i+1}. **{api.get('name', 'N/A')}**: `{api.get('url', 'N/A')}`")

    st.markdown("---")
    st.markdown("#### 添加新接口")
    
    with st.form(key="api_form", clear_on_submit=True):
        name = st.text_input("接口名称", placeholder="例如：TikTok趋势API")
        url = st.text_input("接口 URL", placeholder="https://api.example.com/trends")
        submitted = st.form_submit_button("添加接口")

        if submitted:
            if name and url:
                apis.append({"name": name, "url": url})
                save_apis(apis)
                st.success(f"接口 '{name}' 添加成功！✅")
                st.rerun()
            else:
                st.error("接口名称和URL不能为空。")