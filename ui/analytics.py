import streamlit as st
import pandas as pd
from core.processing.anomaly_detector import detect_anomalies

def render_analytics():
    """Renders the analytics page for anomaly detection and insights."""
    st.header("🧠 智能分析")

    st.markdown("#### 数据指标输入")
    st.write("示例输入：历史销量（用于检测异常）")

    data = [100, 103, 120, 115, 420, 130, 110]
    df = pd.DataFrame({"销量": data})
    st.line_chart(df)

    st.markdown("#### 异常检测结果")
    anomaly_indices = detect_anomalies(data)
    if anomaly_indices:
        for idx in anomaly_indices:
            st.warning(f"在位置 {idx+1} 检测到异常点，值为 {data[idx]}。")
    else:
        st.success("未发现明显异常。")

    st.markdown("#### AI 解释（示例）")
    st.info("系统检测到第 5 个数据点出现异常增长（约 +265%），可能与促销活动或投放策略调整有关。")

    st.markdown("#### 来源验证（权威交叉验证）")
    st.write("""
    - 📊 1688趋势中心：供需指数波动
    - 📉 QuestMobile：App活跃下降 2%
    - 📈 艾瑞咨询：广告ROI 同期增长
    - ✅ 综合可信度：0.87 (高)
    """)
