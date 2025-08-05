<template>
  <div 
    class="service-card relative overflow-hidden cursor-pointer transform transition-all duration-300 hover:scale-105 hover:-translate-y-1"
    @click="$emit('select', service, index)"
  >
    <!-- 卡片背景 -->
    <div class="absolute inset-0 bg-gradient-to-br from-base-100/80 to-base-200/60 backdrop-blur-sm rounded-xl border border-white/20"></div>
    
    <!-- 装饰性元素 -->
    <div class="absolute top-0 right-0 w-24 h-24 bg-gradient-to-bl from-primary/20 to-transparent rounded-bl-full"></div>
    
    <!-- 卡片内容 -->
    <div class="relative z-10 p-6">
      <!-- 服务头部 -->
      <div class="flex items-center mb-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center mr-4 shadow-md"
             :class="serviceIconGradient">
          <component :is="serviceIcon" class="h-6 w-6 text-white" />
        </div>
        <div class="flex-1">
          <h3 class="text-lg font-bold text-base-content mb-1">{{ service.name }}</h3>
          <p class="text-sm text-base-content/60">{{ serviceDescription }}</p>
        </div>
      </div>

      <!-- 工具预览 -->
      <div class="mb-4">
        <div class="flex flex-wrap gap-2 mb-3">
          <div 
            v-for="(tool, idx) in visibleTools" 
            :key="idx"
            class="flex items-center bg-base-100/50 rounded-full px-3 py-1 text-xs border border-white/10"
          >
            <div class="w-2 h-2 rounded-full mr-2" :class="tool.enabled ? 'bg-success' : 'bg-error'"></div>
            <span class="truncate max-w-24">{{ tool.name.replace('工具', '') }}</span>
          </div>
          
          <!-- 更多工具提示 -->
          <div v-if="hiddenToolsCount > 0" class="flex items-center bg-base-200/50 rounded-full px-3 py-1 text-xs text-base-content/60">
            +{{ hiddenToolsCount }} 更多
          </div>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="flex justify-between items-center pt-3 border-t border-white/10">
        <div class="flex space-x-4">
          <div class="text-center">
            <div class="text-lg font-bold text-primary">{{ totalTools }}</div>
            <div class="text-xs text-base-content/60">工具</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-bold" :class="enabledTools > 0 ? 'text-success' : 'text-base-content/40'">
              {{ enabledTools }}
            </div>
            <div class="text-xs text-base-content/60">启用</div>
          </div>
        </div>
        
        <!-- 状态指示器 -->
        <div class="flex items-center">
          <div class="w-3 h-3 rounded-full mr-2" :class="serviceStatusClass"></div>
          <span class="text-xs text-base-content/60">{{ serviceStatusText }}</span>
        </div>
      </div>

      <!-- 进入箭头 -->
      <div class="absolute bottom-4 right-4 opacity-60 group-hover:opacity-100 transition-opacity">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
        </svg>
      </div>
    </div>

    <!-- 悬停效果 -->
    <div class="absolute inset-0 bg-gradient-to-r from-primary/5 to-secondary/5 rounded-xl opacity-0 transition-opacity duration-300 hover:opacity-100"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  service: Object,
  index: Number
})

defineEmits(['select'])

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

// 计算工具统计
const allTools = computed(() => getAllTools(props.service))
const totalTools = computed(() => allTools.value.length)
const enabledTools = computed(() => allTools.value.filter(tool => tool.enabled).length)

// 显示的工具（最多3个）
const visibleTools = computed(() => allTools.value.slice(0, 3))
const hiddenToolsCount = computed(() => Math.max(0, allTools.value.length - 3))

// 服务状态
const serviceStatusClass = computed(() => {
  const ratio = enabledTools.value / totalTools.value
  if (ratio === 1) return 'bg-success'
  if (ratio > 0.5) return 'bg-warning'
  if (ratio > 0) return 'bg-info'
  return 'bg-error'
})

const serviceStatusText = computed(() => {
  const ratio = enabledTools.value / totalTools.value
  if (ratio === 1) return '全部启用'
  if (ratio > 0.5) return '大部分启用'
  if (ratio > 0) return '部分启用'
  return '全部禁用'
})

// 服务图标和渐变
const serviceIconGradient = computed(() => {
  const gradients = {
    '场景服务': 'from-blue-500 to-cyan-500',
    '容器服务': 'from-indigo-500 to-purple-500',
    '攻击服务': 'from-red-500 to-pink-500',
    '修复服务': 'from-green-500 to-emerald-500',
    '阻断服务': 'from-orange-500 to-red-500',
    '溯源服务': 'from-purple-500 to-indigo-500',
    '评估服务': 'from-violet-500 to-purple-500',
    '漏洞修复服务': 'from-green-500 to-emerald-500',
    '威胁阻断服务': 'from-orange-500 to-red-500',
    '攻击溯源服务': 'from-purple-500 to-indigo-500'
  }
  return gradients[props.service.name] || 'from-primary/80 to-secondary/80'
})

const serviceIcon = computed(() => {
  const iconMap = {
    '场景服务': () => `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
    </svg>`,
    '容器服务': () => `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
    </svg>`,
    '攻击服务': () => `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
    </svg>`,
    '修复服务': () => `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>`,
    '阻断服务': () => `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L12 21l-6.364-6.364M5.636 5.636L12 3l6.364 6.364" />
    </svg>`,
    '溯源服务': () => `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>`,
    '评估服务': () => `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>`,
    '漏洞修复服务': () => `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>`,
    '威胁阻断服务': () => `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>`,
    '攻击溯源服务': () => `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
    </svg>`
  }

  return {
    template: iconMap[props.service.name] || iconMap['修复服务']
  }
})

// 服务描述
const serviceDescription = computed(() => {
  const descriptions = {
    '场景服务': '管理攻防场景模板与实例',
    '容器服务': '容器化环境部署与管理',
    '攻击服务': '模拟各类攻击行为',
    '修复服务': '自动化漏洞修复',
    '阻断服务': '威胁检测与阻断',
    '溯源服务': '攻击路径追踪分析',
    '评估服务': '量化评估与报告生成',
    '漏洞修复服务': '智能漏洞修复',
    '威胁阻断服务': '主动威胁防护',
    '攻击溯源服务': '攻击行为溯源'
  }
  return descriptions[props.service.name] || '智能服务模块'
})
</script>

<style scoped>
.service-card {
  min-height: 180px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.service-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}
</style>
