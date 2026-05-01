<template>
  <div class="weather-view">
    <div class="page-header">
      <h1><el-icon><Sunny /></el-icon> 天气查询</h1>
      <p>查询目的地天气，合理安排行程</p>
    </div>
    <div class="coming-soon">
      <el-result
        icon="info"
        title="功能开发中"
        sub-title="天气查询功能即将上线，敬请期待！"
      />
    </div>
  </div>
</template>

<script setup>
import { Sunny } from '@element-plus/icons-vue'
</script>

<style scoped>
.weather-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
</style>