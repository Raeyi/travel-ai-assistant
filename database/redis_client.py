import redis
import json
from typing import Optional, Any, Union
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        logger.info(f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """存储数据到Redis"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            self.client.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """从Redis获取数据"""
        try:
            value = self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """删除Redis键"""
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    def get_session_context(self, session_id: str) -> list:
        """获取会话上下文"""
        key = f"session:{session_id}:context"
        context = self.get(key)
        return context if context else []
    
    def add_to_session_context(self, session_id: str, message: dict) -> bool:
        """添加到会话上下文"""
        key = f"session:{session_id}:context"
        context = self.get_session_context(session_id)
        context.append(message)
        # 限制上下文长度
        if len(context) > 20:  # 保留最近20条消息
            context = context[-20:]
        return self.set(key, context, expire=3600)  # 1小时过期

# 全局Redis客户端实例
redis_client = RedisClient()