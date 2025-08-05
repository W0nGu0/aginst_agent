<template>
  <div 
    class="agent-card relative overflow-hidden cursor-pointer transform transition-all duration-500 hover:scale-105 hover:-translate-y-2"
    @click="$emit('select', agent, index)"
  >
    <!-- 卡片背景 -->
    <div class="absolute inset-0 bg-gradient-to-br from-base-100/90 to-base-200/80 backdrop-blur-md rounded-2xl"></div>
    
    <!-- 装饰性背景图案 -->
    <div class="absolute inset-0 opacity-10">
      <div class="absolute top-4 right-4 w-32 h-32 bg-gradient-to-br from-primary to-secondary rounded-full blur-2xl"></div>
      <div class="absolute bottom-4 left-4 w-24 h-24 bg-gradient-to-br from-accent to-info rounded-full blur-xl"></div>
    </div>

    <!-- 卡片内容 -->
    <div class="relative z-10 p-8 h-full flex flex-col">
      <!-- 卡片头部 -->
      <div class="flex items-center mb-6">
        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br flex items-center justify-center mr-4 shadow-lg"
             :class="cardGradient">
          <component :is="cardIcon" class="w-8 h-8 text-white" />
        </div>
        <div>
          <h3 class="text-2xl font-bold text-gradient mb-1">{{ agent.name }}</h3>
          <p class="text-base-content/60 text-sm">{{ cardSubtitle }}</p>
        </div>
      </div>

      <!-- 功能概览 -->
      <div class="flex-1 mb-6">
        <div class="grid grid-cols-2 gap-3">
          <div 
            v-for="(service, idx) in agent.children.slice(0, 4)" 
            :key="idx"
            class="bg-base-100/50 rounded-lg p-3 backdrop-blur-sm border border-white/10"
          >
            <div class="flex items-center">
              <div class="w-2 h-2 rounded-full mr-2" :class="serviceStatusClass(service)"></div>
              <span class="text-sm font-medium truncate">{{ service.name }}</span>
            </div>
            <div class="text-xs text-base-content/60 mt-1">
              {{ getServiceToolCount(service) }} 个工具
            </div>
          </div>
        </div>
        
        <!-- 更多服务提示 -->
        <div v-if="agent.children.length > 4" class="text-center mt-4">
          <span class="text-xs text-base-content/60">
            还有 {{ agent.children.length - 4 }} 个服务...
          </span>
        </div>
      </div>

      <!-- 卡片底部统计 -->
      <div class="flex justify-between items-center pt-4 border-t border-white/10">
        <div class="flex items-center space-x-4">
          <div class="text-center">
            <div class="text-lg font-bold text-primary">{{ totalTools }}</div>
            <div class="text-xs text-base-content/60">总工具</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-bold text-success">{{ enabledTools }}</div>
            <div class="text-xs text-base-content/60">已启用</div>
          </div>
        </div>
        
        <!-- 进入按钮 -->
        <div class="flex items-center text-primary hover:text-primary-focus transition-colors">
          <span class="text-sm font-medium mr-2">配置</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </div>
      </div>
    </div>

    <!-- 悬停效果 -->
    <div class="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 rounded-2xl opacity-0 transition-opacity duration-300 hover:opacity-100"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  agent: Object,
  index: Number
})

defineEmits(['select'])

// 卡片图标和样式配置
const cardConfigs = {
  0: { // 场景生成 Agent
    icon: 'ScenarioIcon',
    gradient: 'from-blue-500 to-cyan-500',
    subtitle: '智能场景构建与管理'
  },
  1: { // 攻击 Agent
    icon: 'AttackIcon', 
    gradient: 'from-red-500 to-pink-500',
    subtitle: '模拟攻击行为与渗透'
  },
  2: { // 防御 Agent
    icon: 'DefenseIcon',
    gradient: 'from-green-500 to-emerald-500', 
    subtitle: '主动防护与威胁阻断'
  },
  3: { // 评估 Agent
    icon: 'EvaluationIcon',
    gradient: 'from-purple-500 to-indigo-500',
    subtitle: '量化分析与报告生成'
  }
}

const cardGradient = computed(() => cardConfigs[props.index]?.gradient || 'from-gray-500 to-gray-600')
const cardSubtitle = computed(() => cardConfigs[props.index]?.subtitle || '智能代理服务')

// 图标组件
const cardIcon = computed(() => {
  const iconMap = {
    'ScenarioIcon': () => `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
    </svg>`,
    'AttackIcon': () => `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
    </svg>`,
    'DefenseIcon': () => `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>`,
    'EvaluationIcon': () => `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>`
  }
  
  const iconName = cardConfigs[props.index]?.icon || 'ScenarioIcon'
  return {
    template: iconMap[iconName]()
  }
})

// 计算服务状态
function serviceStatusClass(service) {
  const tools = getAllTools(service)
  const enabledCount = tools.filter(tool => tool.enabled).length
  const totalCount = tools.length
  
  if (enabledCount === totalCount) return 'bg-success'
  if (enabledCount > 0) return 'bg-warning'
  return 'bg-error'
}

// 获取服务工具数量
function getServiceToolCount(service) {
  return getAllTools(service).length
}

// 递归获取所有工具
function getAllTools(item) {
  if (!item.children) return []
  
  let tools = []
  for (const child of item.children) {
    if (child.hasOwnProperty('enabled')) {
      tools.push(child)
    } else {
      tools = tools.concat(getAllTools(child))
    }
  }
  return tools
}

// 计算总工具数和已启用工具数
const totalTools = computed(() => getAllTools(props.agent).length)
const enabledTools = computed(() => getAllTools(props.agent).filter(tool => tool.enabled).length)
</script>

<style scoped>
.agent-card {
  min-height: 320px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.agent-card:hover {
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.text-gradient {
  background: linear-gradient(45deg, var(--primary), var(--secondary), var(--accent));
  background-size: 200% 200%;
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: gradientShift 6s ease infinite;
}
</style>
