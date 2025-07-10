import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/scene-detail',
      name: 'sceneDetail',
      component: () => import('../views/SceneDetailView.vue')
    },
    {
      path: '/topology',
      name: 'topology',
      component: () => import('../views/TopologyView.vue')
    }
  ]
})

export default router 