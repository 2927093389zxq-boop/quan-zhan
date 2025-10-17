# =========================================================================
# ===== 1. Windows 下 Playwright 事件循环策略修复 =====
# =========================================================================
import asyncio
import platform
# 注意：不要使用 WindowsSelectorEventLoopPolicy，会导致 Playwright 启动浏览器子进程时报 NotImplementedError
# 如果需要显式指定，可改为：
# if platform.system() == "Windows":
#     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# =========================================================================
# ===== 2. 其他导入 =====
# =========================================================================
import streamlit as st
from datetime import datetime
import os
import json
import socket
from dotenv import load_dotenv

# 分发相关
from distribution.license_manager import LicenseManager
from distribution.telemetry import TelemetrySystem

# 加载环境变量
load_dotenv()

# UI 与核心模块
from ui.dashboard import render_dashboard
from ui.analytics import render_analytics
from ui.prototype_view import render_prototype
from core.collectors.market_collector import fetch_all_trends
from core.collectors.youtube_collector import fetch_channel_stats
from core.collectors.policy_collector import fetch_latest_policies
from ui.api_admin import render_api_admin
from ui.auto_evolution import render_auto_evolution
from ui.auto_patch_view import render_auto_patch
from ui.ai_learning_center import render_ai_learning_center
from ui.source_attribution import render_sources

telemetry = None

def check_license():
    license_manager = LicenseManager()
    if not os.path.exists("license.json"):
        if os.path.exists(".dev"):
            return {"valid": True, "feature_set": "all"}
        return {"valid": False, "reason": "未找到许可证文件"}
    try:
        with open("license.json", "r") as f:
            license_data = json.load(f)
        result = license_manager.verify_license(license_data)
        if result["valid"] and license_data["data"].get("telemetry_enabled", True):
            global telemetry
            telemetry = TelemetrySystem()
            telemetry.collect_system_info()
        return result
    except Exception as e:
        return {"valid": False, "reason": f"许可证验证失败: {str(e)}"}

def render_license_page():
    st.title("📜 许可证激活")
    st.write("请上传有效许可证文件以激活软件。")
    uploaded_file = st.file_uploader("选择许可证文件", type=["json"])
    if uploaded_file:
        try:
            license_data = json.load(uploaded_file)
            license_manager = LicenseManager()
            result = license_manager.verify_license(license_data)
            if result["valid"]:
                with open("license.json", "w") as f:
                    json.dump(license_data, f)
                st.success("许可证已激活！")
                st.write(f"功能集: {result.get('feature_set','N/A')}")
                st.write(f"有效期: {result.get('expires_in_days','N/A')} 天")
                if st.button("开始使用"):
                    st.rerun()
            else:
                st.error(f"无效的许可证: {result['reason']}")
        except Exception as e:
            st.error(f"读取失败: {str(e)}")

def main():
    st.set_page_config(page_title="京盛传媒 企业版智能体", layout="wide")

    license_result = check_license()
    if not license_result.get("valid"):
        render_license_page()
        return

    st.title("京盛传媒 企业版智能体")

    # ===== 侧边栏菜单 =====
    menu = st.sidebar.selectbox(
        "导航",
        [
            "主页", "智能分析", "原型测试",
            "权威数据中心", "数据来源追踪", "YouTube", "TikTok",
            "Amazon采集工具", "爬虫自迭代",
            "AI 学习中心", "AI 自主迭代", "AI 自动修复",
            "API 管理", "政策中心", "系统概览", "日志与设置"
        ]
    )

    # 功能使用跟踪
    if telemetry:
        telemetry.track_feature_usage(menu)

    # ===== 路由逻辑 =====
    if menu == "主页":
        render_dashboard()
    elif menu == "系统概览":
        st.header("系统概览")
        st.metric("主机", socket.gethostname())
        st.metric("系统", platform.platform())
        st.metric("时间", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    elif menu == "智能分析":
        render_analytics()
    elif menu == "原型测试":
        render_prototype()
    elif menu == "权威数据中心":
        st.header("权威数据中心")
        st.info("数据来自：1688 / QuestMobile / 艾瑞 / 易观 等（示例）")
        for d in fetch_all_trends():
            st.markdown(
                f"**来源**：[{d.get('source')}]({d.get('url')})  \n"
                f"- 时间：{d.get('fetched_at')}  \n"
                f"- 内容：{d.get('metric', d.get('data',''))}  \n"
                f"- 权威度：{d.get('credibility','N/A')}"
            )
    elif menu == "数据来源追踪":
        render_sources()
    elif menu == "YouTube":
        st.header("YouTube 频道查询")
        cid = st.text_input("频道 ID")
        if st.button("获取频道统计"):
            try:
                res = fetch_channel_stats(cid)
                st.json(res)
            except Exception as e:
                st.error(str(e))
    elif menu == "TikTok":
        st.header("TikTok 趋势（占位）")
        st.write("当前使用公共占位源，正式接入请在 API 管理中添加接口。")
    elif menu == "Amazon采集工具":
        import ui.amazon_crawl_options
    elif menu == "爬虫自迭代":
        import ui.auto_evolution_crawler
    elif menu == "AI 学习中心":
        render_ai_learning_center()
    elif menu == "AI 自主迭代":
        render_auto_evolution()
    elif menu == "AI 自动修复":
        render_auto_patch()
    elif menu == "API 管理":
        render_api_admin()
    elif menu == "政策中心":
        st.header("政策中心")
        lst = fetch_latest_policies()
        for p in lst:
            st.markdown(
                f"**{p.get('source',{}).get('agency','未知')}** - {p.get('fetched_at')}  \n"
                f"{p.get('snippet','')}"
            )
    elif menu == "日志与设置":
        st.header("日志与设置")
        st.write("请在 config/config.json 中管理邮箱、调度等设置。")

if __name__ == "__main__":
    main()