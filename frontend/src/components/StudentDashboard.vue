<template>
  <div class="student-dashboard">
    <div class="header">
      <h1>校园电瓶车管理系统</h1>
      <button class="secondary" @click="logout">退出登录</button>
    </div>

    <div class="dashboard-content">
      <div class="sidebar">
        <ul>
          <!-- 公共菜单项 -->
          <li v-if="!isAdmin" @click="navigate('personalInfo')">个人信息</li>
          <li v-if="!isAdmin" @click="navigate('vehicleManagement')">
            电动车管理
          </li>
          <li v-if="!isAdmin" @click="navigate('mapNavigation')">地图导航</li>
          <li v-if="isStudentOrStaff" @click="navigate('parkingManagement')">
            停车场管理
          </li>
          <li v-if="isStudentOrStaff" @click="navigate('scoreManagement')">
            积分管理
          </li>
          <li v-if="!isAdmin" @click="navigate('notifications')">通知</li>

          <!-- 管理员菜单项 -->
          <li v-if="isAdmin" @click="navigate('adminDashboard')">系统管理</li>
        </ul>
      </div>

      <div class="main-content">
        <div v-if="activePage === 'personalInfo'" class="section">
          <h2>个人信息管理</h2>
          <div v-if="user">
            <div><strong>姓名：</strong>{{ user.name }}</div>
            <div><strong>学号：</strong>{{ user.school_id }}</div>
            <div><strong>角色：</strong>{{ user.role }}</div>
            <div><strong>电话：</strong>{{ user.phone }}</div>
            <div>
              <strong>车牌：</strong>{{ user.plate_number || "未绑定" }}
            </div>
          </div>
          <div v-else>
            <p>正在加载您的信息...</p>
          </div>
        </div>

        <!-- 电动车管理页面 -->
        <div v-if="activePage === 'vehicleManagement'" class="section">
          <h2 style="color: black; font-weight: bold">电动车管理</h2>

          <!-- 如果已绑定电动车 -->
          <div v-if="vehicle && Object.keys(vehicle).length > 0">
            <div class="vehicle-info-container">
              <h3 class="vehicle-title">我的电动车</h3>
              <div class="vehicle-info-item">
                <strong>车牌号:</strong> {{ vehicle.plate_number }}
              </div>
              <div class="vehicle-info-item">
                <strong>车辆ID:</strong> {{ vehicle.vehicle_id }}
              </div>
              <div class="vehicle-info-item">
                <strong>品牌:</strong> {{ vehicle.brand }}
              </div>
              <div class="vehicle-info-item">
                <strong>颜色:</strong> {{ vehicle.color }}
              </div>
              <div class="vehicle-info-item">
                <strong>型号:</strong> {{ vehicle.model }}
              </div>
              <div class="vehicle-info-item">
                <strong>电池容量:</strong> {{ vehicle.battery_capacity }}
              </div>
            </div>

            <div style="margin-top: 40px"></div>
            <!-- 添加间距 -->

            <div class="button-container">
              <button class="secondary" @click="unbindVehicle">
                解绑电动车
              </button>
              <button @click="showUpdateForm = true">更新电动车信息</button>
              <!-- 点击显示表单 -->
            </div>

            <div style="margin-top: 40px"></div>
            <!-- 添加间距 -->

            <div class="update-form" v-if="showUpdateForm">
              <h3>更新电动车信息</h3>
              <div class="form-grid">
                <label>车牌号:</label>
                <input
                  v-model="updateData.plate_number"
                  type="text"
                  placeholder="请输入新车牌号"
                />

                <label>品牌:</label>
                <input
                  v-model="updateData.brand"
                  type="text"
                  placeholder="请输入新品牌"
                />

                <label>颜色:</label>
                <input
                  v-model="updateData.color"
                  type="text"
                  placeholder="请输入新颜色"
                />

                <label>型号:</label>
                <input
                  v-model="updateData.model"
                  type="text"
                  placeholder="请输入新型号"
                />

                <label>电池容量:</label>
                <input
                  v-model="updateData.battery_capacity"
                  type="number"
                  placeholder="请输入新电池容量"
                />
              </div>
              <div style="margin-top: 40px"></div>
              <!-- 添加间距 -->

              <div class="button-container">
                <button class="primary" @click="updateVehicle">提交更新</button>
                <button class="secondary" @click="showUpdateForm = false">
                  取消
                </button>
              </div>
            </div>
          </div>
          <!-- 如果未绑定电动车 -->
          <div v-else>
            <p style="color: red; font-weight: bold">你还没有绑定电动车！</p>
            <button @click="showBindForm = true">绑定电动车</button>
          </div>

          <div v-if="successMessage" class="success-alert">
            {{ successMessage }}
          </div>

          <!-- 绑定电动车的表单 -->
          <div v-if="showBindForm" class="bind-form">
            <h3>绑定电动车</h3>
            <label>车牌号:</label>
            <input
              v-model="vehicleData.plate_number"
              type="text"
              placeholder="请输入车牌号"
            />

            <label>品牌:</label>
            <input
              v-model="vehicleData.brand"
              type="text"
              placeholder="请输入品牌"
            />

            <label>车型:</label>
            <input
              v-model="vehicleData.model"
              type="text"
              placeholder="请输入车型"
            />

            <label>颜色:</label>
            <input
              v-model="vehicleData.color"
              type="text"
              placeholder="请输入颜色（可选）"
            />

            <label>电池容量:</label>
            <input
              v-model="vehicleData.battery_capacity"
              type="number"
              placeholder="请输入电池容量（可选）"
            />

            <button @click="submitBindVehicle">确认绑定</button>
            <button @click="showBindForm = false">取消</button>
          </div>
        </div>

        <div v-if="activePage === 'mapNavigation'" class="section">
          <h2>地图导航</h2>
          <p>显示导航功能和路径规划。</p>
        </div>

        <div v-if="activePage === 'parkingManagement'" class="section">
          <h2>停车场管理</h2>
          <p>展示停车场实时车位状态及车位预约系统。</p>
        </div>

        <div
          v-if="activePage === 'scoreManagement' && isStudentOrStaff"
          class="section"
        >
          <h2>积分管理</h2>
          <p>展示违规积分及积分扣除规则。</p>
        </div>

        <div v-if="activePage === 'notifications'" class="section">
          <h2>通知模块</h2>
          <p>展示用户的通知信息，推送系统通知等。</p>
        </div>

        <!-- 系统管理页面（仅管理员可见） -->
        <div v-if="activePage === 'adminDashboard' && isAdmin">
          <AdminDashboard />
          <h2>系统管理模块</h2>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from "vue"; // 导入 ref
import { useRouter } from "vue-router"; // 导入 useRouter
import { useAuthStore } from "../store/auth"; // 导入 auth store（假设使用 Pinia）
import { useVehicleStore } from "../store/vehicleService"; // 引入车辆管理 store

export default {
  setup() {
    const router = useRouter(); // 获取路由对象
    const authStore = useAuthStore(); // 获取 auth store（用于管理认证状态）
    const vehicleStore = useVehicleStore(); // 获取 Pinia 车辆 store
    const successMessage = ref(""); // 用于显示成功提示
    const userRole = computed(() => {
      return authStore.user.value?.role ?? "guest"; // 使用可选链操作符和默认值
    });
    const isAdmin = computed(() => userRole.value === "admin");
    const isStaff = computed(() => userRole.value === "staff");
    const isVisitor = computed(() => userRole.value === "visitor");
    const isStudent = computed(() => userRole.value === "student");
    const isStudentOrStaff = computed(() =>
      ["student", "staff"].includes(userRole.value)
    );

    // 定义 activePage 为响应式变量
    const activePage = ref("personalInfo"); // 默认页面是个人信息

    const showBindForm = ref(false); // 控制绑定表单显示
    const showUpdateForm = ref(false); // 控制更新表单的显示
    const vehicleData = ref({
      plate_number: "",
      brand: "",
      model: "",
      color: "",
      battery_capacity: null,
    });

    const updateData = ref({
      brand: "",
      color: "",
      model: "",
      plate_number: "",
    });

    const logout = () => {
      console.log("退出登录方法开始执行");

      // 调用 Pinia store 的 logout 方法
      authStore.logout();

      vehicleStore.vehicle = {}; // 重置车辆状态

      // 跳转到登录页面
      router.replace("/login"); // 使用 replace，避免后退返回仪表盘
      console.log("跳转到登录页面");
    };

    const navigate = (page) => {
      // 动态切换显示的页面
      activePage.value = page; // 使用 ref 的 value 来更新 activePage
    };

    const user = computed(() => authStore.user); // 获取用户信息

    // 页面加载时获取用户信息
    onMounted(() => {
      if (!user.value?.name) {
        // 如果没有用户信息
        authStore.fetchUserInfo(); // 请求并更新用户信息
      }
    });

    const vehicle = computed(() => vehicleStore.vehicle);

    const submitBindVehicle = async () => {
      console.log("提交绑定数据:", vehicleData.value);

      try {
        await vehicleStore.bindVehicleHandler(vehicleData.value);
        console.log("电动车绑定成功");

        showBindForm.value = false; // 关闭表单
        await vehicleStore.fetchMyVehicle(); // 重新获取绑定信息
        // 现在打印 vehicleStore.vehicle 应该有数据了
        console.log("最新的电动车数据:", vehicleStore.vehicle);
      } catch (error) {
        console.error("电动车绑定失败", error.response?.data || error);
        alert("绑定失败，请检查输入信息是否正确！");
      }
    };

    // 解绑电动车
    const unbindVehicle = async () => {
      if (vehicleStore.vehicle) {
        try {
          await vehicleStore.unbindVehicleHandler(
            vehicleStore.vehicle.vehicle_id
          );
          successMessage.value = "解绑成功！"; // 显示成功提示
          // 可选：2秒后自动消失
          setTimeout(() => {
            successMessage.value = "";
          }, 2000);
        } catch (error) {
          console.error("解绑失败:", error);
          alert("解绑失败，请重试。");
        }
      }
    };

    // 更新电动车信息
    const updateVehicle = async () => {
      if (vehicleStore.vehicle) {
        const vehicleId = vehicleStore.vehicle.vehicle_id;
        const updates = {
          plate_number: updateData.value.plate_number,
          brand: updateData.value.brand,
          color: updateData.value.color,
          model: updateData.value.model,
          battery_capacity: updateData.value.battery_capacity,
        };
        try {
          await vehicleStore.updateVehicleHandler(vehicleId, updates);
          // 隐藏表单并重置数据
          showUpdateForm.value = false;
          updateData.value = {
            plate_number: "",
            brand: "",
            color: "",
            model: "",
            battery_capacity: null,
          };
          alert("更新成功！");
        } catch (error) {
          console.error("更新失败:", error.response?.data?.msg || error);
          alert("更新失败，请检查输入信息！");
        }
      }
    };
    // 组件加载时获取电动车信息
    onMounted(() => {
      console.log("组件已挂载，正在获取车辆信息..."); // 新增日志
      vehicleStore.fetchMyVehicle();
    });

    return {
      activePage,
      logout,
      navigate,
      vehicle,
      vehicleStore,
      showBindForm,
      vehicleData,
      submitBindVehicle,
      unbindVehicle,
      updateVehicle,
      updateData,
      showUpdateForm,
      successMessage,
      isAdmin,
      isStaff,
      isVisitor,
      isStudent,
      isStudentOrStaff,
      user,
    };
  },
};
</script>

<style scoped>
.student-dashboard {
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

.vehicle-info-container {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 10px;
  margin-bottom: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  max-width: 500px;
  margin: 0 auto;
}
.vehicle-title {
  margin-bottom: 15px;
  color: #333;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.vehicle-info-item {
  text-align: center;
  font-size: 16px;
  border-bottom: 1px solid #eee; /* 分割线 */
}

/* 包裹按钮的容器 */
.button-container {
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
  gap: 40px; /* 按钮之间的间距 */
}

/* 按钮样式 */
button {
  padding: 10px 20px;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
  font-size: 16px;
}

button.primary {
  background-color: #007bff;
  color: white;
}

button.secondary {
  background-color: #dc3545;
  color: white;
}

button:hover {
  background-color: darken(currentColor, 20%);
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

/* 绑定表单样式 */
.bind-form {
  position: fixed; /* 固定位置 */
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%); /* 让元素居中 */
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 90%; /* 适配小屏幕 */
  z-index: 1000; /* 确保在最上层 */
}

.bind-form h3 {
  margin-bottom: 10px;
}

.bind-form label {
  display: block;
  margin-top: 10px;
}

.bind-form input {
  width: 100%;
  padding: 8px;
  margin-top: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.bind-form button {
  margin-top: 10px;
  padding: 8px 15px;
  border: none;
  background-color: #28a745;
  color: white;
  border-radius: 4px;
  cursor: pointer;
}

.bind-form button:hover {
  background-color: #218838;
}

.bind-form button:last-child {
  background-color: #dc3545;
}

.bind-form button:last-child:hover {
  background-color: #c82333;
}

.update-form {
  margin-top: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px; /* 元素之间的间距 */
  align-items: center;
}

.button-container {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.success-alert {
  position: fixed; /* 固定定位 */
  top: 50%; /* 垂直方向居中 */
  left: 50%; /* 水平方向居中 */
  transform: translate(-50%, -50%); /* 精确居中 */
  padding: 20px 40px; /* 增大内边距 */
  background-color: #4caf50;
  color: white;
  border-radius: 12px; /* 边框圆角 */
  font-size: 20px; /* 字体放大 */
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.2); /* 阴影效果 */
  text-align: center; /* 文字居中 */
  max-width: 400px; /* 最大宽度 */
  z-index: 1000; /* 确保在最上层 */
}
</style>
