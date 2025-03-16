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
  const role = await authStore.login(username.value, password.value);
  //console.log("获取的角色:", role);
  if (role) {
    //alert("获取到了角色：" + role);

    // 登录成功后获取用户信息
    //await authStore.fetchUserInfo();

    // 根据角色跳转页面
    if (role === "admin") {
      // 如果是管理员，跳转到管理员面板
      router.push("/admin-dashboard");
    } else {
      // 如果是普通用户，跳转到用户信息管理页面
      router.push("/user-management");
    }
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
