import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

// 获取所有充电区
export const getLocations = () => {
  return api.get('/charging_area/get_charging_areas')
}

// 获取某个充电区下的充电桩
export const getChargingPiles = (locationId) => {
  return api.get('/charging-piles', {
    params: { location_id: locationId },
  })
}

// —— 新增：获取某桩当日时段状态 ——
// date: "YYYY-MM-DD"，userId 可选，用于标记“mine”
export const getPileSlots = (pileId, date, userId = null) => {
  return api.get(`/charging-piles/${pileId}/slots`, {
    params: { date, user_id: userId },
  })
}

// 预约充电桩 —— 多传 date 与 slot
// date: "YYYY-MM-DD"，slot: "HH:mm"
export const reserveSession = (userId, pileId, vehicleId, date, slot) => {
  return api.post('/charging-sessions/reserve', {
    user_id:    userId,
    pile_id:    pileId,
    vehicle_id: vehicleId,
    date,
    slot,
  })
}

// 取消预约 —— 新增接口
export const cancelSession = (sessionId) => {
  return api.post(`/charging-sessions/${sessionId}/cancel`)
}

// 开始充电
export const startSession = (sessionId) => {
  return api.post(`/charging-sessions/${sessionId}/start`)
}

// 停止充电
export const stopSession = (sessionId) => {
  return api.post(`/charging-sessions/${sessionId}/stop`)
}

export const getMyReservations = (userId) =>
  api.get(`/charging-sessions/user/${userId}`)
