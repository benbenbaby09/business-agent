<template>
  <div class="skill-detail-container">
    <el-card class="skill-detail-card">
      <template #header>
        <div class="card-header">
          <h2>{{ skill?.name }} - 详情</h2>
          <el-button type="primary" @click="handleEditSkill">
            编辑
          </el-button>
        </div>
      </template>
      
      <div class="skill-info">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="名称">{{ skill?.name }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ skill?.description }}</el-descriptions-item>
          <el-descriptions-item label="类型">{{ getTypeName(skill?.type) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="skill?.status === 'active' ? 'success' : 'warning'">
              {{ skill?.status === 'active' ? '开启' : '停用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ skill?.created_at }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ skill?.updated_at }}</el-descriptions-item>
        </el-descriptions>
      </div>
      
      <div class="skill-actions">
        <el-button 
          v-if="skill?.status === 'draft'" 
          type="success" 
          @click="handlePublishSkill"
        >
          发布Skill
        </el-button>
      </div>
      
      <!-- 文件列表 -->
      <div class="files-section">
        <h3>文件列表</h3>
        <el-upload
          class="upload-demo"
          :action="`/api/skills/${skillId}/files`"
          :headers="{ Authorization: `Bearer ${localStorage.getItem('token')}` }"
          :on-success="handleFileUploadSuccess"
          :on-error="handleFileUploadError"
          :auto-upload="true"
        >
          <el-button type="primary">
            <el-icon><Upload /></el-icon>
            上传文件
          </el-button>
        </el-upload>
        
        <el-table :data="files" style="width: 100%" v-loading="filesLoading">
          <el-table-column prop="filename" label="文件名" />
          <el-table-column prop="file_type" label="文件类型" />
          <el-table-column prop="version" label="版本" />
          <el-table-column prop="created_at" label="上传时间" width="180" />
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button size="small" @click="handleDownloadFile(scope.row._id, scope.row.filename)">
                下载
              </el-button>
              <el-button size="small" type="danger" @click="handleDeleteFile(scope.row._id)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 版本历史 -->
      <div class="versions-section">
        <h3>版本历史</h3>
        <el-table :data="versions" style="width: 100%" v-loading="versionsLoading">
          <el-table-column prop="version" label="版本号" />
          <el-table-column prop="changes" label="变更描述" />
          <el-table-column prop="created_at" label="创建时间" width="180" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSkillsStore } from '../../stores/skills'
import { useFilesStore } from '../../stores/files'
import { Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const skillsStore = useSkillsStore()
const filesStore = useFilesStore()

const skillId = ref('')
const skill = ref(null)
const files = ref([])
const versions = ref([])
const loading = ref(false)
const filesLoading = ref(false)
const versionsLoading = ref(false)

const getTypeName = (type) => {
    const typeMap = {
      'restaurant_entity': '餐饮实体'
    }
    return typeMap[type] || type
  }

const handleEditSkill = () => {
  router.push(`/skills/${skillId.value}/edit`)
}

const handlePublishSkill = () => {
  ElMessageBox.prompt('请输入发布说明', '发布Skill', {
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async ( { value } ) => {
    try {
      await skillsStore.publishSkill(skillId.value, value)
      ElMessage.success('发布成功')
      fetchSkillDetail()
    } catch (error) {
      ElMessage.error('发布失败')
    }
  })
}

const handleFileUploadSuccess = (response) => {
  ElMessage.success('上传成功')
  fetchFiles()
}

const handleFileUploadError = () => {
  ElMessage.error('上传失败')
}

const handleDownloadFile = (fileId, filename) => {
  filesStore.downloadFile(skillId.value, fileId, filename)
}

const handleDeleteFile = (fileId) => {
  ElMessageBox.confirm('确定要删除这个文件吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await filesStore.deleteFile(skillId.value, fileId)
      ElMessage.success('删除成功')
      fetchFiles()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const fetchSkillDetail = async () => {
  loading.value = true
  try {
    skill.value = await skillsStore.fetchSkillById(skillId.value)
  } catch (error) {
    console.error('获取Skill详情失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchFiles = async () => {
  filesLoading.value = true
  try {
    files.value = await filesStore.fetchFiles(skillId.value)
  } catch (error) {
    console.error('获取文件列表失败:', error)
  } finally {
    filesLoading.value = false
  }
}

const fetchVersions = async () => {
  versionsLoading.value = true
  try {
    versions.value = await skillsStore.fetchVersions(skillId.value)
  } catch (error) {
    console.error('获取版本历史失败:', error)
  } finally {
    versionsLoading.value = false
  }
}

onMounted(() => {
  skillId.value = route.params.id
  fetchSkillDetail()
  fetchFiles()
  fetchVersions()
})
</script>

<style scoped>
.skill-detail-container {
  padding: 20px 0;
}

.skill-detail-card {
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

.skill-info {
  margin-bottom: 30px;
}

.skill-actions {
  margin-bottom: 30px;
}

.files-section,
.versions-section {
  margin-top: 30px;
}

.files-section h3,
.versions-section h3 {
  margin-bottom: 15px;
  font-size: 16px;
  color: #303133;
}

.upload-demo {
  margin-bottom: 20px;
}
</style>
