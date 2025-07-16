<template>
  <div>
    <div
      class="flex items-center justify-between bg-base-100/70 backdrop-blur-sm px-4 py-3 rounded-lg cursor-pointer hover:bg-base-100/90 transition-all transform hover:-translate-y-0.5 hover:shadow-md"
      @click="toggle">
      <div class="flex items-center gap-2">
        <svg v-if="hasChildren" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 transition-transform" :class="{ 'rotate-90': open }" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
        <span class="font-medium" :class="levelClass">{{ item.name }}</span>
      </div>
      <!-- Tool 开关 -->
      <template v-if="isTool">
        <label class="inline-flex items-center cursor-pointer">
          <span class="relative">
            <input type="checkbox" class="sr-only" v-model="item.enabled" @click.stop="emitToggle" />
            <div class="w-11 h-6 bg-base-300 rounded-full shadow-inner transition-colors" :class="item.enabled ? 'bg-primary/60' : 'bg-base-300'"></div>
            <div class="dot absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition transform" :class="item.enabled ? 'translate-x-5' : ''"></div>
          </span>
        </label>
      </template>
    </div>

    <!-- 子元素 -->
    <transition name="fade">
      <div v-show="open" class="mt-2 pl-4 border-l border-base-300 space-y-2">
        <CollapsibleItem
          v-for="(child, idx) in item.children"
          :key="idx"
          :item="child"
          :level="childLevel"
          @toggle-tool="emitToggle"
        />
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import CollapsibleItem from './CollapsibleItem.vue'

const props = defineProps({
  item: Object,
  level: String // agent / mcp / tool
})
const emit = defineEmits(['toggle-tool'])

const open = ref(false)
const hasChildren = computed(() => Array.isArray(props.item.children) && props.item.children.length)
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

const isTool = computed(() => Object.prototype.hasOwnProperty.call(props.item, 'enabled'))
function toggle () {
  if (hasChildren.value) open.value = !open.value
}
function emitToggle (item) {
  emit('toggle-tool', item || props.item)
}
const levelClass = computed(() => {
  switch (props.level) {
    case 'agent': return 'text-lg'
    case 'subAgent': return 'text-base'
    case 'mcp': return 'text-base'
    default: return 'text-sm'
  }
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: all 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style> 