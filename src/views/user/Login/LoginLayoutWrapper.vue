<template>
  <div class="min-h-screen w-full flex flex-col lg:flex-row overflow-hidden">
    <!-- 左侧介绍与动画，与 LoginView 相同 -->
    <div class="relative hidden lg:flex flex-col justify-center items-center w-1/2 cyber-bg text-base-100 p-12 animate-fade-in overflow-hidden">
      <div class="cyber-graphic absolute inset-0 pointer-events-none">
        <div class="cyber-circle animate-pulse-slow"></div>
        <div class="cyber-grid"></div>
        <div class="cyber-nodes"></div>
        <div class="pulse-waves"></div>
        <div v-for="n in 20" :key="n" class="absolute rounded-full opacity-70" :style="generateParticleStyle()"></div>
      </div>
      <h1 class="text-5xl font-extrabold mb-6 z-10 bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent animate-gradient">AI-Force 靶场推演智枢</h1>
      <p class="text-xl leading-relaxed mb-10 max-w-md text-center z-10 text-white">构建真实网络环境，体验攻防对抗，快速提升网络安全技能。</p>
      <div class="w-56 h-56 relative z-10 transition-transform duration-300 hover:scale-105">
        <div class="absolute inset-0 rounded-full bg-base-100/10 blur-xl animate-pulse-slow"></div>
        <img src="../../../assets/logo.svg" alt="Logo" class="relative w-full h-full object-contain" />
      </div>
    </div>

    <!-- 右侧表单插槽 -->
    <div class="flex-1 flex items-center justify-center bg-base-200">
      <div class="w-full max-w-md p-8 bg-base-100/80 backdrop-blur-md rounded-lg shadow-lg animate-slide-in transition-transform duration-300 hover:-translate-y-1">
        <h2 class="text-3xl font-bold mb-6 text-center">{{ title }}</h2>
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'

function getRandomColor() {
  const colors = [
    'var(--primary)',
    'var(--secondary)',
    'var(--accent)'
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}
function generateParticleStyle() {
  const size = 2 + Math.random() * 4
  const duration = 5 + Math.random() * 10
  const delay = Math.random() * 5
  return `width:${size}px;height:${size}px;background-color:${getRandomColor()};left:${Math.random()*100}%;top:${Math.random()*100}%;opacity:${0.3+Math.random()*0.5};animation: float ${duration}s ease-in-out ${delay}s infinite;`
}

defineProps({ title: String })
</script> 