from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from config.settings import settings
import redis
import json
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True)
    username = Column(String(100))
    email = Column(String(200))
    phone = Column(String(50))
    preferences = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关系
    conversations = relationship("Conversation", back_populates="user")
    travel_plans = relationship("TravelPlan", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("users.user_id"))
    session_id = Column(String(100), index=True)
    query = Column(Text)
    response = Column(Text)
    intent = Column(String(100))
    confidence = Column(Float)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    
    # 关系
    user = relationship("User", back_populates="conversations")

class TravelPlan(Base):
    __tablename__ = "travel_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey("users.user_id"))
    plan_id = Column(String(100), unique=True, index=True)
    destination = Column(String(200))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget = Column(Float)
    travelers = Column(Integer)
    interests = Column(JSON, default=[])
    itinerary = Column(JSON, default={})
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="travel_plans")

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), index=True)
    title = Column(String(200))
    content = Column(Text)
    metadata = Column(JSON, default={})
    source = Column(String(200))
    embedding = Column(Text)  # 存储向量嵌入
    created_at = Column(DateTime, default=func.now())

# 创建数据库引擎
def get_db_engine():
    connection_string = (
        f"mysql+mysqlconnector://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
        f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
    )
    return create_engine(connection_string, pool_pre_ping=True, pool_recycle=3600)

engine = get_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()