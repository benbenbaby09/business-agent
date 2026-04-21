// Skill模板配置
// 定义不同类型Skill的表单模板

export const skillTemplates = {
  restaurant_entity: {
    name: '餐饮实体',
    description: '适用于餐厅、咖啡馆等餐饮场所的Skill配置',
    fields: [
      {
        name: 'shopName',
        label: '店名',
        type: 'text',
        placeholder: '请输入店铺名称',
        required: true,
        rules: [
          { required: true, message: '请输入店名', trigger: 'blur' },
          { min: 2, max: 50, message: '店名长度在2-50个字符之间', trigger: 'blur' }
        ]
      },
      {
        name: 'address',
        label: '地址',
        type: 'text',
        placeholder: '请输入店铺地址',
        required: true,
        rules: [
          { required: true, message: '请输入地址', trigger: 'blur' }
        ]
      },
      {
        name: 'phone',
        label: '电话',
        type: 'text',
        placeholder: '请输入联系电话',
        required: true,
        rules: [
          { required: true, message: '请输入电话', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$|^0\d{2,3}-?\d{7,8}$/, message: '请输入正确的电话号码', trigger: 'blur' }
        ]
      },
      {
        name: 'businessHours',
        label: '营业时间',
        type: 'text',
        placeholder: '例如：09:00-22:00',
        required: true,
        rules: [
          { required: true, message: '请输入营业时间', trigger: 'blur' }
        ]
      },
      {
        name: 'wifiPassword',
        label: 'Wi-Fi密码',
        type: 'text',
        placeholder: '请输入Wi-Fi密码（可选）',
        required: false
      },
      {
        name: 'specialDishes',
        label: '特色菜品列表',
        type: 'textarea',
        placeholder: '请输入特色菜品，每行一个菜品',
        required: false,
        rows: 4
      }
    ]
  }
}

// 获取模板配置
export function getTemplate(type) {
  return skillTemplates[type] || null
}

// 获取所有模板类型
export function getTemplateTypes() {
  return Object.keys(skillTemplates).map(key => ({
    value: key,
    label: skillTemplates[key].name
  }))
}

// 生成初始表单数据
export function generateInitialData(type) {
  const template = getTemplate(type)
  if (!template) return {}
  
  const initialData = {}
  template.fields.forEach(field => {
    initialData[field.name] = ''
  })
  return initialData
}

// 验证表单数据
export function validateFormData(type, formData) {
  const template = getTemplate(type)
  if (!template) return { valid: false, errors: ['无效的模板类型'] }
  
  const errors = []
  template.fields.forEach(field => {
    if (field.required && !formData[field.name]) {
      errors.push(`${field.label}不能为空`)
    }
  })
  
  return {
    valid: errors.length === 0,
    errors
  }
}
