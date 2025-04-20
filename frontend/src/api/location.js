import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api/location',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 增强的请求拦截器
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  const userId = localStorage.getItem('userId');

  console.log('token:', token);
  console.log('userId:', userId);

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    config.headers['X-User-ID'] = userId;
  }
  return config;
});

// 统一的响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    const errorMessage = error.response?.data?.message || 
                        error.message || 
                        '请求失败，请检查网络连接';
    return Promise.reject(new Error(errorMessage));
  }
);

// 获取所有地点
export const getLocations = async () => {
  return api.get('/get_location');
};

// 获取单个地点
export const getLocation = async (locationId) => {
  return api.get(`/get_location/${locationId}`);
};

// 创建地点
export const addLocation = async (data) => {
  return api.post('/add_location', {
    name: data.name,
    latitude: data.latitude,
    longitude: data.longitude,
    location_type: data.locationType,
    description: data.description
  });
};

// 更新地点
export const updateLocation = async (locationId, data) => {
  try {
    const response = await api.put(`/update_location/${locationId}`, {
      name: data.name,
      latitude: data.latitude,
      longitude: data.longitude,
      location_type: data.location_type,
      description: data.description,
    });
    return response;
  } catch (error) {
    console.error('更新地点失败:', error);
    throw error; // 抛出错误，让调用者处理
  }
};


// 删除地点
export const deleteLocation = async (locationId) => {
  return api.delete(`/delete_location/${locationId}`);
};

// 根据地点类型获取地点
export const getLocationsByType = async (locationType) => {
  return api.get(`/get_locations/type/${locationType}`);
};

export default api;
