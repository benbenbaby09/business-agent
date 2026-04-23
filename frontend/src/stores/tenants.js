import { defineStore } from 'pinia'
import axios from '../utils/axios'

export const useTenantsStore = defineStore('tenants', {
  state: () => ({
    tenants: [],
    currentTenant: null,
    loading: false,
    error: null
  }),
  
  getters: {
    getTenantById: (state) => (id) => {
      return state.tenants.find(tenant => tenant.id === id)
    }
  },
  
  actions: {
    async fetchTenants() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/tenants', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        this.tenants = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取租户列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async fetchTenantById(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get(`/tenants/${id}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        this.currentTenant = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取租户详情失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async createTenant(tenantData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/tenants', tenantData, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        this.tenants.unshift(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '创建租户失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async updateTenant(id, tenantData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.put(`/tenants/${id}`, tenantData, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        const index = this.tenants.findIndex(tenant => tenant.id === id)
        if (index !== -1) {
          this.tenants[index] = response.data
        }
        
        if (this.currentTenant && this.currentTenant.id === id) {
          this.currentTenant = response.data
        }
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '更新租户失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async deleteTenant(id) {
      this.loading = true
      this.error = null
      
      try {
        await axios.delete(`/tenants/${id}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        this.tenants = this.tenants.filter(tenant => tenant.id !== id)
        if (this.currentTenant && this.currentTenant.id === id) {
          this.currentTenant = null
        }
      } catch (error) {
        this.error = error.response?.data?.error || '删除租户失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async regenerateApiKey(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post(`/tenants/${id}/regenerate-api-key`, {}, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '重新生成API密钥失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    setCurrentTenant(tenant) {
      this.currentTenant = tenant
      // 保存到localStorage
      if (tenant) {
        localStorage.setItem('currentTenant', JSON.stringify(tenant))
      } else {
        localStorage.removeItem('currentTenant')
      }
    },
    
    loadCurrentTenant() {
      const tenant = localStorage.getItem('currentTenant')
      if (tenant) {
        this.currentTenant = JSON.parse(tenant)
      }
    }
  }
})
