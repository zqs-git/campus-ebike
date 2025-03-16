import { defineStore } from 'pinia';
import api from '../api/auth';
// import axios from 'axios';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || '',
  }),
  
  actions: {
    async login(username, password) {
      try {
        const response = await api.post('/login', { username, password });
        if (!response?.data?.data?.access_token) {
          throw new Error("登录响应格式错误");
        }
    
        // 保存 Token
        const token = response.data.data.access_token;
        localStorage.setItem("token", token);
        this.token = token;
    
        // 必须等待用户信息加载完成
        await this.fetchUserInfo();
    
        // 确保用户信息已存在
        if (!this.user?.role) {
          throw new Error("用户角色未定义");
        }
        return this.user.role;
    
      } catch (error) {
        console.error("Login error:", error.message);
        // this.logout(); // 清除无效 Token
        throw error; // 抛出错误给调用方
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

    async fetchUserInfo() {
      try {
        console.log("开始获取用户信息...");
        if (!this.token) {
          throw new Error("Token 不存在");
        }
        console.log("使用 Token 获取用户信息:", this.token);

        const response = await api.get("/info", {
          headers: { Authorization: `Bearer ${this.token}` }, // 使用 Store 的 Token
          timeout: 20000, // 单独为这个请求设置 20 秒超时
        });

        console.log("获取到的用户信息:", response.data);
    
        // 验证数据结构
        if (!response?.data?.data) {
          throw new Error("用户信息格式错误");
        }
    
        this.user = response.data.data;
        console.log("用户信息加载完成:", this.user);
    
      } catch (error) {
        console.error("获取用户信息失败:", error.message);
        console.error("详细错误信息:", error);
        if (error.response?.status === 401) {
          this.logout(); // Token 失效时清除状态
        }
        throw error; // 允许外层处理
      }
    }
    
    
  },
});