import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { setAxiosConfig } from './utils/axios'
import { ElMessage } from 'element-plus'

const app = createApp(App)

// 配置axios
setAxiosConfig({
  // 401错误时自动跳转到登录页
  autoRedirectOn401: true,
  // 使用Element Plus的消息提示
  showMessage: (message) => {
    ElMessage.error(message)
  }
})

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')
