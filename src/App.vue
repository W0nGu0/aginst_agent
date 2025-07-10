<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useAppStore } from './stores/app'
import { computed } from 'vue'

const appStore = useAppStore()
const theme = computed(() => appStore.currentTheme)

function toggleTheme() {
  appStore.toggleTheme()
}
</script>

<template>
  <div class="app min-h-screen bg-base-200" :data-theme="theme">
    <!-- 导航栏 -->
    <nav class="fixed top-0 w-full z-50 backdrop-blur-md bg-base-100/80 border-b border-white/10">
      <div class="container mx-auto px-4">
        <div class="flex justify-between items-center h-16">
          <!-- Logo位置 -->
          <div class="flex items-center">
            <div class="w-10 h-10 rounded-lg bg-gradient-to-r from-primary to-secondary flex items-center justify-center shadow-glow-sm">
              <span class="text-base-100 font-bold text-xl">AI</span>
            </div>
            <span class="ml-2 text-xl font-bold text-gradient">攻防靶场</span>
          </div>
          
          <!-- 导航链接 -->
          <div class="hidden md:flex space-x-8">
            <RouterLink 
              to="/" 
              class="text-base-content/70 hover:text-primary font-medium transition-colors"
              active-class="text-primary border-b-2 border-primary/70">
              首页
            </RouterLink>
            <RouterLink 
              to="/scene-detail" 
              class="text-base-content/70 hover:text-primary font-medium transition-colors"
              active-class="text-primary border-b-2 border-primary/70">
              场景库
            </RouterLink>
            <RouterLink 
              to="/topology" 
              class="text-base-content/70 hover:text-primary font-medium transition-colors"
              active-class="text-primary border-b-2 border-primary/70">
              靶场实验
            </RouterLink>
            <a href="#" class="text-base-content/70 hover:text-primary font-medium transition-colors">推演记录</a>
            <a href="#" class="text-base-content/70 hover:text-primary font-medium transition-colors">知识库</a>
          </div>
          
          <!-- 用户头像 -->
          <div class="flex items-center space-x-4">
            <button @click="toggleTheme" class="btn btn-circle btn-sm btn-ghost hover:bg-primary/10">
              <svg v-if="theme === 'light'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </button>
            
            <div class="w-10 h-10 rounded-full bg-gradient-to-r from-secondary to-accent flex items-center justify-center shadow-md">
              <span class="text-base-100 font-bold">U</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- 主要内容 -->
    <main class="container mx-auto px-4 pt-24 pb-16">
      <RouterView v-slot="{ Component }">
        <Transition name="fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>
    
    <!-- 页脚装饰 -->
    <footer class="w-full h-1 bg-gradient-to-r from-transparent via-primary/30 to-transparent"></footer>
  </div>
</template>

<style>
@import './assets/main.css';

:root {
  --primary-rgb: 74, 158, 255;
  --primary: #4a9eff;
  --primary-light: #6eb2ff;
  --secondary: #7b68ee;
  --accent: #06b6d4; /* cyan-500 */
}

[data-theme="night"] {
  --primary-rgb: 74, 158, 255;
  --primary: #4a9eff;
  --primary-light: #6eb2ff;
  --secondary: #7b68ee;
  --accent: #06b6d4; /* cyan-500 */
}

[data-theme="light"] {
  --primary-rgb: 74, 158, 255;
  --primary: #3f83d5;
  --primary-light: #4a9eff;
  --secondary: #6a58d9;
  --accent: #2dd4bf; /* teal-400 */
}

html, body {
  min-height: 100vh;
  scroll-behavior: smooth;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
