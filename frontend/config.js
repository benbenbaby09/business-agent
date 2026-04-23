// 全局配置文件 - 所有环境共享
// 修改此处即可全局生效

// 后端服务器基础地址
// 优先使用环境变量，其次使用默认值
export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:9000'

// API 基础路径
export const API_BASE_URL = `${BACKEND_URL}/api`

// 其他常用路径
export const STORAGE_URL = `${BACKEND_URL}/storage`

// 默认导出配置对象
export default {
  backendUrl: BACKEND_URL,
  apiBaseUrl: API_BASE_URL,
  storageUrl: STORAGE_URL
}
