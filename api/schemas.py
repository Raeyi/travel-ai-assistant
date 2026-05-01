from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
import re

class MessageType(str, Enum):
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"

class Intent(str, Enum):
    FLIGHT_SEARCH = "flight_search"
    FLIGHT_BOOK = "flight_book"
    HOTEL_SEARCH = "hotel_search"
    HOTEL_BOOK = "hotel_book"
    ATTRACTION_SEARCH = "attraction_search"
    TRAVEL_PLAN = "travel_plan"
    WEATHER_QUERY = "weather_query"
    ROUTE_PLANNING = "route_planning"
    CURRENCY_EXCHANGE = "currency_exchange"
    TRANSLATION = "translation"
    EMERGENCY_HELP = "emergency_help"
    GENERAL_QA = "general_qa"
    FOOD_RECOMMENDATION = "food_recommendation"
    SHOPPING_INFO = "shopping_info"

class UserMessage(BaseModel):
    """用户消息请求模型"""
    session_id: str = Field(..., description="会话ID")
    user_id: Optional[str] = Field(default=None, description="用户ID")
    message: str = Field(..., description="用户消息内容")
    message_type: MessageType = Field(default=MessageType.TEXT, description="消息类型")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="时间戳")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")
    
    @validator('session_id')
    def validate_session_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("session_id不能为空")
        return v.strip()

class AIResponse(BaseModel):
    """AI响应模型"""
    session_id: str = Field(..., description="会话ID")
    response_id: str = Field(..., description="响应ID")
    message: str = Field(..., description="AI回复内容")
    intent: Optional[Intent] = Field(default=None, description="识别的意图")
    entities: Optional[Dict[str, Any]] = Field(default_factory=dict, description="提取的实体")
    confidence: Optional[float] = Field(default=None, ge=0, le=1, description="置信度")
    suggestions: Optional[List[str]] = Field(default_factory=list, description="建议回复")
    actions: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="建议操作")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    
    @validator('response_id')
    def generate_response_id(cls, v, values):
        if not v:
            return f"resp_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        return v

class TravelPlanRequest(BaseModel):
    """旅行计划请求模型"""
    user_id: str = Field(..., description="用户ID")
    destination: str = Field(..., description="目的地")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    budget: Optional[float] = Field(default=None, ge=0, description="预算")
    travelers: int = Field(default=1, ge=1, le=20, description="旅行人数")
    interests: Optional[List[str]] = Field(default_factory=list, description="兴趣列表")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="偏好设置")
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError("结束日期必须晚于开始日期")
        return v
    
    @validator('destination')
    def validate_destination(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("目的地不能为空")
        return v.strip()

class TravelPlanResponse(BaseModel):
    """旅行计划响应模型"""
    plan_id: str = Field(..., description="计划ID")
    user_id: str = Field(..., description="用户ID")
    destination: str = Field(..., description="目的地")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    budget: Optional[float] = Field(default=None, description="预算")
    travelers: int = Field(..., description="旅行人数")
    itinerary: Dict[str, Any] = Field(..., description="行程安排")
    status: str = Field(default="draft", description="状态")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

class FlightSearchRequest(BaseModel):
    """航班搜索请求模型"""
    departure: str = Field(..., description="出发地")
    arrival: str = Field(..., description="目的地")
    departure_date: date = Field(..., description="出发日期")
    return_date: Optional[date] = Field(default=None, description="返程日期")
    passengers: int = Field(default=1, ge=1, le=10, description="乘客人数")
    class_type: Optional[str] = Field(default="economy", description="舱位类型")
    direct_only: bool = Field(default=False, description="仅直飞")
    
    @validator('departure', 'arrival')
    def validate_location(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("地点不能为空")
        return v.strip().upper()
    
    @validator('return_date')
    def validate_return_date(cls, v, values):
        if v and 'departure_date' in values and v <= values['departure_date']:
            raise ValueError("返程日期必须晚于出发日期")
        return v

class HotelSearchRequest(BaseModel):
    """酒店搜索请求模型"""
    location: str = Field(..., description="地点")
    check_in: date = Field(..., description="入住日期")
    check_out: date = Field(..., description="离店日期")
    guests: int = Field(default=1, ge=1, le=10, description="客人数量")
    rooms: int = Field(default=1, ge=1, le=5, description="房间数量")
    min_price: Optional[float] = Field(default=None, ge=0, description="最低价格")
    max_price: Optional[float] = Field(default=None, ge=0, description="最高价格")
    star_rating: Optional[int] = Field(default=None, ge=1, le=5, description="星级")
    
    @validator('check_out')
    def validate_dates(cls, v, values):
        if 'check_in' in values and v <= values['check_in']:
            raise ValueError("离店日期必须晚于入住日期")
        return v

class WeatherQueryRequest(BaseModel):
    """天气查询请求模型"""
    location: str = Field(..., description="地点")
    query_date: Optional[date] = Field(default=None, description="查询日期")
    days: Optional[int] = Field(default=1, ge=1, le=7, description="天数")

class KnowledgeSearchRequest(BaseModel):
    """知识库搜索请求模型"""
    query: str = Field(..., description="查询内容")
    category: Optional[str] = Field(default=None, description="类别")
    limit: int = Field(default=5, ge=1, le=20, description="返回数量")

class KnowledgeAddRequest(BaseModel):
    """知识添加请求模型"""
    category: str = Field(..., description="类别")
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")
    source: str = Field(default="user", description="来源")

class UserCreateRequest(BaseModel):
    """用户创建请求模型"""
    user_id: str = Field(..., description="用户ID")
    username: Optional[str] = Field(default=None, description="用户名")
    email: Optional[str] = Field(default=None, description="邮箱")
    phone: Optional[str] = Field(default=None, description="电话")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="偏好")
    
    @validator('email')
    def validate_email(cls, v):
        if v is not None:
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, v):
                raise ValueError("邮箱格式无效")
        return v

class ConversationHistoryRequest(BaseModel):
    """对话历史请求模型"""
    session_id: str = Field(..., description="会话ID")
    limit: int = Field(default=20, ge=1, le=100, description="返回数量")
    offset: int = Field(default=0, ge=0, description="偏移量")

class PaymentRequest(BaseModel):
    """支付请求模型"""
    order_id: str = Field(..., description="订单ID")
    amount: float = Field(..., gt=0, description="金额")
    payment_method: str = Field(default="alipay", description="支付方式")
    user_id: str = Field(..., description="用户ID")
    description: Optional[str] = Field(default=None, description="描述")

class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="状态")
    version: str = Field(..., description="版本")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    services: Dict[str, bool] = Field(default_factory=dict, description="服务状态")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(default=None, description="详细信息")
    code: int = Field(..., description="错误码")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")