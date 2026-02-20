<template>
  <div>
    <h2 class="text-3xl font-bold mb-8">帮助中心</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
      <div class="card p-6">
        <div class="flex items-center space-x-3 mb-4">
          <div class="p-2 bg-blue-100 rounded-lg">
            <Zap class="text-blue-600" :size="24" />
          </div>
          <h3 class="text-xl font-semibold">快速爬取</h3>
        </div>
        <p class="text-gray-500">输入任意新闻URL，快速识别新闻源并爬取内容，支持多种主流新闻网站。</p>
      </div>
      
      <div class="card p-6">
        <div class="flex items-center space-x-3 mb-4">
          <div class="p-2 bg-green-100 rounded-lg">
            <Brain class="text-green-600" :size="24" />
          </div>
          <h3 class="text-xl font-semibold">AI智能处理</h3>
        </div>
        <p class="text-gray-500">选择AI模型对爬取的内容进行二次处理，生成摘要、翻译、润色等。</p>
      </div>
      
      <div class="card p-6">
        <div class="flex items-center space-x-3 mb-4">
          <div class="p-2 bg-purple-100 rounded-lg">
            <Clock class="text-purple-600" :size="24" />
          </div>
          <h3 class="text-xl font-semibold">定时任务</h3>
        </div>
        <p class="text-gray-500">创建定时爬取任务，设定执行时间和周期，自动采集目标网站内容。</p>
      </div>
      
      <div class="card p-6">
        <div class="flex items-center space-x-3 mb-4">
          <div class="p-2 bg-orange-100 rounded-lg">
            <Download class="text-orange-600" :size="24" />
          </div>
          <h3 class="text-xl font-semibold">数据导出</h3>
        </div>
        <p class="text-gray-500">支持将爬取的结果导出为CSV格式，方便后续分析和处理。</p>
      </div>
    </div>
    
    <div class="card p-6 mb-8">
      <h3 class="text-xl font-semibold mb-6">支持的任务类型</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="task in taskTypes" :key="task.name" class="text-center p-4 border rounded-lg">
          <div class="font-medium">{{ task.name }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ task.desc }}</div>
        </div>
      </div>
    </div>
    
    <div class="card p-6 mb-8">
      <h3 class="text-xl font-semibold mb-6">支持的新闻源</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="source in newsSources" :key="source.name" class="p-4 border rounded-lg hover:bg-gray-50">
          <div class="font-medium">{{ source.name }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ source.category }}</div>
        </div>
      </div>
    </div>
    
    <div class="card p-6 mb-8">
      <h3 class="text-xl font-semibold mb-4">常见问题</h3>
      <div class="space-y-6">
        <div>
          <h4 class="font-semibold text-lg mb-2">如何创建爬取任务？</h4>
          <p class="text-gray-500">1. 在左侧导航点击"任务管理"<br/>2. 点击"新建任务"按钮<br/>3. 填写任务名称、选择新闻源、设置爬取URL<br/>4. 选择任务类型（一次性/定时）<br/>5. 点击"创建并运行"即可</p>
        </div>
        
        <div>
          <h4 class="font-semibold text-lg mb-2">如何使用快速爬取功能？</h4>
          <p class="text-gray-500">1. 在左侧导航点击"快速爬取"<br/>2. 输入或粘贴新闻URL<br/>3. 点击"识别URL"自动识别新闻源<br/>4. 系统会自动爬取内容并显示在左侧<br/>5. 在右侧选择AI模型进行处理</p>
        </div>
        
        <div>
          <h4 class="font-semibold text-lg mb-2">如何配置API密钥？</h4>
          <p class="text-gray-500">1. 在左侧导航点击"API管理"<br/>2. 点击"新增API"按钮<br/>3. 填写API名称、选择API类型（如OpenAI）<br/>4. 输入API Key和可选的Base URL<br/>5. 选择默认模型<br/>6. 保存即可使用</p>
        </div>
        
        <div>
          <h4 class="font-semibold text-lg mb-2">如何导出爬取的数据？</h4>
          <p class="text-gray-500">1. 在左侧导航点击"结果管理"<br/>2. 可以通过筛选器选择特定任务或新闻源的数据<br/>3. 点击"导出数据"按钮<br/>4. 数据将下载为CSV文件</p>
        </div>
        
        <div>
          <h4 class="font-semibold text-lg mb-2">支持哪些AI模型？</h4>
          <p class="text-gray-500">系统支持多种AI模型，包括：<br/>- OpenAI (GPT-4, GPT-3.5 Turbo)<br/>- Claude (Anthropic)<br/>- 通义千问 (阿里云)<br/>- 智谱清言<br/>- MiniMax<br/>- 任何兼容OpenAI API格式的模型</p>
        </div>
        
        <div>
          <h4 class="font-semibold text-lg mb-2">定时任务不执行怎么办？</h4>
          <p class="text-gray-500">1. 检查后端服务是否运行<br/>2. 确认定时任务已启用<br/>3. 检查任务的时间设置是否正确<br/>4. 查看后端日志排查错误</p>
        </div>
      </div>
    </div>
    
    <div class="card p-6">
      <h3 class="text-xl font-semibold mb-4">使用技巧</h3>
      <div class="space-y-4">
        <div class="flex items-start space-x-3">
          <Lightbulb class="text-yellow-500 flex-shrink-0 mt-1" :size="20" />
          <div>
            <h4 class="font-semibold">使用粘贴功能</h4>
            <p class="text-gray-500 text-sm">在快速爬取页面，可以直接点击"粘贴"按钮读取剪贴板中的URL，省去手动输入的麻烦。</p>
          </div>
        </div>
        
        <div class="flex items-start space-x-3">
          <Lightbulb class="text-yellow-500 flex-shrink-0 mt-1" :size="20" />
          <div>
            <h4 class="font-semibold">批量处理内容</h4>
            <p class="text-gray-500 text-sm">在结果管理页面，可以选择多个结果进行批量导出或删除操作。</p>
          </div>
        </div>
        
        <div class="flex items-start space-x-3">
          <Lightbulb class="text-yellow-500 flex-shrink-0 mt-1" :size="20" />
          <div>
            <h4 class="font-semibold">利用AI生成摘要</h4>
            <p class="text-gray-500 text-sm">爬取长篇文章后，可以使用AI模型生成简洁的摘要，节省阅读时间。</p>
          </div>
        </div>
        
        <div class="flex items-start space-x-3">
          <Lightbulb class="text-yellow-500 flex-shrink-0 mt-1" :size="20" />
          <div>
            <h4 class="font-semibold">设置分类标签</h4>
            <p class="text-gray-500 text-sm">创建任务时可以设置分类标签，便于后续筛选和管理爬取结果。</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Zap, Brain, Clock, Download, Lightbulb } from 'lucide-vue-next'

const taskTypes = [
  { name: '即时任务', desc: '立即执行一次' },
  { name: '定时任务', desc: '按设定时间执行' },
  { name: '周期任务', desc: '按周期循环执行' },
]

const newsSources = [
  { name: '网易新闻', category: '时事、科技、娱乐' },
  { name: '搜狐新闻', category: '新闻、财经、娱乐' },
  { name: '新浪新闻', category: '国际、国内、科技' },
  { name: '腾讯新闻', category: '新闻、科技、体育' },
  { name: '澎湃新闻', category: '时政、深度报道' },
  { name: 'IT之家', category: '科技、数码' },
  { name: '环球网', category: '国际、军事' },
  { name: '中国日报', category: '时政、国际' },
]
</script>
