<template>
  <div class="skill-list-container">
    <el-card class="skill-list-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h2>Skill管理</h2>
            <el-select v-model="selectedTenantId" @change="handleTenantChange" placeholder="选择商家" class="tenant-select">
              <el-option
                v-for="tenant in tenants"
                :key="tenant._id"
                :label="tenant.name"
                :value="tenant._id"
              />
            </el-select>
            <el-tag v-if="currentTenant" type="success" class="tenant-tag">
              当前商家: {{ currentTenant.name }}
            </el-tag>
            <el-tag v-else type="warning" class="tenant-tag">
              未选择商家
            </el-tag>
          </div>
          <el-button type="primary" @click="handleCreateSkill" :disabled="!currentTenant">
            <el-icon><Plus /></el-icon>
            创建Skill
          </el-button>
        </div>
      </template>
      
      <!-- 未选择租户提示 -->
      <el-alert
        v-if="!currentTenant"
        title="未选择租户"
        description="请先前往租户管理页面选择一个租户，才能查看和管理该租户下的Skill"
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
      
      <div class="filter-container">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-select v-model="filter.status" placeholder="状态">
              <el-option label="全部" value="" />
              <el-option label="开启" value="active" />
              <el-option label="停用" value="inactive" />
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-select v-model="filter.type" placeholder="类型">
                <el-option label="全部" value="" />
                <el-option label="餐饮实体" value="restaurant_entity" />
              </el-select>
          </el-col>
          <el-col :span="8">
            <el-input v-model="filter.keyword" placeholder="搜索名称" clearable>
              <template #append>
                <el-button @click="handleSearch">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
          </el-col>
        </el-row>
      </div>
      
      <el-table :data="skills" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="名称" />
        <el-table-column label="类型">
          <template #default="scope">
            {{ getTypeName(scope.row.type) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'warning'">
              {{ scope.row.status === 'active' ? '开启' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="280">
          <template #default="scope">
            <el-button size="small" @click="handleViewSkill(scope.row._id)">
              查看
            </el-button>
            <el-button size="small" type="primary" @click="handleEditSkill(scope.row._id)">
              编辑
            </el-button>
            <el-button size="small" type="success" @click="handleConfigSkill(scope.row)">
              配置
            </el-button>
            <el-button size="small" type="danger" @click="handleDeleteSkill(scope.row._id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="limit"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 配置对话框 -->
    <el-dialog
      v-model="configDialogVisible"
      title="Skill配置"
      width="600px"
      :close-on-click-modal="false"
      @closed="handleDialogClosed"
    >
      <div v-if="currentSkill" class="config-dialog-content">
        <h4>{{ currentSkill.name }} - 配置信息</h4>
        <DynamicForm
          v-if="currentSkill && currentSkill.type"
          ref="configFormRef"
          :template-type="currentSkill.type"
          :initial-data="currentSkill.config || {}"
          submit-text="保存配置"
          @submit="handleConfigSubmit"
          @reset="handleConfigReset"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useSkillsStore } from '../../stores/skills'
import { useTenantsStore } from '../../stores/tenants'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import DynamicForm from '../../components/DynamicForm.vue'

const router = useRouter()
const skillsStore = useSkillsStore()
const tenantsStore = useTenantsStore()

const loading = ref(false)
const skills = ref([])
const total = ref(0)
const page = ref(1)
const limit = ref(10)
const tenants = ref([])
const selectedTenantId = ref('')

// 当前选中的租户
const currentTenant = computed(() => tenantsStore.currentTenant)

// 配置对话框
const configDialogVisible = ref(false)
const currentSkill = ref(null)
const configFormRef = ref(null)

const filter = ref({
  status: '',
  type: '',
  keyword: ''
})

const getTypeName = (type) => {
  const typeMap = {
    'restaurant_entity': '餐饮实体'
  }
  return typeMap[type] || type
}

const fetchSkills = async () => {
  loading.value = true
  try {
    const tenantId = currentTenant.value ? currentTenant.value._id : ''
    const result = await skillsStore.fetchSkills(
      page.value, 
      limit.value, 
      filter.value.status, 
      filter.value.type,
      tenantId
    )
    skills.value = result.skills
    total.value = result.total
  } catch (error) {
    console.error('获取Skill列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleCreateSkill = () => {
  router.push('/skills/create')
}

const handleViewSkill = (id) => {
  router.push(`/skills/${id}`)
}

const handleEditSkill = (id) => {
  router.push(`/skills/${id}/edit`)
}

// 打开配置对话框
const handleConfigSkill = (skill) => {
  currentSkill.value = skill
  configDialogVisible.value = true
}

// 保存配置
const handleConfigSubmit = async (configData) => {
  try {
    const updateData = {
      name: currentSkill.value.name,
      description: currentSkill.value.description,
      type: currentSkill.value.type,
      status: currentSkill.value.status,
      config: configData
    }
    await skillsStore.updateSkill(currentSkill.value._id, updateData)
    ElMessage.success('配置保存成功')
    configDialogVisible.value = false
    fetchSkills()
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('配置保存失败')
  }
}

// 重置配置
const handleConfigReset = () => {
  if (configFormRef.value) {
    configFormRef.value.resetFields()
  }
}

// 对话框关闭时的处理
const handleDialogClosed = () => {
  currentSkill.value = null
}

const handleDeleteSkill = (id) => {
  ElMessageBox.confirm('确定要删除这个Skill吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await skillsStore.deleteSkill(id)
      ElMessage.success('删除成功')
      fetchSkills()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const handleSearch = () => {
  page.value = 1
  fetchSkills()
}

const handleSizeChange = (size) => {
  limit.value = size
  fetchSkills()
}

const handleCurrentChange = (current) => {
  page.value = current
  fetchSkills()
}

// 获取商家列表
const fetchTenants = async () => {
  try {
    await tenantsStore.fetchTenants()
    tenants.value = tenantsStore.tenants
    if (currentTenant.value) {
      selectedTenantId.value = currentTenant.value._id
    }
  } catch (error) {
    console.error('获取商家列表失败:', error)
  }
}

// 处理商家选择变化
const handleTenantChange = async (tenantId) => {
  try {
    const tenant = tenants.value.find(t => t._id === tenantId)
    if (tenant) {
      await tenantsStore.setCurrentTenant(tenant)
      page.value = 1
      await fetchSkills()
    }
  } catch (error) {
    console.error('切换商家失败:', error)
  }
}

onMounted(async () => {
  await fetchTenants()
  fetchSkills()
})
</script>

<style scoped>
.skill-list-container {
  padding: 20px 0;
}

.skill-list-card {
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

.tenant-select {
  margin-left: 20px;
  width: 200px;
}

.tenant-tag {
  margin-left: 10px;
}

.filter-container {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.config-dialog-content {
  padding: 20px 0;
}

.config-dialog-content h4 {
  margin-bottom: 20px;
  font-size: 16px;
  color: #303133;
}
</style>
