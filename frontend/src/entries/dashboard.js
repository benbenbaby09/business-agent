import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { setAxiosConfig } from '../utils/axios'
import { ElMessage } from 'element-plus'
import Layout from '../components/Layout.vue'
import Dashboard from '../views/Dashboard.vue'

console.log('Dashboard entry loading...')

try {
  const app = createApp({
    components: { Layout, Dashboard },
    template: '<Layout><Dashboard /></Layout>'
  })

  console.log('App created')

  // 配置axios
  setAxiosConfig({
    autoRedirectOn401: true,
    showMessage: (message) => {
      ElMessage.error(message)
    }
  })

  app.use(createPinia())
  console.log('Pinia installed')

  app.use(ElementPlus)
  console.log('ElementPlus installed')

  app.mount('#app')
  console.log('App mounted')
} catch (error) {
  console.error('Error mounting app:', error)
}
