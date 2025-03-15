import { defineStore } from 'pinia';
import api from '../api/auth';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || '',
  }),
  
  actions: {
    async login(username, password) {
      try {
        const response = await api.post('/login', { username, password });
        this.user = response.data.data.user_info;
        this.token = response.data.data.access_token;
        localStorage.setItem('token', this.token);
        return true;
      } catch (error) {
        console.error('登录失败:', error.response.data.msg);
        return false;
      }
    },

    async register(userData) {
      try {
        const response = await api.post('/register', userData);
        return response.data;
      } catch (error) {
        console.error('注册失败:', error.response.data);
        return false;
      }
    },

    logout() {
      this.user = null;
      this.token = '';
      localStorage.removeItem('token');
    },
  },
});