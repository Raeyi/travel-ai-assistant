from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
import logging
import json
import uuid
from datetime import datetime, timedelta
import os
from pathlib import Path

from api.schemas import (
    UserMessage, AIResponse, TravelPlanRequest, TravelPlanResponse,
    FlightSearchRequest, HotelSearchRequest, WeatherQueryRequest,
    KnowledgeSearchRequest, KnowledgeAddRequest, UserCreateRequest,
    ConversationHistoryRequest, PaymentRequest, HealthCheckResponse,
    ErrorResponse, MessageType
)
from core.agent import TravelAIAgent, travel_agent
from services.nlp_service import nlp_service
from services.travel_planning import travel_planning_service
from services.knowledge_base import knowledge_base_service
from services.third_party import (
    third_party_service, get_weather_info, search_flights,
    search_hotels, get_attractions, calculate_route,
    get_currency_rate, translate_text
)
from database.mysql_client import SessionLocal, get_db
from database.redis_client import redis_client
import utils.audio_processor as audio_processor
import utils.file_processor as file_processor
from config.settings import settings

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="旅游业AI客服系统API",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置为具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建上传目录
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局变量
chat_agents = {}

def get_or_create_agent(session_id: str) -> TravelAIAgent:
    """获取或创建Agent"""
    if session_id not in chat_agents:
        chat_agents[session_id] = TravelAIAgent(session_id=session_id)
    return chat_agents[session_id]

@app.get("/", tags=["根路径"])
async def root():
    """根路径"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "旅游业AI客服系统API",
        "status": "running"
    }

@app.get("/health", response_model=HealthCheckResponse, tags=["健康检查"])
async def health_check():
    """健康检查端点"""
    services = {
        "api": True,
        "database": False,
        "redis": False,
        "llm": False
    }
    
    # 检查数据库连接
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        services["database"] = True
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
    
    # 检查Redis连接
    try:
        redis_client.client.ping()
        services["redis"] = True
    except Exception as e:
        logger.error(f"Redis连接失败: {e}")
    
    # 检查LLM连接
    try:
        # 简单测试LLM连接
        test_response = nlp_service.detect_intent("你好")
        if test_response and "intent" in test_response:
            services["llm"] = True
    except Exception as e:
        logger.error(f"LLM连接失败: {e}")
    
    status = "healthy" if all(services.values()) else "degraded"
    
    return HealthCheckResponse(
        status=status,
        version=settings.VERSION,
        timestamp=datetime.now(),
        services=services
    )

@app.post("/chat", response_model=AIResponse, tags=["对话"])
async def chat(message: UserMessage, background_tasks: BackgroundTasks = None):
    """处理用户消息"""
    try:
        # 获取或创建Agent
        agent = get_or_create_agent(message.session_id)
        
        # 记录用户消息到上下文
        user_message = {
            "role": "user",
            "content": message.message,
            "type": message.message_type,
            "timestamp": message.timestamp.isoformat() if message.timestamp else datetime.now().isoformat(),
            "metadata": message.metadata
        }
        redis_client.add_to_session_context(message.session_id, user_message)
        
        # 处理消息
        response_data = agent.process_message(
            message=message.message,
            message_type=message.message_type,
            user_id=message.user_id
        )
        
        # 生成响应
        response = AIResponse(
            session_id=message.session_id,
            response_id=f"resp_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            message=response_data.get("response", "抱歉，我暂时无法处理您的请求。"),
            intent=response_data.get("intent"),
            entities=response_data.get("entities", {}),
            confidence=response_data.get("confidence", 0.0),
            suggestions=response_data.get("suggestions", []),
            actions=response_data.get("actions", []),
            timestamp=datetime.now()
        )
        
        # 记录AI响应到上下文
        ai_message = {
            "role": "assistant",
            "content": response.message,
            "intent": response.intent.value if response.intent else None,
            "timestamp": response.timestamp.isoformat()
        }
        redis_client.add_to_session_context(message.session_id, ai_message)
        
        # 异步保存到数据库
        if background_tasks and message.user_id:
            background_tasks.add_task(save_conversation, message, response)
        
        return response
        
    except Exception as e:
        logger.error(f"处理聊天消息失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理消息失败: {str(e)}")

@app.post("/chat/text", response_model=AIResponse, tags=["对话"])
async def chat_text(
    session_id: str = Form(...),
    message: str = Form(...),
    user_id: Optional[str] = Form(None)
):
    """处理文本消息（表单格式）"""
    return await chat(UserMessage(
        session_id=session_id,
        user_id=user_id,
        message=message,
        message_type=MessageType.TEXT
    ))

@app.post("/chat/voice", response_model=AIResponse, tags=["对话"])
async def chat_voice(
    session_id: str = Form(...),
    audio_file: UploadFile = File(...),
    user_id: Optional[str] = Form(None)
):
    """处理语音消息"""
    try:
        # 保存音频文件
        audio_path = UPLOAD_DIR / f"voice_{session_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
        
        with open(audio_path, "wb") as buffer:
            content = await audio_file.read()
            buffer.write(content)
        
        # 语音转文本
        text = audio_processor.speech_to_text(str(audio_path))
        
        if not text:
            raise HTTPException(status_code=400, detail="语音识别失败")
        
        # 清理临时文件
        audio_path.unlink(missing_ok=True)
        
        # 处理文本消息
        return await chat(UserMessage(
            session_id=session_id,
            user_id=user_id,
            message=text,
            message_type=MessageType.VOICE
        ))
        
    except Exception as e:
        logger.error(f"处理语音消息失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理语音消息失败: {str(e)}")

@app.post("/chat/image", response_model=AIResponse, tags=["对话"])
async def chat_image(
    session_id: str = Form(...),
    image_file: UploadFile = File(...),
    user_id: Optional[str] = Form(None)
):
    """处理图片消息"""
    try:
        # 保存图片文件
        image_path = UPLOAD_DIR / f"image_{session_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        
        with open(image_path, "wb") as buffer:
            content = await image_file.read()
            buffer.write(content)
        
        # 图片转文本（OCR）
        text = file_processor.image_to_text(str(image_path))
        
        if not text:
            text = "这是一张图片，但我无法识别其中的文字内容。"
        
        # 清理临时文件
        image_path.unlink(missing_ok=True)
        
        # 处理文本消息
        return await chat(UserMessage(
            session_id=session_id,
            user_id=user_id,
            message=f"图片内容: {text}",
            message_type=MessageType.IMAGE
        ))
        
    except Exception as e:
        logger.error(f"处理图片消息失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理图片消息失败: {str(e)}")

@app.post("/travel/plan", response_model=TravelPlanResponse, tags=["旅行规划"])
async def create_travel_plan(request: TravelPlanRequest):
    """创建旅行计划"""
    try:
        # 生成旅行计划
        plan_data = {
            "destination": request.destination,
            "start_date": request.start_date.strftime("%Y-%m-%d"),
            "end_date": request.end_date.strftime("%Y-%m-%d"),
            "budget": request.budget,
            "travelers": request.travelers,
            "interests": request.interests,
            "preferences": request.preferences
        }
        
        result = travel_planning_service.generate_travel_plan(plan_data)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        plan = result["plan"]
        plan_id = travel_planning_service.save_travel_plan(request.user_id, plan)
        
        if not plan_id:
            raise HTTPException(status_code=500, detail="保存旅行计划失败")
        
        return TravelPlanResponse(
            plan_id=plan_id,
            user_id=request.user_id,
            destination=request.destination,
            start_date=request.start_date,
            end_date=request.end_date,
            budget=request.budget,
            travelers=request.travelers,
            itinerary=plan,
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"创建旅行计划失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建旅行计划失败: {str(e)}")

@app.get("/travel/plan/{plan_id}", response_model=TravelPlanResponse, tags=["旅行规划"])
async def get_travel_plan(plan_id: str, user_id: str):
    """获取旅行计划"""
    try:
        plan = travel_planning_service.get_travel_plan(user_id, plan_id)
        
        if not plan:
            raise HTTPException(status_code=404, detail="旅行计划不存在")
        
        metadata = plan.get("metadata", {})
        
        return TravelPlanResponse(
            plan_id=plan_id,
            user_id=user_id,
            destination=metadata.get("destination", ""),
            start_date=datetime.strptime(metadata.get("start_date", "2024-01-01"), "%Y-%m-%d").date(),
            end_date=datetime.strptime(metadata.get("end_date", "2024-01-01"), "%Y-%m-%d").date(),
            budget=metadata.get("budget"),
            travelers=metadata.get("travelers", 1),
            itinerary=plan,
            status="active",
            created_at=datetime.strptime(metadata.get("generated_at", datetime.now().isoformat()), "%Y-%m-%dT%H:%M:%S.%f"),
            updated_at=datetime.strptime(metadata.get("generated_at", datetime.now().isoformat()), "%Y-%m-%dT%H:%M:%S.%f")
        )
        
    except Exception as e:
        logger.error(f"获取旅行计划失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取旅行计划失败: {str(e)}")

@app.post("/flights/search", tags=["航班服务"])
async def search_flights_api(request: FlightSearchRequest):
    """搜索航班"""
    try:
        result = third_party_service.search_flights(
            departure=request.departure,
            arrival=request.arrival,
            date=request.departure_date.strftime("%Y-%m-%d"),
            passengers=request.passengers
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "搜索航班失败"))
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"搜索航班失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索航班失败: {str(e)}")

@app.post("/hotels/search", tags=["酒店服务"])
async def search_hotels_api(request: HotelSearchRequest):
    """搜索酒店"""
    try:
        result = third_party_service.search_hotels(
            location=request.location,
            check_in=request.check_in.strftime("%Y-%m-%d"),
            check_out=request.check_out.strftime("%Y-%m-%d"),
            guests=request.guests,
            rooms=request.rooms
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "搜索酒店失败"))
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"搜索酒店失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索酒店失败: {str(e)}")

@app.post("/weather", tags=["天气服务"])
async def get_weather_api(request: WeatherQueryRequest):
    """获取天气信息"""
    try:
        result = third_party_service.get_weather(
            city=request.location,
            date=request.query_date.strftime("%Y-%m-%d") if request.query_date else None
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "获取天气信息失败"))
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取天气信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取天气信息失败: {str(e)}")

@app.post("/knowledge/search", tags=["知识库"])
async def search_knowledge(request: KnowledgeSearchRequest):
    """搜索知识库"""
    try:
        results = knowledge_base_service.search(
            query=request.query,
            category=request.category,
            limit=request.limit
        )
        
        return {
            "success": True,
            "query": request.query,
            "results": results,
            "total": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"搜索知识库失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索知识库失败: {str(e)}")

@app.post("/knowledge/add", tags=["知识库"])
async def add_knowledge(request: KnowledgeAddRequest):
    """添加知识"""
    try:
        success = knowledge_base_service.add_knowledge(
            category=request.category,
            title=request.title,
            content=request.content,
            metadata=request.metadata,
            source=request.source
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="添加知识失败")
        
        return {
            "success": True,
            "message": "知识添加成功",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"添加知识失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加知识失败: {str(e)}")

@app.post("/user/create", tags=["用户管理"])
async def create_user(request: UserCreateRequest):
    """创建用户"""
    try:
        from database.mysql_client import User, SessionLocal
        
        db = SessionLocal()
        
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.user_id == request.user_id).first()
        if existing_user:
            db.close()
            raise HTTPException(status_code=400, detail="用户已存在")
        
        # 创建新用户
        user = User(
            user_id=request.user_id,
            username=request.username,
            email=request.email,
            phone=request.phone,
            preferences=request.preferences
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()
        
        return {
            "success": True,
            "message": "用户创建成功",
            "user_id": user.user_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建用户失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")

@app.get("/user/{user_id}/conversations", tags=["用户管理"])
async def get_user_conversations(user_id: str, limit: int = 20, offset: int = 0):
    """获取用户对话历史"""
    try:
        from database.mysql_client import Conversation, SessionLocal
        
        db = SessionLocal()
        
        conversations = db.query(Conversation)\
            .filter(Conversation.user_id == user_id)\
            .order_by(Conversation.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        db.close()
        
        result = []
        for conv in conversations:
            result.append({
                "id": conv.id,
                "session_id": conv.session_id,
                "query": conv.query,
                "response": conv.response,
                "intent": conv.intent,
                "confidence": conv.confidence,
                "created_at": conv.created_at.isoformat() if conv.created_at else None
            })
        
        return {
            "success": True,
            "user_id": user_id,
            "conversations": result,
            "total": len(result),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取对话历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取对话历史失败: {str(e)}")

@app.post("/payment/process", tags=["支付服务"])
async def process_payment(request: PaymentRequest):
    """处理支付"""
    try:
        result = third_party_service.make_payment(
            order_id=request.order_id,
            amount=request.amount,
            payment_method=request.payment_method
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "支付失败"))
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"处理支付失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理支付失败: {str(e)}")

@app.post("/currency/convert", tags=["工具服务"])
async def convert_currency(amount: float, from_currency: str, to_currency: str):
    """货币转换"""
    try:
        result = third_party_service.convert_currency(amount, from_currency, to_currency)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "货币转换失败"))
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"货币转换失败: {e}")
        raise HTTPException(status_code=500, detail=f"货币转换失败: {str(e)}")

@app.post("/route/calculate", tags=["工具服务"])
async def calculate_route_api(origin: str, destination: str, mode: str = "driving"):
    """计算路线"""
    try:
        result = third_party_service.get_transportation_info(origin, destination, mode)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "计算路线失败"))
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"计算路线失败: {e}")
        raise HTTPException(status_code=500, detail=f"计算路线失败: {str(e)}")

@app.post("/translate", tags=["工具服务"])
async def translate_text_api(text: str, target_language: str = "en"):
    """翻译文本"""
    try:
        translated = translate_text(text, target_language)
        
        return {
            "success": True,
            "original": text,
            "translated": translated,
            "target_language": target_language,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"翻译失败: {e}")
        raise HTTPException(status_code=500, detail=f"翻译失败: {str(e)}")

@app.get("/session/{session_id}/context", tags=["会话管理"])
async def get_session_context(session_id: str):
    """获取会话上下文"""
    try:
        context = redis_client.get_session_context(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "context": context,
            "count": len(context),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取会话上下文失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取会话上下文失败: {str(e)}")

@app.delete("/session/{session_id}", tags=["会话管理"])
async def clear_session_context(session_id: str):
    """清除会话上下文"""
    try:
        key = f"session:{session_id}:context"
        success = redis_client.delete(key)
        
        if success:
            return {
                "success": True,
                "message": "会话上下文已清除",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="清除会话上下文失败")
        
    except Exception as e:
        logger.error(f"清除会话上下文失败: {e}")
        raise HTTPException(status_code=500, detail=f"清除会话上下文失败: {str(e)}")

async def save_conversation(message: UserMessage, response: AIResponse):
    """保存对话记录到数据库"""
    try:
        from database.mysql_client import Conversation, SessionLocal
        
        db = SessionLocal()
        
        conversation = Conversation(
            user_id=message.user_id or "anonymous",
            session_id=message.session_id,
            query=message.message,
            response=response.message,
            intent=response.intent.value if response.intent else None,
            confidence=response.confidence or 0.0,
            meta_data={  # 修改这里
                "message_type": message.message_type.value,
                "user_metadata": message.metadata or {},
                "response_metadata": {
                    "suggestions": response.suggestions,
                    "actions": response.actions
                }
            }
        )
        
        db.add(conversation)
        db.commit()
        db.close()
        
        logger.info(f"已保存对话记录: {message.session_id}")
        
    except Exception as e:
        logger.error(f"保存对话记录失败: {e}")

# 异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            code=exc.status_code
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="服务器内部错误",
            detail=str(exc),
            code=500
        ).dict()
    )

# 启动时初始化
@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info(f"{settings.PROJECT_NAME} v{settings.VERSION} 正在启动...")
    
    # 初始化数据库
    try:
        from database.mysql_client import init_db
        init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
    
    # 测试LLM连接
    try:
        test_response = nlp_service.detect_intent("测试连接")
        logger.info(f"LLM连接测试成功: {test_response.get('intent')}")
    except Exception as e:
        logger.error(f"LLM连接测试失败: {e}")
    
    logger.info(f"{settings.PROJECT_NAME} 启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info(f"{settings.PROJECT_NAME} 正在关闭...")
    
    # 清理资源
    chat_agents.clear()
    
    logger.info(f"{settings.PROJECT_NAME} 已关闭")