<template>
  <div class="tenant-list-container">
    <el-card class="tenant-list-card">
      <template #header>
        <div class="card-header">
          <h2>租户（商家）管理</h2>
          <el-button type="primary" @click="handleCreateTenant">
            <el-icon><Plus /></el-icon>
            创建租户
          </el-button>
        </div>
      </template>
      
      <el-table :data="tenants" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="租户名称" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="类型" width="120">
          <template #default="scope">
            <el-tag type="info">{{ getTypeName(scope.row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'">
              {{ scope.row.status === 'active' ? '正常' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="400">
          <template #default="scope">
            <el-button size="small" @click="handleViewTenant(scope.row)">
              查看
            </el-button>
            <el-button size="small" type="primary" @click="handleEditTenant(scope.row)">
              编辑
            </el-button>
            <el-button size="small" type="info" @click="handleConfigTenant(scope.row)">
              配置
            </el-button>
            <el-button size="small" type="primary" @click="handleMcpConfig(scope.row)">
              MCP
            </el-button>
            <el-button size="small" type="success" @click="handleSelectTenant(scope.row)">
              SKILL
            </el-button>
            <el-button size="small" type="warning" @click="handleRegenerateApiKey(scope.row)">
              重置密钥
            </el-button>
            <el-button size="small" type="danger" @click="handleDeleteTenant(scope.row._id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑租户' : '创建租户'"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入租户名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入租户描述"
          />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择类型" :disabled="isEdit">
            <el-option label="餐饮实体" value="restaurant_entity" />
          </el-select>
          <div class="form-tip">创建后不可修改，该类型决定了租户下所有Skill的配置模板</div>
        </el-form-item>
        <el-form-item label="状态" prop="status" v-if="isEdit">
          <el-select v-model="form.status" placeholder="请选择状态">
            <el-option label="正常" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- API密钥对话框 -->
    <el-dialog
      v-model="apiKeyDialogVisible"
      title="API密钥"
      width="500px"
    >
      <div v-if="apiKeyData" class="api-key-info">
        <el-alert
          title="请妥善保管API密钥，此信息只显示一次"
          type="warning"
          :closable="false"
          show-icon
        />
        <div class="api-key-item">
          <label>API Key:</label>
          <el-input v-model="apiKeyData.api_key" readonly>
            <template #append>
              <el-button @click="copyToClipboard(apiKeyData.api_key)">复制</el-button>
            </template>
          </el-input>
        </div>
        <div class="api-key-item">
          <label>API Secret:</label>
          <el-input v-model="apiKeyData.api_secret" readonly type="password" show-password>
            <template #append>
              <el-button @click="copyToClipboard(apiKeyData.api_secret)">复制</el-button>
            </template>
          </el-input>
        </div>
      </div>
    </el-dialog>

    <!-- 配置对话框 -->
    <el-dialog
      v-model="configDialogVisible"
      title="租户配置"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-if="currentConfigTenant" class="config-dialog-content">
        <el-alert
          title="以下配置将应用于该租户下的所有Skill"
          type="info"
          :closable="false"
          show-icon
          class="config-info"
        />
        <el-form :model="configForm" ref="configFormRef" label-width="120px">
          <el-form-item label="店名">
            <el-input v-model="configForm.shopName" placeholder="请输入店名" />
          </el-form-item>
          <el-form-item label="地址">
            <el-input v-model="configForm.address" placeholder="请输入地址" />
          </el-form-item>
          <el-form-item label="电话">
            <el-input v-model="configForm.phone" placeholder="请输入电话" />
          </el-form-item>
          <el-form-item label="营业时间">
            <el-input v-model="configForm.businessHours" placeholder="如: 9:00-22:00" />
          </el-form-item>
          <el-form-item label="Wi-Fi密码">
            <el-input v-model="configForm.wifiPassword" placeholder="请输入Wi-Fi密码" />
          </el-form-item>
          <el-form-item label="特色菜品">
            <el-input
              v-model="configForm.specialDishes"
              type="textarea"
              :rows="3"
              placeholder="请输入特色菜品，多个菜品用逗号分隔"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="configDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveConfig" :loading="configSubmitting">
          保存配置
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTenantsStore } from '../../stores/tenants'
import { Plus } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'

const router = useRouter()
const tenantsStore = useTenantsStore()

const loading = ref(false)
const submitting = ref(false)
const tenants = ref([])
const dialogVisible = ref(false)
const apiKeyDialogVisible = ref(false)
const configDialogVisible = ref(false)
const isEdit = ref(false)
const currentTenantId = ref('')
const apiKeyData = ref(null)
const currentConfigTenant = ref(null)
const configSubmitting = ref(false)

const formRef = ref(null)
const configFormRef = ref(null)
const form = reactive({
  name: '',
  description: '',
  type: 'restaurant_entity',
  status: 'active'
})

const configForm = reactive({
  shopName: '',
  address: '',
  phone: '',
  businessHours: '',
  wifiPassword: '',
  specialDishes: ''
})

const rules = {
  name: [
    { required: true, message: '请输入租户名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在2-50个字符之间', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择类型', trigger: 'blur' }
  ]
}

const getTypeName = (type) => {
  const typeMap = {
    'restaurant_entity': '餐饮实体'
  }
  return typeMap[type] || type
}

const fetchTenants = async () => {
  loading.value = true
  try {
    tenants.value = await tenantsStore.fetchTenants()
  } catch (error) {
    console.error('获取租户列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleCreateTenant = () => {
  isEdit.value = false
  currentTenantId.value = ''
  form.name = ''
  form.description = ''
  form.type = 'restaurant_entity'
  form.status = 'active'
  dialogVisible.value = true
}

const handleEditTenant = (tenant) => {
  isEdit.value = true
  currentTenantId.value = tenant._id
  form.name = tenant.name
  form.description = tenant.description || ''
  form.type = tenant.type || 'restaurant_entity'
  form.status = tenant.status
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          await tenantsStore.updateTenant(currentTenantId.value, form)
          ElMessage.success('更新成功')
        } else {
          const result = await tenantsStore.createTenant(form)
          ElMessage.success('创建成功')
          // 显示API密钥
          apiKeyData.value = {
            api_key: result.api_key,
            api_secret: result.api_secret
          }
          apiKeyDialogVisible.value = true
        }
        dialogVisible.value = false
        fetchTenants()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleDeleteTenant = (id) => {
  ElMessageBox.confirm('确定要删除这个租户吗？删除后该租户下的所有Skill也会被删除。', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await tenantsStore.deleteTenant(id)
      ElMessage.success('删除成功')
      fetchTenants()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const handleRegenerateApiKey = async (tenant) => {
  try {
    const result = await tenantsStore.regenerateApiKey(tenant._id)
    apiKeyData.value = result
    apiKeyDialogVisible.value = true
    ElMessage.success('API密钥已重新生成')
    fetchTenants()
  } catch (error) {
    ElMessage.error('重新生成API密钥失败')
  }
}

const handleSelectTenant = (tenant) => {
  tenantsStore.setCurrentTenant(tenant)
  ElMessage.success(`已切换到租户: ${tenant.name}`)
  router.push('/skills')
}

const handleViewTenant = (tenant) => {
  tenantsStore.setCurrentTenant(tenant)
  router.push(`/tenants/${tenant._id}`)
}

const handleMcpConfig = (tenant) => {
  tenantsStore.setCurrentTenant(tenant)
  router.push('/mcp')
}

const handleConfigTenant = (tenant) => {
  currentConfigTenant.value = tenant
  // 加载现有配置
  const config = tenant.config || {}
  configForm.shopName = config.shopName || ''
  configForm.address = config.address || ''
  configForm.phone = config.phone || ''
  configForm.businessHours = config.businessHours || ''
  configForm.wifiPassword = config.wifiPassword || ''
  configForm.specialDishes = config.specialDishes || ''
  configDialogVisible.value = true
}

const handleSaveConfig = async () => {
  if (!currentConfigTenant.value) return

  configSubmitting.value = true
  try {
    await tenantsStore.updateTenant(currentConfigTenant.value._id, {
      config: { ...configForm }
    })
    ElMessage.success('配置保存成功')
    configDialogVisible.value = false
    fetchTenants()
  } catch (error) {
    ElMessage.error('配置保存失败')
  } finally {
    configSubmitting.value = false
  }
}

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

onMounted(() => {
  fetchTenants()
})
</script>

<style scoped>
.tenant-list-container {
  padding: 20px 0;
}

.tenant-list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.api-key-info {
  padding: 20px;
}

.api-key-item {
  margin-top: 20px;
}

.api-key-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #303133;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.config-dialog-content {
  padding: 10px 0;
}

.config-info {
  margin-bottom: 20px;
}
</style>
