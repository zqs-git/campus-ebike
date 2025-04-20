import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api/parking',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 增强的请求拦截器
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  const userId = localStorage.getItem('userId');

  console.log('token:', localStorage.getItem('token'));
  console.log('userId:', localStorage.getItem('userId'));

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

// API 方法
export const getParkingLots = async () => {
  return api.get('/parking_lots');
};

export const addParkingLot = async (data) => {
  return api.post('/add_parking_lot', {
    location_id: data.location_id,
    name: data.name,
    capacity: data.capacity
  });
};

export const parkIn = async (parkingdata) => {
  return api.post('/park_in', {
    lot_id: parkingdata.lot_id,
    vehicle_id: parkingdata.vehicle_id,
    user_id: parkingdata.user_id,
  });
};

export const parkOut = async (recordId) => {
  return api.post(`/park_out/${recordId}`);
};

export const getCurrentRecord = async () => {
  return api.get('/current_record');
};

// 更新停车场信息
export const updateParkingLot = async (lotId, data) => {
  return api.put(`/parking_lot/${lotId}`, data);
};

// 删除停车场
export const deleteParkingLot = async (lotId) => {
  return api.delete(`/parking_lot/${lotId}`);
};

// 📌 **修改 getParkingRecords，增加分页参数**
export const getParkingRecords = async ({ keyword = '', page = 1, pageSize = 10 }) => {
  return api.get('/parking_records', {
    params: {
      keyword,  // 车牌号搜索
      page,     // 当前页码
      pageSize  // 每页数量
    }
  });
};

export default api;
