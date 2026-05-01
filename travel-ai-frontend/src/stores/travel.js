import { defineStore } from 'pinia'
import { ref } from 'vue'
import travelApi from '@/api'

export const useTravelStore = defineStore('travel', () => {
  const travelPlans = ref([])
  const currentPlan = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  
  // 创建旅行计划
  const createTravelPlan = async (planData) => {
    try {
      isLoading.value = true
      const response = await travelApi.createTravelPlan(planData)
      
      if (response) {
        currentPlan.value = response
        travelPlans.value.unshift(response)
        return response
      }
    } catch (err) {
      console.error('创建旅行计划失败:', err)
      error.value = '创建旅行计划失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // 获取旅行计划
  const getTravelPlan = async (planId, userId) => {
    try {
      isLoading.value = true
      const response = await travelApi.getTravelPlan(planId, userId)
      
      if (response) {
        currentPlan.value = response
        return response
      }
    } catch (err) {
      console.error('获取旅行计划失败:', err)
      error.value = '获取旅行计划失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // 搜索航班
  const searchFlights = async (flightData) => {
    try {
      isLoading.value = true
      const response = await travelApi.searchFlights(flightData)
      return response
    } catch (err) {
      console.error('搜索航班失败:', err)
      error.value = '搜索航班失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // 搜索酒店
  const searchHotels = async (hotelData) => {
    try {
      isLoading.value = true
      const response = await travelApi.searchHotels(hotelData)
      return response
    } catch (err) {
      console.error('搜索酒店失败:', err)
      error.value = '搜索酒店失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // 获取天气
  const getWeather = async (weatherData) => {
    try {
      isLoading.value = true
      const response = await travelApi.getWeather(weatherData)
      return response
    } catch (err) {
      console.error('获取天气失败:', err)
      error.value = '获取天气失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  return {
    travelPlans,
    currentPlan,
    isLoading,
    error,
    
    createTravelPlan,
    getTravelPlan,
    searchFlights,
    searchHotels,
    getWeather
  }
})