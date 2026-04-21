import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 配置项
const axiosConfig = {
  // 401错误时是否自动跳转到登录页
  autoRedirectOn401: true,
  // 401错误时的回调函数
  on401: null,
  // 是否显示错误提示
  showErrorMessage: true,
  // 错误提示函数
  showMessage: (message) => {
    console.error(message)
  }
}

// 设置配置项
export function setAxiosConfig(config) {
  Object.assign(axiosConfig, config)
}

// 获取配置项
export function getAxiosConfig() {
  return { ...axiosConfig }
}

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 从本地存储获取令牌
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response
  },
  error => {
    // 处理错误
    if (error.response) {
      const status = error.response.status
      const message = error.response.data?.error || '请求失败'
      
      switch (status) {
        case 401:
          // 未授权
          if (axiosConfig.showErrorMessage) {
            axiosConfig.showMessage('登录已过期，请重新登录')
          }
          
          // 清除登录状态
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          
          // 调用自定义回调
          if (axiosConfig.on401) {
            axiosConfig.on401(error)
          }
          
          // 自动跳转到登录页
          if (axiosConfig.autoRedirectOn401) {
            window.location.href = '/login'
          }
          break
          
        case 403:
          // 禁止访问
          if (axiosConfig.showErrorMessage) {
            axiosConfig.showMessage('没有权限执行此操作')
          }
          break
          
        case 404:
          // 资源不存在
          if (axiosConfig.showErrorMessage) {
            axiosConfig.showMessage('请求的资源不存在')
          }
          break
          
        case 500:
          // 服务器错误
          if (axiosConfig.showErrorMessage) {
            axiosConfig.showMessage('服务器错误，请稍后重试')
          }
          break
          
        default:
          // 其他错误
          if (axiosConfig.showErrorMessage) {
            axiosConfig.showMessage(message)
          }
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      if (axiosConfig.showErrorMessage) {
        axiosConfig.showMessage('网络错误，请检查网络连接')
      }
    } else {
      // 请求配置出错
      if (axiosConfig.showErrorMessage) {
        axiosConfig.showMessage('请求配置错误')
      }
    }
    
    return Promise.reject(error)
  }
)

export default api
