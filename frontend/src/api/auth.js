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

export default api;
