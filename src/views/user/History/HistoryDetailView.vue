<template>
  <div class="p-6 md:p-10 space-y-6">
    <button class="btn btn-outline btn-sm flex items-center gap-1 mb-4 hover:-translate-y-0.5 transition-transform" @click="goBack">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg> 返回
    </button>

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
        <!-- 红队评估指标 -->
        <div class="bg-base-100 rounded-xl shadow-lg p-6">
          <h3 class="text-xl font-bold text-primary mb-4">红队评估指标</h3>
          <div class="flex flex-col md:flex-row items-center gap-6">
            <div class="w-64 h-64">
              <canvas id="redTeamChart"></canvas>
            </div>
            <div class="flex flex-col gap-2">
              <div v-for="(item, index) in redData" :key="index" class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-sm" :style="`background-color: ${redChartColors[index]}`"></div>
                <span class="text-sm">{{ item.label }}: {{ item.value }}%</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 蓝队评估指标 -->
        <div class="bg-base-100 rounded-xl shadow-lg p-6">
          <h3 class="text-xl font-bold text-secondary mb-4">蓝队评估指标</h3>
          <div class="flex flex-col md:flex-row items-center gap-6">
            <div class="w-64 h-64">
              <canvas id="blueTeamChart"></canvas>
            </div>
            <div class="flex flex-col gap-2">
              <div v-for="(item, index) in blueData" :key="index" class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-sm" :style="`background-color: ${blueChartColors[index]}`"></div>
                <span class="text-sm">{{ item.label }}: {{ item.value }}%</span>
              </div>
            </div>
          </div>
        </div>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Chart from 'chart.js/auto'

const router = useRouter()
function goBack() { router.back() }

// 红方核心能力维度数据
const redData = ref([
  { label: '目标识别与情报收集(H)', value: 22 },
  { label: '漏洞利用与攻击执行(I)', value: 20 },
  { label: '横向移动与权限提升(J)', value: 18 },
  { label: '隐蔽性与对抗规避(K)', value: 15 },
  { label: '攻击链完整性(L)', value: 13 },
  { label: '智能决策与策略演化(M)', value: 12 }
])

// 红队图表颜色
const redChartColors = [
  '#ff6b81', // 浅红
  '#ff4757', // 红色
  '#ff1f3d', // 深红
  '#ff5252', // 鲜红
  '#ff3838', // 亮红
  '#ff4d4d'  // 橙红
]

// 蓝方核心能力维度数据
const blueData = ref([
  { label: '攻击预防能力(A)', value: 18 },
  { label: '防御加固能力(B)', value: 17 },
  { label: '反制能力(C)', value: 14 },
  { label: '事件检测能力(D)', value: 16 },
  { label: '事件响应能力(E)', value: 15 },
  { label: '关联分析能力(F)', value: 10 },
  { label: '安全运营能力(G)', value: 10 }
])

// 蓝队图表颜色
const blueChartColors = [
  '#70a1ff', // 浅蓝
  '#1e90ff', // 道奇蓝
  '#3742fa', // 蓝色
  '#5352ed', // 明亮的蓝色
  '#2e86de', // 天蓝色
  '#0984e3', // 电子蓝
  '#00a8ff'  // 鲜蓝
]

const metrics = [
  { label: '漏洞修复率', value: 76, bar: 'bg-primary' },
  { label: '威胁检测精度', value: 82, bar: 'bg-secondary' }
]

// 初始化图表
onMounted(() => {
  // 红队评估指标图表
  new Chart(document.getElementById('redTeamChart'), {
    type: 'doughnut',
    data: {
      labels: redData.value.map(item => item.label),
      datasets: [{
        data: redData.value.map(item => item.value),
        backgroundColor: redChartColors,
        borderColor: 'transparent',
        borderWidth: 0,
        hoverOffset: 5
      }]
    },
    options: {
      responsive: true,
      cutout: '70%',
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.label}: ${context.raw}%`;
            }
          }
        }
      }
    }
  });

  // 蓝队评估指标图表
  new Chart(document.getElementById('blueTeamChart'), {
    type: 'doughnut',
    data: {
      labels: blueData.value.map(item => item.label),
      datasets: [{
        data: blueData.value.map(item => item.value),
        backgroundColor: blueChartColors,
        borderColor: 'transparent',
        borderWidth: 0,
        hoverOffset: 5
      }]
    },
    options: {
      responsive: true,
      cutout: '70%',
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.label}: ${context.raw}%`;
            }
          }
        }
      }
    }
  });
});
</script> 