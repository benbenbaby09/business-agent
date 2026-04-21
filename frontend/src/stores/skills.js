import { defineStore } from 'pinia'
import axios from '../utils/axios'

export const useSkillsStore = defineStore('skills', {
  state: () => ({
    skills: [],
    currentSkill: null,
    loading: false,
    error: null,
    total: 0,
    page: 1,
    limit: 10
  }),
  
  getters: {
    getSkillById: (state) => (id) => {
      return state.skills.find(skill => skill._id === id)
    }
  },
  
  actions: {
    async fetchSkills(page = 1, limit = 10, status = '', type = '', tenantId = '') {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/skills', {
          params: {
            page,
            limit,
            status,
            type,
            tenant_id: tenantId
          },
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        this.skills = response.data.skills
        this.total = response.data.total
        this.page = response.data.page
        this.limit = response.data.limit
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取Skill列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async fetchSkillById(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get(`/skills/${id}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        this.currentSkill = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取Skill详情失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async createSkill(skillData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/skills', skillData, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        this.skills.unshift(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '创建Skill失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async updateSkill(id, skillData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.put(`/skills/${id}`, skillData, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        const index = this.skills.findIndex(skill => skill._id === id)
        if (index !== -1) {
          this.skills[index] = response.data
        }
        
        if (this.currentSkill && this.currentSkill._id === id) {
          this.currentSkill = response.data
        }
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '更新Skill失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async deleteSkill(id) {
      this.loading = true
      this.error = null
      
      try {
        await axios.delete(`/skills/${id}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        this.skills = this.skills.filter(skill => skill._id !== id)
        if (this.currentSkill && this.currentSkill._id === id) {
          this.currentSkill = null
        }
      } catch (error) {
        this.error = error.response?.data?.error || '删除Skill失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async publishSkill(id, changes) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post(`/skills/${id}/publish`, { changes }, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        const index = this.skills.findIndex(skill => skill._id === id)
        if (index !== -1) {
          this.skills[index] = response.data
        }
        
        if (this.currentSkill && this.currentSkill._id === id) {
          this.currentSkill = response.data
        }
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '发布Skill失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async fetchVersions(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get(`/skills/${id}/versions`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取版本历史失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
