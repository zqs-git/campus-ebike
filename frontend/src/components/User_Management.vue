<template>
  <div>
    <h1>用户信息</h1>
    <p v-if="user">姓名: {{ user.name }}</p>
    <p v-if="user">学工号: {{ user.school_id }}</p>
    <p v-if="user">手机号: {{ user.phone }}</p>
    <p v-if="user">角色: {{ user.role }}</p>
    <p v-else>加载中...</p>
  </div>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { useAuthStore } from "../store/auth";

const authStore = useAuthStore();
const user = computed(() => authStore.user);

onMounted(() => {
  authStore.fetchUserInfo(); // 组件加载时获取用户信息
});
</script>
