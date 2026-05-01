<template>
  <div class="about-view">
    <div class="page-header">
      <h1><el-icon><InfoFilled /></el-icon> 关于我们</h1>
    </div>
    <div class="about-content">
      <el-card>
        <h2>旅游AI客服系统</h2>
        <p>版本: 1.0.0</p>
        <p>一个基于人工智能的旅游客服系统，为您提供全方位的旅游咨询服务。</p>
        <h3>功能特点：</h3>
        <ul>
          <li>智能对话助手</li>
          <li>旅行规划</li>
          <li>航班/酒店查询</li>
          <li>天气查询</li>
          <li>知识库问答</li>
        </ul>
        <h3>技术栈：</h3>
        <p>后端: Python FastAPI + LangChain + DeepSeek API</p>
        <p>前端: Vue 3 + Element Plus</p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { InfoFilled } from '@element-plus/icons-vue'
</script>

<style scoped>
.about-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.about-content {
  line-height: 1.6;
  
  h2, h3 {
    margin: 20px 0 10px 0;
  }
  
  ul {
    margin: 10px 0 20px 20px;
  }
}
</style>