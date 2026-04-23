<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>{{ isLogin ? '登录' : '注册' }}</h2>
        </div>
      </template>
      
      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="80px"
      >
        <el-form-item v-if="!isLogin" label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item :label="isLogin ? '用户名' : '邮箱'" :prop="isLogin ? 'email' : 'email'">
          <el-input v-model="form.email" :type="isLogin ? 'text' : 'email'" :placeholder="isLogin ? '请输入用户名' : '请输入邮箱'" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading" style="width: 100%">
            {{ isLogin ? '登录' : '注册' }}
          </el-button>
        </el-form-item>
        
        <el-form-item>
          <el-link @click="toggleMode">{{ isLogin ? '没有账号？立即注册' : '已有账号？立即登录' }}</el-link>
        </el-form-item>
      </el-form>
      
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        class="error-alert"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref(null)

const isLogin = ref(true)
const loading = ref(false)
const error = ref('')

const form = reactive({
  username: '',
  email: '',
  password: ''
})

const rules = reactive({
  username: [
    {
      required: !isLogin.value,
      message: '请输入用户名',
      trigger: 'blur'
    }
  ],
  email: [
    {
      required: true,
      message: (value) => isLogin.value ? '请输入用户名' : '请输入邮箱',
      trigger: 'blur'
    },
    {
      type: 'email',
      message: '请输入正确的邮箱格式',
      trigger: 'blur',
      // 只在注册时验证邮箱格式
      validator: (rule, value, callback) => {
        if (!isLogin.value && value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          callback(new Error('请输入正确的邮箱格式'))
        } else {
          callback()
        }
      }
    }
  ],
  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: 'blur'
    },
    {
      min: 6,
      message: '密码长度至少为6位',
      trigger: 'blur'
    }
  ]
})

const toggleMode = () => {
  isLogin.value = !isLogin.value
  error.value = ''
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      error.value = ''
      
      try {
        if (isLogin.value) {
          // 登录时使用邮箱作为用户名
          await authStore.login(form.email, form.password)
        } else {
          await authStore.register(form.username, form.email, form.password)
        }
        
        // 多页应用跳转
        window.location.href = '/pages/dashboard.html'
      } catch (err) {
        error.value = authStore.error
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.login-card {
  width: 400px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.error-alert {
  margin-top: 20px;
}
</style>
