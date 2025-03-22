<template>
  <div class="login-container">
    <h2>用户登录</h2>
    <el-form @submit.prevent="handleLogin">
      <el-form-item label="用户名">
        <el-input v-model="username" placeholder="手机号或学工号" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="password" type="password" placeholder="请输入密码" />
      </el-form-item>
      <el-button type="primary" @click="handleLogin">登录</el-button>
      <p>还没有账号？<router-link to="/register">去注册</router-link></p>
    </el-form>

    <!-- 访客通行证更新表单 -->
    <div v-if="showUpdateForm" class="update-form">
      <h3>请注册或更新访客通行证</h3>
      <el-form @submit.prevent="updateVisitorPass">
        <el-form-item label="用户名">
          <el-input
            v-model="visitorUsername"
            placeholder="手机号或学工号"
            required
          />
        </el-form-item>
        <el-form-item label="车牌号">
          <el-input
            v-model="licensePlate"
            placeholder="请输入您的车牌号（后续自动生成）"
            required
          />
        </el-form-item>
        <el-button type="primary" @click="updateVisitorPass"
          >更新通行证</el-button
        >
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useAuthStore } from "../store/auth";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

const username = ref("");
const password = ref("");
const showUpdateForm = ref(false);
const licensePlate = ref("");
const visitorInfo = ref(null);
const visitorUsername = ref("");

const handleLogin = async () => {
  const user = await authStore.login(username.value, password.value);
  console.log("登录返回的用户信息:", user);

  if (user?.need_update) {
    // 访客通行证已过期，显示更新表单
    showUpdateForm.value = true;
    visitorInfo.value = user; // 保存用户信息
    licensePlate.value = user.license_plate || ""; // 预填车牌号
    visitorUsername.value = user.username || ""; // 预填用户名
    return;
  }

  if (user && user.role) {
    // 登录成功后根据角色跳转到不同的页面
    switch (user.role) {
      case "admin":
        router.replace("/admin-dashboard"); // 使用 replace，确保浏览器后退按钮可以返回登录页面
        break;
      case "student":
        router.replace("/student-dashboard"); // 使用 replace 跳转
        break;
      case "staff":
        router.replace("/staff-dashboard"); // 使用 replace 跳转
        break;
      case "visitor":
        router.replace("/visitor-dashboard"); // 使用 replace 跳转
        break;
      default:
        alert("未知角色");
        break;
    }
  } else {
    alert("登录失败，请检查用户名或密码");
  }
};

const updateVisitorPass = async () => {
  try {
    const response = await authStore.updateVisitorPass(
      visitorUsername.value,
      licensePlate.value
    );

    if (response.success) {
      alert("通行证已更新，正在重新登录...");
      showUpdateForm.value = false;

      // 重新使用原来的用户名和密码登录
      await handleLogin();
    }
  } catch (error) {
    alert("更新通行证失败，请稍后重试");
  }
};
</script>

<style scoped>
.update-form {
  margin-top: 20px;
  padding: 20px;
  border: 1px solid #ccc;
  background-color: #f9f9f9;
}
</style>
