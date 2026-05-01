import sqlite3
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path
import os
from difflib import SequenceMatcher
import re

logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    """知识库服务 - 简化版，不使用向量数据库"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 使用项目根目录下的data目录
            self.db_path = Path(__file__).parent.parent / "data" / "knowledge.db"
        else:
            self.db_path = Path(db_path)
        
        # 确保目录存在
        os.makedirs(self.db_path.parent, exist_ok=True)
        
        logger.info(f"知识库数据库路径: {self.db_path}")
        self.init_database()
    
    def init_database(self):
        """初始化知识库数据库"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # 创建知识表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    meta_data TEXT,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON knowledge(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON knowledge(title)')
            
            # 创建FAQ表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS faq (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    category TEXT,
                    tags TEXT,
                    use_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建示例数据
            self._create_sample_data(cursor)
            
            conn.commit()
            conn.close()
            logger.info("知识库数据库初始化完成")
            
        except Exception as e:
            logger.error(f"知识库数据库初始化失败: {e}")
            raise
    
    def _create_sample_data(self, cursor):
        """创建示例数据"""
        # 检查是否已有数据
        cursor.execute("SELECT COUNT(*) FROM knowledge")
        count = cursor.fetchone()[0]
        
        if count == 0:
            sample_data = [
                {
                    "category": "destination",
                    "title": "北京旅游指南",
                    "content": "北京是中国的首都，拥有丰富的历史文化遗产。主要景点包括故宫、天安门、长城、颐和园等。最佳旅游季节是春季和秋季。",
                    "meta_data": '{"tags": ["历史", "文化", "古都"], "best_season": ["春季", "秋季"]}',
                    "source": "官方旅游指南"
                },
                {
                    "category": "destination",
                    "title": "上海旅游指南",
                    "content": "上海是中国的经济中心，现代化大都市。主要景点包括外滩、东方明珠、南京路、迪士尼乐园等。适合购物和美食体验。",
                    "meta_data": '{"tags": ["现代", "购物", "美食"], "best_season": ["全年"]}',
                    "source": "官方旅游指南"
                },
                {
                    "category": "attraction",
                    "title": "故宫博物院",
                    "content": "故宫是中国明清两代的皇家宫殿，位于北京中轴线的中心。开放时间：8:30-17:00，门票：60元。建议游览时间：3-4小时。",
                    "meta_data": '{"location": "北京", "ticket_price": 60, "open_hours": "8:30-17:00"}',
                    "source": "故宫官网"
                },
                {
                    "category": "attraction",
                    "title": "长城",
                    "content": "长城是世界文化遗产，中国的象征之一。八达岭长城是最著名的段落。开放时间：7:00-18:00，门票：40元。最佳游览季节：春秋季。",
                    "meta_data": '{"location": "北京", "ticket_price": 40, "open_hours": "7:00-18:00"}',
                    "source": "长城官网"
                },
                {
                    "category": "food",
                    "title": "北京烤鸭",
                    "content": "北京烤鸭是北京著名菜式，以色泽红艳，肉质细嫩，味道醇厚，肥而不腻的特色而闻名。推荐餐厅：全聚德、便宜坊。",
                    "meta_data": '{"city": "北京", "price_range": "中等", "cuisine": "北京菜"}',
                    "source": "美食指南"
                },
                {
                    "category": "transportation",
                    "title": "北京地铁",
                    "content": "北京地铁系统发达，覆盖全市主要区域。运营时间：5:00-23:00。票价：3-9元。推荐使用亿通行APP扫码乘车。",
                    "meta_data": '{"city": "北京", "operating_hours": "5:00-23:00", "price_range": "3-9"}',
                    "source": "北京地铁官网"
                },
                {
                    "category": "emergency",
                    "title": "紧急联系电话",
                    "content": "警察：110，火警：119，急救：120。旅游投诉：12301。外交部全球领事保护与服务应急呼叫中心：+86-10-12308。",
                    "meta_data": '{"type": "emergency", "country": "中国"}',
                    "source": "政府官网"
                }
            ]
            
            for data in sample_data:
                cursor.execute('''
                    INSERT INTO knowledge (category, title, content, meta_data, source)
                    VALUES (?, ?, ?, ?, ?)
                ''', (data["category"], data["title"], data["content"], 
                      data["meta_data"], data["source"]))
            
            # 添加示例FAQ
            sample_faqs = [
                {
                    "question": "如何预订酒店？",
                    "answer": "您可以通过以下方式预订酒店：1) 在网站或APP上搜索目的地和日期 2) 选择心仪的酒店和房型 3) 填写入住人信息 4) 完成支付。也可以直接联系客服协助预订。",
                    "category": "hotel",
                    "tags": "预订,酒店,流程"
                },
                {
                    "question": "航班取消怎么办？",
                    "answer": "如果航班取消，您可以：1) 联系航空公司改签或退票 2) 查看是否有其他可选的航班 3) 如果购买了旅行保险，联系保险公司理赔。我们也可以协助您处理相关事宜。",
                    "category": "flight",
                    "tags": "航班,取消,处理"
                },
                {
                    "question": "如何办理签证？",
                    "answer": "签证办理流程：1) 准备所需材料（护照、照片、申请表等） 2) 预约签证中心 3) 递交材料并缴费 4) 等待审批。不同国家要求不同，建议提前咨询相关使领馆。",
                    "category": "visa",
                    "tags": "签证,办理,流程"
                }
            ]
            
            for faq in sample_faqs:
                cursor.execute('''
                    INSERT INTO faq (question, answer, category, tags)
                    VALUES (?, ?, ?, ?)
                ''', (faq["question"], faq["answer"], faq["category"], faq["tags"]))
            
            logger.info(f"已添加 {len(sample_data)} 条示例数据和 {len(sample_faqs)} 条FAQ")
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def search(self, query: str, category: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        """搜索知识库 - 基于关键词和相似度"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            results = []
            
            # 关键词搜索
            if category:
                cursor.execute('''
                    SELECT id, category, title, content, meta_data, source
                    FROM knowledge
                    WHERE category = ? AND (title LIKE ? OR content LIKE ?)
                ''', (category, f"%{query}%", f"%{query}%"))
            else:
                cursor.execute('''
                    SELECT id, category, title, content, meta_data, source
                    FROM knowledge
                    WHERE title LIKE ? OR content LIKE ?
                ''', (f"%{query}%", f"%{query}%"))
            
            rows = cursor.fetchall()
            
            # 计算相似度并排序
            scored_results = []
            for row in rows:
                content = f"{row['title']} {row['content']}"
                similarity = self._calculate_similarity(query, content)
                
                scored_results.append({
                    "title": row["title"],
                    "content": row["content"],
                    "meta_data": row["meta_data"],
                    "score": similarity,
                    "source": row["source"],
                    "category": row["category"]
                })
            
            # 按相似度排序
            scored_results.sort(key=lambda x: x["score"], reverse=True)
            
            # 取前limit个结果
            results = scored_results[:limit]
            
            # 如果结果不足，使用模糊匹配
            if len(results) < limit:
                cursor.execute('SELECT id, category, title, content, meta_data, source FROM knowledge')
                all_rows = cursor.fetchall()
                
                all_scored = []
                for row in all_rows:
                    content = f"{row['title']} {row['content']}"
                    similarity = self._calculate_similarity(query, content)
                    
                    all_scored.append({
                        "title": row["title"],
                        "content": row["content"],
                        "meta_data": row["meta_data"],
                        "score": similarity * 0.8,  # 模糊匹配分数打折扣
                        "source": row["source"],
                        "category": row["category"]
                    })
                
                # 合并结果，去重
                existing_titles = {r["title"] for r in results}
                for item in all_scored:
                    if item["title"] not in existing_titles and item["score"] > 0.3:
                        results.append(item)
                        existing_titles.add(item["title"])
                    
                    if len(results) >= limit:
                        break
            
            conn.close()
            
            # 重新按分数排序
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"知识库搜索失败: {e}")
            return []
    
    def add_knowledge(self, category: str, title: str, content: str, 
                     meta_data: Dict = None, source: str = "user"):
        """添加知识"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            meta_data_str = json.dumps(meta_data, ensure_ascii=False) if meta_data else "{}"
            
            cursor.execute('''
                INSERT INTO knowledge (category, title, content, meta_data, source)
                VALUES (?, ?, ?, ?, ?)
            ''', (category, title, content, meta_data_str, source))
            
            conn.commit()
            conn.close()
            
            logger.info(f"已添加知识: {title}")
            return True
            
        except Exception as e:
            logger.error(f"添加知识失败: {e}")
            return False
    
    def search_faq(self, question: str, limit: int = 3) -> List[Dict[str, Any]]:
        """搜索FAQ"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 先尝试精确匹配
            cursor.execute('''
                SELECT id, question, answer, category, tags, use_count
                FROM faq
                WHERE question LIKE ? OR answer LIKE ?
            ''', (f"%{question}%", f"%{question}%"))
            
            rows = cursor.fetchall()
            
            # 计算相似度
            scored_faqs = []
            for row in rows:
                similarity = self._calculate_similarity(question, row["question"])
                scored_faqs.append({
                    "id": row["id"],
                    "question": row["question"],
                    "answer": row["answer"],
                    "category": row["category"],
                    "tags": row["tags"].split(",") if row["tags"] else [],
                    "use_count": row["use_count"],
                    "score": similarity
                })
            
            # 如果精确匹配不足，进行模糊匹配
            if len(scored_faqs) < limit:
                cursor.execute('SELECT id, question, answer, category, tags, use_count FROM faq')
                all_rows = cursor.fetchall()
                
                for row in all_rows:
                    # 跳过已添加的
                    if any(f["id"] == row["id"] for f in scored_faqs):
                        continue
                    
                    similarity = self._calculate_similarity(question, row["question"])
                    if similarity > 0.3:  # 相似度阈值
                        scored_faqs.append({
                            "id": row["id"],
                            "question": row["question"],
                            "answer": row["answer"],
                            "category": row["category"],
                            "tags": row["tags"].split(",") if row["tags"] else [],
                            "use_count": row["use_count"],
                            "score": similarity * 0.7  # 模糊匹配分数打折扣
                        })
                    
                    if len(scored_faqs) >= limit:
                        break
            
            conn.close()
            
            # 按分数排序
            scored_faqs.sort(key=lambda x: x["score"], reverse=True)
            
            return scored_faqs[:limit]
            
        except Exception as e:
            logger.error(f"FAQ搜索失败: {e}")
            return []
    
    def add_faq(self, question: str, answer: str, 
               category: str = None, tags: List[str] = None):
        """添加FAQ"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            tags_str = ",".join(tags) if tags else ""
            
            cursor.execute('''
                INSERT INTO faq (question, answer, category, tags)
                VALUES (?, ?, ?, ?)
            ''', (question, answer, category, tags_str))
            
            conn.commit()
            conn.close()
            
            logger.info(f"已添加FAQ: {question}")
            return True
            
        except Exception as e:
            logger.error(f"添加FAQ失败: {e}")
            return False
    
    def increment_faq_use(self, faq_id: int):
        """增加FAQ使用计数"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE faq SET use_count = use_count + 1 WHERE id = ?
            ''', (faq_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"更新FAQ使用计数失败: {e}")

# 全局知识库服务实例
knowledge_base_service = KnowledgeBaseService()