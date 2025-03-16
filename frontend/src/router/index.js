import { createRouter, createWebHistory } from 'vue-router';
import Login from '../components/User_Login.vue';
import Register from '../components/User_Register.vue';
// import Dashboard from '../views/Dashboard.vue';
import User_Management from '../components/User_Management'; // 确保此文件存在

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  // { path: '/dashboard', component: Dashboard },
  { path: '/user-management', component: User_Management },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;