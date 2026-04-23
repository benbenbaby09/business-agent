import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { setAxiosConfig } from '../utils/axios'
import { ElMessage } from 'element-plus'
import Layout from '../components/Layout.vue'
import McpManagement from '../views/mcp/McpManagement.vue'

const app = createApp({
  components: { Layout, McpManagement },
  template: '<Layout><McpManagement /></Layout>'
})

// 配置axios
setAxiosConfig({
  autoRedirectOn401: true,
  showMessage: (message) => {
    ElMessage.error(message)
  }
})

app.use(createPinia())
app.use(ElementPlus)

app.mount('#app')
