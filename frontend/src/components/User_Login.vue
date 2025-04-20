<template>
  <div class="login-page">
    <div class="login-box">
      <h1 class="main-title">校园电瓶车管理系统</h1>
      <h2 class="sub-title">用户登录</h2>
      <el-form @submit.prevent="handleLogin" class="login-form">
        <el-form-item label="用户名">
          <el-input v-model="username" placeholder="手机号或学工号" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-button type="primary" class="login-btn" @click="handleLogin">登录</el-button>
        <p class="register-tip">
          还没有账号？<router-link to="/register">去注册</router-link>
        </p>
      </el-form>

      <!-- 访客通行证更新表单 -->
      <div v-if="showUpdateForm" class="update-form">
        <h3>请注册或更新访客通行证</h3>
        <el-form @submit.prevent="updateVisitorPass" class="visitor-form">
          <el-form-item label="用户名">
            <el-input v-model="visitorUsername" placeholder="手机号或学工号" required />
          </el-form-item>
          <el-form-item label="车牌号">
            <el-input v-model="licensePlate" placeholder="请输入您的车牌号（后续自动生成）" required />
          </el-form-item>
          <el-button type="primary" @click="updateVisitorPass">更新通行证</el-button>
        </el-form>
      </div>
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
    showUpdateForm.value = true;
    visitorInfo.value = user;
    licensePlate.value = user.license_plate || "";
    visitorUsername.value = user.username || "";
    return;
  }

  if (user && user.role) {
    switch (user.role) {
      case "admin":
        router.replace("/admin-dashboard");
        break;
      case "student":
        router.replace("/student-dashboard");
        break;
      case "staff":
        router.replace("/staff-dashboard");
        break;
      case "visitor":
        router.replace("/visitor-dashboard");
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
      await handleLogin();
    }
  } catch (error) {
    alert("更新通行证失败，请稍后重试");
  }
};
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(to right, #f0f2f5, #d9e7ff);
}

.login-box {
  background-color: #fff;
  padding: 40px 30px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  width: 420px;
}

.main-title {
  text-align: center;
  font-size: 28px;
  margin-bottom: 10px;
  color: #2c3e50;
}

.sub-title {
  text-align: center;
  font-size: 20px;
  margin-bottom: 25px;
  color: #4b6ea9;
}

.login-btn {
  width: 100%;
  margin-top: 10px;
}

.register-tip {
  margin-top: 15px;
  text-align: center;
  font-size: 14px;
  color: #888;
}

.register-tip a {
  color: #409eff;
  text-decoration: none;
}

.update-form {
  margin-top: 30px;
  padding: 20px;
  border: 1px solid #ebeef5;
  background-color: #fdfdfd;
  border-radius: 10px;
}

.update-form h3 {
  text-align: center;
  margin-bottom: 15px;
  color: #606266;
}
</style>
