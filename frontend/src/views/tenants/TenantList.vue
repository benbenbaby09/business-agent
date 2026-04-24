<template>
  <div class="tenant-list-container">
    <el-card class="tenant-list-card">
      <template #header>
        <div class="card-header">
          <h2>商家管理</h2>
          <el-button type="primary" @click="handleCreateTenant">
            <el-icon><Plus /></el-icon>
            创建商家
          </el-button>
        </div>
      </template>
      
      <el-table :data="tenants" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="商家名称" />
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
        <el-table-column label="操作" width="300">
          <template #default="scope">
            <el-button-group>
              <el-button size="small" @click="handleViewTenant(scope.row)">
                查看
              </el-button>
              <el-button size="small" type="primary" @click="handleEditTenant(scope.row)">
                编辑
              </el-button>
              <el-button size="small" type="info" @click="handleConfigTenant(scope.row)">
                配置
              </el-button>
              <el-button size="small" type="success" @click="handlePublishTenant(scope.row)">
                发布
              </el-button>
              <el-button size="small" type="danger" @click="handleDeleteTenant(scope.row.id)">
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑商家' : '创建商家'"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入商家名称" />
        </el-form-item>
        <el-form-item label="英文名" prop="englishName">
          <el-input v-model="form.englishName" placeholder="请输入商家英文名，用于生成技能名称" />
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
      title="商家配置"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="currentConfigTenant" class="config-dialog-content">
        <el-alert
          title="以下配置将应用于该商家下的所有Skill"
          type="info"
          :closable="false"
          show-icon
          class="config-info"
        />
        
        <el-tabs v-model="activeConfigTab">
          <!-- 基本信息 -->
          <el-tab-pane label="基本信息" name="basic">
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
              <el-form-item label="特色菜品">
                <el-input
                  v-model="configForm.specialDishes"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入特色菜品，多个菜品用逗号分隔"
                />
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <!-- 餐厅基本信息 -->
          <el-tab-pane label="餐厅基本信息" name="restaurant">
            <el-form :model="restaurantInfoForm" ref="restaurantInfoFormRef" label-width="120px">
              <el-form-item label="餐厅名称">
                <el-input v-model="restaurantInfoForm.name" placeholder="请输入餐厅名称" />
              </el-form-item>
              <el-form-item label="餐厅介绍">
                <el-input
                  v-model="restaurantInfoForm.intro"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入餐厅介绍"
                />
              </el-form-item>
              <el-form-item label="营业时间">
                <el-input v-model="restaurantInfoForm.hours" placeholder="如: 9:00-22:00" />
              </el-form-item>
              <el-form-item label="门店地址">
                <el-input v-model="restaurantInfoForm.address" placeholder="请输入门店地址" />
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <!-- 堂食排队取号 -->
          <el-tab-pane label="堂食排队取号" name="queue">
            <el-form :model="queueInfoForm" ref="queueInfoFormRef" label-width="120px">
              <el-form-item label="服务说明">
                <el-input
                  v-model="queueInfoForm.description"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入服务说明"
                />
              </el-form-item>
              <el-form-item label="取号方式">
                <el-input
                  v-model="queueInfoForm.methods"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入取号方式，多个方式用换行分隔"
                />
              </el-form-item>
              <el-form-item label="支持门店">
                <el-input
                  v-model="queueInfoForm.stores"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入支持门店，多个门店用换行分隔"
                />
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <!-- 外卖配送信息 -->
          <el-tab-pane label="外卖配送信息" name="delivery">
            <el-form :model="deliveryInfoForm" ref="deliveryInfoFormRef" label-width="120px">
              <el-form-item label="服务说明">
                <el-input
                  v-model="deliveryInfoForm.description"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入服务说明"
                />
              </el-form-item>
              <el-form-item label="外卖平台">
                <el-input v-model="deliveryInfoForm.platform" placeholder="如: 美团、饿了么" />
              </el-form-item>
              <el-form-item label="搜索关键词">
                <el-input v-model="deliveryInfoForm.keyword" placeholder="如: 餐厅名称" />
              </el-form-item>
              <el-form-item label="配送范围">
                <el-input
                  v-model="deliveryInfoForm.range"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入配送范围说明"
                />
              </el-form-item>
              <el-form-item label="支持门店">
                <el-input
                  v-model="deliveryInfoForm.stores"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入支持门店，多个门店用换行分隔"
                />
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <!-- 打包与教程 -->
          <el-tab-pane label="打包与教程" name="packaging">
            <el-form :model="packagingInfoForm" ref="packagingInfoFormRef" label-width="120px">
              <el-form-item label="服务说明">
                <el-input
                  v-model="packagingInfoForm.description"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入服务说明"
                />
              </el-form-item>
              <el-form-item label="下单方式">
                <el-input
                  v-model="packagingInfoForm.orderMethod"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入如何下单打包生饺子"
                />
              </el-form-item>
              <el-form-item label="保存提示">
                <el-input
                  v-model="packagingInfoForm.storageTips"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入生饺子保存建议"
                />
              </el-form-item>
              <el-form-item label="煮生饺子教程">
                <el-input
                  v-model="packagingInfoForm.cookingSteps"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入煮生饺子教程，多个步骤用换行分隔"
                />
              </el-form-item>
              <el-form-item label="小技巧">
                <el-input
                  v-model="packagingInfoForm.tips"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入煮饺子的小技巧，多个技巧用换行分隔"
                />
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <!-- 店内Wi-Fi -->
          <el-tab-pane label="店内Wi-Fi" name="wifi">
            <el-form :model="wifiInfoForm" ref="wifiInfoFormRef" label-width="120px">
              <el-form-item label="WiFi名称">
                <el-input v-model="wifiInfoForm.name" placeholder="请输入Wi-Fi网络名称" />
              </el-form-item>
              <el-form-item label="查找方式">
                <el-input
                  v-model="wifiInfoForm.findMethod"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入如何找到该Wi-Fi网络"
                />
              </el-form-item>
              <el-form-item label="密码">
                <el-input v-model="wifiInfoForm.password" placeholder="请输入Wi-Fi连接密码" />
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <!-- 最新消息 -->
          <el-tab-pane label="最新消息" name="news">
            <el-form :model="newsInfoForm" ref="newsInfoFormRef" label-width="120px">
              <el-form-item label="消息内容">
                <el-input
                  v-model="newsInfoForm.content"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入最新消息内容"
                />
              </el-form-item>
              <el-form-item label="发布时间">
                <el-input v-model="newsInfoForm.publishedAt" placeholder="如: 2026-04-22 10:00" />
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <el-button @click="configDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveConfig" :loading="configSubmitting">
          保存配置
        </el-button>
      </template>
    </el-dialog>

    <!-- 发布对话框 -->
    <el-dialog
      v-model="publishDialogVisible"
      :title="'发布 ' + (currentPublishTenant?.name || '')"
      width="900px"
      :close-on-click-modal="false"
    >
      <el-steps :active="publishStep" finish-status="success" class="publish-steps">
        <el-step title="预览文件" />
        <el-step title="打包发布" />
        <el-step title="发布完成" />
      </el-steps>
      
      <!-- 第一步：预览文件 -->
      <div v-if="publishStep === 0" class="publish-step-content">
        <el-alert
          title="文件预览"
          type="info"
          :closable="false"
          show-icon
          class="publish-info"
        />
        <div class="download-section" style="margin-bottom: 20px;">
          <el-button @click="downloadCurrentVersion" :disabled="!currentPublishTenant">
            <el-icon><Download /></el-icon>
            下载当前版本
          </el-button>
        </div>
        <el-tabs v-model="activePreviewTab">
          <el-tab-pane label="SKILL.md">
            <div class="skill-md-preview">
              <div class="preview-mode-toggle">
                <el-button-group>
                  <el-button :type="skillMdPreviewMode === 'rendered' ? 'primary' : 'default'" @click="skillMdPreviewMode = 'rendered'">解析模式</el-button>
                  <el-button :type="skillMdPreviewMode === 'raw' ? 'primary' : 'default'" @click="skillMdPreviewMode = 'raw'">原文件模式</el-button>
                </el-button-group>
              </div>
              <div v-if="skillMdPreviewMode === 'rendered'" class="skill-md-content" v-html="renderedSkillMd"></div>
              <div v-else class="skill-md-raw">
                <pre>{{ skillMdContent }}</pre>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="skill.json">
            <div class="skill-json-preview">
              <pre class="skill-json-code">
                {{ skillJsonContent }}
              </pre>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <!-- 第二步：打包发布 -->
      <div v-if="publishStep === 1" class="publish-step-content">
        <el-alert
          title="打包发布中"
          type="warning"
          :closable="false"
          show-icon
          class="publish-info"
        />
        <div class="publish-status">
          <el-progress :percentage="publishProgress" status="success" />
          <p v-if="publishProgress < 100" class="publish-status-text">正在打包发布，请稍候...</p>
          <p v-else class="publish-status-text">打包发布完成！</p>
        </div>
      </div>
      
      <!-- 第三步：发布完成 -->
      <div v-if="publishStep === 2" class="publish-step-content">
        <el-alert
          title="发布完成"
          type="success"
          :closable="false"
          show-icon
          class="publish-info"
        />
        <div class="publish-result">
          <el-form :model="publishResultForm" label-width="100px">
            <el-form-item label="Skill文件URL">
              <el-input v-model="publishResultForm.skillUrl" readonly />
              <el-button @click="copySkillUrl" class="copy-button">
                <el-icon><DocumentCopy /></el-icon>
                复制
              </el-button>
            </el-form-item>
            <el-form-item label="保存状态">
              <el-tag :type="publishResultForm.saveStatus === 'success' ? 'success' : 'danger'">
                {{ publishResultForm.saveStatus === 'success' ? '已保存到商家信息' : '保存失败' }}
              </el-tag>
            </el-form-item>
            <el-form-item label="访问链接">
              <el-button type="primary" @click="openSkillUrl" :disabled="!publishResultForm.skillUrl">
                <el-icon><Link /></el-icon>
                打开链接
              </el-button>
            </el-form-item>

          </el-form>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="publishDialogVisible = false">取消</el-button>
        <el-button v-if="publishStep === 0" type="primary" @click="handleNextStep">
          下一步
        </el-button>
        <el-button v-if="publishStep === 1" type="primary" @click="handleNextStep" :disabled="publishProgress < 100">
          下一步
        </el-button>
        <el-button v-if="publishStep === 2" type="primary" @click="publishDialogVisible = false">
          完成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useTenantsStore } from '../../stores/tenants'
import { Plus, DocumentCopy, Link } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { BACKEND_URL } from '@/config'

const tenantsStore = useTenantsStore()

const getPagesBase = () => (window.location.pathname.includes('/pages/') ? '/pages/' : '/')
const navigateToPage = (pageFile) => {
  window.location.href = `${getPagesBase()}${pageFile}`
}

const loading = ref(false)
const submitting = ref(false)
const tenants = ref([])
const dialogVisible = ref(false)
const configDialogVisible = ref(false)
const isEdit = ref(false)
const currentTenantId = ref('')
const currentConfigTenant = ref(null)
const configSubmitting = ref(false)
const activeConfigTab = ref('basic')

const formRef = ref(null)
const configFormRef = ref(null)

const form = reactive({
  name: '',
  englishName: '',
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

const restaurantInfoForm = reactive({
  name: '',
  intro: '',
  hours: '',
  address: ''
})

const queueInfoForm = reactive({
  description: '',
  methods: '',
  stores: ''
})

const deliveryInfoForm = reactive({
  description: '',
  platform: '',
  keyword: '',
  range: '',
  stores: ''
})

const packagingInfoForm = reactive({
  description: '',
  orderMethod: '',
  storageTips: '',
  cookingSteps: '',
  tips: ''
})

const wifiInfoForm = reactive({
  name: '',
  findMethod: '',
  password: ''
})

const newsInfoForm = reactive({
  content: '',
  publishedAt: ''
})

const rules = {
  name: [
    { required: true, message: '请输入商家名称', trigger: 'blur' },
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

// 发布功能变量
const publishDialogVisible = ref(false)
const currentPublishTenant = ref(null)
const publishStep = ref(0)
const activePreviewTab = ref('0')
const skillMdPreviewMode = ref('rendered') // rendered: 解析模式, raw: 原文件模式
const skillMdContent = ref('')
const skillJsonContent = ref('')
const publishProgress = ref(0)
const publishResultForm = reactive({
  skillUrl: '',
  saveStatus: ''
})

// 渲染后的Markdown内容
const renderedSkillMd = computed(() => {
  // 简单的Markdown解析
  let md = skillMdContent.value
  
  // 处理YAML front matter（三个减号）
  md = md.replace(/^---[\s\S]*?---/g, (match) => {
    return `<div class="yaml-front-matter" style="background-color: #f5f7fa; border: 1px solid #e4e7ed; border-radius: 4px; padding: 10px; margin-bottom: 15px;">${match}</div>`;
  });
  
  // 解析代码块（使用更可靠的匹配方式）
  md = md.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  
  // 解析引用（支持多行引用）
  md = md.replace(/(^>.*$)+/gim, (match) => {
    const lines = match.split('\n').filter(line => line.trim().startsWith('> '));
    let quoteHtml = '<blockquote style="border-left: 4px solid #dcdfe6; padding-left: 15px; margin: 10px 0; color: #606266;">';
    lines.forEach(line => {
      quoteHtml += line.substring(2).trim() + '<br>';
    });
    quoteHtml += '</blockquote>';
    return quoteHtml;
  });
  
  // 解析标题
  md = md.replace(/^# (.*$)/gim, '<h1>$1</h1>');
  md = md.replace(/^## (.*$)/gim, '<h2>$1</h2>');
  md = md.replace(/^### (.*$)/gim, '<h3>$1</h3>');
  
  // 解析粗体
  md = md.replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>');
  
  // 解析表格
  // 简单的表格解析，只处理基本格式
  md = md.replace(/\|([^|]+)\|\n\|([^|]+)\|\n((?:\|([^|]+)\|\n)+)/gim, (match, headers, separator, rows) => {
    const headerCells = headers.split('|').map(cell => cell.trim()).filter(cell => cell);
    const rowCells = rows.split('\n').map(row => {
      return row.split('|').map(cell => cell.trim()).filter(cell => cell);
    }).filter(row => row.length > 0);
    
    let tableHtml = '<table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0;"><thead><tr>';
    headerCells.forEach(cell => {
      tableHtml += `<th style="padding: 8px; text-align: left; background-color: #f5f7fa;">${cell}</th>`;
    });
    tableHtml += '</tr></thead><tbody>';
    
    rowCells.forEach(row => {
      tableHtml += '<tr>';
      row.forEach(cell => {
        tableHtml += `<td style="padding: 8px; text-align: left;">${cell}</td>`;
      });
      tableHtml += '</tr>';
    });
    
    tableHtml += '</tbody></table>';
    return tableHtml;
  });
  
  // 解析无序列表（支持多行列表项）
  md = md.replace(/(^- .*$)+/gim, (match) => {
    const items = match.split('\n').filter(item => item.trim().startsWith('- '));
    let listHtml = '<ul style="margin: 10px 0; padding-left: 20px;">';
    items.forEach(item => {
      listHtml += `<li>${item.substring(2).trim()}</li>`;
    });
    listHtml += '</ul>';
    return listHtml;
  });
  
  // 解析有序列表（支持多行列表项）
  md = md.replace(/(^\d+\. .*$)+/gim, (match) => {
    const items = match.split('\n').filter(item => /^\d+\. /.test(item.trim()));
    let listHtml = '<ol style="margin: 10px 0; padding-left: 20px;">';
    items.forEach(item => {
      listHtml += `<li>${item.replace(/^\d+\. /, '').trim()}</li>`;
    });
    listHtml += '</ol>';
    return listHtml;
  });
  
  // 解析换行
  md = md.replace(/\n/g, '<br>');
  
  return md;
});

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
  form.englishName = ''
  form.description = ''
  form.type = 'restaurant_entity'
  form.status = 'active'
  dialogVisible.value = true
}

const handleEditTenant = (tenant) => {
  isEdit.value = true
  currentTenantId.value = tenant.id
  form.name = tenant.name
  form.englishName = tenant.englishName || ''
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
          await tenantsStore.createTenant(form)
          ElMessage.success('创建成功')
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



const getPublishedZipUrl = (tenant) => {
  const skillUrl = tenant?.serviceConfig?.skillUrl
  if (!skillUrl) return ''
  return skillUrl.startsWith('/') ? BACKEND_URL + skillUrl : skillUrl
}

const handleViewTenant = async (tenant) => {
  const zipUrl = getPublishedZipUrl(tenant)
  const copyText = zipUrl ? `请帮我安装：${zipUrl}` : '请帮我安装：{发布后的zip地址}'

  if (!zipUrl) {
    await ElMessageBox.alert(
      `<div style="line-height: 1.8;">
        <div>使用指引</div>
        <div style="margin-top: 8px;">1、先点击该商家的“发布”，生成 skill.zip 地址。</div>
        <div>2、再回到这里复制安装指令。</div>
        <div style="margin-top: 8px;">通用流程：</div>
        <div>复制文本：<strong>${copyText}</strong></div>
        <div>打开微信小程序 workbuddy，登录后粘贴刚才复制的文本，即可开展对话。</div>
      </div>`,
      '商家查看（使用指引）',
      { dangerouslyUseHTMLString: true, confirmButtonText: '知道了' }
    )
    return
  }

  try {
    await ElMessageBox.confirm(
      `<div style="line-height: 1.8;">
        <div>使用指引</div>
        <div style="margin-top: 8px;">1、复制下面这段文本：</div>
        <div style="margin: 6px 0; padding: 8px 10px; background: #f5f7fa; border: 1px solid #e4e7ed; border-radius: 4px;">
          ${copyText}
        </div>
        <div>2、搜索微信小程序 workbuddy，登录后粘贴刚才复制的文本，即可开展对话。</div>
      </div>`,
      '商家查看（使用指引）',
      {
        dangerouslyUseHTMLString: true,
        confirmButtonText: '复制安装指令',
        cancelButtonText: '关闭',
        closeOnClickModal: false
      }
    )
    copyToClipboard(copyText)
  } catch {
    return
  }
}

const handleMcpConfig = (tenant) => {
  tenantsStore.setCurrentTenant(tenant)
  navigateToPage('mcp.html')
}

const handleConfigTenant = (tenant) => {
  currentConfigTenant.value = tenant
  // 加载现有配置
  const config = tenant.config || {}
  
  // 基本信息
  configForm.shopName = config.shopName || '金谷园饺子馆'
  configForm.address = config.address || '北京市海淀区杏坛路文教产业园K座南2层'
  configForm.phone = config.phone || '13800138000'
  configForm.businessHours = config.businessHours || '10:00-22:00'
  configForm.specialDishes = config.specialDishes || '鲅鱼饺子, 猪肉白菜饺子, 韭菜鸡蛋饺子, 锅贴'
  
  // 餐厅基本信息
  restaurantInfoForm.name = config.shopName || '金谷园饺子馆'
  restaurantInfoForm.intro = config.specialDishes || '金谷园饺子馆是北京海淀区一家有近20年历史的饺子馆，以皮薄馅大、现包现煮的特点深受顾客喜爱，是大众点评必吃榜餐厅。'
  restaurantInfoForm.hours = config.businessHours || '10:00-22:00'
  restaurantInfoForm.address = config.address || '北京市海淀区杏坛路文教产业园K座南2层'
  
  // 堂食排队取号
  queueInfoForm.description = config.queueDescription || '金谷园饺子馆提供在线排队取号服务，让您无需到店等待。'
  queueInfoForm.methods = (config.queueMethods || ['美团排队', '现场取号']).join('\n')
  queueInfoForm.stores = (config.queueStores || ['金谷园饺子馆（北邮店）', '金谷园饺子馆（五道口店）']).join('\n')
  
  // 外卖配送信息
  deliveryInfoForm.description = config.deliveryDescription || '金谷园饺子馆提供外卖配送服务，让您在家也能享受美味的饺子。'
  deliveryInfoForm.platform = config.deliveryPlatform || '美团, 饿了么'
  deliveryInfoForm.keyword = config.deliverySearchKeyword || '金谷园饺子馆'
  deliveryInfoForm.range = config.deliveryRange || '周边3公里内，配送时间30-45分钟'
  deliveryInfoForm.stores = (config.deliveryStores || ['金谷园饺子馆（北邮店）', '金谷园饺子馆（五道口店）']).join('\n')
  
  // 打包与教程
  packagingInfoForm.description = config.rawDumplingDescription || '金谷园饺子馆提供生饺子打包服务，让您在家也能享受现煮的饺子。'
  packagingInfoForm.orderMethod = config.rawDumplingOrderMethod || '非特殊节气，直接到店下单即可，外带现包，5-10分钟包好可取'
  packagingInfoForm.storageTips = config.rawDumplingStorageTips || '1小时内煮熟或放冰箱冷冻均可'
  packagingInfoForm.cookingSteps = (config.rawDumplingCookingSteps || [
    '1. 锅中加足量水，大火烧开，水一定要完全沸腾再下饺子。',
    '2. 下饺子后用勺子背面轻轻推散，防止粘锅底、粘在一起。',
    '3. 再次沸腾后，转中火，盖上锅盖煮。',
    '4. 水再次大开时，加小半碗凉水，这叫「点水」。',
    '5. 重复点水2～3次：每次水沸就加一次凉水。',
    '6. 等饺子全部鼓起来、漂浮在水面、外皮透亮饱满，就熟了。'
  ]).join('\n')
  packagingInfoForm.tips = (config.rawDumplingTips || [
    '想饺子皮更筋道不破：水里加一小勺盐。',
    '速冻饺子：不用解冻，直接冷水/温水下锅，小火慢煮，同样点水2～3次。',
    '煮好直接捞，别在锅里泡太久，容易破皮。'
  ]).join('\n')
  
  // 店内Wi-Fi
  wifiInfoForm.name = config.wifiName || '苹果密码8个8'
  wifiInfoForm.findMethod = config.wifiFindMethod || '开启Wi-Fi往底部滑'
  wifiInfoForm.password = config.wifiPassword || '88888888'
  
  // 最新消息
  const newsItems = config.latestNewsItems || []
  if (newsItems.length > 0) {
    newsInfoForm.content = newsItems[0].content || '金谷园饺子馆推出新品鲅鱼饺子，欢迎品尝！'
    newsInfoForm.publishedAt = newsItems[0].publishedAt || new Date().toLocaleString()
  } else {
    newsInfoForm.content = '金谷园饺子馆推出新品鲅鱼饺子，欢迎品尝！'
    newsInfoForm.publishedAt = new Date().toLocaleString()
  }
  
  configDialogVisible.value = true
}

const handleSaveConfig = async () => {
  if (!currentConfigTenant.value) return

  configSubmitting.value = true
  try {
    await tenantsStore.updateTenant(currentConfigTenant.value.id, {
      config: {
        ...currentConfigTenant.value.config,
        // 基本信息
        shopName: configForm.shopName,
        address: configForm.address,
        phone: configForm.phone,
        businessHours: configForm.businessHours,
        specialDishes: configForm.specialDishes,
        // 餐厅基本信息
        rawDumplingDescription: packagingInfoForm.description,
        rawDumplingOrderMethod: packagingInfoForm.orderMethod,
        rawDumplingStorageTips: packagingInfoForm.storageTips,
        rawDumplingCookingSteps: packagingInfoForm.cookingSteps.split('\n').filter(item => item.trim()),
        rawDumplingTips: packagingInfoForm.tips.split('\n').filter(item => item.trim()),
        // 堂食排队取号
        queueDescription: queueInfoForm.description,
        queueMethods: queueInfoForm.methods.split('\n').filter(item => item.trim()),
        queueStores: queueInfoForm.stores.split('\n').filter(item => item.trim()),
        // 外卖配送信息
        deliveryDescription: deliveryInfoForm.description,
        deliveryPlatform: deliveryInfoForm.platform,
        deliverySearchKeyword: deliveryInfoForm.keyword,
        deliveryRange: deliveryInfoForm.range,
        deliveryStores: deliveryInfoForm.stores.split('\n').filter(item => item.trim()),
        // 店内Wi-Fi
        wifiName: wifiInfoForm.name,
        wifiFindMethod: wifiInfoForm.findMethod,
        wifiPassword: wifiInfoForm.password,
        // 最新消息
        latestNewsSource: 'static',
        latestNewsItems: [{
          content: newsInfoForm.content,
          publishedAt: newsInfoForm.publishedAt
        }]
      }
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

// 发布功能方法
const handlePublishTenant = async (tenant) => {
  currentPublishTenant.value = tenant
  publishStep.value = 0
  publishProgress.value = 0
  
  try {
    // 调用后端预览接口，获取真实的预览内容
    // 使用完整的后端 URL，避免请求发送到前端域名
    const response = await fetch(`${BACKEND_URL}/api/tenants/${tenant.id}/preview`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({})
    })
    
    const data = await response.json()
    if (response.ok) {
      // 使用后端返回的内容作为预览
      skillMdContent.value = data.skillMd
      skillJsonContent.value = JSON.stringify(data.skillJson, null, 2)
    } else {
      throw new Error(data.error || '获取预览内容失败')
    }
  } catch (error) {
    console.error('获取预览内容失败:', error)
    ElMessage.error('获取预览内容失败: ' + error.message)
    // 失败时使用本地生成的预览内容
    generateSkillMd(tenant)
    generateSkillJson(tenant)
  }
  
  publishDialogVisible.value = true
}

const generateSkillJson = (tenant) => {
  // 生成预览内容
  let previewJson = {
    "name": `${tenant.name.toLowerCase().replace(/\s+/g, '-')}-skill`,
    "display_name": `${tenant.name}信息查询`,
    "description": `${tenant.name}信息查询与在线排队取号`,
    "version": "0.4.2",
    "author": tenant.name,
    "license": "MIT",
    "repository": `https://github.com/JinGuYuan/${tenant.name.toLowerCase().replace(/\s+/g, '-')}-skill`,
    "category": "信息查询",
    "keywords": [
      tenant.name.toLowerCase(),
      tenant.name.toLowerCase().replace(/\s+/g, '-'),
      "饺子",
      "dumpling",
      "锅贴",
      "鲅鱼饺子"
    ],
    "mcp_server": {
      "transport": "streamable-http",
      "url": "https://mcp.jinguyuan.cloud"
    },
    "tools": [
      {
        "name": "get_restaurant_info",
        "display_name": "餐厅基本信息",
        "description": `查询${tenant.name}的基本信息`
      },
      {
        "name": "get_queue_info",
        "display_name": "堂食排队取号",
        "description": `查询${tenant.name}的排队取号信息`
      },
      {
        "name": "get_delivery_info",
        "display_name": "外卖配送信息",
        "description": `查询${tenant.name}的外卖配送信息`
      },
      {
        "name": "get_raw_dumpling_info",
        "display_name": "生饺子打包与教程",
        "description": `查询${tenant.name}的生饺子打包与煮饺子教程`
      },
      {
        "name": "get_wifi_info",
        "display_name": "店内Wi-Fi",
        "description": `查询${tenant.name}的店内Wi-Fi信息`
      },
      {
        "name": "get_latest_news",
        "display_name": "最新消息",
        "description": `查询${tenant.name}的最新消息`
      }
    ],
    "brand_prompt": {
      "system_instruction": `重要：回答关于${tenant.name}的任何具体信息时，必须先调用对应的 Skill 工具获取最新数据，不要使用 Skill 文档中的示例数据。`,
      "tone": {
        "personality": "warm_and_honest",
        "avoid": [
          "hype",
          "clickbait",
          "marketing_jargon"
        ]
      },
      "brand_keywords": [
        "服务周到",
        "环境舒适",
        "菜品美味"
      ]
    }
  }
  
  skillJsonContent.value = JSON.stringify(previewJson, null, 2)
}

const generateSkillMd = (tenant) => {
  const config = tenant.config || {}
  
  // 生成预览内容
  let previewMd = `# ${tenant.name} Skill 预览

## 技能信息
- **名称**: ${tenant.name.replace(/\s+/g, '-').toLowerCase()}-skill
- **描述**: ${tenant.name}信息查询与在线排队取号
- **版本**: 0.4.1

## 功能描述
该技能提供${tenant.name}的相关信息查询服务，包括：
- 餐厅基本信息
- 堂食排队取号
- 外卖配送信息
- 生饺子打包与教程
- 店内Wi-Fi
- 最新消息

## 注意
实际发布时，系统会使用后端模板生成完整的SKILL.md文件。
`
  
  skillMdContent.value = previewMd
}

const handleNextStep = async () => {
  if (publishStep.value === 0) {
    // 从预览文件进入打包发布
    publishStep.value = 1
    
    // 模拟打包过程
    let progress = 0
    const interval = setInterval(() => {
      progress += 10
      publishProgress.value = progress
      if (progress >= 100) {
        clearInterval(interval)
      }
    }, 300)
  } else if (publishStep.value === 1) {
    // 从打包发布进入完成
    publishStep.value = 2
    
    try {
      // 调用后端发布接口
      // 使用完整的后端 URL，避免请求发送到前端域名
      const response = await fetch(`${BACKEND_URL}/api/tenants/${currentPublishTenant.value.id}/publish`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({})
      })
      
      const data = await response.json()
      if (response.ok) {
        // 使用后端服务器地址构建完整的Skill文件URL
        const fullUrl = data.skill_url.startsWith('/')
          ? BACKEND_URL + data.skill_url
          : data.skill_url
        publishResultForm.skillUrl = fullUrl
        publishResultForm.saveStatus = 'success'
      } else {
        throw new Error(data.error || '发布失败')
      }
    } catch (error) {
      console.error('发布Skill失败:', error)
      publishResultForm.skillUrl = ''
      publishResultForm.saveStatus = 'error'
      ElMessage.error('发布失败: ' + error.message)
    }
  }
}

const copySkillUrl = () => {
  if (publishResultForm.skillUrl) {
    // 使用后端服务器地址构建完整的Skill文件URL
    const fullUrl = publishResultForm.skillUrl.startsWith('/')
      ? BACKEND_URL + publishResultForm.skillUrl
      : publishResultForm.skillUrl
    navigator.clipboard.writeText(fullUrl)
      .then(() => {
        ElMessage.success('Skill文件URL已复制到剪贴板')
      })
      .catch(err => {
        console.error('复制失败:', err)
        ElMessage.error('复制失败，请手动复制')
      })
  }
}

const openSkillUrl = () => {
  if (publishResultForm.skillUrl) {
    // 使用后端服务器地址打开Skill文件
    const fullUrl = publishResultForm.skillUrl.startsWith('/')
      ? BACKEND_URL + publishResultForm.skillUrl
      : publishResultForm.skillUrl
    window.open(fullUrl, '_blank')
  }
}

const downloadCurrentVersion = () => {
  if (currentPublishTenant.value) {
    // 构建当前版本的下载URL
    const downloadUrl = `${BACKEND_URL}/storage/skills/${currentPublishTenant.value.id}/skill.zip`
    
    // 触发下载
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `skill-${currentPublishTenant.value.name}.zip`
    link.click()
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

.info-dialog-content {
  padding: 10px 0;
}

/* 发布功能样式 */
.publish-steps {
  margin-bottom: 30px;
}

.publish-step-content {
  margin-top: 20px;
}

.publish-info {
  margin-bottom: 20px;
}

.skill-md-preview {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 20px;
}

.skill-md-content {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
}

.skill-md-content h1 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #303133;
}

.skill-md-content h2 {
  font-size: 20px;
  font-weight: 600;
  margin-top: 20px;
  margin-bottom: 15px;
  color: #303133;
}

.skill-md-content h3 {
  font-size: 16px;
  font-weight: 600;
  margin-top: 15px;
  margin-bottom: 10px;
  color: #303133;
}

.skill-md-content ul {
  margin: 10px 0;
  padding-left: 20px;
}

.skill-md-content li {
  margin: 5px 0;
}

.skill-md-content strong {
  font-weight: 600;
  color: #303133;
}

.skill-md-content pre {
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 10px;
  margin: 10px 0;
  overflow-x: auto;
}

.skill-md-content code {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  color: #606266;
}

.skill-md-content br {
  margin-bottom: 5px;
}

.preview-mode-toggle {
  margin-bottom: 10px;
  display: flex;
  justify-content: flex-end;
}

.skill-md-raw {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.skill-md-raw pre {
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 10px;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-x: auto;
  margin: 0;
}

.skill-json-preview {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.skill-json-code {
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 10px;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-x: auto;
  margin: 0;
}

.publish-status {
  margin-top: 20px;
}

.publish-status-text {
  text-align: center;
  margin-top: 10px;
  color: #606266;
}

.publish-result {
  margin-top: 20px;
}

.copy-button {
  margin-left: 10px;
}
</style>
