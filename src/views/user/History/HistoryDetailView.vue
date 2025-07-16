<template>
  <div class="p-6 md:p-10 space-y-6">
    <button class="btn btn-ghost mb-4" @click="goBack">← 返回</button>

    <div class="grid md:grid-cols-2 gap-6">
      <!-- 视频占位 -->
      <div class="glass-panel p-4 flex items-center justify-center h-64 md:h-full">
        <div class="w-full h-full bg-base-300 flex items-center justify-center relative rounded-md">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-base-content/50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-6.518-3.759A1 1 0 007 8.259v7.482a1 1 0 001.234.97l6.518-1.87A1 1 0 0016 13.87V10.13a1 1 0 00-1.248-.962z" />
          </svg>
        </div>
      </div>

      <!-- 右侧圆环图 -->
      <div class="space-y-6">
        <DonutCard title="红队评估指标" color="primary" :data="redData" />
        <DonutCard title="蓝队评估指标" color="secondary" :data="blueData" />
      </div>
    </div>

    <!-- 报告描述 -->
    <div class="glass-panel p-6 space-y-4">
      <h2 class="text-xl font-semibold text-primary">AI 攻防演练评估报告</h2>
      <p class="text-base-content/70">根据本次攻防演练的数据分析，系统整体安全防护能力处于中等水平。红队在渗透测试中展现出较强的攻击能力，成功发现多个关键漏洞。蓝队的防御响应较为及时，但在威胁检测准确性上仍有提升空间。建议加强以下几方面：</p>
      <ul class="list-disc list-inside space-y-1 text-base-content/70">
        <li>提升漏洞修复效率，优化修复流程</li>
        <li>增强威胁检测准确性，降低误报率</li>
        <li>完善应急响应机制，提高防御效率</li>
      </ul>
    </div>

    <!-- 指标与系统状态 -->
    <div class="grid md:grid-cols-2 gap-6">
      <!-- 关键指标 -->
      <div class="glass-panel p-6 space-y-4">
        <h3 class="font-semibold">关键指标</h3>
        <div v-for="metric in metrics" :key="metric.label">
          <div class="flex justify-between text-sm mb-1">
            <span>{{ metric.label }}</span>
            <span>{{ metric.value }}%</span>
          </div>
          <div class="w-full bg-base-300 rounded">
            <div class="h-2 rounded" :class="metric.bar" :style="`width:${metric.value}%`"></div>
          </div>
        </div>
      </div>

      <!-- 系统状态 -->
      <div class="glass-panel p-6 space-y-4">
        <h3 class="font-semibold">系统状态</h3>
        <p class="text-sm">当前防护等级：<span class="badge badge-success">中等</span></p>
        <p class="text-sm">风险等级：<span class="badge badge-error">高风险</span></p>
      </div>
    </div>

    <!-- 导出按钮 -->
    <div class="text-center">
      <button class="btn btn-primary">生成 PDF 报告</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import DonutCard from './components/DonutCard.vue'

const router = useRouter()
function goBack() { router.back() }

const redData = ref([
  { label: '攻击战术多样性', value: 75 },
  { label: '漏洞利用成功率', value: 68 },
  { label: '路径优化能力', value: 92 }
])
const blueData = ref([
  { label: '防御响应时间', value: 70 },
  { label: '攻击阻止成功率', value: 80 },
  { label: '漏洞补漏率', value: 88 }
])

const metrics = [
  { label: '漏洞修复率', value: 76, bar: 'bg-primary' },
  { label: '威胁检测精度', value: 82, bar: 'bg-secondary' }
]
</script> 