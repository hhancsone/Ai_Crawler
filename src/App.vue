<template>
  <div class="flex h-screen">
    <Sidebar />
    <main class="flex-1 p-8 overflow-y-auto bg-gray-50">
      <router-view />
    </main>
    <NewTaskModal v-if="showTaskModal" @close="showTaskModal = false" @created="handleTaskCreated" />
    <Toast :message="toastMessage" :show="showToast" @hide="showToast = false" />
  </div>
</template>

<script setup>
import { ref, provide, onMounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import NewTaskModal from './components/NewTaskModal.vue'
import Toast from './components/Toast.vue'

const showTaskModal = ref(false)
const showToast = ref(false)
const toastMessage = ref('')

const tasks = ref([])
const results = ref([])
let taskRefreshInterval = null

const API_BASE = 'http://localhost:8000/api'

const fetchTasks = async () => {
  try {
    const res = await fetch(`${API_BASE}/tasks`)
    const data = await res.json()
    tasks.value = data
    const hasRunning = data.some(t => t.status === 'running')
    if (!hasRunning && taskRefreshInterval) {
      clearInterval(taskRefreshInterval)
      taskRefreshInterval = null
    }
  } catch (e) {
    console.error('获取任务失败:', e)
  }
}

const startTaskRefresh = () => {
  if (taskRefreshInterval) return
  fetchTasks()
  taskRefreshInterval = setInterval(fetchTasks, 2000)
}

const fetchResults = async () => {
  try {
    const res = await fetch(`${API_BASE}/results?limit=100`)
    const data = await res.json()
    results.value = data
  } catch (e) {
    console.error('获取结果失败:', e)
  }
}

const fetchStats = async () => {
  try {
    const res = await fetch(`${API_BASE}/stats`)
    return await res.json()
  } catch (e) {
    console.error('获取统计失败:', e)
    return { total: 0, bySource: {}, recent24h: 0, tasks: 0, runningTasks: 0 }
  }
}

const showToastMsg = (message) => {
  toastMessage.value = message
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

const openTaskModal = () => {
  showTaskModal.value = true
}

const handleTaskCreated = (task) => {
  tasks.value.push(task)
  showToastMsg('任务创建成功！')
}

const handleTaskDeleted = (taskId) => {
  tasks.value = tasks.value.filter(t => t.id !== taskId)
  results.value = results.value.filter(r => r.taskId !== taskId)
  showToastMsg('任务已删除')
}

const handleResultDeleted = (resultId) => {
  results.value = results.value.filter(r => r.id !== resultId)
  showToastMsg('结果已删除')
}

provide('tasks', tasks)
provide('results', results)
provide('showToastMsg', showToastMsg)
provide('openTaskModal', openTaskModal)
provide('handleTaskDeleted', handleTaskDeleted)
provide('handleTaskCreated', () => { startTaskRefresh() })
provide('handleResultDeleted', handleResultDeleted)
provide('fetchTasks', fetchTasks)
provide('fetchResults', fetchResults)
provide('fetchStats', fetchStats)
provide('API_BASE', API_BASE)
provide('startTaskRefresh', startTaskRefresh)

onMounted(() => {
  fetchTasks()
  fetchResults()
})
</script>
