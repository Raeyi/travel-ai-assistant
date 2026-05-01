import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加loading状态
    if (config.showLoading !== false) {
      // 可以在这里添加全局loading
    }
    
    // 添加token等认证信息
    const token = localStorage.getItem('travel_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API请求错误:', error)
    
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // token过期，跳转到登录页
          localStorage.removeItem('travel_token')
          window.location.href = '/login'
          break
        case 403:
          alert('没有权限访问此资源')
          break
        case 404:
          alert('请求的资源不存在')
          break
        case 500:
          alert('服务器内部错误')
          break
        default:
          alert(`请求失败: ${error.response.status}`)
      }
    } else if (error.request) {
      alert('网络连接失败，请检查网络设置')
    } else {
      alert(`请求错误: ${error.message}`)
    }
    
    return Promise.reject(error)
  }
)

// API接口定义
const travelApi = {
  // 健康检查
  healthCheck() {
    return api.get('/health')
  },
  
  // 聊天接口
  chat(messageData) {
    return api.post('/chat', messageData)
  },
  
  chatText(sessionId, message, userId = null) {
    const formData = new FormData()
    formData.append('session_id', sessionId)
    formData.append('message', message)
    if (userId) {
      formData.append('user_id', userId)
    }
    return api.post('/chat/text', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  },
  
  // 语音聊天
  chatVoice(sessionId, audioFile, userId = null) {
    const formData = new FormData()
    formData.append('session_id', sessionId)
    formData.append('audio_file', audioFile)
    if (userId) {
      formData.append('user_id', userId)
    }
    return api.post('/chat/voice', formData)
  },
  
  // 创建旅行计划
  createTravelPlan(planData) {
    return api.post('/travel/plan', planData)
  },
  
  // 获取旅行计划
  getTravelPlan(planId, userId) {
    return api.get(`/travel/plan/${planId}`, {
      params: { user_id: userId }
    })
  },
  
  // 搜索航班
  searchFlights(flightData) {
    return api.post('/flights/search', flightData)
  },
  
  // 搜索酒店
  searchHotels(hotelData) {
    return api.post('/hotels/search', hotelData)
  },
  
  // 查询天气
  getWeather(weatherData) {
    return api.post('/weather', weatherData)
  },
  
  // 搜索知识库
  searchKnowledge(queryData) {
    return api.post('/knowledge/search', queryData)
  },
  
  // 货币转换
  convertCurrency(amount, fromCurrency, toCurrency) {
    return api.post('/currency/convert', {
      amount,
      from_currency: fromCurrency,
      to_currency: toCurrency
    })
  },
  
  // 翻译
  translate(text, targetLanguage) {
    return api.post('/translate', {
      text,
      target_language: targetLanguage
    })
  },
  
  // 获取会话上下文
  getSessionContext(sessionId) {
    return api.get(`/session/${sessionId}/context`)
  },
  
  // 清除会话上下文
  clearSessionContext(sessionId) {
    return api.delete(`/session/${sessionId}`)
  },
  
  // 用户管理
  createUser(userData) {
    return api.post('/user/create', userData)
  },
  
  getUserConversations(userId, limit = 20, offset = 0) {
    return api.get(`/user/${userId}/conversations`, {
      params: { limit, offset }
    })
  }
}

export default travelApi