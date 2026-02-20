import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

import Dashboard from './views/Dashboard.vue'
import Tasks from './views/Tasks.vue'
import Results from './views/Results.vue'
import Rules from './views/Rules.vue'
import Schedule from './views/Schedule.vue'
import Help from './views/Help.vue'

const routes = [
  { path: '/', name: 'dashboard', component: Dashboard },
  { path: '/tasks', name: 'tasks', component: Tasks },
  { path: '/results', name: 'results', component: Results },
  { path: '/rules', name: 'rules', component: Rules },
  { path: '/schedule', name: 'schedule', component: Schedule },
  { path: '/help', name: 'help', component: Help },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const app = createApp(App)
app.use(router)
app.mount('#app')
