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
  <div>
    <el-button type="primary">测试按钮</el-button>
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
  const success = await authStore.login(username.value, password.value);
  if (success) {
    router.push("/dashboard");
  } else {
    alert("登录失败，请检查用户名或密码");
  }
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 50px auto;
}
</style>
