import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from config.settings import settings
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class WeatherCondition(Enum):
    SUNNY = "晴天"
    CLOUDY = "多云"
    RAINY = "雨天"
    SNOWY = "雪天"
    FOGGY = "雾天"
    STORMY = "暴风雨"

@dataclass
class FlightInfo:
    flight_number: str
    airline: str
    departure: str
    arrival: str
    departure_time: str
    arrival_time: str
    duration: str
    price: float
    seats_available: int

@dataclass
class HotelInfo:
    name: str
    location: str
    check_in: str
    check_out: str
    price_per_night: float
    rating: float
    amenities: List[str]
    available_rooms: int

class ThirdPartyService:
    """第三方服务集成"""
    
    def __init__(self):
        # 模拟数据，实际项目中应该调用真实API
        self.mock_flights = self._init_mock_flights()
        self.mock_hotels = self._init_mock_hotels()
        self.mock_attractions = self._init_mock_attractions()
    
    def _init_mock_flights(self) -> List[FlightInfo]:
        """初始化模拟航班数据"""
        return [
            FlightInfo(
                flight_number="CA1234",
                airline="中国国际航空",
                departure="北京(PEK)",
                arrival="上海(PVG)",
                departure_time="08:00",
                arrival_time="10:30",
                duration="2小时30分钟",
                price=1200.0,
                seats_available=45
            ),
            FlightInfo(
                flight_number="MU5678",
                airline="东方航空",
                departure="北京(PEK)",
                arrival="上海(SHA)",
                departure_time="14:00",
                arrival_time="16:20",
                duration="2小时20分钟",
                price=980.0,
                seats_available=32
            )
        ]
    
    def _init_mock_hotels(self) -> List[HotelInfo]:
        """初始化模拟酒店数据"""
        return [
            HotelInfo(
                name="北京王府井希尔顿酒店",
                location="北京市东城区王府井大街",
                check_in="14:00",
                check_out="12:00",
                price_per_night=1200.0,
                rating=4.8,
                amenities=["免费WiFi", "游泳池", "健身房", "餐厅", "停车场"],
                available_rooms=10
            ),
            HotelInfo(
                name="上海外滩华尔道夫酒店",
                location="上海市黄浦区中山东一路",
                check_in="15:00",
                check_out="12:00",
                price_per_night=1800.0,
                rating=4.9,
                amenities=["免费WiFi", "水疗中心", "健身房", "多间餐厅", "停车场"],
                available_rooms=5
            )
        ]
    
    def _init_mock_attractions(self) -> List[Dict]:
        """初始化模拟景点数据"""
        return [
            {
                "name": "故宫博物院",
                "location": "北京",
                "description": "中国明清两代的皇家宫殿，世界文化遗产",
                "ticket_price": 60.0,
                "open_hours": "08:30-17:00",
                "rating": 4.9,
                "best_time_to_visit": "春季、秋季"
            },
            {
                "name": "外滩",
                "location": "上海",
                "description": "上海著名的滨江景观，欣赏黄浦江两岸风光",
                "ticket_price": 0.0,
                "open_hours": "全天开放",
                "rating": 4.8,
                "best_time_to_visit": "夜晚"
            }
        ]
    
    def get_weather(self, city: str, date: str = None) -> Dict[str, Any]:
        """获取天气信息（模拟）"""
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # 模拟不同城市的天气
            weather_data = {
                "北京": {
                    "temperature": {"min": 15, "max": 25},
                    "condition": WeatherCondition.SUNNY.value,
                    "humidity": 60,
                    "wind_speed": 10,
                    "air_quality": "良"
                },
                "上海": {
                    "temperature": {"min": 18, "max": 28},
                    "condition": WeatherCondition.CLOUDY.value,
                    "humidity": 70,
                    "wind_speed": 8,
                    "air_quality": "优"
                },
                "广州": {
                    "temperature": {"min": 22, "max": 32},
                    "condition": WeatherCondition.RAINY.value,
                    "humidity": 80,
                    "wind_speed": 12,
                    "air_quality": "良"
                }
            }
            
            city_weather = weather_data.get(
                city, 
                {
                    "temperature": {"min": 20, "max": 30},
                    "condition": WeatherCondition.SUNNY.value,
                    "humidity": 65,
                    "wind_speed": 10,
                    "air_quality": "良"
                }
            )
            
            return {
                "success": True,
                "city": city,
                "date": date,
                "weather": city_weather,
                "source": "mock_data"
            }
            
        except Exception as e:
            logger.error(f"获取天气信息失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_flights(self, departure: str, arrival: str, 
                      date: str, passengers: int = 1) -> Dict[str, Any]:
        """搜索航班（模拟）"""
        try:
            # 在实际项目中，这里应该调用航班API
            # 这里使用模拟数据
            
            matching_flights = []
            for flight in self.mock_flights:
                if departure in flight.departure and arrival in flight.arrival:
                    matching_flights.append({
                        "flight_number": flight.flight_number,
                        "airline": flight.airline,
                        "departure": flight.departure,
                        "arrival": flight.arrival,
                        "departure_time": flight.departure_time,
                        "arrival_time": flight.arrival_time,
                        "duration": flight.duration,
                        "price": flight.price * passengers,
                        "seats_available": flight.seats_available,
                        "date": date
                    })
            
            return {
                "success": True,
                "departure": departure,
                "arrival": arrival,
                "date": date,
                "passengers": passengers,
                "flights": matching_flights,
                "total_count": len(matching_flights),
                "source": "mock_data"
            }
            
        except Exception as e:
            logger.error(f"搜索航班失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_hotels(self, location: str, check_in: str, 
                     check_out: str, guests: int = 1, 
                     rooms: int = 1) -> Dict[str, Any]:
        """搜索酒店（模拟）"""
        try:
            # 计算入住天数
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
            nights = (check_out_date - check_in_date).days
            
            matching_hotels = []
            for hotel in self.mock_hotels:
                if location in hotel.location:
                    total_price = hotel.price_per_night * nights * rooms
                    
                    matching_hotels.append({
                        "name": hotel.name,
                        "location": hotel.location,
                        "check_in": hotel.check_in,
                        "check_out": hotel.check_out,
                        "price_per_night": hotel.price_per_night,
                        "total_price": total_price,
                        "rating": hotel.rating,
                        "amenities": hotel.amenities,
                        "available_rooms": hotel.available_rooms,
                        "nights": nights,
                        "guests": guests,
                        "rooms": rooms
                    })
            
            return {
                "success": True,
                "location": location,
                "check_in": check_in,
                "check_out": check_out,
                "guests": guests,
                "rooms": rooms,
                "hotels": matching_hotels,
                "total_count": len(matching_hotels),
                "source": "mock_data"
            }
            
        except Exception as e:
            logger.error(f"搜索酒店失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_attractions(self, location: str, 
                          keyword: str = None) -> Dict[str, Any]:
        """搜索景点（模拟）"""
        try:
            matching_attractions = []
            for attraction in self.mock_attractions:
                if location in attraction["location"]:
                    if keyword and keyword not in attraction["name"] and keyword not in attraction["description"]:
                        continue
                    matching_attractions.append(attraction)
            
            return {
                "success": True,
                "location": location,
                "keyword": keyword,
                "attractions": matching_attractions,
                "total_count": len(matching_attractions),
                "source": "mock_data"
            }
            
        except Exception as e:
            logger.error(f"搜索景点失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_currency_rate(self, from_currency: str, 
                         to_currency: str) -> Optional[float]:
        """获取汇率（模拟）"""
        try:
            # 模拟汇率数据
            rates = {
                "USD": {"CNY": 7.2, "EUR": 0.92, "JPY": 150},
                "CNY": {"USD": 0.14, "EUR": 0.13, "JPY": 21},
                "EUR": {"USD": 1.09, "CNY": 7.8, "JPY": 163},
                "JPY": {"USD": 0.0067, "CNY": 0.048, "EUR": 0.0061}
            }
            
            if from_currency in rates and to_currency in rates[from_currency]:
                return rates[from_currency][to_currency]
            else:
                return 1.0  # 默认汇率
                
        except Exception as e:
            logger.error(f"获取汇率失败: {e}")
            return None
    
    def convert_currency(self, amount: float, 
                        from_currency: str, 
                        to_currency: str) -> Dict[str, Any]:
        """货币转换"""
        try:
            rate = self.get_currency_rate(from_currency, to_currency)
            if rate is None:
                return {
                    "success": False,
                    "error": "无法获取汇率"
                }
            
            converted_amount = amount * rate
            
            return {
                "success": True,
                "amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "rate": rate,
                "converted_amount": converted_amount,
                "source": "mock_data"
            }
            
        except Exception as e:
            logger.error(f"货币转换失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_transportation_info(self, origin: str, 
                              destination: str, 
                              mode: str = "driving") -> Dict[str, Any]:
        """获取交通信息（模拟）"""
        try:
            # 模拟交通信息
            transportation_data = {
                "distance": "150公里",
                "duration": "2小时",
                "mode": mode,
                "route": f"从{origin}到{destination}的最佳路线",
                "estimated_cost": 300.0,
                "steps": [
                    f"从{origin}出发",
                    "沿G2京沪高速行驶",
                    f"到达{destination}"
                ]
            }
            
            return {
                "success": True,
                "origin": origin,
                "destination": destination,
                "mode": mode,
                "info": transportation_data,
                "source": "mock_data"
            }
            
        except Exception as e:
            logger.error(f"获取交通信息失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def make_payment(self, order_id: str, amount: float, 
                    payment_method: str = "alipay") -> Dict[str, Any]:
        """模拟支付"""
        try:
            # 在实际项目中，这里应该调用支付接口
            # 这里返回模拟的成功响应
            
            return {
                "success": True,
                "order_id": order_id,
                "amount": amount,
                "payment_method": payment_method,
                "transaction_id": f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "status": "success",
                "message": "支付成功",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"支付失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }

# 全局第三方服务实例
third_party_service = ThirdPartyService()

# 为兼容性提供的函数
def get_weather_info(location: str, date: str = None) -> str:
    """获取天气信息（字符串格式）"""
    result = third_party_service.get_weather(location, date)
    if result["success"]:
        weather = result["weather"]
        return (f"{location}的天气：{weather['condition']}，"
                f"温度{weather['temperature']['min']}~{weather['temperature']['max']}°C，"
                f"湿度{weather['humidity']}%，空气质量{weather['air_quality']}")
    else:
        return f"无法获取{location}的天气信息"

def search_flights(departure: str, arrival: str, date: str, 
                   return_date: str = None, passengers: int = 1) -> List[Dict]:
    """搜索航班"""
    result = third_party_service.search_flights(departure, arrival, date, passengers)
    return result.get("flights", []) if result["success"] else []

def search_hotels(location: str, check_in: str, check_out: str, 
                  guests: int = 1, rooms: int = 1) -> List[Dict]:
    """搜索酒店"""
    result = third_party_service.search_hotels(location, check_in, check_out, guests, rooms)
    return result.get("hotels", []) if result["success"] else []

def get_attractions(location: str, keyword: str = None) -> List[Dict]:
    """获取景点信息"""
    result = third_party_service.search_attractions(location, keyword)
    return result.get("attractions", []) if result["success"] else []

def calculate_route(origin: str, destination: str, mode: str = "driving") -> Dict:
    """计算路线"""
    result = third_party_service.get_transportation_info(origin, destination, mode)
    return result.get("info", {}) if result["success"] else {}

def get_currency_rate(from_currency: str, to_currency: str) -> Optional[float]:
    """获取汇率"""
    return third_party_service.get_currency_rate(from_currency, to_currency)

def translate_text(text: str, target_language: str) -> str:
    """翻译文本（模拟）"""
    # 在实际项目中，这里应该调用翻译API
    translations = {
        "你好": {"en": "Hello", "ja": "こんにちは", "ko": "안녕하세요"},
        "谢谢": {"en": "Thank you", "ja": "ありがとう", "ko": "감사합니다"},
        "再见": {"en": "Goodbye", "ja": "さようなら", "ko": "안녕히 가세요"}
    }
    
    if text in translations and target_language in translations[text]:
        return translations[text][target_language]
    return f"[翻译] {text} -> {target_language}"