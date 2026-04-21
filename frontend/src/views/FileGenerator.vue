<template>
  <div class="file-generator-container">
    <el-card class="file-generator-card">
      <template #header>
        <div class="card-header">
          <h2>文件生成</h2>
        </div>
      </template>
      
      <div class="generator-content">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="template-section">
              <h3>选择模板</h3>
              <el-select v-model="selectedTemplate" placeholder="请选择模板">
                <el-option 
                  v-for="template in templates" 
                  :key="template.id" 
                  :label="template.name" 
                  :value="template.id"
                />
              </el-select>
            </div>
            
            <div class="params-section">
              <h3>参数配置</h3>
              <el-form :model="form" label-width="100px">
                <el-form-item v-for="param in currentTemplate?.params" :key="param.name" :label="param.label">
                  <el-input 
                    v-if="param.type === 'text'" 
                    v-model="form[param.name]" 
                    :placeholder="param.placeholder"
                  />
                  <el-select 
                    v-else-if="param.type === 'select'" 
                    v-model="form[param.name]" 
                    :placeholder="param.placeholder"
                  >
                    <el-option 
                      v-for="option in param.options" 
                      :key="option.value" 
                      :label="option.label" 
                      :value="option.value"
                    />
                  </el-select>
                </el-form-item>
              </el-form>
            </div>
            
            <div class="actions-section">
              <el-button type="primary" @click="generateFile">
                生成文件
              </el-button>
              <el-button @click="resetForm">
                重置
              </el-button>
            </div>
          </el-col>
          
          <el-col :span="12">
            <div class="preview-section">
              <h3>预览</h3>
              <el-card class="preview-card">
                <pre v-if="previewContent">{{ previewContent }}</pre>
                <div v-else class="empty-preview">
                  生成文件后将在此处显示预览
                </div>
              </el-card>
              
              <div v-if="previewContent" class="download-section">
                <el-button type="success" @click="downloadFile">
                  下载文件
                </el-button>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { saveAs } from 'file-saver'

const selectedTemplate = ref('')
const form = ref({})
const previewContent = ref('')

const templates = ref([
  {
    id: 'customer_service',
    name: '客服Skill模板',
    params: [
      {
        name: 'skill_name',
        label: 'Skill名称',
        type: 'text',
        placeholder: '请输入Skill名称'
      },
      {
        name: 'welcome_message',
        label: '欢迎语',
        type: 'text',
        placeholder: '请输入欢迎语'
      },
      {
        name: 'fallback_message',
        label: ' fallback语',
        type: 'text',
        placeholder: '请输入fallback语'
      }
    ]
  },
  {
    id: 'sales',
    name: '销售Skill模板',
    params: [
      {
        name: 'skill_name',
        label: 'Skill名称',
        type: 'text',
        placeholder: '请输入Skill名称'
      },
      {
        name: 'product_category',
        label: '产品类别',
        type: 'select',
        placeholder: '请选择产品类别',
        options: [
          { label: '电子产品', value: 'electronics' },
          { label: '服装', value: 'clothing' },
          { label: '食品', value: 'food' },
          { label: '其他', value: 'other' }
        ]
      },
      {
        name: 'promotion_message',
        label: '促销信息',
        type: 'text',
        placeholder: '请输入促销信息'
      }
    ]
  },
  {
    id: 'operation',
    name: '运营Skill模板',
    params: [
      {
        name: 'skill_name',
        label: 'Skill名称',
        type: 'text',
        placeholder: '请输入Skill名称'
      },
      {
        name: 'operation_type',
        label: '运营类型',
        type: 'select',
        placeholder: '请选择运营类型',
        options: [
          { label: '活动运营', value: 'activity' },
          { label: '用户运营', value: 'user' },
          { label: '内容运营', value: 'content' },
          { label: '其他', value: 'other' }
        ]
      },
      {
        name: 'target_audience',
        label: '目标受众',
        type: 'text',
        placeholder: '请输入目标受众'
      }
    ]
  }
])

const currentTemplate = computed(() => {
  return templates.value.find(template => template.id === selectedTemplate.value)
})

const generateFile = () => {
  if (!selectedTemplate.value) {
    ElMessage.warning('请选择模板')
    return
  }
  
  // 检查必填参数
  const requiredParams = currentTemplate.value.params.filter(param => param.required)
  for (const param of requiredParams) {
    if (!form.value[param.name]) {
      ElMessage.warning(`请填写${param.label}`)
      return
    }
  }
  
  // 生成文件内容
  let content = ''
  
  switch (selectedTemplate.value) {
    case 'customer_service':
      content = `{
  "skill_name": "${form.value.skill_name}",
  "type": "customer_service",
  "welcome_message": "${form.value.welcome_message}",
  "fallback_message": "${form.value.fallback_message}",
  "intents": [
    {
      "name": "greeting",
      "patterns": ["你好", "嗨", "哈喽"],
      "responses": ["${form.value.welcome_message}"]
    },
    {
      "name": "thanks",
      "patterns": ["谢谢", "谢谢啦", "感谢"],
      "responses": ["不客气", "很高兴为您服务", "随时为您解答"]
    }
  ]
}`
      break
    case 'sales':
      content = `{
  "skill_name": "${form.value.skill_name}",
  "type": "sales",
  "product_category": "${form.value.product_category}",
  "promotion_message": "${form.value.promotion_message}",
  "intents": [
    {
      "name": "product_info",
      "patterns": ["产品信息", "介绍一下产品", "产品详情"],
      "responses": ["我们的${form.value.product_category}产品质量上乘，${form.value.promotion_message}"]
    },
    {
      "name": "price",
      "patterns": ["价格", "多少钱", "价位"],
      "responses": ["我们的产品价格合理，${form.value.promotion_message}"]
    }
  ]
}`
      break
    case 'operation':
      content = `{
  "skill_name": "${form.value.skill_name}",
  "type": "operation",
  "operation_type": "${form.value.operation_type}",
  "target_audience": "${form.value.target_audience}",
  "intents": [
    {
      "name": "activity_info",
      "patterns": ["活动信息", "有什么活动", "活动详情"],
      "responses": ["我们针对${form.value.target_audience}开展了${form.value.operation_type}活动，欢迎参与"]
    },
    {
      "name": "participate",
      "patterns": ["如何参与", "怎么参加", "参与方式"],
      "responses": ["您可以通过我们的官方渠道参与活动，详情请咨询客服"]
    }
  ]
}`
      break
  }
  
  previewContent.value = content
  ElMessage.success('文件生成成功')
}

const resetForm = () => {
  selectedTemplate.value = ''
  form.value = {}
  previewContent.value = ''
}

const downloadFile = () => {
  if (!previewContent.value) return
  
  const blob = new Blob([previewContent.value], { type: 'application/json' })
  saveAs(blob, `${form.value.skill_name || 'skill'}.json`)
  ElMessage.success('文件下载成功')
}
</script>

<style scoped>
.file-generator-container {
  padding: 20px 0;
}

.file-generator-card {
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

.generator-content {
  margin-top: 20px;
}

.template-section,
.params-section,
.actions-section,
.preview-section {
  margin-bottom: 20px;
}

.template-section h3,
.params-section h3,
.preview-section h3 {
  margin-bottom: 15px;
  font-size: 16px;
  color: #303133;
}

.preview-card {
  height: 400px;
  overflow: auto;
}

.empty-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #909399;
}

.download-section {
  margin-top: 20px;
}
</style>
