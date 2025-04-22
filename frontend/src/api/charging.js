import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api',  // 后端的 API 地址
  timeout: 10000,  // 设置请求超时
  headers: {
    'Content-Type': 'application/json',  // 设置请求头
  },
})

// 获取所有充电区
export const getLocations = () => {
  return api.get('/charging_area/get_charging_areas')  // 获取所有充电区，返回数组
}

// 获取某个充电区下的充电桩
export const getChargingPiles = (locationId) => {
  return api.get('/charging-piles', {
    params: { location_id: locationId },  // 传递查询参数
  })
}

// 预约充电桩
export const reserveSession = (userId, pileId) => {
  return api.post('/charging-sessions/reserve', {
    user_id: userId,
    pile_id: pileId,
  })
}

// 开始充电
export const startSession = (sessionId) => {
  return api.post(`/charging-sessions/${sessionId}/start`)
}

// 停止充电
export const stopSession = (sessionId) => {
  return api.post(`/charging-sessions/${sessionId}/stop`)
}
