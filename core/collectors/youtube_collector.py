"""
YouTube 数据收集器
用于获取 YouTube 频道统计信息
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

def fetch_channel_stats(channel_id: str) -> Dict[str, Any]:
    """
    获取 YouTube 频道统计信息
    
    参数:
        channel_id: YouTube 频道 ID
    
    返回:
        频道统计信息字典
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    
    if not api_key:
        return {
            "error": "未配置 YOUTUBE_API_KEY",
            "channel_id": channel_id,
            "message": "请在 .env 文件中配置 YOUTUBE_API_KEY"
        }
    
    try:
        from googleapiclient.discovery import build
        
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        request = youtube.channels().list(
            part='statistics,snippet',
            id=channel_id
        )
        response = request.execute()
        
        if not response.get('items'):
            return {
                "error": "频道不存在",
                "channel_id": channel_id
            }
        
        channel = response['items'][0]
        snippet = channel.get('snippet', {})
        statistics = channel.get('statistics', {})
        
        return {
            "channel_id": channel_id,
            "title": snippet.get('title', 'N/A'),
            "description": snippet.get('description', 'N/A'),
            "subscriber_count": statistics.get('subscriberCount', '0'),
            "view_count": statistics.get('viewCount', '0'),
            "video_count": statistics.get('videoCount', '0'),
            "published_at": snippet.get('publishedAt', 'N/A')
        }
    except ImportError:
        return {
            "error": "Google API Client 未安装",
            "channel_id": channel_id,
            "message": "请安装 google-api-python-client: pip install google-api-python-client"
        }
    except Exception as e:
        return {
            "error": f"获取频道数据失败: {str(e)}",
            "channel_id": channel_id
        }
