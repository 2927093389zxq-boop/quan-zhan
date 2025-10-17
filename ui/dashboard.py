import streamlit as st
import pandas as pd
from datetime import datetime

# 导入我们新创建的核心数据获取函数和平台列表
from core.data_fetcher import get_platform_data, PLATFORM_LIST

def render_dashboard():
    """
    渲染全新的、可交互的主仪表盘页面。
    """
    st.header("📊 动态数据总览")

    # 1. 保留顶部的实时信息
    col1, col2, col3 = st.columns(3)
    col1.metric("当前时间", datetime.now().strftime("%H:%M:%S"))
    col2.metric("联网状态", "在线 ✅")
    col3.metric("数据源数量", f"{len(PLATFORM_LIST)} 个")

    st.markdown("---") # 添加一条分割线

    # 2. 创建交互式数据看板
    st.markdown("### 🔥 跨平台热门产品看板")
    st.caption("选择一个平台，然后点击按钮来获取最新的公开热门商品数据。")

    # 创建一个两列的布局
    col_select, col_button = st.columns([3, 1])

    with col_select:
        # 创建平台选择下拉菜单
        selected_platform = st.selectbox(
            "请选择数据平台:",
            options=PLATFORM_LIST,
            index=0  # 默认选中第一个平台 'Amazon'
        )

    with col_button:
        # 创建一个垂直对齐的按钮
        st.write("") # 占位符让按钮垂直居中
        st.write("")
        fetch_button = st.button("🚀 获取数据", use_container_width=True)

    # 3. 获取并显示数据
    if fetch_button:
        # 当用户点击按钮时，执行以下操作
        with st.spinner(f"正在从 {selected_platform} 获取数据，请稍候..."):
            # 调用我们的核心函数
            data = get_platform_data(selected_platform)

            if data:
                # 如果成功获取到数据，将其转换为Pandas DataFrame并显示
                # 使用st.dataframe可以让表格滚动，比st.table更适合大量数据
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            else:
                # 如果返回空列表，显示提示信息
                # 注意：具体的错误信息已经在 get_platform_data 函数内部通过 st.error 显示了
                st.info("未能获取到数据。请查看上方的警告或错误信息。")
