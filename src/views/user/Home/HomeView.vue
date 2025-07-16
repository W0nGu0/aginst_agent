<template>
  <div class="home-view w-full py-16 px-6 md:px-12 lg:px-24 grid gap-14 md:grid-cols-2 items-start">
    <!-- 标题 & 按钮区域 -->
    <div class="text-center md:text-left">
      <h1 class="text-4xl md:text-5xl font-extrabold mb-6 text-gradient leading-tight">
        AI 驱动的攻防推演平台
      </h1>
      <p class="text-base-content/80 text-lg mb-10">
        我们的平台集成 AI 智能推荐、可视化网络拓扑与实时攻防演练，帮助安全从业者快速构建并体验真实的攻防场景。
      </p>
      <div class="flex flex-col sm:flex-row justify-center md:justify-start gap-4">
        <RouterLink to="/against" class="btn btn-primary btn-lg shadow-lg">立即创建动态靶场</RouterLink>
        <RouterLink to="/history" class="btn btn-outline btn-lg">查看推演记录</RouterLink>
      </div>
    </div>

    <!-- 功能卡片区域 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div class="glass-panel p-6">
        <h3 class="text-xl font-semibold mb-2">智能场景生成</h3>
        <p class="text-base-content/70">基于自然语言描述，一键生成个性化攻防场景。</p>
      </div>
      <div class="glass-panel p-6">
        <h3 class="text-xl font-semibold mb-2">可视化拓扑设计</h3>
        <p class="text-base-content/70">拖拽式网络拓扑编辑器，快速搭建复杂网络环境。</p>
      </div>
      <div class="glass-panel p-6">
        <h3 class="text-xl font-semibold mb-2">实时演练与记录</h3>
        <p class="text-base-content/70">实时监控攻防过程，自动生成推演报告。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script> 