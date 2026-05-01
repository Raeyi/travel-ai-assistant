"""
AI Agent核心实现
"""
from typing import Dict, List, Any, Optional, Tuple
import json
import re
from datetime import datetime
import logging

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from config.settings import settings
from core.tools import get_all_tools, TOOL_FUNCTIONS
from services.nlp_service import nlp_service
from database.redis_client import redis_client

logger = logging.getLogger(__name__)

class TravelAIAgent:
    """旅游AI Agent"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 初始化LLM
        llm_config = {
            "model": settings.OPENAI_MODEL,
            "temperature": 0.7,
            "openai_api_key": settings.OPENAI_API_KEY,
        }
        
        if settings.OPENAI_BASE_URL:
            llm_config["openai_api_base"] = settings.OPENAI_BASE_URL
        
        self.llm = ChatOpenAI(**llm_config)
        
        # 获取工具
        self.tools = get_all_tools()
        
        # 创建系统提示
        self.system_prompt = """你是一个专业的旅游客服助手，专门帮助用户规划旅行、预订服务、查询信息等。

你的能力包括：
1. 查询天气信息
2. 搜索航班信息
3. 搜索酒店信息
4. 推荐旅游景点
5. 计算旅行路线
6. 货币转换
7. 翻译服务
8. 创建旅行计划
9. 搜索旅游知识库

请遵循以下原则：
1. 友好热情，体现服务精神
2. 清晰准确，提供有用信息
3. 如果用户信息不完整，请主动询问缺少的信息
4. 尽量一次提供完整的回答
5. 如果使用工具获取了信息，请整理成用户易懂的格式
6. 保持专业但不过于正式

当前时间: {current_time}
"""
        
        # 创建Agent
        self.agent = self._create_agent()
        
        # 内存
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        logger.info(f"初始化TravelAIAgent，session_id: {self.session_id}")
    
    def _create_agent(self) -> AgentExecutor:
        """创建Agent执行器"""
        try:
            # 创建提示模板
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content=self.system_prompt.format(
                    current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessage(content="{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            
            # 创建Agent
            agent = create_openai_tools_agent(self.llm, self.tools, prompt)
            
            # 创建执行器
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=settings.DEBUG,
                max_iterations=5,
                early_stopping_method="generate",
                handle_parsing_errors=True
            )
            
            return agent_executor
            
        except Exception as e:
            logger.error(f"创建Agent失败: {e}")
            # 返回一个模拟的Agent执行器
            return None
    
    def process_message(self, message: str, message_type: str = "text", 
                       user_id: str = None) -> Dict[str, Any]:
        """处理用户消息"""
        try:
            # 获取对话历史
            context = redis_client.get_session_context(self.session_id)
            
            # 意图识别
            intent_result = nlp_service.detect_intent(message, context)
            intent = intent_result.get("intent", "general_qa")
            entities = intent_result.get("entities", {})
            confidence = intent_result.get("confidence", 0.0)
            
            logger.info(f"识别意图: {intent}, 置信度: {confidence}, 实体: {entities}")
            
            # 根据意图选择合适的处理方式
            if intent in ["flight_search", "hotel_search", "weather_query", 
                         "attraction_search", "currency_exchange", "translation",
                         "route_planning", "travel_plan"] and confidence > 0.6:
                # 使用工具处理
                response_data = self._process_with_tools(message, intent, entities)
            else:
                # 使用LLM直接回复
                response_data = self._process_with_llm(message, intent, entities, context)
            
            # 添加意图信息
            response_data["intent"] = intent
            response_data["entities"] = entities
            response_data["confidence"] = confidence
            
            # 生成建议回复
            response_data["suggestions"] = self._generate_suggestions(intent, entities)
            
            return response_data
            
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            return {
                "response": "抱歉，处理您的请求时出现了问题。请稍后重试。",
                "intent": "error",
                "confidence": 0.0,
                "suggestions": ["您可以尝试重新提问", "或者联系人工客服"]
            }
    
    def _process_with_tools(self, message: str, intent: str, 
                          entities: Dict[str, Any]) -> Dict[str, Any]:
        """使用工具处理消息"""
        try:
            if not self.agent:
                return self._fallback_response(message, intent, entities)
            
            # 准备工具调用参数
            tool_input = self._prepare_tool_input(message, intent, entities)
            
            # 执行Agent
            result = self.agent.invoke({
                "input": tool_input,
                "chat_history": self.memory.chat_memory.messages[-10:] if self.memory.chat_memory.messages else []
            })
            
            response = result.get("output", "抱歉，我暂时无法处理您的请求。")
            
            return {
                "response": response,
                "actions": self._extract_actions(intent, entities)
            }
            
        except Exception as e:
            logger.error(f"工具处理失败: {e}")
            return self._fallback_response(message, intent, entities)
    
    def _prepare_tool_input(self, message: str, intent: str, 
                           entities: Dict[str, Any]) -> str:
        """准备工具调用输入"""
        # 根据意图和实体构建更清晰的查询
        if intent == "weather_query":
            location = entities.get("location", "")
            date = entities.get("date", "")
            if location:
                query = f"查询{location}的天气"
                if date:
                    query += f"，日期是{date}"
                return query
        
        elif intent == "flight_search":
            departure = entities.get("origin") or entities.get("departure", "")
            arrival = entities.get("destination") or entities.get("arrival", "")
            date = entities.get("date", "")
            
            if departure and arrival:
                query = f"查询从{departure}到{arrival}的航班"
                if date:
                    query += f"，日期是{date}"
                return query
        
        elif intent == "hotel_search":
            location = entities.get("location", "")
            check_in = entities.get("check_in", "")
            check_out = entities.get("check_out", "")
            
            if location:
                query = f"查询{location}的酒店"
                if check_in and check_out:
                    query += f"，入住{check_in}，离店{check_out}"
                return query
        
        elif intent == "travel_plan":
            destination = entities.get("destination", "")
            start_date = entities.get("start_date", "")
            end_date = entities.get("end_date", "")
            
            if destination:
                query = f"创建{destination}的旅行计划"
                if start_date and end_date:
                    query += f"，从{start_date}到{end_date}"
                return query
        
        # 默认返回原消息
        return message
    
    def _process_with_llm(self, message: str, intent: str, 
                         entities: Dict[str, Any], 
                         context: List[Dict] = None) -> Dict[str, Any]:
        """使用LLM直接处理消息"""
        try:
            # 构建提示
            prompt = f"用户意图: {intent}\n"
            if entities:
                prompt += f"实体信息: {json.dumps(entities, ensure_ascii=False)}\n"
            
            prompt += f"用户消息: {message}\n\n"
            prompt += "请以旅游客服的身份进行回复:"
            
            # 调用LLM
            messages = [
                SystemMessage(content=self.system_prompt.format(
                    current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            return {
                "response": response.content,
                "actions": []
            }
            
        except Exception as e:
            logger.error(f"LLM处理失败: {e}")
            return {
                "response": "您好！我是您的旅游助手。请问有什么可以帮助您的吗？",
                "actions": []
            }
    
    def _fallback_response(self, message: str, intent: str, 
                          entities: Dict[str, Any]) -> Dict[str, Any]:
        """回退响应"""
        # 尝试直接调用工具函数
        try:
            if intent == "weather_query" and "location" in entities:
                location = entities["location"]
                date = entities.get("date")
                from core.tools import get_weather_tool
                response = get_weather_tool(location, date)
                return {"response": response, "actions": []}
            
            elif intent == "flight_search" and all(k in entities for k in ["origin", "destination", "date"]):
                from core.tools import search_flights_tool
                response = search_flights_tool(
                    entities["origin"],
                    entities["destination"],
                    entities["date"],
                    entities.get("return_date"),
                    entities.get("passengers", 1)
                )
                return {"response": response, "actions": []}
            
            elif intent == "hotel_search" and all(k in entities for k in ["location", "check_in", "check_out"]):
                from core.tools import search_hotels_tool
                response = search_hotels_tool(
                    entities["location"],
                    entities["check_in"],
                    entities["check_out"],
                    entities.get("guests", 1),
                    entities.get("rooms", 1)
                )
                return {"response": response, "actions": []}
            
        except Exception as e:
            logger.error(f"回退处理失败: {e}")
        
        # 最终回退
        return {
            "response": "您好！我是您的旅游助手。请问有什么可以帮助您的吗？",
            "actions": []
        }
    
    def _generate_suggestions(self, intent: str, entities: Dict[str, Any]) -> List[str]:
        """生成建议回复"""
        suggestions = []
        
        if intent == "weather_query":
            if "location" in entities:
                suggestions.append(f"{entities['location']}未来三天的天气")
                suggestions.append(f"{entities['location']}的最佳旅行季节")
            else:
                suggestions.append("您想查询哪个城市的天气？")
        
        elif intent == "flight_search":
            suggestions.append("查看具体航班详情")
            suggestions.append("比较不同航空公司的价格")
        
        elif intent == "hotel_search":
            suggestions.append("筛选4星以上酒店")
            suggestions.append("查看带早餐的酒店")
        
        elif intent == "travel_plan":
            suggestions.append("添加具体景点")
            suggestions.append("调整预算")
        
        else:
            suggestions.append("查询天气")
            suggestions.append("搜索航班")
            suggestions.append("预订酒店")
            suggestions.append("创建旅行计划")
        
        return suggestions[:3]  # 最多返回3个建议
    
    def _extract_actions(self, intent: str, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取操作建议"""
        actions = []
        
        if intent == "flight_search":
            actions.append({
                "type": "book_flight",
                "label": "预订航班",
                "data": entities
            })
        
        elif intent == "hotel_search":
            actions.append({
                "type": "book_hotel",
                "label": "预订酒店",
                "data": entities
            })
        
        elif intent == "travel_plan":
            actions.append({
                "type": "save_plan",
                "label": "保存计划",
                "data": entities
            })
        
        return actions
    
    def clear_memory(self):
        """清除记忆"""
        self.memory.clear()
        logger.info(f"已清除Agent记忆，session_id: {self.session_id}")

# 全局Agent实例
def get_travel_agent(session_id: str = None) -> TravelAIAgent:
    """获取旅游Agent实例"""
    return TravelAIAgent(session_id=session_id)

# 兼容性实例
travel_agent = TravelAIAgent()