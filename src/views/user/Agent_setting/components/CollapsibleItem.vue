<template>
  <div class="collapsible-item" :class="containerClass">
    <!-- 主要内容区域 -->
    <div
      class="flex items-center justify-between px-4 py-3 rounded-xl cursor-pointer transition-all duration-300 group"
      :class="itemClass"
      @click="toggle"
    >
      <!-- 左侧内容 -->
      <div class="flex items-center gap-3 flex-1 min-w-0">
        <!-- 展开/收起图标 -->
        <div v-if="hasChildren" class="flex-shrink-0">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5 transition-all duration-300 text-base-content/60 group-hover:text-base-content"
            :class="{ 'rotate-90 text-primary': open }"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </div>

        <!-- 层级图标 -->
        <div class="flex-shrink-0" :class="iconContainerClass">
          <svg xmlns="http://www.w3.org/2000/svg" :class="iconClass" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="levelIcon" />
          </svg>
        </div>

        <!-- 名称和描述 -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <h3 class="font-semibold truncate" :class="nameClass">{{ item.name }}</h3>
            <!-- 状态标识 -->
            <span v-if="statusBadge" class="badge badge-xs" :class="statusBadgeClass">
              {{ statusBadge }}
            </span>
          </div>
          <!-- 描述信息 -->
          <p v-if="item.description" class="text-xs text-base-content/60 truncate">
            {{ item.description }}
          </p>
          <!-- 子项统计 -->
          <div v-if="hasChildren && childrenStats" class="flex items-center gap-2 mt-1">
            <span class="text-xs text-base-content/50">
              {{ childrenStats }}
            </span>
          </div>
        </div>
      </div>

      <!-- 右侧控制区域 -->
      <div class="flex items-center gap-2 flex-shrink-0">
        <!-- 工具开关 -->
        <template v-if="isTool">
          <div class="flex items-center gap-2">
            <!-- 工具状态指示器 -->
            <div class="w-2 h-2 rounded-full" :class="toolStatusIndicator"></div>

            <!-- 开关控制 -->
            <label class="inline-flex items-center cursor-pointer" @click.stop>
              <span class="relative">
                <input
                  type="checkbox"
                  class="sr-only"
                  v-model="item.enabled"
                  @change="emitToggle"
                />
                <div
                  class="w-12 h-6 rounded-full shadow-inner transition-all duration-300"
                  :class="item.enabled ? 'bg-success' : 'bg-base-300'"
                >
                </div>
                <div
                  class="dot absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition-transform duration-300 shadow-sm"
                  :class="item.enabled ? 'translate-x-6' : 'translate-x-0'"
                >
                </div>
              </span>
            </label>
          </div>
        </template>

        <!-- 非工具项的展开指示器 -->
        <template v-else-if="hasChildren">
          <div class="flex items-center gap-1 text-xs text-base-content/50">
            <span>{{ enabledChildrenCount }}/{{ totalChildrenCount }}</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </template>
      </div>
    </div>

    <!-- 子元素容器 -->
    <transition
      name="expand"
      @enter="onEnter"
      @after-enter="onAfterEnter"
      @leave="onLeave"
      @after-leave="onAfterLeave"
    >
      <div v-show="open" class="children-container overflow-hidden">
        <div class="children-content" :class="childrenContainerClass">
          <CollapsibleItem
            v-for="(child, idx) in item.children"
            :key="`${child.id || child.name}-${idx}`"
            :item="child"
            :level="childLevel"
            :parent-open="open"
            @toggle-tool="emitToggle"
          />
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import CollapsibleItem from './CollapsibleItem.vue'

const props = defineProps({
  item: Object,
  level: String, // agent / subAgent / mcp / tool
  parentOpen: {
    type: Boolean,
    default: true
  }
})
const emit = defineEmits(['toggle-tool'])

const open = ref(false)

// 基础计算属性
const hasChildren = computed(() => Array.isArray(props.item.children) && props.item.children.length)
const isTool = computed(() => Object.prototype.hasOwnProperty.call(props.item, 'enabled'))

const childLevel = computed(() => {
  if (!hasChildren.value) return ''
  if (props.level === 'agent') {
    // 判断是否还需要 subAgent 级
    const firstChildHasChildren = Array.isArray(props.item.children[0]?.children) && props.item.children[0].children.length
    return firstChildHasChildren ? 'subAgent' : 'mcp'
  }
  if (props.level === 'subAgent') return 'mcp'
  if (props.level === 'mcp') return 'tool'
  return ''
})

// 样式计算属性
const containerClass = computed(() => {
  return [
    'transition-all duration-300',
    {
      'mb-3': props.level === 'agent',
      'mb-2': props.level === 'subAgent',
      'mb-1': props.level === 'mcp',
      'mb-0.5': props.level === 'tool'
    }
  ]
})

const itemClass = computed(() => {
  const baseClasses = [
    'hover:shadow-lg',
    'hover:-translate-y-1',
    'border border-transparent',
    'backdrop-blur-sm'
  ]

  switch (props.level) {
    case 'agent':
      return [
        ...baseClasses,
        'bg-gradient-to-r from-primary/15 to-secondary/15',
        'hover:from-primary/25 hover:to-secondary/25',
        'border-primary/30',
        'shadow-md'
      ]
    case 'subAgent':
      return [
        ...baseClasses,
        'bg-gradient-to-r from-secondary/10 to-accent/10',
        'hover:from-secondary/20 hover:to-accent/20',
        'border-secondary/25',
        'shadow-sm'
      ]
    case 'mcp':
      return [
        ...baseClasses,
        'bg-base-100/80',
        'hover:bg-base-100/95',
        'border-base-300/40'
      ]
    case 'tool':
      return [
        ...baseClasses,
        'bg-base-200/60',
        'hover:bg-base-200/80',
        'border-base-300/30'
      ]
    default:
      return baseClasses
  }
})

const iconContainerClass = computed(() => {
  switch (props.level) {
    case 'agent':
      return 'w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-primary/20 flex items-center justify-center shadow-sm'
    case 'subAgent':
      return 'w-8 h-8 rounded-lg bg-gradient-to-br from-secondary/30 to-secondary/20 flex items-center justify-center'
    case 'mcp':
      return 'w-7 h-7 rounded-md bg-gradient-to-br from-accent/30 to-accent/20 flex items-center justify-center'
    case 'tool':
      return 'w-6 h-6 rounded bg-gradient-to-br from-info/30 to-info/20 flex items-center justify-center'
    default:
      return 'w-6 h-6 rounded bg-base-300/50 flex items-center justify-center'
  }
})

const iconClass = computed(() => {
  switch (props.level) {
    case 'agent':
      return 'h-6 w-6 text-primary'
    case 'subAgent':
      return 'h-5 w-5 text-secondary'
    case 'mcp':
      return 'h-4 w-4 text-accent'
    case 'tool':
      return 'h-3.5 w-3.5 text-info'
    default:
      return 'h-4 w-4 text-base-content/60'
  }
})

const levelIcon = computed(() => {
  switch (props.level) {
    case 'agent':
      return 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z'
    case 'subAgent':
      return 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10'
    case 'mcp':
      return 'M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z'
    case 'tool':
      return 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z'
    default:
      return 'M9 5H7a2 2 0 00-2 2v6a2 2 0 002 2h2m5 0h2a2 2 0 002-2V7a2 2 0 00-2-2h-2m-5 4h5'
  }
})

const nameClass = computed(() => {
  switch (props.level) {
    case 'agent':
      return 'text-lg text-primary font-bold'
    case 'subAgent':
      return 'text-base text-secondary font-semibold'
    case 'mcp':
      return 'text-sm text-accent font-medium'
    case 'tool':
      return 'text-sm text-base-content'
    default:
      return 'text-base text-base-content'
  }
})

// 统计计算属性
const totalChildrenCount = computed(() => {
  if (!hasChildren.value) return 0
  return props.item.children.length
})

const enabledChildrenCount = computed(() => {
  if (!hasChildren.value) return 0
  return props.item.children.filter(child => {
    if (child.enabled !== undefined) return child.enabled
    if (child.children) {
      return child.children.some(grandChild => grandChild.enabled)
    }
    return false
  }).length
})

const childrenStats = computed(() => {
  if (!hasChildren.value) return null
  const enabled = enabledChildrenCount.value
  const total = totalChildrenCount.value
  return `${enabled}/${total} 项已启用`
})

const statusBadge = computed(() => {
  if (isTool.value) {
    return props.item.enabled ? '已启用' : '已禁用'
  } else if (hasChildren.value) {
    const enabled = enabledChildrenCount.value
    const total = totalChildrenCount.value
    if (enabled === total) return '全部启用'
    if (enabled === 0) return '全部禁用'
    return '部分启用'
  }
  return null
})

const statusBadgeClass = computed(() => {
  if (isTool.value) {
    return props.item.enabled ? 'badge-success' : 'badge-ghost'
  } else if (hasChildren.value) {
    const enabled = enabledChildrenCount.value
    const total = totalChildrenCount.value
    if (enabled === total) return 'badge-success'
    if (enabled === 0) return 'badge-ghost'
    return 'badge-warning'
  }
  return 'badge-ghost'
})

const toolStatusIndicator = computed(() => {
  if (!isTool.value) return ''
  return props.item.enabled ? 'bg-success animate-pulse' : 'bg-base-300'
})

const childrenContainerClass = computed(() => {
  switch (props.level) {
    case 'agent':
      return 'mt-4 ml-8 pl-4 border-l-2 border-primary/40 space-y-3'
    case 'subAgent':
      return 'mt-3 ml-6 pl-3 border-l-2 border-secondary/40 space-y-2'
    case 'mcp':
      return 'mt-2 ml-5 pl-3 border-l border-accent/40 space-y-1'
    default:
      return 'mt-1 ml-4 pl-2 border-l border-base-300/40 space-y-1'
  }
})

// 方法
function toggle() {
  if (hasChildren.value) {
    open.value = !open.value
  }
}

function emitToggle(item) {
  emit('toggle-tool', item || props.item)
}

// 动画方法
function onEnter(el) {
  el.style.height = '0'
  el.style.opacity = '0'
  nextTick(() => {
    el.style.height = el.scrollHeight + 'px'
    el.style.opacity = '1'
  })
}

function onAfterEnter(el) {
  el.style.height = 'auto'
}

function onLeave(el) {
  el.style.height = el.scrollHeight + 'px'
  nextTick(() => {
    el.style.height = '0'
    el.style.opacity = '0'
  })
}

function onAfterLeave(el) {
  el.style.height = 'auto'
  el.style.opacity = '1'
}
</script>

<style scoped>
/* 展开/收起动画 */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  height: 0 !important;
  opacity: 0;
  transform: translateY(-8px);
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  transform: translateY(0);
}

/* 子元素容器样式 */
.children-container {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.children-content {
  transform-origin: top;
  transition: transform 0.3s ease;
}

/* 悬停效果增强 */
.collapsible-item:hover .children-content {
  transform: translateX(2px);
}

/* 层级缩进视觉效果 */
.collapsible-item {
  position: relative;
}

.collapsible-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, transparent, var(--primary), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.collapsible-item:hover::before {
  opacity: 0.3;
}

/* 工具状态指示器动画 */
@keyframes pulse-glow {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(34, 197, 94, 0);
  }
}

.animate-pulse {
  animation: pulse-glow 2s infinite;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .collapsible-item {
    margin-bottom: 0.5rem;
  }

  .children-content {
    margin-left: 1rem;
    padding-left: 0.5rem;
  }
}

/* 深色模式优化 */
@media (prefers-color-scheme: dark) {
  .collapsible-item::before {
    background: linear-gradient(to bottom, transparent, var(--secondary), transparent);
  }
}
</style>