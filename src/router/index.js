import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'login',
      component: () => import('../views/user/Login/LoginView.vue')
    },
    {
      path: '/login',
      redirect: '/' // 兼容旧链接
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/user/Login/RegisterView.vue')
    },
    {
      path: '/forgot',
      name: 'forgot',
      component: () => import('../views/user/Login/ForgotPasswordView.vue')
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('../views/user/Home/HomeView.vue')
    },
    {
      path: '/user',
      redirect: '/home'
    },
    {
      path: '/against',
      name: 'against',
      component: () => import('../views/user/Against/Create.vue')
    },
    {
      path: '/topology',
      name: 'topology',
      component: () => import('../views/user/Against/Topology/TopologyView.vue')
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('../views/user/History/HistoryView.vue')
    },
    {
      path: '/history/:id',
      name: 'historyDetail',
      component: () => import('../views/user/History/HistoryDetailView.vue')
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/user/Agent_setting/AgentSettingsView.vue')
    },
    {
      path: '/personal',
      name: 'personal',
      component: () => import('../views/user/Personal/PersonalView.vue')
    },
    {
      path: '/performance',
      name: 'performance',
      component: () => import('../views/user/Agent_performance/performance.vue')
    }
  ]
})

export default router 