<template>
  <div>
    <div class="flex justify-between items-center mb-8">
      <h2 class="text-3xl font-bold">仪表盘</h2>
      <button class="btn-primary px-6 py-2 rounded-lg font-semibold flex items-center space-x-2" @click="openTaskModal">
        <Plus :size="20" />
        <span>新建任务</span>
      </button>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500">总任务数</p>
            <p class="text-3xl font-bold">{{ tasks.length }}</p>
          </div>
          <ListChecks class="w-12 h-12 text-indigo-600" />
        </div>
      </div>
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500">运行中</p>
            <p class="text-3xl font-bold">{{ runningTasks }}</p>
          </div>
          <Play class="w-12 h-12 text-green-500" />
        </div>
      </div>
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500">已完成</p>
            <p class="text-3xl font-bold">{{ completedTasks }}</p>
          </div>
          <CheckCircle class="w-12 h-12 text-blue-500" />
        </div>
      </div>
      <div class="card p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-500">数据量</p>
            <p class="text-3xl font-bold">{{ stats.total }}</p>
          </div>
          <Database class="w-12 h-12 text-yellow-500" />
        </div>
      </div>
    </div>
    <h3 class="text-xl font-semibold mb-4">最近任务</h3>
    <div class="space-y-4">
      <div v-for="task in recentTasks" :key="task.id" class="card p-6">
        <div class="flex justify-between items-center">
          <div>
            <div class="flex items-center space-x-2 mb-1">
              <h4 class="font-semibold">{{ task.name }}</h4>
              <span v-if="task.sourceName || task.source" class="px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full text-xs">{{ task.sourceName || task.source }}</span>
              <span v-if="task.category" class="px-2 py-0.5 bg-gray-100 rounded-full text-xs">{{ task.category }}</span>
            </div>
          </div>
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
        </div>
        <div class="mt-4 flex justify-between items-center">
          <span class="text-sm text-gray-500">{{ formatDate(task.createdAt) }}</span>
          <span class="text-sm font-semibold">{{ task.dataCount }} 条数据</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, inject, ref, onMounted } from 'vue'
import { Plus, ListChecks, Play, CheckCircle, Database } from 'lucide-vue-next'

const tasks = inject('tasks')
const results = inject('results')
const openTaskModal = inject('openTaskModal')
const fetchStats = inject('fetchStats')

const stats = ref({ total: 0, bySource: {}, recent24h: 0, tasks: 0, runningTasks: 0 })

const runningTasks = computed(() => tasks.value.filter(t => t.status === 'running').length)
const completedTasks = computed(() => tasks.value.filter(t => t.status === 'completed').length)
const recentTasks = computed(() => tasks.value.slice(-3).reverse())

const formatDate = (date) => {
  return new Date(date).toLocaleString()
}

onMounted(async () => {
  stats.value = await fetchStats()
})
</script>
