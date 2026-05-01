<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from 'vue-router'

const route = useRoute()

const navItems = [
  { path: '/', label: '首页', icon: '🏠' },
  { path: '/chat', label: 'AI聊天', icon: '💬' },
  { path: '/travel-plan', label: '旅行规划', icon: '🗺️' },
  { path: '/flights', label: '航班查询', icon: '✈️' },
  { path: '/hotels', label: '酒店预订', icon: '🏨' },
  { path: '/weather', label: '天气查询', icon: '🌤️' },
  { path: '/knowledge', label: '知识库', icon: '📚' },
  { path: '/about', label: '关于', icon: 'ℹ️' },
]
</script>

<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-content">
        <router-link to="/" class="logo">
          <span class="logo-icon">🌍</span>
          <span class="logo-text">旅游AI助手</span>
        </router-link>
        <nav class="nav-menu">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="nav-link"
            :class="{ active: route.path === item.path }"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
          </router-link>
        </nav>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<style lang="scss">

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background: #fff;
  box-shadow: $box-shadow-base;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  height: 60px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: $text-primary;
  font-size: $font-size-large;
  font-weight: 600;
  margin-right: 40px;
  flex-shrink: 0;

  .logo-icon {
    font-size: 24px;
  }
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 4px;
  overflow-x: auto;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  border-radius: $border-radius-base;
  text-decoration: none;
  color: $text-regular;
  font-size: $font-size-base;
  white-space: nowrap;
  transition: all 0.2s;

  &:hover {
    background: $background-color-base;
    color: $primary-color;
  }

  &.active {
    background: rgba(64, 158, 255, 0.1);
    color: $primary-color;
    font-weight: 500;
  }

  .nav-icon {
    font-size: 16px;
  }
}

.app-main {
  flex: 1;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 24px;
}

@media (max-width: $breakpoint-md) {
  .header-content {
    padding: 0 12px;
  }

  .logo {
    margin-right: 16px;
    .logo-text {
      display: none;
    }
  }

  .nav-link {
    padding: 8px 10px;
    .nav-label {
      display: none;
    }
  }
}
</style>
