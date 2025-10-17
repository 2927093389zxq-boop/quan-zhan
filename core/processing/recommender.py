"""
AI 推荐引擎
基于 OpenAI 生成智能建议
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

def ai_recommendation(summary: str, context: Optional[str] = None) -> str:
    """
    基于摘要生成 AI 推荐建议
    
    参数:
        summary: 数据摘要
        context: 可选的上下文信息
    
    返回:
        AI 生成的建议文本
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return "⚠️ 未配置 OPENAI_API_KEY，无法生成 AI 建议。请在 .env 文件中配置。"
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
作为一个电商和市场分析专家，请基于以下数据摘要提供专业的分析和建议：

数据摘要：
{summary}
"""
        
        if context:
            prompt += f"\n\n补充信息：\n{context}"
        
        prompt += "\n\n请提供：\n1. 数据趋势分析\n2. 潜在机会\n3. 风险提示\n4. 具体行动建议"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一个专业的电商和市场分析专家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content.strip()
    
    except ImportError:
        return "⚠️ OpenAI 库未安装。请运行: pip install openai"
    except Exception as e:
        return f"⚠️ AI 推荐生成失败: {str(e)}"


def generate_product_recommendations(products: list, user_preferences: dict = None) -> str:
    """
    基于产品列表生成推荐
    
    参数:
        products: 产品列表
        user_preferences: 用户偏好（可选）
    
    返回:
        推荐文本
    """
    if not products:
        return "没有可用的产品数据"
    
    # 构建产品摘要
    product_summary = f"共有 {len(products)} 个产品\n"
    
    # 提取价格范围
    prices = []
    for p in products[:20]:  # 只分析前20个
        price_str = p.get('price', '')
        if price_str and isinstance(price_str, str):
            # 尝试提取数字
            import re
            match = re.search(r'[\d.]+', price_str)
            if match:
                try:
                    prices.append(float(match.group()))
                except:
                    pass
    
    if prices:
        product_summary += f"价格范围: ${min(prices):.2f} - ${max(prices):.2f}\n"
        product_summary += f"平均价格: ${sum(prices)/len(prices):.2f}\n"
    
    # 添加一些示例产品
    product_summary += "\n示例产品：\n"
    for i, p in enumerate(products[:5]):
        title = p.get('title', 'N/A')[:50]
        price = p.get('price', 'N/A')
        product_summary += f"{i+1}. {title} - {price}\n"
    
    return ai_recommendation(product_summary, context=str(user_preferences) if user_preferences else None)
