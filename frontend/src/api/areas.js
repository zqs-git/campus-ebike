import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api/areas',  // 后端的 API 地址
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 获取所有区域
export const getAreas = () => {
  return api.get('')  // 获取所有区域，响应返回一个数组
}

// 创建新区域
export const createArea = (area) => {
  return api.post('', area)  // 提交新区域数据，返回区域的 id
}

// 更新区域
export const updateArea = (areaId, areaData) => {
  return api.put(`/${areaId}`, areaData)  // 更新指定区域的数据
}

// 删除区域
export const deleteArea = (areaId) => {
  return api.delete(`/${areaId}`)  // 删除指定区域
}
