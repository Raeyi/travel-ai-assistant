import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: {
      title: '旅游AI客服 - 首页'
    }
  },
  {
    path: '/chat',
    name: 'chat',
    component: () => import('@/views/ChatView.vue'),
    meta: {
      title: 'AI聊天助手'
    }
  },
  {
    path: '/travel-plan',
    name: 'travel-plan',
    component: () => import('@/views/TravelPlanView.vue'),
    meta: {
      title: '旅行规划'
    }
  },
  {
    path: '/flights',
    name: 'flights',
    component: () => import('@/views/FlightsView.vue'),
    meta: {
      title: '航班查询'
    }
  },
  {
    path: '/hotels',
    name: 'hotels',
    component: () => import('@/views/HotelsView.vue'),
    meta: {
      title: '酒店预订'
    }
  },
  {
    path: '/weather',
    name: 'weather',
    component: () => import('@/views/WeatherView.vue'),
    meta: {
      title: '天气查询'
    }
  },
  {
    path: '/knowledge',
    name: 'knowledge',
    component: () => import('@/views/KnowledgeView.vue'),
    meta: {
      title: '知识库'
    }
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('@/views/AboutView.vue'),
    meta: {
      title: '关于我们'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: {
      title: '页面未找到'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router