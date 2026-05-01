<template>
  <div class="home-view">
    <!-- 头部 -->
    <header class="home-header">
      <div class="container">
        <h1 class="title">旅游AI客服系统</h1>
        <p class="subtitle">智能规划您的完美旅程</p>
        <el-button type="primary" size="large" @click="gotoChat">
          开始聊天 <el-icon><ChatLineRound /></el-icon>
        </el-button>
      </div>
    </header>
    
    <!-- 功能展示 -->
    <section class="features">
      <div class="container">
        <h2 class="section-title">核心功能</h2>
        <div class="features-grid">
          <div v-for="feature in features" :key="feature.id" class="feature-card">
            <div class="feature-icon" :style="{ backgroundColor: feature.color }">
              <component :is="feature.icon" />
            </div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
            <el-button type="text" @click="gotoPage(feature.route)">
              立即体验 →
            </el-button>
          </div>
        </div>
      </div>
    </section>
    
    <!-- 使用指南 -->
    <section class="guide">
      <div class="container">
        <h2 class="section-title">使用指南</h2>
        <div class="steps">
          <div v-for="(step, index) in steps" :key="index" class="step">
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-content">
              <h3>{{ step.title }}</h3>
              <p>{{ step.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- 页脚 -->
    <footer class="footer">
      <div class="container">
        <p>© 2024 旅游AI客服系统. 由DeepSeek和LangChain提供技术支持</p>
        <p>快乐旅行科技公司出品</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { 
  ChatLineRound, 
  Promotion, 
  House, 
  Sunny, 
  MapLocation, 
  CollectionTag 
} from '@element-plus/icons-vue'

const router = useRouter()

const features = ref([
  {
    id: 1,
    icon: ChatLineRound,
    title: '智能对话',
    description: '与AI助手自然对话，解答旅游相关问题',
    route: '/chat',
    color: '#409EFF'
  },
  {
    id: 2,
    icon: Promotion,
    title: '航班查询',
    description: '实时查询航班信息，比较价格和时间',
    route: '/flights',
    color: '#67C23A'
  },
  {
    id: 3,
    icon: House,
    title: '酒店预订',
    description: '查找合适酒店，比较价格和评价',
    route: '/hotels',
    color: '#E6A23C'
  },
  {
    id: 4,
    icon: MapLocation,
    title: '旅行规划',
    description: 'AI自动生成个性化旅行计划',
    route: '/travel-plan',
    color: '#F56C6C'
  },
  {
    id: 5,
    icon: Sunny,
    title: '天气查询',
    description: '查询目的地天气，合理安排行程',
    route: '/weather',
    color: '#909399'
  },
  {
    id: 6,
    icon: CollectionTag,
    title: '知识库',
    description: '丰富的旅游知识和常见问题解答',
    route: '/knowledge',
    color: '#8E44AD'
  }
])

const steps = ref([
  {
    title: '开始对话',
    description: '在聊天界面与AI助手交流，描述您的旅行需求'
  },
  {
    title: '获取建议',
    description: 'AI根据您的需求提供航班、酒店、景点等建议'
  },
  {
    title: '规划行程',
    description: 'AI为您创建详细的旅行计划，包括行程安排和预算'
  },
  {
    title: '预订服务',
    description: '通过集成的第三方服务完成机票、酒店等预订'
  }
])

const gotoChat = () => {
  router.push('/chat')
}

const gotoPage = (route) => {
  router.push(route)
}
</script>

<style lang="scss" scoped>
.home-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.home-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 100px 0;
  text-align: center;
  flex: 1;
  
  .title {
    font-size: 3.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
  }
  
  .subtitle {
    font-size: 1.5rem;
    opacity: 0.9;
    margin-bottom: 2rem;
  }
  
  .el-button {
    font-size: 1.2rem;
    padding: 1rem 2rem;
  }
}

.features {
  padding: 80px 0;
  background-color: #f8fafc;
  
  .section-title {
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 3rem;
    color: #1a202c;
  }
  
  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
  }
  
  .feature-card {
    background: white;
    border-radius: 10px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
    
    &:hover {
      transform: translateY(-5px);
    }
    
    .feature-icon {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto 1.5rem;
      
      svg {
        width: 30px;
        height: 30px;
        color: white;
      }
    }
    
    h3 {
      font-size: 1.5rem;
      margin-bottom: 1rem;
      color: #1a202c;
    }
    
    p {
      color: #718096;
      margin-bottom: 1.5rem;
      line-height: 1.6;
    }
  }
}

.guide {
  padding: 80px 0;
  
  .section-title {
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 3rem;
    color: #1a202c;
  }
  
  .steps {
    max-width: 800px;
    margin: 0 auto;
  }
  
  .step {
    display: flex;
    align-items: flex-start;
    margin-bottom: 3rem;
    padding: 1.5rem;
    border-radius: 10px;
    background: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .step-number {
      width: 50px;
      height: 50px;
      border-radius: 50%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.5rem;
      font-weight: bold;
      margin-right: 1.5rem;
      flex-shrink: 0;
    }
    
    .step-content {
      flex: 1;
      
      h3 {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        color: #1a202c;
      }
      
      p {
        color: #718096;
        line-height: 1.6;
      }
    }
  }
}

.footer {
  background: #1a202c;
  color: white;
  padding: 2rem 0;
  text-align: center;
  margin-top: auto;
  
  p {
    margin: 0.5rem 0;
    opacity: 0.8;
  }
}
</style>