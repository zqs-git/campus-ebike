import { createRouter, createWebHistory } from 'vue-router';
import Login from '../components/User_Login.vue';
import Register from '../components/User_Register.vue';
import AdminDashboard from '../components/AdminDashboard'; 
import StudentDashboard from '../components/StudentDashboard'; 
import StaffDashboard from '../components/StaffDashboard'; 
import VisitorDashboard from '../components/VisitorDashboard';
import { useAuthStore } from '../store/auth'; // 导入authStore，获取用户信息

const routes = [
  { path: '/', redirect: '/login' }, // 根路径重定向到登录页面
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/student-dashboard', component: StudentDashboard },
  { path: '/staff-dashboard', component: StaffDashboard },
  { path: '/admin-dashboard', component: AdminDashboard },
  { path: '/visitor-dashboard', component: VisitorDashboard },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  
  // 如果用户已登录，且试图访问登录或注册页面，直接跳转到角色页面
  if (authStore.isAuthenticated) {
    const userRole = authStore.user?.role;
    
    if (to.path === '/login' || to.path === '/register') {
      // 已登录用户，跳转到对应角色的首页
      switch (userRole) {
        case 'admin':
          return next('/admin-dashboard');
        case 'student':
          return next('/student-dashboard');
        case 'staff':
          return next('/staff-dashboard');
        case 'visitor':
          return next('/visitor-dashboard');
        default:
          return next('/login'); // 如果角色没有匹配的，跳转到登录页
      }
    }
  } else {
    // 未登录用户，只有在访问登录或注册页面时才放行
    if (to.path !== '/login' && to.path !== '/register') {
      return next('/login');
    }
  }

  next(); // 确保导航继续
});

export default router;
