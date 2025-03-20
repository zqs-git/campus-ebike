import axios from 'axios';

// 创建 API 客户端
const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api/vehicle',  // 后端 API 基础 URL
  timeout: 10000,           // 请求超时
});


// 绑定电动车
export const bindVehicle = async (vehicleData) => {
  const token = localStorage.getItem('token');  // 获取存储的 token
  if (!token) throw new Error('未找到有效 token');
  try {
    const response = await apiClient.post('/bind', vehicleData, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    console.error('绑定电动车失败', error);
    throw error;
  }
};

// 获取绑定的电动车
export const getMyVehicle = async () => {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('未找到有效 token');
  try {
    const response = await apiClient.get('/my_vehicle', {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    console.error('获取电动车信息失败', error);
    throw error;
  }
};


// 新增获取所有车辆的方法（管理员接口）
export const getAllVehicles = async () => {
  const token = localStorage.getItem('token'); // 获取存储的 token
  if (!token) throw new Error('未找到有效 token');
  try {
    const response = await apiClient.get('/admin_vehicle', { 
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    console.error('获取所有电动车信息失败', error);
    throw error;
  }
};


// 解绑电动车
export const unbindVehicle = async (vehicleId) => {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('未找到有效 token');
  try {
    const response = await apiClient.post('/unbind', { vehicle_id: vehicleId }, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    console.error('解绑电动车失败', error);
    throw error;
  }
};

// 更新电动车信息
export const updateVehicle = async (vehicleId, updates) => {
  const token = localStorage.getItem('token');
  if (!token) throw new Error('未找到有效 token');
  try {
    const response = await apiClient.put('/update', { vehicle_id: vehicleId, ...updates }, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    console.error('更新电动车信息失败', error);
    throw error;
  }
};
