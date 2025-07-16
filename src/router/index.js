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
      path: '/home',
      name: 'home',
      component: () => import('../views/user/Home/HomeView.vue')
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
      path: '/settings',
      name: 'settings',
      component: () => import('../views/user/Tool/ToolView.vue')
    },
    {
      path: '/personal',
      name: 'personal',
      component: () => import('../views/user/Personal/PersonalView.vue')
    }
  ]
})

export default router 