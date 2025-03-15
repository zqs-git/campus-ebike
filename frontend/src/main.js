import { createApp } from 'vue'
import App from './App.vue'
import router from './router';  // 确保正确导入 router
import { createPinia } from 'pinia';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';  // 导入 Element Plus 样式

const app = createApp(App);
app.use(router); // 确保 router 被 Vue 应用使用

// 创建 Pinia 实例
const pinia = createPinia();
app.use(pinia);

app.use(ElementPlus);

app.mount('#app');