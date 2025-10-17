import streamlit as st
from core.ai.auto_patch import generate_autopatch, list_patches
import os

def render_auto_patch():
    """
    Renders the AI auto-patch generation and management page.
    """
    st.header("🧩 AI 自动修复与补丁管理")

    st.markdown("""
    系统可以自动读取日志，调用AI分析潜在的运行时错误，并生成修复建议（补丁）。
    **注意：** 所有补丁都需要由人工审查，不会自动应用。
    """)

    if st.button("立即为我生成补丁"):
        with st.spinner("AI 正在分析系统运行日志并生成补丁..."):
            try:
                path, content = generate_autopatch()
                if path and content:
                    st.success(f"补丁已生成：`{path}`")
                    st.text_area("补丁内容预览", content, height=300)
                else:
                    st.warning(content) # Show "No logs found" message
            except Exception as e:
                st.error(f"生成失败: {e}")

    st.markdown("### 📜 已生成的补丁列表")
    try:
        patches = list_patches()
        if patches:
            for p in reversed(patches): # Show newest first
                st.markdown(f"- 📄 `{os.path.basename(p)}`")
        else:
            st.info("暂无补丁文件。")
    except Exception as e:
        st.error(f"无法列出补丁文件: {e}")