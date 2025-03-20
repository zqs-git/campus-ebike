<template>
  <div class="admin-dashboard">
    <div class="header">
      <h1>校园电瓶车管理系统后台</h1>
      <button @click="logout">退出登录</button>
    </div>

    <div class="dashboard-content">
      <div class="sidebar">
        <ul>
          <!-- 系统仪表盘 -->
          <li @click="navigate('systemDashboard')">系统仪表盘</li>

          <!-- 用户管理 -->
          <li @click="navigate('userManagement')">用户管理</li>

          <!-- 车辆管理 -->
          <li @click="navigate('vehicleManagement')">电动车管理</li>

          <!-- 停车场管理 -->
          <li @click="navigate('parkingManagement')">停车场管理</li>

          <!-- 积分管理 -->
          <li @click="navigate('scoreManagement')">积分管理</li>

          <!-- 系统设置 -->
          <li @click="navigate('systemSettings')">系统设置</li>

          <!-- 通知管理 -->
          <li @click="navigate('notifications')">通知管理</li>
        </ul>
      </div>

      <div class="main-content">
        <!-- 系统仪表盘 -->
        <div v-if="activePage === 'systemDashboard'" class="section">
          <h2>系统仪表盘</h2>
          <div class="dashboard-widgets">
            <div class="widget">
              <h3>车辆总数统计</h3>
              <p>数据展示区域</p>
            </div>
            <div class="widget">
              <h3>停车场使用率</h3>
              <p>数据展示区域</p>
            </div>
            <div class="widget">
              <h3>违规记录统计</h3>
              <p>数据展示区域</p>
            </div>
          </div>
        </div>

        <!-- 用户管理 -->
        <div v-if="activePage === 'userManagement'" class="section">
          <h2>用户管理</h2>
          <div class="user-management">
            <div class="user-list">
              <h3>用户列表</h3>
              <div class="user-filter">
                <select>
                  <option>学生</option>
                  <option>教职工</option>
                  <option>访客</option>
                </select>
              </div>
              <table class="user-table">
                <thead>
                  <tr>
                    <th>用户名</th>
                    <th>角色</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>示例用户</td>
                    <td>管理员</td>
                    <td>编辑/删除</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="role-management">
              <h3>角色分配</h3>
              <p>角色分配功能区域</p>
            </div>
            <div class="blacklist-management">
              <h3>黑名单管理</h3>
              <p>黑名单管理功能区域</p>
            </div>
          </div>
        </div>

        <!-- 车辆管理 -->
        <div v-if="activePage === 'vehicleManagement'" class="section">
          <h2>电动车管理</h2>
          <div class="vehicle-management">
            <div class="vehicle-list">
              <h3 class="left-aligned">所有车辆信息列表</h3>
              <table class="vehicle-table">
                <thead>
                  <tr>
                    <th>车牌号</th>
                    <th>车主</th>
                    <th>状态</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="vehicle in allVehicles" :key="vehicle.vehicle_id">
                    <td>{{ vehicle.plate_number }}</td>
                    <td>{{ vehicle.owner_id }}</td>
                    <td>{{ vehicle.status }}</td>
                    <td>
                      <button @click="handleEdit(vehicle)">编辑</button>
                      <button
                        @click="handleDelete(vehicle.vehicle_id)"
                        class="danger"
                      >
                        删除
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="binding-audit">
              <h3>车辆绑定审核</h3>
              <p>审核功能区域</p>
            </div>
            <div class="force-unbind">
              <h3>强制解绑</h3>
              <p>解绑操作区域</p>
            </div>
          </div>
        </div>

        <!-- 停车场管理 -->
        <div v-if="activePage === 'parkingManagement'" class="section">
          <h2>停车场管理</h2>
          <div class="parking-management">
            <div class="parking-configuration">
              <h3>车位配置</h3>
              <p>车位配置功能区域</p>
            </div>
            <div class="parking-violation">
              <h3>违规停车处理</h3>
              <p>违规处理区域</p>
            </div>
            <div class="export-data">
              <h3>数据导出</h3>
              <button>导出为Excel</button>
              <button>导出为CSV</button>
            </div>
          </div>
        </div>

        <!-- 积分管理 -->
        <div v-if="activePage === 'scoreManagement'" class="section">
          <h2>积分管理</h2>
          <div class="score-management">
            <div class="score-rules">
              <h3>积分规则设置</h3>
              <p>规则配置区域</p>
            </div>
            <div class="score-adjustment">
              <h3>手动扣分/加分</h3>
              <p>积分调整功能区域</p>
            </div>
            <div class="violation-review">
              <h3>违规记录审核</h3>
              <p>审核功能区域</p>
            </div>
          </div>
        </div>

        <!-- 系统设置 -->
        <div v-if="activePage === 'systemSettings'" class="section">
          <h2>系统设置</h2>
          <div class="system-settings">
            <div class="token-settings">
              <h3>Token 过期时间配置</h3>
              <input type="number" placeholder="访问令牌过期时间（小时）" />
              <input type="number" placeholder="刷新令牌过期时间（天）" />
              <button>保存设置</button>
            </div>
            <div class="notification-templates">
              <h3>通知模板管理</h3>
              <p>模板管理功能区域</p>
            </div>
          </div>
        </div>

        <!-- 通知管理 -->
        <div v-if="activePage === 'notifications'" class="section">
          <h2>通知管理</h2>
          <div class="notification-management">
            <div class="system-notifications">
              <h3>系统通知推送</h3>
              <p>通知推送功能区域</p>
            </div>
            <div class="violation-notifications">
              <h3>违规通知发送</h3>
              <p>违规通知功能区域</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../store/auth"; // 验证管理员权限
import { useVehicleStore } from "../store/vehicleService";

export default {
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const vehicleStore = useVehicleStore();
    const allVehicles = computed(() => vehicleStore.allVehicles);

    onMounted(async () => {
      try {
        // 权限二次验证（确保是管理员）
        if (authStore.user?.role !== "admin") {
          alert("无权限访问该功能");
          return;
        }

        await vehicleStore.fetchAllVehicles(); // 调用新方法获取数据
      } catch (error) {
        console.error("加载车辆列表失败:", error);
        alert("加载车辆列表失败，请重试");
      }
    });

    // 主动修改默认页面为系统仪表盘
    const activePage = ref("systemDashboard");

    const logout = () => {
      authStore.logout();
      router.replace("/login");
    };

    const navigate = (page) => {
      activePage.value = page;
    };

    return {
      activePage,
      logout,
      navigate,
      allVehicles,
    };
  },
};
</script>

<style scoped>
/* 完全保留原有样式，仅新增结构所需的样式 */
.dashboard-widgets {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  justify-content: space-between;
}

.widget {
  flex: 1 1 30%;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-management {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

.user-table th {
  background-color: #f8f9fa;
  font-weight: bold;
}

.user-table tr:hover {
  background-color: #f1f3f5;
}

.vehicle-management {
  display: flex;
  flex-direction: column;
  text-align: left;
  gap: 20px;
}

/* 车辆表格优化 */
.vehicle-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

.vehicle-table th,
.vehicle-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.vehicle-table th {
  background-color: #f8f9fa;
  font-weight: bold;
}

.vehicle-table tr:hover {
  background-color: #f1f3f5;
}

.parking-management {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.system-settings {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.notification-management {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

/* 保留原有按钮样式 */
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

/* 保持原有布局样式 */
.admin-dashboard {
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

.sidebar li {
  padding: 12px 16px; /* 增大内边距 */
  font-size: 16px;
  border-radius: 4px;
}

.sidebar li:hover {
  background-color: #343a40; /* 更柔和的悬浮色 */
  color: white;
}

.main-content {
  flex: 1;
  padding: 20px;
  background-color: #f8f9fa;
  overflow-y: auto;
}

/* 卡片式容器 */
.section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.section h2 {
  color: #333;
}

.section p {
  color: #777;
  font-size: 16px;
}

/* 标题样式 */
h2 {
  color: #212529;
  font-weight: 600;
  margin-bottom: 15px;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 10px;
}
</style>
