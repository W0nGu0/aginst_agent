<template>
  <div class="home-view">
    <!-- 高科技图形展示区 -->
    <div class="relative h-96 mb-20 rounded-2xl overflow-hidden cyber-bg">
      <div class="absolute inset-0 flex items-center justify-center">
        <div class="cyber-graphic">
          <div class="cyber-circle animate-pulse-slow"></div>
          <div class="cyber-grid"></div>
          <div class="cyber-nodes"></div>
          <div class="pulse-waves"></div>
        </div>

        <div class="z-10 text-center max-w-3xl px-4">
          <h1 class="text-4xl md:text-5xl font-bold mb-6 text-gradient leading-tight">
            AI 驱动的动态攻防推演靶场
          </h1>
          <p class="text-base-content/80 text-lg max-w-2xl mx-auto">
            通过智能AI创建逼真攻防场景，训练与提升网络安全技能，体验真实环境下的攻防对抗
          </p>
          <div class="mt-8 flex justify-center gap-4">
            <button class="btn btn-primary">立即开始</button>
            <button class="btn btn-outline">了解更多</button>
          </div>
        </div>
      </div>

      <!-- 底部装饰 -->
      <div class="absolute bottom-0 w-full h-12 bg-gradient-to-t from-base-200 to-transparent"></div>
    </div>

    <!-- 动态滚动提示词胶卷 -->
    <div class="mb-20 relative">
      <div class="absolute left-0 top-0 w-32 h-full bg-gradient-to-r from-base-200 to-transparent z-10"></div>
      <div class="absolute right-0 top-0 w-32 h-full bg-gradient-to-l from-base-200 to-transparent z-10"></div>

      <h2 class="text-2xl font-bold mb-8 text-base-content flex items-center">
        <span class="text-primary mr-2">#</span> 热门场景提示
        <span class="ml-2 badge badge-glowing">智能推荐</span>
      </h2>

      <div class="scene-prompts-container overflow-hidden">
        <div class="scene-prompts flex space-x-4" :style="scrollStyle" ref="scrollContainer">
          <ScenePromptCard v-for="(prompt, index) in displayPrompts" :key="index" :prompt="prompt"
            @click="navigateToSceneDetail" />
        </div>
      </div>
    </div>

    <!-- 场景生成输入区 -->
    <div class="max-w-4xl mx-auto">
      <h2 class="text-2xl font-bold mb-8 text-base-content flex items-center">
        <span class="text-primary mr-2">#</span> 自定义场景生成
      </h2>

      <div class="glass-panel p-8">
        <!-- 快速选择区域 -->
        <div class="mb-6">
          <h3 class="text-lg font-semibold mb-4 text-base-content">快速场景配置</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- 攻击类型选择 -->
            <div>
              <label class="block text-sm font-medium text-base-content/80 mb-2">攻击类型</label>
              <select v-model="selectedAttackType"
                class="w-full bg-base-300/50 text-base-content rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary/50 border border-white/10">
                <option value="">请选择攻击类型</option>
                <option value="apt">APT高级持续威胁</option>
                <option value="phishing">钓鱼攻击</option>
                <option value="ransomware">勒索软件攻击</option>
                <option value="insider_threat">内部威胁</option>
              </select>
            </div>

            <!-- 业务场景选择 -->
            <div>
              <label class="block text-sm font-medium text-base-content/80 mb-2">业务场景</label>
              <select v-model="selectedBusinessScenario"
                class="w-full bg-base-300/50 text-base-content rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-primary/50 border border-white/10">
                <option value="">请选择业务场景</option>
                <option value="healthcare">医疗机构</option>
                <option value="finance">金融机构</option>
                <option value="education">教育机构</option>
                <option value="manufacturing">制造企业</option>
              </select>
            </div>
          </div>
        </div>

        <!-- 自然语言描述区域 -->
        <div class="relative">
          <label class="block text-sm font-medium text-base-content/80 mb-2">场景描述（可选）</label>
          <textarea v-model="scenePrompt"
            class="w-full h-32 bg-base-300/50 text-base-content rounded-lg p-4 focus:outline-none focus:ring-2 focus:ring-primary/50 placeholder-base-content/40 border border-white/10"
            :placeholder="getPlaceholderText()"></textarea>

          <div class="mt-4 flex justify-between items-center">
            <div class="text-sm text-base-content/60">
              <span v-if="selectedAttackType && selectedBusinessScenario">
                将生成 {{ getAttackTypeName() }} 的 {{ getBusinessScenarioName() }} 场景
              </span>
              <span v-else>请选择攻击类型和业务场景，或直接描述您的需求</span>
            </div>

            <button @click="generateScene" class="btn btn-primary"
              :disabled="isLoading || (!scenePrompt.trim() && (!selectedAttackType || !selectedBusinessScenario))">
              <span>{{ isLoading ? '生成中' : '场景生成' }}</span>
              <svg v-if="!isLoading" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-2" fill="none"
                viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
              <span v-else class="loading-dots">...</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 功能介绍区 -->
      <div class="mt-20">
        <h2 class="text-2xl font-bold mb-8 text-base-content flex items-center">
          <span class="text-primary mr-2">#</span> 平台特色
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="glass-panel p-6">
            <div class="text-primary text-3xl mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24"
                stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold mb-2">可视化网络拓扑</h3>
            <p class="text-base-content/70">通过直观的拖放式界面，轻松设计和构建复杂的网络拓扑结构</p>
          </div>

          <div class="glass-panel p-6">
            <div class="text-secondary text-3xl mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24"
                stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold mb-2">实时攻防演练</h3>
            <p class="text-base-content/70">模拟真实网络环境中的攻击与防御过程，提供沉浸式学习体验</p>
          </div>

          <div class="glass-panel p-6">
            <div class="text-accent text-3xl mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24"
                stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold mb-2">AI驱动推荐</h3>
            <p class="text-base-content/70">智能分析您的技能水平和学习需求，推荐个性化的场景和挑战</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../../../stores/app'
import ScenePromptCard from '../components/ScenePromptCard.vue'

const router = useRouter()
const appStore = useAppStore()
const scenePrompt = ref('')
const isLoading = ref(false)
const scrollContainer = ref(null)
const scrollPosition = ref(0)
const scrollSpeed = 0.5 // 滚动速度，数值越大滚动越快
const scrollInterval = ref(null)

// 新增：场景配置选项
const selectedAttackType = ref('')
const selectedBusinessScenario = ref('')

// 攻击类型映射
const attackTypeMap = {
  'apt': 'APT高级持续威胁',
  'phishing': '钓鱼攻击',
  'ransomware': '勒索软件攻击',
  'insider_threat': '内部威胁'
}

// 业务场景映射
const businessScenarioMap = {
  'healthcare': '医疗机构',
  'finance': '金融机构',
  'education': '教育机构',
  'manufacturing': '制造企业'
}

// 场景提示 - 添加更多卡片
const scenePrompts = [
  {
    type: 'network',
    title: '企业内网渗透场景：多层防御网络架构下的横向移动与权限提升'
  },
  {
    type: 'web',
    title: '电商平台API漏洞：OWASP Top 10漏洞利用与防护策略'
  },
  {
    type: 'iot',
    title: '智能家居设备攻防：固件逆向与安全通信协议分析'
  },
  {
    type: 'social',
    title: '目标定向钓鱼攻击：企业员工社会工程学攻防演练'
  },
  {
    type: 'wireless',
    title: '公共WiFi中间人攻击：无线网络流量监听与安全加密通信'
  },
  {
    type: 'cloud',
    title: 'Kubernetes集群攻防：容器逃逸与权限边界突破演练'
  },
  {
    type: 'malware',
    title: '勒索软件防御：恶意软件行为分析与应急响应策略'
  },
  {
    type: 'web',
    title: 'Web应用渗透测试：API安全与业务逻辑漏洞挖掘'
  },
  {
    type: 'network',
    title: '内网域渗透：活动目录权限提升与横向移动技术'
  },
  {
    type: 'cloud',
    title: '云环境安全：AWS/Azure资源配置错误利用与防护'
  },
  {
    type: 'iot',
    title: '工业控制系统安全：SCADA系统漏洞利用与防护'
  },
  {
    type: 'social',
    title: '供应链攻击：第三方依赖风险评估与防御策略'
  }
]

// 为了实现无缝滚动，复制一份卡片
const displayPrompts = computed(() => {
  return [...scenePrompts, ...scenePrompts]
})

// 滚动样式
const scrollStyle = computed(() => {
  return {
    transform: `translateX(${-scrollPosition.value}px)`,
    // 不使用transition，让动画更加平滑
  }
})

// 启动滚动
function startScroll() {
  if (scrollInterval.value) return

  // 计算一组卡片的总宽度
  const cardWidth = 336 // 卡片宽度(320) + 间距(16)
  const totalWidth = scenePrompts.length * cardWidth

  // 设置初始位置为负值，这样卡片会从右侧进入
  if (scrollPosition.value === 0) {
    // 只在初始化时设置，避免重置滚动时跳回
    scrollPosition.value = -cardWidth * 2 // 从右侧开始，显示2个卡片的宽度
  }

  scrollInterval.value = setInterval(() => {
    // 增加位置，实现从右向左滚动
    scrollPosition.value += scrollSpeed

    // 当滚动到第一组卡片的末尾时，重置位置
    if (scrollPosition.value >= totalWidth) {
      // 无缝循环：当第一组卡片滚完时，立即跳回开始位置
      scrollPosition.value = 0
    }
  }, 16) // 约60fps，保持滚动平滑
}

// 暂停滚动
function pauseScroll() {
  if (scrollInterval.value) {
    clearInterval(scrollInterval.value)
    scrollInterval.value = null
  }
}

// 鼠标悬停时暂停滚动
function handleMouseEnter() {
  pauseScroll()
}

// 鼠标离开时恢复滚动
function handleMouseLeave() {
  startScroll()
}

// 组件挂载时启动滚动
onMounted(() => {
  startScroll()

  // 添加鼠标事件监听
  if (scrollContainer.value) {
    scrollContainer.value.addEventListener('mouseenter', handleMouseEnter)
    scrollContainer.value.addEventListener('mouseleave', handleMouseLeave)
  }
})

// 组件卸载前清除定时器和事件监听
onBeforeUnmount(() => {
  pauseScroll()

  if (scrollContainer.value) {
    scrollContainer.value.removeEventListener('mouseenter', handleMouseEnter)
    scrollContainer.value.removeEventListener('mouseleave', handleMouseLeave)
  }
})

// 跳转到场景详情页
function navigateToSceneDetail() {
  isLoading.value = true
  // 模拟加载
  setTimeout(() => {
    router.push('/topology')
  }, 1500)
}

// 获取攻击类型名称
function getAttackTypeName() {
  return attackTypeMap[selectedAttackType.value] || selectedAttackType.value
}

// 获取业务场景名称
function getBusinessScenarioName() {
  return businessScenarioMap[selectedBusinessScenario.value] || selectedBusinessScenario.value
}

// 获取占位符文本
function getPlaceholderText() {
  if (selectedAttackType.value && selectedBusinessScenario.value) {
    return `描述具体的 ${getAttackTypeName()} 攻击场景，例如：攻击者如何渗透 ${getBusinessScenarioName()} 的网络系统...`
  }
  return '描述您想要的攻防场景，例如：医疗机构遭受APT攻击，攻击者通过钓鱼邮件获得初始访问权限...'
}

// 生成场景
async function generateScene() {
  // 验证输入
  if (!scenePrompt.value.trim() && (!selectedAttackType.value || !selectedBusinessScenario.value)) {
    return
  }

  isLoading.value = true

  try {
    // 调用场景智能体进行综合处理
    const response = await fetch('/api/scenario/process_request', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt: scenePrompt.value.trim() || getPlaceholderText()
      })
    })

    const result = await response.json()

    if (result.status === 'success') {
      // 将场景数据存储到sessionStorage，供拓扑页面使用
      sessionStorage.setItem('scenarioData', JSON.stringify({
        prompt: scenePrompt.value.trim(),
        agentOutput: result.data.agent_output,
        timestamp: Date.now(),
        selectedAttackType: selectedAttackType.value,
        selectedBusinessScenario: selectedBusinessScenario.value
      }))

      // 跳转到拓扑页面，带上场景模式参数
      router.push('/topology?mode=scenario')
    } else {
      throw new Error(result.message || '场景生成失败')
    }
  } catch (error) {
    console.error('场景生成过程中出错:', error)
    // 这里可以添加错误提示
  } finally {
    isLoading.value = false
  }
}

// 获取随机颜色
function getRandomColor() {
  const colors = [
    'var(--primary)',
    'var(--secondary)',
    'var(--accent)'
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}
</script>

<style scoped>
@keyframes float {

  0%,
  100% {
    transform: translate(0, 0);
  }

  25% {
    transform: translate(10px, -10px);
  }

  50% {
    transform: translate(15px, 5px);
  }

  75% {
    transform: translate(-10px, 10px);
  }
}

.scene-prompts-container {
  position: relative;
  padding: 1rem 0;
}

.scene-prompts {
  will-change: transform;
  white-space: nowrap;
}

.scene-prompt-card {
  display: inline-block;
  margin-right: 1rem;
  min-width: 256px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.scene-prompt-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}
</style>