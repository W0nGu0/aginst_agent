<template>
  <div class="detail-view-container">
    <!-- 背景遮罩 -->
    <div class="fixed inset-0 bg-black/20 backdrop-blur-sm z-30" @click="$emit('back')"></div>

    <!-- 居中的详细面板 -->
    <div class="fixed inset-0 z-40 flex items-center justify-center p-4 md:p-8">
      <div class="detail-panel bg-base-100/95 backdrop-blur-xl rounded-3xl shadow-2xl max-w-6xl w-full h-full overflow-hidden top-10 relative">
        <!-- 返回按钮 -->
        <div
          class="absolute top-6 left-6 z-50 cursor-pointer bg-base-200/80 backdrop-blur-sm rounded-full p-3 hover:bg-base-200 transition-all duration-300 shadow-lg"
          @click="$emit('back')"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </div>

        <!-- 滑动进入的详细视图 -->
        <div class="detail-view p-6 md:p-10 pt-20 md:pt-24 overflow-y-auto h-full">
          <!-- 头部信息 -->
          <div class="text-center mb-12">
            <div class="flex items-center justify-center mb-6">
              <div class="w-20 h-20 rounded-3xl bg-gradient-to-br flex items-center justify-center mr-6 shadow-xl"
                   :class="agentGradient">
                <div v-html="agentIcon" class="w-10 h-10 text-white"></div>
              </div>
              <div class="text-left">
                <h1 class="text-4xl font-bold text-gradient mb-2">{{ agent.name }}</h1>
                <p class="text-base-content/70 text-lg">{{ agentDescription }}</p>
              </div>
            </div>

            <!-- 统计信息 -->
            <div class="flex justify-center space-x-8 mb-8">
              <div class="text-center">
                <div class="text-3xl font-bold text-primary">{{ totalServices }}</div>
                <div class="text-sm text-base-content/60">服务模块</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-secondary">{{ totalTools }}</div>
                <div class="text-sm text-base-content/60">可用工具</div>
              </div>
              <div class="text-center">
                <div class="text-3xl font-bold text-success">{{ enabledTools }}</div>
                <div class="text-sm text-base-content/60">已启用</div>
              </div>
            </div>
          </div>

          <!-- 服务列表 -->
          <div v-if="!selectedService">
            <h2 class="text-2xl font-bold mb-8 text-center">服务配置</h2>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ServiceCard
                v-for="(service, index) in agent.children"
                :key="index"
                :service="service"
                :index="index"
                @select="selectService"
              />
            </div>
          </div>

          <!-- 工具详细配置视图 -->
          <ToolConfigView
            v-if="selectedService"
            :service="selectedService"
            :service-index="selectedServiceIndex"
            @toggle-tool="$emit('toggle-tool', $event)"
            @back="goBackToServices"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import ServiceCard from './ServiceCard.vue'
import ToolConfigView from './ToolConfigView.vue'

const props = defineProps({
  agent: Object,
  agentIndex: Number
})

defineEmits(['toggle-tool', 'back'])

// 防止背景滚动
onMounted(() => {
  document.body.style.overflow = 'hidden'
})

onUnmounted(() => {
  document.body.style.overflow = ''
})

// 选中的服务
const selectedService = ref(null)
const selectedServiceIndex = ref(-1)

// Agent配置
const agentConfigs = {
  0: { 
    gradient: 'from-blue-500 to-cyan-500',
    description: '智能化场景生成与容器管理，支持一键部署复杂攻防环境'
  },
  1: { 
    gradient: 'from-red-500 to-pink-500',
    description: '模拟真实攻击行为，提供全方位的渗透测试能力'
  },
  2: { 
    gradient: 'from-green-500 to-emerald-500',
    description: '主动防护与威胁检测，构建多层次安全防御体系'
  },
  3: { 
    gradient: 'from-purple-500 to-indigo-500',
    description: '量化分析攻防效果，生成专业的评估报告'
  }
}

const agentGradient = computed(() => agentConfigs[props.agentIndex]?.gradient || 'from-gray-500 to-gray-600')
const agentDescription = computed(() => agentConfigs[props.agentIndex]?.description || '智能代理服务')

// 图标HTML
const agentIcon = computed(() => {
  const iconMap = {
    0: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
    </svg>`,
    1: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
    </svg>`,
    2: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>`,
    3: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>`
  }
  
  return iconMap[props.agentIndex] || iconMap[0]
})

// 选择服务
function selectService(service, index) {
  selectedService.value = service
  selectedServiceIndex.value = index
}

// 返回服务列表
function goBackToServices() {
  selectedService.value = null
  selectedServiceIndex.value = -1
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

// 计算统计信息
const totalServices = computed(() => props.agent.children.length)
const totalTools = computed(() => getAllTools(props.agent).length)
const enabledTools = computed(() => getAllTools(props.agent).filter(tool => tool.enabled).length)
</script>

<style scoped>
.detail-view-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 30;
}

.detail-panel {
  animation: modalSlideIn 0.4s ease-out;
  border: 1px solid rgba(var(--primary-rgb), 0.1);
}

.detail-view {
  animation: fadeInUp 0.5s ease-out 0.1s both;
}

@keyframes modalSlideIn {
  from {
    transform: scale(0.9);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
