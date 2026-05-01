<template>
  <div class="travel-plan-view">
    <!-- 头部 -->
    <div class="page-header">
      <h1><el-icon><MapLocation /></el-icon> 旅行规划</h1>
      <p>AI智能生成个性化旅行计划</p>
    </div>
    
    <!-- 创建计划表单 -->
    <div class="create-plan-form">
      <el-card>
        <template #header>
          <h2>创建新的旅行计划</h2>
        </template>
        
        <el-form 
          :model="planForm" 
          :rules="formRules" 
          ref="formRef" 
          label-width="100px"
          label-position="top"
        >
          <div class="form-grid">
            <el-form-item label="目的地" prop="destination">
              <el-input 
                v-model="planForm.destination" 
                placeholder="例如：北京、上海、杭州等"
                size="large"
              >
                <template #prefix>
                  <el-icon><Location /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item label="出发日期" prop="startDate">
              <el-date-picker
                v-model="planForm.startDate"
                type="date"
                placeholder="选择出发日期"
                size="large"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            
            <el-form-item label="返回日期" prop="endDate">
              <el-date-picker
                v-model="planForm.endDate"
                type="date"
                placeholder="选择返回日期"
                size="large"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                :disabled-date="disabledEndDate"
              />
            </el-form-item>
            
            <el-form-item label="旅行人数" prop="travelers">
              <el-input-number
                v-model="planForm.travelers"
                :min="1"
                :max="20"
                controls-position="right"
                size="large"
              />
            </el-form-item>
            
            <el-form-item label="预算（元）" prop="budget">
              <el-input
                v-model="planForm.budget"
                placeholder="例如：5000"
                size="large"
              >
                <template #prefix>
                  <el-icon><Money /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item label="兴趣偏好" prop="interests">
              <el-select
                v-model="planForm.interests"
                multiple
                placeholder="请选择兴趣偏好"
                size="large"
                style="width: 100%"
              >
                <el-option
                  v-for="interest in interestOptions"
                  :key="interest.value"
                  :label="interest.label"
                  :value="interest.value"
                />
              </el-select>
            </el-form-item>
          </div>
          
          <el-form-item label="其他偏好" prop="preferences">
            <el-input
              v-model="planForm.preferences"
              type="textarea"
              :rows="3"
              placeholder="例如：希望安排轻松一点的行程，喜欢尝试当地美食，需要有Wi-Fi的住宿等"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              size="large" 
              @click="generatePlan" 
              :loading="isLoading"
            >
              <template #icon>
                <el-icon><MagicStick /></el-icon>
              </template>
              生成旅行计划
            </el-button>
            <el-button size="large" @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
    
    <!-- 生成的计划展示 -->
    <div v-if="generatedPlan" class="generated-plan">
      <el-card>
        <template #header>
          <div class="plan-header">
            <h2>生成的旅行计划</h2>
            <div class="plan-actions">
              <el-button type="success" @click="savePlan" :loading="isSaving">
                <el-icon><DocumentAdd /></el-icon> 保存计划
              </el-button>
              <el-button @click="exportPlan">
                <el-icon><Download /></el-icon> 导出
              </el-button>
            </div>
          </div>
        </template>
        
        <div class="plan-summary">
          <h3>计划概览</h3>
          <div class="summary-info">
            <div class="info-item">
              <el-icon><Location /></el-icon>
              <span>目的地：{{ generatedPlan.destination }}</span>
            </div>
            <div class="info-item">
              <el-icon><Calendar /></el-icon>
              <span>时间：{{ generatedPlan.startDate }} 至 {{ generatedPlan.endDate }}</span>
            </div>
            <div class="info-item">
              <el-icon><User /></el-icon>
              <span>人数：{{ generatedPlan.travelers }} 人</span>
            </div>
            <div class="info-item">
              <el-icon><Money /></el-icon>
              <span>预算：¥{{ generatedPlan.budget }}</span>
            </div>
          </div>
        </div>
        
        <!-- 每日行程 -->
        <div class="daily-itinerary">
          <h3>每日行程安排</h3>
          <el-timeline>
            <el-timeline-item
              v-for="(day, index) in generatedPlan.itinerary"
              :key="index"
              :timestamp="`第 ${day.day} 天`"
              placement="top"
              type="primary"
              :hollow="true"
            >
              <el-card>
                <template #header>
                  <h4>{{ day.date }} - {{ day.theme }}</h4>
                </template>
                
                <div class="day-schedule">
                  <!-- 上午安排 -->
                  <div class="time-slot morning">
                    <h5><el-icon><Sunrise /></el-icon> 上午</h5>
                    <div class="activities">
                      <div v-for="activity in day.morning" :key="activity.time" class="activity">
                        <span class="activity-time">{{ activity.time }}</span>
                        <span class="activity-name">{{ activity.name }}</span>
                        <el-tag v-if="activity.cost" type="info" size="small">
                          ¥{{ activity.cost }}
                        </el-tag>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 中午安排 -->
                  <div class="time-slot noon">
                    <h5><el-icon><Sunny /></el-icon> 中午</h5>
                    <div class="activities">
                      <div v-for="activity in day.noon" :key="activity.time" class="activity">
                        <span class="activity-time">{{ activity.time }}</span>
                        <span class="activity-name">{{ activity.name }}</span>
                        <el-tag v-if="activity.cost" type="info" size="small">
                          ¥{{ activity.cost }}
                        </el-tag>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 下午安排 -->
                  <div class="time-slot afternoon">
                    <h5><el-icon><Sunset /></el-icon> 下午</h5>
                    <div class="activities">
                      <div v-for="activity in day.afternoon" :key="activity.time" class="activity">
                        <span class="activity-time">{{ activity.time }}</span>
                        <span class="activity-name">{{ activity.name }}</span>
                        <el-tag v-if="activity.cost" type="info" size="small">
                          ¥{{ activity.cost }}
                        </el-tag>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 晚上安排 -->
                  <div class="time-slot evening">
                    <h5><el-icon><Moon /></el-icon> 晚上</h5>
                    <div class="activities">
                      <div v-for="activity in day.evening" :key="activity.time" class="activity">
                        <span class="activity-time">{{ activity.time }}</span>
                        <span class="activity-name">{{ activity.name }}</span>
                        <el-tag v-if="activity.cost" type="info" size="small">
                          ¥{{ activity.cost }}
                        </el-tag>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 小贴士 -->
                <div v-if="day.tips" class="day-tips">
                  <h5><el-icon><Opportunity /></el-icon> 小贴士</h5>
                  <p>{{ day.tips }}</p>
                </div>
                
                <!-- 当日预算 -->
                <div class="day-budget">
                  <h5><el-icon><Coin /></el-icon> 当日预算估算</h5>
                  <div class="budget-breakdown">
                    <div class="budget-item">
                      <span>住宿：</span>
                      <span>¥{{ day.budget_breakdown?.accommodation || 0 }}</span>
                    </div>
                    <div class="budget-item">
                      <span>餐饮：</span>
                      <span>¥{{ day.budget_breakdown?.food || 0 }}</span>
                    </div>
                    <div class="budget-item">
                      <span>交通：</span>
                      <span>¥{{ day.budget_breakdown?.transportation || 0 }}</span>
                    </div>
                    <div class="budget-item">
                      <span>门票：</span>
                      <span>¥{{ day.budget_breakdown?.tickets || 0 }}</span>
                    </div>
                    <div class="budget-item total">
                      <span>小计：</span>
                      <span>¥{{ day.budget_breakdown?.total || 0 }}</span>
                    </div>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
        
        <!-- 预算总结 -->
        <div class="budget-summary">
          <h3>预算总结</h3>
          <el-table :data="budgetSummary" style="width: 100%">
            <el-table-column prop="category" label="类别" width="200" />
            <el-table-column prop="budget" label="预算(元)" width="150">
              <template #default="scope">
                ¥{{ scope.row.budget.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="percentage" label="占比" width="100">
              <template #default="scope">
                {{ scope.row.percentage }}%
              </template>
            </el-table-column>
            <el-table-column prop="description" label="说明" />
          </el-table>
        </div>
        
        <!-- 建议 -->
        <div class="recommendations">
          <h3>旅行建议</h3>
          <div class="recommendation-grid">
            <el-card v-for="(rec, index) in recommendations" :key="index" class="recommendation-card">
              <template #header>
                <h4>
                  <el-icon :color="rec.color">
                    <component :is="rec.icon" />
                  </el-icon>
                  {{ rec.title }}
                </h4>
              </template>
              <p>{{ rec.content }}</p>
            </el-card>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  MapLocation, Location, Calendar, User, Money, 
  MagicStick, DocumentAdd, Download, Sunrise, 
  Sunny, Sunset, Moon, Opportunity, Coin
} from '@element-plus/icons-vue'
import { useTravelStore } from '@/stores/travel'
import { ElMessage, ElMessageBox } from 'element-plus'

const travelStore = useTravelStore()
const formRef = ref(null)
const isLoading = ref(false)
const isSaving = ref(false)
const generatedPlan = ref(null)

// 表单数据
const planForm = ref({
  destination: '',
  startDate: '',
  endDate: '',
  budget: '',
  travelers: 1,
  interests: [],
  preferences: ''
})

// 表单验证规则
const formRules = {
  destination: [
    { required: true, message: '请输入目的地', trigger: 'blur' }
  ],
  startDate: [
    { required: true, message: '请选择出发日期', trigger: 'change' }
  ],
  endDate: [
    { required: true, message: '请选择返回日期', trigger: 'change' }
  ],
  budget: [
    { required: true, message: '请输入预算', trigger: 'blur' },
    { pattern: /^\d+$/, message: '预算必须为数字', trigger: 'blur' }
  ]
}

// 兴趣选项
const interestOptions = [
  { label: '历史文化', value: 'history_culture' },
  { label: '自然风光', value: 'natural_scenery' },
  { label: '美食餐饮', value: 'food_dining' },
  { label: '购物娱乐', value: 'shopping_entertainment' },
  { label: '亲子家庭', value: 'family_friendly' },
  { label: '户外探险', value: 'outdoor_adventure' },
  { label: '艺术展览', value: 'art_exhibition' },
  { label: '摄影打卡', value: 'photography' },
  { label: '休闲度假', value: 'leisure_vacation' },
  { label: '商务出差', value: 'business_trip' }
]

// 计算结束日期禁用
const disabledEndDate = (time) => {
  if (!planForm.value.startDate) return false
  return time.getTime() <= new Date(planForm.value.startDate).getTime()
}

// 生成旅行计划
const generatePlan = async () => {
  try {
    await formRef.value.validate()
    isLoading.value = true
    
    const planData = {
      user_id: 'temp_user_' + Date.now(),
      destination: planForm.value.destination,
      start_date: planForm.value.startDate,
      end_date: planForm.value.endDate,
      budget: Number(planForm.value.budget),
      travelers: planForm.value.travelers,
      interests: planForm.value.interests,
      preferences: planForm.value.preferences ? { notes: planForm.value.preferences } : {}
    }
    
    const result = await travelStore.createTravelPlan(planData)
    
    if (result) {
      generatedPlan.value = {
        ...result,
        destination: planForm.value.destination,
        startDate: planForm.value.startDate,
        endDate: planForm.value.endDate,
        budget: planForm.value.budget,
        travelers: planForm.value.travelers
      }
      ElMessage.success('旅行计划生成成功！')
    }
  } catch (error) {
    console.error('生成计划失败:', error)
    ElMessage.error('生成计划失败，请重试')
  } finally {
    isLoading.value = false
  }
}

// 保存计划
const savePlan = async () => {
  try {
    isSaving.value = true
    // 这里可以添加保存到后端的逻辑
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('计划保存成功！')
  } catch (error) {
    console.error('保存计划失败:', error)
    ElMessage.error('保存计划失败')
  } finally {
    isSaving.value = false
  }
}

// 导出计划
const exportPlan = () => {
  ElMessage.info('导出功能开发中...')
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  generatedPlan.value = null
}

// 计算预算总结
const budgetSummary = computed(() => {
  if (!generatedPlan.value?.itinerary) return []
  
  const totals = {}
  generatedPlan.value.itinerary.forEach(day => {
    if (day.budget_breakdown) {
      Object.entries(day.budget_breakdown).forEach(([category, amount]) => {
        totals[category] = (totals[category] || 0) + (Number(amount) || 0)
      })
    }
  })
  
  const totalBudget = Object.values(totals).reduce((sum, val) => sum + val, 0)
  
  return [
    { category: '住宿', budget: totals.accommodation || 0, percentage: Math.round((totals.accommodation || 0) / totalBudget * 100) || 0, description: '酒店/民宿费用' },
    { category: '餐饮', budget: totals.food || 0, percentage: Math.round((totals.food || 0) / totalBudget * 100) || 0, description: '三餐及零食费用' },
    { category: '交通', budget: totals.transportation || 0, percentage: Math.round((totals.transportation || 0) / totalBudget * 100) || 0, description: '机票/火车/出租车/公共交通' },
    { category: '门票', budget: totals.tickets || 0, percentage: Math.round((totals.tickets || 0) / totalBudget * 100) || 0, description: '景点门票费用' },
    { category: '购物', budget: totals.shopping || 0, percentage: Math.round((totals.shopping || 0) / totalBudget * 100) || 0, description: '购物纪念品费用' },
    { category: '其他', budget: totals.other || 0, percentage: Math.round((totals.other || 0) / totalBudget * 100) || 0, description: '其他杂项费用' },
    { category: '总计', budget: totalBudget, percentage: 100, description: '总预算' }
  ]
})

// 建议卡片
const recommendations = computed(() => [
  { 
    title: '最佳旅行时间',
    content: '春季(3-5月)和秋季(9-11月)是最佳旅行时间，天气适宜，景色优美。',
    icon: 'Calendar',
    color: '#409EFF'
  },
  { 
    title: '交通建议',
    content: '建议乘坐地铁出行，避免交通拥堵。下载当地交通APP可享受更多优惠。',
    icon: 'Van',
    color: '#67C23A'
  },
  { 
    title: '美食推荐',
    content: '一定要尝试当地特色小吃，如烤鸭、豆汁、炸酱面等。',
    icon: 'KnifeFork',
    color: '#E6A23C'
  },
  { 
    title: '购物提示',
    content: '王府井步行街和西单是购物的好去处，注意比价，可适当讨价还价。',
    icon: 'ShoppingCart',
    color: '#F56C6C'
  },
  { 
    title: '天气提醒',
    content: '当地昼夜温差较大，建议携带外套。注意防晒和补水。',
    icon: 'Sunny',
    color: '#909399'
  },
  { 
    title: '安全注意',
    content: '保管好个人财物，避免前往人流过于密集的地方，注意交通安全。',
    icon: 'Warning',
    color: '#8E44AD'
  }
])

onMounted(() => {
  // 页面加载时的一些初始化
})
</script>

<style lang="scss" scoped>
.travel-plan-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  
  h1 {
    font-size: 2.5rem;
    color: #303133;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }
  
  p {
    font-size: 1.1rem;
    color: #606266;
  }
}

.create-plan-form {
  margin-bottom: 40px;
  
  .el-card__header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    
    h2 {
      color: white;
      margin: 0;
    }
  }
  
  .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
  }
}

.generated-plan {
  .plan-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h2 {
      margin: 0;
    }
  }
  
  .plan-summary {
    margin-bottom: 30px;
    
    .summary-info {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin-top: 20px;
      
      .info-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 15px;
        background: #f5f7fa;
        border-radius: 8px;
        
        svg {
          color: #409EFF;
          font-size: 20px;
        }
        
        span {
          font-size: 1rem;
          font-weight: 500;
        }
      }
    }
  }
  
  .daily-itinerary {
    margin: 30px 0;
    
    .day-schedule {
      .time-slot {
        margin-bottom: 20px;
        
        h5 {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 10px;
          color: #606266;
          
          svg {
            font-size: 18px;
          }
        }
        
        .activities {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        
        .activity {
          display: flex;
          align-items: center;
          gap: 15px;
          padding: 10px 15px;
          background: #f8fafc;
          border-radius: 6px;
          
          .activity-time {
            min-width: 60px;
            color: #409EFF;
            font-weight: 500;
          }
          
          .activity-name {
            flex: 1;
          }
        }
      }
    }
    
    .day-tips {
      margin: 20px 0;
      padding: 15px;
      background: #fff8e1;
      border-radius: 8px;
      
      h5 {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #e6a23c;
        margin-bottom: 10px;
      }
      
      p {
        color: #606266;
        line-height: 1.6;
      }
    }
    
    .day-budget {
      margin: 20px 0;
      
      h5 {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #67c23a;
        margin-bottom: 15px;
      }
      
      .budget-breakdown {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 10px;
        
        .budget-item {
          display: flex;
          justify-content: space-between;
          padding: 8px 12px;
          background: #f5f7fa;
          border-radius: 4px;
          
          &.total {
            background: #e1f5e1;
            font-weight: bold;
          }
        }
      }
    }
  }
  
  .recommendations {
    margin-top: 40px;
    
    .recommendation-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      margin-top: 20px;
    }
    
    .recommendation-card {
      .el-card__header {
        h4 {
          margin: 0;
          display: flex;
          align-items: center;
          gap: 8px;
        }
      }
      
      p {
        color: #606266;
        line-height: 1.6;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .travel-plan-view {
    padding: 10px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .form-grid {
    grid-template-columns: 1fr !important;
  }
  
  .plan-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start !important;
  }
  
  .summary-info {
    grid-template-columns: 1fr !important;
  }
  
  .budget-breakdown {
    grid-template-columns: 1fr !important;
  }
  
  .recommendation-grid {
    grid-template-columns: 1fr !important;
  }
}
</style>