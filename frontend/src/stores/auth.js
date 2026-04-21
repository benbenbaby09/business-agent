import { defineStore } from 'pinia'
import axios from '../utils/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user')) || null,
    loading: false,
    error: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token
  },
  
  actions: {
    async login(email, password) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/auth/login', {
          email,
          password
        })
        
        this.token = response.data.token
        this.user = response.data.user
        
        // 保存到本地存储
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '登录失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async register(username, email, password) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/auth/register', {
          username,
          email,
          password
        })
        
        this.token = response.data.token
        this.user = response.data.user
        
        // 保存到本地存储
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '注册失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    logout() {
      this.token = ''
      this.user = null
      
      // 清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
    
    async getMe() {
      if (!this.token) return
      
      try {
        const response = await axios.get('/auth/me', {
          headers: {
            Authorization: `Bearer ${this.token}`
          }
        })
        
        this.user = response.data
        localStorage.setItem('user', JSON.stringify(response.data))
      } catch (error) {
        console.error('获取用户信息失败:', error)
        this.logout()
      }
    }
  }
})
