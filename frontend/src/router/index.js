import { createRouter, createWebHistory } from 'vue-router';
import Login from '../components/User_Login.vue';
import Register from '../components/User_Register.vue';
// import Dashboard from '../views/Dashboard.vue';

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  // { path: '/dashboard', component: Dashboard },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;