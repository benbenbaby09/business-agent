<template>
  <div class="app-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="200px" class="sidebar">
        <div class="logo">
          <h1>商家智能体平台</h1>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/merchants">
            <el-icon><OfficeBuilding /></el-icon>
            <span>商家管理</span>
          </el-menu-item>
          <el-menu-item index="/mcp">
            <el-icon><Connection /></el-icon>
            <span>MCP管理</span>
          </el-menu-item>
          <el-menu-item index="/skills">
            <el-icon><Document /></el-icon>
            <span>Skill管理</span>
          </el-menu-item>
          <el-menu-item index="/generator">
            <el-icon><MagicStick /></el-icon>
            <span>文件生成</span>
          </el-menu-item>
          <el-menu-item index="/versions">
            <el-icon><RefreshLeft /></el-icon>
            <span>版本管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-container class="main-container">
        <!-- 顶部导航栏 -->
        <el-header class="header">
          <div class="user-info">
            <el-dropdown>
              <span class="user-name">{{ user.username }}</span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <!-- 内容区域 -->
        <el-main class="content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { HomeFilled, Document, MagicStick, RefreshLeft, OfficeBuilding, Connection } from '@element-plus/icons-vue'

const router = useRouter()
const store = useAuthStore()

const activeMenu = computed(() => {
  return router.currentRoute.value.path
})

const user = ref({
  username: '商家用户'
})

const handleMenuSelect = (key) => {
  router.push(key)
}

const handleLogout = () => {
  // 清除登录状态
  store.logout()
  router.push('/login')
}

onMounted(() => {
  // 检查登录状态
  if (!store.token) {
    router.push('/login')
  }
})
</script>

<style scoped>
.app-container {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.sidebar {
  background-color: #2c3e50;
  color: white;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
}

.logo {
  padding: 20px;
  border-bottom: 1px solid #34495e;
}

.logo h1 {
  font-size: 18px;
  margin: 0;
  text-align: center;
}

.menu {
  margin-top: 20px;
  background-color: transparent;
  border-right: none;
}

.menu .el-menu-item {
  color: white;
  height: 60px;
  line-height: 60px;
  font-size: 14px;
}

.menu .el-menu-item.is-active {
  background-color: #34495e;
  color: #409eff;
}

.menu .el-menu-item:hover {
  background-color: #34495e;
}

.main-container {
  margin-left: 200px;
  height: 100vh;
}

.header {
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 0 20px;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-name {
  cursor: pointer;
  margin-right: 10px;
}

.content {
  padding: 20px;
  background-color: #f5f7fa;
  overflow-y: auto;
}
</style>
