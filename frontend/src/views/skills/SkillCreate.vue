<template>
  <div class="skill-create-container">
    <el-card class="skill-create-card">
      <template #header>
        <div class="card-header">
          <h2>{{ isEdit ? '编辑Skill' : '创建Skill' }}</h2>
          <div v-if="currentTenant" class="tenant-info">
            <el-tag type="info">租户: {{ currentTenant.name }}</el-tag>
            <el-tag type="warning" class="type-tag" v-if="currentTenant.type">租户类型参考: {{ getTypeName(currentTenant.type) }}</el-tag>
          </div>
        </div>
      </template>
      
      <!-- 未选择租户提示 -->
      <el-alert
        v-if="!currentTenant && !isEdit"
        title="请先选择租户"
        description="创建Skill前需要先在租户管理页面选择一个租户"
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
      
      <!-- 基础信息 -->
      <el-form
        :model="basicForm"
        :rules="basicRules"
        ref="basicFormRef"
        label-width="100px"
        class="basic-form"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="basicForm.name" placeholder="请输入Skill名称" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="basicForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入Skill描述"
          />
        </el-form-item>
        
        <el-form-item label="类型" prop="type">
          <el-select v-model="basicForm.type" placeholder="请选择Skill类型">
            <el-option label="餐饮实体" value="restaurant_entity" />
          </el-select>
          <div class="form-tip">Skill类型可自由选择，租户类型仅供参考</div>
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-select v-model="basicForm.status" placeholder="请选择状态">
            <el-option label="开启" value="active" />
            <el-option label="停用" value="inactive" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="所属租户" prop="tenant_id" v-if="isEdit">
          <el-input v-model="basicForm.tenant_id" disabled />
        </el-form-item>
      </el-form>
      
      <!-- 租户配置信息展示 -->
      <div class="tenant-config-section" v-if="currentTenant">
        <h3>租户配置信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="店名">{{ currentTenant.config?.shopName || '-' }}</el-descriptions-item>
          <el-descriptions-item label="地址">{{ currentTenant.config?.address || '-' }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ currentTenant.config?.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="营业时间">{{ currentTenant.config?.businessHours || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Wi-Fi密码">{{ currentTenant.config?.wifiPassword || '-' }}</el-descriptions-item>
          <el-descriptions-item label="特色菜品">{{ currentTenant.config?.specialDishes || '-' }}</el-descriptions-item>
        </el-descriptions>
        <div class="config-actions">
          <el-button type="primary" @click="handleSave" :loading="loading">
            {{ isEdit ? '保存' : '创建' }}
          </el-button>
          <el-button @click="handleCancel">取消</el-button>
        </div>
      </div>
      
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        class="error-alert"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSkillsStore } from '../../stores/skills'
import { useTenantsStore } from '../../stores/tenants'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const skillsStore = useSkillsStore()
const tenantsStore = useTenantsStore()
const basicFormRef = ref(null)

const isEdit = ref(false)
const skillId = ref('')
const loading = ref(false)
const error = ref('')

// 当前选中的租户
const currentTenant = computed(() => tenantsStore.currentTenant)

// 基础信息表单
const basicForm = reactive({
  name: '',
  description: '',
  type: 'restaurant_entity',
  status: 'active',
  tenant_id: ''
})

// 获取类型名称
const getTypeName = (type) => {
  const typeMap = {
    'restaurant_entity': '餐饮实体'
  }
  return typeMap[type] || type
}

// 基础信息验证规则
const basicRules = reactive({
  name: [
    {
      required: true,
      message: '请输入Skill名称',
      trigger: 'blur'
    }
  ],
  type: [
    {
      required: true,
      message: '请选择Skill类型',
      trigger: 'blur'
    }
  ],
  status: [
    {
      required: true,
      message: '请选择状态',
      trigger: 'blur'
    }
  ]
})

// 保存Skill
const handleSave = async () => {
  // 先验证基础表单
  const basicValid = await basicFormRef.value.validate().catch(() => false)
  if (!basicValid) return

  // 检查是否选择了租户
  if (!isEdit.value && !currentTenant.value) {
    error.value = '请先选择租户'
    ElMessage.error('请先选择租户')
    return
  }

  loading.value = true
  error.value = ''

  try {
    // Skill使用租户的配置，不再单独存储config
    const skillData = {
      ...basicForm,
      tenant_id: isEdit.value ? basicForm.tenant_id : currentTenant.value._id,
      config: {} // Skill不再存储配置，统一使用租户配置
    }

    if (isEdit.value) {
      await skillsStore.updateSkill(skillId.value, skillData)
      ElMessage.success('更新成功')
    } else {
      await skillsStore.createSkill(skillData)
      ElMessage.success('创建成功')
    }

    router.push('/skills')
  } catch (err) {
    error.value = skillsStore.error || '操作失败'
  } finally {
    loading.value = false
  }
}

// 取消
const handleCancel = () => {
  router.push('/skills')
}

onMounted(async () => {
  // 检查是否是编辑模式
  const id = route.params.id
  if (id) {
    isEdit.value = true
    skillId.value = id

    try {
      const skill = await skillsStore.fetchSkillById(id)
      // 填充基础信息
      Object.assign(basicForm, {
        name: skill.name,
        description: skill.description,
        type: skill.type,
        status: skill.status,
        tenant_id: skill.tenant_id || ''
      })
    } catch (error) {
      console.error('获取Skill详情失败:', error)
    }
  }
})
</script>

<style scoped>
.skill-create-container {
  padding: 20px 0;
}

.skill-create-card {
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tenant-info {
  font-size: 14px;
  display: flex;
  gap: 8px;
}

.type-tag {
  font-size: 12px;
}

.tenant-alert {
  margin-bottom: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.basic-form {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.tenant-config-section {
  margin-top: 20px;
}

.tenant-config-section h3 {
  margin-bottom: 20px;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.config-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.error-alert {
  margin-top: 20px;
}
</style>
