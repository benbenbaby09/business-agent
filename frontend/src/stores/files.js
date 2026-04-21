import { defineStore } from 'pinia'
import axios from '../utils/axios'
import { saveAs } from 'file-saver'

export const useFilesStore = defineStore('files', {
  state: () => ({
    files: [],
    loading: false,
    error: null
  }),
  
  actions: {
    async uploadFile(skillId, file) {
      this.loading = true
      this.error = null
      
      try {
        const formData = new FormData()
        formData.append('file', file)
        
        const response = await axios.post(`/skills/${skillId}/files`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        this.files.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '上传文件失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async fetchFiles(skillId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get(`/skills/${skillId}/files`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        this.files = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取文件列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async downloadFile(skillId, fileId, filename) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get(`/skills/${skillId}/files/${fileId}`, {
          responseType: 'blob',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        saveAs(response.data, filename)
      } catch (error) {
        this.error = error.response?.data?.error || '下载文件失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async deleteFile(skillId, fileId) {
      this.loading = true
      this.error = null
      
      try {
        await axios.delete(`/skills/${skillId}/files/${fileId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        this.files = this.files.filter(file => file._id !== fileId)
      } catch (error) {
        this.error = error.response?.data?.error || '删除文件失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
