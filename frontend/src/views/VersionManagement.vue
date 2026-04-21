<template>
  <div class="version-management-container">
    <el-card class="version-management-card">
      <template #header>
        <div class="card-header">
          <h2>版本管理</h2>
        </div>
      </template>
      
      <div class="filter-container">
        <el-select v-model="selectedSkill" placeholder="选择Skill" @change="handleSkillChange">
          <el-option 
            v-for="skill in skills" 
            :key="skill._id" 
            :label="skill.name" 
            :value="skill._id"
          />
        </el-select>
      </div>
      
      <el-table :data="versions" style="width: 100%" v-loading="loading">
        <el-table-column prop="version" label="版本号" />
        <el-table-column prop="changes" label="变更描述" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="handleRollback(scope.row)">
              回滚
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useSkillsStore } from '../stores/skills'
import { ElMessage, ElMessageBox } from 'element-plus'

const skillsStore = useSkillsStore()

const skills = ref([])
const selectedSkill = ref('')
const versions = ref([])
const loading = ref(false)

const fetchSkills = async () => {
  try {
    const result = await skillsStore.fetchSkills()
    skills.value = result.skills
  } catch (error) {
    console.error('获取Skill列表失败:', error)
  }
}

const fetchVersions = async () => {
  if (!selectedSkill.value) return
  
  loading.value = true
  try {
    versions.value = await skillsStore.fetchVersions(selectedSkill.value)
  } catch (error) {
    console.error('获取版本历史失败:', error)
  } finally {
    loading.value = false
  }
}

const handleRollback = (version) => {
  ElMessageBox.confirm(`确定要回滚到版本 ${version.version} 吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      // 这里应该实现版本回滚的逻辑
      // 暂时只是模拟操作
      ElMessage.success('回滚成功')
    } catch (error) {
      ElMessage.error('回滚失败')
    }
  })
}

// 监听Skill选择变化
const handleSkillChange = () => {
  fetchVersions()
}

onMounted(() => {
  fetchSkills()
})
</script>

<style scoped>
.version-management-container {
  padding: 20px 0;
}

.version-management-card {
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

.filter-container {
  margin-bottom: 20px;
  width: 300px;
}
</style>
