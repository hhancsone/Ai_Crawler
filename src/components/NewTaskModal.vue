<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="$emit('close')">
    <div class="card p-8 w-full max-w-2xl">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold">新建爬取任务</h2>
        <button class="p-2 hover:bg-gray-100 rounded-full" @click="$emit('close')">
          <X :size="20" />
        </button>
      </div>
      <form @submit.prevent="handleSubmit">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium mb-1">任务名称</label>
            <input 
              type="text" 
              v-model="taskForm.name"
              class="w-full p-2 border rounded-lg bg-gray-50" 
              placeholder="给任务起个名字"
            >
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">新闻源</label>
            <select v-model="taskForm.source" class="w-full p-2 border rounded-lg bg-gray-50">
              <option value="">选择新闻源</option>
              <option v-for="src in newsSources" :key="src.id" :value="src.id">{{ src.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">分类 (可多选)</label>
            <div v-if="!taskForm.source" class="p-2 border rounded-lg bg-gray-200 text-gray-400 text-sm">
              请先选择新闻源
            </div>
            <div v-else class="border rounded-lg p-2 max-h-60 overflow-y-auto bg-gray-50">
              <label v-for="cat in categories" :key="cat" class="flex items-center justify-between py-1 cursor-pointer hover:bg-gray-100 px-2">
                <div class="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    :value="cat" 
                    v-model="taskForm.categories"
                    class="rounded"
                  >
                  <span>{{ cat }}</span>
                </div>
                <input 
                  v-if="taskForm.categories.includes(cat)"
                  type="number" 
                  v-model="taskForm.categoryCounts[cat]"
                  class="w-20 p-1 text-sm border rounded"
                  placeholder="数量"
                  min="1"
                  max="100"
                >
              </label>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">爬取频率</label>
            <select v-model="taskForm.rate" class="w-full p-2 border rounded-lg bg-gray-50">
              <option value="fast">快速 (60秒)</option>
              <option value="normal">正常 (180秒)</option>
              <option value="slow">慢速 (300秒)</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">爬取总数量</label>
            <div class="w-full p-2 border rounded-lg bg-gray-100 text-gray-700">
              {{ totalCount }} 篇
            </div>
          </div>
        </div>
        <div class="mt-6 flex justify-end space-x-4">
          <button type="button" class="px-6 py-2 border rounded-lg hover:bg-gray-100" @click="$emit('close')">取消</button>
          <button type="submit" class="btn-primary px-6 py-2 rounded-lg font-semibold">创建并运行</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, computed } from 'vue'
import { X } from 'lucide-vue-next'
import { newsSources as baseNewsSources } from '../utils/constants'

const emit = defineEmits(['close', 'created'])

const tasks = inject('tasks')
const API_BASE = inject('API_BASE')
const showToastMsg = inject('showToastMsg')
const startTaskRefresh = inject('startTaskRefresh')

const newsSources = baseNewsSources.map(s => ({
  ...s,
  file: `${s.id}.py`
}))

const categories = computed(() => {
  const source = newsSources.find(s => s.id === taskForm.value.source)
  return source ? source.categories : ['新闻', '科技', '体育', '国际新闻', '汽车', '游戏', '财经', '娱乐', '教育', '健康', '其他']
})

const taskForm = ref({
  name: '',
  source: '',
  categories: [],
  categoryCounts: {},
  rate: 'normal'
})

const totalCount = computed(() => {
  let total = 0
  for (const cat of taskForm.value.categories) {
    const c = parseInt(taskForm.value.categoryCounts[cat]) || 0
    if (c > 0) {
      total += c
    }
  }
  return total
})

const handleSubmit = async () => {
  if (!taskForm.value.name || !taskForm.value.source) {
    showToastMsg('请填写任务名称和选择新闻源')
    return
  }
  
  if (!taskForm.value.categories || taskForm.value.categories.length === 0) {
    showToastMsg('请选择至少一个分类')
    return
  }
  
  if (totalCount.value <= 0) {
    showToastMsg('请输入爬取数量')
    return
  }
  
  const exists = tasks.value.some(t => t.name === taskForm.value.name)
  if (exists) {
    showToastMsg('任务名称已存在，请使用其他名称')
    return
  }
  
  try {
    const res = await fetch(`${API_BASE}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: taskForm.value.name,
        source: taskForm.value.source,
        categories: taskForm.value.categories,
        categoryCounts: taskForm.value.categoryCounts,
        rate: taskForm.value.rate,
        count: totalCount.value
      })
    })
    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}))
      throw new Error(errorData.message || '请求失败')
    }
    const newTask = await res.json()
    emit('created', newTask)
    if (startTaskRefresh) startTaskRefresh()
    showToastMsg('任务创建成功')
    emit('close')
  } catch (e) {
    console.error('创建任务失败:', e)
    showToastMsg(e.message || '创建任务失败，请重试')
  }
}
</script>
