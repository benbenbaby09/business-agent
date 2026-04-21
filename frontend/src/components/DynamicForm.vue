<template>
  <el-form
    :model="formData"
    :rules="formRules"
    ref="formRef"
    label-width="100px"
  >
    <template v-for="field in templateFields" :key="field.name">
      <!-- 文本输入 -->
      <el-form-item
        v-if="field.type === 'text'"
        :label="field.label"
        :prop="field.name"
      >
        <el-input
          v-model="formData[field.name]"
          :placeholder="field.placeholder"
          clearable
        />
      </el-form-item>

      <!-- 文本域 -->
      <el-form-item
        v-else-if="field.type === 'textarea'"
        :label="field.label"
        :prop="field.name"
      >
        <el-input
          v-model="formData[field.name]"
          type="textarea"
          :rows="field.rows || 3"
          :placeholder="field.placeholder"
        />
      </el-form-item>

      <!-- 数字输入 -->
      <el-form-item
        v-else-if="field.type === 'number'"
        :label="field.label"
        :prop="field.name"
      >
        <el-input-number
          v-model="formData[field.name]"
          :placeholder="field.placeholder"
          :min="field.min"
          :max="field.max"
        />
      </el-form-item>

      <!-- 选择器 -->
      <el-form-item
        v-else-if="field.type === 'select'"
        :label="field.label"
        :prop="field.name"
      >
        <el-select
          v-model="formData[field.name]"
          :placeholder="field.placeholder"
          clearable
        >
          <el-option
            v-for="option in field.options"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </el-form-item>

      <!-- 开关 -->
      <el-form-item
        v-else-if="field.type === 'switch'"
        :label="field.label"
        :prop="field.name"
      >
        <el-switch v-model="formData[field.name]" />
      </el-form-item>

      <!-- 单选框 -->
      <el-form-item
        v-else-if="field.type === 'radio'"
        :label="field.label"
        :prop="field.name"
      >
        <el-radio-group v-model="formData[field.name]">
          <el-radio
            v-for="option in field.options"
            :key="option.value"
            :label="option.value"
          >
            {{ option.label }}
          </el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 复选框 -->
      <el-form-item
        v-else-if="field.type === 'checkbox'"
        :label="field.label"
        :prop="field.name"
      >
        <el-checkbox-group v-model="formData[field.name]">
          <el-checkbox
            v-for="option in field.options"
            :key="option.value"
            :label="option.value"
          >
            {{ option.label }}
          </el-checkbox>
        </el-checkbox-group>
      </el-form-item>
    </template>

    <el-form-item>
      <el-button type="primary" @click="handleSubmit" :loading="loading">
        {{ submitText }}
      </el-button>
      <el-button @click="handleReset">重置</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { getTemplate, generateInitialData, validateFormData } from '../templates/skillTemplates'

const props = defineProps({
  templateType: {
    type: String,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  submitText: {
    type: String,
    default: '保存'
  },
  initialData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['submit', 'reset'])

const formRef = ref(null)
const formData = reactive({})

// 获取模板配置
const template = computed(() => getTemplate(props.templateType))

// 获取模板字段
const templateFields = computed(() => {
  return template.value?.fields || []
})

// 生成表单验证规则
const formRules = computed(() => {
  const rules = {}
  templateFields.value.forEach(field => {
    if (field.rules) {
      rules[field.name] = field.rules
    }
  })
  return rules
})

// 监听模板类型变化，初始化表单数据
watch(() => props.templateType, (newType) => {
  if (newType && getTemplate(newType)) {
    const initialData = generateInitialData(newType)
    Object.assign(formData, initialData, props.initialData)
  }
}, { immediate: true })

// 监听初始数据变化
watch(() => props.initialData, (newData) => {
  if (newData && Object.keys(newData).length > 0) {
    Object.assign(formData, newData)
  }
}, { deep: true })

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate((valid) => {
    if (valid) {
      // 验证通过，触发submit事件
      const validation = validateFormData(props.templateType, formData)
      if (validation.valid) {
        emit('submit', { ...formData })
      }
    }
  })
}

// 重置表单
const handleReset = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  const initialData = generateInitialData(props.templateType)
  Object.assign(formData, initialData)
  emit('reset')
}

// 获取表单数据
const getFormData = () => {
  return { ...formData }
}

// 设置表单数据
const setFormData = (data) => {
  Object.assign(formData, data)
}

// 验证表单
const validate = () => {
  return formRef.value?.validate()
}

// 暴露方法
defineExpose({
  getFormData,
  setFormData,
  validate,
  resetFields: handleReset
})
</script>

<style scoped>
/* 可以在这里添加自定义样式 */
</style>
