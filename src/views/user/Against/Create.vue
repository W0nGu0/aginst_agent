<template>
  <div class="home-view">
    <!-- 动态靶场头部展示区 -->
    <div class="relative h-96 mb-20 rounded-2xl overflow-hidden against-hero-bg">
      <!-- 背景图片层 -->
      <div class="absolute inset-0">
        <img
          src="/Against_background.png"
          alt="Against Background"
          class="w-full h-full object-cover"
        />
        <!-- 虚化遮罩层 -->
        <div class="absolute inset-0 bg-gradient-to-br from-base-100/60 via-base-200/40 to-base-300/60 backdrop-blur-sm"></div>
        <!-- 额外的深色遮罩确保文字可读性 -->
        <div class="absolute inset-0 bg-black/20"></div>
      </div>

      <!-- 动态图形效果层 -->
      <div class="absolute inset-0 flex items-center justify-center">
        <div class="against-graphic">
          <div class="against-circle animate-pulse-slow"></div>
          <div class="against-grid"></div>
          <div class="against-nodes"></div>
          <div class="against-waves"></div>
        </div>

        <div class="z-10 text-center max-w-3xl px-4">
          <h1 class="text-4xl md:text-5xl font-bold mb-6 text-gradient-bright leading-tight animate-title-glow">
            AI 驱动的动态攻防推演靶场
          </h1>
          <p class="text-base-content/60 text-lg max-w-2xl mx-auto font-normal animate-fade-in-up">
            通过智能AI创建逼真攻防场景，训练与提升网络安全技能，体验真实环境下的攻防对抗
          </p>
        </div>
      </div>

      <!-- 底部装饰 -->
      <div class="absolute bottom-0 w-full h-12 bg-gradient-to-t from-base-200 to-transparent"></div>
    </div>

    <!-- 动态滚动提示词胶卷 -->
    <div class="mb-20 relative">
      <!-- 左右渐变遮罩 -->
      <div class="absolute left-0 top-0 w-40 h-full bg-gradient-to-r from-base-200 via-base-200/80 to-transparent z-10 pointer-events-none"></div>
      <div class="absolute right-0 top-0 w-40 h-full bg-gradient-to-l from-base-200 via-base-200/80 to-transparent z-10 pointer-events-none"></div>

      <div class="mb-8 text-center">
        <h2 class="text-3xl font-bold text-base-content flex items-center justify-center">
          <span class="text-accent mr-3 text-4xl animate-pulse">#</span>
          <span class="text-gradient-bright animate-title-glow">热门场景推荐</span>
        </h2>
        <div class="mt-2 w-24 h-1 bg-gradient-to-r from-primary via-accent to-secondary mx-auto rounded-full animate-pulse"></div>
      </div>

      <div class="scene-prompts-container overflow-hidden rounded-xl border border-accent/20 shadow-lg">
        <!-- 装饰性顶部条纹 -->
        <div class="h-1 bg-gradient-to-r from-primary via-accent to-secondary animate-pulse"></div>

        <div
          class="scene-prompts flex space-x-8 py-4"
          :style="scrollStyle"
          ref="scrollContainer"
          @mouseenter="handleMouseEnter"
          @mouseleave="handleMouseLeave"
        >
          <ScenePromptCard
            v-for="(prompt, index) in displayPrompts"
            :key="`${prompt.type}-${index}`"
            :prompt="prompt"
            @click="navigateToSceneDetail"
          />
        </div>

        <!-- 装饰性底部条纹 -->
        <div class="h-1 bg-gradient-to-r from-secondary via-accent to-primary animate-pulse"></div>
      </div>
    </div>

    <!-- 场景生成输入区 -->
    <div class="max-w-6xl mx-auto">
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


    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import ScenePromptCard from '../components/ScenePromptCard.vue'

const router = useRouter()
const scenePrompt = ref('')
const isLoading = ref(false)
const scrollContainer = ref(null)
const scrollPosition = ref(0)
const scrollSpeed = 1.2 // 滚动速度，数值越大滚动越快
const scrollInterval = ref(null)
const isScrollPaused = ref(false)

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
    transition: isScrollPaused.value ? 'transform 0.3s ease-out' : 'none',
  }
})

// 启动滚动
function startScroll() {
  if (scrollInterval.value || isScrollPaused.value) return

  // 计算一组卡片的总宽度 - 增加间距
  const cardWidth = 368 // 卡片宽度(320) + 间距(48)
  const totalWidth = scenePrompts.length * cardWidth

  // 设置初始位置为负值，这样卡片会从右侧进入
  if (scrollPosition.value === 0) {
    scrollPosition.value = -cardWidth * 1.5 // 从右侧开始
  }

  scrollInterval.value = setInterval(() => {
    if (isScrollPaused.value) return

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
  isScrollPaused.value = true
  pauseScroll()
}

// 鼠标离开时恢复滚动
function handleMouseLeave() {
  isScrollPaused.value = false
  setTimeout(() => {
    if (!isScrollPaused.value) {
      startScroll()
    }
  }, 100) // 短暂延迟，避免快速移动鼠标时的闪烁
}

// 组件挂载时启动滚动
onMounted(() => {
  // 延迟启动滚动，确保DOM完全渲染
  setTimeout(() => {
    startScroll()
  }, 500)
})

// 组件卸载前清除定时器和事件监听
onBeforeUnmount(() => {
  isScrollPaused.value = true
  pauseScroll()
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
</script>

<style scoped>
/* 字体和文字效果优化 */
.text-gradient-bright {
  background: linear-gradient(135deg,
    #ffffff 0%,
    rgba(var(--primary-rgb), 1) 25%,
    rgba(var(--accent-rgb), 1) 50%,
    rgba(var(--secondary-rgb), 1) 75%,
    #ffffff 100%
  );
  background-size: 200% 200%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: gradientShift 3s ease-in-out infinite;
}

/* 标题发光动画 */
@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.animate-title-glow {
  text-shadow:
    0 0 10px rgba(var(--primary-rgb), 0.5),
    0 0 20px rgba(var(--accent-rgb), 0.3),
    0 0 30px rgba(var(--secondary-rgb), 0.2);
  animation: titleGlow 2s ease-in-out infinite alternate;
}

@keyframes titleGlow {
  from {
    text-shadow:
      0 0 10px rgba(var(--primary-rgb), 0.5),
      0 0 20px rgba(var(--accent-rgb), 0.3),
      0 0 30px rgba(var(--secondary-rgb), 0.2);
  }
  to {
    text-shadow:
      0 0 15px rgba(var(--primary-rgb), 0.8),
      0 0 25px rgba(var(--accent-rgb), 0.6),
      0 0 35px rgba(var(--secondary-rgb), 0.4);
  }
}

.animate-fade-in-up {
  animation: fadeInUp 1s ease-out 0.5s both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 动态靶场专用背景样式 */
.against-hero-bg {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg,
    rgba(var(--base-100-rgb), 0.95) 0%,
    rgba(var(--base-200-rgb), 0.9) 30%,
    rgba(var(--base-300-rgb), 0.85) 70%,
    rgba(var(--base-100-rgb), 0.9) 100%
  );
}

.against-graphic {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
  opacity: 0.6;
}

.against-circle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 20rem;
  height: 20rem;
  border-radius: 50%;
  border: 1px solid rgba(var(--accent-rgb), 0.4);
  box-shadow: 0 0 60px rgba(var(--accent-rgb), 0.3), inset 0 0 40px rgba(var(--accent-rgb), 0.1);
  animation: rotate 20s linear infinite;
}

.against-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0.2;
  background-image:
    linear-gradient(rgba(var(--accent-rgb), 0.15) 1px, transparent 1px),
    linear-gradient(90deg, rgba(var(--accent-rgb), 0.15) 1px, transparent 1px);
  background-size: 30px 30px;
  animation: gridMove 15s linear infinite;
}

.against-nodes {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.against-nodes::before {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 25% 35%, rgba(var(--accent-rgb), 0.12) 0%, transparent 50%),
             radial-gradient(circle at 75% 65%, rgba(var(--secondary-rgb), 0.12) 0%, transparent 50%),
             radial-gradient(circle at 50% 20%, rgba(var(--primary-rgb), 0.08) 0%, transparent 40%);
}

.against-waves {
  position: absolute;
  width: 24rem;
  height: 24rem;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, transparent 60%, rgba(var(--primary-rgb), 0.08) 61%, transparent 65%);
  animation: pulse-against 12s infinite ease-in-out;
}

/* 滚动容器优化 */
.scene-prompts-container {
  position: relative;
  background: linear-gradient(135deg,
    rgba(var(--base-200-rgb), 0.4) 0%,
    rgba(var(--base-100-rgb), 0.2) 30%,
    rgba(var(--base-100-rgb), 0.2) 70%,
    rgba(var(--base-200-rgb), 0.4) 100%
  );
  backdrop-filter: blur(8px);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.scene-prompts {
  will-change: transform;
  white-space: nowrap;
}

/* 动画定义 */
@keyframes rotate {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

@keyframes gridMove {
  0% { background-position: 0 0; }
  100% { background-position: 30px 30px; }
}

@keyframes pulse-against {
  0%, 100% {
    transform: translate(-50%, -50%) scale(0.9);
    opacity: 0.3;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0.6;
  }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  25% { transform: translate(10px, -10px); }
  50% { transform: translate(15px, 5px); }
  75% { transform: translate(-10px, 10px); }
}
</style>