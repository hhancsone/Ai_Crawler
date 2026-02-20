<template>
  <div>
    <h2 class="text-3xl font-bold mb-8">API管理</h2>
    
    <div class="card p-6 mb-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-xl font-semibold">API密钥列表</h3>
        <button 
          @click="showAddModal = true"
          class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          添加API
        </button>
      </div>
      
      <div v-if="apiKeys.length === 0" class="text-center py-8 text-gray-500">
        暂无API密钥，请点击"添加API"按钮添加
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-gray-50">
              <th class="px-4 py-2 text-left">名称</th>
              <th class="px-4 py-2 text-left">类型</th>
              <th class="px-4 py-2 text-left">API Key</th>
              <th class="px-4 py-2 text-left">Base URL</th>
              <th class="px-4 py-2 text-left">模型</th>
              <th class="px-4 py-2 text-center">状态</th>
              <th class="px-4 py-2 text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="key in apiKeys" :key="key.id" class="border-t">
              <td class="px-4 py-2">{{ key.name }}</td>
              <td class="px-4 py-2">{{ key.api_type }}</td>
              <td class="px-4 py-2 font-mono text-sm">{{ maskApiKey(key.api_key) }}</td>
              <td class="px-4 py-2">{{ key.api_base || '-' }}</td>
              <td class="px-4 py-2">{{ key.model || '-' }}</td>
              <td class="px-4 py-2 text-center">
                <button 
                  @click="toggleStatus(key)" 
                  :disabled="togglingId === key.id"
                  :class="key.status === 1 ? 'text-green-500 hover:text-green-700' : 'text-red-500 hover:text-red-700'"
                  :style="{ opacity: togglingId === key.id ? 0.5 : 1 }"
                >
                  {{ togglingId === key.id ? '...' : (key.status === 1 ? '启用' : '禁用') }}
                </button>
              </td>
              <td class="px-4 py-2 text-center">
                <button @click="editApiKey(key)" class="text-blue-500 hover:text-blue-700 mr-2">编辑</button>
                <button @click="deleteApiKey(key.id)" class="text-red-500 hover:text-red-700">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showAddModal || showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-xl font-semibold mb-4">{{ showEditModal ? '编辑API' : '添加API' }}</h3>
        
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">名称</label>
              <input 
                v-model="formData.name" 
                type="text" 
                class="w-full px-3 py-2 border rounded-lg"
                placeholder="如：OpenAI"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium mb-1">API类型</label>
              <input 
                v-model="formData.api_type" 
                type="text" 
                class="w-full px-3 py-2 border rounded-lg"
                placeholder="如：openai、deepseek等"
              />
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-1">API Key</label>
            <input 
              v-model="formData.api_key" 
              type="password" 
              class="w-full px-3 py-2 border rounded-lg"
              placeholder="请输入API Key"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-1">Base URL (可选)</label>
            <input 
              v-model="formData.api_base" 
              type="text" 
              class="w-full px-3 py-2 border rounded-lg"
              placeholder="如：https://api.openai.com/v1"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-1">模型</label>
            <input 
              v-model="formData.model" 
              type="text" 
              class="w-full px-3 py-2 border rounded-lg"
              placeholder="如：gpt-4、gpt-3.5-turbo"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-1">系统提示词 (可选)</label>
            <textarea 
              v-model="formData.prompt" 
              class="w-full px-3 py-2 border rounded-lg"
              rows="3"
              placeholder="设置系统提示词..."
            ></textarea>
          </div>
        </div>
        
        <div class="flex justify-end gap-2 mt-6">
          <button 
            @click="closeModal" 
            class="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
          >
            取消
          </button>
          <button 
            @click="submitForm" 
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            {{ showEditModal ? '保存' : '添加' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API_BASE = 'http://localhost:8000/api'

const apiKeys = ref([])
const showAddModal = ref(false)
const showEditModal = ref(false)
const editingId = ref(null)
const togglingId = ref(null)

const formData = ref({
  name: '',
  api_type: '',
  api_key: '',
  api_base: '',
  model: '',
  prompt: ''
})

async function fetchApiKeys() {
  try {
    const res = await fetch(`${API_BASE}/api-keys`)
    const data = await res.json()
    apiKeys.value = data
  } catch (e) {
    console.error('获取API密钥失败:', e)
  }
}

function maskApiKey(key) {
  if (!key) return ''
  if (key.length <= 8) return '***'
  return key.substring(0, 4) + '...' + key.substring(key.length - 4)
}

function resetForm() {
  formData.value = {
    name: '',
    api_type: '',
    api_key: '',
    api_base: '',
    model: '',
    prompt: ''
  }
}

function closeModal() {
  showAddModal.value = false
  showEditModal.value = false
  editingId.value = null
  resetForm()
}

function editApiKey(key) {
  editingId.value = key.id
  formData.value = {
    name: key.name,
    api_type: key.api_type,
    api_key: key.api_key,
    api_base: key.api_base || '',
    model: key.model || '',
    prompt: key.prompt || ''
  }
  showEditModal.value = true
}

async function submitForm() {
  try {
    const url = showEditModal.value 
      ? `${API_BASE}/api-keys/${editingId.value}`
      : `${API_BASE}/api-keys`
    const method = showEditModal.value ? 'PUT' : 'POST'
    
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData.value)
    })
    
    if (res.ok) {
      closeModal()
      fetchApiKeys()
    } else {
      alert('操作失败')
    }
  } catch (e) {
    console.error('操作失败:', e)
    alert('操作失败')
  }
}

async function deleteApiKey(id) {
  if (!confirm('确定要删除这个API密钥吗？')) return
  
  try {
    const res = await fetch(`${API_BASE}/api-keys/${id}`, {
      method: 'DELETE'
    })
    if (res.ok) {
      fetchApiKeys()
    } else {
      alert('删除失败')
    }
  } catch (e) {
    console.error('删除失败:', e)
    alert('删除失败')
  }
}

async function toggleStatus(key) {
  if (togglingId.value === key.id) return
  
  togglingId.value = key.id
  try {
    const newStatus = key.status === 1 ? 0 : 1
    const res = await fetch(`${API_BASE}/api-keys/${key.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: key.name,
        api_type: key.api_type,
        api_key: key.api_key,
        api_base: key.api_base,
        model: key.model,
        prompt: key.prompt,
        status: newStatus,
        is_default: key.is_default || 0
      })
    })
    if (res.ok) {
      fetchApiKeys()
    } else {
      alert('操作失败')
    }
  } catch (e) {
    console.error('操作失败:', e)
    alert('操作失败')
  } finally {
    togglingId.value = null
  }
}

onMounted(() => {
  fetchApiKeys()
})
</script>
