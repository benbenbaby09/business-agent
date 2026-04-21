<template>
  <div class="dashboard-container">
    <el-card class="dashboard-card">
      <template #header>
        <div class="card-header">
          <h2>仪表盘</h2>
        </div>
      </template>
      
      <div class="stats-container">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ totalSkills }}</div>
                <div class="stat-label">总Skill数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ publishedSkills }}</div>
                <div class="stat-label">已发布Skill</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-number">{{ draftSkills }}</div>
                <div class="stat-label">草稿Skill</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <div class="recent-activities">
        <h3>最近活动</h3>
        <el-table :data="recentActivities" style="width: 100%">
          <el-table-column prop="type" label="活动类型" width="120" />
          <el-table-column prop="skillName" label="Skill名称" />
          <el-table-column prop="time" label="时间" width="180" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useSkillsStore } from '../stores/skills'

const skillsStore = useSkillsStore()

const totalSkills = ref(0)
const publishedSkills = ref(0)
const draftSkills = ref(0)
const recentActivities = ref([
  { type: '创建', skillName: '智能客服', time: '2026-04-20 14:30' },
  { type: '发布', skillName: '订单管理', time: '2026-04-19 10:15' },
  { type: '更新', skillName: '库存查询', time: '2026-04-18 09:45' }
])

onMounted(async () => {
  try {
    // 获取Skill统计信息
    const skills = await skillsStore.fetchSkills()
    totalSkills.value = skills.total
    
    // 计算已发布和草稿的Skill数量
    publishedSkills.value = skills.skills.filter(skill => skill.status === 'published').length
    draftSkills.value = skills.skills.filter(skill => skill.status === 'draft').length
  } catch (error) {
    console.error('获取仪表盘数据失败:', error)
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px 0;
}

.dashboard-card {
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

.stats-container {
  margin-bottom: 30px;
}

.stat-card {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-content {
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.recent-activities {
  margin-top: 30px;
}

.recent-activities h3 {
  margin-bottom: 15px;
  font-size: 16px;
  color: #303133;
}
</style>
