import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api/auth', // Flask 后端 URL
  timeout: 10000,
  // withCredentials: true, // 允许发送 cookies 和 token
  headers: {
    'Content-Type': 'application/json',
  },
});

// 拦截请求，自动加上 Authorization 头
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getAllUsers = async () => {
  // 直接返回 Promise，错误由调用方处理
  return api.get('/admin_users').then(response => response.data);
};

export const getVisitorInfo = async () => {
    return api.get('/getVisitorInfo').then(response => response.data);
};

// // 更新用户信息请求方法
// export function updateUserInfo(data) {
//   return api.put('/info/update', data, {
//     headers: {
//       Authorization: `Bearer ${localStorage.getItem('token')}`  // 携带 token
//     }
//   });
// }

export const updateUserInfo = async (data) => {
  try {
    const response = await api.put('/info/update', data);
    return response.data;
  } catch (error) {
    // 打印详细错误信息，方便调试
    console.error("更新个人信息 API 错误:", error);

    // 提取后端返回的错误信息
    const errData = error.response?.data;

    // 返回结构化的错误，调用方可使用 err.msg 显示错误信息
    return {
      code: errData?.code || 500,
      msg: errData?.msg || "更新失败，请稍后再试！",
      detail: errData?.detail || error.message
    };
  }
};


export default api;
