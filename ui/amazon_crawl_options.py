import streamlit as st
from core.data_fetcher import get_platform_data

import streamlit as st
from core.data_fetcher import get_platform_data
from core.crawl.dispatcher import run_batch
from scrapers.logger import log_info

st.header("Amazon采集工具（全量增强版）")

mode = st.radio("模式选择", ["单页采集", "批量URL采集"], horizontal=True)

storage_mode = st.selectbox("存储模式", ["local", "mongo", "mysql", "cloud"], index=0)
deep_detail = st.checkbox("采集详情页", value=True)
max_items = st.slider("单页最大商品数", 10, 200, 50, 10)

if mode == "单页采集":
    pattern = st.radio("页面类型", ["Bestseller", "关键词搜索", "分类URL"], horizontal=True)
    keyword = ""
    category_url = ""
    if pattern == "关键词搜索":
        keyword = st.text_input("关键词", value="laptop")
    elif pattern == "分类URL":
        category_url = st.text_input("分类URL", value="https://www.amazon.com/bestsellers")

    if st.button("开始单页采集 🚀"):
        with st.spinner("采集中..."):
            data = get_platform_data(
                platform_name="Amazon",
                keyword=keyword,
                category_url=category_url,
                max_items=max_items,
                deep_detail=deep_detail
            )
        if data:
            st.success(f"完成，采集 {len(data)} 条。前10条预览：")
            st.json(data[:10])
        else:
            st.error("未采集到数据。请尝试更换模式或查看日志。")

else:
    st.write("批量模式：输入多个 URL（每行一个）")
    urls_text = st.text_area("URL 列表", value="https://www.amazon.com/bestsellers\nhttps://www.amazon.com/s?k=usb+hub")
    if st.button("开始批量采集 🧩"):
        urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
        if not urls:
            st.error("请提供至少一个 URL。")
        else:
            st.info(f"共 {len(urls)} 个任务，开始调度...")
            run_batch(urls, storage_mode=storage_mode)
            st.success("批量任务已完成（查看 data/ 或数据库中结果）。")

st.divider()
st.markdown("**日志提示：** 请查看根目录 scraper.log 或数据库内容。")