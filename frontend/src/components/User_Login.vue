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

const handleLogin = async () => {
  const user = await authStore.login(username.value, password.value);

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
</script>
