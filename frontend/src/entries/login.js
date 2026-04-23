import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { setAxiosConfig } from '../utils/axios'
import { ElMessage } from 'element-plus'
import Login from '../views/Login.vue'

const app = createApp(Login)

// 配置axios
setAxiosConfig({
  autoRedirectOn401: false,
  showMessage: (message) => {
    ElMessage.error(message)
  }
})

app.use(createPinia())
app.use(ElementPlus)

app.mount('#app')
