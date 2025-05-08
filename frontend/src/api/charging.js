import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

// 获取所有充电区
export const getLocations = () => api.get('/charging_area/get_charging_areas')

// 获取某个充电区下的充电桩
export const getChargingPiles = (locationId) =>
  api.get('/charging-piles', { params: { location_id: locationId } })

// 获取某桩当日时段状态，date: "YYYY-MM-DD"，userId 可选，用于标记“mine”
export const getPileSlots = (pileId, date, userId = null) =>
  api.get(`/charging-piles/${pileId}/slots`, { params: { date, user_id: userId } })

// 预约充电桩 —— 旧的单时段接口（按 slot 拆分），如仍需使用可保留：
// export const reserveSession = (userId, pileId, vehicleId, date, slot) =>
//   api.post('/charging-sessions/reserve', {
//     user_id:    userId,
//     pile_id:    pileId,
//     vehicle_id: vehicleId,
//     date,
//     slot,
//   })

// 预约充电桩 —— 新增完整区间接口，传 start_time 和 end_time
export const reserveSessionRange = (
  userId,
  pileId,
  vehicleId,
  date,
  startTime,
  endTime
) =>
  api.post('/charging-sessions/reserve', {
    user_id:    userId,
    pile_id:    pileId,
    vehicle_id: vehicleId,
    date,
    start_time: startTime,
    end_time:   endTime,
  })

// 取消预约
export const cancelSession = (sessionId) =>
  api.post(`/charging-sessions/${sessionId}/cancel`)

// 开始充电
export const startSession = (sessionId) =>
  api.post(`/charging-sessions/${sessionId}/start`)

// 停止充电
export const stopSession = (sessionId) =>
  api.post(`/charging-sessions/${sessionId}/stop`)

// 获取我的所有预约
export const getMyReservations = (userId) =>
  api.get(`/charging-sessions/user/${userId}`)
