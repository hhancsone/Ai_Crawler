<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <h2 class="text-3xl font-bold">任务管理</h2>
      <button class="btn-primary px-6 py-2 rounded-lg font-semibold flex items-center space-x-2" @click="openTaskModal">
        <Plus :size="20" />
        <span>新建任务</span>
      </button>
    </div>
    <div class="card p-6">
      <div class="flex justify-between items-center mb-4">
        <div class="flex items-center space-x-4">
          <input 
            type="text" 
            v-model="searchTerm"
            class="p-2 border rounded-lg bg-gray-50" 
            placeholder="搜索任务..."
          >
          <select v-model="sourceFilter" class="p-2 border rounded-lg bg-gray-50">
            <option value="all">全部新闻源</option>
            <option v-for="src in newsSources" :key="src.id" :value="src.id">{{ src.name }}</option>
          </select>
          <select v-model="categoryFilter" :disabled="sourceFilter === 'all'" :class="sourceFilter === 'all' ? 'p-2 border rounded-lg bg-gray-200 text-gray-400 cursor-not-allowed' : 'p-2 border rounded-lg bg-gray-50'" style="max-height: 300px; overflow-y: auto;">
            <option value="all">全部分类</option>
            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
          <select v-model="statusFilter" class="p-2 border rounded-lg bg-gray-50">
            <option value="all">全部状态</option>
            <option value="running">运行中</option>
            <option value="completed">已完成</option>
            <option value="failed">失败</option>
          </select>
        </div>
      </div>
      <table class="w-full text-left">
        <thead>
          <tr class="border-b">
            <th class="p-2">任务名称</th>
            <th class="p-2">新闻源</th>
            <th class="p-2">分类</th>
            <th class="p-2">状态</th>
            <th class="p-2">创建时间</th>
            <th class="p-2">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in filteredTasks" :key="task.id" class="border-b">
            <td class="p-2">{{ task.name }}</td>
            <td class="p-2">
              <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">{{ task.sourceName || task.source || '未选择' }}</span>
            </td>
            <td class="p-2">
              <span class="px-2 py-1 bg-gray-100 rounded-full text-xs">{{ task.categories?.join(', ') || '未分类' }}</span>
            </td>
            <td class="p-2">
              <span 
                class="px-2 py-1 rounded-full text-xs font-semibold"
                :class="{
                  'bg-green-100 text-green-800': task.status === 'running',
                  'bg-blue-100 text-blue-800': task.status === 'completed',
                  'bg-red-100 text-red-800': task.status === 'failed'
                }"
              >
                {{ task.status === 'running' ? '运行中' : task.status === 'completed' ? '已完成' : '失败' }}
              </span>
            </td>
            <td class="p-2">{{ formatDate(task.createdAt) }}</td>
            <td class="p-2 space-x-2">
              <button class="p-1 text-indigo-600 hover:bg-gray-100 rounded" @click="viewTaskLogs(task.id)">
                <FileText :size="18" />
              </button>
              <button class="p-1 text-green-500 hover:bg-gray-100 rounded" @click="runTask(task.id)">
                <Play :size="18" />
              </button>
              <button class="p-1 text-red-500 hover:bg-gray-100 rounded" @click="deleteTask(task.id)">
                <Trash2 :size="18" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import { Plus, FileText, Play, Trash2 } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { simpleNewsSources, defaultCategories } from '../utils/constants'
import { formatDate } from '../utils/formatDate'

const router = useRouter()

const tasks = inject('tasks')
const openTaskModal = inject('openTaskModal')
const showToastMsg = inject('showToastMsg')
const handleTaskDeleted = inject('handleTaskDeleted')
const startTaskRefresh = inject('startTaskRefresh')
const API_BASE = inject('API_BASE')
const fetchTasks = inject('fetchTasks')

const searchTerm = ref('')
const statusFilter = ref('all')
const categoryFilter = ref('all')
const sourceFilter = ref('all')

const newsSources = simpleNewsSources

const categories = computed(() => {
  if (sourceFilter.value === 'all') {
    return defaultCategories
  }
  const source = newsSources.find(s => s.id === sourceFilter.value)
  return source ? source.categories : []
})

const filteredTasks = computed(() => {
  return tasks.value.filter(task => {
    const selectedSource = newsSources.find(s => s.id === sourceFilter.value)
    const sourceName = selectedSource ? selectedSource.name : null
    const matchesSearch = task.name.toLowerCase().includes(searchTerm.value.toLowerCase())
    const matchesStatus = statusFilter.value === 'all' || task.status === statusFilter.value
    const matchesCategory = categoryFilter.value === 'all' || (task.categories && task.categories.includes(categoryFilter.value))
    const matchesSource = sourceFilter.value === 'all' || task.source === sourceFilter.value || task.source === sourceName
    return matchesSearch && matchesStatus && matchesCategory && matchesSource
  })
})

const viewTaskLogs = (taskId) => {
  const task = tasks.value.find(t => t.id === taskId)
  if (task) {
    router.push({ path: '/results', query: { source: task.source } })
  }
}

const runTask = async (taskId) => {
  try {
    await fetch(`${API_BASE}/tasks/${taskId}/run`, { method: 'POST' })
    const task = tasks.value.find(t => t.id === taskId)
    if (task) {
      task.status = 'running'
    }
    if (startTaskRefresh) startTaskRefresh()
    showToastMsg(`任务已开始运行`)
  } catch (e) {
    showToastMsg('启动任务失败')
  }
}

const deleteTask = async (taskId) => {
  if (confirm('确定要删除此任务吗？')) {
    try {
      await fetch(`${API_BASE}/tasks/${taskId}`, { method: 'DELETE' })
      handleTaskDeleted(taskId)
    } catch (e) {
      showToastMsg('删除任务失败')
    }
  }
}
</script>
