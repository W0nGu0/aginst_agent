<template>
  <div class="p-6 md:p-10 space-y-6">
    <button class="btn btn-outline btn-sm flex items-center gap-1 mb-4 hover:-translate-y-0.5 transition-transform" @click="goBack">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg> 返回
    </button>

    <div class="grid md:grid-cols-2 gap-6">
      <!-- 攻防推演记录视频播放区域 -->
      <div class="glass-panel p-4 h-64 md:h-full">
        <div class="w-full h-full relative rounded-md overflow-hidden bg-gradient-to-br from-base-200/50 to-base-300/30">
          <video 
            ref="videoPlayer"
            class="w-full h-full object-cover rounded-md"
            controls
            preload="metadata"
            @loadedmetadata="onVideoLoaded"
            @error="onVideoError"
          >
            <source src="/攻防推演记录.mp4" type="video/mp4">
            <p class="text-base-content/70 text-center p-4">
              您的浏览器不支持视频播放，请升级浏览器或下载视频文件观看。
            </p>
          </video>
          
          <!-- 视频加载状态 -->
          <div v-if="videoLoading" class="absolute inset-0 bg-base-100/80 backdrop-blur-sm flex items-center justify-center">
            <div class="flex flex-col items-center gap-2">
              <div class="loading loading-spinner loading-lg text-primary"></div>
              <span class="text-sm text-base-content/70">正在加载攻防推演记录...</span>
            </div>
          </div>
          
          <!-- 视频加载错误 -->
          <div v-if="videoError" class="absolute inset-0 bg-base-100/80 backdrop-blur-sm flex items-center justify-center">
            <div class="flex flex-col items-center gap-2 text-center p-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <span class="text-sm text-error">视频加载失败</span>
              <span class="text-xs text-base-content/50">请检查视频文件是否存在</span>
              <button class="btn btn-sm btn-outline btn-primary mt-2" @click="retryVideo">
                重新加载
              </button>
            </div>
          </div>
          
          <!-- 视频信息覆盖层 -->
          <div class="absolute top-2 left-2 bg-black/50 text-white px-2 py-1 rounded text-xs">
            APT攻防推演记录
          </div>
          
          <!-- 视频控制提示 -->
          <div v-if="!videoLoading && !videoError" class="absolute bottom-2 right-2 bg-black/50 text-white px-2 py-1 rounded text-xs opacity-0 hover:opacity-100 transition-opacity">
            点击播放查看完整演练过程
          </div>
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
      <p class="text-base-content/70">一、综合评估概览</p>
      <ul class="list-disc list-inside space-y-1 text-base-content/70">
        <li>演练总览：本轮攻防演练覆盖企业级内网环境，包含共计 8 台目标主机及 12 个关键资产节点。</li>
        <li>防护等级评估：当前系统防护能力水平为中等，可应对大部分常见攻击场景，但在精准识别与策略响应效率上仍有优化空间。</li>
        <li>风险评级：系统风险等级为高风险，建议加强关键节点的入侵检测与响应机制。</li>
      </ul>
      <p class="text-base-content/70">二、攻防行为统计</p>
      <ul class="list-disc list-inside space-y-1 text-base-content/70">
        <li>攻击策略覆盖数：红队 Agent 尝试共计 18 种攻击策略，涵盖信息收集、漏洞利用、横向移动、持久化建立等多个阶段。</li>
        <li>防御策略响应数：蓝队 Agent 启用 12 种防御策略，包括防火墙动态更新、行为异常检测、访问控制规则自动下发等。</li>
        <li>攻击路径评估:成功完成攻击路径数:4 条; 被成功阻断路径数:3 条; 部分中断路径数:2 条。</li>
        <li>关键攻击阶段识别：首次入侵检测时间:T+13秒; 横向移动检测覆盖率:85%; 持久化企图检测率:71%。</li>

      </ul>
      <p class="text-base-content/70">三、预警详情</p>
      <ul class="list-disc list-inside space-y-1 text-base-content/70">
        <li>告警事件分:告警总次数:126 次; 有效告警(与真实攻击对应):89 次; 虚警率:29.4%。</li>
        <li>主要告警类型:异常端口扫描、非授权访问、未知进程执行、工具签名命中(Metasploit/Nmap)。</li>
      </ul>
      <p class="text-base-content/70">四、重点分析建议</p>
      <ul class="list-disc list-inside space-y-1 text-base-content/70">
        <li>攻击链处置分析：在“初始访问—漏洞利用—横向移动”路径中，防御 Agent 在横向移动阶段表现出较强响应，但对初始入侵侦测延迟较长。</li>
        <li>防御策略优化建议：增强防护策略自动演化能力，根据攻击演化轨迹自适应调整规则集。引入基于图谱节点权重的防御资源动态分配算法。</li>
        <li>日志与告警改进建议：减少重复与低优先级告警条目，提升 SOC 处理效率。提高告警与攻击路径的对应精度，建议优化行为图谱与日志事件映射策略。</li>
      </ul>
      <p class="text-base-content/70">五、关键指标量化结果（节选）</p>
<table class="w-full border-collapse mt-2 mb-4">
  <thead>
    <tr class="bg-base-200">
      <th class="border border-base-300 p-3 text-left text-base-content/80">指标名称</th>
      <th class="border border-base-300 p-3 text-left text-base-content/80">本次评估</th>
      <th class="border border-base-300 p-3 text-left text-base-content/80">评估说明</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="(item, index) in keyIndicators" :key="index" class="hover:bg-base-100">
      <td class="border border-base-300 p-3 text-base-content/70">{{ item.name }}</td>
      <td class="border border-base-300 p-3 text-base-content/70 font-medium">{{ item.result }}</td>
      <td class="border border-base-300 p-3 text-base-content/70">{{ item.description }}</td>
    </tr>
  </tbody>
</table>

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

// 视频相关状态
const videoPlayer = ref(null)
const videoLoading = ref(true)
const videoError = ref(false)

// 视频事件处理
const onVideoLoaded = () => {
  console.log('攻防推演记录视频加载完成')
  videoLoading.value = false
  videoError.value = false
}

const onVideoError = (event) => {
  console.error('攻防推演记录视频加载失败:', event)
  videoLoading.value = false
  videoError.value = true
}

const retryVideo = () => {
  if (videoPlayer.value) {
    videoLoading.value = true
    videoError.value = false
    videoPlayer.value.load()
  }
}

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
// 关键指标量化结果数据
const keyIndicators = [
  {
    name: "漏洞修复效率",
    result: "76%",
    description: "针对已识别漏洞的修复操作响应及时率"
  },
  {
    name: "威胁检测精度",
    result: "82%",
    description: "实际威胁命中率（排除虚警）"
  },
  {
    name: "响应延迟",
    result: "1.8 分钟",
    description: "从告警生成至响应动作执行的平均延迟"
  },
  {
    name: "图谱覆盖度",
    result: "91%",
    description: "行为图谱节点覆盖演练关键行为的比例"
  },
  {
    name: "可解释性指数",
    result: "96%",
    description: "每个评分项可追溯至具体日志与图谱节点的占比"
  }
];

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

<style scoped>
/* 视频播放器样式优化 */
video {
  background-color: transparent;
}

video::-webkit-media-controls-panel {
  background-color: rgba(0, 0, 0, 0.8);
}

video::-webkit-media-controls-play-button,
video::-webkit-media-controls-pause-button {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

video::-webkit-media-controls-timeline {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

video::-webkit-media-controls-current-time-display,
video::-webkit-media-controls-time-remaining-display {
  color: white;
  text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.5);
}

/* 玻璃面板样式 */
.glass-panel {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

/* 加载动画优化 */
.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 悬停效果 */
.glass-panel:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  transition: all 0.3s ease;
}
</style> 