<template>
  <div class="hotels-view">
    <div class="page-header">
      <h1><el-icon><House /></el-icon> 酒店查询</h1>
      <p>查找合适酒店，比较价格和评价</p>
    </div>
    <div class="coming-soon">
      <el-result
        icon="info"
        title="功能开发中"
        sub-title="酒店查询功能即将上线，敬请期待！"
      >
        <template #extra>
          <el-button type="primary" @click="goBack">返回首页</el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup>
import { House } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const goBack = () => {
  router.push('/')
}
</script>

<style scoped>
.hotels-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.coming-soon {
  margin-top: 100px;
}
</style>