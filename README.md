# 🌍 旅游AI客服系统

一个基于人工智能的旅游客服系统，集成航班查询、酒店预订、旅行规划、天气查询、知识库问答等多项功能，为用户提供全方位的旅游咨询服务。

---

## 🌟 核心特性

- 🗣️ **多模态输入支持** — 文本、语音、图片多种输入方式
- 🧠 **智能意图识别** — 自动识别用户查询意图（航班、酒店、景点等）
- 🗺️ **旅行规划** — AI自动生成个性化旅行计划
- 📚 **知识库问答** — 基于向量检索的专业旅游知识库
- 🔗 **第三方服务集成** — 航班、酒店、天气、汇率等实时查询
- 🌐 **完整的API接口** — RESTful API设计，支持快速集成
- 🏭 **生产就绪** — 健康检查、错误处理、日志记录、Docker部署

---

## 📋 系统架构

### 技术栈

| 类别 | 技术 |
|:-----|:-----|
| 后端框架 | FastAPI |
| AI框架 | LangChain |
| 大语言模型 | OpenAI GPT-4 / DeepSeek |
| 数据库 | MySQL + Redis |
| 向量存储 | FAISS |
| 前端框架 | Vue 3 + Element Plus |
| 部署 | Docker + Docker Compose |

### 模块架构

```
用户界面层 → 服务层 → 数据层
    ├── 文本/语音/图片输入
    ├── 意图识别
    ├── 知识检索
    ├── 旅行规划
    ├── 第三方服务集成
    └── 数据分析
```

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- MySQL 8.0+
- Redis 7.0+
- OpenAI API Key

### 1. 克隆项目

```bash
git clone https://github.com/Raeyi/travel-ai-assistant
cd travel-ai-assistant
```

### 2. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装系统依赖（Linux）
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim ffmpeg
```

### 3. 安装前端依赖

```bash
cd travel-ai-frontend
npm install
cd ..
```

### 4. 配置环境

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑.env文件，设置您的配置
vim .env
```

`.env` 文件配置示例：

```env
# OpenAI配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-1106-preview

# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=travel_ai

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 5. 初始化系统

```bash
# 一站式初始化（推荐）
python main.py all

# 或分步初始化
python main.py init        # 初始化应用
python main.py migrate     # 数据库迁移
python main.py sample-data # 创建示例数据
```

### 6. 启动服务

```bash
# 启动后端（开发模式，热重载）
python main.py run --reload

# 启动前端
cd travel-ai-frontend
npm run dev
```

后端运行在 http://localhost:8000，前端运行在 http://localhost:3000

### 7. 访问API文档

启动后访问以下地址：

| 文档 | 地址 |
|:-----|:-----|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| 健康检查 | http://127.0.0.1:8000/health |

### 前端页面

| 页面 | 路径 | 说明 |
|:-----|:-----|:-----|
| 首页 | `/` | 功能展示与使用指南 |
| AI聊天 | `/chat` | 智能对话助手 |
| 旅行规划 | `/travel-plan` | AI生成个性化旅行计划 |
| 航班查询 | `/flights` | 实时航班搜索 |
| 酒店预订 | `/hotels` | 酒店搜索与预订 |
| 天气查询 | `/weather` | 目的地天气信息 |
| 知识库 | `/knowledge` | 旅游知识检索 |
| 关于 | `/about` | 关于我们 |

---

## 📦 Docker部署

### 前置准备

确保已创建 `.env` 文件并配置好必要的环境变量：

```bash
cp .env.example .env
# 编辑 .env，设置 OPENAI_API_KEY 等配置
```

### 服务架构

Docker Compose 启动以下 4 个服务：

|| 服务 | 端口 | 说明 |
||:-----|:-----|:-----|
|| mysql | 3306 | MySQL 8.0 数据库 |
|| redis | 6379 | Redis 7 缓存 |
|| app | 8000 | FastAPI 后端 |
|| frontend | 3000 | Vue 3 前端（Nginx 托管） |

### 使用 Docker Compose（推荐）

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 查看某个服务日志
docker-compose logs -f app

# 停止服务
docker-compose down

# 停止并清理数据卷
docker-compose down -v
```

启动后访问：
- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 仅构建后端镜像

```bash
# 构建镜像
docker build -t travel-ai-assistant .

# 运行容器（需自行配置数据库和Redis）
docker run -p 8000:8000 --env-file .env travel-ai-assistant
```

### 注意事项

- `.dockerignore` 已排除 `travel_env/`、`node_modules/`、`.git/` 等不必要的文件
- 前端通过 Nginx 托管，API 请求自动代理到后端（`/api/*` → `app:8000/*`）
- 数据库和 Redis 数据使用 Docker Volume 持久化

---

## 📡 API接口文档

### 主要接口

#### 1. 对话接口

```http
POST /chat
Content-Type: application/json

{
    "session_id": "unique_session_id",
    "user_id": "optional_user_id",
    "message": "我想去北京旅游",
    "message_type": "text"
}
```

#### 2. 创建旅行计划

```http
POST /travel/plan
Content-Type: application/json

{
    "user_id": "user_001",
    "destination": "北京",
    "start_date": "2024-05-01",
    "end_date": "2024-05-05",
    "budget": 5000,
    "travelers": 2,
    "interests": ["历史", "美食", "购物"]
}
```

#### 3. 搜索航班

```http
POST /flights/search
Content-Type: application/json

{
    "departure": "上海",
    "arrival": "北京",
    "date": "2024-05-01",
    "passengers": 2
}
```

#### 4. 搜索酒店

```http
POST /hotels/search
Content-Type: application/json

{
    "location": "北京",
    "check_in": "2024-05-01",
    "check_out": "2024-05-05",
    "guests": 2,
    "rooms": 1
}
```

### 完整的API接口列表

| 方法 | 路径 | 描述 |
|:-----|:-----|:-----|
| POST | `/chat` | 智能对话（支持多种消息类型） |
| POST | `/chat/text` | 文本对话 |
| POST | `/chat/voice` | 语音对话 |
| POST | `/chat/image` | 图片对话 |
| POST | `/travel/plan` | 创建旅行计划 |
| GET | `/travel/plan/{plan_id}` | 获取旅行计划 |
| POST | `/flights/search` | 搜索航班 |
| POST | `/hotels/search` | 搜索酒店 |
| POST | `/weather` | 查询天气 |
| POST | `/knowledge/search` | 搜索知识库 |
| POST | `/knowledge/add` | 添加知识 |
| POST | `/currency/convert` | 货币转换 |
| POST | `/translate` | 翻译文本 |
| POST | `/payment/process` | 处理支付 |
| GET | `/health` | 健康检查 |

---

## 🎯 使用示例

### Python客户端示例

```python
import requests
import json

BASE_URL = "http://localhost:8000"

class TravelAIClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session_id = "user_session_001"
    
    def ask_question(self, question):
        """发送问题并获取回答"""
        response = requests.post(
            f"{self.base_url}/chat/text",
            data={
                "session_id": self.session_id,
                "message": question
            }
        )
        return response.json()
    
    def create_travel_plan(self, destination, start_date, end_date, budget=5000):
        """创建旅行计划"""
        data = {
            "user_id": "user_001",
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "budget": budget,
            "travelers": 2,
            "interests": ["美食", "景点", "购物"]
        }
        response = requests.post(
            f"{self.base_url}/travel/plan",
            json=data
        )
        return response.json()

# 使用示例
client = TravelAIClient()

# 对话
response = client.ask_question("我想去北京旅游，有什么推荐吗？")
print(f"AI回复: {response['message']}")

# 创建旅行计划
plan = client.create_travel_plan("北京", "2024-05-01", "2024-05-05")
print(f"旅行计划ID: {plan['plan_id']}")
```

### cURL示例

```bash
# 1. 对话
curl -X POST "http://localhost:8000/chat/text" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "session_id=test_001&message=北京的天气怎么样？"

# 2. 语音对话
curl -X POST "http://localhost:8000/chat/voice" \
  -F "session_id=test_001" \
  -F "audio_file=@audio.wav"

# 3. 搜索航班
curl -X POST "http://localhost:8000/flights/search" \
  -H "Content-Type: application/json" \
  -d '{
    "departure": "上海",
    "arrival": "北京",
    "date": "2024-05-01",
    "passengers": 2
  }'
```

---

## 📁 项目结构

```
travel-ai-assistant/
├── api/                          # API接口层
│   ├── endpoints.py              # 所有API端点
│   └── schemas.py                # Pydantic数据模型
├── config/                       # 配置管理
│   ├── settings.py               # 应用配置
│   └── llm_config.py             # LLM配置
├── core/                         # 核心业务逻辑
│   ├── agent.py                  # AI Agent核心
│   └── tools.py                  # 工具函数定义
├── services/                     # 业务服务
│   ├── nlp_service.py            # NLP服务
│   ├── travel_planning.py        # 旅行规划服务
│   ├── knowledge_base.py         # 知识库服务
│   └── third_party.py            # 第三方服务集成
├── database/                     # 数据访问层
│   ├── mysql_client.py           # MySQL客户端
│   └── redis_client.py           # Redis客户端
├── models/                       # 数据模型
│   ├── user_models.py            # 用户模型
│   └── travel_models.py          # 旅行数据模型
├── utils/                        # 工具函数
│   ├── audio_processor.py        # 音频处理
│   ├── file_processor.py         # 文件处理
│   └── __init__.py               # 工具函数集合
├── travel-ai-frontend/           # 前端项目
│   ├── src/                      # 前端源代码
│   │   ├── api/                  # API请求封装
│   │   ├── assets/               # 静态资源
│   │   ├── components/           # 公共组件
│   │   ├── router/               # 路由配置
│   │   ├── stores/               # Pinia状态管理
│   │   └── views/                # 页面视图
│   ├── Dockerfile                # 前端Docker镜像配置
│   ├── nginx.conf                # Nginx配置
│   ├── package.json              # 前端依赖配置
│   └── vite.config.ts            # Vite构建配置
├── uploads/                      # 文件上传目录
├── data/                         # 数据目录
├── Dockerfile                    # 后端Docker镜像配置
├── docker-compose.yml            # Docker Compose配置
├── .dockerignore                 # Docker构建排除文件
├── requirements.txt              # Python依赖
├── .env.example                  # 环境变量示例
├── main.py                       # 应用入口点
└── README.md                     # 项目文档
```

---

## 🔧 配置说明

### 环境变量

| 变量名 | 必填 | 默认值 | 说明 |
|:-------|:-----|:-------|:-----|
| `OPENAI_API_KEY` | ✅ | - | OpenAI API密钥 |
| `OPENAI_MODEL` | ❌ | gpt-4-1106-preview | OpenAI模型名称 |
| `MYSQL_HOST` | ❌ | localhost | MySQL主机地址 |
| `MYSQL_PORT` | ❌ | 3306 | MySQL端口 |
| `MYSQL_DATABASE` | ❌ | travel_ai | 数据库名 |
| `REDIS_HOST` | ❌ | localhost | Redis主机地址 |
| `REDIS_PORT` | ❌ | 6379 | Redis端口 |

### 数据库配置

系统会自动创建以下表：

- `users` — 用户信息
- `conversations` — 对话记录
- `travel_plans` — 旅行计划
- `knowledge_base` — 知识库
- `faq` — 常见问题

---

## 🛠️ 开发指南

### 添加新的工具

1. 在 `core/tools.py` 中添加新工具函数：

```python
@tool
def search_restaurants(location: str, cuisine: str = None) -> str:
    """搜索餐厅"""
    # 实现搜索逻辑
    return f"在{location}找到{cuisine}餐厅"
```

2. 在 `core/agent.py` 中将工具添加到工具列表。

### 添加新的第三方服务

1. 在 `services/third_party.py` 中添加新的服务类：

```python
def search_events(location: str, date: str = None) -> dict:
    """搜索活动/事件"""
    # 实现活动搜索逻辑
    return {
        "success": True,
        "events": [...]
    }
```

2. 在 `core/tools.py` 中创建对应的工具函数。

### 自定义意图识别

修改 `services/nlp_service.py` 中的 `detect_intent` 方法来支持新的意图。

---

## 📊 监控与日志

### 日志文件

- 应用日志：`app.log`
- 访问日志：控制台输出

### 健康检查

```bash
curl http://localhost:8000/health
```

响应示例：

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00",
  "services": {
    "api": true,
    "database": true,
    "redis": true,
    "llm": true
  }
}
```

---

## 🧪 测试

### 运行测试

```bash
# 运行服务测试
python main.py test

# 测试特定功能
python -m pytest tests/ -v
```

### 测试用例示例

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from api.endpoints import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["healthy", "degraded"]
```

---

## 🤝 贡献指南

欢迎贡献代码！请按照以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### 开发规范

- 遵循 PEP 8 代码规范
- 为新增功能编写测试用例
- 更新相关文档
- 确保代码通过所有测试

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 📞 支持与联系

- 🐛 问题反馈：[GitHub Issues](https://github.com/Raeyi/travel-ai-assistant/issues)
- 💡 功能请求：[GitHub Discussions](https://github.com/Raeyi/travel-ai-assistant/discussions)
- 📧 邮件联系：<surrayi@163.com>

---

## ✨ 致谢

感谢以下开源项目的贡献：

| 项目 | 说明 |
|:-----|:-----|
| [FastAPI](https://fastapi.tiangolo.com/) | 现代、快速的Web框架 |
| [LangChain](https://langchain.com/) | LLM应用开发框架 |
| [OpenAI](https://openai.com/) | GPT模型提供商 |
| [FAISS](https://github.com/facebookresearch/faiss) | 向量相似性搜索库 |
