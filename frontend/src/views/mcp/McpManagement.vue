<template>
  <div class="mcp-management-container">
    <el-card class="mcp-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h2>MCP服务管理</h2>
            <el-tag v-if="currentTenant" type="success" class="tenant-tag">
              当前租户: {{ currentTenant.name }}
            </el-tag>
            <el-tag v-else type="warning" class="tenant-tag">
              未选择租户
            </el-tag>
          </div>
        </div>
      </template>

      <!-- 未选择租户提示 -->
      <el-alert
        v-if="!currentTenant"
        title="未选择租户"
        description="请先前往租户管理页面选择一个租户，才能管理该租户的MCP服务"
        type="warning"
        show-icon
        :closable="false"
        class="tenant-alert"
      >
        <template #default>
          <el-button type="primary" size="small" @click="router.push('/tenants')">
            前往租户管理
          </el-button>
        </template>
      </el-alert>

      <div v-else>
        <!-- 未创建服务状态 -->
        <div v-if="!mcpService" class="create-service-section">
          <el-empty description="该租户尚未创建MCP服务">
            <el-button type="primary" @click="handleCreateService" :loading="creating">
              <el-icon><Plus /></el-icon>
              创建MCP服务
            </el-button>
          </el-empty>
        </div>

        <!-- 已创建服务状态 -->
        <div v-else v-loading="loading">
          <!-- MCP服务信息 -->
          <div class="mcp-info-section">
            <h3>MCP服务信息</h3>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="服务名称">{{ mcpService.name }}</el-descriptions-item>
              <el-descriptions-item label="服务ID">{{ mcpService.id }}</el-descriptions-item>
              <el-descriptions-item label="服务状态">
                <el-tag :type="mcpService.status === 'active' ? 'success' : 'warning'">
                  {{ mcpService.status === 'active' ? '运行中' : '已暂停' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ formatDate(mcpService.created_at) }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 接口配置管理 -->
          <div class="tools-section">
            <div class="section-header">
              <h3>接口配置</h3>
              <el-button type="primary" @click="handleCreateTool">
                <el-icon><Plus /></el-icon>
                添加接口
              </el-button>
            </div>

            <el-table :data="tools" style="width: 100%">
              <el-table-column prop="name" label="接口名称" />
              <el-table-column prop="title" label="标题" />
              <el-table-column prop="type" label="类型" width="120">
                <template #default="scope">
                  <el-tag type="info">{{ getTypeName(scope.row.type) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="scope">
                  <el-button size="small" @click="handleViewTool(scope.row)">
                    查看
                  </el-button>
                  <el-button size="small" type="primary" @click="handleEditTool(scope.row)">
                    编辑
                  </el-button>
                  <el-button size="small" type="danger" @click="handleDeleteTool(scope.row)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 生成完整配置 -->
          <div class="generate-section">
            <el-button type="success" @click="handleGenerateFullConfig">
              <el-icon><DocumentCopy /></el-icon>
              生成完整MCP配置
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 创建/编辑接口对话框 -->
    <el-dialog
      v-model="toolDialogVisible"
      :title="isEdit ? '编辑接口' : '添加接口'"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form :model="toolForm" :rules="toolRules" ref="toolFormRef" label-width="100px">
        <el-form-item label="类型" prop="type">
          <el-select v-model="toolForm.type" placeholder="请选择类型" :disabled="isEdit" @change="handleTypeChange">
            <el-option label="餐厅基本信息" value="restaurant_entity" />
            <el-option label="堂食排队取号" value="queue_info" />
          </el-select>
        </el-form-item>
        <el-form-item label="接口名称" prop="name">
          <el-input v-model="toolForm.name" placeholder="如: get_restaurant_info" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="标题" prop="title">
          <el-input v-model="toolForm.title" placeholder="如: 餐厅基本信息" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="toolForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入接口描述"
          />
        </el-form-item>

        <!-- 餐厅基本信息配置 -->
        <div v-if="toolForm.type === 'restaurant_entity'" class="config-section">
          <h4>餐厅基本信息配置</h4>
          <el-form-item label="餐厅名称">
            <el-input v-model="toolForm.config.restaurantName" placeholder="请输入餐厅名称" />
          </el-form-item>
          <el-form-item label="餐厅介绍">
            <el-input
              v-model="toolForm.config.restaurantIntro"
              type="textarea"
              :rows="3"
              placeholder="请输入餐厅介绍"
            />
          </el-form-item>
          <el-form-item label="营业时间">
            <el-input v-model="toolForm.config.businessHours" placeholder="如: 9:00-22:00" />
          </el-form-item>

          <!-- 门店列表 -->
          <div class="locations-section">
            <div class="section-header">
              <span>门店列表</span>
              <el-button type="primary" size="small" @click="addLocation">
                <el-icon><Plus /></el-icon>
                添加门店
              </el-button>
            </div>
            <div
              v-for="(location, index) in toolForm.config.locations"
              :key="index"
              class="location-item"
            >
              <el-card shadow="never">
                <template #header>
                  <div class="location-header">
                    <span>门店 {{ index + 1 }}</span>
                    <el-button type="danger" size="small" @click="removeLocation(index)">
                      删除
                    </el-button>
                  </div>
                </template>
                <el-form-item label="门店名称">
                  <el-input v-model="location.name" placeholder="请输入门店名称" />
                </el-form-item>
                <el-form-item label="门店地址">
                  <el-input v-model="location.address" placeholder="请输入门店地址" />
                </el-form-item>
              </el-card>
            </div>
          </div>
        </div>

        <!-- 堂食排队取号配置 -->
        <div v-if="toolForm.type === 'queue_info'" class="config-section">
          <h4>堂食排队取号配置</h4>
          <el-form-item label="服务说明">
            <el-input
              v-model="toolForm.config.queueDescription"
              type="textarea"
              :rows="3"
              placeholder="请输入服务说明"
            />
          </el-form-item>

          <!-- 取号方式列表 -->
          <div class="queue-methods-section">
            <div class="section-header">
              <span>取号方式</span>
              <el-button type="primary" size="small" @click="addQueueMethod">
                <el-icon><Plus /></el-icon>
                添加
              </el-button>
            </div>
            <div
              v-for="(method, index) in toolForm.config.queueMethods"
              :key="index"
              class="queue-method-item"
            >
              <el-card shadow="never">
                <template #header>
                  <div class="queue-method-header">
                    <span>方式 {{ index + 1 }}</span>
                    <el-button type="danger" size="small" @click="removeQueueMethod(index)">
                      删除
                    </el-button>
                  </div>
                </template>
                <el-form-item>
                  <el-input v-model="toolForm.config.queueMethods[index]" placeholder="如: 微信小程序搜索'美味不用等'" />
                </el-form-item>
              </el-card>
            </div>
          </div>

          <!-- 支持门店列表 -->
          <div class="queue-stores-section">
            <div class="section-header">
              <span>支持门店</span>
              <el-button type="primary" size="small" @click="addQueueStore">
                <el-icon><Plus /></el-icon>
                添加
              </el-button>
            </div>
            <div
              v-for="(store, index) in toolForm.config.queueStores"
              :key="index"
              class="queue-store-item"
            >
              <el-card shadow="never">
                <template #header>
                  <div class="queue-store-header">
                    <span>门店 {{ index + 1 }}</span>
                    <el-button type="danger" size="small" @click="removeQueueStore(index)">
                      删除
                    </el-button>
                  </div>
                </template>
                <el-form-item>
                  <el-input v-model="toolForm.config.queueStores[index]" placeholder="如: 金谷园饺子馆（总店）" />
                </el-form-item>
              </el-card>
            </div>
          </div>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="toolDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitTool" :loading="submitting">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 生成完整配置对话框 -->
    <el-dialog
      v-model="fullConfigDialogVisible"
      title="完整MCP配置"
      width="900px"
      :close-on-click-modal="false"
    >
      <div v-if="fullConfig" class="json-preview">
        <el-alert
          title="以下是完整的MCP服务配置JSON"
          type="info"
          :closable="false"
          show-icon
          class="json-info"
        />
        <pre class="json-code">{{ JSON.stringify(fullConfig, null, 2) }}</pre>
        <div class="json-actions">
          <el-button type="primary" @click="copyFullConfig">
            <el-icon><DocumentCopy /></el-icon>
            复制JSON
          </el-button>
          <el-button @click="downloadFullConfig">
            <el-icon><Download /></el-icon>
            下载JSON
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useTenantsStore } from '../../stores/tenants'
import { useMcpServicesStore } from '../../stores/mcpServices'
import { Plus, DocumentCopy, Download } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const tenantsStore = useTenantsStore()
const mcpServicesStore = useMcpServicesStore()

const currentTenant = computed(() => tenantsStore.currentTenant)

const loading = computed(() => mcpServicesStore.loading)
const creating = ref(false)
const submitting = ref(false)
const mcpService = computed(() => mcpServicesStore.mcpService)
const tools = computed(() => mcpServicesStore.tools)

const toolDialogVisible = ref(false)
const fullConfigDialogVisible = ref(false)
const isEdit = ref(false)
const currentToolId = ref('')
const fullConfig = ref(null)

const toolFormRef = ref(null)
const toolForm = reactive({
  name: '',
  title: '',
  type: 'restaurant_entity',
  description: '',
  config: {
    restaurantName: '',
    restaurantIntro: '',
    businessHours: '',
    locations: [],
    queueDescription: '',
    queueMethods: [],
    queueStores: []
  }
})

const toolRules = {
  name: [
    { required: true, message: '请输入接口名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在2-50个字符之间', trigger: 'blur' }
  ],
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择类型', trigger: 'blur' }
  ]
}

const getTypeName = (type) => {
  const typeMap = {
    'restaurant_entity': '餐厅基本信息',
    'queue_info': '堂食排队取号'
  }
  return typeMap[type] || type
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 从API加载MCP服务
const loadMcpService = async () => {
  if (!currentTenant.value) return
  try {
    await mcpServicesStore.getMcpService(currentTenant.value._id)
  } catch (error) {
    // 404表示服务不存在，这是正常的
    console.log('MCP service not found')
  }
}

// 从API加载工具列表
const loadTools = async () => {
  if (!currentTenant.value || !mcpService.value) return
  try {
    await mcpServicesStore.fetchTools(currentTenant.value._id)
  } catch (error) {
    console.error('加载工具列表失败:', error)
  }
}

// 创建MCP服务
const handleCreateService = async () => {
  creating.value = true
  try {
    await mcpServicesStore.createMcpService(currentTenant.value._id)
    ElMessage.success('MCP服务创建成功')
  } catch (error) {
    ElMessage.error('创建失败: ' + (error.response?.data?.error || '未知错误'))
  } finally {
    creating.value = false
  }
}

const handleCreateTool = () => {
  isEdit.value = false
  currentToolId.value = ''
  toolForm.type = 'restaurant_entity'
  
  // 触发类型变化，自动填充默认值
  handleTypeChange('restaurant_entity')
  
  toolDialogVisible.value = true
}

const handleEditTool = (tool) => {
  isEdit.value = true
  currentToolId.value = tool.id
  toolForm.name = tool.name
  toolForm.title = tool.title
  toolForm.type = tool.type
  toolForm.description = tool.description || ''
  toolForm.config = JSON.parse(JSON.stringify(tool.config))
  toolDialogVisible.value = true
}

const addLocation = () => {
  toolForm.config.locations.push({ name: '', address: '' })
}

const removeLocation = (index) => {
  toolForm.config.locations.splice(index, 1)
}

// 类型变化时自动填充默认值
const handleTypeChange = (type) => {
  if (isEdit.value) return // 编辑模式不自动填充
  
  const tenantConfig = currentTenant.value?.config || {}
  
  if (type === 'restaurant_entity') {
    toolForm.name = 'get_restaurant_info'
    toolForm.title = '餐厅基本信息'
    toolForm.description = `获取${tenantConfig.shopName || '餐厅'}基本信息，包括门店地址和营业时间。当用户询问餐厅在哪、几点营业等基本问题时使用。仅返回硬编码的静态数据。`
    
    // 重置配置
    toolForm.config = {
      restaurantName: tenantConfig.shopName || '',
      restaurantIntro: tenantConfig.specialDishes || '',
      businessHours: tenantConfig.businessHours || '',
      locations: [],
      queueDescription: '',
      queueMethods: [],
      queueStores: []
    }
    
    // 如果租户有地址，添加为默认门店
    if (tenantConfig.address) {
      toolForm.config.locations.push({
        name: tenantConfig.shopName || '总店',
        address: tenantConfig.address
      })
    }
  } else if (type === 'queue_info') {
    toolForm.name = 'get_queue_info'
    toolForm.title = '堂食排队取号'
    toolForm.description = `获取${tenantConfig.shopName || '餐厅'}堂食排队取号方式。当用户询问怎么排队、怎么取号、怎么到店吃时使用。仅返回硬编码的静态数据。`
    
    // 重置配置
    toolForm.config = {
      restaurantName: '',
      restaurantIntro: '',
      businessHours: '',
      locations: [],
      queueDescription: '',
      queueMethods: [],
      queueStores: []
    }
  }
}

const addQueueMethod = () => {
  toolForm.config.queueMethods.push('')
}

const removeQueueMethod = (index) => {
  toolForm.config.queueMethods.splice(index, 1)
}

const addQueueStore = () => {
  toolForm.config.queueStores.push('')
}

const removeQueueStore = (index) => {
  toolForm.config.queueStores.splice(index, 1)
}

const handleSubmitTool = async () => {
  if (!toolFormRef.value) return

  const valid = await toolFormRef.value.validate().catch(() => false)
  if (!valid) return

  if (toolForm.type === 'restaurant_entity' && toolForm.config.locations.length === 0) {
    ElMessage.error('请至少添加一个门店')
    return
  }

  submitting.value = true
  try {
    const toolData = {
      name: toolForm.name,
      title: toolForm.title,
      type: toolForm.type,
      description: toolForm.description,
      config: JSON.parse(JSON.stringify(toolForm.config))
    }

    if (isEdit.value) {
      await mcpServicesStore.updateTool(currentTenant.value._id, currentToolId.value, toolData)
    } else {
      await mcpServicesStore.createTool(currentTenant.value._id, toolData)
    }

    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
    toolDialogVisible.value = false
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

const handleViewTool = (tool) => {
  handleEditTool(tool)
}

const handleDeleteTool = (tool) => {
  ElMessageBox.confirm(`确定要删除接口 "${tool.title}" 吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await mcpServicesStore.deleteTool(currentTenant.value._id, tool._id)
      ElMessage.success('删除成功')
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const handleGenerateFullConfig = () => {
  // 生成完整的MCP服务配置
  const toolsConfig = tools.value.map(tool => {
    if (tool.type === 'queue_info') {
      return {
        name: tool.name,
        title: tool.title,
        description: tool.description,
        inputSchema: {
          $schema: 'http://json-schema.org/draft-07/schema#',
          type: 'object',
          properties: {}
        },
        annotations: {
          readOnlyHint: true,
          destructiveHint: false,
          idempotentHint: true,
          openWorldHint: false
        },
        execution: {
          taskSupport: 'forbidden'
        },
        outputSchema: {
          type: 'object',
          properties: {
            '说明': { type: 'string', description: '服务说明' },
            '取号方式': { type: 'array', items: { type: 'string' }, description: '可用的取号渠道列表' },
            '门店': { type: 'array', items: { type: 'string' }, description: '支持的门店列表' }
          },
          required: ['说明', '取号方式', '门店'],
          additionalProperties: false,
          $schema: 'http://json-schema.org/draft-07/schema#'
        },
        data: {
          '说明': tool.config.queueDescription,
          '取号方式': tool.config.queueMethods,
          '门店': tool.config.queueStores
        }
      }
    } else {
      return {
        name: tool.name,
        title: tool.title,
        description: tool.description,
        inputSchema: {
          $schema: 'http://json-schema.org/draft-07/schema#',
          type: 'object',
          properties: {}
        },
        annotations: {
          readOnlyHint: true,
          destructiveHint: false,
          idempotentHint: true,
          openWorldHint: false
        },
        execution: {
          taskSupport: 'forbidden'
        },
        outputSchema: {
          type: 'object',
          properties: {
            name: { type: 'string', description: '餐厅名称' },
            intro: { type: 'string', description: '餐厅介绍' },
            hours: { type: 'string', description: '营业时间' },
            locations: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  name: { type: 'string', description: '门店名称' },
                  address: { type: 'string', description: '门店地址' }
                },
                required: ['name', 'address'],
                additionalProperties: false
              },
              description: '门店列表'
            }
          },
          required: ['name', 'intro', 'hours', 'locations'],
          additionalProperties: false,
          $schema: 'http://json-schema.org/draft-07/schema#'
        },
        data: {
          name: tool.config.restaurantName,
          intro: tool.config.restaurantIntro,
          hours: tool.config.businessHours,
          locations: tool.config.locations
        }
      }
    }
  })

  fullConfig.value = {
    name: mcpService.value.name,
    version: '1.0.0',
    description: `${currentTenant.value.name}的MCP服务`,
    tools: toolsConfig
  }
  fullConfigDialogVisible.value = true
}

const copyFullConfig = () => {
  navigator.clipboard.writeText(JSON.stringify(fullConfig.value, null, 2)).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

const downloadFullConfig = () => {
  const blob = new Blob([JSON.stringify(fullConfig.value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `mcp_service_${mcpService.value.id}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  ElMessage.success('下载成功')
}

watch(currentTenant, async (newTenant) => {
  if (newTenant) {
    await loadMcpService()
    await loadTools()
  }
}, { immediate: true })

onMounted(async () => {
  if (currentTenant.value) {
    await loadMcpService()
    await loadTools()
  }
})
</script>

<style scoped>
.mcp-management-container {
  padding: 20px 0;
}

.mcp-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.tenant-tag {
  font-size: 12px;
}

.tenant-alert {
  margin-bottom: 20px;
}

.create-service-section {
  padding: 60px 0;
}

.mcp-info-section {
  margin-bottom: 30px;
}

.mcp-info-section h3 {
  margin-bottom: 20px;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.tools-section {
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.generate-section {
  margin-top: 30px;
  text-align: center;
}

.config-section {
  margin-top: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.config-section h4 {
  margin-bottom: 20px;
  font-size: 14px;
  color: #303133;
  font-weight: 600;
}

.locations-section,
.queue-methods-section,
.queue-stores-section {
  margin-top: 20px;
}

.location-item,
.queue-method-item,
.queue-store-item {
  margin-bottom: 15px;
}

.location-header,
.queue-method-header,
.queue-store-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.json-preview {
  padding: 10px 0;
}

.json-info {
  margin-bottom: 15px;
}

.json-code {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
  line-height: 1.6;
  overflow-x: auto;
  max-height: 500px;
  overflow-y: auto;
}

.json-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}
</style>
