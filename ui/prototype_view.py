import streamlit as st
from core.collectors.spider_engine import SpiderEngine
from core.processing.recommender import ai_recommendation

def render_prototype():
    """
    Renders the prototype testing page in the Streamlit UI.
    Allows testing of data collection and AI analysis modules.
    """
    st.header("原型测试（采集→AI分析）")
    
    # Use tabs for a cleaner layout
    tab1, tab2, tab3 = st.tabs(["采集验证", "AI分析验证", "完整流程"])

    with tab1:
        st.subheader("采集验证")
        urls = st.text_area("输入URL，每行一个", "https://www.cbp.gov\nhttps://www.gov.uk", key="prototype_urls")
        if st.button("开始采集"):
            with st.spinner("正在采集数据..."):
                urls_list = [u.strip() for u in urls.splitlines() if u.strip()]
                if not urls_list:
                    st.warning("请输入有效的URL。")
                else:
                    se = SpiderEngine()
                    results = se.collect(urls_list)
                    st.success(f"采集完成！共 {len(results)} 个结果。")
                    for i, r in enumerate(results):
                        st.text_area(f"结果 {i+1}", r[:1000] if isinstance(r, str) else str(r), height=200, key=f"res_{i}")

    with tab2:
        st.subheader("AI分析验证")
        text = st.text_area("输入市场摘要", "示例：北美市场GMV上涨15%，但用户活跃度下降5%。", key="prototype_ai_text")
        if st.button("调用AI进行分析"):
            with st.spinner("AI正在生成建议..."):
                recommendation = ai_recommendation(text)
                st.success("AI建议已生成：")
                st.write(recommendation)

    with tab3:
        st.subheader("完整流程（示例）")
        st.info("此流程模拟从采集数据到AI分析的全过程。")
        if st.button("运行完整流程示例"):
            with st.spinner("正在执行完整流程..."):
                urls = ["https://www.cbp.gov", "https://www.gov.uk"]
                se = SpiderEngine()
                results = se.collect(urls)
                st.write("---")
                st.write("**第一步：数据采集结果（摘要）**")
                st.json([res[:200] + "..." if isinstance(res, str) else str(res) for res in results])
                
                st.write("---")
                st.write("**第二步：调用AI进行分析**")
                summary_for_ai = "政策网站数据已更新，显示北美和英国的贸易政策有微小调整。"
                recommendation = ai_recommendation(summary_for_ai)
                st.success("AI建议：")
                st.write(recommendation)
