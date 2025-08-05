<template>
  <div class="home-view w-full overflow-hidden">
    <!-- Hero Section -->
    <section class="relative cyber-bg hero-section overflow-hidden py-20 px-6 md:px-12 lg:px-32 flex flex-col md:flex-row items-center gap-12">
      <!-- 动态背景图形 -->
      <div class="cyber-graphic absolute inset-0 pointer-events-none">
        <!-- 向右移动50px的同心圆，并添加logo -->
        <div class="cyber-circle-with-logo">
          <div class="cyber-circle animate-pulse-slow"></div>
          <div class="logo-container">
            <img :src="logoSrc" alt="Logo" class="logo-image animate-float" />
          </div>
        </div>
        <div class="cyber-grid"></div>
        <div class="cyber-nodes"></div>
        <div class="pulse-waves"></div>
        <!-- 红蓝对抗效果 -->
        <div class="battle-effects">
          <div class="red-attack-wave"></div>
          <div class="blue-defense-wave"></div>
          <div class="battle-particles"></div>
        </div>
      </div>

      <!-- 左侧文字 -->
      <div class="flex-1 z-10 text-center md:text-left" data-aos="fade-right">
        <h1 class="text-gradient text-4xl md:text-6xl font-extrabold mb-6 animate-gradient leading-snug">
          AI 驱动的攻防推演平台
        </h1>
        <p class="text-base-content/80 text-lg md:text-xl mb-10 max-w-2xl">
          集成可视化网络拓扑、实时演练与智能评估体系，帮助安全从业者迅速构建并体验高度仿真的攻防场景。
        </p>
        <div class="flex flex-col sm:flex-row justify-center md:justify-start gap-4">
          <RouterLink to="/against" class="btn btn-primary btn-lg shadow-lg transition-transform duration-200 hover:-translate-y-1">立即创建动态靶场</RouterLink>
          <RouterLink to="/history" class="btn btn-outline btn-lg transition-transform duration-200 hover:-translate-y-1">查看推演记录</RouterLink>
        </div>
      </div>
    </section>

    <!-- Platform Features Section -->
    <section class="py-16 px-6 md:px-12 lg:px-32 bg-gradient-transition relative">
      <div class="text-center mb-12">
        <h2 class="text-3xl font-bold mb-8 text-gradient animate-gradient">平台特色</h2>
        <div class="flex flex-wrap justify-center items-center gap-16 md:gap-20 lg:gap-24 xl:gap-28">
          <!-- 特色球体1 -->
          <div class="feature-sphere feature-sphere-1">
            <div class="sphere-content">
              <div class="sphere-icon">🎯</div>
              <div class="sphere-text">场景一键生成<br>大模型语义解析</div>
            </div>
          </div>

          <!-- 特色球体2 -->
          <div class="feature-sphere feature-sphere-2">
            <div class="sphere-content">
              <div class="sphere-icon">🤖</div>
              <div class="sphere-text">深度强化学习驱动<br>Agent 智能协同</div>
            </div>
          </div>

          <!-- 特色球体3 -->
          <div class="feature-sphere feature-sphere-3">
            <div class="sphere-content">
              <div class="sphere-icon">📊</div>
              <div class="sphere-text">实时态势监控</div>
            </div>
          </div>

          <!-- 特色球体4 -->
          <div class="feature-sphere feature-sphere-4">
            <div class="sphere-content">
              <div class="sphere-icon">📈</div>
              <div class="sphere-text">全域量化指标</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Feature Cards -->
    <section class="py-16 px-6 md:px-12 lg:px-32 feature-cards-section relative">
      <h2 class="text-center text-3xl font-bold mb-12 text-gradient animate-gradient">核心能力</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
        <div class="glass-panel p-8 text-center transition-transform duration-300 hover:-translate-y-2">
          <h3 class="text-xl font-semibold mb-2">智能场景生成</h3>
          <p class="text-base-content/70">基于场景生成智能体和自然语言描述，一键生成个性化攻防场景。</p>
        </div>
        <div class="glass-panel p-8 text-center transition-transform duration-300 hover:-translate-y-2">
          <h3 class="text-xl font-semibold mb-2">高度仿真攻防推演</h3>
          <p class="text-base-content/70">基于攻击智能体和防御智能体体系，完成贴合真实业务场景的攻防推演。</p>
        </div>
        <div class="glass-panel p-8 text-center transition-transform duration-300 hover:-translate-y-2">
          <h3 class="text-xl font-semibold mb-2">全域动态量化评估</h3>
          <p class="text-base-content/70">基于中控智能体和评估智能体的全域实时监控技术，获取演练数据并自动生成推演报告。</p>
        </div>
      </div>
    </section>

    <!-- Metrics Section -->
    <section class="py-16 px-6 md:px-12 lg:px-32 metrics-section relative">
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
import logoSrc from '@/assets/logo.svg'
</script>

<style scoped>
@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

@keyframes sphereFloat1 {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-8px) rotate(5deg); }
}

@keyframes sphereFloat2 {
  0%, 100% { transform: translateY(-5px) rotate(0deg); }
  50% { transform: translateY(-15px) rotate(-5deg); }
}

@keyframes sphereFloat3 {
  0%, 100% { transform: translateY(-3px) rotate(0deg); }
  50% { transform: translateY(-12px) rotate(3deg); }
}

@keyframes sphereFloat4 {
  0%, 100% { transform: translateY(-2px) rotate(0deg); }
  50% { transform: translateY(-10px) rotate(-3deg); }
}

@keyframes redAttackWave {
  0% {
    transform: translateX(-100%) scale(0.8);
    opacity: 0;
  }
  50% {
    opacity: 0.8;
    transform: translateX(0%) scale(1);
  }
  100% {
    transform: translateX(100%) scale(1.2);
    opacity: 0;
  }
}

@keyframes blueDefenseWave {
  0% {
    transform: translateX(100%) scale(0.8);
    opacity: 0;
  }
  50% {
    opacity: 0.6;
    transform: translateX(0%) scale(1);
  }
  100% {
    transform: translateX(-100%) scale(1.2);
    opacity: 0;
  }
}

@keyframes battleParticles {
  0% {
    transform: translate(0, 0) scale(0);
    opacity: 0;
  }
  20% {
    opacity: 1;
    transform: translate(10px, -10px) scale(1);
  }
  80% {
    opacity: 1;
    transform: translate(50px, -50px) scale(0.8);
  }
  100% {
    transform: translate(100px, -100px) scale(0);
    opacity: 0;
  }
}

.animate-gradient {
  background-size: 200% 200%;
  animation: gradientShift 8s ease infinite;
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}

/* Hero Section 样式 */
.hero-section {
  position: relative;
}

.hero-section::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100px;
  background: linear-gradient(
    180deg,
    transparent 0%,
    rgba(var(--base-200-rgb), 0.3) 50%,
    rgba(var(--base-200-rgb), 0.8) 100%
  );
  pointer-events: none;
  z-index: 1;
}

/* 平台特色部分背景渐变过渡 */
.bg-gradient-transition {
  background: linear-gradient(
    180deg,
    rgba(var(--base-200-rgb), 0.8) 0%,
    rgba(var(--base-200-rgb), 0.9) 20%,
    rgba(var(--base-200-rgb), 0.7) 50%,
    rgba(var(--base-200-rgb), 0.9) 80%,
    rgba(var(--base-300-rgb), 0.6) 100%
  );
  backdrop-filter: blur(12px);
}

.bg-gradient-transition::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: linear-gradient(
    180deg,
    rgba(var(--base-200-rgb), 0.9) 0%,
    transparent 100%
  );
  pointer-events: none;
  z-index: 1;
}

.bg-gradient-transition::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: linear-gradient(
    0deg,
    rgba(var(--base-300-rgb), 0.8) 0%,
    transparent 100%
  );
  pointer-events: none;
  z-index: 1;
}

/* Feature Cards Section 样式 */
.feature-cards-section {
  background: linear-gradient(
    180deg,
    rgba(var(--base-300-rgb), 0.6) 0%,
    rgba(var(--base-100-rgb), 0.4) 30%,
    rgba(var(--base-100-rgb), 0.6) 70%,
    rgba(var(--base-300-rgb), 0.8) 100%
  );
  backdrop-filter: blur(6px);
}

.feature-cards-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(
    180deg,
    rgba(var(--base-300-rgb), 0.9) 0%,
    transparent 100%
  );
  pointer-events: none;
  z-index: 1;
}

.feature-cards-section::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(
    0deg,
    rgba(var(--base-300-rgb), 0.9) 0%,
    transparent 100%
  );
  pointer-events: none;
  z-index: 1;
}

/* Metrics Section 样式 */
.metrics-section {
  background: linear-gradient(
    180deg,
    rgba(var(--base-300-rgb), 0.8) 0%,
    rgba(var(--base-300-rgb), 0.9) 30%,
    rgba(var(--base-300-rgb), 0.95) 70%,
    rgba(var(--base-300-rgb), 1) 100%
  );
  backdrop-filter: blur(10px);
}

.metrics-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: linear-gradient(
    180deg,
    rgba(var(--base-300-rgb), 1) 0%,
    transparent 100%
  );
  pointer-events: none;
  z-index: 1;
}

/* 同心圆容器 - 向右移动200px */
.cyber-circle-with-logo {
  position: absolute;
  top: 50%;
  left: calc(50% + 200px); /* 向右移动200px */
  transform: translate(-50%, -50%);
  width: 300px;
  height: 300px;
}

/* Logo容器 - 向右移动150px */
.logo-container {
  position: absolute;
  top: 50%;
  left: calc(50% + 10px); /* Logo独立向右移动150px */
  transform: translate(-50%, -50%);
  z-index: 10;
}

.logo-image {
  width: 120px; /* 放大logo */
  height: 120px;
  filter: drop-shadow(0 0 15px rgba(var(--primary-rgb), 0.6));
}

/* 特色球体样式 */
.feature-sphere {
  position: relative;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: linear-gradient(135deg,
    rgba(var(--primary-rgb), 0.2) 0%,
    rgba(var(--secondary-rgb), 0.2) 50%,
    rgba(var(--accent-rgb), 0.2) 100%);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(var(--primary-rgb), 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow:
    0 8px 32px rgba(var(--primary-rgb), 0.2),
    inset 0 2px 8px rgba(255, 255, 255, 0.1);
}

.feature-sphere:hover {
  transform: translateY(-5px) scale(1.05);
  box-shadow:
    0 12px 40px rgba(var(--primary-rgb), 0.3),
    inset 0 2px 8px rgba(255, 255, 255, 0.2);
}

.feature-sphere-1 {
  animation: sphereFloat1 4s ease-in-out infinite;
}

.feature-sphere-2 {
  animation: sphereFloat2 4.5s ease-in-out infinite;
}

.feature-sphere-3 {
  animation: sphereFloat3 3.8s ease-in-out infinite;
}

.feature-sphere-4 {
  animation: sphereFloat4 4.2s ease-in-out infinite;
}

.sphere-content {
  text-align: center;
  color: var(--base-content);
}

.sphere-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  display: block;
}

.sphere-text {
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.3;
}

/* 红蓝对抗效果 */
.battle-effects {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.red-attack-wave {
  position: absolute;
  top: 30%;
  left: 0;
  width: 200px;
  height: 4px;
  background: linear-gradient(90deg,
    transparent 0%,
    #ff4444 20%,
    #ff6666 50%,
    #ff4444 80%,
    transparent 100%);
  border-radius: 2px;
  animation: redAttackWave 6s ease-in-out infinite;
  box-shadow: 0 0 10px #ff4444;
}

.blue-defense-wave {
  position: absolute;
  top: 70%;
  right: 0;
  width: 180px;
  height: 3px;
  background: linear-gradient(90deg,
    transparent 0%,
    #4444ff 20%,
    #6666ff 50%,
    #4444ff 80%,
    transparent 100%);
  border-radius: 2px;
  animation: blueDefenseWave 7s ease-in-out infinite 1s;
  box-shadow: 0 0 8px #4444ff;
}

.battle-particles {
  position: absolute;
  top: 50%;
  left: 20%;
  width: 100%;
  height: 100%;
}

.battle-particles::before,
.battle-particles::after {
  content: '';
  position: absolute;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  animation: battleParticles 3s ease-out infinite;
}

.battle-particles::before {
  background: #ff4444;
  top: 20%;
  left: 10%;
  animation-delay: 0s;
  box-shadow: 0 0 6px #ff4444;
}

.battle-particles::after {
  background: #4444ff;
  top: 60%;
  left: 30%;
  animation-delay: 1.5s;
  box-shadow: 0 0 6px #4444ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .feature-sphere {
    width: 140px;
    height: 140px;
  }

  .sphere-icon {
    font-size: 2rem;
  }

  .sphere-text {
    font-size: 0.8rem;
  }

  .cyber-circle-with-logo {
    left: calc(50% + 100px); /* 在移动设备上向右移动100px */
    width: 250px;
    height: 250px;
  }

  .logo-container {
    left: calc(50% + 80px); /* 移动设备上logo向右移动80px */
  }

  .logo-image {
    width: 90px; /* 移动设备上也放大logo */
    height: 90px;
  }
}
</style>