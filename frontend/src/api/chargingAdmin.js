// src/api/adminCharging.js
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000
})

// ---- 充电区管理 ----
export const fetchAreas = () => api.get('/charging_area/get_charging_areas')
export const createArea = (area) => api.post('/charging_area/create', area)
export const updateArea = (id, area) => api.put(`/charging_area/${id}/update`, area)
export const deleteArea = (id) => api.delete(`/charging_area/${id}/delete`)

// ---- 充电桩管理 ----
export const fetchPilesByArea = (areaId) =>
  api.get('/charging-piles', { params: { location_id: areaId } })

export const createPile = (areaId, pile) =>
  api.post(`/charging-piles`, { ...pile, location_id: areaId })

export const updatePile = (id, pile) =>
  api.put(`/charging-piles/${id}`, pile)

export const deletePile = (id) =>
  api.delete(`/charging-piles/${id}`)

// ---- 充电日志 ----
export const fetchChargingLogs = () => api.get('/charging-logs') // 自行实现后端路由
