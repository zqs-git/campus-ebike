import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api/auth', // Flask 后端 URL
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
