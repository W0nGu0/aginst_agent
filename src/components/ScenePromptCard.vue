<template>
  <div class="scene-prompt-item flex-shrink-0 w-64 h-32 border border-base-300/30 rounded-lg p-4 bg-base-100 hover:border-primary/50 transition-all cursor-pointer">
    <div 
      :class="{
        'text-primary/70': prompt.type === 'network',
        'text-secondary/70': prompt.type === 'web',
        'text-accent/70': prompt.type === 'iot',
        'text-primary/70': prompt.type === 'social',
        'text-secondary/70': prompt.type === 'wireless',
        'text-accent/70': prompt.type === 'cloud'
      }" 
      class="text-xs mb-2"
    >
      {{ getTypeLabel(prompt.type) }}
    </div>
    <div class="text-base-content font-medium">{{ prompt.title }}</div>
  </div>
</template>

<script setup>
defineProps({
  prompt: {
    type: Object,
    required: true
  }
})

function getTypeLabel(type) {
  const types = {
    'network': '网络设施',
    'web': 'Web应用',
    'iot': '物联网',
    'social': '社会工程',
    'wireless': '无线网络',
    'cloud': '云原生'
  }
  
  return types[type] || type
}
</script> 