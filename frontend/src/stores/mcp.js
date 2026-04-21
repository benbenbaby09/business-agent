import { defineStore } from 'pinia'
import axios from '../utils/axios'

export const useMcpStore = defineStore('mcp', {
  state: () => ({
    mcpService: null,
    contexts: [],
    stats: null,
    loading: false,
    error: null
  }),

  actions: {
    // 获取租户的MCP服务信息
    async getMcpService(tenantId) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.get(`/tenants/${tenantId}/mcp`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })

        this.mcpService = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取MCP服务信息失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 重新生成MCP API密钥
    async regenerateKeys(tenantId) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.post(`/tenants/${tenantId}/mcp/regenerate-keys`, {}, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })

        if (this.mcpService) {
          this.mcpService.api_key = response.data.api_key
          this.mcpService.api_secret = response.data.api_secret
        }

        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '重新生成密钥失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取MCP上下文列表
    async fetchContexts(tenantId) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.get(`/tenants/${tenantId}/mcp/contexts`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })

        this.contexts = response.data.contexts
        return response.data.contexts
      } catch (error) {
        this.error = error.response?.data?.error || '获取上下文列表失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 创建MCP上下文
    async createContext(tenantId, contextData) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.post(`/tenants/${tenantId}/mcp/contexts`, contextData, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })

        this.contexts.unshift(response.data)
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '创建上下文失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 删除MCP上下文
    async deleteContext(tenantId, contextId) {
      this.loading = true
      this.error = null

      try {
        await axios.delete(`/tenants/${tenantId}/mcp/contexts/${contextId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })

        this.contexts = this.contexts.filter(ctx => ctx.id !== contextId)
        return true
      } catch (error) {
        this.error = error.response?.data?.error || '删除上下文失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取MCP统计信息
    async getStats(tenantId) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.get(`/tenants/${tenantId}/mcp/stats`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        })

        this.stats = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || '获取统计信息失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
