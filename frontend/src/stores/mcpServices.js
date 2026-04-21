import { defineStore } from 'pinia'
import axios from '../utils/axios'

export const useMcpServicesStore = defineStore('mcpServices', {
  state: () => ({
    mcpService: null,
    tools: [],
    loading: false,
    error: null
  }),

  actions: {
    // 获取租户的MCP服务
    async getMcpService(tenantId) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.get(`/tenants/${tenantId}/mcp/service`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })

        this.mcpService = response.data
        return response.data
      } catch (error) {
        if (error.response?.status === 404) {
          this.mcpService = null
          return null
        }
        this.error = error.response?.data?.error || '获取MCP服务失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 创建MCP服务
    async createMcpService(tenantId) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.post(`/tenants/${tenantId}/mcp/service`, {}, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })

        this.mcpService = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '创建MCP服务失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取MCP工具列表
    async fetchTools(tenantId) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.get(`/tenants/${tenantId}/mcp/tools`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })

        this.tools = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取工具列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 创建MCP工具
    async createTool(tenantId, toolData) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.post(`/tenants/${tenantId}/mcp/tools`, toolData, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })

        this.tools.push(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '创建工具失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 更新MCP工具
    async updateTool(tenantId, toolId, toolData) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.put(`/tenants/${tenantId}/mcp/tools/${toolId}`, toolData, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })

        const index = this.tools.findIndex(t => t._id === toolId)
        if (index !== -1) {
          this.tools[index] = response.data
        }
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '更新工具失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 删除MCP工具
    async deleteTool(tenantId, toolId) {
      this.loading = true
      this.error = null

      try {
        await axios.delete(`/tenants/${tenantId}/mcp/tools/${toolId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })

        this.tools = this.tools.filter(t => t._id !== toolId)
        return true
      } catch (error) {
        this.error = error.response?.data?.error || '删除工具失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
