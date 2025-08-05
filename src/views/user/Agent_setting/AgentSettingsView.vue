<template>
  <div class="settings-bg relative overflow-hidden min-h-screen">
    <!-- 动态背景特效 -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <!-- 浮动粒子 -->
      <div class="floating-particles">
        <div v-for="i in 20" :key="i" class="particle" :style="getParticleStyle(i)"></div>
      </div>

      <!-- 网格线条 -->
      <div class="grid-lines">
        <div class="grid-line horizontal" v-for="i in 10" :key="'h' + i" :style="{ top: i * 10 + '%' }"></div>
        <div class="grid-line vertical" v-for="i in 10" :key="'v' + i" :style="{ left: i * 10 + '%' }"></div>
      </div>

      <!-- 脉冲波纹 -->
      <div class="pulse-rings">
        <div class="pulse-ring" v-for="i in 3" :key="i" :style="getPulseStyle(i)"></div>
      </div>

      <!-- 数据流 -->
      <div class="data-streams">
        <div class="data-stream" v-for="i in 5" :key="i" :style="getStreamStyle(i)"></div>
      </div>
    </div>

    <!-- 主视图 -->
    <div v-if="!selectedAgent" class="p-6 md:p-10 relative z-10">
      <!-- 页面标题 -->
      <div class="text-center mb-12">
        <h1 class="text-4xl md:text-5xl font-bold mb-6 text-gradient animate-gradient">
          Agent 功能配置中心
        </h1>

        <!-- 优化的说明部分 -->
        <div class="max-w-4xl mx-auto">
          <div class="glass-panel p-8 mb-8 relative overflow-hidden">
            <!-- 装饰性背景 -->
            <div class="absolute inset-0 bg-gradient-to-r from-primary/5 via-secondary/5 to-accent/5"></div>
            <div class="relative z-10">
              <div class="flex items-center justify-center mb-4">
                <div class="w-12 h-12 bg-gradient-to-r from-primary to-secondary rounded-full flex items-center justify-center mr-4">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <h2 class="text-2xl font-semibold text-gradient">智能配置管理</h2>
              </div>
              <p class="text-base-content/80 text-lg leading-relaxed mb-4">
                通过精细化的工具开关控制，您可以为每个 AI Agent 定制专属的能力组合，
                以适应不同的攻防推演场景需求。
              </p>
              <div class="flex flex-wrap justify-center gap-4 text-sm">
                <span class="badge badge-primary badge-outline">🎯 场景定制</span>
                <span class="badge badge-secondary badge-outline">⚡ 实时配置</span>
                <span class="badge badge-accent badge-outline">🔧 精细控制</span>
                <span class="badge badge-info badge-outline">📊 性能优化</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Agent 卡片网格 -->
      <div class="max-w-6xl mx-auto">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <AgentCard
            v-for="(agent, index) in agents"
            :key="index"
            :agent="agent"
            :index="index"
            @select="selectAgent"
          />
        </div>
      </div>
    </div>

    <!-- 详细视图 -->
    <AgentDetailView
      v-if="selectedAgent"
      :agent="selectedAgent"
      :agent-index="selectedAgentIndex"
      @toggle-tool="toggleTool"
      @back="goBack"
    />
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import AgentCard from './components/AgentCard.vue'
import AgentDetailView from './components/AgentDetailView.vue'

// 初步数据结构（后续可从后端 / 配置加载）
const agents = reactive([
  {
    name: '场景生成 Agent',
    children: [
      {
        name: '场景服务',
        children: [
          { name: '列出现有场景模板工具', enabled: true },
          { name: '获取模板详情工具', enabled: true },
          { name: '根据模板创建场景工具', enabled: true },
          { name: '销毁场景实例工具', enabled: true },
          { name: '列出正在运行场景工具', enabled: true }
        ]
      },
      {
        name: '容器服务',
        children: [
          { name: '启动容器组工具', enabled: true },
          { name: '移除容器工具', enabled: true },
          { name: '创建虚拟网络工具', enabled: true },
          { name: '清理虚拟网络工具', enabled: true }
        ]
      }
    ]
  },
  {
    name: '攻击 Agent',
    children: [
      {
        name: '攻击服务',
        children: [
          { name: '端口扫描工具', enabled: true },
          { name: 'URL抓取工具', enabled: true },
          { name: '钓鱼邮件生成工具', enabled: false },
          { name: '邮箱泄露查询工具', enabled: true },
          { name: '凭据收集模拟工具', enabled: false },
          { name: '漏洞搜索工具', enabled: true },
          { name: '漏洞利用执行工具', enabled: true },
          { name: '远程命令执行工具', enabled: true },
          { name: '网络信息收集工具', enabled: true },
          { name: '恶意文档生成工具', enabled: false },
          { name: '性勒索邮件生成工具', enabled: false },
          { name: '亲和聊天脚本工具', enabled: false },
          { name: '虚假Offer邮件生成工具', enabled: false }
        ]
      }
    ]
  },
  {
    name: '防御 Agent',
    children: [
      {
        name: '漏洞修复服务',
        children: [
          { name: '漏洞扫描工具', enabled: true },
          { name: '自动打补丁工具', enabled: true },
          { name: '修改配置文件工具', enabled: true },
          { name: '重启服务工具', enabled: false }
        ]
      },
      {
        name: '威胁阻断服务',
        children: [
          { name: '防火墙阻断恶意流量工具', enabled: true },
          { name: '隔离受害主机工具', enabled: true },
          { name: '终止主机恶意进程工具', enabled: true },
          { name: '隔离恶意文件工具', enabled: false }
        ]
      },
      {
        name: '攻击溯源服务',
        children: [
          { name: 'ip威胁查询工具', enabled: true },
          { name: '哈希文件威胁查询工具', enabled: true },
          { name: '检测恶意通信和数据外传工具', enabled: true },
          { name: '检测恶意进程工具', enabled: true },
          { name: '检测恶意文件工具', enabled: true },
          { name: '检测恶意网络流量工具', enabled: true }
        ]
      }
    ]
  },
  {
    name: '评估 Agent',
    children: [
      {
        name: '评估服务',
        children: [
              { name: '数据获取工具', enabled: true },
              { name: '场景拓扑获取工具', enabled: true },
              { name: '攻击量化指标计算工具', enabled: true },
              { name: '防御量化指标计算工具', enabled: true },
              { name: '报告生成工具', enabled: true },
              { name: '长期人员画像更新工具', enabled: true },
              { name: '长期攻击agent性能更新工具', enabled: true },
              { name: '长期防御agent性能更新工具', enabled: true }
        ]
      }
    ]
  }
])

// 选中的Agent状态
const selectedAgent = ref(null)
const selectedAgentIndex = ref(-1)

// 选择Agent
function selectAgent(agent, index) {
  selectedAgent.value = agent
  selectedAgentIndex.value = index
}

// 返回主视图
function goBack() {
  selectedAgent.value = null
  selectedAgentIndex.value = -1
}

// 动态背景特效
function getParticleStyle(index) {
  const size = Math.random() * 4 + 2
  const duration = Math.random() * 20 + 10
  const delay = Math.random() * 5
  return {
    width: size + 'px',
    height: size + 'px',
    left: Math.random() * 100 + '%',
    top: Math.random() * 100 + '%',
    animationDuration: duration + 's',
    animationDelay: delay + 's'
  }
}

function getPulseStyle(index) {
  const size = 100 + index * 50
  const duration = 3 + index * 0.5
  const delay = index * 0.8
  return {
    width: size + 'px',
    height: size + 'px',
    left: '50%',
    top: '50%',
    transform: 'translate(-50%, -50%)',
    animationDuration: duration + 's',
    animationDelay: delay + 's'
  }
}

function getStreamStyle(index) {
  const duration = Math.random() * 3 + 2
  const delay = Math.random() * 2
  const startX = Math.random() * 100
  return {
    left: startX + '%',
    animationDuration: duration + 's',
    animationDelay: delay + 's'
  }
}

// 切换 Tool 开关
function toggleTool (toolItem) {
  if (Object.prototype.hasOwnProperty.call(toolItem, 'enabled')) {
    toolItem.enabled = !toolItem.enabled
  }
}
</script>

<style scoped>
/* 动态背景特效 */
.floating-particles {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
}

.particle {
  position: absolute;
  background: radial-gradient(circle, rgba(var(--primary-rgb), 0.6) 0%, transparent 70%);
  border-radius: 50%;
  animation: float infinite ease-in-out;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0.3;
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
    opacity: 0.8;
  }
}

.grid-lines {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
}

.grid-line {
  position: absolute;
  background: linear-gradient(90deg, transparent, rgba(var(--primary-rgb), 0.1), transparent);
  animation: gridPulse 4s ease-in-out infinite;
}

.grid-line.horizontal {
  width: 100%;
  height: 1px;
}

.grid-line.vertical {
  width: 1px;
  height: 100%;
  background: linear-gradient(0deg, transparent, rgba(var(--primary-rgb), 0.1), transparent);
}

@keyframes gridPulse {
  0%, 100% {
    opacity: 0.1;
  }
  50% {
    opacity: 0.3;
  }
}

.pulse-rings {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
}

.pulse-ring {
  position: absolute;
  border: 2px solid rgba(var(--primary-rgb), 0.3);
  border-radius: 50%;
  animation: pulse infinite ease-out;
}

@keyframes pulse {
  0% {
    transform: translate(-50%, -50%) scale(0.8);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(2);
    opacity: 0;
  }
}

.data-streams {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
}

.data-stream {
  position: absolute;
  top: 0;
  width: 2px;
  height: 100%;
  background: linear-gradient(to bottom,
    transparent 0%,
    rgba(var(--secondary-rgb), 0.8) 50%,
    transparent 100%);
  animation: stream infinite linear;
}

@keyframes stream {
  0% {
    transform: translateY(-100%);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(100vh);
    opacity: 0;
  }
}
/* 背景星空特效 */
.settings-bg::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-radial-gradient(circle at 30% 40%, rgba(255,255,255,0.05) 0 1px, transparent 2px 100px),
              repeating-radial-gradient(circle at 70% 60%, rgba(255,255,255,0.04) 0 1px, transparent 2px 120px);
  animation: drift 60s linear infinite;
}
@keyframes drift {
  0% { transform: translateY(0); }
  100% { transform: translateY(-50%); }
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.animate-gradient {
  background-size: 200% 200%;
  animation: gradientShift 6s ease infinite;
}
</style> 