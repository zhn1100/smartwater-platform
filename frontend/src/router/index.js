import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated, isAdmin } from '../api/auth.js'

// 懒加载组件
const Login = () => import('../pages/Login.vue')
const Monitor = () => import('../pages/Monitor.vue')
const AdminPanel = () => import('../pages/AdminPanel.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/monitor'
  },
  {
    path: '/monitor',
    name: 'Monitor',
    component: Monitor,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'AdminPanel',
    component: AdminPanel,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    if (!isAuthenticated()) {
      // 未登录，跳转到登录页
      next('/login')
      return
    }
    
    // 检查是否需要管理员权限
    if (to.meta.requiresAdmin && !isAdmin()) {
      // 不是管理员，跳转到监控页面
      next('/monitor')
      return
    }
  }
  
  // 如果已经登录，访问登录页时跳转到监控页面
  if (to.path === '/login' && isAuthenticated()) {
    next('/monitor')
    return
  }
  
  next()
})

export default router
