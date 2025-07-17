<template>
   <div class="glass-panel p-6">
     <h3 class="font-semibold mb-4" :class="`text-${color}`">{{ title }}</h3>
     <div class="flex items-center gap-6 flex-wrap">
       <svg viewBox="0 0 42 42" class="w-48 h-48 rotate-[-90deg]">
         <circle r="15.915" cx="21" cy="21" fill="transparent" stroke-width="6" class="text-base-300" stroke="currentColor" />
         <circle
           v-for="(d,idx) in data"
           :key="idx"
           r="15.915" cx="21" cy="21" fill="transparent" stroke-width="6"
           :stroke-dasharray="dashArray(d.value)"
           :stroke-dashoffset="dashOffset(idx)"
           :stroke="segmentColor(idx)" />
       </svg>
       <ul class="space-y-1">
         <li v-for="(d,idx) in data" :key="idx" class="flex items-center gap-2 text-sm text-base-content/80">
           <span class="inline-block w-3 h-3 rounded" :style="`background:${segmentColor(idx)}`"></span>{{ d.label }}：{{ d.value }}%
         </li>
       </ul>
     </div>
   </div>
 </template>
 
 <script setup>
 import { computed } from 'vue'
 const props = defineProps({ title: String, data: Array, color: String })
 const circumference = 2 * Math.PI * 15.915
 const total = 100 // 以百分比
 function dashArray(val) {
   return `${circumference * val / total} ${circumference}`
 }
 function dashOffset(index) {
   const prior = props.data.slice(0, index).reduce((a, b) => a + b.value, 0)
   return circumference * (1 - prior / total)
 }
 function segmentColor(i) {
   const primary = ['#fb7185', '#f43f5e', '#e11d48', '#be123c']
   const secondary = ['#60a5fa', '#3b82f6', '#2563eb', '#1d4ed8']
   const p = props.color === 'primary' ? primary : secondary
   return p[i % p.length]
 }
 </script> 