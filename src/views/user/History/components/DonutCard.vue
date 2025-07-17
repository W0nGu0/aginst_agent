<template>
  <div class="bg-base-100/30 rounded-xl p-6">
    <h3 class="font-semibold mb-6" :class="`text-${color}`">{{ title }}</h3>
    <div class="flex flex-col md:flex-row items-start gap-8">
      <!-- 环状图 -->
      <div class="relative w-48 h-48">
        <svg viewBox="0 0 100 100" class="w-full h-full transform -rotate-90">
          <!-- 背景圆环 -->
          <circle 
            cx="50" 
            cy="50" 
            r="40" 
            fill="transparent" 
            stroke="#1e293b" 
            stroke-width="12"
          />
          
          <!-- 数据圆环段 -->
          <circle 
            v-for="(item, index) in processedData" 
            :key="index"
            cx="50" 
            cy="50" 
            r="40" 
            fill="transparent" 
            :stroke="getSegmentColor(index)" 
            stroke-width="12"
            :stroke-dasharray="`${item.dashLength} ${circumference}`"
            :stroke-dashoffset="item.dashOffset"
          />
        </svg>
        
        <!-- 中心空白 -->
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="w-24 h-24 rounded-full bg-base-100"></div>
        </div>
      </div>
      
      <!-- 图例 -->
      <div class="flex flex-col gap-3">
        <div 
          v-for="(item, index) in data" 
          :key="index"
          class="flex items-center gap-2"
        >
          <span 
            class="inline-block w-3 h-3 rounded-sm" 
            :style="`background-color: ${getSegmentColor(index)}`"
          ></span>
          <span class="text-sm text-base-content/90">{{ item.label }}: {{ item.value }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  title: String,
  data: Array,
  color: String
});

// 圆环周长
const circumference = computed(() => 2 * Math.PI * 40);

// 处理数据，计算每个段的dash长度和偏移量
const processedData = computed(() => {
  const total = props.data.reduce((sum, item) => sum + item.value, 0);
  let currentOffset = 0;
  
  return props.data.map((item, index) => {
    // 计算当前段的长度
    const dashLength = (item.value / total) * circumference.value;
    
    // 计算当前段的偏移量
    const dashOffset = -currentOffset;
    currentOffset += dashLength;
    
    return {
      ...item,
      dashLength,
      dashOffset
    };
  });
});

// 获取段的颜色
function getSegmentColor(index) {
  // 红队颜色
  const primaryColors = [
    '#ff6b81', // 浅红
    '#ff4757', // 红色
    '#ff1f3d', // 深红
    '#ff5252', // 鲜红
    '#ff3838', // 亮红
    '#ff4d4d'  // 橙红
  ];
  
  // 蓝队颜色
  const secondaryColors = [
    '#70a1ff', // 浅蓝
    '#1e90ff', // 道奇蓝
    '#3742fa', // 蓝色
    '#5352ed', // 明亮的蓝色
    '#2e86de', // 天蓝色
    '#0984e3', // 电子蓝
    '#00a8ff'  // 鲜蓝
  ];
  
  const colors = props.color === 'primary' ? primaryColors : secondaryColors;
  return colors[index % colors.length];
}
</script>