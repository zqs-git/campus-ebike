// 忽略 ResizeObserver loop completed 警告
window.addEventListener('error', (e) => {
    if (
      e.message &&
      e.message.includes('ResizeObserver loop completed')
    ) {
      // 阻止这条错误冒泡到 overlay
      e.stopImmediatePropagation()
    }
  })
  

import { createApp } from 'vue'
import App from './App.vue'
import router from './router';  // 确保正确导入 router
import { createPinia } from 'pinia';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';  // 导入 Element Plus 样式
import MapNavigation from "@/components/MapNavigation.vue"; // 导入 MapNavigation 组件
import StudentParkingPage from "@/components/ParkingPage.vue"; // 导入 StudentParkingPage 组件
import AdminParkingPage from "@/components/AdminParkingPage.vue"; // 导入 AdminParkingPage 组件
import ChargingPage from '@/components/ChargingPage.vue';   // 导入 Charging_Page 组件
import ChargingAdmin from '@/components/ChargingAdmin.vue';
const app = createApp(App);
app.use(router); // 确保 router 被 Vue 应用使用

app.component("MapNavigation", MapNavigation);
app.component("StudentParkingPage", StudentParkingPage);
app.component("AdminParkingPage", AdminParkingPage);
app.component("ChargingPage", ChargingPage); // 注册 ChargingPage 组件
app.component("ChargingAdmin", ChargingAdmin); // 注册 ChargingAdmin 组件
// 创建 Pinia 实例
const pinia = createPinia();


app.use(pinia);

app.use(ElementPlus);

app.mount('#app');