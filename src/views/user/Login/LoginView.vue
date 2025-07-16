<template>
  <div class="min-h-screen w-full flex flex-col lg:flex-row overflow-hidden">
    <!-- 左侧介绍区 -->
    <div class="relative hidden lg:flex flex-col justify-center items-center w-1/2 bg-base-200 text-base-100 p-12 animate-fade-in overflow-hidden">
      <!-- 动态高科技背景 -->
      <div class="cyber-graphic absolute inset-0 pointer-events-none">
        <div class="cyber-circle animate-pulse-slow"></div>
        <div class="cyber-grid"></div>
        <div class="cyber-nodes"></div>
        <div class="pulse-waves"></div>
        <!-- 粒子 -->
        <div 
          v-for="n in 20" :key="n" 
          class="absolute rounded-full opacity-70" 
          :style="generateParticleStyle()"></div>
      </div>
      <h1 class="text-5xl font-extrabold mb-6 z-10 bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent animate-gradient">
        AI-Force 靶场推演智枢
      </h1>
      <p class="text-xl opacity-90 leading-relaxed mb-10 max-w-md text-center z-10 text-white">
        构建真实网络环境，体验攻防对抗，快速提升网络安全技能。
      </p>
      <div class="w-56 h-56 relative z-10 transition-transform duration-300 hover:scale-105">
        <div class="absolute inset-0 rounded-full bg-base-100/10 blur-xl animate-pulse-slow"></div>
        <img :src="logo" alt="Logo" class="relative w-full h-full object-contain" />
      </div>
    </div>

    <!-- 右侧登录区 -->
    <div class="flex-1 flex items-center justify-center bg-base-200">
      <div class="w-full max-w-md p-8 bg-base-100/80 backdrop-blur-md rounded-lg shadow-lg animate-slide-in transition-transform duration-300 hover:-translate-y-1">
        <h2 class="text-3xl font-bold mb-6 text-center">登录</h2>
        <form class="space-y-4" @submit.prevent="submit">
          <input v-model="username" type="text" placeholder="用户名" class="input input-bordered w-full" />
          <input v-model="password" type="password" placeholder="密码" class="input input-bordered w-full" />
          <button class="btn btn-primary w-full transition-transform duration-200 hover:-translate-y-0.5" type="submit">登录</button>
          <p v-if="errorMsg" class="text-error text-sm text-center">{{ errorMsg }}</p>
        </form>
        <p class="text-sm text-base-content/60 mt-4 text-center">默认账号: user / 123456</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../../../stores/app'
import logoSvg from '../../../assets/logo.svg'

const router = useRouter()
const appStore = useAppStore()

const username = ref('')
const password = ref('')
const errorMsg = ref('')

// logo path
const logo = logoSvg

function submit () {
  if (username.value === 'user' && password.value === '123456') {
    appStore.login(username.value)
    router.push('/home')
  } else {
    errorMsg.value = '账号或密码错误'
  }
}

// 生成随机颜色
function getRandomColor () {
  const colors = [
    'var(--primary)',
    'var(--secondary)',
    'var(--accent)'
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}

// 动态生成粒子的 style
function generateParticleStyle () {
  const size = 2 + Math.random() * 4
  const duration = 5 + Math.random() * 10
  const delay = Math.random() * 5
  return `
    width: ${size}px;
    height: ${size}px;
    background-color: ${getRandomColor()};
    left: ${Math.random() * 100}%;
    top: ${Math.random() * 100}%;
    opacity: ${0.3 + Math.random() * 0.5};
    animation: float ${duration}s ease-in-out ${delay}s infinite;
  `
}
</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes slide-in {
  from { opacity: 0; transform: translateX(50px); }
  to { opacity: 1; transform: translateX(0); }
}
@keyframes pulse {
  0% { transform: scale(0.9); opacity: 0.7; }
  50% { opacity: 1; }
  100% { transform: scale(1.1); opacity: 0.7; }
}
@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  25% { transform: translate(10px, -10px); }
  50% { transform: translate(15px, 5px); }
  75% { transform: translate(-10px, 10px); }
}
.animate-fade-in { animation: fade-in 0.8s ease-out forwards; }
.animate-slide-in { animation: slide-in 0.6s ease-out forwards; }
.animate-pulse-slow { animation: pulse 3s infinite; }
</style>
<style scoped>
@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.animate-gradient {
  background-size: 200% 200%;
  animation: gradientShift 6s ease infinite;
}
</style> 