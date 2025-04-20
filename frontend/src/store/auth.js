import { defineStore } from 'pinia';
import api from '../api/auth';
import { ref } from 'vue';
import { getAllUsers } from '../api/auth'; // 新增导入
import { getVisitorInfo } from '../api/auth'; // 新增导入
import { updateUserInfo } from '../api/auth'; // 新增导入

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: ref(JSON.parse(localStorage.getItem('user')) || {}),
    token: ref(localStorage.getItem('token') || ''),
    isAuthenticated: ref(!!localStorage.getItem('token')),
    role: 'student',
    allUsers: ref([]),
    visitorInfo: ref(null),
    updateError: ref(''),
  }),

  actions: {
    async login(username, password) {
      try {
        const response = await api.post('/login', { username, password });
        if (response.data.code === 403 && response.data.need_update) {
          alert("尚未注册通行证/通行证已过期，请更新通行证");
          this.showUpdateForm(response.data.user_info);
          return { 
            need_update: true, 
            license_plate: response.data.user_info?.license_plate || "" 
          };
        }
        console.log("登录响应:", response?.data);
        if (!response?.data?.data?.access_token) {
          throw new Error("登录响应格式错误");
        }
        const token = response.data.data.access_token;
        localStorage.setItem("token", token);
        this.token = token;
        this.isAuthenticated = true;
        const user = await this.fetchUserInfo();
        console.log("获取到的用户信息:", user);
        if (!user?.role) {
          throw new Error("用户角色未定义");
        }
        localStorage.setItem('user', JSON.stringify(user));
        localStorage.setItem('userId', user.user_id);
        this.user = user;
        return user;
      } catch (error) {
        console.error("登录失败:", error.message);
        if (error.response && error.response.status === 403 && error.response.data.need_update) {
          alert("尚未注册通行证/通行证已过期，请更新通行证");
          this.showUpdateForm(error.response.data.user_info);
          return { need_update: true };
        }
        this.logout();
        throw error;
      }
    },

    showUpdateForm(userInfo) {
      this.showForm = true;
      this.licensePlate = userInfo.license_plate || '';
    },

    async updateVisitorPass(visitorUsername, licensePlate) {
      try {
        console.log("更新通行证请求，车牌号:", licensePlate);
        console.log("更新通行证请求，访客用户名:", visitorUsername);
        const response = await api.post('/updateVisitorPass', {
          username: visitorUsername,
          license_plate: licensePlate
        });
        if (response.data.success) {
          alert("通行证已更新，请重新登录...");
        } else {
          console.error("更新通行证失败:", response.data.message);
        }
      } catch (error) {
        console.error("请求发生错误:", error.response || error);
      }
    },

    async fetchVisitorInfo() {
      try {
        const response = await getVisitorInfo();
        this.visitorInfo = response.data;
      } catch (error) {
        if (error.response?.status === 403) {
          alert("权限不足：仅访客可访问该信息");
        } else {
          console.error("获取访客信息失败:", error);
        }
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

    async updateUser(updatedData) {
      try {
        const result = await updateUserInfo(updatedData);
        if (result && result.code === 200) {
          await this.fetchUserInfo();
          this.updateError = "";
          return { success: true };
        } else {
          const errMsg = result?.msg || "更新失败";
          const detail = result?.detail || "";
          this.updateError = `${errMsg}${detail ? `：${detail}` : ""}`;
          return { success: false, msg: this.updateError };
        }
      } catch (error) {
        console.error("更新用户信息失败：", error);
        this.updateError = "更新失败，请稍后再试！";
        return { success: false, msg: this.updateError };
      }
    },

    // 新增删除用户方法
    async deleteUser(userId) {
      try {
        const response = await api.delete(`/admin/users/${userId}`);
        const result = response.data;
        if (result.code === 200) {
          await this.fetchAllUsers();
          return { success: true };
        } else {
          throw new Error(result.msg || "删除失败");
        }
      } catch (error) {
        console.error("删除用户失败:", error);
        throw error;
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
        console.log("用户信息响应:", response?.data);
        if (!response?.data?.data) {
          throw new Error("用户信息格式错误");
        }
        this.user = response.data.data;
        localStorage.setItem('user', JSON.stringify(this.user));
        return this.user;
      } catch (error) {
        console.error("获取用户信息失败:", error.message);
        if (error.response?.status === 401) {
          this.logout();
        }
        throw error;
      }
    },

    async fetchAllUsers() {
      try {
        const response = await getAllUsers();
        if (response.code === 200 && Array.isArray(response.data)) {
          // 过滤掉无效的用户对象
          this.allUsers = response.data.filter(user => user && user.user_id);
        } else {
          this.allUsers = [];
          throw new Error(response.msg);
        }
      } catch (error) {
        console.error("获取用户列表失败:", error);
        if (error.response?.status === 401) {
          alert("登录已过期，请重新登录");
        }
      }
    }
    
    
  },
});
