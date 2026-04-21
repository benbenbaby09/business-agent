import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import SkillList from '../views/skills/SkillList.vue'
import SkillDetail from '../views/skills/SkillDetail.vue'
import SkillCreate from '../views/skills/SkillCreate.vue'
import FileGenerator from '../views/FileGenerator.vue'
import VersionManagement from '../views/VersionManagement.vue'
import TenantList from '../views/tenants/TenantList.vue'
import McpManagement from '../views/mcp/McpManagement.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/skills',
    name: 'SkillList',
    component: SkillList
  },
  {
    path: '/skills/create',
    name: 'SkillCreate',
    component: SkillCreate
  },
  {
    path: '/skills/:id',
    name: 'SkillDetail',
    component: SkillDetail
  },
  {
    path: '/tenants',
    name: 'TenantList',
    component: TenantList
  },
  {
    path: '/mcp',
    name: 'McpManagement',
    component: McpManagement
  },
  {
    path: '/generator',
    name: 'FileGenerator',
    component: FileGenerator
  },
  {
    path: '/versions',
    name: 'VersionManagement',
    component: VersionManagement
  },
  {
    path: '/',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 检查是否需要登录
  const requiresAuth = to.path !== '/login'
  const token = localStorage.getItem('token')
  
  if (requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
