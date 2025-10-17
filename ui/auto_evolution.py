import streamlit as st
from core.ai.evolution_engine import analyze_logs_with_gpt

def render_auto_evolution():
    """
    Renders the AI auto-evolution page.
    Allows triggering AI analysis of runtime logs.
    """
    st.header("🤖 AI 自主迭代（日志分析）")
    st.info("系统将调用 AI 检查 `logs/runtime.log` 文件，分析潜在问题并生成改进建议。")

    if st.button("立即分析日志"):
        with st.spinner("AI 正在分析日志，请稍候..."):
            try:
                # This function should return the suggestions
                suggestions = analyze_logs_with_gpt()
                st.success("✅ 分析完成！")
                st.text_area("AI 生成的建议", suggestions, height=400)
            except Exception as e:
                st.error(f"分析失败: {e}")
                st.warning("请确保您的 OpenAI API Key 已在 .env 文件中正确配置。")
