<template>
  <div class="h-screen w-screen flex flex-col lg:flex-row">
    <!-- 左侧介绍区 -->
    <div class="hidden lg:flex flex-col justify-center items-center w-1/2 bg-gradient-to-br from-primary to-secondary text-base-100 p-12 animate-fade-in">
      <h1 class="text-5xl font-extrabold mb-6">AI-Force 靶场推演智枢</h1>
      <p class="text-xl opacity-90 leading-relaxed mb-10 max-w-md text-center">
        构建真实网络环境，体验攻防对抗，快速提升网络安全技能。
      </p>
      <div class="w-56 h-56 relative">
        <div class="absolute inset-0 rounded-full bg-base-100/10 blur-xl animate-pulse-slow"></div>
        <img :src="logo" alt="Logo" class="relative w-full h-full object-contain" />
      </div>
    </div>

    <!-- 右侧登录区 -->
    <div class="flex-1 flex items-center justify-center bg-base-200">
      <div class="w-full max-w-md p-8 bg-base-100 rounded-lg shadow-lg animate-slide-in">
        <h2 class="text-3xl font-bold mb-6 text-center">登录到平台</h2>
        <form class="space-y-4" @submit.prevent="submit">
          <input v-model="username" type="text" placeholder="用户名" class="input input-bordered w-full" />
          <input v-model="password" type="password" placeholder="密码" class="input input-bordered w-full" />
          <button class="btn btn-primary w-full" type="submit">登录</button>
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
.animate-fade-in { animation: fade-in 0.8s ease-out forwards; }
.animate-slide-in { animation: slide-in 0.6s ease-out forwards; }
.animate-pulse-slow { animation: pulse 3s infinite; }
</style> 