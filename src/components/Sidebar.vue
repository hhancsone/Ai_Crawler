<template>
  <aside class="w-64 flex-shrink-0 p-6 bg-white">
    <div class="flex items-center space-x-2 mb-8">
      <Bug class="text-indigo-600" :size="24" />
      <h1 class="text-2xl font-bold">EasyCrawler</h1>
    </div>
    <nav class="space-y-2">
      <router-link 
        to="/" 
        class="flex items-center space-x-2 p-2 rounded-lg"
        :class="$route.path === '/' ? 'bg-gray-100' : 'hover:bg-gray-100'"
      >
        <LayoutDashboard :size="20" />
        <span>仪表盘</span>
      </router-link>
      <router-link 
        to="/schedule" 
        class="flex items-center space-x-2 p-2 rounded-lg"
        :class="$route.path === '/schedule' ? 'bg-gray-100' : 'hover:bg-gray-100'"
      >
        <CalendarClock :size="20" />
        <span>快速爬取</span>
      </router-link>
      <router-link 
        to="/rules" 
        class="flex items-center space-x-2 p-2 rounded-lg"
        :class="$route.path === '/rules' ? 'bg-gray-100' : 'hover:bg-gray-100'"
      >
        <Code :size="20" />
        <span>API管理</span>
      </router-link>
      <router-link 
        to="/tasks" 
        class="flex items-center space-x-2 p-2 rounded-lg"
        :class="$route.path === '/tasks' ? 'bg-gray-100' : 'hover:bg-gray-100'"
      >
        <ListChecks :size="20" />
        <span>任务管理</span>
      </router-link>
      <router-link 
        to="/results" 
        class="flex items-center space-x-2 p-2 rounded-lg"
        :class="$route.path === '/results' ? 'bg-gray-100' : 'hover:bg-gray-100'"
      >
        <FileText :size="20" />
        <span>结果管理</span>
      </router-link>
      <router-link 
        to="/help" 
        class="flex items-center space-x-2 p-2 rounded-lg"
        :class="$route.path === '/help' ? 'bg-gray-100' : 'hover:bg-gray-100'"
      >
        <HelpCircle :size="20" />
        <span>帮助中心</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup>
import { Bug, LayoutDashboard, CalendarClock, Code, ListChecks, FileText, HelpCircle } from 'lucide-vue-next'
</script>
