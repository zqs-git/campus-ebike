<template>
  <div class="visitor-dashboard">
    <div class="header">
      <h1>校园电瓶车管理系统</h1>
      <button @click="logout">退出登录</button>
    </div>

    <div class="dashboard-content">
      <div class="sidebar">
        <ul>
          <li @click="navigate('visitorInfo')">访客信息</li>
          <li @click="navigate('vehicleManagement')">电动车管理</li>
          <li @click="navigate('parkingManagement')">停车场管理</li>
          <li @click="navigate('notifications')">通知</li>
        </ul>
      </div>

      <div class="main-content">
        <div v-if="activePage === 'visitorInfo'" class="section">
          <h2>访客信息管理</h2>
          <p>展示访客的基本信息：姓名、身份证号、访客事由等。</p>
        </div>

        <div v-if="activePage === 'vehicleManagement'" class="section">
          <h2>电动车管理</h2>
          <p>展示临时借用的电动车信息。</p>
        </div>

        <div v-if="activePage === 'parkingManagement'" class="section">
          <h2>停车场管理</h2>
          <p>展示停车场车位状态及车位预约。</p>
        </div>

        <div v-if="activePage === 'notifications'" class="section">
          <h2>通知模块</h2>
          <p>展示访客的相关通知。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from "vue"; // 导入 ref
import { useRouter } from "vue-router"; // 导入 useRouter
import { useAuthStore } from "../store/auth"; // 导入 auth store

export default {
  setup() {
    const router = useRouter(); // 获取路由对象
    const authStore = useAuthStore(); // 获取 auth store

    // 定义 activePage 为响应式变量
    const activePage = ref("visitorInfo"); // 默认页面是访客信息

    const logout = () => {
      console.log("退出登录方法开始执行");

      // 调用 Pinia store 的 logout 方法
      authStore.logout();

      // 跳转到登录页面
      router.replace("/login"); // 使用 replace，避免后退返回仪表盘
      console.log("跳转到登录页面");
    };

    const navigate = (page) => {
      // 动态切换显示的页面
      activePage.value = page; // 使用 ref 的 value 来更新 activePage
    };

    return { activePage, logout, navigate };
  },
};
</script>

<style scoped>
.visitor-dashboard {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f4f4f4;
}

.header {
  background-color: #3a3a3a;
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

button {
  background-color: #ff4d4d;
  color: white;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  border-radius: 5px;
}

button:hover {
  background-color: #ff1a1a;
}

.dashboard-content {
  display: flex;
  height: calc(100vh - 80px);
}

.sidebar {
  width: 200px;
  background-color: #2d2d2d;
  color: white;
  padding-top: 20px;
}

.sidebar ul {
  list-style-type: none;
  padding: 0;
}

.sidebar li {
  padding: 15px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.sidebar li:hover {
  background-color: #ff4d4d;
}

.main-content {
  flex: 1;
  padding: 20px;
  background-color: white;
  overflow-y: auto;
}

h2 {
  color: #333;
}

.section {
  margin-bottom: 30px;
}

.section p {
  color: #777;
  font-size: 16px;
}
</style>
