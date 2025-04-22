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
          <li v-if="isStudentOrStaff" @click="navigate('personalInfo')">
            个人信息
          </li>
          <li v-if="isStudentOrStaff" @click="navigate('vehicleManagement')">
            电动车管理
          </li>
          <!-- 访客菜单项 -->
          <li v-if="!isAdmin && !isStaff && !isStudent" @click="navigate('visitorInfo')">
            访客通行证
          </li>
          <li v-if="isStudentOrStaff" @click="navigate('parkingManagement')">
            查看停车场
          </li>
          <li v-if="!isAdmin" @click="navigate('mapNavigation')">地图导航</li>
          <li v-if="isStudentOrStaff" @click="navigate('chargreManagement')">
            查看充电桩
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
        <!-- 个人信息管理页面 -->
        <div v-if="activePage === 'personalInfo'" class="section">
          <div class="info-card">
            <h2 class="info-title">个人信息管理</h2>
            <div v-if="user" class="info-grid">
              <div class="info-item">
                <label>姓名：</label>
                <span>{{ user.name }}</span>
              </div>
              <div class="info-item">
                <label>学工号：</label>
                <span>{{ user.school_id || '无' }}</span>
              </div>
              <div class="info-item">
                <label>角色：</label>
                <span>{{ user.role }}</span>
              </div>
              <div class="info-item">
                <label>电话：</label>
                <span>{{ user.phone }}</span>
              </div>
              <div class="info-item">
                <label>车牌号：</label>
                <span>{{ user.license_plate || '未绑定' }}</span>
              </div>
            </div>
            <div v-else class="info-loading">
              <p>正在加载您的信息...</p>
            </div>
            <div class="button-container" style="margin-top: 20px;">
              <button class="primary" @click="toggleEditPersonal">编辑个人信息</button>
            </div>
            <div v-if="showEditPersonalForm" class="edit-personal-form">
              <h3>编辑个人信息</h3>
              <div class="form-grid">
                <label>姓名:</label>
                <input v-model="personalForm.name" type="text" placeholder="请输入姓名" />

                <label>学工号:</label>
                <input v-model="personalForm.school_id" type="text" placeholder="请输入学号" />

                <label>电话:</label>
                <input v-model="personalForm.phone" type="text" placeholder="请输入电话" />
              </div>
              <div class="button-container" style="margin-top: 10px;">
                <button class="primary" @click="handleSavePersonal">保存</button>
                <button class="secondary" @click="toggleEditPersonal">取消</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 电动车管理页面 -->
        <div v-if="activePage === 'vehicleManagement'" class="section">
          <h2 class="section-title">我的电动车</h2>
          <!-- 如果已绑定电动车 -->
          <div v-if="vehicle && Object.keys(vehicle).length > 0">
            <div class="vehicle-info-container">
              <div class="vehicle-info-item">
                <strong>车牌号:</strong> {{ vehicle.plate_number }}
              </div>
              <div class="vehicle-info-item">
                <strong>品牌:</strong> {{ vehicle.brand }}
              </div>
              <div class="vehicle-info-item">
                <strong>颜色:</strong> {{ vehicle.color || '未填写' }}
              </div>
              <div class="vehicle-info-item" v-if="vehicle.image_url">
                <strong>图片:</strong>
                <img :src="vehicle.image_url" alt="车辆图片" class="vehicle-image" />
              </div>
            </div>

            <div class="button-container" style="margin-top: 40px;">
              <button class="secondary" @click="unbindVehicle">解绑电动车</button>
              <button @click="initializeUpdateForm">更新电动车信息</button>
            </div>

            <!-- 更新电动车信息的表单 -->
            <div v-if="showUpdateForm" class="update-form">
              <h3>更新电动车信息</h3>
              <div class="form-grid">
                <!-- 车牌号输入 -->
                <label>车牌号:</label>
                <div class="license-input" style="display: flex; gap: 10px; align-items: center;">
                  <select v-model="updateVehicleData.province">
                    <option value="川">川</option>
                    <option value="粤">粤</option>
                    <option value="京">京</option>
                    <option value="津">津</option>
                    <option value="沪">沪</option>
                    <option value="渝">渝</option>
                    <option value="鲁">鲁</option>
                    <option value="苏">苏</option>
                    <option value="浙">浙</option>
                    <option value="皖">皖</option>
                    <option value="赣">赣</option>
                    <option value="鄂">鄂</option>
                    <option value="湘">湘</option>
                    <option value="豫">豫</option>
                    <option value="晋">晋</option>
                    <option value="陕">陕</option>
                    <option value="冀">冀</option>
                    <option value="辽">辽</option>
                    <option value="吉">吉</option>
                    <option value="黑">黑</option>
                    <option value="蒙">蒙</option>
                    <option value="宁">宁</option>
                    <option value="青">青</option>
                    <option value="新">新</option>
                    <option value="藏">藏</option>
                    <option value="桂">桂</option>
                    <option value="琼">琼</option>
                    <option value="港">港</option>
                    <option value="澳">澳</option>
                    <option value="台">台</option>
                    <option value="甘">甘</option>
                    <option value="贵">贵</option>
                    <option value="云">云</option>
                    <option value="闽">闽</option>
                    <option value="陕">陕</option>
                    <!-- 根据需要添加其他省份 -->
                  </select>
                  <select v-model="updateVehicleData.cityCode">
                    <option v-for="letter in cityCodes" :key="letter" :value="letter">
                      {{ letter }}
                    </option>
                  </select>
                  <input
                    v-model="updateVehicleData.plate_number_suffix"
                    type="text"
                    placeholder="请输入车牌号后缀"
                  />
                </div>
                <!-- 品牌选择 -->
                <label>品牌:</label>
                <input
                  list="brandOptions"
                  v-model="updateVehicleData.brand"
                  placeholder="请选择或输入品牌"
                />
                <datalist id="brandOptions">
                  <option value="自定义"></option>
                  <option value="雅迪"></option>
                  <option value="爱码"></option>
                  <option value="小刀"></option>
                  <option value="台铃"></option>
                  <option value="绿源"></option>
                  <option value="比亚迪"></option>
                  <option value="小牛"></option>
                </datalist>
                <!-- 如选择其他则显示自定义输入框 -->
                <div v-if="updateVehicleData.brand === '自定义'" style="grid-column: span 2;">
                  <input
                    v-model="updateVehicleData.customBrand"
                    type="text"
                    placeholder="请输入自定义品牌"
                  />
                </div>
                <!-- 颜色输入 -->
                <label>颜色:</label>
                <select v-model="vehicleData.color">
                  <option value="">请选择颜色</option>
                  <option value="黑色">黑色</option>
                  <option value="白色">白色</option>
                  <option value="灰色">灰色</option>
                  <option value="红色">红色</option>
                  <option value="黄色">黄色</option>
                  <option value="绿色">绿色</option>
                  <option value="蓝色">蓝色</option>
                  <option value="其他">其他</option>
                </select>

                <!-- 如果选择"其他"则显示自定义颜色输入框 -->
                <div v-if="vehicleData.color === '其他'" style="grid-column: span 2;">
                  <input
                    v-model="vehicleData.customColor"
                    type="text"
                    placeholder="请输入自定义颜色"
                  />
                </div>

                <!-- 上传图片 -->
                <label>上传车辆图片:</label>
                <input type="file" @change="handleUpdateImageUpload" accept="image/*" />
                <!-- 图片预览 -->
                <div v-if="updateVehicleData.imageUrl || (vehicle && vehicle.image_url)">
                  <img
                    :src="updateVehicleData.imageUrl ? updateVehicleData.imageUrl : vehicle.image_url"
                    alt="车辆图片预览"
                    style="max-width: 10%; margin-top: 1px;"
                  />
                </div>
              </div>
              <div class="button-container" style="margin-top: 20px;">
                <button class="primary" @click="submitUpdateVehicle">提交更新</button>
                <button class="secondary" @click="showUpdateForm = false">取消</button>
              </div>
            </div>
          </div>
          <!-- 如果未绑定电动车 -->
          <div v-else>
            <h2 class="alert-text">你还没有绑定电动车！</h2>
            <button @click="showBindForm = true">绑定电动车</button>
          </div>

          <div v-if="successMessage" class="success-alert">
            {{ successMessage }}
          </div>

          <!-- 绑定电动车的弹窗 -->
          <div v-if="showBindForm" class="bind-form">
            <h3>绑定电动车</h3>
            <label>车牌号:</label>
            <div class="license-input" style="display: flex; gap: 10px; align-items: center;">
              <select v-model="vehicleData.province">
                <option value="川">川</option>
                <option value="粤">粤</option>
                <option value="京">京</option>
                <option value="津">津</option>
                <option value="沪">沪</option>
                <option value="渝">渝</option>
                <option value="鲁">鲁</option>
                <option value="苏">苏</option>
                <option value="浙">浙</option>
                <option value="皖">皖</option>
                <option value="赣">赣</option>
                <option value="鄂">鄂</option>
                <option value="湘">湘</option>
                <option value="豫">豫</option>
                <option value="晋">晋</option>
                <option value="陕">陕</option>
                <option value="冀">冀</option>
                <option value="辽">辽</option>
                <option value="吉">吉</option>
                <option value="黑">黑</option>
                <option value="蒙">蒙</option>
                <option value="宁">宁</option>
                <option value="青">青</option>
                <option value="新">新</option>
                <option value="藏">藏</option>
                <option value="桂">桂</option>
                <option value="琼">琼</option>
                <option value="港">港</option>
                <option value="澳">澳</option>
                <option value="台">台</option>
                <option value="甘">甘</option>
                <option value="贵">贵</option>
                <option value="云">云</option>
                <option value="闽">闽</option>
                <option value="陕">陕</option>
                <!-- 根据需要添加其他省份 -->
              </select>
              <select v-model="vehicleData.cityCode">
                <option v-for="letter in cityCodes" :key="letter" :value="letter">
                  {{ letter }}
                </option>
              </select>
              <input
                v-model="vehicleData.plate_number_suffix"
                type="text"
                placeholder="请输入车牌号后缀"
              />
            </div>
            <!-- 品牌 -->
            <label>品牌:</label>
            <input
              list="brandOptions"
              v-model="vehicleData.brand"
              placeholder="请选择或输入品牌"
            />
            <datalist id="brandOptions">
              <option value="自定义"></option>
              <option value="雅迪"></option>
              <option value="爱码"></option>
              <option value="小刀"></option>
              <option value="台铃"></option>
              <option value="绿源"></option>
              <option value="比亚迪"></option>
              <option value="小牛"></option>

            </datalist>
            <div v-if="vehicleData.brand === '自定义'" style="grid-column: span 2;">
              <input
                v-model="vehicleData.customBrand"
                type="text"
                placeholder="请输入自定义品牌"
              />
            </div>
            <!-- 颜色 -->
            <label>颜色:</label>
            <select v-model="vehicleData.color">
              <option value="">请选择颜色</option>
              <option value="黑色">黑色</option>
              <option value="白色">白色</option>
              <option value="灰色">灰色</option>
              <option value="红色">红色</option>
              <option value="黄色">黄色</option>
              <option value="绿色">绿色</option>
              <option value="蓝色">蓝色</option>
              <option value="其他">其他</option>
            </select>

            <!-- 如果选择"其他"则显示自定义颜色输入框 -->
            <div v-if="vehicleData.color === '其他'" style="grid-column: span 2;">
              <input
                v-model="vehicleData.customColor"
                type="text"
                placeholder="请输入自定义颜色"
              />
            </div>

            <!-- 上传图片 -->
            <label>上传车辆图片:</label>
            <input type="file" @change="handleImageUpload" accept="image/*" />
            <!-- 图片预览 -->
            <div v-if="vehicleData.imageUrl">
              <img
                :src="vehicleData.imageUrl"
                alt="电动车图片预览"
                style="max-width: 10%; margin-top: 1px;"
              />
            </div>
            <div class="button-container" style="margin-top: 10px;">
              <button @click="submitBindVehicle">确认绑定</button>
              <button @click="showBindForm = false">取消</button>
            </div>
          </div>
        </div>

        <!-- 访客通行证页面 -->
        <div v-if="activePage === 'visitorInfo'" class="visitor-profile">
          <h2>访客信息</h2>
          <div v-if="visitorInfo" class="visitor-profile">
            <div class="profile-item">
              <strong>姓名:</strong> {{ visitorInfo.name }}
            </div>
            <div class="profile-item">
              <strong>手机号:</strong> {{ visitorInfo.phone }}
            </div>
            <div class="profile-item">
              <strong>车牌号:</strong> {{ visitorInfo.license_plate }}
            </div>
            <div class="profile-item">
              <strong>通行证有效期:</strong>
              {{
                visitorInfo.expires_at
                  ? new Date(visitorInfo.expires_at).toLocaleString()
                  : "未绑定"
              }}
            </div>
          </div>
          <div v-else class="loading">
            <p>正在加载访客信息...</p>
          </div>
        </div>

        <!-- 地图导航 -->
        <div v-if="activePage === 'mapNavigation'" class="section">
          <h2>地图导航</h2>
          <div id="app">
            <MapNavigation />
          </div>
          <p>显示导航功能和路径规划。</p>
        </div>

        <!-- 停车场管理 -->
        <div v-if="activePage === 'parkingManagement'" class="section">
          <StudentParkingPage />
          <p>展示停车场信息及指引导航功能</p>
        </div>

        <!-- 积分管理 -->
        <div v-if="activePage === 'scoreManagement' && isStudentOrStaff" class="section">
          <h2>积分管理</h2>
          <p>展示违规积分及积分扣除规则。</p>
        </div>

        <!-- 充电桩管理 -->
        <div v-if="activePage === 'chargreManagement' && isStudentOrStaff" class="section">
          <ChargingPage />
          <p>展示充电桩实时状态及充电预约</p>
        </div>

        <!-- 通知 -->
        <div v-if="activePage === 'notifications'" class="section">
          <h2>通知模块</h2>
          <p>展示用户的通知信息，推送系统通知等。</p>
        </div>

        <!-- 系统管理（仅管理员可见） -->
        <div v-if="activePage === 'adminDashboard' && isAdmin">
          <AdminDashboard />
          <h2>系统管理模块</h2>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";
import { useVehicleStore } from "../store/vehicleService";
import MapNavigation from "@/components/MapNavigation.vue";
import StudentParkingPage from '@/components/ParkingPage.vue';
import { ElMessage } from 'element-plus';
import ChargingPage from "@/components/ChargingPage.vue";

export default {
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const vehicleStore = useVehicleStore();

    const successMessage = ref("");
    const activePage = ref("personalInfo");
    const showBindForm = ref(false);
    const showUpdateForm = ref(false);

    // 用户角色相关
    const userRole = computed(() => authStore.user.value?.role ?? "student");
    const isAdmin = computed(() => userRole.value === "admin");
    const isStaff = computed(() => userRole.value === "staff");
    const isVisitor = computed(() => userRole.value === "visitor");
    const isStudent = computed(() => userRole.value === "student");
    const isStudentOrStaff = computed(() => userRole.value === "student" || userRole.value === "staff");

    // 个人信息
    const user = computed(() => authStore.user);
    const visitorInfo = computed(() => authStore.visitorInfo);

    // 绑定车辆的数据
    const vehicleData = ref({
      province: "川",
      cityCode: "A",
      plate_number_suffix: "",
      brand: "",
      customBrand: "",
      color: "",
      image: null,
      imageUrl: "",
    });

    // 更新车辆的数据（更新逻辑与绑定类似）
    const updateVehicleData = ref({
      province: "川",
      cityCode: "A",
      plate_number_suffix: "",
      brand: "",
      customBrand: "",
      color: "",
      image: null,
      imageUrl: "",
    });

    // 更新时使用城市字母数组
    const cityCodes = Array.from({ length: 26 }, (_, i) =>
      String.fromCharCode(65 + i)
    );

    // 预览图片上传——绑定车辆
    const handleImageUpload = (event) => {
      const file = event.target.files[0];
      if (file) {
        vehicleData.value.image = file;
        vehicleData.value.imageUrl = URL.createObjectURL(file);
      }
    };

    // 预览图片上传——更新车辆
    const handleUpdateImageUpload = (event) => {
      const file = event.target.files[0];
      if (file) {
        updateVehicleData.value.image = file;
        updateVehicleData.value.imageUrl = URL.createObjectURL(file);
      }
    };

    // 绑定车辆提交逻辑
    const submitBindVehicle = async () => {
    const fullPlateNumber =
      vehicleData.value.province +
      vehicleData.value.cityCode +
      vehicleData.value.plate_number_suffix;
    
    const finalBrand =
      vehicleData.value.brand === "其他"
        ? vehicleData.value.customBrand
        : vehicleData.value.brand;

    const finalColor = vehicleData.value.color === "其他" ? vehicleData.value.customColor : vehicleData.value.color;

    const formData = new FormData();
    formData.append("plate_number", fullPlateNumber);
    formData.append("brand", finalBrand);
    formData.append("color", finalColor || "");
    formData.append("status", "active");
    
    if (vehicleData.value.image) {
      formData.append("image", vehicleData.value.image);
    }

    try {
      const res = await vehicleStore.bindVehicleHandler(formData);
      console.log("绑定成功:", res);
      showBindForm.value = false;
      await vehicleStore.fetchMyVehicle();
      ElMessage.success("电动车绑定成功");
    } catch (error) {
      console.error("绑定失败", error.response?.data || error);
      ElMessage.error(error.response?.data?.msg || "绑定失败，请重试");
    }
  };


    // 初始化更新表单，将现有车辆数据拆分后赋值到 updateVehicleData
    const initializeUpdateForm = () => {
      if (vehicleStore.vehicle && Object.keys(vehicleStore.vehicle).length > 0) {
        // 假设后端存储的车牌号格式是“京A12345”
        const plate = vehicleStore.vehicle.plate_number || "";
        updateVehicleData.value.province = plate.charAt(0) || "川";
        updateVehicleData.value.cityCode = plate.charAt(1) || "A";
        updateVehicleData.value.plate_number_suffix = plate.slice(2);
        updateVehicleData.value.brand = vehicleStore.vehicle.brand || "";
        updateVehicleData.value.color = vehicleStore.vehicle.color || "";
        // 清空图片相关数据，如果用户不上传新图片则默认保留现有图片
        updateVehicleData.value.image = null;
        updateVehicleData.value.imageUrl = "";
        // 显示更新表单
        showUpdateForm.value = true;
      }
    };

    // 提交更新车辆信息的逻辑
    const submitUpdateVehicle = async () => {
      const fullPlateNumber =
        updateVehicleData.value.province +
        updateVehicleData.value.cityCode +
        updateVehicleData.value.plate_number_suffix;
      const finalBrand =
        updateVehicleData.value.brand === "其他"
          ? updateVehicleData.value.customBrand
          : updateVehicleData.value.brand;

      const formData = new FormData();
      formData.append("plate_number", fullPlateNumber);
      formData.append("brand", finalBrand);
      formData.append("color", updateVehicleData.value.color);
      if (updateVehicleData.value.image) {
        formData.append("image", updateVehicleData.value.image);
      }

      try {
        // vehicleStore.updateVehicleHandler 接收车辆ID和FormData作为参数
        await vehicleStore.updateVehicleHandler(vehicle.value.vehicle_id, formData);
        showUpdateForm.value = false;
        await vehicleStore.fetchMyVehicle();
        ElMessage.success("电动车信息更新成功！");
      } catch (error) {
        console.error("更新失败", error.response?.data || error);
        ElMessage.error(error.response?.data?.msg || "更新失败，请重试");
      }
    };

    // 解绑车辆
    const unbindVehicle = async () => {
      if (vehicleStore.vehicle) {
        try {
          await vehicleStore.unbindVehicleHandler(vehicleStore.vehicle.vehicle_id);
          successMessage.value = "解绑成功！";
          setTimeout(() => { successMessage.value = ""; }, 2000);
        } catch (error) {
          console.error("解绑失败:", error);
          alert("解绑失败，请重试。");
        }
      }
    };

    // 个人信息相关
    const showEditPersonalForm = ref(false);
    const personalForm = ref({
      name: authStore.user.value?.name || "",
      school_id: authStore.user.value?.school_id || "",
      phone: authStore.user.value?.phone || "",
    });

    const toggleEditPersonal = () => {
      showEditPersonalForm.value = !showEditPersonalForm.value;
    };

    const handleSavePersonal = async () => {
      const updatedData = {
        name: personalForm.value.name,
        school_id: personalForm.value.school_id,
        phone: personalForm.value.phone,
      };
      const result = await authStore.updateUser(updatedData);
      if (result.success) {
        ElMessage.success("更新成功！");
        showEditPersonalForm.value = false;
      } else {
        ElMessage.error(result.msg || "更新失败，请检查输入信息或稍后再试！");
      }
    };

    const logout = () => {
      authStore.logout();
      vehicleStore.vehicle = {};
      router.replace("/login");
    };

    const navigate = (page) => {
      activePage.value = page;
    };

    onMounted(async () => {
      // 获取个人或访客信息
      if (user.value?.role) {
        if (user.value.role === "student" || user.value.role === "staff") {
          if (!user.value?.name) {
            await authStore.fetchUserInfo();
          }
        } else if (user.value.role === "guest") {
          try {
            await authStore.fetchVisitorInfo();
          } catch (error) {
            console.error("获取访客信息失败:", error);
          }
        }
      }
      // 获取电动车信息
      vehicleStore.fetchMyVehicle();
    });

    const vehicle = computed(() => vehicleStore.vehicle);

    return {
      // 全局状态和方法
      activePage,
      logout,
      navigate,
      user,
      visitorInfo,
      isAdmin,
      isStaff,
      isVisitor,
      isStudent,
      isStudentOrStaff,
      // 个人信息相关
      personalForm,
      showEditPersonalForm,
      toggleEditPersonal,
      handleSavePersonal,
      // 绑定车辆相关
      showBindForm,
      vehicleData,
      submitBindVehicle,
      handleImageUpload,
      // 更新车辆相关
      showUpdateForm,
      updateVehicleData,
      handleUpdateImageUpload,
      submitUpdateVehicle,
      initializeUpdateForm,
      // 车辆操作
      vehicle,
      unbindVehicle,
      successMessage,
      // 公共组件、数组等
      cityCodes,
      MapNavigation,
      StudentParkingPage,
      ChargingPage,
    };
  },
};
</script>



<style scoped>
/* 整体样式 */
.personal-info {
  background: #ffffff;
  padding: 30px 40px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  max-width: 600px;
  margin: 40px auto;
  position: relative;
}

/* 头部样式 */
.header {
  background-color: #3a3a3a;
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 仪表盘左右布局 */
.dashboard-content {
  display: flex;
  height: calc(100vh - 80px);
}

/* 侧边栏 */
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

/* 主内容区 */
.main-content {
  flex: 1;
  padding: 20px;
  background-color: white;
  overflow-y: auto;
}

h2, .section-title {
  color: #333;
}

/* 区块间距 */
.section {
  margin-bottom: 30px;
}

/* 按钮容器 */
.button-container {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 25px;
}

.personal-buttons button {
  min-width: 140px;
}

/* 按钮样式 */
button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

button.primary {
  background-color: #007bff;
  color: #fff;
}

button.secondary {
  background-color: #dc3545;
  color: #fff;
}

button:hover {
  opacity: 0.9;
}

/* 信息卡样式 */
.info-card {
  background: #ffffff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  max-width: 600px;
  margin: 0 auto;
  transition: all 0.3s ease;
}

/* 标题 */
.info-title {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  text-align: center;
  margin-bottom: 25px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-radius: 6px;
  background-color: #f9f9f9;
  transition: background-color 0.3s;
}

.info-item label {
  font-weight: 600;
  color: #555;
  font-size: 16px;
}

.info-item span {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.info-item:hover {
  background-color: #f0f8ff;
}

.info-loading {
  text-align: center;
  color: #888;
}

/* 电动车信息卡 */
.vehicle-info-container {
  display: grid;
  grid-template-columns: 1fr;
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
  border-bottom: 1px solid #eee;
}

/* 弹窗及表单样式 */
.bind-form,
.edit-personal-form,
.bind-vehicle-form,
.update-form {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 90%;
  z-index: 1000;
}

.bind-form h3,
.edit-personal-form h3,
.bind-vehicle-form h3,
.update-form h3 {
  margin-bottom: 10px;
}

/* 通用表单网格 */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  align-items: center;
}

.bind-form label,
.edit-personal-form label,
.bind-vehicle-form label,
.update-form label {
  grid-column: span 2;
  margin-top: 10px;
}

.bind-form input,
.edit-personal-form input,
.bind-vehicle-form input,
.update-form input {
  grid-column: span 2;
  width: 100%;
  padding: 8px;
  margin-top: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

/* 成功提示 */
.success-alert {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 20px 40px;
  background-color: #4caf50;
  color: white;
  border-radius: 12px;
  font-size: 20px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
  text-align: center;
  max-width: 400px;
  z-index: 1000;
}

/* 访客信息样式 */
.visitor-profile {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.profile-item {
  margin-bottom: 10px;
  font-size: 16px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  text-align: center;
  margin-bottom: 20px;
  color: #2c3e50;
  border-bottom: 2px solid #ddd;
  padding-bottom: 8px;
}

.vehicle-info-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
  background-color: #fdfdfd;
  max-width: 300px;
  margin: 20px auto;
  transition: all 0.3s ease;
}

.vehicle-info-item {
  display: flex;
  justify-content: space-between;
  font-size: 16px;
  border-bottom: 1px dashed #ccc;
  padding: 8px 0;
  color: #444;
}

.vehicle-title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 16px;
  text-align: center;
}

.button-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}

button {
  min-width: 120px;
  padding: 10px 18px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s ease-in-out;
}

button.primary {
  background: linear-gradient(to right, #1e90ff, #007bff);
  color: white;
  font-weight: 500;
}

button.secondary {
  background: linear-gradient(to right, #ff6b6b, #dc3545);
  color: white;
  font-weight: 500;
}

button:hover {
  opacity: 0.85;
  transform: translateY(-1px);
}

.alert-text {
  color: #e74c3c;
  font-weight: 600;
  text-align: center;
  margin-bottom: 12px;
}

/* 响应式处理 */
@media (max-width: 600px) {
  .vehicle-info-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .button-container {
    flex-direction: column;
    align-items: center;
  }
}

.student-dashboard {
  display: flex;
  flex-direction: column;
  height: 100vh; /* 确保撑满整个页面 */
  overflow: hidden; /* 避免多余滚动 */
}

.dashboard-content {
  display: flex;
  flex: 1; /* 撑满剩余高度 */
  overflow: hidden; /* 避免外部滚动条 */
}

.main-content {
  flex: 1;
  overflow-y: auto; /* 只在主内容区域滚动 */
  padding: 20px;
  background-color: white;
}

.vehicle-image {
  max-width: 200px; /* 限制最大宽度 */
  height: auto;     /* 保持比例 */
  display: block;   /* 避免内联元素间隙 */
  margin: 10px auto; /* 居中显示 */
}

</style>
