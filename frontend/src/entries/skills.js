import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { setAxiosConfig } from '../utils/axios'
import { ElMessage } from 'element-plus'
import Layout from '../components/Layout.vue'
import SkillList from '../views/skills/SkillList.vue'

const app = createApp({
  components: { Layout, SkillList },
  template: '<Layout><SkillList /></Layout>'
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
