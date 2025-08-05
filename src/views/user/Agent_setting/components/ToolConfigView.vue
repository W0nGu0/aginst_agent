<template>
  <div class="tool-config-container fixed inset-0 z-50 overflow-hidden">
    <!-- 背景遮罩 -->
    <div class="fixed inset-0 bg-black/30 backdrop-blur-sm z-30" @click="$emit('back')"></div>

    <!-- 居中的配置面板 -->
    <div class="fixed inset-0 z-40 flex items-center justify-center p-1 md:p-2 ">
      <div class="tool-config-panel bg-base-100/95 backdrop-blur-xl rounded-3xl shadow-2xl w-[98vw] h-full max-w-none overflow-hidden relative">
        <!-- 工具配置视图 -->
        <div class="tool-config-view p-6 md:p-8 h-full flex flex-col">
          <!-- 固定头部信息 -->
          <div class="flex-shrink-0 text-center mb-6 pb-6 border-b border-base-300/30">
            <div class="flex items-center justify-center mb-6">
              <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/80 to-secondary/80 flex items-center justify-center mr-4 shadow-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div class="text-left">
                <h1 class="text-3xl font-bold text-gradient mb-2">{{ service.name }}</h1>
                <p class="text-base-content/70">工具配置与管理</p>
              </div>
            </div>

            <!-- 快速操作 -->
            <div class="flex justify-center space-x-4">
              <button
                class="btn btn-primary btn-sm"
                @click="enableAllTools"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                全部启用
              </button>
              <button
                class="btn btn-outline btn-sm"
                @click="disableAllTools"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                全部禁用
              </button>
              <button
                class="btn btn-ghost btn-sm"
                @click="resetToDefault"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                重置默认
              </button>
            </div>
          </div>

          <!-- 可滚动的工具列表 -->
          <div class="flex-1 overflow-y-auto custom-scrollbar">
            <div class="max-w-none mx-auto px-2">
              <div class="grid grid-cols-1  gap-4">
                <ToolItem
                  v-for="(tool, index) in allTools"
                  :key="index"
                  :tool="tool"
                  :index="index"
                  @toggle="toggleTool"
                />
              </div>

              <!-- 空状态 -->
              <div v-if="allTools.length === 0" class="text-center py-12">
                <div class="w-24 h-24 mx-auto mb-4 bg-base-200 rounded-full flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-base-content/40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                  </svg>
                </div>
                <h3 class="text-lg font-medium text-base-content/60 mb-2">暂无可配置工具</h3>
                <p class="text-base-content/40">该服务模块暂未包含可配置的工具</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import ToolItem from './ToolItem.vue'

const props = defineProps({
  service: Object,
  serviceIndex: Number
})

const emit = defineEmits(['toggle-tool', 'back'])

// 防止背景滚动
onMounted(() => {
  document.body.classList.add('modal-open')
  document.body.style.overflow = 'hidden'
})

onUnmounted(() => {
  document.body.classList.remove('modal-open')
  document.body.style.overflow = ''
})

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

const allTools = computed(() => getAllTools(props.service))

// 工具操作
function toggleTool(tool) {
  tool.enabled = !tool.enabled
}

function enableAllTools() {
  allTools.value.forEach(tool => {
    tool.enabled = true
  })
}

function disableAllTools() {
  allTools.value.forEach(tool => {
    tool.enabled = false
  })
}

function resetToDefault() {
  // 这里可以根据实际需求设置默认状态
  // 暂时设置为大部分启用的状态
  allTools.value.forEach((tool, index) => {
    tool.enabled = index % 3 !== 2 // 大约2/3的工具启用
  })
}
</script>

<style scoped>
.tool-config-container {
  /* 防止背景滚动 */
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 50;
}

.tool-config-panel {
  animation: modalSlideIn 0.4s ease-out;
  border: 1px solid rgba(var(--primary-rgb), 0.1);
}

.tool-config-view {
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
    transform: translateY(30px);
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

/* 自定义滚动条样式 */
.custom-scrollbar {
  scrollbar-width: thin;  /* Firefox */
  scrollbar-color: rgba(var(--primary-rgb), 0.4) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(var(--base-300-rgb), 0.2);
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(var(--primary-rgb), 0.4);
  border-radius: 4px;
  border: 1px solid rgba(var(--base-100-rgb), 0.1);
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--primary-rgb), 0.6);
}

/* 防止背景滚动 */
body.modal-open {
  overflow: hidden;
}
</style>
