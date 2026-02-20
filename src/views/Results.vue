<template>
  <div>
    <h2 class="text-3xl font-bold mb-8">结果管理</h2>
    
    <!-- 详情弹窗 - 左右布局 -->
    <div v-if="showDetailModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="showDetailModal = false">
      <div class="bg-white rounded-lg w-full max-w-5xl" style="height: 70vh; display: flex; flex-direction: column;">
        <div class="flex justify-between items-center p-4 border-b" style="flex-shrink: 0;">
          <h3 class="text-xl font-bold">内容详情</h3>
          <button class="p-2 hover:bg-gray-100 rounded-full" @click="closeDetailModal">
            <X :size="20" />
          </button>
        </div>
        <div class="flex-1 overflow-hidden" style="flex: 1;">
          <div class="grid grid-cols-2 h-full">
            <!-- 左侧：爬取内容 -->
            <div class="p-4 overflow-y-auto border-r" style="height: 100%;">
              <h4 class="font-semibold text-lg mb-4">爬取内容</h4>
              <div class="space-y-4 pb-4">
                <div>
                  <span class="text-gray-500 font-medium">标题：</span>
                  <span class="text-lg">{{ selectedResult?.title || '无' }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span v-if="selectedResult?.source" class="px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs">{{ selectedResult.sourceName || selectedResult.source }}</span>
                  <span v-if="selectedResult?.category" class="px-2 py-0.5 bg-indigo-100 text-indigo-800 rounded-full text-xs">{{ selectedResult.category }}</span>
                  <span v-if="selectedResult?.taskName" class="px-2 py-0.5 bg-green-100 text-green-800 rounded-full text-xs">{{ selectedResult.taskName }}</span>
                </div>
                <div v-if="selectedResult?.publishTime || selectedResult?.date_str">
                  <span class="text-gray-500 font-medium">发布时间：</span>
                  <span>{{ selectedResult?.publishTime || selectedResult?.date_str }}</span>
                </div>
                <div v-if="selectedResult?.coverUrl">
                  <span class="text-gray-500 font-medium">封面图：</span>
                  <img :src="selectedResult.coverUrl" alt="封面" class="mt-2 max-w-full h-auto rounded-lg" style="max-width: 200px;" />
                </div>
                <div>
                  <span class="text-gray-500 font-medium">文章内容：</span>
                  <div class="mt-2 p-4 bg-gray-50 rounded-lg max-h-80 overflow-y-auto whitespace-pre-wrap text-sm">{{ selectedResult?.content || '无内容' }}</div>
                </div>
                <div v-if="selectedResult?.article_url">
                  <span class="text-gray-500 font-medium">原文链接：</span>
                  <a :href="selectedResult.article_url" target="_blank" class="text-blue-500 hover:underline ml-1">{{ selectedResult.article_url }}</a>
                </div>
              </div>
            </div>
            
            <!-- 右侧：AI处理 -->
            <div class="p-4 overflow-y-auto" style="height: 100%;">
              <h4 class="font-semibold text-lg mb-4">AI处理</h4>
              <div class="space-y-4 pb-4">
                <div>
                  <label class="block text-sm font-medium mb-1">选择API</label>
                  <select v-model="selectedApiId" class="w-full px-3 py-2 border rounded-lg">
                    <option value="">请选择API</option>
                    <option v-for="api in apiList" :key="api.id" :value="api.id">{{ api.name }} ({{ api.model || api.api_type }})</option>
                  </select>
                </div>
                
                <button 
                  @click="generateContent"
                  :disabled="!selectedApiId || isGenerating"
                  class="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  {{ isGenerating ? '生成中...' : '生成' }}
                </button>
                
                <div v-if="generatedContent">
                  <div class="flex items-center justify-between">
                    <span class="text-gray-500 font-medium">处理结果</span>
                    <button @click="copyGeneratedContent" class="text-sm text-blue-500 hover:text-blue-700">复制</button>
                  </div>
                  <div class="mt-2 p-4 bg-gray-50 rounded-lg max-h-80 overflow-y-auto whitespace-pre-wrap text-sm">{{ generatedContent }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="card p-6">
      <div class="flex justify-between items-center mb-4">
        <div class="flex items-center space-x-4">
          <select v-model="sourceFilter" class="p-2 border rounded-lg bg-gray-50">
            <option value="all">全部新闻源</option>
            <option v-for="src in newsSources" :key="src.id" :value="src.id">{{ src.name }}</option>
          </select>
          <select v-model="categoryFilter" :disabled="sourceFilter === 'all'" size="1" :class="sourceFilter === 'all' ? 'p-2 border rounded-lg bg-gray-200 text-gray-400 cursor-not-allowed' : 'p-2 border rounded-lg bg-gray-50'" style="max-height: 300px; overflow-y: auto;">
            <option value="all">全部分类</option>
            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
          <select v-model="taskIdFilter" class="p-2 border rounded-lg bg-gray-50">
            <option value="all">选择任务</option>
            <option v-for="task in tasks" :key="task.id" :value="task.id">{{ task.name }}</option>
          </select>
          <input 
            type="text" 
            v-model="searchTerm"
            class="p-2 border rounded-lg bg-gray-50" 
            placeholder="搜索内容..."
          >
        </div>
        <button class="btn-secondary px-4 py-2 rounded-lg font-semibold flex items-center space-x-2" @click="exportResults">
          <Download :size="18" />
          <span>导出数据</span>
        </button>
      </div>
      <div class="space-y-4">
        <div v-for="result in filteredResults" :key="result.id" class="card p-6">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="flex items-center space-x-2 mb-1">
                <h4 class="text-lg font-semibold">
                  <a :href="result.url" target="_blank" class="hover:text-indigo-600">{{ result.title }}</a>
                </h4>
                <span v-if="result.source" class="px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs">{{ result.sourceName || result.source }}</span>
                <span v-if="result.category" class="px-2 py-0.5 bg-indigo-100 text-indigo-800 rounded-full text-xs">{{ result.category }}</span>
                <span v-if="result.taskName" class="px-2 py-0.5 bg-green-100 text-green-800 rounded-full text-xs">{{ result.taskName }}</span>
              </div>
              <p class="text-gray-500 mt-2 line-clamp-2">{{ result.content }}</p>
            </div>
            <span class="text-xs text-gray-500 ml-4">{{ formatDate(result.createdAt) }}</span>
          </div>
          <div class="mt-4 flex justify-end space-x-2">
            <button class="p-1 text-indigo-600 hover:bg-gray-100 rounded" @click="viewResultDetail(result.id)">
              <Eye :size="18" />
            </button>
            <button class="p-1 text-red-500 hover:bg-gray-100 rounded" @click="deleteResult(result.id)">
              <Trash2 :size="18" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted, watch } from 'vue'
import { Download, Eye, Trash2, X } from 'lucide-vue-next'
import { useRoute } from 'vue-router'
import { newsSources, defaultCategories } from '../utils/constants'
import { formatDate } from '../utils/formatDate'

const route = useRoute()

const tasks = inject('tasks')
const results = inject('results')
const showToastMsg = inject('showToastMsg')
const handleResultDeleted = inject('handleResultDeleted')
const API_BASE = inject('API_BASE')
const fetchResults = inject('fetchResults')

const taskIdFilter = ref('all')
const searchTerm = ref('')
const categoryFilter = ref('all')
const sourceFilter = ref('all')
const showDetailModal = ref(false)
const selectedResult = ref(null)

const apiList = ref([])
const selectedApiId = ref('')
const isGenerating = ref(false)
const generatedContent = ref('')

onMounted(() => {
  fetchResults()
  fetchApiList()
  if (route.query.source) {
    sourceFilter.value = route.query.source
  }
})

const categories = computed(() => {
  if (sourceFilter.value === 'all') {
    return defaultCategories
  }
  const source = newsSources.find(s => s.id === sourceFilter.value)
  return source ? source.categories : []
})

const filteredResults = computed(() => {
  return results.value.filter(result => {
    const selectedSource = newsSources.find(s => s.id === sourceFilter.value)
    const sourceName = selectedSource ? selectedSource.name : null
    const matchesSource = sourceFilter.value === 'all' || result.source === sourceFilter.value || result.source === sourceName
    const matchesCategory = categoryFilter.value === 'all' || result.category === categoryFilter.value
    const matchesTask = taskIdFilter.value === 'all' || (result.taskId && result.taskId.toString() === taskIdFilter.value.toString())
    const matchesSearch = (result.title && result.title.toLowerCase().includes(searchTerm.value.toLowerCase())) || 
                         (result.content && result.content.toLowerCase().includes(searchTerm.value.toLowerCase()))
    return matchesSource && matchesCategory && matchesTask && matchesSearch
  })
})

const exportResults = () => {
  if (filteredResults.value.length === 0) {
    showToastMsg('没有可导出的数据！')
    return
  }
  
  const data = filteredResults.value
  const headers = ['id', 'title', 'source', 'category', 'author', 'publishTime', 'createdAt', 'content', 'article_url', 'taskId', 'taskName', 'coverUrl', 'imgList']
  const csvRows = [headers.join(',')]
  
  for (const row of data) {
    const values = headers.map(header => {
      const val = row[header] ?? ''
      const strVal = String(val).replace(/"/g, '""')
      return strVal.includes(',') || strVal.includes('"') || strVal.includes('\n') 
        ? `"${strVal}"` 
        : strVal
    })
    csvRows.push(values.join(','))
  }
  
  const csvContent = csvRows.join('\n')
  
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `crawler-results-${new Date().toISOString().slice(0,10)}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  showToastMsg('数据导出成功！')
}

const viewResultDetail = (resultId) => {
  const result = results.value.find(r => r.id === resultId)
  if (result) {
    selectedResult.value = result
    showDetailModal.value = true
  }
}

const deleteResult = async (resultId) => {
  if (confirm('确定要删除此结果吗？')) {
    try {
      await fetch(`${API_BASE}/results/${resultId}`, { method: 'DELETE' })
      handleResultDeleted(resultId)
    } catch (e) {
      showToastMsg('删除失败')
    }
  }
}

async function fetchApiList() {
  try {
    const res = await fetch(`${API_BASE}/api-keys`)
    apiList.value = await res.json()
  } catch (e) {
    console.error('获取API列表失败:', e)
  }
}

function closeDetailModal() {
  showDetailModal.value = false
  selectedApiId.value = ''
  generatedContent.value = ''
}

async function generateContent() {
  if (!selectedApiId.value) {
    showToastMsg('请选择API')
    return
  }
  
  if (!selectedResult.value || !selectedResult.value.content) {
    showToastMsg('没有可处理的内容')
    return
  }
  
  isGenerating.value = true
  generatedContent.value = ''
  
  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        api_key_id: selectedApiId.value,
        message: selectedResult.value.content
      })
    })
    
    const data = await res.json()
    if (data.success) {
      generatedContent.value = data.data
    } else {
      showToastMsg(data.detail || '生成失败')
    }
  } catch (e) {
    console.error('生成失败:', e)
    showToastMsg('生成失败')
  } finally {
    isGenerating.value = false
  }
}

function copyGeneratedContent() {
  if (generatedContent.value) {
    navigator.clipboard.writeText(generatedContent.value)
    showToastMsg('已复制到剪贴板')
  }
}
</script>
