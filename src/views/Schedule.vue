<template>
  <div>
    <h2 class="text-3xl font-bold mb-8">快速爬取</h2>
    
    <div class="mb-6 flex gap-4 items-end">
      <div class="flex-1">
        <label class="block text-sm font-medium mb-1">输入URL</label>
        <input 
          v-model="inputUrl" 
          type="text" 
          class="w-full px-3 py-2 border rounded-lg"
          placeholder="请输入新闻URL"
        />
      </div>
      <button 
        @click="pasteUrl"
        class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
      >
        粘贴
      </button>
      <button 
        @click="analyzeUrl"
        class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
      >
        识别URL
      </button>
      <button 
        @click="resetForm"
        class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
      >
        重置
      </button>
    </div>
    
    <div v-if="recognizedInfo" class="mb-4 bg-green-50 border border-green-200 rounded-lg p-4">
      <div class="flex items-center gap-4 text-sm">
        <span><span class="text-gray-500">新闻源：</span><span class="font-medium">{{ recognizedInfo.sourceName }}</span></span>
        <span><span class="text-gray-500">状态：</span><span class="font-medium text-green-600">已识别</span></span>
      </div>
    </div>
    
    <div v-if="crawledContent" class="grid grid-cols-2 gap-6">
      <div class="bg-white border border-gray-200 rounded-lg p-4">
        <h4 class="font-semibold text-lg mb-4">爬取内容</h4>
        <div class="space-y-4">
          <div>
            <span class="text-gray-500 font-medium">标题：</span>
            <span class="text-lg">{{ crawledContent.title || '无' }}</span>
          </div>
          <div v-if="crawledContent.date_str">
            <span class="text-gray-500 font-medium">发布时间：</span>
            <span>{{ crawledContent.date_str }}</span>
          </div>
          <div v-if="crawledContent.cover_url">
            <span class="text-gray-500 font-medium">封面图：</span>
            <img :src="crawledContent.cover_url" alt="封面" class="mt-2 max-w-full h-auto rounded-lg" style="max-width: 150px;" />
          </div>
          <div v-if="crawledContent.img_list && crawledContent.img_list.length > 0">
            <div class="flex items-center gap-2">
              <span class="text-gray-500 font-medium">文章图片：</span>
              <button @click="downloadAllImages" class="text-sm text-blue-500 hover:text-blue-700">下载全部图片</button>
            </div>
            <div class="mt-2 grid grid-cols-3 gap-2">
              <div v-for="(img, index) in crawledContent.img_list" :key="index" class="relative group">
                <img :src="img" :alt="'图片' + (index + 1)" class="w-full h-24 object-cover rounded-lg" />
                <button 
                  @click="downloadImage(img, index)"
                  class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          <div>
            <span class="text-gray-500 font-medium">文章内容：</span>
            <div class="mt-2 p-4 bg-gray-50 rounded-lg max-h-96 overflow-y-auto whitespace-pre-wrap text-sm">{{ crawledContent.article_info || '无内容' }}</div>
          </div>
          <div>
            <span class="text-gray-500 font-medium">原文链接：</span>
            <a :href="crawledContent.article_url" target="_blank" class="text-blue-500 hover:underline">{{ crawledContent.article_url }}</a>
          </div>
        </div>
      </div>
      
      <div class="bg-white border border-gray-200 rounded-lg p-4">
        <h4 class="font-semibold text-lg mb-4">AI处理</h4>
        <div class="space-y-4">
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
            <div class="mt-2 p-4 bg-gray-50 rounded-lg max-h-96 overflow-y-auto whitespace-pre-wrap text-sm">{{ generatedContent }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <div 
      v-if="message" 
      :class="messageType === 'success' ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-50 border-red-200 text-red-700'"
      class="border rounded-lg p-3 mt-4"
    >
      {{ message }}
    </div>
    
    <div class="mt-8">
      <h3 class="text-xl font-semibold mb-4">支持的新闻源</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <a 
          v-for="source in newsSources" 
          :key="source.id" 
          :href="source.website" 
          target="_blank"
          class="bg-white border border-gray-200 p-3 rounded-lg hover:bg-blue-50 hover:border-blue-300 hover:text-blue-600 transition-all cursor-pointer shadow-sm"
        >
          <div class="font-medium">{{ source.name }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ source.baseUrl }}</div>
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { simpleNewsSources } from '../utils/constants'

const API_BASE = 'http://localhost:8000/api'

const inputUrl = ref('')
const recognizedInfo = ref(null)
const crawledContent = ref(null)
const message = ref('')
const messageType = ref('success')

const apiList = ref([])
const selectedApiId = ref('')
const isGenerating = ref(false)
const generatedContent = ref('')

const newsSources = simpleNewsSources

async function fetchApiList() {
  try {
    const res = await fetch(`${API_BASE}/api-keys`)
    apiList.value = await res.json()
  } catch (e) {
    console.error('获取API列表失败:', e)
  }
}

function parseUrl(url) {
  const patterns = {
    'news.163.com': { sourceId: 'wangyi', sourceName: '网易新闻', category: '时事热点' },
    'www.163.com': { sourceId: 'wangyi', sourceName: '网易新闻', category: '时事热点' },
    'dy.163.com': { sourceId: 'wangyi', sourceName: '网易新闻', category: '时事热点' },
    '163.com': { sourceId: 'wangyi', sourceName: '网易新闻', category: '时事热点' },
    'sohu.com': { sourceId: 'souhu', sourceName: '搜狐新闻', category: '新闻' },
    'sina.com.cn': { sourceId: 'xinlang', sourceName: '新浪新闻', category: '新闻' },
    'qq.com': { sourceId: 'tengxun', sourceName: '腾讯新闻', category: '新闻' },
    'thepaper.cn': { sourceId: 'pengpai', sourceName: '澎湃新闻', category: '新闻' },
    'ithome.com': { sourceId: 'ithome', sourceName: 'IT之家', category: '科技' },
  }
  
  for (const [pattern, info] of Object.entries(patterns)) {
    if (url.includes(pattern)) {
      return { ...info, success: true }
    }
  }
  
  return { error: '无法识别的新闻源，请输入有效的新闻网站URL', success: false }
}

function showMessage(msg, type = 'success') {
  message.value = msg
  messageType.value = type
}

async function analyzeUrl() {
  message.value = ''
  recognizedInfo.value = null
  crawledContent.value = null
  generatedContent.value = ''
  
  if (!inputUrl.value.trim()) {
    showMessage('请输入URL', 'error')
    return
  }
  
  const result = parseUrl(inputUrl.value.trim())
  
  if (result.error) {
    showMessage(result.error, 'error')
    return
  }
  
  recognizedInfo.value = result
  
  isLoading.value = true
  
  fetch(`${API_BASE}/crawl-url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      url: inputUrl.value.trim()
    })
  })
  .then(res => res.json())
  .then(data => {
    isLoading.value = false
    if (data.success && data.data) {
      crawledContent.value = data.data
    } else {
      showMessage(data.detail || '爬取失败，请重试', 'error')
    }
  })
  .catch(e => {
    isLoading.value = false
    console.error('爬取失败:', e)
    showMessage('爬取失败，请重试', 'error')
  })
}

const isLoading = ref(false)

async function generateContent() {
  if (!selectedApiId.value) {
    showMessage('请选择API', 'error')
    return
  }
  
  if (!crawledContent.value || !crawledContent.value.article_info) {
    showMessage('没有可处理的内容', 'error')
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
        message: crawledContent.value.article_info
      })
    })
    
    const data = await res.json()
    if (data.success) {
      generatedContent.value = data.data
    } else {
      showMessage(data.detail || '生成失败', 'error')
    }
  } catch (e) {
    console.error('生成失败:', e)
    showMessage('生成失败', 'error')
  } finally {
    isGenerating.value = false
  }
}

function downloadImage(url, index) {
  const proxyUrl = `${API_BASE}/download-image?url=${encodeURIComponent(url)}`
  fetch(proxyUrl)
    .then(response => response.blob())
    .then(blob => {
      const blobUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = `image_${index + 1}.jpg`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(blobUrl)
    })
    .catch(e => {
      console.error('下载失败:', e)
      window.open(proxyUrl, '_blank')
    })
}

function downloadAllImages() {
  if (!crawledContent.value || !crawledContent.value.img_list) return
  
  crawledContent.value.img_list.forEach((img, index) => {
    setTimeout(() => {
      downloadImage(img, index)
    }, index * 500)
  })
}

async function pasteUrl() {
  try {
    const text = await navigator.clipboard.readText()
    if (text) {
      inputUrl.value = text
      showMessage('已粘贴URL', 'success')
    }
  } catch (e) {
    console.error('粘贴失败:', e)
    showMessage('粘贴失败，请手动粘贴', 'error')
  }
}

function resetForm() {
  inputUrl.value = ''
  recognizedInfo.value = null
  crawledContent.value = null
  message.value = ''
  generatedContent.value = ''
  selectedApiId.value = ''
}

async function copyGeneratedContent() {
  try {
    await navigator.clipboard.writeText(generatedContent.value)
  } catch (e) {
    console.error('复制失败:', e)
  }
}

onMounted(() => {
  fetchApiList()
})
</script>
