<template>
  <div class="knowledge-view">
    <div class="page-header">
      <h1><el-icon><CollectionTag /></el-icon> 知识库</h1>
      <p>丰富的旅游知识和常见问题解答</p>
    </div>
    <div class="coming-soon">
      <el-result
        icon="info"
        title="功能开发中"
        sub-title="知识库功能即将上线，敬请期待！"
      />
    </div>
  </div>
</template>

<script setup>
import { CollectionTag } from '@element-plus/icons-vue'
</script>

<style scoped>
.knowledge-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
</style>