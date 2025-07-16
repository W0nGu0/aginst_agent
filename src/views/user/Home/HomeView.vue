<template>
  <div class="home-view w-full overflow-hidden">
    <!-- Hero Section -->
    <section class="relative cyber-bg overflow-hidden py-20 px-6 md:px-12 lg:px-32 flex flex-col md:flex-row items-center gap-12">
      <!-- 动态背景图形 -->
      <div class="cyber-graphic absolute inset-0 pointer-events-none">
        <div class="cyber-circle animate-pulse-slow"></div>
        <div class="cyber-grid"></div>
        <div class="cyber-nodes"></div>
        <div class="pulse-waves"></div>
      </div>

      <!-- 左侧文字 -->
      <div class="flex-1 z-10 text-center md:text-left" data-aos="fade-right">
        <h1 class="text-gradient text-4xl md:text-6xl font-extrabold mb-6 animate-gradient leading-snug">
          AI 驱动的攻防推演平台
        </h1>
        <p class="text-base-content/80 text-lg md:text-xl mb-10 max-w-2xl">
          集成智能推荐、可视化网络拓扑与实时演练，帮助安全从业者迅速构建并体验逼真的攻防场景。
        </p>
        <div class="flex flex-col sm:flex-row justify-center md:justify-start gap-4">
          <RouterLink to="/against" class="btn btn-primary btn-lg shadow-lg transition-transform duration-200 hover:-translate-y-1">立即创建动态靶场</RouterLink>
          <RouterLink to="/history" class="btn btn-outline btn-lg transition-transform duration-200 hover:-translate-y-1">查看推演记录</RouterLink>
        </div>
      </div>

      <!-- 右侧示意卡片 -->
      <div class="flex-1 z-10 hidden md:block" data-aos="fade-left">
        <div class="glass-panel p-6 rounded-2xl shadow-2xl transform hover:scale-105 transition-transform duration-300">
          <h3 class="text-2xl font-semibold mb-4 text-primary text-center">平台特色</h3>
          <ul class="space-y-2 text-base-content/70">
            <li>• 场景一键生成、大模型语义解析</li>
            <li>• 深度强化学习驱动的攻防agent体系、Agent 智能协同</li>
            <li>• 实时指标监控</li>
            <li>• 全域量化指标</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Feature Cards -->
    <section class="py-16 px-6 md:px-12 lg:px-32">
      <h2 class="text-center text-3xl font-bold mb-12 text-gradient animate-gradient">核心能力</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
        <div class="glass-panel p-8 text-center transition-transform duration-300 hover:-translate-y-2">
          <h3 class="text-xl font-semibold mb-2">智能场景生成</h3>
          <p class="text-base-content/70">基于自然语言描述，一键生成个性化攻防场景。</p>
        </div>
        <div class="glass-panel p-8 text-center transition-transform duration-300 hover:-translate-y-2">
          <h3 class="text-xl font-semibold mb-2">可视化拓扑设计</h3>
          <p class="text-base-content/70">拖拽式网络拓扑编辑器，快速搭建复杂网络环境。</p>
        </div>
        <div class="glass-panel p-8 text-center transition-transform duration-300 hover:-translate-y-2">
          <h3 class="text-xl font-semibold mb-2">实时演练与记录</h3>
          <p class="text-base-content/70">实时监控攻防过程，自动生成推演报告。</p>
        </div>
      </div>
    </section>

    <!-- Metrics Section -->
    <section class="py-16 px-6 md:px-12 lg:px-32 bg-base-300/30 backdrop-blur-sm">
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-6 text-center">
        <div>
          <span class="text-4xl font-bold text-primary">30+</span>
          <p class="text-base-content/60 mt-2">预置攻防场景</p>
        </div>
        <div>
          <span class="text-4xl font-bold text-secondary">50+</span>
          <p class="text-base-content/60 mt-2">智能Agent工具</p>
        </div>
        <div>
          <span class="text-4xl font-bold text-accent">99.9%</span>
          <p class="text-base-content/60 mt-2">运行稳定性</p>
        </div>
        <div>
          <span class="text-4xl font-bold text-primary">24/7</span>
          <p class="text-base-content/60 mt-2">实时监控</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.animate-gradient {
  background-size: 200% 200%;
  animation: gradientShift 8s ease infinite;
}
</style> 