"""
LLM配置模块
"""
from typing import Optional
from config.settings import settings
import openai

def configure_openai():
    """配置OpenAI客户端"""
    # 设置API密钥
    openai.api_key = settings.OPENAI_API_KEY
    
    # 如果有自定义基础URL，设置它
    if settings.OPENAI_BASE_URL:
        openai.base_url = settings.OPENAI_BASE_URL
    
    # 配置代理（如果需要）
    # 注意：新版本OpenAI移除了proxies参数
    # 如果需要代理，可以通过环境变量设置
    # os.environ["HTTP_PROXY"] = "http://your-proxy:port"
    # os.environ["HTTPS_PROXY"] = "http://your-proxy:port"
    
    return {
        "api_key": settings.OPENAI_API_KEY,
        "base_url": settings.OPENAI_BASE_URL,
        "model": settings.OPENAI_MODEL
    }

# 全局配置
openai_config = configure_openai()