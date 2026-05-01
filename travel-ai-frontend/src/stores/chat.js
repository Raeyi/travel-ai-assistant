import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import travelApi from '@/api'
import { v4 as uuidv4 } from 'uuid'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const messages = ref([])
  const sessionId = ref('')
  const isLoading = ref(false)
  const error = ref(null)
  const currentIntent = ref('')
  const entities = ref({})
  const suggestions = ref([])
  
  // 获取会话ID
  const getOrCreateSessionId = () => {
    if (!sessionId.value) {
      const storedSessionId = localStorage.getItem('travel_session_id')
      if (storedSessionId) {
        sessionId.value = storedSessionId
      } else {
        sessionId.value = `session_${Date.now()}_${uuidv4().slice(0, 8)}`
        localStorage.setItem('travel_session_id', sessionId.value)
      }
    }
    return sessionId.value
  }
  
  // 加载会话历史
  const loadChatHistory = async () => {
    try {
      const sessionId = getOrCreateSessionId()
      const response = await travelApi.getSessionContext(sessionId)
      
      if (response.success && response.context) {
        messages.value = response.context
      }
    } catch (err) {
      console.error('加载聊天历史失败:', err)
      error.value = '加载聊天历史失败'
    }
  }
  
  // 发送消息
  const sendMessage = async (message, messageType = 'text', userId = null) => {
    try {
      isLoading.value = true
      error.value = null
      
      const sessionId = getOrCreateSessionId()
      
      // 添加用户消息到本地
      const userMessage = {
        role: 'user',
        content: message,
        type: messageType,
        timestamp: new Date().toISOString()
      }
      messages.value.push(userMessage)
      
      let response
      
      if (messageType === 'text') {
        response = await travelApi.chatText(sessionId, message, userId)
      } else if (messageType === 'voice') {
        // 语音消息处理
        response = await travelApi.chatVoice(sessionId, message, userId)
      }
      
      if (response) {
        // 添加AI回复
        const aiMessage = {
          role: 'assistant',
          content: response.message,
          intent: response.intent,
          confidence: response.confidence,
          entities: response.entities,
          suggestions: response.suggestions || [],
          actions: response.actions || [],
          timestamp: response.timestamp || new Date().toISOString()
        }
        messages.value.push(aiMessage)
        
        // 更新状态
        currentIntent.value = response.intent
        entities.value = response.entities || {}
        suggestions.value = response.suggestions || []
        
        return response
      }
    } catch (err) {
      console.error('发送消息失败:', err)
      error.value = '发送消息失败，请重试'
      
      // 移除失败的用户消息
      messages.value = messages.value.filter(msg => msg !== messages.value[messages.value.length - 1])
      
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // 发送建议
  const sendSuggestion = async (suggestion) => {
    return sendMessage(suggestion, 'text')
  }
  
  // 清除聊天记录
  const clearChat = async () => {
    try {
      const sessionId = getOrCreateSessionId()
      await travelApi.clearSessionContext(sessionId)
      messages.value = []
      currentIntent.value = ''
      entities.value = {}
      suggestions.value = []
      
      // 生成新的会话ID
      sessionId.value = `session_${Date.now()}_${uuidv4().slice(0, 8)}`
      localStorage.setItem('travel_session_id', sessionId.value)
    } catch (err) {
      console.error('清除聊天记录失败:', err)
      error.value = '清除聊天记录失败'
      throw err
    }
  }
  
  // 计算属性
  const hasMessages = computed(() => messages.value.length > 0)
  const lastMessage = computed(() => messages.value[messages.value.length - 1])
  const messageCount = computed(() => messages.value.length)
  const isAiTyping = computed(() => isLoading.value && messages.value[messages.value.length - 1]?.role === 'user')
  
  return {
    // 状态
    messages,
    sessionId,
    isLoading,
    error,
    currentIntent,
    entities,
    suggestions,
    
    // 计算属性
    hasMessages,
    lastMessage,
    messageCount,
    isAiTyping,
    
    // 方法
    getOrCreateSessionId,
    loadChatHistory,
    sendMessage,
    sendSuggestion,
    clearChat
  }
})