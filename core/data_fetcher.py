"""
Core Data Fetcher Module
统一数据获取接口，支持多平台数据采集
"""
import streamlit as st
from typing import List, Dict, Any, Optional

# 支持的平台列表
PLATFORM_LIST = [
    "Amazon",
    "1688",
    "Taobao",
    "JD.com",
    "Pinduoduo"
]

def get_platform_data(
    platform_name: str,
    keyword: str = "",
    category_url: str = "",
    max_items: int = 50,
    deep_detail: bool = True,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    统一的平台数据获取接口
    
    参数:
        platform_name: 平台名称 (如 "Amazon", "1688" 等)
        keyword: 搜索关键词
        category_url: 分类URL
        max_items: 最大商品数量
        deep_detail: 是否采集详情页
        **kwargs: 其他可选参数
    
    返回:
        商品数据列表
    """
    try:
        if platform_name == "Amazon":
            return _fetch_amazon_data(keyword, category_url, max_items, deep_detail, **kwargs)
        elif platform_name == "1688":
            return _fetch_1688_data(keyword, max_items)
        elif platform_name in ["Taobao", "JD.com", "Pinduoduo"]:
            st.warning(f"{platform_name} 数据源暂未实现，返回示例数据")
            return _fetch_demo_data(platform_name, max_items)
        else:
            st.error(f"不支持的平台: {platform_name}")
            return []
    except Exception as e:
        st.error(f"获取 {platform_name} 数据时发生错误: {str(e)}")
        return []

def _fetch_amazon_data(
    keyword: str,
    category_url: str,
    max_items: int,
    deep_detail: bool,
    **kwargs
) -> List[Dict[str, Any]]:
    """从 Amazon 获取数据"""
    try:
        from scrapers.amazon_scraper import scrape_amazon
        
        # 构建URL
        if category_url:
            url = category_url
        elif keyword:
            url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}"
        else:
            url = "https://www.amazon.com/bestsellers"
        
        # 调用爬虫
        results = scrape_amazon(
            url=url,
            max_items=max_items,
            deep_detail=deep_detail,
            resume=True,
            use_proxy=False,
            storage_mode=kwargs.get("storage_mode", "local"),
            headless=True
        )
        
        return results
    except ImportError:
        st.error("Amazon 爬虫模块未安装")
        return []
    except Exception as e:
        st.error(f"Amazon 数据获取失败: {str(e)}")
        return []

def _fetch_1688_data(keyword: str, max_items: int) -> List[Dict[str, Any]]:
    """从 1688 获取数据（示例实现）"""
    st.info("1688 数据源使用示例数据")
    return _fetch_demo_data("1688", max_items)

def _fetch_demo_data(platform: str, max_items: int) -> List[Dict[str, Any]]:
    """
    返回示例数据用于测试和演示
    """
    demo_products = [
        {
            "title": f"{platform} 示例商品 #{i+1}",
            "price": f"${(i+1) * 10}.99",
            "url": f"https://example.com/product/{i+1}",
            "rating": 4.5,
            "reviews": 100 + i * 10
        }
        for i in range(min(max_items, 10))
    ]
    return demo_products
