<template>
  <div class="flights-view">
    <!-- 头部 -->
    <div class="page-header">
      <h1><el-icon><Promotion /></el-icon> 航班查询</h1>
      <p>实时查询航班信息，比较价格和时间</p>
    </div>
    
    <!-- 搜索表单 -->
    <div class="search-form">
      <el-card>
        <el-form :model="searchForm" label-width="80px">
          <div class="form-row">
            <el-form-item label="出发地">
              <el-input v-model="searchForm.departure" placeholder="例如：北京" />
            </el-form-item>
            <el-form-item label="目的地">
              <el-input v-model="searchForm.arrival" placeholder="例如：上海" />
            </el-form-item>
            <el-form-item label="出发日期">
              <el-date-picker
                v-model="searchForm.date"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            <el-form-item label="乘客">
              <el-input-number
                v-model="searchForm.passengers"
                :min="1"
                :max="10"
                controls-position="right"
              />
            </el-form-item>
          </div>
          <el-form-item>
            <el-button type="primary" @click="searchFlights" :loading="isLoading">
              搜索航班
            </el-button>
            <el-button @click="resetForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
    
    <!-- 搜索结果 -->
    <div v-if="searchResults.length > 0" class="search-results">
      <h2>搜索结果 ({{ searchResults.length }} 个航班)</h2>
      
      <div class="results-list">
        <el-card
          v-for="flight in searchResults"
          :key="flight.flight_number"
          class="flight-card"
        >
          <div class="flight-info">
            <div class="flight-header">
              <div class="airline">
                <h3>{{ flight.airline }}</h3>
                <span class="flight-number">{{ flight.flight_number }}</span>
              </div>
              <el-tag type="success" v-if="flight.direct">直飞</el-tag>
            </div>
            
            <div class="route-info">
              <div class="departure">
                <div class="time">{{ flight.departure_time }}</div>
                <div class="airport">{{ flight.departure }}</div>
              </div>
              
              <div class="duration">
                <div class="line"></div>
                <div class="duration-text">{{ flight.duration }}</div>
              </div>
              
              <div class="arrival">
                <div class="time">{{ flight.arrival_time }}</div>
                <div class="airport">{{ flight.arrival }}</div>
              </div>
            </div>
            
            <div class="flight-details">
              <div class="price-section">
                <div class="price">¥{{ flight.price.toFixed(2) }}</div>
                <div class="per-person">人均 ¥{{ (flight.price / searchForm.passengers).toFixed(2) }}</div>
              </div>
              
              <div class="actions">
                <el-button type="primary" @click="bookFlight(flight)">
                  立即预订
                </el-button>
                <el-button @click="showFlightDetails(flight)">
                  查看详情
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 无结果提示 -->
    <div v-else-if="searched" class="no-results">
      <el-empty description="没有找到符合条件的航班" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Promotion } from '@element-plus/icons-vue'
import { useTravelStore } from '@/stores/travel'
import { ElMessage, ElMessageBox } from 'element-plus'

const travelStore = useTravelStore()
const isLoading = ref(false)
const searched = ref(false)
const searchResults = ref([])

// 搜索表单
const searchForm = ref({
  departure: '北京',
  arrival: '上海',
  date: '2024-12-01',
  passengers: 1,
  return_date: null,
  class_type: 'economy',
  direct_only: false
})

// 搜索航班
const searchFlights = async () => {
  try {
    isLoading.value = true
    searched.value = true
    
    const result = await travelStore.searchFlights({
      departure: searchForm.value.departure,
      arrival: searchForm.value.arrival,
      date: searchForm.value.date,
      return_date: searchForm.value.return_date,
      passengers: searchForm.value.passengers,
      class_type: searchForm.value.class_type,
      direct_only: searchForm.value.direct_only
    })
    
    if (result?.data?.flights) {
      searchResults.value = result.data.flights
      ElMessage.success(`找到 ${result.data.flights.length} 个航班`)
    } else {
      searchResults.value = []
    }
  } catch (error) {
    console.error('搜索航班失败:', error)
    ElMessage.error('搜索失败，请重试')
  } finally {
    isLoading.value = false
  }
}

// 预订航班
const bookFlight = (flight) => {
  ElMessageBox.confirm(
    `确认预订 ${flight.airline} ${flight.flight_number} 航班？`,
    '确认预订',
    {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.success('预订成功！')
  })
}

// 显示航班详情
const showFlightDetails = (flight) => {
  ElMessageBox.alert(
    `航班详情：
    航空公司：${flight.airline}
    航班号：${flight.flight_number}
    出发：${flight.departure} ${flight.departure_time}
    到达：${flight.arrival} ${flight.arrival_time}
    时长：${flight.duration}
    价格：¥${flight.price.toFixed(2)}
    可用座位：${flight.seats_available}`,
    '航班详情'
  )
}

// 重置表单
const resetForm = () => {
  searchForm.value = {
    departure: '',
    arrival: '',
    date: '',
    passengers: 1,
    return_date: null,
    class_type: 'economy',
    direct_only: false
  }
  searchResults.value = []
  searched.value = false
}
</script>

<style lang="scss" scoped>
.flights-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  
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

.search-form {
  margin-bottom: 40px;
  
  .el-form-item {
    margin-bottom: 20px;
  }
  
  .form-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
  }
}

.search-results {
  h2 {
    margin-bottom: 20px;
    color: #303133;
  }
  
  .results-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .flight-card {
    transition: transform 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .flight-info {
      .flight-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        
        .airline {
          display: flex;
          align-items: center;
          gap: 10px;
          
          h3 {
            margin: 0;
            font-size: 1.2rem;
          }
          
          .flight-number {
            color: #409EFF;
            font-weight: 500;
          }
        }
      }
      
      .route-info {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 20px 0;
        padding: 20px 0;
        border-top: 1px solid #e4e7ed;
        border-bottom: 1px solid #e4e7ed;
        
        .departure, .arrival {
          text-align: center;
          flex: 1;
          
          .time {
            font-size: 1.5rem;
            font-weight: bold;
            color: #303133;
            margin-bottom: 5px;
          }
          
          .airport {
            color: #606266;
            font-size: 0.9rem;
          }
        }
        
        .duration {
          display: flex;
          flex-direction: column;
          align-items: center;
          flex: 2;
          
          .line {
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, #409EFF 0%, #67C23A 100%);
            position: relative;
            
            &::before, &::after {
              content: '';
              position: absolute;
              width: 8px;
              height: 8px;
              background: #409EFF;
              border-radius: 50%;
              top: -3px;
            }
            
            &::before {
              left: 0;
            }
            
            &::after {
              right: 0;
              background: #67C23A;
            }
          }
          
          .duration-text {
            margin-top: 5px;
            color: #909399;
            font-size: 0.9rem;
          }
        }
      }
      
      .flight-details {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        .price-section {
          .price {
            font-size: 1.8rem;
            font-weight: bold;
            color: #F56C6C;
          }
          
          .per-person {
            color: #909399;
            font-size: 0.9rem;
          }
        }
        
        .actions {
          display: flex;
          gap: 10px;
        }
      }
    }
  }
}

.no-results {
  text-align: center;
  margin-top: 50px;
}

// 响应式设计
@media (max-width: 768px) {
  .flights-view {
    padding: 10px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .form-row {
    grid-template-columns: 1fr !important;
  }
  
  .flight-header {
    flex-direction: column;
    align-items: flex-start !important;
    gap: 10px;
  }
  
  .route-info {
    flex-direction: column !important;
    gap: 20px;
    
    .duration {
      order: 3;
      width: 100%;
      
      .line {
        width: 100% !important;
      }
    }
  }
  
  .flight-details {
    flex-direction: column !important;
    align-items: stretch !important;
    gap: 20px;
    
    .actions {
      width: 100%;
      
      .el-button {
        width: 100%;
      }
    }
  }
}
</style>