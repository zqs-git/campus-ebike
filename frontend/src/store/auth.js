import { defineStore } from 'pinia';
import api from '../api/auth';
import { ref } from 'vue';
import { getAllUsers } from '../api/auth'; // 新增导入
import { getVisitorInfo } from '../api/auth'; // ✅ 新增导入
export const useAuthStore = defineStore('auth', {
  state: () => ({
    // 使用 `ref` 来保持响应式，同时从 localStorage 中恢复数据
    user: ref(JSON.parse(localStorage.getItem('user')) || {}),  // 如果 localStorage 中有数据就恢复，没有就设置为空对象
    token: ref(localStorage.getItem('token') || ''),            // 从 localStorage 获取 token
    isAuthenticated: ref(!!localStorage.getItem('token')),       // 如果 token 存在，说明已认证
    role: 'student',                                           // 默认角色为 student
    allUsers: ref([]), // 存储所有用户数据
    visitorInfo: ref(null), // ✅ 新增访客信息字段
  }),

  actions: {
    async login(username, password) {
      try {
        const response = await api.post('/login', { username, password });

        // 检查是否需要更新通行证
        if (response.data.code === 403 && response.data.need_update) {
          // 显示提示信息：通行证已过期
          alert("尚未注册通行证/通行证已过期，请更新通行证");
          this.showUpdateForm(response.data.user_info);  // 展示更新通行证表单
          return { 
            need_update: true, 
            license_plate: response.data.user_info?.license_plate || "" 
          };
        }

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

        // 处理 403 错误并弹出表单
        if (error.response && error.response.status === 403 && error.response.data.need_update) {
          // 显示提示信息：通行证已过期
          alert("尚未注册通行证/通行证已过期，请更新通行证");
          this.showUpdateForm(error.response.data.user_info);  // 展示更新通行证表单
          return { 
            need_update: true,  
          };
        }

        this.logout(); // 避免存储无效 token
        throw error;
      }
    },


    showUpdateForm(userInfo) {
      this.showForm = true;  // 显示弹窗
      this.licensePlate = userInfo.license_plate || '';  // 设置默认车牌号
    },
  
    async updateVisitorPass(visitorUsername,licensePlate) {
      try {

        console.log("更新通行证请求，车牌号:", licensePlate);
        console.log("更新通行证请求，访客用户名:", visitorUsername);
        // console.log("更新通行证请求，访客密码:",visitorPassword);
        const response = await api.post('/updateVisitorPass', {
          username: visitorUsername,  // 传递用户名
          // password: visitorPassword,  // 传递密码
          license_plate:licensePlate
        });

        
  
        // 更新通行证成功后，自动登录并跳转
        if (response.data.success) {
          alert("通行证已更新，请重新登录...");
          // console.log(visitorUsername, visitorPassword);
          // await this.login(visitorUsername, visitorPassword);  // 使用用户的用户名和密码重新登录
        } else {
          console.error("更新通行证失败:", response.data.message);
          // alert("更新通行证失败，请稍后重试");
        }
      } catch (error) {
        console.error("请求发生错误:", error.response || error);  // 输出详细的错误信息
      }
    },

    async fetchVisitorInfo() {
      try {
        const response = await getVisitorInfo();
        this.visitorInfo = response.data; // ✅ 存储访客信息
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

    async fetchAllUsers() {
      try {
        const response = await getAllUsers();
        if (response.code === 200) {
          this.allUsers = response.data; // 更新状态
        } else {
          this.allUsers = [];
          throw new Error(response.msg);
        }
      } catch (error) {
        console.error("获取用户列表失败:", error);
        if (error.response?.status === 401) {
          alert("登录已过期，请重新登录");
          // 跳转登录页
        }
      }
    },
  },
});
