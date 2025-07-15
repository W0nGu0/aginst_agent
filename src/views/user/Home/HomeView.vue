<template>
  <div class="home-view flex justify-center w-full">
    <section class="text-center pt-16 w-full max-w-[1280px]">
      <h1 class="text-4xl md:text-5xl font-bold mb-6 text-gradient">AI 驱动的攻防推演平台</h1>
      <p class="text-base-content/80 text-lg mb-10">我们的平台集成 AI 智能推荐、可视化网络拓扑与实时攻防演练，帮助安全从业者快速构建并体验真实的攻防场景。</p>
      <div class="flex flex-col md:flex-row justify-center gap-4 mb-16">
        <RouterLink to="/against" class="btn btn-primary btn-lg">立即创建动态靶场</RouterLink>
        <RouterLink to="/history" class="btn btn-outline btn-lg">查看推演记录</RouterLink>
      </div>
    </section>

    <section class="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-[1280px] mx-auto">
      <div class="glass-panel p-6 text-center">
        <h3 class="text-xl font-semibold mb-2">智能场景生成</h3>
        <p class="text-base-content/70">基于自然语言描述，一键生成个性化攻防场景。</p>
      </div>
      <div class="glass-panel p-6 text-center">
        <h3 class="text-xl font-semibold mb-2">可视化拓扑设计</h3>
        <p class="text-base-content/70">拖拽式网络拓扑编辑器，快速搭建复杂网络环境。</p>
      </div>
      <div class="glass-panel p-6 text-center">
        <h3 class="text-xl font-semibold mb-2">实时演练与记录</h3>
        <p class="text-base-content/70">实时监控攻防过程，自动生成推演报告。</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script> 