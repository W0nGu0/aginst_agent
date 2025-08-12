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
            医疗行业APT攻防推演记录
          </div>

          <!-- 视频控制提示 -->
          <div v-if="!videoLoading && !videoError" class="absolute bottom-2 right-2 bg-black/50 text-white px-2 py-1 rounded text-xs opacity-0 hover:opacity-100 transition-opacity">
            点击播放查看医疗APT攻防演练过程
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
      <h2 class="text-xl font-semibold text-primary">医疗行业APT攻防演练评估报告</h2>
      <p class="text-base-content/70">一、综合评估概览</p>
      <ul class="list-disc list-inside space-y-1 text-base-content/70">
        <li>演练总览：本轮医疗APT攻防演练模拟针对某三甲医院信息系统的高级持续威胁攻击，覆盖HIS系统、PACS影像系统、LIS检验系统等核心医疗业务系统，包含共计12台目标主机及18个关键医疗资产节点。</li>
        <li>防护等级评估：当前医疗信息系统防护能力水平为中等偏上，可应对大部分常见医疗行业攻击场景，但在针对性APT攻击的精准识别与策略响应效率上仍有优化空间。</li>
        <li>风险评级：医疗系统风险等级为高风险，建议加强患者隐私数据保护、医疗设备安全防护及关键业务系统的入侵检测与响应机制。</li>
      </ul>
      <p class="text-base-content/70">二、医疗APT攻防行为统计</p>
      <ul class="list-disc list-inside space-y-1 text-base-content/70">
        <li>攻击策略覆盖数：红队Agent模拟APT组织尝试共计22种医疗行业针对性攻击策略，涵盖医疗邮件钓鱼、医疗设备漏洞利用、HIS系统横向移动、患者数据窃取等多个阶段。</li>
        <li>防御策略响应数：蓝队Agent启用15种医疗专用防御策略，包括医疗网络分段防护、患者数据访问控制、医疗设备异常行为检测、HIPAA合规性监控等。</li>
        <li>攻击路径评估：成功完成医疗APT攻击路径数：5条；被成功阻断路径数：4条；部分中断路径数：3条；涉及患者数据泄露风险路径：2条。</li>
        <li>关键攻击阶段识别：首次医疗系统入侵检测时间：T+18秒；医疗网络横向移动检测覆盖率：78%；患者数据访问企图检测率：89%；医疗设备感染检测率：65%。</li>
      </ul>
      <p class="text-base-content/70">三、医疗安全预警详情</p>
      <ul class="list-disc list-inside space-y-1 text-base-content/70">
        <li>告警事件统计：告警总次数：156次；有效告警（与真实医疗APT攻击对应）：118次；虚警率：24.4%；患者数据相关告警：34次。</li>
        <li>主要告警类型：医疗邮件异常、HIS系统非授权访问、PACS影像数据异常下载、医疗设备通信异常、患者隐私数据访问违规、医疗数据库SQL注入尝试。</li>
      </ul>
      <p class="text-base-content/70">四、医疗安全重点分析建议</p>
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

      <!-- 医疗系统状态 -->
      <div class="glass-panel p-6 space-y-4">
        <h3 class="font-semibold">医疗系统安全状态</h3>
        <p class="text-sm">当前医疗防护等级：<span class="badge badge-success">中等偏上</span></p>
        <p class="text-sm">医疗APT风险等级：<span class="badge badge-error">高风险</span></p>
        <p class="text-sm">患者数据保护状态：<span class="badge badge-info">良好</span></p>
        <p class="text-sm">HIPAA合规状态：<span class="badge badge-warning">需改进</span></p>
      </div>
    </div>

    <!-- 导出按钮 -->
    <div class="text-center">
      <button class="btn btn-primary">生成医疗APT攻防演练 PDF 报告</button>
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

// 红方核心能力维度数据 (与个人中心保持一致 - 5个指标)
const redData = ref([
  { label: '目标识别与情报收集(H)', value: 25 },
  { label: '漏洞利用与攻击执行(I)', value: 22 },
  { label: '横向移动与权限提升(J)', value: 20 },
  { label: '隐蔽性与对抗规避(K)', value: 16 },
  { label: '攻击链完整性(L)', value: 10 }
])

// 红队图表颜色 - 增强区分度
const redChartColors = [
  '#e74c3c', // 鲜红
  '#c0392b', // 深红
  '#f39c12', // 橙色
  '#e67e22', // 深橙
  '#d35400'  // 暗橙
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

// 蓝队图表颜色 - 增强区分度
const blueChartColors = [
  '#3498db', // 蓝色
  '#2980b9', // 深蓝
  '#9b59b6', // 紫色
  '#8e44ad', // 深紫
  '#1abc9c', // 青绿
  '#16a085', // 深青绿
  '#34495e'  // 深灰蓝
]


const metrics = [
  { label: '医疗系统漏洞修复率', value: 78, bar: 'bg-primary' },
  { label: '医疗APT威胁检测精度', value: 85, bar: 'bg-secondary' },
  { label: '患者数据保护率', value: 92, bar: 'bg-accent' },
  { label: 'HIPAA合规性评分', value: 88, bar: 'bg-info' }
]
// 关键指标量化结果数据
const keyIndicators = [
  {
    name: "医疗系统漏洞修复效率",
    result: "78%",
    description: "针对医疗系统已识别漏洞的修复操作响应及时率"
  },
  {
    name: "医疗APT威胁检测精度",
    result: "85%",
    description: "医疗行业APT攻击实际威胁命中率（排除虚警）"
  },
  {
    name: "医疗安全事件响应延迟",
    result: "1.2 分钟",
    description: "从医疗安全告警生成至响应动作执行的平均延迟"
  },
  {
    name: "患者数据保护覆盖度",
    result: "94%",
    description: "患者隐私数据保护措施覆盖关键医疗业务的比例"
  },
  {
    name: "HIPAA合规性评估",
    result: "88%",
    description: "医疗数据处理流程符合HIPAA法规要求的比例"
  },
  {
    name: "医疗设备安全监控率",
    result: "76%",
    description: "医疗设备网络行为监控覆盖率"
  }
];

// 初始化图表
onMounted(() => {
  // 红队评估指标图表 - 扇形图
  new Chart(document.getElementById('redTeamChart'), {
    type: 'pie',
    data: {
      labels: redData.value.map(item => item.label),
      datasets: [{
        data: redData.value.map(item => item.value),
        backgroundColor: redChartColors,
        borderColor: '#ffffff',
        borderWidth: 1,
        hoverOffset: 8,
        hoverBorderWidth: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#ffffff',
          bodyColor: '#ffffff',
          borderColor: '#ffffff',
          borderWidth: 1,
          callbacks: {
            label: function(context) {
              return `${context.label}: ${context.raw}%`;
            }
          }
        }
      },
      elements: {
        arc: {
          borderJoinStyle: 'round'
        }
      }
    }
  });

  // 蓝队评估指标图表 - 扇形图
  new Chart(document.getElementById('blueTeamChart'), {
    type: 'pie',
    data: {
      labels: blueData.value.map(item => item.label),
      datasets: [{
        data: blueData.value.map(item => item.value),
        backgroundColor: blueChartColors,
        borderColor: '#ffffff',
        borderWidth: 1,
        hoverOffset: 8,
        hoverBorderWidth: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#ffffff',
          bodyColor: '#ffffff',
          borderColor: '#ffffff',
          borderWidth: 1,
          callbacks: {
            label: function(context) {
              return `${context.label}: ${context.raw}%`;
            }
          }
        }
      },
      elements: {
        arc: {
          borderJoinStyle: 'round'
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