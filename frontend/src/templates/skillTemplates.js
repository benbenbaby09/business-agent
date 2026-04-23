// Skill模板配置

// 模板定义
const templates = {
  // 技能基本信息模板
  skillBasic: {
    fields: [
      {
        name: 'name',
        label: '技能名称',
        type: 'text',
        placeholder: '请输入技能名称',
        rules: [
          { required: true, message: '请输入技能名称', trigger: 'blur' },
          { min: 1, max: 50, message: '技能名称长度在 1 到 50 个字符之间', trigger: 'blur' }
        ]
      },
      {
        name: 'type',
        label: '技能类型',
        type: 'select',
        placeholder: '请选择技能类型',
        options: [
          { value: 'chat', label: '聊天' },
          { value: 'tool', label: '工具' },
          { value: 'custom', label: '自定义' }
        ],
        rules: [
          { required: true, message: '请选择技能类型', trigger: 'change' }
        ]
      },
      {
        name: 'description',
        label: '技能描述',
        type: 'textarea',
        placeholder: '请输入技能描述',
        rows: 3,
        rules: [
          { required: true, message: '请输入技能描述', trigger: 'blur' }
        ]
      },
      {
        name: 'version',
        label: '版本号',
        type: 'text',
        placeholder: '请输入版本号，如 1.0.0',
        rules: [
          { required: true, message: '请输入版本号', trigger: 'blur' }
        ]
      },
      {
        name: 'status',
        label: '状态',
        type: 'select',
        placeholder: '请选择技能状态',
        options: [
          { value: 'active', label: '活跃' },
          { value: 'inactive', label: '不活跃' }
        ],
        rules: [
          { required: true, message: '请选择技能状态', trigger: 'change' }
        ]
      }
    ]
  },
  // 技能详细配置模板
  skillConfig: {
    fields: [
      {
        name: 'timeout',
        label: '超时时间',
        type: 'number',
        placeholder: '请输入超时时间（秒）',
        min: 1,
        max: 300,
        rules: [
          { required: true, message: '请输入超时时间', trigger: 'blur' }
        ]
      },
      {
        name: 'memoryLimit',
        label: '内存限制',
        type: 'number',
        placeholder: '请输入内存限制（MB）',
        min: 128,
        max: 2048,
        rules: [
          { required: true, message: '请输入内存限制', trigger: 'blur' }
        ]
      },
      {
        name: 'enableLogging',
        label: '启用日志',
        type: 'switch'
      },
      {
        name: 'environment',
        label: '环境变量',
        type: 'textarea',
        placeholder: '请输入环境变量，JSON格式',
        rows: 4
      }
    ]
  }
}

/**
 * 获取模板配置
 * @param {string} templateType 模板类型
 * @returns {Object} 模板配置
 */
export function getTemplate(templateType) {
  return templates[templateType] || null
}

/**
 * 生成初始数据
 * @param {string} templateType 模板类型
 * @returns {Object} 初始数据
 */
export function generateInitialData(templateType) {
  const template = getTemplate(templateType)
  if (!template) return {}

  const initialData = {}
  template.fields.forEach(field => {
    switch (field.type) {
      case 'text':
      case 'textarea':
        initialData[field.name] = ''
        break
      case 'number':
        initialData[field.name] = field.min || 0
        break
      case 'select':
        initialData[field.name] = field.options?.[0]?.value || ''
        break
      case 'switch':
        initialData[field.name] = false
        break
      case 'radio':
        initialData[field.name] = field.options?.[0]?.value || ''
        break
      case 'checkbox':
        initialData[field.name] = []
        break
      default:
        initialData[field.name] = ''
    }
  })

  return initialData
}

/**
 * 验证表单数据
 * @param {string} templateType 模板类型
 * @param {Object} formData 表单数据
 * @returns {Object} 验证结果
 */
export function validateFormData(templateType, formData) {
  const template = getTemplate(templateType)
  if (!template) {
    return {
      valid: false,
      message: '模板不存在'
    }
  }

  // 简单的验证逻辑
  for (const field of template.fields) {
    if (field.rules) {
      for (const rule of field.rules) {
        if (rule.required && (!formData[field.name] || formData[field.name] === '')) {
          return {
            valid: false,
            message: rule.message || `请输入${field.label}`
          }
        }
        
        if (rule.min && formData[field.name].length < rule.min) {
          return {
            valid: false,
            message: rule.message || `${field.label}长度不能小于${rule.min}`
          }
        }
        
        if (rule.max && formData[field.name].length > rule.max) {
          return {
            valid: false,
            message: rule.message || `${field.label}长度不能大于${rule.max}`
          }
        }
      }
    }
  }

  return {
    valid: true,
    message: '验证通过'
  }
}
