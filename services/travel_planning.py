from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from config.settings import settings
from database.mysql_client import SessionLocal
from database.redis_client import redis_client
import logging

logger = logging.getLogger(__name__)

class TravelPlanningService:
    """旅行规划服务"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_BASE_URL
        )
    
    def generate_travel_plan(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """生成旅行计划"""
        destination = user_input.get("destination", "")
        start_date = user_input.get("start_date", "")
        end_date = user_input.get("end_date", "")
        budget = user_input.get("budget", 0)
        travelers = user_input.get("travelers", 1)
        interests = user_input.get("interests", [])
        preferences = user_input.get("preferences", {})
        
        # 计算旅行天数
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            days = (end - start).days
        except:
            days = 3  # 默认3天
        
        system_prompt = f"""你是一个专业的旅行规划师，请为游客制定详细的旅行计划。

旅行信息：
- 目的地：{destination}
- 旅行天数：{days}天
- 预算：{budget}元
- 人数：{travelers}人
- 兴趣：{', '.join(interests) if interests else '未指定'}
- 偏好：{json.dumps(preferences, ensure_ascii=False)}

请生成一个完整的旅行计划，包含以下部分：
1. 总体概述
2. 每日详细行程
3. 住宿建议
4. 餐饮推荐
5. 交通安排
6. 预算分配
7. 注意事项

请以JSON格式返回，结构如下：
{{
    "overview": "总体概述",
    "daily_itinerary": [
        {{
            "day": 1,
            "date": "{start_date}",
            "morning": "上午活动",
            "afternoon": "下午活动",
            "evening": "晚上活动",
            "meals": {{"breakfast": "早餐建议", "lunch": "午餐建议", "dinner": "晚餐建议"}},
            "accommodation": "住宿建议",
            "transportation": "交通安排",
            "estimated_cost": 估算费用
        }}
    ],
    "budget_breakdown": {{
        "accommodation": {{"budget": 预算, "description": "说明"}},
        "transportation": {{"budget": 预算, "description": "说明"}},
        "food": {{"budget": 预算, "description": "说明"}},
        "activities": {{"budget": 预算, "description": "说明"}},
        "shopping": {{"budget": 预算, "description": "说明"}},
        "miscellaneous": {{"budget": 预算, "description": "说明"}}
    }},
    "tips": ["提示1", "提示2", "提示3"],
    "emergency_contacts": ["紧急联系人1", "紧急联系人2"]
}}
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="请生成旅行计划:")
        ]
        
        try:
            response = self.llm.invoke(messages)
            plan = json.loads(response.content)
            
            # 添加元数据
            plan["metadata"] = {
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "days": days,
                "budget": budget,
                "travelers": travelers,
                "interests": interests,
                "generated_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "plan": plan,
                "message": "旅行计划生成成功"
            }
            
        except Exception as e:
            logger.error(f"旅行计划生成失败: {e}")
            return {
                "success": False,
                "plan": {},
                "message": f"生成旅行计划时出错: {str(e)}"
            }
    
    def optimize_plan(self, plan: Dict[str, Any], 
                     constraints: Dict[str, Any]) -> Dict[str, Any]:
        """优化旅行计划"""
        system_prompt = """请根据给定的约束条件优化旅行计划。

约束条件：
"""
        
        for key, value in constraints.items():
            system_prompt += f"- {key}: {value}\n"
        
        system_prompt += f"""
原始计划：
{json.dumps(plan, ensure_ascii=False, indent=2)}

请优化计划，使其更符合约束条件，同时保持计划的完整性和吸引力。
"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="请优化旅行计划:")
        ]
        
        try:
            response = self.llm.invoke(messages)
            optimized_plan = json.loads(response.content)
            return optimized_plan
        except Exception as e:
            logger.error(f"旅行计划优化失败: {e}")
            return plan
    
    def generate_itinerary_summary(self, plan: Dict[str, Any]) -> str:
        """生成行程摘要"""
        try:
            summary = f"旅行计划摘要 - {plan.get('metadata', {}).get('destination', '未知目的地')}\n\n"
            summary += f"行程时间: {plan.get('metadata', {}).get('start_date')} 至 {plan.get('metadata', {}).get('end_date')}\n"
            summary += f"总天数: {plan.get('metadata', {}).get('days')}天\n"
            summary += f"预算: ¥{plan.get('metadata', {}).get('budget', 0):,.2f}\n\n"
            
            # 添加每日行程概要
            daily_itinerary = plan.get('daily_itinerary', [])
            if daily_itinerary:
                summary += "每日行程概要:\n"
                for day_plan in daily_itinerary:
                    summary += f"第{day_plan.get('day')}天: "
                    summary += f"上午: {day_plan.get('morning', '未安排')[:20]}... | "
                    summary += f"下午: {day_plan.get('afternoon', '未安排')[:20]}...\n"
            
            # 预算摘要
            budget = plan.get('budget_breakdown', {})
            if budget:
                summary += "\n预算分配:\n"
                for category, info in budget.items():
                    summary += f"- {category}: ¥{info.get('budget', 0):,.2f}\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"生成行程摘要失败: {e}")
            return "无法生成行程摘要"
    
    def save_travel_plan(self, user_id: str, plan: Dict[str, Any]) -> str:
        """保存旅行计划到缓存"""
        try:
            plan_id = f"plan_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            key = f"user:{user_id}:plan:{plan_id}"
            
            # 保存到Redis，有效期7天
            redis_client.set(key, plan, expire=604800)
            
            return plan_id
        except Exception as e:
            logger.error(f"保存旅行计划失败: {e}")
            return ""
    
    def get_travel_plan(self, user_id: str, plan_id: str) -> Optional[Dict[str, Any]]:
        """从缓存获取旅行计划"""
        try:
            key = f"user:{user_id}:plan:{plan_id}"
            return redis_client.get(key)
        except Exception as e:
            logger.error(f"获取旅行计划失败: {e}")
            return None

# 全局旅行规划服务实例
travel_planning_service = TravelPlanningService()