<template>
  <div class="register-container">
    <h2>用户注册</h2>
    <el-form @submit.prevent="handleRegister">
      <el-form-item label="姓名">
        <el-input v-model="formData.name" placeholder="请输入姓名" />
      </el-form-item>
      <el-form-item label="手机号">
        <el-input v-model="formData.phone" placeholder="请输入手机号" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input
          v-model="formData.password"
          type="password"
          placeholder="请输入密码"
        />
      </el-form-item>
      <el-form-item label="用户类型">
        <el-select v-model="formData.user_type">
          <el-option label="校内人员" value="internal"></el-option>
          <el-option label="校外访客" value="external"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item v-if="formData.user_type === 'internal'" label="学工号">
        <el-input v-model="formData.school_id" placeholder="请输入学工号" />
      </el-form-item>
      <el-form-item v-if="formData.user_type === 'external'" label="身份证号">
        <el-input v-model="formData.id_card" placeholder="请输入身份证号" />
      </el-form-item>
      <el-form-item v-if="formData.user_type === 'external'" label="车牌号">
        <el-input v-model="formData.license_plate" placeholder="请输入车牌号" />
      </el-form-item>
      <el-button type="primary" @click="handleRegister">注册</el-button>
      <p>已有账号？<router-link to="/login">去登录</router-link></p>
    </el-form>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useAuthStore } from "../store/auth";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

const formData = ref({
  name: "",
  phone: "",
  password: "",
  user_type: "internal",
  school_id: "",
  id_card: "",
  license_plate: "",
});

const handleRegister = async () => {
  const response = await authStore.register(formData.value);
  if (response) {
    alert("注册成功，请登录！");
    router.push("/login");
  } else {
    alert("注册失败，请检查输入信息");
  }
};
</script>

<style scoped>
.register-container {
  max-width: 400px;
  margin: 50px auto;
}
</style>
