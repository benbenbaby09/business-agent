<template>
  <div class="mcp-management-container">
    <el-card class="mcp-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h2>MCP服务管理</h2>
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
            <div class="section-header">
              <h3>MCP服务信息</h3>
              <el-button type="primary" @click="handleConfigService">
                <el-icon><Setting /></el-icon>
                服务配置
              </el-button>
            </div>
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
              <el-button type="primary" @click="handleAutoGenerateTools">
                <el-icon><Refresh /></el-icon>
                自动生成接口
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
              <el-table-column label="操作" width="100">
                <template #default="scope">
                  <el-button size="small" @click="handleViewTool(scope.row)">
                    查看
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

    <!-- 查看接口对话框 -->
    <el-dialog
      v-model="toolDialogVisible"
      :title="'查看接口: ' + toolForm.title"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form :model="toolForm" ref="toolFormRef" label-width="100px">
        <el-form-item label="类型">
          <el-select v-model="toolForm.type" disabled>
            <el-option label="餐厅基本信息" value="restaurant_entity" />
            <el-option label="堂食排队取号" value="queue_info" />
            <el-option label="外卖配送信息" value="delivery_info" />
            <el-option label="生饺子打包与教程" value="raw_dumpling_info" />
            <el-option label="店内Wi-Fi" value="wifi_info" />
            <el-option label="最新消息" value="latest_news" />
          </el-select>
        </el-form-item>
        <el-form-item label="接口名称">
          <el-input v-model="toolForm.name" disabled />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="toolForm.title" disabled />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="toolForm.description"
            type="textarea"
            :rows="3"
            disabled
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
                  <el-input v-model="toolForm.config.queueStores[index]" placeholder="如: 餐厅名称（分店名称）" />
                </el-form-item>
              </el-card>
            </div>
          </div>
        </div>

        <div v-if="toolForm.type === 'delivery_info'" class="config-section">
          <h4>外卖配送信息配置</h4>
          <el-form-item label="服务说明">
            <el-input
              v-model="toolForm.config.deliveryDescription"
              type="textarea"
              :rows="3"
              placeholder="请输入服务说明"
            />
          </el-form-item>
          <el-form-item label="外卖平台">
            <el-input v-model="toolForm.config.deliveryPlatform" placeholder="如: 美团、饿了么" />
          </el-form-item>
          <el-form-item label="搜索关键词">
            <el-input v-model="toolForm.config.deliverySearchKeyword" placeholder="如: 餐厅名称" />
          </el-form-item>
          <el-form-item label="配送范围">
            <el-input
              v-model="toolForm.config.deliveryRange"
              type="textarea"
              :rows="2"
              placeholder="请输入配送范围说明"
            />
          </el-form-item>

          <div class="queue-stores-section">
            <div class="section-header">
              <span>支持门店</span>
              <el-button type="primary" size="small" @click="addDeliveryStore">
                <el-icon><Plus /></el-icon>
                添加
              </el-button>
            </div>
            <div
              v-for="(store, index) in toolForm.config.deliveryStores"
              :key="index"
              class="queue-store-item"
            >
              <el-card shadow="never">
                <template #header>
                  <div class="queue-store-header">
                    <span>门店 {{ index + 1 }}</span>
                    <el-button type="danger" size="small" @click="removeDeliveryStore(index)">
                      删除
                    </el-button>
                  </div>
                </template>
                <el-form-item>
                  <el-input v-model="toolForm.config.deliveryStores[index]" placeholder="如: 餐厅名称（分店名称）" />
                </el-form-item>
              </el-card>
            </div>
          </div>
        </div>

        <div v-if="toolForm.type === 'raw_dumpling_info'" class="config-section">
          <h4>生饺子打包与教程配置</h4>
          <el-form-item label="服务说明">
            <el-input
              v-model="toolForm.config.rawDumplingDescription"
              type="textarea"
              :rows="2"
              placeholder="请输入服务说明"
            />
          </el-form-item>
          <el-form-item label="下单方式">
            <el-input
              v-model="toolForm.config.rawDumplingOrderMethod"
              type="textarea"
              :rows="1"
              placeholder="请输入如何下单打包生饺子"
            />
          </el-form-item>
          <el-form-item label="保存提示">
            <el-input
              v-model="toolForm.config.rawDumplingStorageTips"
              type="textarea"
              :rows="1"
              placeholder="请输入生饺子保存建议"
            />
          </el-form-item>

          <div class="queue-methods-section compact-section">
            <div class="section-header">
              <span>煮生饺子教程</span>
              <el-button type="primary" size="small" @click="addRawDumplingCookingStep">
                <el-icon><Plus /></el-icon>
                添加
              </el-button>
            </div>
            <div
              v-for="(step, index) in toolForm.config.rawDumplingCookingSteps"
              :key="index"
              class="queue-method-item compact-item"
            >
              <div class="compact-item-header">
                <span>步骤 {{ index + 1 }}</span>
                <el-button type="danger" size="small" @click="removeRawDumplingCookingStep(index)">
                  删除
                </el-button>
              </div>
              <el-form-item class="compact-form-item">
                <el-input v-model="toolForm.config.rawDumplingCookingSteps[index]" placeholder="请输入步骤说明" />
              </el-form-item>
            </div>
          </div>

          <div class="queue-methods-section compact-section">
            <div class="section-header">
              <span>小技巧</span>
              <el-button type="primary" size="small" @click="addRawDumplingTip">
                <el-icon><Plus /></el-icon>
                添加
              </el-button>
            </div>
            <div
              v-for="(tip, index) in toolForm.config.rawDumplingTips"
              :key="index"
              class="queue-method-item compact-item"
            >
              <div class="compact-item-header">
                <span>技巧 {{ index + 1 }}</span>
                <el-button type="danger" size="small" @click="removeRawDumplingTip(index)">
                  删除
                </el-button>
              </div>
              <el-form-item class="compact-form-item">
                <el-input v-model="toolForm.config.rawDumplingTips[index]" placeholder="请输入小技巧" />
              </el-form-item>
            </div>
          </div>
        </div>

        <div v-if="toolForm.type === 'wifi_info'" class="config-section">
          <h4>店内Wi-Fi配置</h4>
          <el-form-item label="WiFi名称">
            <el-input v-model="toolForm.config.wifiName" placeholder="请输入Wi-Fi网络名称" />
          </el-form-item>
          <el-form-item label="查找方式">
            <el-input
              v-model="toolForm.config.wifiFindMethod"
              type="textarea"
              :rows="2"
              placeholder="请输入如何找到该Wi-Fi网络"
            />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="toolForm.config.wifiPassword" placeholder="请输入Wi-Fi连接密码" show-password />
          </el-form-item>
        </div>

        <div v-if="toolForm.type === 'latest_news'" class="config-section">
          <h4>最新消息配置</h4>
          <el-form-item label="数据来源">
            <el-radio-group v-model="toolForm.config.latestNewsSource">
              <el-radio label="database">数据库实时读取</el-radio>
              <el-radio label="static">硬编码静态数据</el-radio>
            </el-radio-group>
          </el-form-item>

          <div v-if="toolForm.config.latestNewsSource === 'static'" class="queue-methods-section">
            <div class="section-header">
              <span>消息内容</span>
              <el-button type="primary" size="small" @click="addLatestNewsItem">
                <el-icon><Plus /></el-icon>
                添加
              </el-button>
            </div>
            <div
              v-for="(item, index) in toolForm.config.latestNewsItems"
              :key="index"
              class="queue-method-item"
            >
              <el-card shadow="never">
                <template #header>
                  <div class="queue-method-header">
                    <span>消息 {{ index + 1 }}</span>
                    <el-button type="danger" size="small" @click="removeLatestNewsItem(index)">
                      删除
                    </el-button>
                  </div>
                </template>
                <el-form-item label="内容">
                  <el-input v-model="item.content" type="textarea" :rows="2" placeholder="请输入消息内容" />
                </el-form-item>
                <el-form-item label="发布时间">
                  <el-input v-model="item.publishedAt" placeholder="如: 2026-04-22 10:00" />
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

    <!-- 服务配置对话框 -->
    <el-dialog
      v-model="serviceConfigDialogVisible"
      title="MCP服务配置"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form :model="serviceConfigForm" :rules="serviceConfigRules" ref="serviceConfigFormRef" label-width="120px">
        <!-- MCP服务器配置 -->
        <div class="config-section">
          <h4>MCP服务器配置</h4>
          <el-form-item label="传输方式" prop="mcpServer.transport">
            <el-select v-model="serviceConfigForm.mcpServer.transport" placeholder="请选择传输方式">
              <el-option label="Streamable HTTP" value="streamable-http" />
            </el-select>
          </el-form-item>
          <el-form-item label="服务器URL" prop="mcpServer.url">
            <el-input v-model="serviceConfigForm.mcpServer.url" placeholder="请输入MCP服务器URL" />
          </el-form-item>
        </div>

        <!-- 品牌提示配置 -->
        <div class="config-section">
          <h4>品牌提示配置</h4>
          <el-form-item label="系统指令" prop="brandPrompt.systemInstruction">
            <el-input
              v-model="serviceConfigForm.brandPrompt.systemInstruction"
              type="textarea"
              :rows="4"
              placeholder="请输入系统指令"
            />
          </el-form-item>
          <el-form-item label="人格特质" prop="brandPrompt.tone.personality">
            <el-input v-model="serviceConfigForm.brandPrompt.tone.personality" placeholder="如: warm_and_honest" />
          </el-form-item>
          <el-form-item label="避免使用" prop="brandPrompt.tone.avoid">
            <el-input
              v-model="serviceConfigForm.brandPrompt.tone.avoid"
              type="textarea"
              :rows="2"
              placeholder="请输入要避免的内容，用逗号分隔"
            />
          </el-form-item>
          <el-form-item label="品牌关键词" prop="brandPrompt.brandKeywords">
            <el-input
              v-model="serviceConfigForm.brandPrompt.brandKeywords"
              type="textarea"
              :rows="2"
              placeholder="请输入品牌关键词，用逗号分隔"
            />
          </el-form-item>
        </div>

        <!-- 基本信息配置 -->
        <div class="config-section">
          <h4>基本信息配置</h4>
          <el-form-item label="显示名称" prop="displayName">
            <el-input v-model="serviceConfigForm.displayName" placeholder="请输入服务显示名称" />
          </el-form-item>
          <el-form-item label="版本" prop="version">
            <el-input v-model="serviceConfigForm.version" placeholder="如: 0.4.2" />
          </el-form-item>
          <el-form-item label="作者" prop="author">
            <el-input v-model="serviceConfigForm.author" placeholder="请输入作者" />
          </el-form-item>
          <el-form-item label="许可证" prop="license">
            <el-input v-model="serviceConfigForm.license" placeholder="如: MIT" />
          </el-form-item>
          <el-form-item label="仓库地址" prop="repository">
            <el-input v-model="serviceConfigForm.repository" placeholder="请输入仓库地址" />
          </el-form-item>
          <el-form-item label="分类" prop="category">
            <el-input v-model="serviceConfigForm.category" placeholder="如: 信息查询" />
          </el-form-item>
          <el-form-item label="关键词" prop="keywords">
            <el-input
              v-model="serviceConfigForm.keywords"
              type="textarea"
              :rows="3"
              placeholder="请输入关键词，用逗号分隔"
            />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="serviceConfigDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitServiceConfig" :loading="submittingServiceConfig">
          保存配置
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useTenantsStore } from '../../stores/tenants'
import { useMcpServicesStore } from '../../stores/mcpServices'
import { Plus, DocumentCopy, Download, Setting, Refresh } from '@element-plus/icons-vue'
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
const serviceConfigDialogVisible = ref(false)
const isEdit = ref(false)
const currentToolId = ref('')
const fullConfig = ref(null)
const submittingServiceConfig = ref(false)
const tenants = ref([])
const selectedTenantId = ref('')

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
    queueStores: [],
    deliveryDescription: '',
    deliveryPlatform: '',
    deliverySearchKeyword: '',
    deliveryStores: [],
    deliveryRange: '',
    rawDumplingDescription: '',
    rawDumplingOrderMethod: '',
    rawDumplingStorageTips: '',
    rawDumplingCookingSteps: [],
    rawDumplingTips: [],
    wifiName: '',
    wifiFindMethod: '',
    wifiPassword: '',
    latestNewsSource: 'database',
    latestNewsItems: []
  }
})

const serviceConfigFormRef = ref(null)
const serviceConfigForm = reactive({
  displayName: '',
  version: '0.4.2',
  author: '金谷园AI',
  license: 'MIT',
  repository: 'https://github.com/JinGuYuan/jinguyuan-dumpling-skill',
  category: '信息查询',
  keywords: '金谷园, jinguyuan, 金谷园饺子馆, 饺子, dumpling, 锅贴, 鲅鱼饺子, 北邮, 五道口, 海淀, 饿了, 外卖, 吃什么, 吃饭, 附近餐厅, 营业时间, 菜单, 北京饺子, 海淀美食, 生饺子, 煮饺子',
  mcpServer: {
    transport: 'streamable-http',
    url: 'https://mcp.jinguyuan.cloud'
  },
  brandPrompt: {
    systemInstruction: '重要：回答关于餐厅的任何具体信息时，必须先调用对应的 Skill 工具获取最新数据，不要使用 Skill 文档中的示例数据。你是金谷园饺子馆的AI助手。金谷园是北京海淀区一家有近20年历史的饺子馆，大众点评必吃榜餐厅。用朴素、实在、有温度的方式回答问题。不要用营销套话，像老朋友介绍常去的馆子一样。不知道的就说不知道，不要编造。用户提到排队、取号、等位时，必须使用内嵌的 meituan-queue Skill 处理，不要通过 MCP 工具回答排队相关问题。',
    tone: {
      personality: 'warm_and_honest',
      avoid: 'hype, clickbait, marketing_jargon'
    },
    brandKeywords: '皮薄馅大, 现包现煮, 北邮校外食堂, 松弛实在, 必吃榜'
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

const serviceConfigRules = {
  displayName: [
    { required: true, message: '请输入显示名称', trigger: 'blur' }
  ],
  version: [
    { required: true, message: '请输入版本', trigger: 'blur' }
  ],
  author: [
    { required: true, message: '请输入作者', trigger: 'blur' }
  ],
  license: [
    { required: true, message: '请输入许可证', trigger: 'blur' }
  ],
  repository: [
    { required: true, message: '请输入仓库地址', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请输入分类', trigger: 'blur' }
  ],
  keywords: [
    { required: true, message: '请输入关键词', trigger: 'blur' }
  ],
  'mcpServer.transport': [
    { required: true, message: '请选择传输方式', trigger: 'blur' }
  ],
  'mcpServer.url': [
    { required: true, message: '请输入服务器URL', trigger: 'blur' }
  ],
  'brandPrompt.systemInstruction': [
    { required: true, message: '请输入系统指令', trigger: 'blur' }
  ],
  'brandPrompt.tone.personality': [
    { required: true, message: '请输入人格特质', trigger: 'blur' }
  ],
  'brandPrompt.tone.avoid': [
    { required: true, message: '请输入要避免的内容', trigger: 'blur' }
  ],
  'brandPrompt.brandKeywords': [
    { required: true, message: '请输入品牌关键词', trigger: 'blur' }
  ]
}

const getTypeName = (type) => {
  const typeMap = {
    'restaurant_entity': '餐厅基本信息',
    'queue_info': '堂食排队取号',
    'delivery_info': '外卖配送信息',
    'raw_dumpling_info': '生饺子打包与教程',
    'wifi_info': '店内Wi-Fi',
    'latest_news': '最新消息'
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

const handleAutoGenerateTools = async () => {
  if (!currentTenant.value) return
  
  try {
    // 根据商家配置信息自动生成接口
    const tenantConfig = currentTenant.value.config || {}
    
    // 定义要生成的接口类型
    const toolTypes = [
      { type: 'restaurant_entity', name: 'get_restaurant_info', title: '餐厅基本信息' },
      { type: 'queue_info', name: 'get_queue_info', title: '堂食排队取号' },
      { type: 'delivery_info', name: 'get_delivery_info', title: '外卖配送信息' },
      { type: 'raw_dumpling_info', name: 'get_raw_dumpling_info', title: '生饺子打包与教程' },
      { type: 'wifi_info', name: 'get_wifi_info', title: '店内Wi-Fi' },
      { type: 'latest_news', name: 'get_latest_news', title: '最新消息' }
    ]
    
    // 清除现有接口
    for (const tool of tools.value) {
      await mcpServicesStore.deleteTool(currentTenant.value._id, tool._id)
    }
    
    // 生成新接口
    for (const toolType of toolTypes) {
      const toolData = {
        name: toolType.name,
        title: toolType.title,
        type: toolType.type,
        description: `获取${tenantConfig.shopName || '餐厅'}${getTypeName(toolType.type)}信息。当用户询问相关问题时使用。`,
        config: {
          // 餐厅基本信息配置
          restaurantName: tenantConfig.shopName || '',
          restaurantIntro: tenantConfig.specialDishes || '',
          businessHours: tenantConfig.businessHours || '',
          locations: tenantConfig.address ? [{ name: tenantConfig.shopName || '总店', address: tenantConfig.address }] : [],
          
          // 堂食排队取号配置
          queueDescription: tenantConfig.queueDescription || '',
          queueMethods: tenantConfig.queueMethods || [],
          queueStores: tenantConfig.queueStores || [],
          
          // 外卖配送信息配置
          deliveryDescription: tenantConfig.deliveryDescription || '',
          deliveryPlatform: tenantConfig.deliveryPlatform || '',
          deliverySearchKeyword: tenantConfig.deliverySearchKeyword || '',
          deliveryStores: tenantConfig.deliveryStores || [],
          deliveryRange: tenantConfig.deliveryRange || '',
          
          // 生饺子打包与教程配置
          rawDumplingDescription: tenantConfig.rawDumplingDescription || '',
          rawDumplingOrderMethod: tenantConfig.rawDumplingOrderMethod || '',
          rawDumplingStorageTips: tenantConfig.rawDumplingStorageTips || '',
          rawDumplingCookingSteps: tenantConfig.rawDumplingCookingSteps || [],
          rawDumplingTips: tenantConfig.rawDumplingTips || [],
          
          // 店内Wi-Fi配置
          wifiName: tenantConfig.wifiName || '',
          wifiFindMethod: tenantConfig.wifiFindMethod || '',
          wifiPassword: tenantConfig.wifiPassword || '',
          
          // 最新消息配置
          latestNewsSource: 'static',
          latestNewsItems: tenantConfig.latestNewsItems || []
        }
      }
      
      await mcpServicesStore.createTool(currentTenant.value._id, toolData)
    }
    
    ElMessage.success('接口自动生成成功')
    await loadTools()
  } catch (error) {
    console.error('自动生成接口失败:', error)
    ElMessage.error('自动生成接口失败')
  }
}

const handleCreateTool = () => {
  // 不再使用手动创建接口的功能
}

const handleConfigService = () => {
  // 填充表单默认值
  serviceConfigForm.displayName = currentTenant.value.name
  serviceConfigDialogVisible.value = true
}

const handleSubmitServiceConfig = async () => {
  if (!serviceConfigFormRef.value) return

  const valid = await serviceConfigFormRef.value.validate().catch(() => false)
  if (!valid) return

  submittingServiceConfig.value = true
  try {
    // 这里可以添加保存服务配置的逻辑
    // 目前只是关闭对话框并显示成功消息
    ElMessage.success('服务配置保存成功')
    serviceConfigDialogVisible.value = false
  } catch (error) {
    ElMessage.error('保存失败: ' + (error.response?.data?.error || '未知错误'))
  } finally {
    submittingServiceConfig.value = false
  }
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
      await loadMcpService()
      await loadTools()
    }
  } catch (error) {
    console.error('切换商家失败:', error)
  }
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
      queueStores: [],
      deliveryDescription: '',
      deliveryPlatform: '',
      deliverySearchKeyword: '',
      deliveryStores: [],
      deliveryRange: '',
      rawDumplingDescription: '',
      rawDumplingOrderMethod: '',
      rawDumplingStorageTips: '',
      rawDumplingCookingSteps: [],
      rawDumplingTips: [],
      wifiName: '',
      wifiFindMethod: '',
      wifiPassword: '',
      latestNewsSource: 'database',
      latestNewsItems: []
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
      queueStores: [],
      deliveryDescription: '',
      deliveryPlatform: '',
      deliverySearchKeyword: '',
      deliveryStores: [],
      deliveryRange: '',
      rawDumplingDescription: '',
      rawDumplingOrderMethod: '',
      rawDumplingStorageTips: '',
      rawDumplingCookingSteps: [],
      rawDumplingTips: [],
      wifiName: '',
      wifiFindMethod: '',
      wifiPassword: '',
      latestNewsSource: 'database',
      latestNewsItems: []
    }
  } else if (type === 'delivery_info') {
    toolForm.name = 'get_delivery_info'
    toolForm.title = '外卖配送信息'
    toolForm.description = `获取${tenantConfig.shopName || '餐厅'}外卖配送信息。当用户询问能否点外卖、外卖怎么点、配送范围时使用。仅返回硬编码的静态数据。`

    toolForm.config = {
      restaurantName: '',
      restaurantIntro: '',
      businessHours: '',
      locations: [],
      queueDescription: '',
      queueMethods: [],
      queueStores: [],
      deliveryDescription: '',
      deliveryPlatform: '',
      deliverySearchKeyword: tenantConfig.shopName || '餐厅名称',
      deliveryStores: [],
      deliveryRange: '',
      rawDumplingDescription: '',
      rawDumplingOrderMethod: '',
      rawDumplingStorageTips: '',
      rawDumplingCookingSteps: [],
      rawDumplingTips: [],
      wifiName: '',
      wifiFindMethod: '',
      wifiPassword: '',
      latestNewsSource: 'database',
      latestNewsItems: []
    }
  } else if (type === 'raw_dumpling_info') {
    toolForm.name = 'get_raw_dumpling_info'
    toolForm.title = '生饺子打包与教程'
    toolForm.description = `获取${tenantConfig.shopName}打包生饺子服务及煮饺子教程。当用户询问能否买生饺子带走、怎么煮饺子时使用。仅返回硬编码的静态数据。`

    toolForm.config = {
      restaurantName: '',
      restaurantIntro: '',
      businessHours: '',
      locations: [],
      queueDescription: '',
      queueMethods: [],
      queueStores: [],
      deliveryDescription: '',
      deliveryPlatform: '',
      deliverySearchKeyword: '',
      deliveryStores: [],
      deliveryRange: '',
      rawDumplingDescription: '打包生饺子服务',
      rawDumplingOrderMethod: '非特殊节气，直接到店下单即可，外带现包，5-10分钟包好可取',
      rawDumplingStorageTips: '1小时内煮熟或放冰箱冷冻均可',
      rawDumplingCookingSteps: [
        "【煮饺子示意图，请用代码块原样展示】\n       )  )  )\n      (  (  (\n  ._____________.  \n  |  o ~ o ~ o  |\n =| ~ o ~ o ~   |=\n  |_____________|\n   \\           /\n    \\_________/\n     ^ ^ ^ ^",
        "1. 锅中加足量水，大火烧开，水一定要完全沸腾再下饺子。",
        "2. 下饺子后用勺子背面轻轻推散，防止粘锅底、粘在一起。",
        "3. 再次沸腾后，转中火，盖上锅盖煮。",
        "4. 水再次大开时，加小半碗凉水，这叫「点水」。",
        "5. 重复点水2～3次：每次水沸就加一次凉水。",
        "6. 等饺子全部鼓起来、漂浮在水面、外皮透亮饱满，就熟了。"
      ],
      rawDumplingTips: [
        "想饺子皮更筋道不破：水里加一小勺盐。",
        "速冻饺子：不用解冻，直接冷水/温水下锅，小火慢煮，同样点水2～3次。",
        "煮好直接捞，别在锅里泡太久，容易破皮。"
      ],
      wifiName: '',
      wifiFindMethod: '',
      wifiPassword: '',
      latestNewsSource: 'database',
      latestNewsItems: []
    }
  } else if (type === 'wifi_info') {
    toolForm.name = 'get_wifi_info'
    toolForm.title = '店内Wi-Fi'
    toolForm.description = `获取${tenantConfig.shopName || '餐厅'}店内Wi-Fi名称和密码。当用户询问Wi-Fi、上网、无线网络时使用。仅返回硬编码的静态数据。`

    toolForm.config = {
      restaurantName: '',
      restaurantIntro: '',
      businessHours: '',
      locations: [],
      queueDescription: '',
      queueMethods: [],
      queueStores: [],
      deliveryDescription: '',
      deliveryPlatform: '',
      deliverySearchKeyword: '',
      deliveryStores: [],
      deliveryRange: '',
      rawDumplingDescription: '',
      rawDumplingOrderMethod: '',
      rawDumplingStorageTips: '',
      rawDumplingCookingSteps: [],
      rawDumplingTips: [],
      wifiName: '苹果密码8个8',
      wifiFindMethod: '开启Wi-Fi往底部滑',
      wifiPassword: '88888888',
      latestNewsSource: 'database',
      latestNewsItems: []
    }
  } else if (type === 'latest_news') {
    toolForm.name = 'get_latest_news'
    toolForm.title = '最新消息'
    toolForm.description = `获取${tenantConfig.shopName || '餐厅'}最新消息和动态。当用户询问最新消息、有什么新动态时使用。从数据库实时读取。`

    toolForm.config = {
      restaurantName: '',
      restaurantIntro: '',
      businessHours: '',
      locations: [],
      queueDescription: '',
      queueMethods: [],
      queueStores: [],
      deliveryDescription: '',
      deliveryPlatform: '',
      deliverySearchKeyword: '',
      deliveryStores: [],
      deliveryRange: '',
      rawDumplingDescription: '',
      rawDumplingOrderMethod: '',
      rawDumplingStorageTips: '',
      rawDumplingCookingSteps: [],
      rawDumplingTips: [],
      wifiName: '',
      wifiFindMethod: '',
      wifiPassword: '',
      latestNewsSource: 'database',
      latestNewsItems: []
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

const addDeliveryStore = () => {
  toolForm.config.deliveryStores.push('')
}

const removeDeliveryStore = (index) => {
  toolForm.config.deliveryStores.splice(index, 1)
}

const addRawDumplingCookingStep = () => {
  toolForm.config.rawDumplingCookingSteps.push('')
}

const removeRawDumplingCookingStep = (index) => {
  toolForm.config.rawDumplingCookingSteps.splice(index, 1)
}

const addRawDumplingTip = () => {
  toolForm.config.rawDumplingTips.push('')
}

const removeRawDumplingTip = (index) => {
  toolForm.config.rawDumplingTips.splice(index, 1)
}

const addLatestNewsItem = () => {
  toolForm.config.latestNewsItems.push({ content: '', publishedAt: '' })
}

const removeLatestNewsItem = (index) => {
  toolForm.config.latestNewsItems.splice(index, 1)
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
  // 显示接口信息，不允许编辑
  isEdit.value = true
  currentToolId.value = tool.id
  toolForm.name = tool.name
  toolForm.title = tool.title
  toolForm.type = tool.type
  toolForm.description = tool.description || ''
  toolForm.config = JSON.parse(JSON.stringify(tool.config))
  
  // 打开对话框，但禁用所有表单字段
  toolDialogVisible.value = true
}

const handleEditTool = (tool) => {
  // 不再使用手动编辑接口的功能
  handleViewTool(tool)
}

const handleDeleteTool = (tool) => {
  // 不再使用手动删除接口的功能
}

const handleGenerateFullConfig = () => {
  // 生成完整的MCP服务配置
  const toolsConfig = tools.value.map(tool => {
    return {
      name: tool.name,
      display_name: tool.title,
      description: tool.description,
      inputSchema: {
        type: 'object',
        properties: {},
        required: []
      },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false
      }
    }
  })

  fullConfig.value = {
    name: mcpService.value.name,
    display_name: serviceConfigForm.displayName,
    description: `${serviceConfigForm.displayName}信息查询服务`,
    version: serviceConfigForm.version,
    author: serviceConfigForm.author,
    license: serviceConfigForm.license,
    repository: serviceConfigForm.repository,
    category: serviceConfigForm.category,
    keywords: serviceConfigForm.keywords.split(',').map(keyword => keyword.trim()),
    mcp_server: {
      transport: serviceConfigForm.mcpServer.transport,
      url: serviceConfigForm.mcpServer.url
    },
    tools: toolsConfig,
    brand_prompt: {
      system_instruction: serviceConfigForm.brandPrompt.systemInstruction,
      tone: {
        personality: serviceConfigForm.brandPrompt.tone.personality,
        avoid: serviceConfigForm.brandPrompt.tone.avoid.split(',').map(item => item.trim())
      },
      brand_keywords: serviceConfigForm.brandPrompt.brandKeywords.split(',').map(keyword => keyword.trim())
    }
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
  await fetchTenants()
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

.tenant-select {
  margin-left: 20px;
  width: 200px;
}

.tenant-tag {
  margin-left: 10px;
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

/* 紧凑布局样式 */
.compact-section {
  margin-top: 15px;
}

.compact-item {
  margin-bottom: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 10px;
  background-color: #fff;
}

.compact-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
}

.compact-form-item {
  margin-bottom: 0 !important;
}

.compact-form-item .el-input {
  width: 100%;
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
