import streamlit as st
import os
from core.auto_crawler_iter.iteration_engine import CrawlerIterationEngine
from core.auto_crawler_iter.metrics_collector import MetricsCollector
from scrapers.logger import log_info

st.header("🧬 爬虫自我迭代控制台")

engine = CrawlerIterationEngine()
collector = MetricsCollector()

col1, col2 = st.columns(2)
with col1:
    if st.button("运行一轮迭代"):
        result = engine.run_once()
        st.write(result)
with col2:
    metrics = collector.collect()
    st.subheader("当前指标")
    st.json(metrics)

st.divider()
st.subheader("候选补丁列表")
patch_dir = engine.cfg["patch_output_dir"]
patches = []
if os.path.isdir(patch_dir):
    patches = [f for f in os.listdir(patch_dir) if f.endswith(".patch")]
if not patches:
    st.info("暂无补丁候选。点击上方“运行一轮迭代”生成。")
else:
    for p in patches:
        tag = p.replace(".patch", "")
        with st.expander(f"补丁: {p}"):
            st.code(open(os.path.join(patch_dir, p), "r", encoding="utf-8").read(), language="diff")
            apply = st.button(f"应用补丁 {tag}")
            if apply:
                res = engine.apply_patch(tag)
                st.success(res)

st.divider()
st.caption("提示：补丁只修改 scrapers/amazon_scraper.py，生成时写入 sandbox 目录以及 diff 补丁，需手动应用。")