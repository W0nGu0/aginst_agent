<template>
  <div class="glass-panel p-6">
    <h3 class="font-semibold mb-4" :class="`text-${color}`">{{ title }}</h3>
    <svg viewBox="0 0 32 32" class="w-40 h-40 mx-auto rotate-[-90deg]">
      <circle v-for="(d,idx) in data" :key="idx" r="14" cx="16" cy="16" fill="transparent" stroke-width="6" :stroke-dasharray="circumference" :stroke-dashoffset="offset(idx)" :stroke="segmentColor(idx)" stroke-linecap="round" />
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ title: String, data: Array, color: String })
const total = computed(()=> props.data.reduce((a,b)=> a+b.value,0))
const circumference = 2*Math.PI*14
function offset(index){
  const prior = props.data.slice(0,index).reduce((a,b)=>a+b.value,0)
  return circumference * (1 - prior/ total.value)
}
function segmentColor(i){
  const palette = props.color==='primary' ? ['#fca5a5','#f87171','#ef4444'] : ['#93c5fd','#60a5fa','#3b82f6']
  return palette[i % palette.length]
}
</script> 