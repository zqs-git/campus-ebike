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
          <li @click="navigate('parkingManagement')">停车场充电区管理</li>
          <!-- 积分管理 -->
          <li @click="navigate('scoreManagement')">积分管理</li>
          <!-- 通知管理 -->
          <li @click="navigate('notifications')">通知管理</li>
          <!-- 系统设置 -->
          <li @click="navigate('systemSettings')">系统设置</li>
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
              <h3>充电桩使用数据</h3>
              <p>数据展示区域</p>
            </div>
            <div class="widget">
              <h3>违规记录统计</h3>
              <p>数据展示区域</p>
            </div>
            <div class="widget">
              <h3>访客记录统计</h3>
              <p>数据展示区域</p>
            </div>
          </div>
        </div>

        <!-- 用户管理模块 -->
        <div v-if="activePage === 'userManagement'" class="section">
          <h2>用户管理</h2>
          <!-- 搜索输入框 -->
          <div class="search-box">
            <input type="text" v-model="searchText" placeholder="搜索用户名、手机号、学工号或车牌号" />
          </div>
          <div class="user-management">
            <div class="user-list">
              <h3>用户列表</h3>
              <table class="user-table">
                <thead>
                  <tr>
                    <th>用户ID</th>
                    <th>用户名</th>
                    <th>角色</th>
                    <th>手机号</th>
                    <th>车牌号</th>
                    <th>学工号</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <!-- 1. 加载中 -->
                  <template v-if="isLoading">
                    <tr class="loading-state">
                      <td colspan="6">
                        <div class="spinner"></div> 数据加载中...
                      </td>
                    </tr>
                  </template>

                  <!-- 2. 无数据 -->
                  <template v-else-if="!filteredUsers.length">
                    <tr class="empty-state">
                      <td colspan="6">未找到匹配用户</td>
                    </tr>
                  </template>

                  <!-- 3. 正常渲染 -->
                  <template v-else>
                    <tr
                      v-for="user in filteredUsers"
                      :key="user.user_id"
                    >
                    <td v-html="highlightText(user.user_id.toString(), searchText)" />
                    <td v-html="highlightText(user.name || '', searchText)" />
                    <td v-html="highlightText(user.role || '', searchText)" />
                    <td v-html="highlightText(user.phone || '', searchText) || '未填写'" />
                    <td v-html="highlightText(user.license_plate || '', searchText) || '无'" />
                    <td v-html="highlightText(user.school_id || '', searchText) || '无'" />

                    <td>
                        <button
                          class="edit"
                          @click.stop="openEditModal(user)"
                        >
                          编辑
                        </button>
                        <button
                          class="danger"
                          @click.stop="deleteUser(user.user_id)"
                        >
                          删除
                        </button>
                      </td>
                    </tr>
                  </template>
                </tbody>

              </table>
            </div>
          </div>
          <!-- 编辑用户信息的弹出层 -->
          <div v-if="showEditModal" class="edit-modal">
            <h3>编辑用户信息</h3>
            <div class="form-grid">
              <label>用户ID:</label>
              <span>{{ editForm.user_id }}</span>
              <label>用户名:</label>
              <input v-model="editForm.name" type="text" placeholder="请输入用户名" />
              <label>手机号:</label>
              <input v-model="editForm.phone" type="text" placeholder="请输入手机号" />
              <label>车牌号:</label>
              <input v-model="editForm.license_plate" type="text" placeholder="请输入车牌号" />
            </div>
            <div class="button-container">
              <button class="primary" @click="submitUserEdit">保存</button>
              <button class="secondary" @click="closeEditModal">取消</button>
            </div>
          </div>
        </div>

        <!-- 车辆管理 -->
        <div v-if="activePage === 'vehicleManagement'" class="section">
          <h2>电动车管理</h2>
          <!-- 搜索区域：按车牌号搜索 -->
          <div class="search-box">
            <input type="text" v-model="searchQuery" placeholder="请输入车牌号搜索" />
          </div>
          <div class="vehicle-management">
            <div class="vehicle-list">
              <h3 class="left-aligned">所有车辆信息列表</h3>
              <table class="vehicle-table">
                <thead>
                  <tr>
                    <th>车牌号</th>
                    <th>车主</th>
                    <th>品牌</th>
                    <th>颜色</th>
                    <th>状态</th>
                    <th>图片</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="vehicle in filteredVehicles" :key="vehicle.id">
                    <td v-html="highlightText(vehicle.plate_number || '', searchQuery)"></td>
                    <td v-html="highlightText(vehicle.owner_name || vehicle.owner_id || '', searchQuery)"></td>
                    <td v-html="highlightText(vehicle.brand || '', searchQuery)"></td>
                    <td v-html="highlightText(vehicle.color || '', searchQuery)"></td>
                    <td>{{ vehicle.status }}</td>
                    <td>
                      <img v-if="vehicle.image_url" :src="vehicle.image_url" alt="车辆图片" class="vehicle-image" />
                    </td>
                    <td>
                      <button @click="showEditForm(vehicle)" class="edit">编辑</button>
                      <button @click="handleDelete(vehicle.id)" class="danger">删除</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- 编辑车辆状态的弹出层 -->
            <div v-if="editingVehicle" class="edit-form">
              <h3>编辑车辆状态</h3>
              <div class="form-grid">
                <label>车牌号:</label>
                <span>{{ editingVehicle.plate_number }}</span>
                <label>当前状态:</label>
                <select v-model="editingVehicle.status">
                  <option value="active">正常</option>
                  <option value="维修中">维修中</option>
                  <option value="报废">报废</option>
                </select>
              </div>
              <button class="primary" @click="submitVehicleEdit">保存</button>
              <button class="secondary" @click="cancelEdit">取消</button>
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
          <div v-if="activePage === 'parkingManagement'" class="section">
          <h2>停车场充电区管理</h2>
          <!-- 引入并使用 AdminParkingPage 组件 -->
          <AdminParkingPage />
          <h3>地图导航管理</h3>
          <MapNavigation /> 
        </div>
          <div class="parking-management">
            <!-- <div class="parking-violation">
              <h3>违规停车处理</h3>
              <p>违规处理区域</p>
            </div> -->
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
// 只导入一次 useAuthStore，因为认证和用户管理都放在一个文件中
import { useAuthStore } from "../store/auth";
import { useVehicleStore } from "../store/vehicleService";
import AdminParkingPage from '@/components/AdminParkingPage.vue';
import MapNavigation from "@/components/MapNavigation.vue";


export default {
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const vehicleStore = useVehicleStore();

    // 使用 authStore 来管理用户数据（包括所有用户列表）
    const searchText = ref("");
    const showEditModal = ref(false);
    const editForm = ref({
      user_id: "",
      name: "",
      phone: "",
      license_plate: ""
    });

    const isLoading = ref(true);

    onMounted(async () => {
      // 权限校验
      if (authStore.user?.role !== 'admin') {
        alert('无权限访问');
        return router.replace('/login');
      }

      // 初始化 & 加载
      authStore.allUsers = [];     // 确保不是 undefined
      isLoading.value = true;
      try {
        await authStore.fetchAllUsers();
      } catch (e) {
        console.error(e);
        alert('数据加载失败');
      } finally {
        isLoading.value = false;
      }
    });



    const highlightText = (text, keyword) => {
      if (!keyword) return text;
      const regex = new RegExp(`(${keyword})`, 'gi');
      return text.replace(regex, '<span class="highlightText">$1</span>');
    };
    
    const filteredUsers = computed(() => {
      const list = authStore.allUsers || [];
      const q = searchText.value.trim().toLowerCase();

      return list
        // 1) 严格剔除掉 null/undefined、非对象，或缺少 user_id 的条目
        .filter(u => u && typeof u === 'object' && u.user_id != null)
        // 2) 再对合法项做搜索过滤
        .filter(u => {
          if (!q) return true;
          const haystack = [
            u.user_id.toString().toLowerCase(),
            u.name?.toLowerCase()     || '',
            u.phone?.toLowerCase()    || '',
            u.license_plate?.toLowerCase() || '',
            u.school_id?.toLowerCase() || ''
          ].join('|');
          return haystack.includes(q);
        });
        
    });





    // 用户编辑：打开编辑模态框
    const openEditModal = (user) => {
      console.log('openEditModal 被调用，user:', user)
      // 添加对象有效性验证
      if (!user || typeof user !== 'object' || !user.user_id) {
        console.error('无效的用户对象', user);
        alert('用户数据异常，请刷新后重试');
        return;
      }

      // 使用可选链和默认值
      editForm.value = {
        user_id: user?.user_id ?? '',
        name: user?.name ?? '',
        phone: user?.phone ?? '',
        license_plate: user?.license_plate ?? ''
      };
      
      showEditModal.value = true;
    };

    const closeEditModal = () => {
      showEditModal.value = false;
    };

    // 提交用户编辑（重命名为 submitUserEdit）
    const submitUserEdit = async () => {
      try {
        await authStore.updateUser({
          user_id:editForm.value.user_id,
          name: editForm.value.name,
          phone: editForm.value.phone,
          license_plate: editForm.value.license_plate
        });
        alert("更新成功！");
        showEditModal.value = false;
        await authStore.fetchAllUsers();
      } catch (error) {
        console.error("编辑失败:", error);
        alert("编辑失败，请重试！");
      }
    };

    // 删除用户
    const deleteUser = async (userId) => {
      if (!userId) {
        console.error('删除操作接收到无效用户ID');
        return;
      }

      if (confirm(`确认删除用户 ${userId} 吗？此操作不可撤销！`)) {
        try {
          await authStore.deleteUser(userId);
          await authStore.fetchAllUsers();
          alert('删除成功');
        } catch (error) {
          console.error('删除失败:', error);
          alert(`删除失败: ${error.response?.data?.message || error.message}`);
        }
      }
    };

    // 以下车辆管理部分保持不变
    const allVehicles = computed(() => vehicleStore.allVehicles);
    const editingVehicle = ref(null);
    const searchQuery = ref("");
    const filteredVehicles = computed(() => {
      if (!searchQuery.value) return allVehicles.value;
      return allVehicles.value.filter(vehicle =>
        vehicle.plate_number?.toLowerCase().includes(searchQuery.value.toLowerCase())
      );
    });

    onMounted(async () => {
      try {
        if (authStore.user?.role !== "admin") {
          alert("无权限访问该功能");
          return;
        }
        await vehicleStore.fetchAllVehicles();
        
      } catch (error) {
        console.error("加载车辆列表失败:", error);
        alert("加载车辆列表失败，请重试");
      }
    });

    const showEditForm = (vehicle) => {
      editingVehicle.value = { ...vehicle };
    };

    const submitVehicleEdit = async () => {
      try {
        await vehicleStore.adminupdateVehicle(
          editingVehicle.value.id,
          editingVehicle.value
        );
        editingVehicle.value = null;
        alert("车辆编辑成功！");
      } catch (error) {
        console.error("车辆编辑失败:", error);
        alert("车辆编辑失败，请检查输入信息！");
      }
    };

    const cancelEdit = () => {
      editingVehicle.value = null;
    };

    const handleDelete = async (vehicleId) => {
      if (confirm("确定删除该车辆？")) {
        try {
          await vehicleStore.deleteVehicle(vehicleId);
          alert("删除成功！");
        } catch (error) {
          console.error("删除失败:", error);
          alert("删除失败，请重试！");
        }
      }
    };

    const activePage = ref("systemDashboard");

    const logout = () => {
      if (confirm("确定要退出登录吗？")) {
        authStore.logout();
        router.replace("/login");
      }
    };

    const navigate = (page) => {
      activePage.value = page;
    };

    return {
      activePage,
      logout,
      navigate,
      allVehicles,
      filteredUsers,
      filteredVehicles,
      editingVehicle,
      showEditForm,
      submitUserEdit,
      submitVehicleEdit,
      openEditModal,
      closeEditModal,
      showEditModal,
      deleteUser,
      cancelEdit,
      searchText,
      searchQuery,
      AdminParkingPage,
      handleDelete,
      editForm,
      isLoading,
      highlightText,
      MapNavigation,
    };
  },
};
</script>

<style scoped>
/* 请根据需要保留或调整样式 */

/* 全局样式 */
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
  background-color: #f9f9f9;
}

.user-table td:last-child button.danger {
  background-color: #dc3545;
  margin-left: 10px;
}

.user-table td:last-child button.edit {
  background-color: rgb(55, 182, 46);
  margin-left: 10px;
}


.vehicle-management {
  display: flex;
  flex-direction: column;
  text-align: left;
  gap: 20px;
}

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

.vehicle-table td:last-child button.danger {
  background-color: #dc3545;
  margin-left: 10px;
}

.vehicle-table td:last-child button.edit {
  background-color: rgb(55, 182, 46);
  margin-left: 10px;
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

.search-box {
  margin-bottom: 15px;
}

.search-box input {
  width: 300px;
  padding: 8px;
  border: 1px solid #ced4da;
  border-radius: 4px;
}

.vehicle-image {
  max-width: 100px;
  max-height: 70px;
  object-fit: contain;
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
  padding: 12px 16px;
  font-size: 16px;
  border-radius: 4px;
}

.sidebar li:hover {
  background-color: #343a40;
  color: white;
}

.main-content {
  flex: 1;
  padding: 20px;
  background-color: #f8f9fa;
  overflow-y: auto;
}

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

h2 {
  color: #212529;
  font-weight: 600;
  margin-bottom: 15px;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 10px;
}

.edit-form {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  width: 600px;
  z-index: 1000;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.edit-form input,
.edit-form select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ced4da;
  border-radius: 4px;
}

/* 加载状态样式 */
.loading-state {
  text-align: center;
  padding: 40px 0;
  color: #666;
}

.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(0,0,0,0.1);
  border-radius: 50%;
  border-top-color: #007bff;
  animation: spin 1s ease-in-out infinite;
  margin-right: 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  padding: 20px 0;
  color: #999;
  text-align: center;
}

/* 按钮点击保护 */
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 用户管理的编辑弹窗 */
.edit-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: #fff;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  width: 500px;
  z-index: 1000;
}

:deep(.highlightText) {
  background-color: yellow;
  font-weight: bold;
  color: #d12a2a;
}



</style>
