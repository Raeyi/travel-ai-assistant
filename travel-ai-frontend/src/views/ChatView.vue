<template>
  <div class="chat-view">
    <!-- 头部 -->
    <div class="chat-header">
      <div class="header-content">
        <h1>
          <el-icon><ChatLineRound /></el-icon>
          AI旅游助手
        </h1>
        <div class="header-actions">
          <el-tooltip content="清空对话历史" placement="bottom">
            <el-button @click="clearChat" :disabled="chatStore.isLoading">
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
          </el-tooltip>
          <el-tooltip content="新建会话" placement="bottom">
            <el-button @click="newSession" :disabled="chatStore.isLoading">
              <el-icon><Refresh /></el-icon>
              新建
            </el-button>
          </el-tooltip>
          <el-tooltip content="返回首页" placement="bottom">
            <el-button @click="goHome">
              <el-icon><HomeFilled /></el-icon>
              首页
            </el-button>
          </el-tooltip>
        </div>
      </div>
    </div>
    
    <!-- 聊天主体 -->
    <div class="chat-main">
      <!-- 侧边栏 - 意图和建议 -->
      <div class="chat-sidebar" v-if="chatStore.currentIntent || chatStore.suggestions.length > 0">
        <div class="intent-info" v-if="chatStore.currentIntent">
          <h3><el-icon><Finished /></el-icon> 当前意图</h3>
          <el-tag type="primary" size="large" class="intent-tag">
            {{ getIntentName(chatStore.currentIntent) }}
          </el-tag>
          <p class="confidence">置信度: {{ (chatStore.confidence * 100).toFixed(1) }}%</p>
        </div>
        
        <div class="suggestions" v-if="chatStore.suggestions.length > 0">
          <h3><el-icon><Lightning /></el-icon> 快速建议</h3>
          <div class="suggestion-buttons">
            <el-button
              v-for="(suggestion, index) in chatStore.suggestions"
              :key="index"
              @click="sendSuggestion(suggestion)"
              class="suggestion-btn"
            >
              {{ suggestion }}
            </el-button>
          </div>
        </div>
        
        <div class="entities" v-if="Object.keys(chatStore.entities).length > 0">
          <h3><el-icon><Collection /></el-icon> 提取信息</h3>
          <div class="entity-list">
            <div v-for="(value, key) in chatStore.entities" :key="key" class="entity-item">
              <span class="entity-key">{{ key }}:</span>
              <span class="entity-value">{{ value }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 聊天内容区 -->
      <div class="chat-content">
        <!-- 欢迎消息 -->
        <div v-if="!chatStore.hasMessages" class="welcome-message">
          <div class="welcome-content">
            <h2>👋 您好！我是您的旅游助手</h2>
            <p>我可以帮助您规划旅行、查询信息、预订服务等</p>
            <div class="quick-questions">
              <h3>试试问我：</h3>
              <div class="question-buttons">
                <el-button
                  v-for="(question, index) in quickQuestions"
                  :key="index"
                  @click="sendQuickQuestion(question)"
                  class="question-btn"
                >
                  {{ question }}
                </el-button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 消息列表 -->
        <div v-else class="messages-container" ref="messagesContainer">
          <div
            v-for="(message, index) in chatStore.messages"
            :key="index"
            :class="['message-item', message.role === 'user' ? 'user-message' : 'assistant-message']"
          >
            <div class="message-avatar">
              <el-avatar
                v-if="message.role === 'user'"
                :style="{ backgroundColor: '#409EFF' }"
              >
                <el-icon><User /></el-icon>
              </el-avatar>
              <el-avatar
                v-else
                :style="{ backgroundColor: '#67C23A' }"
              >
                <el-icon><Cpu /></el-icon>
              </el-avatar>
            </div>
            
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(message.content)"></div>
              
              <!-- AI消息的额外信息 -->
              <div v-if="message.role === 'assistant' && message.intent" class="message-meta">
                <el-tag size="small" type="info">
                  {{ getIntentName(message.intent) }}
                </el-tag>
                <span class="message-time">
                  {{ formatTime(message.timestamp) }}
                </span>
              </div>
            </div>
          </div>
          
          <!-- 加载指示器 -->
          <div v-if="chatStore.isLoading" class="typing-indicator">
            <div class="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span class="typing-text">AI正在思考...</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div class="chat-input-area">
      <div class="input-container">
        <div class="input-actions">
          <el-tooltip content="语音输入" placement="top">
            <el-button circle @click="toggleVoiceInput" :type="isRecording ? 'danger' : ''">
              <el-icon><Microphone /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="发送图片" placement="top">
            <el-button circle>
              <el-icon><Picture /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="表情" placement="top">
            <el-button circle>
              <el-icon><ChatDotSquare /></el-icon>
            </el-button>
          </el-tooltip>
        </div>
        
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="输入您的问题，例如：我想去北京旅游有什么推荐？"
          :maxlength="1000"
          show-word-limit
          @keydown.enter.exact.prevent="handleSendMessage"
          resize="none"
        />
        
        <div class="send-button">
          <el-button
            type="primary"
            @click="handleSendMessage"
            :loading="chatStore.isLoading"
            :disabled="!inputMessage.trim()"
          >
            <template #icon>
              <el-icon><Position /></el-icon>
            </template>
            发送
          </el-button>
        </div>
      </div>
      
      <!-- 语音输入提示 -->
      <div v-if="isRecording" class="voice-recording">
        <div class="voice-animation">
          <div class="voice-wave"></div>
          <div class="voice-wave"></div>
          <div class="voice-wave"></div>
        </div>
        <p>正在录音... 点击停止</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { 
  ChatLineRound, 
  Delete, 
  Refresh, 
  HomeFilled,
  Finished,
  Lightning,
  Collection,
  User,
  Cpu,
  Microphone,
  Picture,
  ChatDotSquare,
  Position
} from '@element-plus/icons-vue'

const router = useRouter()
const chatStore = useChatStore()
const messagesContainer = ref(null)
const inputMessage = ref('')
const isRecording = ref(false)

// 快速问题示例
const quickQuestions = ref([
  '北京有什么好玩的？',
  '帮我查一下明天北京到上海的航班',
  '推荐几个北京的美食',
  '北京三天两晚旅行计划',
  '故宫的门票多少钱？',
  '北京现在的天气怎么样？'
])

// 意图名称映射
const intentNames = {
  'flight_search': '航班查询',
  'hotel_search': '酒店搜索',
  'attraction_search': '景点搜索',
  'travel_plan': '旅行规划',
  'weather_query': '天气查询',
  'general_qa': '一般问答',
  'food_recommendation': '美食推荐',
  'currency_exchange': '货币兑换',
  'translation': '翻译服务'
}

// 初始化
onMounted(async () => {
  await chatStore.loadChatHistory()
  scrollToBottom()
})

// 监听消息变化
watch(() => chatStore.messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

// 发送消息
const handleSendMessage = async () => {
  if (!inputMessage.value.trim() || chatStore.isLoading) return
  
  const message = inputMessage.value.trim()
  inputMessage.value = ''
  
  try {
    await chatStore.sendMessage(message)
  } catch (error) {
    console.error('发送消息失败:', error)
  }
}

// 发送快速问题
const sendQuickQuestion = async (question) => {
  inputMessage.value = question
  await handleSendMessage()
}

// 发送建议
const sendSuggestion = async (suggestion) => {
  await chatStore.sendSuggestion(suggestion)
}

// 清空聊天
const clearChat = async () => {
  await chatStore.clearChat()
}

// 新建会话
const newSession = () => {
  localStorage.removeItem('travel_session_id')
  chatStore.sessionId = ''
  clearChat()
}

// 返回首页
const goHome = () => {
  router.push('/')
}

// 切换语音输入
const toggleVoiceInput = () => {
  isRecording.value = !isRecording.value
  if (isRecording.value) {
    // 这里可以添加语音识别逻辑
    setTimeout(() => {
      isRecording.value = false
      inputMessage.value = '这是模拟的语音输入内容'
    }, 2000)
  }
}

// 获取意图名称
const getIntentName = (intent) => {
  return intentNames[intent] || intent
}

// 格式化消息内容
const formatMessage = (text) => {
  if (!text) return ''
  return text
    .replace(/\n/g, '<br>')
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>

<style lang="scss" scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f7fa;
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  
  .header-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h1 {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 1.5rem;
      margin: 0;
    }
    
    .header-actions {
      display: flex;
      gap: 0.5rem;
      
      .el-button {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        
        &:hover {
          background: rgba(255, 255, 255, 0.2);
        }
      }
    }
  }
}

.chat-main {
  flex: 1;
  display: flex;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  padding: 1rem;
  gap: 1rem;
  overflow: hidden;
}

.chat-sidebar {
  width: 300px;
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 2rem;
  overflow-y: auto;
  flex-shrink: 0;
  
  h3 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1rem;
    color: #303133;
    margin-bottom: 1rem;
    
    svg {
      color: #409EFF;
    }
  }
  
  .intent-info {
    .intent-tag {
      font-size: 1rem;
      padding: 0.5rem 1rem;
      border-radius: 20px;
    }
    
    .confidence {
      margin-top: 0.5rem;
      font-size: 0.875rem;
      color: #909399;
    }
  }
  
  .suggestions {
    .suggestion-buttons {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      
      .suggestion-btn {
        text-align: left;
        justify-content: flex-start;
        white-space: normal;
        height: auto;
        min-height: 40px;
        padding: 0.5rem 1rem;
        border: 1px solid #e4e7ed;
        
        &:hover {
          border-color: #409EFF;
          color: #409EFF;
        }
      }
    }
  }
  
  .entities {
    .entity-list {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      
      .entity-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem;
        background: #f5f7fa;
        border-radius: 4px;
        
        .entity-key {
          font-weight: 500;
          color: #303133;
        }
        
        .entity-value {
          color: #409EFF;
          font-weight: 500;
        }
      }
    }
  }
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.welcome-message {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  
  .welcome-content {
    text-align: center;
    max-width: 600px;
    
    h2 {
      font-size: 2rem;
      margin-bottom: 1rem;
      color: #303133;
    }
    
    p {
      font-size: 1.125rem;
      color: #606266;
      margin-bottom: 2rem;
    }
    
    .quick-questions {
      h3 {
        font-size: 1rem;
        color: #909399;
        margin-bottom: 1rem;
      }
      
      .question-buttons {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        
        .question-btn {
          height: auto;
          min-height: 60px;
          white-space: normal;
          text-align: left;
          justify-content: flex-start;
          padding: 1rem;
          border: 1px solid #e4e7ed;
          
          &:hover {
            border-color: #409EFF;
            color: #409EFF;
          }
        }
      }
    }
  }
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message-item {
  display: flex;
  gap: 1rem;
  animation: fadeIn 0.3s ease;
  
  &.user-message {
    flex-direction: row-reverse;
    
    .message-content {
      align-items: flex-end;
      
      .message-text {
        background: #409EFF;
        color: white;
        border-radius: 18px 18px 4px 18px;
      }
    }
  }
  
  &.assistant-message {
    .message-text {
      background: #f5f7fa;
      color: #303133;
      border-radius: 18px 18px 18px 4px;
    }
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.message-text {
  padding: 1rem 1.5rem;
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
  
  :deep(pre) {
    background: #2d2d2d;
    color: #f8f8f2;
    padding: 1rem;
    border-radius: 6px;
    overflow-x: auto;
    margin: 0.5rem 0;
    
    code {
      background: none;
      padding: 0;
    }
  }
  
  :deep(code) {
    background: #f0f0f0;
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
    font-family: 'Consolas', 'Monaco', monospace;
  }
  
  :deep(strong) {
    font-weight: bold;
  }
  
  :deep(em) {
    font-style: italic;
  }
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  .message-time {
    font-size: 0.75rem;
    color: #909399;
  }
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: #f5f7fa;
  border-radius: 18px 18px 18px 4px;
  width: fit-content;
  animation: pulse 1.5s infinite;
  
  .typing-dots {
    display: flex;
    gap: 0.25rem;
    
    span {
      width: 8px;
      height: 8px;
      background: #409EFF;
      border-radius: 50%;
      animation: typing 1.4s infinite;
      
      &:nth-child(2) { animation-delay: 0.2s; }
      &:nth-child(3) { animation-delay: 0.4s; }
    }
  }
  
  .typing-text {
    color: #606266;
    font-size: 0.875rem;
  }
}

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-4px); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.chat-input-area {
  background: white;
  border-top: 1px solid #e4e7ed;
  padding: 1rem 2rem;
  
  .input-container {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    align-items: flex-end;
    gap: 1rem;
  }
  
  .input-actions {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .el-textarea {
    flex: 1;
    
    :deep(.el-textarea__inner) {
      border: 1px solid #e4e7ed;
      border-radius: 8px;
      resize: none;
      font-size: 1rem;
      padding: 1rem;
      
      &:focus {
        border-color: #409EFF;
        box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
      }
    }
  }
  
  .send-button {
    margin-bottom: 6px;
    
    .el-button {
      padding: 0.75rem 2rem;
      font-size: 1rem;
    }
  }
}

.voice-recording {
  text-align: center;
  padding: 1rem;
  background: #fef0f0;
  border-radius: 8px;
  margin-top: 1rem;
  animation: slideUp 0.3s ease;
  
  .voice-animation {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0.25rem;
    height: 40px;
    margin-bottom: 0.5rem;
    
    .voice-wave {
      width: 4px;
      height: 20px;
      background: #f56c6c;
      border-radius: 2px;
      animation: wave 1s ease-in-out infinite;
      
      &:nth-child(2) { animation-delay: 0.2s; }
      &:nth-child(3) { animation-delay: 0.4s; }
    }
  }
  
  p {
    margin: 0;
    color: #f56c6c;
    font-weight: 500;
  }
}

@keyframes wave {
  0%, 100% { height: 20px; }
  50% { height: 40px; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .chat-main {
    flex-direction: column;
  }
  
  .chat-sidebar {
    width: 100%;
    max-height: 200px;
  }
  
  .welcome-message {
    .question-buttons {
      grid-template-columns: 1fr !important;
    }
  }
  
  .message-content {
    max-width: 85%;
  }
}

@media (max-width: 768px) {
  .chat-header {
    padding: 1rem;
    
    .header-content {
      flex-direction: column;
      gap: 1rem;
      
      h1 {
        font-size: 1.25rem;
      }
    }
  }
  
  .chat-main {
    padding: 0.5rem;
  }
  
  .chat-input-area {
    padding: 1rem;
  }
  
  .input-container {
    flex-direction: column;
  }
  
  .input-actions {
    flex-direction: row !important;
  }
}
</style>