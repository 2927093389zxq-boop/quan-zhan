import streamlit as st
from core.ai.memory_manager import get_recent_learning

def render_ai_learning_center():
    """Renders the AI's learning center page."""
    st.header("🧠 智能体学习中心")
    st.info("企业版系统会定时进行自我学习与进化，以下为最近的学习记录：")

    try:
        data = get_recent_learning()
        if not data:
            st.warning("暂无学习记录，请等待系统自动学习任务运行。")
            return

        for d in reversed(data): # Show newest first
            st.markdown(f"- **{d.get('time', 'N/A')}** — {d.get('insight', '无内容')} (置信度: {d.get('confidence', 0)})")
    except Exception as e:
        st.error(f"无法加载学习记录: {e}")
        st.info("这可能是因为 `memory` 文件夹或文件尚未创建。当学习任务第一次运行时，它们会自动生成。")