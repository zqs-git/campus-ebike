import { defineStore } from 'pinia';
import api from '../api/auth';
import { ref } from 'vue';
export const useAuthStore = defineStore('auth', {
  state: () => ({
    // 使用 `ref` 来保持响应式，同时从 localStorage 中恢复数据
    user: ref(JSON.parse(localStorage.getItem('user')) || {}),  // 如果 localStorage 中有数据就恢复，没有就设置为空对象
    token: ref(localStorage.getItem('token') || ''),            // 从 localStorage 获取 token
    isAuthenticated: ref(!!localStorage.getItem('token')),       // 如果 token 存在，说明已认证
    role: 'student',                                           // 默认角色为 student
  }),

  actions: {
    async login(username, password) {
      try {
        const response = await api.post('/login', { username, password });
    
        console.log("登录响应:", response?.data);  // 添加日志，检查返回的数据
    
        if (!response?.data?.data?.access_token) {
          throw new Error("登录响应格式错误");
        }
    
        // 保存 Token
        const token = response.data.data.access_token;
        localStorage.setItem("token", token);
        this.token = token;
    
        // 更新认证状态
        this.isAuthenticated = true;
    
        // 获取用户信息
        const user = await this.fetchUserInfo();
        console.log("获取到的用户信息:", user); // 添加日志，检查用户信息
    
        // 确保用户信息有效
        if (!user?.role) {
          throw new Error("用户角色未定义");
        }
    
        // 将用户信息存入本地存储
        localStorage.setItem('user', JSON.stringify(user));
    
        // 更新用户信息
        this.user = user;
    
        return user; // 登录成功后返回角色
    
      } catch (error) {
        console.error("登录失败:", error.message);
        this.logout(); // 避免存储无效 token
        throw error;
      }
    },

    async register(userData) {
      try {
        const response = await api.post('/register', userData);
        return response.data;
      } catch (error) {
        console.error('注册失败:', error.response?.data || error.message);
        return false;
      }
    },

    logout() {
      console.log("退出登录方法开始执行");
    
      this.user = {};
      this.token = '';
      this.isAuthenticated = false;
      console.log("清除用户信息和认证状态");
    
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      console.log("从 localStorage 中移除 token 和 user");
    },

    async fetchUserInfo() {
      try {
        if (!this.token) {
          throw new Error("未找到 Token，请重新登录");
        }

        const response = await api.get("/info", {
          headers: { Authorization: `Bearer ${this.token}` },
          timeout: 20000,
        });

        console.log("用户信息响应:", response?.data); // 添加日志，检查返回的用户信息

        if (!response?.data?.data) {
          throw new Error("用户信息格式错误");
        }

        this.user = response.data.data;

        // 缓存用户信息到 localStorage
        localStorage.setItem('user', JSON.stringify(this.user));

        return this.user;

      } catch (error) {
        console.error("获取用户信息失败:", error.message);
        if (error.response?.status === 401) {
          this.logout(); // 401 代表 token 失效，清除状态
        }
        throw error;
      }
    },
  },
});
