import './assets/main.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

const app = createApp(App)
if (import.meta.env.PROD) { // 生产环境判断
  app.config.devtools = false
}
app.use(createPinia())
app.use(router)
app.mount('#app')
