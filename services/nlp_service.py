from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from typing import Dict, List, Any, Optional, Tuple
import json
import re
from datetime import datetime
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class NLPService:
    """自然语言处理服务"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.1,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_BASE_URL
        )
        
        # 意图定义
        self.intents = {
            "flight_search": "查询航班信息",
            "flight_book": "预订航班",
            "hotel_search": "查询酒店信息",
            "hotel_book": "预订酒店",
            "attraction_search": "查询景点信息",
            "travel_plan": "制定旅行计划",
            "weather_query": "查询天气",
            "route_planning": "路线规划",
            "currency_exchange": "货币兑换",
            "translation": "翻译服务",
            "emergency_help": "紧急帮助",
            "general_qa": "一般问答",
            "food_recommendation": "美食推荐",
            "shopping_info": "购物信息"
        }
        
        # 实体定义
        self.entities = [
            "location", "date", "time", "price_range", "person_count",
            "destination", "origin", "airline", "hotel_name", "attraction_name",
            "cuisine", "budget", "duration", "preference", "room_type"
        ]
    
    def detect_intent(self, text: str, context: List[Dict] = None) -> Dict[str, Any]:
        """检测用户意图"""
        system_prompt = """你是一个旅游意图识别专家。请分析用户的输入，识别意图并提取关键信息。

可识别的意图包括：
- flight_search: 用户想要查询航班信息
- flight_book: 用户想要预订航班
- hotel_search: 用户想要查询酒店信息
- hotel_book: 用户想要预订酒店
- attraction_search: 用户想要查询旅游景点
- travel_plan: 用户想要制定旅行计划
- weather_query: 用户想要查询天气
- route_planning: 用户想要规划路线
- currency_exchange: 用户想要货币兑换
- translation: 用户需要翻译
- emergency_help: 用户需要紧急帮助
- general_qa: 一般性问答
- food_recommendation: 用户想要美食推荐
- shopping_info: 用户想要购物信息

请以JSON格式返回结果，包含以下字段：
- intent: 主要意图
- confidence: 置信度(0-1)
- entities: 提取的实体信息
- additional_info: 其他相关信息
"""
        
        user_prompt = f"用户输入: {text}"
        if context:
            user_prompt += f"\n上下文: {json.dumps(context[-5:], ensure_ascii=False)}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            result = json.loads(response.content)
            
            # 验证结果格式
            if "intent" not in result:
                result["intent"] = "general_qa"
            if "confidence" not in result:
                result["confidence"] = 0.7
            if "entities" not in result:
                result["entities"] = {}
            if "additional_info" not in result:
                result["additional_info"] = {}
            
            return result
            
        except Exception as e:
            logger.error(f"意图识别失败: {e}")
            return {
                "intent": "general_qa",
                "confidence": 0.5,
                "entities": {},
                "additional_info": {"error": str(e)}
            }
    
    def extract_entities(self, text: str, intent: str) -> Dict[str, Any]:
        """提取关键实体"""
        system_prompt = f"""请从文本中提取旅游相关的实体信息。当前意图: {intent}

需要提取的实体类型:
- location: 地点(城市、国家、景点名称)
- date: 日期(YYYY-MM-DD格式)
- time: 时间
- duration: 持续时间(如: 3天2晚)
- person_count: 人数
- budget: 预算
- hotel_name: 酒店名称
- airline: 航空公司
- flight_number: 航班号
- room_type: 房间类型
- preference: 偏好(如: 靠近地铁, 海景房等)

请以JSON格式返回，只包含提取到的实体。
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"文本: {text}")
        ]
        
        try:
            response = self.llm.invoke(messages)
            entities = json.loads(response.content)
            return entities
        except Exception as e:
            logger.error(f"实体提取失败: {e}")
            return {}
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """分析用户情感"""
        system_prompt = """分析用户的情绪状态，返回以下信息:
- sentiment: positive/neutral/negative/urgent
- emotion: 具体情绪(如: happy, angry, anxious等)
- urgency_level: 紧急程度(1-5)
- needs_attention: 是否需要人工介入(True/False)
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"用户输入: {text}")
        ]
        
        try:
            response = self.llm.invoke(messages)
            sentiment = json.loads(response.content)
            return sentiment
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return {
                "sentiment": "neutral",
                "emotion": "unknown",
                "urgency_level": 1,
                "needs_attention": False
            }
    
    def generate_response(self, intent: str, entities: Dict, 
                         context: List[Dict] = None) -> str:
        """生成自然语言回复"""
        system_prompt = f"""你是一个专业的旅游客服助手。请根据以下信息生成友好、专业的回复。

意图: {intent}
实体信息: {json.dumps(entities, ensure_ascii=False)}
"""
        
        if context:
            system_prompt += f"\n对话历史: {json.dumps(context[-3:], ensure_ascii=False)}"
        
        system_prompt += """
请确保回复:
1. 友好热情，体现服务精神
2. 清晰准确，提供有用信息
3. 适当提问以获取更多信息
4. 保持专业但不过于正式
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="请生成客服回复:")
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"回复生成失败: {e}")
            return "您好！我是您的旅游助手。请问有什么可以帮助您的吗？"
    
    def validate_travel_info(self, info: Dict[str, Any]) -> Tuple[bool, str]:
        """验证旅行信息完整性"""
        required_fields = {
            "flight_search": ["origin", "destination", "date"],
            "hotel_search": ["location", "check_in", "check_out"],
            "travel_plan": ["destination", "start_date", "end_date"]
        }
        
        intent = info.get("intent", "")
        if intent in required_fields:
            missing = []
            for field in required_fields[intent]:
                if field not in info.get("entities", {}):
                    missing.append(field)
            
            if missing:
                return False, f"缺少必要信息: {', '.join(missing)}"
        
        return True, "信息完整"

# 全局NLP服务实例
nlp_service = NLPService()