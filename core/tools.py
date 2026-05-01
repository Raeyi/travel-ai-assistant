"""
Agent工具定义
"""
from langchain.tools import Tool
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import json

from services.third_party import (
    get_weather_info,
    search_flights,
    search_hotels,
    get_attractions,
    calculate_route,
    get_currency_rate,
    translate_text
)
from services.travel_planning import travel_planning_service
from services.knowledge_base import knowledge_base_service
from services.nlp_service import nlp_service

logger = logging.getLogger(__name__)

def get_weather_tool(location: str, date: Optional[str] = None) -> str:
    """获取天气信息"""
    try:
        from services.third_party import third_party_service
        result = third_party_service.get_weather(location, date)
        if result["success"]:
            weather = result["weather"]
            return (f"{location}的天气：{weather['condition']}，"
                    f"温度{weather['temperature']['min']}~{weather['temperature']['max']}°C，"
                    f"湿度{weather['humidity']}%，空气质量{weather['air_quality']}")
        else:
            return f"无法获取{location}的天气信息"
    except Exception as e:
        logger.error(f"获取天气失败: {e}")
        return f"获取天气信息时出错: {str(e)}"

def search_flights_tool(departure: str, arrival: str, date: str, 
                       return_date: Optional[str] = None, 
                       passengers: int = 1) -> str:
    """搜索航班信息"""
    try:
        from services.third_party import third_party_service
        result = third_party_service.search_flights(departure, arrival, date, passengers)
        if result["success"] and result["flights"]:
            flights = result["flights"]
            response = f"找到{len(flights)}个从{departure}到{arrival}的航班：\n"
            for i, flight in enumerate(flights[:5], 1):  # 显示前5个
                response += (f"{i}. {flight['airline']} {flight['flight_number']}: "
                           f"{flight['departure_time']} → {flight['arrival_time']}, "
                           f"价格: ¥{flight['price']:.2f}\n")
            return response
        else:
            return f"没有找到从{departure}到{arrival}的航班"
    except Exception as e:
        logger.error(f"搜索航班失败: {e}")
        return f"搜索航班时出错: {str(e)}"

def search_hotels_tool(location: str, check_in: str, check_out: str,
                      guests: int = 1, rooms: int = 1) -> str:
    """搜索酒店信息"""
    try:
        from services.third_party import third_party_service
        result = third_party_service.search_hotels(location, check_in, check_out, guests, rooms)
        if result["success"] and result["hotels"]:
            hotels = result["hotels"]
            response = f"在{location}找到{len(hotels)}家酒店：\n"
            for i, hotel in enumerate(hotels[:5], 1):  # 显示前5个
                response += (f"{i}. {hotel['name']}: "
                           f"¥{hotel['price_per_night']:.2f}/晚，"
                           f"评分: {hotel['rating']}，"
                           f"设施: {', '.join(hotel['amenities'][:3])}\n")
            return response
        else:
            return f"在{location}没有找到符合条件的酒店"
    except Exception as e:
        logger.error(f"搜索酒店失败: {e}")
        return f"搜索酒店时出错: {str(e)}"

def get_attractions_tool(location: str, keyword: Optional[str] = None) -> str:
    """获取景点信息"""
    try:
        from services.third_party import third_party_service
        result = third_party_service.search_attractions(location, keyword)
        if result["success"] and result["attractions"]:
            attractions = result["attractions"]
            response = f"在{location}找到{len(attractions)}个景点：\n"
            for i, attraction in enumerate(attractions[:5], 1):
                response += (f"{i}. {attraction['name']}: "
                           f"{attraction['description'][:50]}...，"
                           f"门票: ¥{attraction['ticket_price']}，"
                           f"开放时间: {attraction['open_hours']}\n")
            return response
        else:
            keyword_msg = f"包含'{keyword}'的" if keyword else ""
            return f"在{location}没有找到{keyword_msg}景点"
    except Exception as e:
        logger.error(f"搜索景点失败: {e}")
        return f"搜索景点时出错: {str(e)}"

def calculate_route_tool(origin: str, destination: str, mode: str = "driving") -> str:
    """计算路线"""
    try:
        from services.third_party import third_party_service
        result = third_party_service.get_transportation_info(origin, destination, mode)
        if result["success"]:
            info = result["info"]
            return (f"从{origin}到{destination}的路线({mode}):\n"
                    f"距离: {info['distance']}\n"
                    f"时间: {info['duration']}\n"
                    f"费用: 约¥{info['estimated_cost']:.2f}\n"
                    f"路线: {' -> '.join(info['steps'][:3])}...")
        else:
            return f"无法计算从{origin}到{destination}的路线"
    except Exception as e:
        logger.error(f"计算路线失败: {e}")
        return f"计算路线时出错: {str(e)}"

def currency_convert_tool(amount: float, from_currency: str, to_currency: str) -> str:
    """货币转换"""
    try:
        from services.third_party import third_party_service
        result = third_party_service.convert_currency(amount, from_currency, to_currency)
        if result["success"]:
            return (f"货币转换: {amount} {from_currency} = "
                    f"{result['converted_amount']:.2f} {to_currency} "
                    f"(汇率: {result['rate']})")
        else:
            return f"无法进行货币转换: {from_currency} -> {to_currency}"
    except Exception as e:
        logger.error(f"货币转换失败: {e}")
        return f"货币转换时出错: {str(e)}"

def translate_tool(text: str, target_language: str) -> str:
    """翻译文本"""
    try:
        translated = translate_text(text, target_language)
        return f"翻译结果: {translated}"
    except Exception as e:
        logger.error(f"翻译失败: {e}")
        return f"翻译时出错: {str(e)}"

def create_travel_plan_tool(destination: str, start_date: str, end_date: str,
                          budget: Optional[float] = None, travelers: int = 1,
                          interests: List[str] = None) -> str:
    """创建旅行计划"""
    try:
        plan_data = {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "budget": budget,
            "travelers": travelers,
            "interests": interests or []
        }
        
        result = travel_planning_service.generate_travel_plan(plan_data)
        if result["success"]:
            plan_id = travel_planning_service.save_travel_plan("temp_user", result["plan"])
            summary = travel_planning_service.generate_itinerary_summary(result["plan"])
            return f"✅ 旅行计划创建成功！\n计划ID: {plan_id}\n\n{summary}"
        else:
            return f"❌ 创建旅行计划失败: {result['message']}"
    except Exception as e:
        logger.error(f"创建旅行计划失败: {e}")
        return f"创建旅行计划时出错: {str(e)}"

def search_knowledge_tool(query: str, category: Optional[str] = None) -> str:
    """搜索知识库"""
    try:
        results = knowledge_base_service.search(query, category, limit=3)
        if results:
            response = f"找到{len(results)}条相关信息：\n"
            for i, result in enumerate(results, 1):
                response += f"{i}. {result['title']}: {result['content'][:100]}...\n"
            return response
        else:
            return f"没有找到关于'{query}'的信息"
    except Exception as e:
        logger.error(f"搜索知识库失败: {e}")
        return f"搜索知识库时出错: {str(e)}"

# 创建LangChain工具
def get_all_tools():
    """获取所有工具"""
    tools = [
        Tool(
            name="get_weather",
            func=get_weather_tool,
            description="获取指定地点的天气信息。参数: location(地点), date(日期，可选)"
        ),
        Tool(
            name="search_flights",
            func=search_flights_tool,
            description="搜索航班信息。参数: departure(出发地), arrival(目的地), date(日期), return_date(返程日期，可选), passengers(乘客数，默认1)"
        ),
        Tool(
            name="search_hotels",
            func=search_hotels_tool,
            description="搜索酒店信息。参数: location(地点), check_in(入住日期), check_out(离店日期), guests(客人数量，默认1), rooms(房间数量，默认1)"
        ),
        Tool(
            name="get_attractions",
            func=get_attractions_tool,
            description="获取旅游景点信息。参数: location(地点), keyword(关键词，可选)"
        ),
        Tool(
            name="calculate_route",
            func=calculate_route_tool,
            description="计算路线。参数: origin(起点), destination(终点), mode(交通方式: driving/walking/transit，默认driving)"
        ),
        Tool(
            name="currency_convert",
            func=currency_convert_tool,
            description="货币转换。参数: amount(金额), from_currency(原货币), to_currency(目标货币)"
        ),
        Tool(
            name="translate",
            func=translate_tool,
            description="翻译文本。参数: text(要翻译的文本), target_language(目标语言)"
        ),
        Tool(
            name="create_travel_plan",
            func=create_travel_plan_tool,
            description="创建旅行计划。参数: destination(目的地), start_date(开始日期), end_date(结束日期), budget(预算，可选), travelers(旅行人数，默认1), interests(兴趣列表，可选)"
        ),
        Tool(
            name="search_knowledge",
            func=search_knowledge_tool,
            description="搜索知识库。参数: query(查询内容), category(类别，可选)"
        )
    ]
    return tools

# 工具函数映射
TOOL_FUNCTIONS = {
    "get_weather": get_weather_tool,
    "search_flights": search_flights_tool,
    "search_hotels": search_hotels_tool,
    "get_attractions": get_attractions_tool,
    "calculate_route": calculate_route_tool,
    "currency_convert": currency_convert_tool,
    "translate": translate_tool,
    "create_travel_plan": create_travel_plan_tool,
    "search_knowledge": search_knowledge_tool
}