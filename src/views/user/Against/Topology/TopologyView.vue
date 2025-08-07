<template>
  <div class="topology-view">
    <div class="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-6">
      <!-- 左侧控制面板 -->
      <div class="bg-base-100 rounded-lg p-4 border border-base-300/30 mb-6">
        <!-- 场景模式控制 -->
        <div v-if="isScenarioMode" class="mb-6 p-4 bg-info/10 rounded-lg border border-info/30">
          <h3 class="text-lg font-semibold mb-3 flex items-center">
            <span class="text-info mr-2">🎯</span>场景编辑模式
          </h3>

          <!-- 编辑工具栏 -->
          <div class="flex flex-wrap gap-2 mb-4">
            <button @click="deleteSelectedNode" class="btn btn-sm btn-error"
              :disabled="!selectedObject || (!selectedObject.type === 'device' && !selectedObject.nodeData)">
              🗑️ 删除节点
            </button>
            <button @click="editSelectedNodeIP" class="btn btn-sm btn-info"
              :disabled="!selectedObject || (!selectedObject.type === 'device' && !selectedObject.nodeData)">
              🏷️ 设置IP
            </button>
            <button @click="openContainerConfig" class="btn btn-sm btn-primary"
              :disabled="!selectedObject || (!selectedObject.type === 'device' && !selectedObject.nodeData) || !isContainerRunning(selectedObject)">
              ⚙️ 容器配置
            </button>
            <button @click="startConnectingNodes" class="btn btn-sm btn-warning"
              :class="{ 'btn-active': isConnectingNodes }">
              🔗 连接节点
            </button>
            <button v-if="isConnectingNodes" @click="stopConnectingNodes" class="btn btn-sm btn-ghost">
              ❌ 取消连接
            </button>

          </div>

          <!-- 节点添加区域 -->
          <div class="mb-4">
            <h4 class="font-medium mb-2">添加节点:</h4>
            <div class="grid grid-cols-2 gap-2">
              <button v-for="nodeType in availableNodeTypes" :key="nodeType.type" @click="startAddingNode(nodeType)"
                class="btn btn-sm btn-outline"
                :class="{ 'btn-active': isAddingNode && selectedNodeType?.type === nodeType.type }">
                {{ nodeType.name }}
              </button>
            </div>
            <button v-if="isAddingNode" @click="stopAddingNode" class="btn btn-sm btn-ghost mt-2 w-full">
              ❌ 取消添加 (调试: {{ isAddingNode }})
            </button>
          </div>

          <!-- 场景信息 -->
          <div v-if="scenarioData" class="text-sm text-base-content/70">
            <p><strong>场景:</strong> {{ scenarioData.metadata?.description || 'APT医疗场景' }}</p>
            <p><strong>节点数:</strong> {{ scenarioData.nodes?.length || 0 }}</p>
            <p><strong>虚拟节点:</strong> {{ virtualNodes.size }}</p>
            <p><strong>运行节点:</strong> {{ runningNodes.size }}</p>
          </div>
        </div>

        <!-- 普通设备库 -->
        <div v-if="!isScenarioMode">
          <h2 class="text-xl font-semibold mb-4 flex items-center">
            <span class="text-primary mr-2">#</span>设备库
          </h2>

          <div class="device-grid">
            <div v-for="(color, type) in deviceTypes" :key="type" class="device-item" @click="createDevice(type)">
              <div class="device-icon" :style="`background-color: ${color}`">
                <img :src="getDeviceIcon(type)" class="w-6 h-6" alt="">
              </div>
              <div class="device-name">{{ getDeviceTypeName(type) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧拓扑图区域 -->
      <div class="bg-base-100 rounded-lg p-4 border border-base-300/30">
        <h2 class="text-xl font-semibold mb-4 flex items-center justify-between">
          <div>
            <span class="text-primary mr-2">#</span>网络拓扑图
          </div>
          <div class="flex gap-2 flex-wrap">
            <!-- 场景模式按钮 -->
            <template v-if="isScenarioMode">
              <button @click="generateScenario" class="btn btn-sm btn-success" :disabled="virtualNodes.size === 0">
                🚀 部署容器 ({{ virtualNodes.size }})
              </button>
              <button @click="disableEditMode" class="btn btn-sm btn-ghost">
                ❌ 退出编辑
              </button>
            </template>

            <!-- 普通模式按钮 -->
            <template v-else>
              <button @click="saveTopology" class="btn btn-sm btn-primary">保存拓扑图</button>
              <button @click="generateScenario" class="btn btn-sm btn-success">生成场景</button>
              <button @click="destroyScenario" class="btn btn-sm btn-error">销毁场景</button>
            </template>

            <button @click="toggleFullScreen" class="btn btn-sm">全屏</button>
          </div>
        </h2>

        <div class="topology-container relative" id="topology-wrapper">
          <div id="topology-loading" class="absolute inset-0 bg-base-300/50 flex items-center justify-center z-10">
            <div class="loading-spinner">
              <div class="spinner"></div>
              <div class="mt-3 text-base-content">加载中...</div>
            </div>
          </div>
          <canvas id="network-topology" width="800" height="500"></canvas>



          <!-- 事件监控器 -->
          <div class="event-monitor-container">
            <EventMonitor ref="eventMonitorRef" :attackTaskStatus="currentAttackTaskStatus"
              @nodes-status-reset="handleNodesStatusReset" @nodes-status-refreshed="handleNodesStatusRefreshed" />
          </div>
        </div>
      </div>
    </div>

    <!-- 虚拟时间轴 - 放在拓扑图下方 -->
    <div class="virtual-timeline-section">
      <VirtualTimeline ref="virtualTimelineRef" :auto-start="false" @timeline-started="onTimelineStarted"
        @timeline-paused="onTimelinePaused" @timeline-reset="onTimelineReset" @phase-changed="onPhaseChanged"
        @speed-changed="onSpeedChanged" />
    </div>

    <!-- 攻击者对话框 -->
    <AttackerDialog :show="showAttackerDialog" :attacker="selectedAttacker" :targets="attackTargets"
      @close="showAttackerDialog = false" @attack="handleAttack" />

    <!-- 防火墙对话框 -->
    <FirewallDialog :show="showFirewallDialog" :firewall="selectedFirewall" @close="showFirewallDialog = false"
      @save="handleFirewallSave" @firewall-updated="handleFirewallUpdated" />

    <!-- 主机信息对话框 -->
    <HostInfoDialog :show="showHostInfoDialog" :host="selectedHost" @close="showHostInfoDialog = false" />

    <!-- 容器配置对话框 -->
    <ContainerConfigDialog :show="showContainerConfigDialog" :container="selectedContainer"
      @close="showContainerConfigDialog = false" @message="handleMessage" />

    <!-- IP设置对话框 -->
    <div v-if="showIPDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-base-100 rounded-lg p-6 w-96 max-w-md">
        <h3 class="text-lg font-semibold mb-4">设置节点IP地址</h3>
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">节点名称:</label>
          <input v-model="editingNode.name" type="text" class="input input-bordered w-full" placeholder="输入节点名称" />
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">IP地址:</label>
          <input v-model="editingNode.ip" type="text" class="input input-bordered w-full"
            placeholder="例如: 192.168.1.100" />
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium mb-2">网络段:</label>
          <select v-model="editingNode.network" class="select select-bordered w-full">
            <option value="">选择网络段</option>
            <option value="dmz_segment">DMZ段 (172.16.100.0/24)</option>
            <option value="server_segment">服务器段 (192.168.200.0/24)</option>
            <option value="user_segment">用户段 (192.168.100.0/24)</option>
            <option value="db_segment">数据库段 (192.168.214.0/24)</option>
            <option value="medical_segment">医疗段 (192.168.101.0/24)</option>
          </select>
        </div>
        <div class="flex gap-2 justify-end">
          <button @click="closeIPDialog" class="btn btn-ghost">取消</button>
          <button @click="saveNodeIP" class="btn btn-primary">保存</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useTopologyStore } from '../../../../stores/topology'
import NetworkTopology from './core/NetworkTopology'
import TopologyGenerator from './core/TopologyGenerator'
import FabricAttackVisualization from './core/FabricAttackVisualization'
import FabricDefenseVisualization from './core/FabricDefenseVisualization'
// 移除未使用的AttackStageAnimations导入
import TopologyService from './services/TopologyService'
import AttackService from './services/AttackService'
import ScenarioDataService from './services/ScenarioDataService'

import AttackAgentService from './services/AttackAgentService'
import AttackTaskService from './services/AttackTaskService'
import WebSocketService from './services/WebSocketService'
import AttackerDialog from './components/AttackerDialog.vue'
import FirewallDialog from './components/FirewallDialog.vue'
import HostInfoDialog from './components/HostInfoDialog.vue'
import ContainerConfigDialog from './components/ContainerConfigDialog.vue'
import EventMonitor from './components/EventMonitor.vue'
import VirtualTimeline from './components/VirtualTimeline.vue'

const topologyStore = useTopologyStore()
let topology = null
let attackVisualization = null
let defenseVisualization = null
let fabricLoaded = true // 直接设置为 true，因为我们已经通过 import 导入了 fabric

// 设备类型及其颜色
const deviceTypes = {
  'router': '#4CAF50',      // 路由器
  'firewall': '#F44336',    // 防火墙
  'switch': '#2196F3',      // 交换机
  'server': '#FF9800',      // 通用服务器
  'pc': '#9C27B0',          // 工作站/终端
  'db': '#3f51b5',          // 数据库服务器
  'web': '#03a9f4',         // Web服务器
  'app': '#795548',         // 应用服务器
  'file': '#607d8b',        // 文件服务器
  'mail': '#6d4c41',        // 邮件服务器
  'vpn': '#009688',         // VPN网关
  'dns': '#8bc34a',         // DNS服务器
  'proxy': '#ff5722',       // 代理服务器
  'load': '#673AB7'         // 负载均衡器
}

// 对话框状态
const showAttackerDialog = ref(false)
const showFirewallDialog = ref(false)
const showHostInfoDialog = ref(false)
const showContainerConfigDialog = ref(false)
const selectedAttacker = ref(null)
const selectedFirewall = ref(null)
const selectedHost = ref(null)
const selectedContainer = ref(null)
const attackTargets = ref([])
const eventMonitorRef = ref(null)
const virtualTimelineRef = ref(null)

// 攻击任务状态
const currentAttackTaskId = ref('')
const currentAttackTaskStatus = ref(null)

// 场景模式状态
const isScenarioMode = ref(false)
const scenarioData = ref(null)
const virtualNodes = ref(new Set())
const runningNodes = ref(new Set())
const serviceToNodeMap = ref(new Map()) // 服务名到节点ID的映射

// 节点编辑状态
const isEditMode = ref(false)
const isAddingNode = ref(false)
const isConnectingNodes = ref(false)
const selectedNodeForConnection = ref(null)
const selectedNodeType = ref(null)

// 拖拽状态管理
const isDragging = ref(false)
const dragStartTime = ref(0)
const dragStartPosition = ref({ x: 0, y: 0 })
const DRAG_THRESHOLD = 5 // 像素阈值，超过这个距离才认为是拖拽
const CLICK_TIME_THRESHOLD = 200 // 毫秒阈值，超过这个时间才认为是拖拽

// 节点类型计数器
const nodeTypeCounters = ref({
  workstation: 0,
  server: 0,
  firewall: 0,
  router: 0,
  switch: 0,
  database: 0,
  pc: 0
})

// 选中状态
const selectedObject = ref(null)

// IP设置对话框状态
const showIPDialog = ref(false)
const editingNode = ref({
  id: null,
  name: '',
  ip: '',
  network: ''
})
const availableNodeTypes = ref([
  { type: 'workstation', name: '工作站', icon: '/icons/workstation.svg' },
  { type: 'server', name: '服务器', icon: '/icons/server.svg' },
  { type: 'database', name: '数据库', icon: '/icons/database.svg' },
  { type: 'firewall', name: '防火墙', icon: '/icons/firewall.svg' },
  { type: 'router', name: '路由器', icon: '/icons/router.svg' },
  { type: 'switch', name: '交换机', icon: '/icons/switch.svg' }
])





// 初始化拓扑图
onMounted(async () => {
  await loadFabric()

  // 检查是否是场景模式 - 修复Vue Router hash模式下的参数解析
  const fullUrl = window.location.href
  const hashPart = window.location.hash
  let mode = null

  // 从hash中提取查询参数
  if (hashPart.includes('?')) {
    const queryString = hashPart.split('?')[1]
    const urlParams = new URLSearchParams(queryString)
    mode = urlParams.get('mode')
  }

  console.log('🔍 URL参数检查:')
  console.log('   - 完整URL:', fullUrl)
  console.log('   - Hash部分:', hashPart)
  console.log('   - mode参数:', mode)

  // 检查sessionStorage中的场景数据
  let scenarioDataStr = sessionStorage.getItem('scenarioData')
  console.log('🔍 SessionStorage检查:')
  console.log('   - scenarioData存在:', !!scenarioDataStr)
  console.log('   - scenarioData长度:', scenarioDataStr?.length || 0)

  // 如果sessionStorage中没有数据，检查localStorage
  if (!scenarioDataStr) {
    scenarioDataStr = localStorage.getItem('persistentScenarioData')
    console.log('🔍 LocalStorage检查:')
    console.log('   - persistentScenarioData存在:', !!scenarioDataStr)
    console.log('   - persistentScenarioData长度:', scenarioDataStr?.length || 0)

    if (scenarioDataStr) {
      console.log('📦 从localStorage恢复场景数据')
    }
  }

  if (mode === 'scenario') {
    console.log('✅ 检测到场景模式')

    if (scenarioDataStr) {
      try {
        const storedData = JSON.parse(scenarioDataStr)
        console.log('📋 成功解析场景数据:')
        console.log('   - 数据结构:', Object.keys(storedData))
        console.log('   - prompt:', storedData.prompt)
        console.log('   - agentOutput长度:', storedData.agentOutput?.length || 0)

        // 保存数据到全局变量，以便调试
        window.currentScenarioData = storedData
        console.log('💾 场景数据已保存到 window.currentScenarioData')

        // 场景模式：直接初始化场景拓扑，不使用通用的initializeTopology
        await initializeScenarioTopology(storedData)

        // 保存到localStorage以便持久化存储
        localStorage.setItem('persistentScenarioData', JSON.stringify(storedData))
        console.log('💾 场景数据已保存到localStorage以便持久化')

        // 清理sessionStorage（在成功加载后）
        sessionStorage.removeItem('scenarioData')
        console.log('🧹 已清理sessionStorage中的场景数据')
      } catch (error) {
        console.error('❌ 解析场景数据失败:', error)
        // 场景数据解析失败，回退到普通模式
        initializeBasicTopology()
      }
    } else {
      console.warn('⚠️ 场景模式但未找到场景数据，尝试加载预设APT场景')
      // 始终保持场景模式，加载预设APT场景
      await initializeAPTScenario()
    }
  } else {
    console.log('📋 普通模式，但强制使用场景模式，加载预设APT场景')
    // 始终使用场景模式
    await initializeAPTScenario()
  }

  // 添加攻击进度和完成事件监听
  window.addEventListener('attack-progress', handleAttackProgress)
  window.addEventListener('attack-completed', handleAttackCompleted)

  // 添加拓扑动画事件监听
  document.addEventListener('topology-animation', handleTopologyAnimationEvent)

  // 初始化WebSocket连接
  await initWebSocketConnection()

  // 页面加载完成后滚动到顶部
  setTimeout(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, 100)
})

// 初始化WebSocket连接
async function initWebSocketConnection() {
  try {
    // 连接到WebSocket服务器
    const connected = await WebSocketService.connect();

    if (connected) {
      console.log('WebSocket连接成功');

      // 添加消息处理器
      WebSocketService.addMessageHandler(handleWebSocketMessage);

      // 发送测试消息
      logInfo('系统', 'WebSocket连接已建立，可以接收实时日志');

      // 每30秒检查一次连接状态
      setInterval(() => {
        if (!WebSocketService.connected) {
          console.log('WebSocket连接已断开，尝试重新连接');
          WebSocketService.connect();
        }
      }, 30000);
    } else {
      console.error('WebSocket连接失败');
      logWarning('系统', 'WebSocket连接失败，无法接收实时日志');

      // 5秒后重试
      setTimeout(() => initWebSocketConnection(), 5000);
    }
  } catch (error) {
    console.error('初始化WebSocket连接失败:', error);
    logError('系统', `初始化WebSocket连接失败: ${error.message}`);

    // 5秒后重试
    setTimeout(() => initWebSocketConnection(), 5000);
  }
}

// 处理WebSocket消息
function handleWebSocketMessage(message) {
  try {
    // 检查消息格式
    if (!message || !message.level || !message.source || !message.message) {
      console.warn('收到格式不正确的WebSocket消息:', JSON.stringify(message, null, 2));
      return;
    }

    console.log('收到WebSocket消息:', JSON.stringify(message, null, 2));

    // 记录日志到系统日志区域，标记为WebSocket日志
    // 如果消息包含attack_info，需要传递给EventMonitor处理
    if (message.attack_info) {
      // 直接调用EventMonitor的addLog方法，确保attack_info被处理
      if (eventMonitorRef.value) {
        eventMonitorRef.value.addLog({
          level: message.level,
          source: message.source,
          message: message.message,
          timestamp: new Date().toLocaleTimeString(),
          fromWebSocket: true,
          attack_info: message.attack_info  // 传递attack_info
        });
      }

      // 同时添加到虚拟时间轴
      if (virtualTimelineRef.value && message.attack_info) {
        const attackInfo = message.attack_info
        virtualTimelineRef.value.addEvent({
          phase: getPhaseDisplayName(attackInfo.stage),
          type: getEventType(message.level),
          message: message.message,
          details: {
            '技术': attackInfo.technique,
            '源节点': attackInfo.source_node,
            '目标节点': attackInfo.target_node,
            '状态': attackInfo.status,
            '进度': attackInfo.progress + '%'
          }
        })

        // 更新时间轴阶段
        virtualTimelineRef.value.setPhase(getPhaseDisplayName(attackInfo.stage))

        // 更新受影响资产数量
        if (attackInfo.status === 'completed' && attackInfo.target_node) {
          updateCompromisedAssetsCount()
        }
      }
    } else {
      // 普通日志使用logMessage函数
      logMessage(message.level, message.source, message.message, true);
    }

    // 判断是否是关键事件
    const isKeyEvent = isKeyAttackEvent(message);

    // 如果是关键事件，添加到关键事件区域
    if (isKeyEvent) {
      // 确定事件类型
      const eventType = determineEventType(message);

      // 添加到关键事件，标记为WebSocket事件
      addEvent({
        type: eventType,
        message: `[${message.source}] ${message.message}`,
        fromWebSocket: true
      });
    }

    // 如果是攻击相关的消息，也添加到关键事件区域
    if (message.source.includes('攻击') ||
      message.message.toLowerCase().includes('攻击') ||
      message.message.toLowerCase().includes('侦察') ||
      message.message.toLowerCase().includes('扫描') ||
      message.message.toLowerCase().includes('武器化') ||
      message.message.toLowerCase().includes('投递') ||
      message.message.toLowerCase().includes('利用') ||
      message.message.toLowerCase().includes('安装') ||
      message.message.toLowerCase().includes('命令') ||
      message.message.toLowerCase().includes('控制') ||
      message.message.toLowerCase().includes('目标')) {

      // 添加到关键事件，标记为WebSocket事件
      addAttackEvent(`[${message.source}] ${message.message}`, true);
    }

    // 基于真实攻击日志触发可视化动画（只在攻击真正执行时）
    if (attackVisualization && topology && topology.devices) {
      // 检查当前攻击任务状态，只在真正攻击阶段才显示动画
      const shouldShowAnimation = shouldTriggerAttackAnimation(message)
      if (shouldShowAnimation) {
        triggerAttackVisualizationFromLog(message)
      }
    }

    // 基于防御日志触发防御可视化动画
    if (defenseVisualization && topology && topology.devices) {
      const shouldShowDefenseAnimation = shouldTriggerDefenseAnimation(message)
      if (shouldShowDefenseAnimation) {
        console.log('🛡️ 触发防御可视化动画:', message.source, message.message)
        triggerDefenseVisualizationFromLog(message)
      }
    }

    // 如果是防御相关的消息，也添加到关键事件区域
    if (message.source.includes('威胁阻断') ||
      message.source.includes('漏洞修复') ||
      message.source.includes('攻击溯源') ||
      message.source.includes('防御协调器') ||
      message.source.includes('攻防演练裁判') ||
      message.message.includes('防御') ||
      message.message.includes('阻断') ||
      message.message.includes('修复') ||
      message.message.includes('溯源') ||
      message.message.includes('胜利') ||
      message.message.includes('演练结束')) {

      // 添加到关键事件，标记为防御事件
      addEvent({
        type: 'defense',
        message: `[${message.source}] ${message.message}`,
        fromWebSocket: true
      });
    }

    // 特殊处理裁判系统的胜负判定消息
    if (message.source.includes('攻防演练裁判')) {
      if (message.message.includes('攻击方胜利') || message.message.includes('🔴')) {
        // 攻击方胜利
        showBattleResult('attack_victory', message.message);
      } else if (message.message.includes('防御方胜利') || message.message.includes('🟢')) {
        // 防御方胜利
        showBattleResult('defense_victory', message.message);
      } else if (message.message.includes('攻防演练开始') || message.message.includes('🚀')) {
        // 演练开始
        showBattleResult('battle_start', message.message);
      } else if (message.message.includes('战报') || message.message.includes('📊')) {
        // 战报信息
        showBattleReport(message.message);
      }
    }

    // 如果是攻击相关的消息，更新攻击状态
    if (message.source.includes('攻击') ||
      message.message.includes('攻击') ||
      message.message.includes('侦察') ||
      message.message.includes('钓鱼') ||
      message.message.includes('扫描') ||
      message.message.includes('漏洞') ||
      message.message.includes('利用') ||
      message.message.includes('命令') ||
      message.message.includes('控制')) {

      // 如果有攻击任务ID，更新任务状态
      if (currentAttackTaskId.value) {
        // 添加日志到任务
        AttackTaskService.addTaskLog(
          currentAttackTaskId.value,
          message.level,
          message.source,
          message.message
        );

        // 根据消息内容更新攻击阶段
        updateAttackPhaseFromMessage(message);
      }
    }
  } catch (error) {
    console.error('处理WebSocket消息失败:', error);
  }
}

// 判断是否是关键攻击事件
function isKeyAttackEvent(message) {
  const msg = message.message.toLowerCase();
  const source = message.source.toLowerCase();

  // 关键词列表
  const keyPhrases = [
    '开始侦察', '扫描目标', '情报收集', '元数据',
    '武器化', '生成钓鱼', '定制钓鱼',
    '投递', '发送邮件', '邮件已发送',
    '利用', '漏洞', '点击链接', '凭据',
    '安装', '持久化', '访问权限',
    '命令控制', '远程连接', '横向移动',
    '目标行动', '数据窃取', '攻陷', '完成'
  ];

  // 检查消息是否包含关键词
  return keyPhrases.some(phrase => msg.includes(phrase)) ||
    message.level === 'success' ||
    message.level === 'error' ||
    source.includes('攻击智能体') ||
    source.includes('中央智能体');
}

// 确定事件类型
function determineEventType(message) {
  const level = message.level.toLowerCase();
  const msg = message.message.toLowerCase();

  if (level === 'error') {
    return 'failure';
  } else if (level === 'warning') {
    return 'warning';
  } else if (level === 'success') {
    return 'success';
  } else if (msg.includes('攻击') || msg.includes('侦察') || msg.includes('扫描') ||
    msg.includes('武器化') || msg.includes('投递') || msg.includes('利用') ||
    msg.includes('安装') || msg.includes('命令') || msg.includes('控制') ||
    msg.includes('目标')) {
    return 'attack';
  } else if (msg.includes('防御') || msg.includes('阻止') || msg.includes('检测')) {
    return 'defense';
  } else {
    return 'system';
  }
}

// 根据消息内容更新攻击阶段
function updateAttackPhaseFromMessage(message) {
  const msg = message.message.toLowerCase();
  const source = message.source.toLowerCase();

  // 根据消息内容判断当前阶段
  let phase = null;
  let progress = 0;

  if (source.includes('侦察') || msg.includes('侦察') || msg.includes('扫描') || msg.includes('情报收集')) {
    phase = AttackTaskService.PHASE.RECONNAISSANCE;
    progress = 10;
  } else if (source.includes('武器化') || msg.includes('武器化') || msg.includes('生成') || msg.includes('钓鱼邮件')) {
    phase = AttackTaskService.PHASE.WEAPONIZATION;
    progress = 25;
  } else if (source.includes('投递') || msg.includes('投递') || msg.includes('发送') || msg.includes('邮件')) {
    phase = AttackTaskService.PHASE.DELIVERY;
    progress = 40;
  } else if (source.includes('利用') || msg.includes('利用') || msg.includes('漏洞') || msg.includes('点击')) {
    phase = AttackTaskService.PHASE.EXPLOITATION;
    progress = 60;
  } else if (source.includes('安装') || msg.includes('安装') || msg.includes('持久') || msg.includes('访问')) {
    phase = AttackTaskService.PHASE.INSTALLATION;
    progress = 75;
  } else if (source.includes('命令') || msg.includes('命令') || msg.includes('控制') || msg.includes('远程')) {
    phase = AttackTaskService.PHASE.COMMAND_AND_CONTROL;
    progress = 85;
  } else if (source.includes('目标') || msg.includes('目标') || msg.includes('数据') || msg.includes('攻陷')) {
    phase = AttackTaskService.PHASE.ACTIONS_ON_OBJECTIVES;
    progress = 95;
  }

  // 如果确定了阶段，更新任务状态
  if (phase) {
    const currentTask = AttackTaskService.getTaskStatus(currentAttackTaskId.value);
    if (currentTask) {
      // 只有当新阶段比当前阶段更高时才更新
      const currentPhaseIndex = Object.values(AttackTaskService.PHASE).indexOf(currentTask.phase);
      const newPhaseIndex = Object.values(AttackTaskService.PHASE).indexOf(phase);

      if (newPhaseIndex > currentPhaseIndex || currentTask.progress < progress) {
        AttackTaskService.updateTask(currentAttackTaskId.value, {
          phase,
          progress: Math.max(progress, currentTask.progress)
        });

        // 触发任务更新事件
        const event = new CustomEvent('attack-progress', {
          detail: {
            taskId: currentAttackTaskId.value,
            status: AttackTaskService.getTaskStatus(currentAttackTaskId.value)
          }
        });
        window.dispatchEvent(event);
      }
    }
  }
}

// 在组件卸载时移除事件监听器
onUnmounted(() => {
  // 移除事件监听器
  window.removeEventListener('attack-progress', handleAttackProgress)
  window.removeEventListener('attack-completed', handleAttackCompleted)
  document.removeEventListener('topology-animation', handleTopologyAnimationEvent)

  // 移除WebSocket消息处理器
  WebSocketService.removeMessageHandler(handleWebSocketMessage)

  // 断开WebSocket连接
  WebSocketService.disconnect()
})

// 加载Fabric.js库
async function loadFabric() {
  // Fabric.js 已通过 import 导入，无需动态加载
  console.log('Fabric.js已加载')
  return Promise.resolve()
}

// 普通模式的基础拓扑图初始化（简化版）
function initializeBasicTopology() {
  if (!fabricLoaded) {
    console.error('Fabric.js未加载，无法初始化拓扑图')
    return
  }

  console.log('🚀 普通模式：创建基础拓扑图实例...')

  try {
    topology = new NetworkTopology({
      canvasId: 'network-topology'
    })

    console.log('✅ 普通模式：NetworkTopology 实例创建成功')
    window.topology = topology

    topology.initialize().then(() => {
      console.log('✅ 普通模式：拓扑图初始化完成')

      // 设置Fabric实例
      const canvas = document.querySelector('#network-topology')
      if (canvas && topology.canvas) {
        canvas.__fabric = topology.canvas
        canvas.fabric = topology.canvas
        console.log('✅ 普通模式：Fabric 实例已附加到 DOM')
      }

      // 初始化攻击可视化
      try {
        attackVisualization = new FabricAttackVisualization(topology)
        console.log('✅ 普通模式：Fabric攻击可视化初始化成功')
      } catch (error) {
        console.error('❌ 普通模式：Fabric攻击可视化初始化失败:', error)
        attackVisualization = null
      }

      // 初始化防御可视化
      try {
        defenseVisualization = new FabricDefenseVisualization(topology)
        console.log('✅ 普通模式：Fabric防御可视化初始化成功')
      } catch (error) {
        console.error('❌ 普通模式：Fabric防御可视化初始化失败:', error)
        defenseVisualization = null
      }

      // 设置拖拽检测事件监听
      setupDragDetection()

      // 监听取消选中事件
      topology.canvas.on('selection:cleared', () => {
        selectedObject.value = null
      })

      // 添加节点移动事件监听器（用于更新连线和标签）
      topology.canvas.on('object:moving', function (e) {
        const obj = e.target
        if (obj && (obj.type === 'device' || obj.nodeData)) {
          // 使用NetworkTopology原生的连线更新逻辑
          if (topology.connections) {
            topology.connections.forEach(conn => {
              if (conn.source === obj || conn.target === obj) {
                topology._updateConnection(conn)
              }
            })
          }

          // 更新场景模式的网络连线和标签
          const nodeId = obj.nodeData?.scenarioData?.id || obj.nodeData?.id || obj.id
          if (nodeId) {
            updateConnectionsForNode(nodeId)
          }

          // 更新节点相关的标签位置（不包括连线上的IP标签，因为updateConnectionsForNode已经处理了）
          updateNodeLabelsPosition(obj)
        }
      })

      // 初始化canvas store
      topologyStore.setCanvas(topology.canvas)

      // 隐藏加载动画
      const loadingEl = document.getElementById('topology-loading')
      if (loadingEl) {
        loadingEl.style.display = 'none'
        console.log('✅ 普通模式：加载动画已隐藏')
      }

      // 触发初始化完成事件
      const initEvent = new CustomEvent('topology-initialized', {
        detail: {
          topology: topology,
          canvas: topology.canvas,
          mode: 'basic',
          timestamp: new Date()
        }
      })
      document.dispatchEvent(initEvent)
      console.log('🎉 普通模式：拓扑图初始化完成')

    }).catch(err => {
      console.error('❌ 普通模式：拓扑图初始化失败:', err)
    })

  } catch (error) {
    console.error('❌ 普通模式：NetworkTopology 实例创建失败:', error)
  }
}

// 专门用于场景模式的拓扑图初始化
async function initializeScenarioTopology(storedData) {
  console.log('🎯 场景模式：初始化场景拓扑图...')

  if (!fabricLoaded) {
    console.error('Fabric.js未加载，无法初始化拓扑图')
    return
  }

  try {
    // 1. 创建基础拓扑图实例
    topology = new NetworkTopology({
      canvasId: 'network-topology'
    })
    console.log('✅ 场景模式：NetworkTopology 实例创建成功')

    // 将 topology 对象暴露到全局，供调试使用
    window.topology = topology

    // 2. 初始化基础组件
    await topology.initialize()
    console.log('✅ 场景模式：拓扑图基础组件初始化完成')

    // 3. 设置Fabric实例
    const canvas = document.querySelector('#network-topology')
    if (canvas && topology.canvas) {
      canvas.__fabric = topology.canvas
      canvas.fabric = topology.canvas
      console.log('✅ 场景模式：Fabric 实例已附加到 DOM')
    }

    // 4. 初始化攻击可视化
    try {
      attackVisualization = new FabricAttackVisualization(topology)
      console.log('✅ 场景模式：Fabric攻击可视化初始化成功')
    } catch (error) {
      console.error('❌ 场景模式：Fabric攻击可视化初始化失败:', error)
      attackVisualization = null
    }

    // 5. 初始化防御可视化
    try {
      defenseVisualization = new FabricDefenseVisualization(topology)
      console.log('✅ 场景模式：Fabric防御可视化初始化成功')
    } catch (error) {
      console.error('❌ 场景模式：Fabric防御可视化初始化失败:', error)
      defenseVisualization = null
    }

    // 5. 设置拖拽检测事件监听
    setupDragDetection()

    // 监听取消选中事件
    topology.canvas.on('selection:cleared', () => {
      selectedObject.value = null
    })

    // 添加节点移动事件监听器（用于更新连线和标签）
    topology.canvas.on('object:moving', function (e) {
      const obj = e.target
      if (obj && (obj.type === 'device' || obj.nodeData)) {
        // 使用NetworkTopology原生的连线更新逻辑
        if (topology.connections) {
          topology.connections.forEach(conn => {
            if (conn.source === obj || conn.target === obj) {
              topology._updateConnection(conn)
            }
          })
        }

        // 更新场景模式的网络连线和标签
        const nodeId = obj.nodeData?.scenarioData?.id || obj.nodeData?.id || obj.id
        if (nodeId) {
          updateConnectionsForNode(nodeId)
        }

        // 更新节点相关的标签位置（不包括连线上的IP标签，因为updateConnectionsForNode已经处理了）
        updateNodeLabelsPosition(obj)
      }
    })

    // 6. 初始化canvas store
    topologyStore.setCanvas(topology.canvas)

    // 7. 立即加载场景数据（不等待）
    console.log('🚀 场景模式：开始加载场景智能体数据...')
    const success = await loadDynamicScenario(storedData)
    if (success) {
      enableEditMode()
      logInfo('系统', `场景模式已激活: ${storedData.prompt}`)
    }

    // 7.5. 隐藏加载动画
    const loadingEl = document.getElementById('topology-loading')
    if (loadingEl) {
      loadingEl.style.display = 'none'
      console.log('✅ 场景模式：加载动画已隐藏')
    }

    // 8. 触发初始化完成事件
    const initEvent = new CustomEvent('topology-initialized', {
      detail: {
        topology: topology,
        canvas: topology.canvas,
        mode: 'scenario',
        timestamp: new Date()
      }
    })
    document.dispatchEvent(initEvent)
    console.log('🎉 场景模式：拓扑图初始化完成事件已触发')

  } catch (error) {
    console.error('❌ 场景模式：拓扑图初始化失败:', error)
    // 回退到普通模式
    initializeBasicTopology()
  }
}

// 设置拖拽检测
function setupDragDetection() {
  if (!topology || !topology.canvas) return

  // 监听鼠标按下事件
  topology.canvas.on('mouse:down', (e) => {
    if (e.target && (e.target.type === 'device' || e.target.nodeData)) {
      isDragging.value = false
      dragStartTime.value = Date.now()
      const pointer = topology.canvas.getPointer(e.e)
      dragStartPosition.value = { x: pointer.x, y: pointer.y }
      console.log('🖱️ 鼠标按下，开始检测拖拽:', { target: e.target, position: dragStartPosition.value })
    }
  })

  // 监听鼠标移动事件
  topology.canvas.on('mouse:move', (e) => {
    if (dragStartTime.value > 0 && !isDragging.value) {
      const pointer = topology.canvas.getPointer(e.e)
      const deltaX = Math.abs(pointer.x - dragStartPosition.value.x)
      const deltaY = Math.abs(pointer.y - dragStartPosition.value.y)
      const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)
      const timeDelta = Date.now() - dragStartTime.value

      // 如果移动距离超过阈值或时间超过阈值，认为是拖拽
      if (distance > DRAG_THRESHOLD || timeDelta > CLICK_TIME_THRESHOLD) {
        isDragging.value = true
        console.log('🖱️ 检测到拖拽开始:', { distance, timeDelta })
      }
    }
  })

  // 监听鼠标释放事件
  topology.canvas.on('mouse:up', (e) => {
    const wasDragging = isDragging.value
    const target = e.target

    // 重置拖拽状态
    isDragging.value = false
    dragStartTime.value = 0
    dragStartPosition.value = { x: 0, y: 0 }

    // 如果不是拖拽，且点击的是设备，则处理点击事件
    if (!wasDragging && target && (target.type === 'device' || target.nodeData)) {
      console.log('🖱️ 检测到点击事件（非拖拽）:', target)
      handleDeviceClick(target)
    } else if (wasDragging) {
      console.log('🖱️ 拖拽结束，不触发点击事件')
    }
  })

  // 监听选择创建事件，但只在非拖拽时处理
  topology.canvas.on('selection:created', (e) => {
    // 延迟处理，确保拖拽状态已更新
    setTimeout(() => {
      if (!isDragging.value && e.selected && e.selected.length > 0) {
        const selectedObj = e.selected[0]
        console.log('🖱️ 选择创建事件（非拖拽）:', selectedObj)
        selectedObject.value = selectedObj
        topologyStore.setSelectedObject(selectedObj)
      }
    }, 10)
  })

  // 监听选择更新事件
  topology.canvas.on('selection:updated', (e) => {
    setTimeout(() => {
      if (!isDragging.value && e.selected && e.selected.length > 0) {
        const selectedObj = e.selected[0]
        console.log('🖱️ 选择更新事件（非拖拽）:', selectedObj)
        selectedObject.value = selectedObj
        topologyStore.setSelectedObject(selectedObj)
      }
    }, 10)
  })
}

// 处理设备点击事件
function handleDeviceClick(device) {
  console.log('🖱️ 处理设备点击事件:', device)

  // 检查节点状态，只有运行状态的节点才能打开配置弹窗
  const nodeId = device.nodeData?.scenarioData?.id || device.nodeData?.id || device.id
  const nodeStatus = device.nodeData?.scenarioData?.status || device.nodeData?.status || 'virtual'

  // 详细的状态调试信息
  console.log('🔍 详细节点状态检查:', {
    nodeId,
    nodeStatus,
    isRunning: runningNodes.value.has(nodeId),
    runningNodesSet: Array.from(runningNodes.value),
    virtualNodesSet: Array.from(virtualNodes.value),
    deviceOpacity: device.opacity,
    deviceStroke: device.stroke,
    nodeDataStatus: device.nodeData?.status,
    scenarioDataStatus: device.nodeData?.scenarioData?.status,
    deviceData: device.nodeData,
    scenarioData: device.nodeData?.scenarioData
  })

  // 临时：如果节点看起来是实色的（opacity >= 0.9），允许点击
  const isVisuallyRunning = device.opacity >= 0.9
  console.log('🎨 视觉状态检查:', { opacity: device.opacity, isVisuallyRunning })

  // 如果是虚拟状态（半透明），不允许点击配置
  if (nodeStatus === 'virtual' && !runningNodes.value.has(nodeId) && !isVisuallyRunning) {
    console.log('⚠️ 节点处于虚拟状态，无法打开配置弹窗')
    logWarning('系统', `节点 "${device.nodeData?.name || nodeId}" 处于虚拟状态，请先部署容器后再进行配置`)
    return
  }

  // 只有运行状态的节点才能进行配置
  if (!runningNodes.value.has(nodeId) && nodeStatus !== 'running' && !isVisuallyRunning) {
    console.log('⚠️ 节点未运行，无法打开配置弹窗')
    logWarning('系统', `节点 "${device.nodeData?.name || nodeId}" 未运行，请先部署容器后再进行配置`)
    return
  }

  console.log('✅ 节点状态允许配置，打开相应弹窗')

  // 如果是攻击者，显示攻击对话框
  if (device.deviceData.name === '攻击者' ||
    device.deviceData.name === 'attacker' ||
    device.deviceData.name.toLowerCase().includes('attack') ||
    device.deviceType === 'attacker') {
    selectedAttacker.value = device
    // 获取所有可能的攻击目标（除了攻击者自己）
    attackTargets.value = Object.values(topology.devices).filter(d =>
      d !== device &&
      d.deviceData.name !== '攻击节点' &&
      !d.deviceData.name.toLowerCase().includes('attack')
    )
    showAttackerDialog.value = true
    logInfo('系统', '已打开攻击者配置对话框')
  }

  // 如果是防火墙，显示防火墙对话框
  if (device.deviceType === 'firewall') {
    selectedFirewall.value = device
    showFirewallDialog.value = true
    logInfo('系统', '已打开防火墙配置对话框')
  }

  // 如果是其他类型的设备，根据运行状态选择对话框
  if (device.deviceType !== 'firewall' &&
    device.deviceData.name !== '攻击者' &&
    device.deviceData.name !== 'attacker' &&
    !device.deviceData.name.toLowerCase().includes('attack') &&
    device.deviceType !== 'attacker') {
    // 如果是运行中的容器，显示容器配置对话框
    if (runningNodes.value.has(nodeId) || nodeStatus === 'running' || isVisuallyRunning) {
      selectedContainer.value = device
      showContainerConfigDialog.value = true
      logInfo('系统', `已打开容器 "${device.deviceData?.name || nodeId}" 配置对话框`)
    } else {
      // 否则显示主机信息对话框
      selectedHost.value = device
      showHostInfoDialog.value = true
      logInfo('系统', `已打开主机 "${device.deviceData?.name || nodeId}" 信息对话框`)
    }
  }
}

// 处理攻击进度更新事件
function handleAttackProgress(event) {
  const { taskId, status } = event.detail

  // 更新当前任务状态
  if (taskId === currentAttackTaskId.value) {
    currentAttackTaskStatus.value = status

    // 记录日志并触发对应动画
    if (status.logs && status.logs.length > 0) {
      const latestLog = status.logs[status.logs.length - 1]
      logMessage(latestLog.level, latestLog.source, latestLog.message)

      // 根据日志内容触发动画
      if (attackVisualization && selectedAttacker.value) {
        const target = Object.values(topology.devices || {}).find(d =>
          d !== selectedAttacker.value &&
          d.deviceData.name !== '攻击节点' &&
          !d.deviceData.name.toLowerCase().includes('attack')
        )
        attackVisualization.triggerAnimationFromLog(latestLog, selectedAttacker.value, target)
      }
    }

    // 根据阶段更新可视化
    updateAttackVisualizationByPhase(status.phase, status.progress)
  }
}

// 处理攻击完成事件
function handleAttackCompleted(event) {
  const { success, taskId, result, error } = event.detail

  if (taskId === currentAttackTaskId.value) {
    if (success) {
      logSuccess('攻击智能体', '攻击任务已完成')

      // 触发关键事件，通知虚拟时间轴停止
      const keyEvent = new CustomEvent('key-event', {
        detail: {
          type: 'complete',
          status: 'completed',
          message: '攻击任务已完成',
          timestamp: new Date(),
          taskId: taskId,
          result: result
        }
      })
      document.dispatchEvent(keyEvent)
      console.log('🎯 已触发攻击完成关键事件')

      // 解析结果
      if (result && result.final_output) {
        logInfo('攻击结果', result.final_output)
      }

      // 显示成功动画
      if (attackVisualization && selectedAttacker.value) {
        attackVisualization.createSuccessAnimation(selectedAttacker.value, 3)
      }
    } else {
      logError('攻击智能体', `攻击任务失败: ${error}`)
    }

    // 清除当前任务状态
    currentAttackTaskId.value = ''
    currentAttackTaskStatus.value = null
  }
}

// 处理拓扑动画事件
function handleTopologyAnimationEvent(event) {
  const { type, attackInfo, log } = event.detail

  if (!attackVisualization || !topology) {
    console.log('⚠️ 动画系统或拓扑未初始化，跳过动画')
    return
  }

  console.log('🎬 收到拓扑动画事件:', {
    type,
    stage: attackInfo?.stage,
    technique: attackInfo?.technique,
    source: attackInfo?.source_node,
    target: attackInfo?.target_node,
    status: attackInfo?.status,
    message: log?.message
  })

  // 根据攻击信息触发对应动画
  if (type === 'attack_step') {
    triggerAttackStepAnimation(attackInfo, log)
  }
}

// 根据攻击步骤触发动画（简化版）
function triggerAttackStepAnimation(attackInfo, log) {
  try {
    const { stage, technique, source_node, target_node, status, progress } = attackInfo

    // 查找对应的拓扑节点
    const sourceNode = findTopologyNode(source_node)
    const targetNode = findTopologyNode(target_node)

    console.log('🎯 触发攻击步骤动画:', {
      stage,
      technique,
      sourceNode: sourceNode?.deviceData?.name,
      targetNode: targetNode?.deviceData?.name,
      status,
      progress
    })

    // 简化的动画触发逻辑
    if (!attackVisualization) return

    // 根据攻击阶段触发基础动画
    switch (stage) {
      case 'reconnaissance':
        if (sourceNode && attackVisualization.createScanningPulse) {
          attackVisualization.createScanningPulse(sourceNode)
        }
        break
      case 'exploitation':
        if (sourceNode && targetNode && attackVisualization.createAttackPath) {
          attackVisualization.createAttackPath(sourceNode, targetNode)
        }
        break
      case 'actions_on_objectives':
        if (sourceNode && targetNode && attackVisualization.createDataTheftAnimation) {
          attackVisualization.createDataTheftAnimation(targetNode, sourceNode, 3)
        }
        break
      default:
        // 默认使用基于日志的动画触发
        if (log) {
          triggerAttackVisualizationFromLog(log)
        }
        break
    }
  } catch (error) {
    console.error('触发攻击步骤动画时出错:', error)
  }
}

// 查找拓扑节点
function findTopologyNode(nodeId) {
  if (!topology || !nodeId) return null

  console.log('🔍 查找节点:', nodeId)

  // 节点ID映射 - 根据后端实际使用的ID和前端实际设备名称
  const nodeMapping = {
    // 后端使用的ID -> 前端设备名称的可能匹配
    'internet': ['攻击者', '攻击节点', 'attacker'],
    'firewall': ['内部防火墙', '外部防火墙', '防火墙'],
    'target_host': ['PC-1', 'PC-2'],
    'pc-user': ['PC-1', 'PC-2'],
    'internal-server': ['服务器', 'WordPress网站', 'Apache_web服务器'],
    'internal-db': ['数据库', 'PostgreSQL'],
    'internal-file': ['文件服务器'],
    'dmz-web': ['WordPress网站', 'Apache_web服务器'],
    'dmz-dns': ['DNS服务器'],
    'dmz-mail': ['邮件服务器'],
    'vpn': ['VPN网关']
  }

  // 获取可能的设备名称列表
  const possibleNames = nodeMapping[nodeId] || [nodeId]

  // 在拓扑设备中查找
  const devices = Object.values(topology.devices || {})

  // 优先精确匹配
  let foundDevice = devices.find(device => {
    const deviceName = device.deviceData?.name
    return possibleNames.some(name => deviceName === name)
  })

  // 如果精确匹配失败，尝试包含匹配
  if (!foundDevice) {
    foundDevice = devices.find(device => {
      const deviceName = device.deviceData?.name
      return possibleNames.some(name =>
        deviceName?.includes(name) || name.includes(deviceName || '')
      )
    })
  }

  // 如果还是没找到，尝试设备类型匹配
  if (!foundDevice) {
    foundDevice = devices.find(device => device.deviceType === nodeId)
  }

  console.log('🎯 找到设备:', foundDevice?.deviceData?.name || '未找到')

  return foundDevice
}

// 根据攻击阶段更新可视化
function updateAttackVisualizationByPhase(phase, progress) {
  if (!attackVisualization) return

  // 获取攻击者和目标
  const attacker = selectedAttacker.value
  const target = Object.values(topology.devices).find(d =>
    d !== attacker &&
    d.deviceData.name !== '攻击节点' &&
    !d.deviceData.name.toLowerCase().includes('attack')
  )

  if (!attacker || !target) return

  // 根据阶段显示不同的动画
  switch (phase) {
    case 'reconnaissance':
      if (progress <= 5) {
        attackVisualization.createThinkingAnimation(attacker, 3)
      } else if (progress <= 10) {
        attackVisualization.createScanningPulse(target)
      }
      break
    case 'weaponization':
      if (progress <= 20) {
        attackVisualization.createThinkingAnimation(attacker, 3)
      }
      break
    case 'delivery':
      if (progress <= 35) {
        attackVisualization.createAttackPath(attacker, target)
      } else if (progress <= 45) {
        attackVisualization.createThinkingAnimation(target, 2)
      }
      break
    case 'exploitation':
      if (progress <= 60) {
        attackVisualization.updateNodeStatus(target, 'targeted')
      }
      break
    case 'installation':
      if (progress <= 75) {
        attackVisualization.updateNodeStatus(target, 'compromised')
      }
      break
    case 'command_and_control':
      if (progress <= 85) {
        attackVisualization.createDataTheftAnimation(target, attacker, 3)
      }
      break
    case 'actions_on_objectives':
      if (progress >= 95) {
        attackVisualization.createSuccessAnimation(attacker, 3)
      }
      break
  }
}

// 处理攻击事件
async function handleAttack(attackData) {
  try {
    // 检查是否为自动攻击模式（现在自动攻击就是APT攻击）
    if (attackData.attackType === 'auto') {
      // 记录APT攻击开始
      logInfo('APT攻击智能体', `${attackData.attacker.deviceData.name} 启动APT攻击活动`)

      // 添加到关键事件
      addAttackEvent(`APT攻击活动启动：开始高级持续威胁攻击`)

      // 记录详细日志
      logDebug('APT攻击智能体', '初始化APT攻击活动...')

      // 不再使用前端模拟的APT攻击序列，直接依赖后端攻击智能体的真实动作

      // 在拓扑图上显示思考动画
      if (attackVisualization && attackVisualization.createThinkingAnimation) {
        attackVisualization.createThinkingAnimation(attackData.attacker, 3)
      }

      try {
        // 调用攻击智能体服务，执行自动攻击（现在是APT攻击）
        const result = await AttackAgentService.executeAutoAttack({
          ...attackData,
          speedMultiplier: attackSpeedMultiplier.value
        })

        if (result.success) {
          // 更新当前任务ID和状态
          currentAttackTaskId.value = result.taskId
          currentAttackTaskStatus.value = result.details

          // 启动虚拟时间轴
          if (virtualTimelineRef.value) {
            virtualTimelineRef.value.startTimeline()
            console.log('🕒 APT攻击开始，自动启动虚拟时间轴')
          }

          // 记录成功消息
          logSuccess('中央智能体', '成功启动APT攻击活动')
          logInfo('APT攻击智能体', '开始执行多阶段APT攻击流程')

          // 添加到关键事件
          addAttackEvent(`APT攻击活动成功启动，开始执行多阶段攻击`)

          // 攻击可视化现在基于WebSocket日志触发，不再在此处预先触发
          console.log('🎯 APT攻击已启动，等待WebSocket日志触发动画')
        } else {
          logError('中央智能体', `APT攻击启动失败: ${result.message}`)
          addEvent({
            type: 'failure',
            message: `APT攻击启动失败: ${result.message}`
          })
        }
      } catch (error) {
        logError('中央智能体', `与APT攻击智能体通信失败: ${error.message}`)
        addEvent({
          type: 'failure',
          message: `与APT攻击智能体通信失败: ${error.message}`
        })

        // 不再使用前端模拟攻击流程
        logWarning('系统', '后端通信失败，请检查网络连接或后端服务状态')
      }
    } else if (attackData.attackType === 'phishing' || attackData.attackType === 'social_engineering') {
      // 钓鱼攻击或社会工程学攻击
      try {
        // 调用攻击智能体服务，执行社会工程学攻击
        const result = await AttackAgentService.executeSocialEngineeringAttack({
          ...attackData,
          speedMultiplier: attackSpeedMultiplier.value
        })

        if (result.success) {
          // 更新当前任务ID和状态
          if (result.taskId) {
            currentAttackTaskId.value = result.taskId
            currentAttackTaskStatus.value = result.details

            // 不再显示全屏攻击进度监控，而是使用EventMonitor中的攻击链阶段
          }

          // 记录成功消息
          logSuccess('攻击智能体', `成功执行社会工程学攻击: ${result.details.tactic || ''}`)

          // 添加到关键事件
          addAttackEvent(`社会工程学攻击成功: ${result.details.tactic || ''}`)

          // 显示钓鱼攻击可视化 - 暂时禁用
          // selectedPhishingTarget.value = attackData.target
          // currentAttackType.value = attackData.attackType
          // showPhishingAttackVisualization.value = true

          // 攻击可视化现在基于WebSocket日志触发，不再在此处预先触发
          console.log('🎯 社会工程学攻击已启动，等待WebSocket日志触发动画')
        } else {
          logError('攻击智能体', `社会工程学攻击失败: ${result.message}`)
          addEvent({
            type: 'failure',
            message: `社会工程学攻击失败: ${result.message}`
          })
        }
      } catch (error) {
        logError('攻击智能体', `社会工程学攻击执行失败: ${error.message}`)

        // 不再使用前端模拟攻击流程
        logWarning('系统', '后端通信失败，请检查网络连接或后端服务状态')
      }
    } else {
      // 其他类型的攻击
      // 记录日志
      logInfo('攻击', `${attackData.attacker.deviceData.name} 开始对 ${attackData.target.deviceData.name} 发起 ${attackData.attackName} 攻击`)

      // 添加到关键事件
      addAttackEvent(`${attackData.attacker.deviceData.name} 开始对 ${attackData.target.deviceData.name} 发起 ${attackData.attackName} 攻击`)

      // 攻击可视化现在基于WebSocket日志触发，不再在此处预先触发
      console.log('🎯 攻击已启动，等待WebSocket日志触发动画')

      // 使用攻击服务执行攻击
      const result = await AttackService.simulateAttack(attackData)

      // 记录攻击日志
      if (result.logs) {
        result.logs.forEach(log => {
          logMessage(log.level, '攻击', log.message)
        })
      }

      // 显示攻击结果
      if (result.success) {
        logSuccess('攻击', `攻击成功: ${attackData.attackName}`)
        addAttackEvent(`攻击成功: ${attackData.target.deviceData.name} 已被攻陷`)

        // 更新目标节点状态为已攻陷
        updateNodeStatus(attackData.target, 'compromised')
      } else {
        logError('攻击', `攻击失败: ${result.error || '未知错误'}`)
        addEvent({
          type: 'failure',
          message: `攻击失败: ${attackData.target.deviceData.name} 未被攻陷`
        })
      }
    }
  } catch (error) {
    console.error('攻击失败:', error)
    logError('攻击', `攻击过程中发生错误: ${error.message}`)
  }
}

// 攻击速度控制（默认0.2倍速）
const attackSpeedMultiplier = ref(0.2) // 更慢速度，便于观察攻击过程

// 判断是否应该触发攻击动画
function shouldTriggerAttackAnimation(message) {
  // 检查当前攻击任务状态
  if (currentAttackTaskId.value) {
    const taskStatus = AttackTaskService.getTaskStatus(currentAttackTaskId.value)
    if (taskStatus) {
      // 只有在攻击任务真正运行且不在准备阶段时才显示动画
      const isRunning = taskStatus.status === AttackTaskService.STATUS.RUNNING
      const isNotPreparation = taskStatus.phase !== AttackTaskService.PHASE.RECONNAISSANCE ||
        taskStatus.progress > 10 // 侦察阶段进度超过10%才算真正开始

      console.log('🎯 攻击任务状态检查:', {
        taskId: currentAttackTaskId.value,
        status: taskStatus.status,
        phase: taskStatus.phase,
        progress: taskStatus.progress,
        isRunning,
        isNotPreparation,
        shouldShow: isRunning && isNotPreparation,
        message: message.message
      })

      return isRunning && isNotPreparation
    }
  }

  // 如果没有任务状态，使用消息内容判断
  const animationType = getLogAnimationType(message.message?.toLowerCase() || '', message.source?.toLowerCase() || '')
  return animationType !== null
}

// 判断是否应该触发防御动画
function shouldTriggerDefenseAnimation(message) {
  const source = message.source || ''
  const msg = message.message || ''

  // 防御智能体来源检查
  const defenseAgentSources = [
    '威胁阻断智能体',
    '漏洞修复智能体',
    '攻击溯源智能体',
    '防御协调器'
  ]

  // 防御关键词检查
  const defenseKeywords = [
    '阻断', '封锁', '拦截', '防护',
    '修复', '补丁', '加固', '恢复',
    '溯源', '分析', '追踪', '取证',
    '防火墙', '规则更新', '安全策略'
  ]

  // 检查是否来自防御智能体
  const isDefenseAgent = defenseAgentSources.some(agent => source.includes(agent))

  // 检查是否包含防御关键词
  const hasDefenseKeyword = defenseKeywords.some(keyword => msg.includes(keyword))

  return isDefenseAgent || hasDefenseKeyword
}

// 基于防御日志触发防御可视化动画
function triggerDefenseVisualizationFromLog(logMessage) {
  try {
    if (!defenseVisualization || !topology || !topology.devices) {
      console.log('防御可视化未初始化或拓扑图不可用')
      return
    }

    const message = logMessage.message || ''
    const source = logMessage.source || ''

    console.log('🛡️ 触发防御动画:', message)

    // 根据日志内容选择目标节点
    let targetNode = null

    // 提取主机名或IP
    const hostMatch = message.match(/主机\s+([^\s]+)/) || message.match(/设备\s+([^\s]+)/)
    const ipMatch = message.match(/\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b/)

    if (hostMatch) {
      // 根据主机名查找节点
      const hostname = hostMatch[1]
      targetNode = findNodeByName(hostname) || findNodeByType('server')
    } else if (ipMatch) {
      // 根据IP查找节点
      const ip = ipMatch[0]
      targetNode = findNodeByIP(ip) || findNodeByType('firewall')
    } else {
      // 默认节点选择
      if (source.includes('威胁阻断') || message.includes('防火墙')) {
        targetNode = findNodeByType('firewall')
      } else if (source.includes('漏洞修复')) {
        targetNode = findNodeByType('server') || findNodeByType('pc')
      } else if (source.includes('攻击溯源')) {
        targetNode = findNodeByType('server')
      }
    }

    if (!targetNode) {
      console.log('未找到合适的目标节点进行防御动画')
      return
    }

    // 根据防御类型触发相应动画
    if (source.includes('威胁阻断') || message.includes('阻断') || message.includes('防火墙')) {
      defenseVisualization.createThreatBlockingAnimation(targetNode, 'threat_blocked')
    } else if (source.includes('漏洞修复') || message.includes('修复') || message.includes('补丁')) {
      defenseVisualization.createVulnerabilityFixAnimation(targetNode, 'vulnerability_fixed')
    } else if (source.includes('攻击溯源') || message.includes('溯源') || message.includes('分析')) {
      const sourceNode = findNodeByType('internet') || targetNode
      defenseVisualization.createAttackTracingAnimation(sourceNode, targetNode)
    } else if (message.includes('防火墙') && message.includes('规则')) {
      const firewallNode = findNodeByType('firewall') || targetNode
      defenseVisualization.createFirewallUpdateAnimation(firewallNode, 'rule_update')
    }

  } catch (error) {
    console.error('触发防御动画失败:', error)
  }
}

// 根据节点名称查找节点
function findNodeByName(name) {
  if (!topology || !topology.devices) return null

  for (const deviceId in topology.devices) {
    const device = topology.devices[deviceId]
    if (device.deviceData &&
      (device.deviceData.name === name ||
        device.deviceData.hostname === name ||
        deviceId.includes(name))) {
      return device
    }
  }
  return null
}

// 根据IP查找节点
function findNodeByIP(ip) {
  if (!topology || !topology.devices) return null

  for (const deviceId in topology.devices) {
    const device = topology.devices[deviceId]
    if (device.deviceData && device.deviceData.ip === ip) {
      return device
    }
  }
  return null
}

// 根据类型查找节点
function findNodeByType(nodeType) {
  if (!topology || !topology.devices) return null

  for (const deviceId in topology.devices) {
    const device = topology.devices[deviceId]
    if (device.deviceType === nodeType ||
      (device.deviceData && device.deviceData.type === nodeType)) {
      return device
    }
  }
  return null
}

// 基于真实攻击日志触发可视化动画
function triggerAttackVisualizationFromLog(logMessage) {
  try {
    if (!attackVisualization || !topology || !topology.devices) {
      console.log('⚠️ 攻击可视化未初始化或拓扑图不存在')
      return
    }

    const message = logMessage.message.toLowerCase()
    const source = logMessage.source.toLowerCase()

    // 判断日志类型并决定动画类型
    const animationType = getLogAnimationType(message, source)
    if (!animationType) {
      console.log('⏸️ 跳过无需动画的日志:', logMessage.message)
      return
    }

    console.log('🎬 处理攻击日志动画:', {
      source: logMessage.source,
      message: logMessage.message,
      level: logMessage.level,
      animationType: animationType
    })

    // 找到攻击者节点
    const attackerNode = findAttackerNode()
    if (!attackerNode) {
      console.log('⚠️ 未找到攻击者节点')
      return
    }

    // 根据日志类型触发对应的动画
    triggerAnimationByType(animationType, message, attackerNode, logMessage)

  } catch (error) {
    console.error('触发攻击可视化动画时出错:', error)
  }
}

// 判断日志类型并决定是否需要动画
function getLogAnimationType(message, source) {
  // 分析阶段的关键词
  const analysisKeywords = [
    '分析攻击路径', '分析可能的攻击路径', '正在分析目标网络拓扑', '分析目标',
    '制定攻击计划', '评估攻击策略', '选择攻击方式',
    'analyzing', 'analysis complete', 'attack analysis'
  ]

  // 扫描侦察阶段
  const scanningKeywords = [
    '开始扫描', '执行扫描', '端口扫描', '服务扫描', '漏洞扫描', '扫描防火墙',
    'port scan', 'vulnerability scan', 'scanning', 'reconnaissance'
  ]

  // 钓鱼攻击阶段
  const phishingKeywords = [
    '发送钓鱼邮件', '生成钓鱼邮件', '制作钓鱼邮件', '投递载荷',
    'phishing', 'email', 'payload delivery'
  ]

  // 漏洞利用阶段
  const exploitKeywords = [
    '利用漏洞', '执行攻击', '获取权限', '建立连接',
    'exploit', 'vulnerability exploitation', 'gaining access'
  ]

  // 后渗透阶段
  const postExploitKeywords = [
    '执行命令', '获取数据', '横向移动', '权限提升', '安装后门', '建立持久化',
    'command execution', 'data exfiltration', 'lateral movement', 'privilege escalation'
  ]

  // 根据关键词判断日志类型
  if (analysisKeywords.some(keyword => message.includes(keyword))) {
    return 'analysis'
  } else if (scanningKeywords.some(keyword => message.includes(keyword))) {
    return 'scanning'
  } else if (phishingKeywords.some(keyword => message.includes(keyword))) {
    return 'phishing'
  } else if (exploitKeywords.some(keyword => message.includes(keyword))) {
    return 'exploit'
  } else if (postExploitKeywords.some(keyword => message.includes(keyword))) {
    return 'post_exploit'
  }

  return null // 不需要动画
}

// 动画队列管理
const animationQueue = []
let isProcessingAnimations = false
const recentAnimations = new Map() // 记录最近的动画，避免重复

// 根据动画类型触发对应的动画（支持延迟和队列）
function triggerAnimationByType(animationType, message, attackerNode, logMessage) {
  console.log(`🎬 添加${animationType}类型动画到队列:`, message)

  // 检查是否是重复动画（5秒内相同类型的动画）
  const animationKey = `${animationType}_${attackerNode.id || attackerNode.deviceData?.name}`
  const now = Date.now()
  const lastAnimation = recentAnimations.get(animationKey)

  if (lastAnimation && (now - lastAnimation) < 5000) {
    console.log(`⏸️ 跳过重复动画: ${animationType}`)
    return
  }

  // 记录动画时间
  recentAnimations.set(animationKey, now)

  // 将动画添加到队列
  animationQueue.push({
    type: animationType,
    message: message,
    attackerNode: attackerNode,
    logMessage: logMessage,
    timestamp: now
  })

  // 如果没有在处理动画，开始处理队列
  if (!isProcessingAnimations) {
    processAnimationQueue()
  }
}

// 处理动画队列
async function processAnimationQueue() {
  if (isProcessingAnimations || animationQueue.length === 0) {
    return
  }

  isProcessingAnimations = true
  console.log('🎬 开始处理动画队列，当前队列长度:', animationQueue.length)

  while (animationQueue.length > 0) {
    const animation = animationQueue.shift()
    await executeAnimation(animation)

    // 动画之间的延迟，避免冲突（根据动画类型调整延迟）
    const delay = animation.type === 'analysis' ? 1500 : 600
    await new Promise(resolve => setTimeout(resolve, delay))
  }

  isProcessingAnimations = false
  console.log('🎬 动画队列处理完成')
}

// 执行单个动画
async function executeAnimation(animation) {
  const { type, message, attackerNode, logMessage } = animation
  console.log(`🎬 执行${type}类型动画:`, message)

  switch (type) {
    case 'analysis':
      await executeAnalysisAnimation(attackerNode, message)
      break

    case 'scanning':
      await executeScanningAnimation(attackerNode, message)
      break

    case 'phishing':
      await executePhishingAnimation(attackerNode, message)
      break

    case 'exploit':
      await executeExploitAnimation(attackerNode, message)
      break

    case 'post_exploit':
      await executePostExploitAnimation(attackerNode, message)
      break

    default:
      console.log('⚠️ 未知动画类型:', type)
  }
}

// 钓鱼阶段动画（更丰富）
async function executePhishingAnimation(attackerNode, message) {
  console.log('📧 执行钓鱼阶段动画')

  const targetNode = findTargetNodeFromMessage(message)
  if (!targetNode) {
    console.log('⚠️ 未找到钓鱼目标节点')
    return
  }

  // 1. 邮件制作动画
  if (attackVisualization.createThinkingAnimation) {
    attackVisualization.createThinkingAnimation(attackerNode, 1.5)
  }

  // 2. 延迟后发送邮件动画
  setTimeout(() => {
    if (attackVisualization.createPhishingEmailAnimation) {
      attackVisualization.createPhishingEmailAnimation(targetNode)
    }
  }, 1200)

  // 3. 邮件传输路径动画
  setTimeout(() => {
    if (attackVisualization.createAttackPath) {
      attackVisualization.createAttackPath(attackerNode, targetNode, {
        color: '#f59e0b',
        dashArray: [5, 5],
        label: '📧'
      })
    }
  }, 2000)

  // 4. 目标节点反应动画
  setTimeout(() => {
    if (attackVisualization.addNodePulse) {
      attackVisualization.addNodePulse(targetNode, '#f59e0b')
    }
  }, 3000)
}

// 漏洞利用阶段动画（更丰富）
async function executeExploitAnimation(attackerNode, message) {
  console.log('💥 执行漏洞利用阶段动画')

  const targetNode = findTargetNodeFromMessage(message)
  if (!targetNode) {
    console.log('⚠️ 未找到利用目标节点')
    return
  }

  // 1. 漏洞扫描动画
  if (attackVisualization.createScanningPulse) {
    attackVisualization.createScanningPulse(targetNode)
  }

  // 2. 延迟后的攻击路径
  setTimeout(() => {
    if (attackVisualization.createAttackPath) {
      attackVisualization.createAttackPath(attackerNode, targetNode, {
        color: '#dc2626',
        width: 4,
        label: '💥'
      })
    }
  }, 1000)

  // 3. 漏洞利用成功动画
  setTimeout(() => {
    if (attackVisualization.markDeviceAsCompromised) {
      attackVisualization.markDeviceAsCompromised(targetNode, 'exploit_campaign')
    }
  }, 2500)

  // 4. 建立连接动画
  setTimeout(() => {
    if (attackVisualization.createDataTheftAnimation) {
      attackVisualization.createDataTheftAnimation(targetNode, attackerNode, 2)
    }
  }, 3500)
}

// 后渗透阶段动画（更丰富）
async function executePostExploitAnimation(attackerNode, message) {
  console.log('🔧 执行后渗透阶段动画')

  const targetNode = findTargetNodeFromMessage(message)
  if (!targetNode) {
    console.log('⚠️ 未找到后渗透目标节点')
    return
  }

  if (message.includes('数据') || message.includes('窃取') || message.includes('收集')) {
    // 数据窃取动画序列
    console.log('📊 执行数据窃取动画')

    // 1. 数据搜索动画
    if (attackVisualization.createThinkingAnimation) {
      attackVisualization.createThinkingAnimation(targetNode, 2)
    }

    // 2. 数据收集动画
    setTimeout(() => {
      if (attackVisualization.createDataTheftAnimation) {
        attackVisualization.createDataTheftAnimation(targetNode, attackerNode, 4)
      }
    }, 1500)

    // 3. 数据传输动画
    setTimeout(() => {
      if (attackVisualization.startNetworkTraffic) {
        attackVisualization.startNetworkTraffic([targetNode, attackerNode], 'data-exfil')
      }
    }, 3000)

  } else if (message.includes('横向移动') || message.includes('lateral')) {
    // 横向移动动画序列
    console.log('↔️ 执行横向移动动画')

    // 1. 网络侦察动画
    const nearbyDevices = topology.canvas.getObjects().filter(obj =>
      obj.type === 'device' &&
      !obj._deleted &&
      !obj.isDeleted &&
      obj.deviceData &&
      obj !== attackerNode &&
      obj !== targetNode
    ).slice(0, 2)

    nearbyDevices.forEach((device, index) => {
      setTimeout(() => {
        if (attackVisualization.createScanningPulse) {
          attackVisualization.createScanningPulse(device)
        }
      }, index * 600)
    })

    // 2. 横向移动路径
    setTimeout(() => {
      if (nearbyDevices.length > 0 && attackVisualization.createLateralMovementAnimation) {
        attackVisualization.createLateralMovementAnimation(targetNode, nearbyDevices[0], 'lateral_campaign')
      }
    }, 2000)

  } else if (message.includes('命令') || message.includes('执行') || message.includes('控制')) {
    // 命令执行动画
    console.log('🎮 执行命令控制动画')

    // 1. 命令发送动画
    if (attackVisualization.createAttackPath) {
      attackVisualization.createAttackPath(attackerNode, targetNode, {
        color: '#8b5cf6',
        dashArray: [3, 3],
        label: '⌨️'
      })
    }

    // 2. 命令执行反馈
    setTimeout(() => {
      if (attackVisualization.addNodePulse) {
        attackVisualization.addNodePulse(targetNode, '#8b5cf6')
      }
    }, 1000)
  }
}

// 分析阶段动画（更丰富）
async function executeAnalysisAnimation(attackerNode, message) {
  console.log('🧠 执行分析阶段动画')

  // 1. 攻击者思考动画
  if (attackVisualization.createThinkingAnimation) {
    attackVisualization.createThinkingAnimation(attackerNode, 2)
  }

  // 延迟后执行全局分析
  setTimeout(() => {
    if (attackVisualization.createGlobalAnalysisAnimation) {
      attackVisualization.createGlobalAnalysisAnimation(attackerNode)
    }
  }, 1000)

  // 再延迟后显示网络流量分析
  setTimeout(() => {
    const allDevices = topology.canvas.getObjects().filter(obj =>
      obj.type === 'device' && !obj._deleted && !obj.isDeleted && obj.deviceData
    )
    if (allDevices.length > 1 && attackVisualization.startNetworkTraffic) {
      attackVisualization.startNetworkTraffic(allDevices.slice(0, 3), 'analysis-traffic')
    }
  }, 2500)
}

// 扫描阶段动画（更丰富）
async function executeScanningAnimation(attackerNode, message) {
  console.log('🔍 执行扫描阶段动画')

  // 1. 基础扫描脉冲
  if (attackVisualization.createScanningPulse) {
    attackVisualization.createScanningPulse(attackerNode)
  }

  // 2. 延迟后的目标扫描
  setTimeout(() => {
    const targetDevices = topology.canvas.getObjects().filter(obj =>
      obj.type === 'device' &&
      !obj._deleted &&
      !obj.isDeleted &&
      obj.deviceData &&
      obj !== attackerNode
    )

    // 逐个扫描目标设备
    targetDevices.slice(0, 3).forEach((device, index) => {
      setTimeout(() => {
        if (attackVisualization.createScanningPulse) {
          attackVisualization.createScanningPulse(device)
        }
      }, index * 500)
    })
  }, 1000)

  // 3. 扫描结果可视化
  setTimeout(() => {
    if (attackVisualization.createAttackSequence) {
      const targets = topology.canvas.getObjects().filter(obj =>
        obj.type === 'device' &&
        !obj._deleted &&
        !obj.isDeleted &&
        obj.deviceData &&
        obj !== attackerNode
      ).slice(0, 2)

      if (targets.length > 0) {
        attackVisualization.createAttackSequence(attackerNode, targets, 'scan-result')
      }
    }
  }, 2000)
}

// 找到攻击者节点
function findAttackerNode() {
  // 只从画布上实际存在且未被删除的设备中查找
  const canvasDevices = topology.canvas.getObjects().filter(obj =>
    obj.type === 'device' &&
    !obj._deleted &&
    !obj.isDeleted &&
    obj.deviceData
  )

  return canvasDevices.find(device =>
    device.deviceData.name.toLowerCase().includes('attack') ||
    device.deviceData.name.toLowerCase().includes('攻击') ||
    device.deviceData.ip === '192.168.100.11' ||
    device.deviceData.type === 'attacker'
  )
}



// 注意：此函数已被 triggerAnimationByType 替代

// 注意：此函数已被 triggerAnimationByType 替代

// 从攻击信息中找到目标节点
function findTargetNodeFromAttackInfo(attackInfo) {
  if (!attackInfo.target_node) return null

  // 只从画布上实际存在且未被删除的设备中查找
  const canvasDevices = topology.canvas.getObjects().filter(obj =>
    obj.type === 'device' &&
    !obj._deleted &&
    !obj.isDeleted &&
    obj.deviceData
  )

  const targetDevice = canvasDevices.find(device =>
    device.deviceData.name === attackInfo.target_node ||
    device.deviceData.ip === attackInfo.target_node ||
    device.id === attackInfo.target_node
  )

  if (targetDevice) {
    console.log(`🎯 通过攻击信息找到目标节点: ${targetDevice.deviceData.name}`)
  } else {
    console.log(`⚠️ 未找到攻击信息中的目标节点: ${attackInfo.target_node}`)
  }

  return targetDevice
}

// 从日志消息中查找目标节点
function findTargetNodeFromMessage(message, type = 'target') {
  try {
    if (!topology || !topology.devices) return null

    // 只获取画布上实际存在且未被删除的设备
    const canvasDevices = topology.canvas.getObjects().filter(obj =>
      obj.type === 'device' &&
      !obj._deleted &&
      !obj.isDeleted &&
      obj.deviceData
    )

    // 尝试从消息中提取IP地址
    const ipRegex = /(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/g
    const ips = message.match(ipRegex)

    if (ips && ips.length > 0) {
      // 如果有多个IP，根据type选择
      const targetIp = type === 'source' ? ips[0] : ips[ips.length - 1]
      const deviceByIp = canvasDevices.find(device => device.deviceData && device.deviceData.ip === targetIp)
      if (deviceByIp) {
        console.log(`🎯 通过IP找到目标节点: ${deviceByIp.deviceData.name} (${targetIp})`)
        return deviceByIp
      }
    }

    // 默认返回第一个非攻击者节点
    const targetDevice = canvasDevices.find(device =>
      device.deviceData &&
      !device.deviceData.name.toLowerCase().includes('attack') &&
      !device.deviceData.name.toLowerCase().includes('攻击') &&
      device.deviceData.ip !== '192.168.100.11'
    )

    if (targetDevice) {
      console.log(`🎯 找到默认目标节点: ${targetDevice.deviceData.name}`)
    } else {
      console.log('⚠️ 未找到合适的目标节点')
    }

    return targetDevice
  } catch (error) {
    console.error('查找目标节点时出错:', error)
    return null
  }
}

// 可视化APT攻击路径
function visualizeAPTAttackPath(attacker) {
  if (!topology || !attackVisualization) {
    console.log('⚠️ 拓扑图或攻击可视化未初始化')
    return
  }

  console.log('🕵️ 开始APT攻击路径可视化')

  // 找到所有潜在目标 - 只从画布上实际存在且未被删除的设备中查找
  const canvasDevices = topology.canvas.getObjects().filter(obj =>
    obj.type === 'device' &&
    !obj._deleted &&
    !obj.isDeleted &&
    obj.deviceData
  )
  const targets = canvasDevices.filter(d =>
    d !== attacker &&
    d.deviceData.name !== '攻击节点' &&
    !d.deviceData.name.toLowerCase().includes('attack')
  )

  if (targets.length === 0) {
    console.log('⚠️ 未找到合适的APT攻击目标')
    return
  }

  // 创建APT攻击序列动画
  if (attackVisualization.createAttackSequence) {
    attackVisualization.createAttackSequence(attacker, targets, 'apt')
  }

  // 开始连续扫描（APT特有的持续侦察）
  if (attackVisualization.startContinuousScanning) {
    attackVisualization.startContinuousScanning(targets, 'apt-reconnaissance')
  }
}

// 在拓扑图上可视化攻击路径 - 使用新的 Fabric.js 动画系统
function visualizeAttackPath(attacker, target = null) {
  if (!topology || !attackVisualization) {
    console.log('⚠️ 拓扑图或攻击可视化未初始化')
    return
  }

  console.log('🎯 开始 Fabric.js 攻击路径可视化')

  // 如果没有指定目标，寻找合适的目标
  if (!target) {
    const canvasDevices = topology.canvas.getObjects().filter(obj =>
      obj.type === 'device' &&
      !obj._deleted &&
      !obj.isDeleted &&
      obj.deviceData
    )
    target = canvasDevices.find(d =>
      d !== attacker &&
      d.deviceData.name !== '攻击节点' &&
      (d.deviceData.type === 'web' || d.deviceData.type === 'server')
    )
  }

  if (!target) {
    console.log('⚠️ 未找到合适的攻击目标')
    return
  }

  // 创建增强的攻击序列动画
  if (attackVisualization.createAttackSequence) {
    // 找到所有可能的目标 - 只从画布上实际存在且未被删除的设备中查找
    const canvasDevices = topology.canvas.getObjects().filter(obj =>
      obj.type === 'device' &&
      !obj._deleted &&
      !obj.isDeleted &&
      obj.deviceData
    )
    const allTargets = canvasDevices.filter(d =>
      d !== attacker &&
      d.deviceData.name !== '攻击节点' &&
      !d.deviceData.name.toLowerCase().includes('attack')
    )

    attackVisualization.createAttackSequence(attacker, allTargets.slice(0, 3), 'auto')

    // 开始连续扫描
    if (allTargets.length > 0) {
      attackVisualization.startContinuousScanning(allTargets, 'main-scan')
    }

    // 开始网络流量模拟
    if (canvasDevices.length > 1) {
      attackVisualization.startNetworkTraffic(canvasDevices, 'background-traffic')
    }
  } else if (attackVisualization.createAttackPath) {
    // 回退到单个攻击路径
    attackVisualization.createAttackPath(attacker, target)
  }

  if (!topology || !attackVisualization) return

  // 如果没有指定目标，则寻找可能的目标
  if (!target) {
    const canvasDevices = topology.canvas.getObjects().filter(obj =>
      obj.type === 'device' &&
      !obj._deleted &&
      !obj.isDeleted &&
      obj.deviceData
    )

    // 查找Web服务器作为第一个目标
    target = canvasDevices.find(d =>
      d.deviceData.name.includes('Web') || d.deviceType === 'web'
    )

    // 如果没有Web服务器，选择任意一个非攻击者的设备
    if (!target) {
      target = canvasDevices.find(d =>
        d !== attacker &&
        d.deviceData.name !== '攻击节点' &&
        !d.deviceData.name.toLowerCase().includes('attack')
      )
    }

    if (!target) return // 如果没有找到目标，直接返回
  }

  // 清除之前的攻击路径
  attackVisualization.clearAttackPaths()

  // 使用GSAP创建攻击动画序列
  if (attackVisualization.createAttackSequence) {
    // 使用GSAP版本的攻击可视化
    attackVisualization.createAttackSequence(attacker, target, 'phishing')
  } else {
    // 使用简单版本的攻击可视化
    // 创建攻击路径
    const path = []

    // 添加攻击者
    path.push({
      x: attacker.left,
      y: attacker.top
    })

    // 如果攻击者和目标之间有防火墙，添加防火墙作为中间点
    const firewall = Object.values(topology.devices).find(d =>
      d.deviceType === 'firewall'
    )

    if (firewall) {
      path.push({
        x: firewall.left,
        y: firewall.top
      })
    }

    // 添加目标
    path.push({
      x: target.left,
      y: target.top
    })

    // 绘制攻击路径
    attackVisualization.drawAttackPath(path, '#ff0000', 2)

    // 高亮目标节点
    updateNodeStatus(target, 'targeted')

    // 如果是数据库服务器，可能还有第二阶段攻击
    if (target.deviceType === 'web' || target.deviceData.name.includes('Web')) {
      // 寻找数据库服务器作为第二阶段目标
      const secondTarget = Object.values(topology.devices).find(d =>
        d.deviceData.name.includes('数据库') || d.deviceType === 'db'
      )

      if (secondTarget) {
        // 创建第二阶段攻击路径
        const secondPath = []

        // 添加第一个目标（现在是攻击者）
        secondPath.push({
          x: target.left,
          y: target.top
        })

        // 如果有内部防火墙，添加防火墙作为中间点
        const internalFirewall = Object.values(topology.devices).find(d =>
          d.deviceType === 'firewall' && d !== firewall
        )

        if (internalFirewall) {
          secondPath.push({
            x: internalFirewall.left,
            y: internalFirewall.top
          })
        }

        // 添加第二个目标
        secondPath.push({
          x: secondTarget.left,
          y: secondTarget.top
        })

        // 延迟绘制第二阶段攻击路径
        setTimeout(() => {
          attackVisualization.drawAttackPath(secondPath, '#ff9900', 2)
          updateNodeStatus(secondTarget, 'targeted')
        }, 5000)
      }
    }
  }
}

// 更新节点状态
function updateNodeStatus(node, status) {
  if (!node) return

  // 根据状态设置节点样式
  switch (status) {
    case 'targeted':
      // 目标被瞄准
      node.set({
        stroke: '#ff0000',
        strokeWidth: 2
      })
      break
    case 'compromised':
      // 目标已被攻陷
      node.set({
        stroke: '#ff0000',
        strokeWidth: 3,
        strokeDashArray: [5, 5]
      })
      break
    case 'normal':
    default:
      // 恢复正常状态
      node.set({
        stroke: '#ffffff',
        strokeWidth: 1,
        strokeDashArray: null
      })
      break
  }

  // 更新画布
  topology.canvas.requestRenderAll()
}



// 处理防火墙保存事件
function handleFirewallSave(firewallData) {
  logInfo('防火墙', `${selectedFirewall.value.deviceData.name} 配置已更新`)
  console.log('防火墙配置已更新:', firewallData)
}

// 处理防火墙更新事件
function handleFirewallUpdated(updateData) {
  const { action, item } = updateData

  // 记录防火墙更新日志
  switch (action) {
    case 'blacklist_add':
      logWarning('防火墙', `已将恶意IP ${item.address} 添加到黑名单: ${item.reason}`)
      break
    case 'blacklist_remove':
      logInfo('防火墙', `已从黑名单移除IP ${item.address}`)
      break
    case 'whitelist_add':
      logInfo('防火墙', `已将可信IP ${item.address} 添加到白名单: ${item.description}`)
      break
    case 'whitelist_remove':
      logWarning('防火墙', `已从白名单移除IP ${item.address}`)
      break
  }

  // 触发防火墙更新动画
  if (attackVisualization && selectedFirewall.value) {
    // 这里可以添加防火墙更新的可视化效果
    console.log('触发防火墙更新动画:', updateData)
  }
}

// 处理容器配置消息事件
function handleMessage(message) {
  const { type, text } = message

  switch (type) {
    case 'success':
      logInfo('容器配置', text)
      break
    case 'error':
      logError('容器配置', text)
      break
    case 'warning':
      logWarning('容器配置', text)
      break
    case 'info':
    default:
      logInfo('容器配置', text)
      break
  }
}

// 检查容器是否正在运行
function isContainerRunning(device) {
  if (!device) return false

  const nodeId = device.nodeData?.scenarioData?.id || device.nodeData?.id || device.id
  const nodeStatus = device.nodeData?.scenarioData?.status || device.nodeData?.status
  const isVisuallyRunning = device.opacity === 1.0 && !device.strokeDashArray?.length

  return runningNodes.value.has(nodeId) || nodeStatus === 'running' || isVisuallyRunning
}

// 打开容器配置对话框
function openContainerConfig() {
  if (!selectedObject.value) {
    logWarning('系统', '请先选择一个节点')
    return
  }

  const device = selectedObject.value

  if (!isContainerRunning(device)) {
    logWarning('系统', '只有运行中的容器才能进行配置')
    return
  }

  selectedContainer.value = device
  showContainerConfigDialog.value = true
  logInfo('系统', `已打开容器 "${device.deviceData?.name || device.id}" 配置对话框`)
}



// 全屏切换
function toggleFullScreen() {
  const elem = document.getElementById('topology-wrapper')
  if (!elem) return
  if (!document.fullscreenElement) {
    elem.requestFullscreen().catch(err => console.error(err))
  } else {
    document.exitFullscreen()
  }
  setTimeout(() => topology && topology.resizeCanvas(window.innerWidth, window.innerHeight), 300)
}

document.addEventListener('fullscreenchange', () => {
  if (topology) {
    const width = document.fullscreenElement ? window.innerWidth : 1280
    const height = document.fullscreenElement ? window.innerHeight : 720
    topology.resizeCanvas(width, height)
  }
})

// 保存拓扑图
function saveTopology() {
  if (!topology) return

  try {
    // 获取当前场景数据
    const currentData = window.getGlobalScenarioData()

    if (currentData) {
      // 保存到localStorage
      const saveData = {
        ...currentData,
        savedAt: new Date().toISOString(),
        version: '1.0'
      }

      localStorage.setItem('persistentScenarioData', JSON.stringify(saveData))
      console.log('💾 拓扑图已保存到localStorage')
      logInfo('系统', '拓扑图已保存到本地存储')

      // 也保存一个备份到sessionStorage
      sessionStorage.setItem('scenarioData', JSON.stringify(saveData))
      console.log('💾 拓扑图备份已保存到sessionStorage')

    } else {
      console.warn('⚠️ 没有可保存的场景数据')
      logWarning('系统', '没有可保存的场景数据')
    }
  } catch (error) {
    console.error('❌ 保存拓扑图失败:', error)
    logError('系统', `保存拓扑图失败: ${error.message}`)
  }
}

// 加载动态场景数据
async function loadDynamicScenario(storedData) {
  try {
    console.log('🔄 加载动态场景数据...')
    console.log('📊 输入数据结构:', Object.keys(storedData))
    console.log('📄 agentOutput长度:', storedData.agentOutput?.length || 0)
    logInfo('系统', '正在解析场景数据...')

    // 解析agentOutput中的拓扑数据
    const scenarioTopology = parseScenarioTopology(storedData.agentOutput)

    if (scenarioTopology && scenarioTopology.nodes) {
      console.log('✅ 场景拓扑解析成功')
      console.log('📊 拓扑数据概览:', {
        nodes: scenarioTopology.nodes?.length || 0,
        networks: scenarioTopology.networks?.length || 0,
        connections: scenarioTopology.connections?.length || 0
      })

      scenarioData.value = scenarioTopology
      isScenarioMode.value = true

      // 保存到全局变量，便于测试和调试
      const globalData = {
        topology: scenarioTopology,
        prompt: storedData.prompt,
        timestamp: Date.now(),
        source: 'dynamic_scenario'
      }

      if (typeof window.setGlobalScenarioData === 'function') {
        window.setGlobalScenarioData(globalData)
        console.log('💾 场景数据已保存到全局变量')
      } else {
        // 直接设置全局变量作为备选
        window.globalScenarioData = globalData
        console.log('💾 场景数据已直接保存到全局变量')
      }

      // 记录虚拟节点
      virtualNodes.value.clear()
      scenarioTopology.nodes.forEach(node => {
        if (node.status === 'virtual') {
          virtualNodes.value.add(node.id)
          console.log(`📍 记录虚拟节点: ${node.id}`)
        }
      })

      console.log(`📊 虚拟节点总数: ${virtualNodes.value.size}`)

      // 渲染半透明拓扑图
      console.log('🎨 开始渲染拓扑图...')
      renderScenarioTopology(scenarioTopology)

      logInfo('系统', `动态场景加载成功，包含 ${scenarioTopology.nodes.length} 个节点`)
      console.log('✅ 动态场景加载完成')
      return true
    } else {
      console.error('❌ 场景拓扑解析失败')
      console.log('📊 解析结果:', scenarioTopology)
      throw new Error('场景数据格式错误或解析失败')
    }
  } catch (error) {
    console.error('❌ 加载动态场景失败:', error)
    console.error('❌ 错误详情:', error.stack)
    logError('系统', `加载场景失败: ${error.message}`)

    // 如果动态解析失败，回退到预设场景
    console.log('🔄 回退到预设APT医疗场景...')
    return await loadAptMedicalScenario()
  }
}



// 获取节点边框颜色
function getNodeStrokeColor(status) {
  const strokeMap = {
    'virtual': '#bdc3c7',
    'starting': '#f39c12',
    'running': '#27ae60',
    'stopped': '#e74c3c'
  }
  return strokeMap[status] || '#bdc3c7'
}





// 解析场景拓扑数据
function parseScenarioTopology(agentOutput) {
  try {
    console.log('🔍 开始解析agentOutput:')
    console.log('📄 agentOutput长度:', agentOutput.length)
    console.log('📄 agentOutput前500字符:', agentOutput.substring(0, 500))

    // 方法1: 查找```json代码块中的JSON数据
    const jsonBlockMatch = agentOutput.match(/```json\s*([\s\S]*?)\s*```/);
    if (jsonBlockMatch) {
      const jsonStr = jsonBlockMatch[1].trim()
      console.log('🎯 找到JSON代码块:')
      console.log('📊 JSON字符串长度:', jsonStr.length)
      console.log('📊 JSON前200字符:', jsonStr.substring(0, 200) + '...')

      try {
        const parsedData = JSON.parse(jsonStr)
        console.log('✅ 成功解析JSON代码块')
        console.log('📋 解析后的数据结构:', Object.keys(parsedData))

        if (parsedData.topology) {
          console.log('🎯 找到topology字段')
          console.log('📊 topology包含的字段:', Object.keys(parsedData.topology))
          console.log('📊 节点数量:', parsedData.topology.nodes?.length || 0)
          console.log('📊 网络数量:', parsedData.topology.networks?.length || 0)
          console.log('📊 连接数量:', parsedData.topology.connections?.length || 0)

          // 直接返回场景智能体的原始topology数据
          return parsedData.topology
        } else if (parsedData.nodes) {
          console.log('🎯 找到nodes字段，数据本身就是topology格式')
          console.log('📊 节点数量:', parsedData.nodes?.length || 0)
          console.log('📊 网络数量:', parsedData.networks?.length || 0)
          console.log('📊 连接数量:', parsedData.connections?.length || 0)

          // 直接返回场景智能体的原始数据
          return parsedData
        }
      } catch (e) {
        console.error('❌ JSON代码块解析失败:', e)
        console.log('⚠️ 尝试其他解析方法...')
      }
    }

    // 方法2: 查找标准JSON格式的拓扑数据
    const jsonMatch = agentOutput.match(/\{"status":\s*"success"[^}]*"topology":\s*\{[\s\S]*?\}\s*\}/);
    if (jsonMatch) {
      const jsonStr = jsonMatch[0]
      console.log('🎯 找到标准JSON数据:', jsonStr.substring(0, 200) + '...')

      try {
        const parsedData = JSON.parse(jsonStr)
        if (parsedData.topology) {
          console.log('✅ 成功解析标准JSON拓扑数据')
          return parsedData.topology
        }
      } catch (e) {
        console.log('⚠️ 标准JSON解析失败')
      }
    }

    // 方法3: 查找任何包含topology字段的JSON对象
    const allJsonMatches = agentOutput.match(/\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}/g);
    if (allJsonMatches) {
      for (const match of allJsonMatches) {
        try {
          const parsed = JSON.parse(match)
          if (parsed.topology) {
            console.log('✅ 在JSON对象中找到拓扑数据')
            return parsed.topology
          }
        } catch (e) {
          // 忽略解析错误，继续尝试下一个
        }
      }
    }

    // 如果没有找到JSON格式，尝试解析文本格式
    console.log('⚠️ 未找到JSON格式，尝试解析文本格式...')
    return parseTextTopology(agentOutput)

  } catch (error) {
    console.error('解析场景拓扑数据失败:', error)
    return null
  }
}

// 解析文本格式的拓扑数据
function parseTextTopology(agentOutput) {
  try {
    console.log('🔍 开始解析文本格式拓扑数据...')

    const nodes = []
    const networks = []
    const connections = []

    // 解析节点信息 - 匹配新的格式
    // 格式: 1. **节点名称 (节点ID)** 或 1. **节点名称** (类型)
    const nodePattern = /\d+\.\s*\*\*([^*]+?)\s*(?:\(([^)]+)\))?\*\*[\s\S]*?(?:- 类型[：:]\s*([^\n]+))?[\s\S]*?(?:- 网络[：:]\s*([^\n]+))?[\s\S]*?(?:- IP地址[：:]\s*([^\n]+))?/g;

    let nodeMatch;
    while ((nodeMatch = nodePattern.exec(agentOutput)) !== null) {
      const [, nameAndId, typeInParens, typeAfter, network, ip] = nodeMatch;

      // 解析节点名称和ID
      let nodeName = nameAndId.trim();
      let nodeId = typeInParens || nodeName.toLowerCase().replace(/[^a-z0-9]/g, '-');
      let nodeType = typeAfter || typeInParens || 'unknown';

      // 如果名称包含类型信息，提取它
      if (nodeName.includes('(') && nodeName.includes(')')) {
        const parts = nodeName.match(/^([^(]+)\s*\(([^)]+)\)$/);
        if (parts) {
          nodeName = parts[1].trim();
          if (!typeAfter) nodeType = parts[2].trim();
        }
      }

      // 清理数据
      const cleanNetwork = network ? network.trim().replace(/`/g, '') : 'default_network';
      const cleanIp = ip ? ip.trim().replace(/`/g, '') : '192.168.1.100';

      nodes.push({
        id: nodeId,
        name: nodeName,
        type: nodeType,
        networks: [cleanNetwork],
        ip_addresses: {
          [cleanNetwork]: cleanIp
        },
        status: 'virtual'
      });
    }

    // 解析网络信息 - 匹配新的格式
    // 格式: - **网络名称**: 子网
    const networkPattern = /- \*\*([^*]+)\*\*[：:]\s*([^\n]+)/g;
    let networkMatch;
    while ((networkMatch = networkPattern.exec(agentOutput)) !== null) {
      const [, name, subnet] = networkMatch;
      networks.push({
        id: name.trim(),
        name: name.trim(),
        subnet: subnet.trim(),
        type: 'network_segment'
      });
    }

    // 如果没有找到网络，添加默认网络
    if (networks.length === 0 && nodes.length > 0) {
      const defaultNetworks = [
        { id: 'server_segment', name: 'server_segment', subnet: '192.168.200.0/24', type: 'network_segment' },
        { id: 'user_segment', name: 'user_segment', subnet: '192.168.100.0/24', type: 'network_segment' },
        { id: 'dmz_segment', name: 'dmz_segment', subnet: '172.16.100.0/24', type: 'network_segment' },
        { id: 'medical_segment', name: 'medical_segment', subnet: '192.168.101.0/24', type: 'network_segment' },
        { id: 'internet', name: 'internet', subnet: '172.203.100.0/24', type: 'network_segment' }
      ];
      networks.push(...defaultNetworks);
    }

    // 生成基本的连接关系
    if (nodes.length > 1) {
      // 连接同一网络中的节点
      const nodesByNetwork = {};
      nodes.forEach(node => {
        node.networks.forEach(network => {
          if (!nodesByNetwork[network]) nodesByNetwork[network] = [];
          nodesByNetwork[network].push(node);
        });
      });

      Object.entries(nodesByNetwork).forEach(([network, networkNodes]) => {
        for (let i = 0; i < networkNodes.length - 1; i++) {
          for (let j = i + 1; j < networkNodes.length; j++) {
            connections.push({
              id: `${networkNodes[i].id}-${networkNodes[j].id}`,
              source: networkNodes[i].id,
              target: networkNodes[j].id,
              network: network,
              type: 'ethernet'
            });
          }
        }
      });
    }

    // 如果解析到了节点，返回拓扑数据
    if (nodes.length > 0) {
      console.log(`✅ 从文本中解析出 ${nodes.length} 个节点，${networks.length} 个网络，${connections.length} 个连接`)
      return {
        nodes,
        networks,
        connections
      };
    }

    console.log('⚠️ 文本解析未找到有效的拓扑数据')
    return null

  } catch (error) {
    console.error('文本格式解析失败:', error)
    return null
  }
}

// 初始化APT场景（包含拓扑图初始化和场景数据加载）
async function initializeAPTScenario() {
  console.log('🎯 初始化APT场景...')

  // 1. 先初始化基础拓扑图
  await initializeBasicTopology()

  // 2. 加载APT医疗场景数据
  const success = await loadAptMedicalScenario()

  // 3. 如果加载成功，启用编辑模式
  if (success) {
    enableEditMode()
    logInfo('系统', 'APT场景初始化完成，编辑模式已启用')
  }

  return success
}

// 加载APT医疗场景数据（预设场景，作为回退方案）
async function loadAptMedicalScenario() {
  try {
    console.log('🔄 加载预设APT医疗场景数据...')
    logInfo('系统', '正在加载预设APT医疗场景...')

    // 从场景数据服务获取数据
    const aptScenario = await ScenarioDataService.getAptMedicalScenario()

    if (aptScenario && aptScenario.nodes) {
      scenarioData.value = aptScenario
      isScenarioMode.value = true

      // 保存到全局变量，便于测试和调试
      const globalData = {
        topology: aptScenario,
        prompt: 'APT医疗场景（预设）',
        timestamp: Date.now(),
        source: 'preset_apt_medical'
      }

      if (typeof window.setGlobalScenarioData === 'function') {
        window.setGlobalScenarioData(globalData)
        console.log('💾 预设APT场景数据已保存到全局变量')
      } else {
        // 直接设置全局变量作为备选
        window.globalScenarioData = globalData
        console.log('💾 预设APT场景数据已直接保存到全局变量')
      }

      // 记录虚拟节点
      virtualNodes.value.clear()
      aptScenario.nodes.forEach(node => {
        if (node.status === 'virtual') {
          virtualNodes.value.add(node.id)
        }
      })

      // 渲染半透明拓扑图
      renderScenarioTopology(aptScenario)

      logInfo('系统', `预设APT医疗场景加载成功，包含 ${aptScenario.nodes.length} 个节点`)
      return true
    } else {
      throw new Error('预设场景数据格式错误')
    }
  } catch (error) {
    console.error('加载预设APT医疗场景失败:', error)
    logError('系统', `加载预设场景失败: ${error.message}`)
    return false
  }
}

// 节点类型映射函数 - 将场景节点类型映射到设备类型
function mapNodeTypeToDeviceType(nodeType) {
  const typeMap = {
    'database': 'db',
    'web_server': 'web',
    'file_server': 'file',
    'dns_server': 'dns',
    'mail_server': 'mail',
    'workstation': 'pc',
    'attacker': 'pc',
    'firewall': 'firewall',
    'router': 'router',
    'switch': 'switch',
    'server': 'server',
    'medical_server': 'server',
    'vpn_server': 'vpn',
    'proxy_server': 'proxy',
    'load_balancer': 'load'
  }
  return typeMap[nodeType] || 'server' // 默认为服务器类型
}

// 渲染场景拓扑图（半透明模式）
async function renderScenarioTopology(scenarioTopology) {
  if (!topology) {
    console.error('❌ topology对象未初始化')
    return
  }

  try {
    console.log('🎨 开始渲染场景拓扑图...')
    console.log('📊 场景数据结构:', Object.keys(scenarioTopology))
    console.log('📊 节点数量:', scenarioTopology.nodes?.length || 0)
    console.log('📊 网络数量:', scenarioTopology.networks?.length || 0)
    console.log('📊 连接数量:', scenarioTopology.connections?.length || 0)

    // 清空当前拓扑图
    topology.clear()
    console.log('🧹 已清空当前拓扑图')

    // 添加节点
    if (scenarioTopology.nodes && scenarioTopology.nodes.length > 0) {
      console.log('🔧 开始添加节点...')

      // 使用 Promise.all 来等待所有节点创建完成
      const nodePromises = scenarioTopology.nodes.map(async (nodeData, index) => {
        console.log(`📍 处理节点 ${index + 1}/${scenarioTopology.nodes.length}:`, {
          id: nodeData.id,
          name: nodeData.name,
          type: nodeData.type,
          networks: nodeData.networks,
          status: nodeData.status
        })

        // 使用智能布局算法计算节点位置
        const position = calculateSmartNodePosition(nodeData, index, scenarioTopology.nodes)

        // 映射节点类型到设备类型
        const deviceType = mapNodeTypeToDeviceType(nodeData.type)

        // 获取主要IP地址
        const primaryNetwork = nodeData.networks?.[0] || 'default_network'
        const primaryIP = nodeData.ip_addresses?.[primaryNetwork] || '192.168.1.100'

        // 使用现有的 createDevice 方法
        const fabricNode = await topology.createDevice(deviceType, {
          left: position.x,
          top: position.y,
          deviceData: {
            name: nodeData.name,
            ip: primaryIP,
            description: `${nodeData.type} - ${nodeData.status || 'virtual'}`,
            // 保存原始场景数据
            scenarioData: {
              id: nodeData.id,
              networks: nodeData.networks,
              ip_addresses: nodeData.ip_addresses,
              status: nodeData.status || 'virtual',
              ports: nodeData.ports,
              environment: nodeData.environment,
              labels: nodeData.labels
            }
          }
        })

        // 设置半透明样式
        fabricNode.set({
          opacity: 0.5,
          strokeDashArray: [5, 5],
          stroke: getNodeStrokeColor(nodeData.status || 'virtual')
        })

        console.log(`✅ 节点 ${nodeData.id} 已添加到画布`)
        return fabricNode
      })

      // 等待所有节点创建完成
      await Promise.all(nodePromises)
      console.log('✅ 所有节点创建完成')
    } else {
      console.warn('⚠️ 没有找到节点数据')
    }

    // 渲染网络连线和IP标注
    console.log('🔗 开始渲染网络连线和IP标注...')
    await renderNetworkConnections(scenarioTopology)

    // 🚫 已禁用预定义连接逻辑，只使用优化后的防火墙连线
    // 这样可以避免重复连线，只保留简洁的防火墙连接
    console.log('🚫 已跳过预定义连接，只使用优化的防火墙连线逻辑')

    // 添加网络信息到元数据
    if (scenarioTopology.networks && scenarioTopology.networks.length > 0) {
      console.log('🌐 处理网络信息...')
      scenarioTopology.networks.forEach((networkData, index) => {
        console.log(`🌐 网络 ${index + 1}:`, {
          id: networkData.id,
          name: networkData.name,
          subnet: networkData.subnet,
          type: networkData.type
        })
      })
    } else {
      console.warn('⚠️ 没有找到网络数据')
    }

    // 重新渲染画布
    topology.canvas.requestRenderAll()
    console.log('🎨 画布渲染完成')

    // 启用编辑模式，使所有节点可以拖拽和选择
    enableEditMode()

    console.log('✅ 场景拓扑图渲染完成')
    logInfo('系统', '半透明拓扑图渲染完成，编辑模式已启用')

  } catch (error) {
    console.error('❌ 渲染场景拓扑图失败:', error)
    console.error('❌ 错误详情:', error.stack)
    logError('系统', `渲染失败: ${error.message}`)
  }
}

// 根据场景节点ID查找fabric设备对象
function findDeviceByScenarioId(scenarioId) {
  if (!topology || !topology.devices) return null

  // 遍历所有设备，查找匹配的场景ID
  const devices = Object.values(topology.devices)
  return devices.find(device => {
    const scenarioData = device.deviceData?.scenarioData
    return scenarioData && scenarioData.id === scenarioId
  })
}

// 分析网络拓扑结构
function analyzeNetworkTopology(allNodes) {
  const analysis = {
    networks: {},
    firewalls: [],
    attackers: [],
    servers: [],
    workstations: []
  }

  // 分析每个节点
  allNodes.forEach(node => {
    // 按类型分类
    if (node.type === 'firewall') {
      analysis.firewalls.push(node)
    } else if (node.type === 'attacker') {
      analysis.attackers.push(node)
    } else if (node.type.includes('server') || node.type === 'database') {
      analysis.servers.push(node)
    } else if (node.type === 'workstation') {
      analysis.workstations.push(node)
    }

    // 按网络分组
    const networks = node.networks || ['unknown']
    networks.forEach(network => {
      if (!analysis.networks[network]) {
        analysis.networks[network] = []
      }
      analysis.networks[network].push(node)
    })
  })

  return analysis
}

// 智能节点位置计算函数 - 基于网络安全标准拓扑
function calculateSmartNodePosition(nodeData, _, allNodes) {
  // 分析所有节点，构建网络拓扑结构
  const networkAnalysis = analyzeNetworkTopology(allNodes)

  // 使用固定坐标确保布局的一致性和美观性
  const position = calculateFixedPosition(nodeData, allNodes, networkAnalysis)
  if (position) {
    return position
  }

  // 如果没有匹配到固定位置，使用动态布局
  return calculateDynamicPosition(nodeData, allNodes)
}

// 计算固定位置（严格避免重叠的布局算法）
function calculateFixedPosition(nodeData, allNodes, networkAnalysis) {
  const name = nodeData.name?.toLowerCase() || ''
  const type = nodeData.type || ''

  // 最小间距定义 - 增加间距避免重叠
  const MIN_SPACING_X = 150  // 最小水平间距
  const MIN_SPACING_Y = 120  // 最小垂直间距

  // 1. 攻击者 - 最右侧，避免与其他节点重叠
  if (type === 'attacker') {
    return { x: 1000, y: 250 }
  }

  // 2. 防火墙 - 严格按位置排列，绝不重叠
  if (type === 'firewall') {
    if (name.includes('internal')) {
      return { x: 400, y: 250 } // 内部防火墙
    } else if (name.includes('border') || name.includes('external')) {
      return { x: 650, y: 250 } // 边界防火墙
    } else if (name.includes('db') || name.includes('database')) {
      return { x: 400, y: 350 } // 数据库防火墙，在内部防火墙正下方
    } else {
      // 其他防火墙按顺序排列，确保间距
      const firewallIndex = networkAnalysis.firewalls.findIndex(n => n.id === nodeData.id)
      return { x: 400 + firewallIndex * MIN_SPACING_X, y: 250 }
    }
  }

  // 3. DMZ区域 - 边界防火墙上方，横向排列，严格间距
  if (nodeData.networks?.[0] === 'dmz_segment') {
    if (name.includes('web')) {
      return { x: 700, y: 80 } // Web服务器
    } else if (name.includes('wordpress')) {
      return { x: 850, y: 80 } // WordPress，确保与web服务器间距150px
    } else if (name.includes('dns')) {
      return { x: 1000, y: 80 } // DNS服务器，确保与wordpress间距150px
    } else {
      const dmzNodes = allNodes.filter(n => n.networks?.[0] === 'dmz_segment')
      const nodeIndex = dmzNodes.findIndex(n => n.id === nodeData.id)
      return { x: 600 + nodeIndex * MIN_SPACING_X, y: 120 }
    }
  }

  // 4. 服务器区域 - 左上，横向排列，严格间距
  if (type.includes('server') && !type.includes('dns')) {
    if (name.includes('medical')) {
      return { x: 250, y: 480 } // 医疗文件服务器
    } else if (name.includes('crt-files') || name.includes('files')) {
      return { x: 270, y: 80 } // 文件服务器，确保与medical间距120px
    } else if (name.includes('update')) {
      return { x: 390, y: 80 } // 更新服务器，确保与files间距120px
    } else if (name.includes('syslog') || name.includes('log')) {
      return { x: 510, y: 80 } // 日志服务器，与其他服务器同一水平线
    } else {
      const serverNodes = allNodes.filter(n =>
        n.type.includes('server') &&
        !n.name?.includes('dns')
      )
      const nodeIndex = serverNodes.findIndex(n => n.id === nodeData.id)
      return { x: 150 + nodeIndex * MIN_SPACING_X, y: 150 }
    }
  }

  // 5. DNS服务器 - 如果不在DMZ，放在服务器区域右侧
  if (type === 'dns_server' || name.includes('dns')) {
    if (nodeData.networks?.[0] === 'dmz_segment') {
      return { x: 790, y: 80 } // DMZ中的DNS
    } else {
      return { x: 510, y: 80 } // 内网DNS，确保与update服务器间距120px
    }
  }

  // 6. 数据库 - 左下，横向排列，严格间距，绝对避免重叠
  if (type === 'database') {
    // 根据实际的数据库节点名称进行布局
    if (name.includes('cnt-sql')) {
      return { x: 150, y: 80 } // cnt-sql数据库
    } else if (name === 'database') {
      return { x: 350, y: 480 } // database节点，间距200px
    } else if (name.includes('medical-db')) {
      return { x: 450, y: 480 } // medical-db，间距200px
    } else {
      // 其他数据库按顺序排列
      const dbNodes = allNodes.filter(n => n.type === 'database')
      const nodeIndex = dbNodes.findIndex(n => n.id === nodeData.id)
      return { x: 150 + nodeIndex * 200, y: 480 } // 间距200px，确保不重叠
    }
  }

  // 7. 工作站 - 左侧中间，垂直排列，严格间距
  if (type === 'workstation') {
    const wsNodes = allNodes.filter(n => n.type === 'workstation')
    const nodeIndex = wsNodes.findIndex(n => n.id === nodeData.id)
    return { x: 120, y: 300 + nodeIndex * MIN_SPACING_Y } // 确保垂直间距120px
  }

  // 8. 日志服务器 - 如果不是server类型，单独处理
  if (type.includes('syslog') || (name.includes('syslog') && !type.includes('server'))) {
    return { x: 510, y: 150 } // 与服务器同一水平线
  }

  return null // 没有匹配到固定位置
}

// 计算动态位置（当固定位置不适用时的回退方案）
function calculateDynamicPosition(nodeData, allNodes) {
  const primaryNetwork = nodeData.networks?.[0] || 'default'
  const deviceType = nodeData.type

  // 动态布局配置 - 增加间距避免重叠
  const layouts = {
    'internet': { baseX: 1000, baseY: 320, spacing: 120 },
    'dmz_segment': { baseX: 800, baseY: 200, spacing: 150 },
    'server_segment': { baseX: 200, baseY: 120, spacing: 150 },
    'user_segment': { baseX: 120, baseY: 380, spacing: 120 },
    'db_segment': { baseX: 200, baseY: 480, spacing: 150 }
  }

  const layout = layouts[primaryNetwork] || layouts['server_segment']

  // 计算同类型设备的索引
  const sameTypeNodes = allNodes.filter(n =>
    n.type === deviceType &&
    n.networks?.[0] === primaryNetwork
  )
  const nodeIndex = sameTypeNodes.findIndex(n => n.id === nodeData.id)

  return {
    x: layout.baseX + (nodeIndex % 3) * layout.spacing,
    y: layout.baseY + Math.floor(nodeIndex / 3) * 120
  }
}





// 网络连线和IP标注渲染函数
async function renderNetworkConnections(scenarioTopology) {
  if (!topology || !topology.canvas) {
    console.error('❌ 拓扑图未初始化')
    return
  }

  console.log('🔗 开始渲染网络连线和IP标注...')

  const { nodes } = scenarioTopology

  // 网络颜色映射
  const networkColors = {
    'internet': '#ff6b6b',
    'dmz_segment': '#4ecdc4',
    'user_segment': '#45b7d1',
    'server_segment': '#f9ca24',
    'db_segment': '#6c5ce7',
    'medical_segment': '#a29bfe',
    'siem_segment': '#fd79a8'
  }

  // 1. 为非防火墙节点添加IP标签（显示在节点下方）
  console.log('📍 添加节点IP标签...')
  nodes.forEach(node => {
    // 跳过防火墙节点，防火墙的IP只显示在连线上
    if (node.type === 'firewall') {
      console.log(`🔥 跳过防火墙节点 ${node.id}，IP将显示在连线上`)
      return
    }

    const fabricNode = findDeviceByScenarioId(node.id)
    if (!fabricNode) return

    // 获取节点的主要IP地址
    const primaryIP = getPrimaryIP(node)
    if (!primaryIP) return

    // 创建IP标签
    const ipLabel = new fabric.Text(primaryIP, {
      left: fabricNode.left,
      top: fabricNode.top + 55, // 节点下方，增加间距避免与名称重叠
      fontSize: 10,
      fill: '#ffffff',
      textAlign: 'center',
      originX: 'center',
      originY: 'top',
      selectable: false,
      evented: false,
      nodeId: node.id,
      labelType: 'ip'
    })

    // 设置IP标签跟随节点移动
    const updateIPLabelPosition = () => {
      ipLabel.set({
        left: fabricNode.left,
        top: fabricNode.top + 55
      })
      ipLabel.setCoords()
    }

    // 为节点添加移动事件监听器
    fabricNode.on('moving', updateIPLabelPosition)

    // 将更新函数保存到标签对象上
    ipLabel.updatePosition = updateIPLabelPosition
    ipLabel.parentNode = fabricNode

    topology.canvas.add(ipLabel)
    console.log(`📍 为节点 ${node.id} 添加IP标签: ${primaryIP}，已设置移动监听器`)
  })

  // 2. 创建简化的防火墙连线（避免重复连接）
  console.log('🔗 创建简化的防火墙连线...')

  // 找到所有防火墙节点
  const firewallNodes = nodes.filter(node => node.type === 'firewall')
  console.log(`🔥 找到 ${firewallNodes.length} 个防火墙节点:`, firewallNodes.map(f => f.id))

  // 记录已连接的设备，避免重复连接
  const connectedDevices = new Set()

  // 为每个防火墙创建连线，但要确保设备只连接到正确的防火墙
  firewallNodes.forEach(firewallNode => {
    console.log(`🔥 处理防火墙: ${firewallNode.id}`)

    // 获取防火墙连接的所有网络
    const firewallNetworks = firewallNode.networks || []

    firewallNetworks.forEach(networkId => {
      // 根据网络类型决定哪些设备应该连接到这个防火墙
      let shouldConnectDevices = []

      if (firewallNode.id.includes('border')) {
        // 边界防火墙：只连接DMZ设备和Internet设备
        shouldConnectDevices = nodes.filter(node =>
          node.id !== firewallNode.id &&
          node.type !== 'firewall' &&
          node.networks &&
          node.networks.includes(networkId) &&
          (networkId === 'dmz_segment' || networkId === 'internet') &&
          !connectedDevices.has(node.id)
        )
      } else if (firewallNode.id.includes('internal')) {
        // 内部防火墙：连接服务器段和用户段设备，但不连接DMZ设备
        shouldConnectDevices = nodes.filter(node =>
          node.id !== firewallNode.id &&
          node.type !== 'firewall' &&
          node.networks &&
          node.networks.includes(networkId) &&
          (networkId === 'server_segment' || networkId === 'user_segment') &&
          !connectedDevices.has(node.id)
        )
      } else if (firewallNode.id.includes('db')) {
        // 数据库防火墙：连接数据库段和医疗段设备
        shouldConnectDevices = nodes.filter(node =>
          node.id !== firewallNode.id &&
          node.type !== 'firewall' &&
          node.networks &&
          node.networks.includes(networkId) &&
          (networkId === 'db_segment' || networkId === 'medical_segment') &&
          !connectedDevices.has(node.id)
        )
      }

      // 为防火墙与符合条件的设备创建连线
      shouldConnectDevices.forEach(device => {
        const networkColor = networkColors[networkId] || '#95a5a6'
        console.log(`🔗 创建防火墙连接: ${firewallNode.id} -> ${device.id} (${networkId})`)
        createNetworkConnection(firewallNode, device, networkId, networkColor)
        connectedDevices.add(device.id)  // 标记为已连接
      })
    })
  })

  // 特殊处理：防火墙之间的连接（只连接相邻层级）
  const borderFirewall = firewallNodes.find(fw => fw.id.includes('border'))
  const internalFirewall = firewallNodes.find(fw => fw.id.includes('internal'))
  const dbFirewall = firewallNodes.find(fw => fw.id.includes('db'))

  // 边界防火墙 <-> 内部防火墙
  if (borderFirewall && internalFirewall) {
    // 检查两个防火墙是否有共同网络
    const commonNetworks = borderFirewall.networks?.filter(net =>
      internalFirewall.networks?.includes(net)
    ) || []

    if (commonNetworks.length > 0) {
      const networkId = commonNetworks[0] // 使用第一个共同网络
      const networkColor = networkColors[networkId] || '#95a5a6'
      console.log(`🔗 创建防火墙间连接: ${borderFirewall.id} -> ${internalFirewall.id} (${networkId})`)
      createNetworkConnection(borderFirewall, internalFirewall, networkId, networkColor)
    }
  }

  // 内部防火墙 <-> 数据库防火墙
  if (internalFirewall && dbFirewall) {
    // 检查两个防火墙是否有共同网络
    const commonNetworks = internalFirewall.networks?.filter(net =>
      dbFirewall.networks?.includes(net)
    ) || []

    if (commonNetworks.length > 0) {
      const networkId = commonNetworks[0] // 使用第一个共同网络
      const networkColor = networkColors[networkId] || '#95a5a6'
      console.log(`🔗 创建防火墙间连接: ${internalFirewall.id} -> ${dbFirewall.id} (${networkId})`)
      createNetworkConnection(internalFirewall, dbFirewall, networkId, networkColor)
    }
  }

  // 3. 为防火墙连接添加IP标注（只为实际连接的设备添加）
  console.log('🔥 为防火墙连接添加IP标注...')

  // 为每个防火墙的连接添加IP标注
  firewallNodes.forEach(firewallNode => {
    const fabricFirewall = findDeviceByScenarioId(firewallNode.id)
    if (!fabricFirewall) return

    // 获取防火墙在各个网络中的IP地址
    Object.entries(firewallNode.ip_addresses || {}).forEach(([networkId, firewallIP]) => {
      // 根据防火墙类型，只为实际连接的设备添加IP标签
      let targetDevices = []

      if (firewallNode.id.includes('border')) {
        // 边界防火墙：只为DMZ和Internet设备添加IP标签
        targetDevices = nodes.filter(node =>
          node.id !== firewallNode.id &&
          node.type !== 'firewall' &&
          node.networks &&
          node.networks.includes(networkId) &&
          (networkId === 'dmz_segment' || networkId === 'internet') &&
          connectedDevices.has(node.id)
        )
      } else if (firewallNode.id.includes('internal')) {
        // 内部防火墙：只为服务器段和用户段设备添加IP标签
        targetDevices = nodes.filter(node =>
          node.id !== firewallNode.id &&
          node.type !== 'firewall' &&
          node.networks &&
          node.networks.includes(networkId) &&
          (networkId === 'server_segment' || networkId === 'user_segment') &&
          connectedDevices.has(node.id)
        )
      } else if (firewallNode.id.includes('db')) {
        // 数据库防火墙：只为数据库段和医疗段设备添加IP标签
        targetDevices = nodes.filter(node =>
          node.id !== firewallNode.id &&
          node.type !== 'firewall' &&
          node.networks &&
          node.networks.includes(networkId) &&
          (networkId === 'db_segment' || networkId === 'medical_segment') &&
          connectedDevices.has(node.id)
        )
      }

      // 为每个目标设备添加防火墙IP标注（仅在没有手动创建的IP标签时）
      targetDevices.forEach(device => {
        const fabricDevice = findDeviceByScenarioId(device.id)
        if (fabricDevice) {
          // 检查是否已经存在手动创建的防火墙IP标签
          const existingManualLabels = topology.canvas.getObjects().filter(obj =>
            obj.labelType === 'firewall-ip' &&
            ((obj.sourceNodeId === firewallNode.id && obj.targetNodeId === device.id) ||
              (obj.sourceNodeId === device.id && obj.targetNodeId === firewallNode.id))
          )

          if (existingManualLabels.length === 0) {
            console.log(`🏷️ 为防火墙 ${firewallNode.id} 在网络 ${networkId} 添加场景IP标签: ${firewallIP}`)
            addIPLabelOnConnection(fabricFirewall, fabricDevice, firewallIP, firewallNode.id, networkId)
          } else {
            console.log(`🏷️ 跳过为防火墙 ${firewallNode.id} 添加场景IP标签，已存在手动创建的标签`)
          }
        }
      })
    })
  })

  console.log('✅ 网络连线和IP标注渲染完成')
}



// 辅助函数：获取节点的主要IP地址
function getPrimaryIP(node) {
  const ipAddresses = node.ip_addresses || {}
  const ips = Object.values(ipAddresses)
  return ips.length > 0 ? ips[0] : null
}

// 创建两个节点之间的网络连线
function createNetworkConnection(node1, node2, networkId, color) {
  const fabricNode1 = findDeviceByScenarioId(node1.id)
  const fabricNode2 = findDeviceByScenarioId(node2.id)

  if (!fabricNode1 || !fabricNode2) return

  // 计算连线的起点和终点
  const startPoint = getConnectionPoint(fabricNode1)
  const endPoint = getConnectionPoint(fabricNode2)

  // 创建连线
  const line = new fabric.Line([startPoint.x, startPoint.y, endPoint.x, endPoint.y], {
    stroke: color,
    strokeWidth: 2,
    strokeDashArray: getStrokeDashArray(networkId),
    opacity: 0.7,
    selectable: false,
    evented: false,
    networkId: networkId,
    sourceNodeId: node1.id,
    targetNodeId: node2.id,
    connectionType: 'network'
  })

  // 将连线添加到画布底层
  topology.canvas.insertAt(line, 0)

  // 设置移动事件监听器，使连线能跟随节点移动
  const updateLinePosition = () => {
    const newStartPoint = getConnectionPoint(fabricNode1)
    const newEndPoint = getConnectionPoint(fabricNode2)
    line.set({
      x1: newStartPoint.x,
      y1: newStartPoint.y,
      x2: newEndPoint.x,
      y2: newEndPoint.y
    })
    line.setCoords()
    topology.canvas.requestRenderAll()
  }

  // 为两个节点添加移动事件监听器
  fabricNode1.on('moving', updateLinePosition)
  fabricNode2.on('moving', updateLinePosition)

  // 将更新函数保存到连线对象上，以便后续清理
  line.updatePosition = updateLinePosition
  line.sourceNode = fabricNode1
  line.targetNode = fabricNode2

  console.log(`🔗 创建连线: ${node1.id} -> ${node2.id} (${networkId})，已设置移动监听器`)
}

// 在连线上添加IP标签（用于防火墙）
function addIPLabelOnConnection(fabricNode1, fabricNode2, ip, nodeId, networkId) {
  // 计算连线中点
  const midX = (fabricNode1.left + fabricNode2.left) / 2
  const midY = (fabricNode1.top + fabricNode2.top) / 2

  // 计算标签偏移（避免与连线重叠）
  const angle = Math.atan2(fabricNode2.top - fabricNode1.top, fabricNode2.left - fabricNode1.left)
  const offsetDistance = 15
  const offsetX = Math.sin(angle) * offsetDistance
  const offsetY = -Math.cos(angle) * offsetDistance

  // 创建IP标签背景
  const labelBg = new fabric.Rect({
    left: midX + offsetX,
    top: midY + offsetY,
    width: ip.length * 6 + 8,
    height: 16,
    fill: 'rgba(0, 0, 0, 0.7)',
    rx: 3,
    ry: 3,
    originX: 'center',
    originY: 'center',
    selectable: false,
    evented: false,
    labelType: 'ip-bg',
    nodeId: nodeId
  })

  // 创建IP标签文本
  const ipLabel = new fabric.Text(ip, {
    left: midX + offsetX,
    top: midY + offsetY,
    fontSize: 9,
    fill: '#ffffff',
    textAlign: 'center',
    originX: 'center',
    originY: 'center',
    selectable: false,
    evented: false,
    labelType: 'ip-on-connection',
    nodeId: nodeId,
    networkId: networkId
  })

  // 设置标签更新函数
  const updateLabelPosition = () => {
    const midX = (fabricNode1.left + fabricNode2.left) / 2
    const midY = (fabricNode1.top + fabricNode2.top) / 2
    const angle = Math.atan2(fabricNode2.top - fabricNode1.top, fabricNode2.left - fabricNode1.left)
    const offsetX = Math.sin(angle) * offsetDistance
    const offsetY = -Math.cos(angle) * offsetDistance

    labelBg.set({
      left: midX + offsetX,
      top: midY + offsetY
    })
    ipLabel.set({
      left: midX + offsetX,
      top: midY + offsetY
    })
    labelBg.setCoords()
    ipLabel.setCoords()
  }

  // 为两个节点添加移动事件监听器
  fabricNode1.on('moving', updateLabelPosition)
  fabricNode2.on('moving', updateLabelPosition)

  // 将更新函数保存到标签对象上
  labelBg.updatePosition = updateLabelPosition
  ipLabel.updatePosition = updateLabelPosition
  labelBg.sourceNode = fabricNode1
  labelBg.targetNode = fabricNode2
  ipLabel.sourceNode = fabricNode1
  ipLabel.targetNode = fabricNode2

  topology.canvas.add(labelBg)
  topology.canvas.add(ipLabel)
  console.log(`🏷️ 为防火墙 ${nodeId} 在 ${networkId} 网络添加IP标签: ${ip}，已设置移动监听器`)
}

// 辅助函数：获取连线的起点/终点
function getConnectionPoint(fabricNode) {
  return {
    x: fabricNode.left,
    y: fabricNode.top
  }
}

// 辅助函数：根据网络类型获取虚线样式
function getStrokeDashArray(networkId) {
  const dashPatterns = {
    'internet': [5, 5],
    'dmz_segment': [],
    'user_segment': [3, 3],
    'server_segment': [],
    'db_segment': [2, 2],
    'medical_segment': [4, 2],
    'siem_segment': [6, 2]
  }
  return dashPatterns[networkId] || []
}

// 更新连线位置（当节点移动时调用）
function updateConnectionsForNode(nodeId) {
  if (!topology || !topology.canvas) return

  const canvas = topology.canvas
  const allObjects = canvas.getObjects()
  const fabricNode = findDeviceByScenarioId(nodeId)

  if (!fabricNode) return

  // 1. 更新场景模式的网络连线
  const relatedConnections = allObjects.filter(obj =>
    obj.connectionType === 'network' &&
    (obj.sourceNodeId === nodeId || obj.targetNodeId === nodeId)
  )

  relatedConnections.forEach(connection => {
    const sourceNode = findDeviceByScenarioId(connection.sourceNodeId)
    const targetNode = findDeviceByScenarioId(connection.targetNodeId)

    if (sourceNode && targetNode) {
      const startPoint = getConnectionPoint(sourceNode)
      const endPoint = getConnectionPoint(targetNode)

      connection.set({
        x1: startPoint.x,
        y1: startPoint.y,
        x2: endPoint.x,
        y2: endPoint.y
      })
      connection.setCoords()
    }
  })

  // 2. 更新手动创建的连线
  const manualConnections = allObjects.filter(obj =>
    obj.type === 'line' && obj.connectionData &&
    (obj.connectionData.source === nodeId || obj.connectionData.target === nodeId)
  )

  manualConnections.forEach(connection => {
    const sourceNode = findDeviceByScenarioId(connection.connectionData.source)
    const targetNode = findDeviceByScenarioId(connection.connectionData.target)

    if (sourceNode && targetNode) {
      connection.set({
        x1: sourceNode.left,
        y1: sourceNode.top,
        x2: targetNode.left,
        y2: targetNode.top
      })
      connection.setCoords()

      // 更新连线上的标签
      if (connection.labels) {
        const midX = (sourceNode.left + targetNode.left) / 2
        const midY = (sourceNode.top + targetNode.top) / 2
        const angle = Math.atan2(targetNode.top - sourceNode.top, targetNode.left - sourceNode.left)
        const offsetDistance = 15
        const offsetX = Math.sin(angle) * offsetDistance
        const offsetY = -Math.cos(angle) * offsetDistance

        connection.labels.forEach(label => {
          label.set({
            left: midX + offsetX,
            top: midY + offsetY
          })
          label.setCoords()
        })
      }
    }
  })

  // 3. 更新相关的IP标签位置
  updateIPLabelsForNode(nodeId)
  canvas.renderAll()
}

// 更新节点的IP标签位置
function updateIPLabelsForNode(nodeId) {
  if (!topology || !topology.canvas) return

  const canvas = topology.canvas
  const allObjects = canvas.getObjects()
  const fabricNode = findDeviceByScenarioId(nodeId)

  if (!fabricNode) return

  // 1. 更新节点下方的IP标签
  const nodeIPLabels = allObjects.filter(obj => obj.nodeId === nodeId)

  nodeIPLabels.forEach(label => {
    if (label.labelType === 'ip') {
      // 更新节点下方的IP标签
      label.set({
        left: fabricNode.left,
        top: fabricNode.top + 55
      })
      label.setCoords()
    }
  })

  // 2. 更新场景模式中防火墙连线上的IP标签
  const networkConnections = allObjects.filter(obj =>
    obj.connectionType === 'network' &&
    (obj.sourceNodeId === nodeId || obj.targetNodeId === nodeId)
  )

  networkConnections.forEach(connection => {
    const sourceNode = findDeviceByScenarioId(connection.sourceNodeId)
    const targetNode = findDeviceByScenarioId(connection.targetNodeId)

    if (sourceNode && targetNode) {
      // 查找与此连线相关的防火墙IP标签（场景模式使用的标签类型）
      const connectionLabels = allObjects.filter(obj =>
        (obj.labelType === 'ip-on-connection' || obj.labelType === 'ip-bg') &&
        (obj.nodeId === connection.sourceNodeId || obj.nodeId === connection.targetNodeId)
      )

      if (connectionLabels.length > 0) {
        const midX = (sourceNode.left + targetNode.left) / 2
        const midY = (sourceNode.top + targetNode.top) / 2

        const angle = Math.atan2(targetNode.top - sourceNode.top, targetNode.left - sourceNode.left)
        const offsetDistance = 15
        const offsetX = Math.sin(angle) * offsetDistance
        const offsetY = -Math.cos(angle) * offsetDistance

        connectionLabels.forEach(label => {
          label.set({
            left: midX + offsetX,
            top: midY + offsetY
          })
          label.setCoords()
        })
      }
    }
  })

  // 3. 更新手动创建连接线上的防火墙IP标签
  const manualConnections = allObjects.filter(obj =>
    obj.type === 'line' && obj.connectionData &&
    (obj.connectionData.source === nodeId || obj.connectionData.target === nodeId)
  )

  manualConnections.forEach(connection => {
    if (connection.labels) {
      const sourceNode = findDeviceByScenarioId(connection.connectionData.source)
      const targetNode = findDeviceByScenarioId(connection.connectionData.target)

      if (sourceNode && targetNode) {
        const midX = (sourceNode.left + targetNode.left) / 2
        const midY = (sourceNode.top + targetNode.top) / 2

        const angle = Math.atan2(targetNode.top - sourceNode.top, targetNode.left - sourceNode.left)
        const offsetDistance = 15
        const offsetX = Math.sin(angle) * offsetDistance
        const offsetY = -Math.cos(angle) * offsetDistance

        connection.labels.forEach(label => {
          if (label.labelType === 'firewall-ip' || label.labelType === 'firewall-ip-bg') {
            label.set({
              left: midX + offsetX,
              top: midY + offsetY
            })
            label.setCoords()
          }
        })
      }
    }
  })
}

// 清除所有网络连线和IP标签
function clearNetworkConnections() {
  if (!topology || !topology.canvas) return

  const canvas = topology.canvas
  const allObjects = canvas.getObjects()

  // 移除网络连线
  const networkConnections = allObjects.filter(obj => obj.connectionType === 'network')
  networkConnections.forEach(connection => {
    canvas.remove(connection)
  })

  // 移除IP标签
  const ipLabels = allObjects.filter(obj =>
    obj.labelType === 'ip' ||
    obj.labelType === 'ip-on-connection' ||
    obj.labelType === 'ip-bg'
  )
  ipLabels.forEach(label => {
    canvas.remove(label)
  })

  canvas.renderAll()
  console.log('🧹 已清除所有网络连线和IP标签')
}

// 全局变量保存场景数据，避免重复生成
window.globalScenarioData = null

// 设置场景数据的函数
window.setGlobalScenarioData = function (data) {
  window.globalScenarioData = data
  console.log('✅ 全局场景数据已设置，节点数量:', data?.topology?.nodes?.length || 0)
  console.log('📊 场景数据概览:', {
    nodes: data?.topology?.nodes?.length || 0,
    networks: data?.topology?.networks?.length || 0,
    connections: data?.topology?.connections?.length || 0
  })
}

// 清除保存的场景数据（用于测试）
window.clearSavedScenarioData = function () {
  localStorage.removeItem('persistentScenarioData')
  sessionStorage.removeItem('scenarioData')
  window.globalScenarioData = null
  console.log('🧹 已清除所有保存的场景数据')
}

// 获取场景数据的函数（优先级：全局 > 当前 > 空）
window.getGlobalScenarioData = function () {
  if (window.globalScenarioData) {
    console.log('📦 使用全局场景数据')
    return window.globalScenarioData
  }

  if (window.currentScenarioData?.data) {
    console.log('📦 使用当前场景数据')
    return window.currentScenarioData.data
  }

  console.log('❌ 没有可用的场景数据')
  return null
}

// 便捷测试函数
window.testNetworkRender = function () {
  console.log('🧪 测试网络连线渲染...')

  const scenarioData = window.getGlobalScenarioData()
  if (!scenarioData) {
    console.error('❌ 没有场景数据，请先调用场景智能体生成数据')
    return
  }

  if (typeof window.renderNetworkConnections === 'function') {
    window.renderNetworkConnections(scenarioData.topology)
    console.log('✅ 网络连线渲染完成')
  } else {
    console.error('❌ renderNetworkConnections 函数不存在')
  }
}

// 暴露函数到全局作用域以便调试
window.renderScenarioTopology = renderScenarioTopology
window.renderNetworkConnections = renderNetworkConnections
window.updateConnectionsForNode = updateConnectionsForNode
window.clearNetworkConnections = clearNetworkConnections
window.mapNodeTypeToDeviceType = mapNodeTypeToDeviceType
window.findDeviceByScenarioId = findDeviceByScenarioId

// 切换节点场景状态（虚拟 -> 实体）
function updateNodeScenarioStatus(nodeId, newStatus) {
  if (!topology) return

  // 使用现有的 findDeviceByScenarioId 函数查找节点
  const node = findDeviceByScenarioId(nodeId)
  if (!node) {
    console.warn(`⚠️ 未找到节点: ${nodeId}`)
    return
  }

  console.log(`🔄 更新节点状态: ${nodeId} -> ${newStatus}`)

  // 更新节点样式
  switch (newStatus) {
    case 'running':
      node.set({
        opacity: 1.0,
        strokeDashArray: [],
        stroke: '#27ae60',
        strokeWidth: 3
      })
      virtualNodes.value.delete(nodeId)
      runningNodes.value.add(nodeId)
      // 强制触发Vue响应式更新
      virtualNodes.value = new Set(virtualNodes.value)
      runningNodes.value = new Set(runningNodes.value)
      console.log(`✅ 节点 ${nodeId} 已设置为运行状态，添加到runningNodes`)
      break
    case 'starting':
      node.set({
        opacity: 0.8,
        strokeDashArray: [3, 3],
        stroke: '#f39c12',
        strokeWidth: 3
      })
      console.log(`🟡 节点 ${nodeId} 已设置为启动中状态`)
      break
    case 'stopped':
      node.set({
        opacity: 0.6,
        strokeDashArray: [5, 5],
        stroke: '#e74c3c',
        strokeWidth: 2
      })
      runningNodes.value.delete(nodeId)
      // 强制触发Vue响应式更新
      runningNodes.value = new Set(runningNodes.value)
      console.log(`🔴 节点 ${nodeId} 已设置为停止状态，从runningNodes移除`)
      break
    case 'virtual':
    default:
      node.set({
        opacity: 0.5,
        strokeDashArray: [5, 5],
        stroke: '#bdc3c7',
        strokeWidth: 2
      })
      runningNodes.value.delete(nodeId)
      virtualNodes.value.add(nodeId)
      // 强制触发Vue响应式更新
      virtualNodes.value = new Set(virtualNodes.value)
      runningNodes.value = new Set(runningNodes.value)
      console.log(`⚪ 节点 ${nodeId} 已设置为虚拟状态，添加到virtualNodes`)
      break
  }

  // 更新节点状态数据
  if (node.nodeData) {
    node.nodeData.status = newStatus
    if (node.nodeData.scenarioData) {
      node.nodeData.scenarioData.status = newStatus
    }
  }

  topology.canvas.requestRenderAll()

  // 输出当前状态统计
  console.log(`📊 状态更新后统计:`, {
    runningNodes: Array.from(runningNodes.value),
    virtualNodes: Array.from(virtualNodes.value),
    nodeOpacity: node.opacity,
    nodeStroke: node.stroke
  })
}

// 调试函数：检查所有节点状态
function debugAllNodeStatus() {
  console.log('🔍 调试：检查所有节点状态')

  if (!topology || !topology.canvas) {
    console.log('❌ 拓扑图未初始化')
    return
  }

  const allNodes = []
  topology.canvas.forEachObject((obj) => {
    if (obj.type === 'device' || obj.nodeData) {
      const nodeId = obj.nodeData?.scenarioData?.id || obj.nodeData?.id || obj.id
      allNodes.push({
        nodeId,
        name: obj.nodeData?.name,
        opacity: obj.opacity,
        stroke: obj.stroke,
        status: obj.nodeData?.status,
        scenarioStatus: obj.nodeData?.scenarioData?.status,
        isInRunningNodes: runningNodes.value.has(nodeId),
        isInVirtualNodes: virtualNodes.value.has(nodeId)
      })
    }
  })

  console.table(allNodes)
  console.log('📊 集合状态:', {
    runningNodes: Array.from(runningNodes.value),
    virtualNodes: Array.from(virtualNodes.value)
  })
}

// 调试函数：检查虚拟节点集合状态
function debugVirtualNodes() {
  console.log('🔍 虚拟节点集合调试信息:')
  console.log('virtualNodes.size:', virtualNodes.value.size)
  console.log('virtualNodes内容:', Array.from(virtualNodes.value))
  console.log('runningNodes.size:', runningNodes.value.size)
  console.log('runningNodes内容:', Array.from(runningNodes.value))

  // 检查画布上的所有节点
  const canvasNodes = []
  if (topology && topology.canvas) {
    topology.canvas.forEachObject((obj) => {
      if (obj.type === 'device' || obj.nodeData) {
        const nodeId = obj.nodeData?.scenarioData?.id || obj.nodeData?.id || obj.id
        canvasNodes.push({
          nodeId,
          objectId: obj.id,
          name: obj.nodeData?.name,
          opacity: obj.opacity,
          isInVirtualNodes: virtualNodes.value.has(nodeId),
          isInRunningNodes: runningNodes.value.has(nodeId)
        })
      }
    })
  }

  console.log('画布上的节点:', canvasNodes)
  console.log('画布节点总数:', canvasNodes.length)
  console.log('虚拟节点数量:', virtualNodes.value.size)
  console.log('运行节点数量:', runningNodes.value.size)
}

// 将调试函数暴露到全局
window.debugAllNodeStatus = debugAllNodeStatus
window.debugVirtualNodes = debugVirtualNodes


// 启用编辑模式
function enableEditMode() {
  isEditMode.value = true

  // 使所有节点可拖拽移动
  if (topology && topology.canvas) {
    let deviceCount = 0
    topology.canvas.forEachObject((obj) => {
      // 检查是否为设备节点（包括各种可能的设备类型）
      if (obj.type === 'device' ||
        obj.deviceType ||
        obj.nodeData ||
        obj.deviceData ||
        (obj.id && obj.id.includes('device'))) {

        obj.set({
          selectable: true,
          moveable: true,
          evented: true,
          hasControls: true,
          hasBorders: true,
          lockMovementX: false,
          lockMovementY: false
        })
        deviceCount++
        console.log(`✅ 设备 ${obj.id || obj.deviceData?.name || 'unknown'} 已设置为可编辑`)
      }
    })

    // 确保画布允许选择
    topology.canvas.selection = true
    topology.canvas.requestRenderAll()

    console.log(`📊 总共设置了 ${deviceCount} 个设备为可编辑状态`)
  }

  logInfo('系统', '已启用拓扑编辑模式，所有节点现在可以拖拽移动和选择')
}

// 禁用编辑模式
function disableEditMode() {
  isEditMode.value = false
  isAddingNode.value = false
  isConnectingNodes.value = false
  selectedNodeForConnection.value = null
  logInfo('系统', '已禁用拓扑编辑模式')
}

// 删除选中的节点
function deleteSelectedNode() {
  if (!topology || !topology.canvas?.getActiveObject()) {
    logWarning('系统', '请先选择要删除的节点')
    return
  }

  const selectedObject = topology.canvas.getActiveObject()

  if (selectedObject.type === 'device' || selectedObject.nodeData) {
    // 优先使用scenarioData.id，这是我们添加节点时设置的ID
    const nodeId = selectedObject.nodeData?.scenarioData?.id || selectedObject.nodeData?.id || selectedObject.id
    const nodeName = selectedObject.nodeData?.name || nodeId

    // 调试信息：删除前的状态
    console.log('🗑️ 准备删除节点:', {
      nodeId,
      nodeName,
      virtualNodesBefore: Array.from(virtualNodes.value),
      runningNodesBefore: Array.from(runningNodes.value),
      virtualNodesSize: virtualNodes.value.size,
      isInVirtualNodes: virtualNodes.value.has(nodeId),
      isInRunningNodes: runningNodes.value.has(nodeId),
      selectedObjectData: {
        id: selectedObject.id,
        nodeDataId: selectedObject.nodeData?.id,
        scenarioDataId: selectedObject.nodeData?.scenarioData?.id,
        type: selectedObject.type
      }
    })

    // 确认删除
    if (confirm(`确定要删除节点 "${nodeName}" 吗？`)) {
      // 删除相关连接
      deleteNodeConnections(nodeId)

      // 删除节点相关的所有标签（名称标签和IP标签）
      deleteNodeLabels(selectedObject)

      // 删除与该节点相关的所有防火墙IP标签
      deleteFirewallIPLabelsForNode(nodeId)

      // 从虚拟节点集合中移除
      console.log('🔍 删除前检查所有可能的节点ID:', {
        nodeId,
        selectedObjectId: selectedObject.id,
        nodeDataId: selectedObject.nodeData?.id,
        scenarioDataId: selectedObject.nodeData?.scenarioData?.id,
        virtualNodesBeforeDelete: Array.from(virtualNodes.value),
        runningNodesBeforeDelete: Array.from(runningNodes.value)
      })

      // 尝试所有可能的节点ID进行删除
      const possibleIds = [
        nodeId,
        selectedObject.id,
        selectedObject.nodeData?.id,
        selectedObject.nodeData?.scenarioData?.id
      ].filter(id => id) // 过滤掉undefined

      let wasInVirtual = false
      let wasInRunning = false

      // 尝试删除所有可能的ID
      possibleIds.forEach(id => {
        if (virtualNodes.value.has(id)) {
          virtualNodes.value.delete(id)
          wasInVirtual = true
          console.log(`✅ 从virtualNodes删除了ID: ${id}`)
        }
        if (runningNodes.value.has(id)) {
          runningNodes.value.delete(id)
          wasInRunning = true
          console.log(`✅ 从runningNodes删除了ID: ${id}`)
        }
      })

      // 强制触发Vue响应式更新
      virtualNodes.value = new Set(virtualNodes.value)
      runningNodes.value = new Set(runningNodes.value)

      // 标记节点为已删除（防止在生成拓扑数据时被包含）
      selectedObject._deleted = true
      selectedObject.isDeleted = true

      // 删除节点本身（在清理完数据后再删除）
      topology.canvas.remove(selectedObject)

      // 调试信息：删除后的状态
      console.log('🗑️ 节点删除完成:', {
        nodeId,
        nodeName,
        wasInVirtual,
        wasInRunning,
        possibleIds,
        virtualNodesAfter: Array.from(virtualNodes.value),
        runningNodesAfter: Array.from(runningNodes.value),
        virtualNodesSizeAfter: virtualNodes.value.size
      })

      topology.canvas.requestRenderAll()
      logInfo('系统', `已删除节点: ${nodeName}`)
    }
  } else {
    logWarning('系统', '选中的对象不是节点')
  }
}

// 删除节点的所有标签
function deleteNodeLabels(fabricNode) {
  if (!topology || !fabricNode) return

  const nodeId = fabricNode.nodeData?.scenarioData?.id || fabricNode.nodeData?.id || fabricNode.id

  // 查找并删除所有与该节点相关的标签
  const labelsToRemove = []

  topology.canvas.forEachObject((obj) => {
    // 删除IP标签
    if (obj.labelType === 'ip' && obj.nodeId === nodeId) {
      labelsToRemove.push(obj)
    }
    // 删除名称标签（如果有的话）
    if (obj.labelType === 'name' && obj.nodeId === nodeId) {
      labelsToRemove.push(obj)
    }
    // 删除场景模式的防火墙IP标签
    if ((obj.labelType === 'ip-on-connection' || obj.labelType === 'ip-bg') && obj.nodeId === nodeId) {
      labelsToRemove.push(obj)
    }
    // 删除手动创建的防火墙IP标签
    if ((obj.labelType === 'firewall-ip' || obj.labelType === 'firewall-ip-bg') && obj.nodeId === nodeId) {
      labelsToRemove.push(obj)
    }
    // 删除Fabric.js自带的标签
    if (obj.type === 'text' && obj.nodeId === nodeId) {
      labelsToRemove.push(obj)
    }
    // 删除与节点绑定的标签（通过label属性）
    if (fabricNode.label && obj === fabricNode.label) {
      labelsToRemove.push(obj)
    }
  })

  // 批量删除标签
  labelsToRemove.forEach(label => {
    topology.canvas.remove(label)
  })

  console.log(`🗑️ 已删除节点 ${nodeId} 的 ${labelsToRemove.length} 个标签`)
}

// 删除与节点相关的所有防火墙IP标签
function deleteFirewallIPLabelsForNode(nodeId) {
  if (!topology) return

  const labelsToRemove = []

  topology.canvas.forEachObject((obj) => {
    // 删除所有类型的防火墙IP标签
    const isFirewallIPLabel = (
      (obj.type === 'text' && (obj.labelType === 'firewall-ip' || obj.labelType === 'ip-on-connection')) ||
      (obj.type === 'rect' && (obj.labelType === 'firewall-ip-bg' || obj.labelType === 'ip-bg'))
    )

    if (isFirewallIPLabel) {
      // 检查标签是否与要删除的节点相关
      const isRelatedToNode = (
        obj.nodeId === nodeId ||
        obj.sourceNodeId === nodeId ||
        obj.targetNodeId === nodeId ||
        obj.connectionSourceId === nodeId ||
        obj.connectionTargetId === nodeId
      )

      // 检查通过parentConnection关联的标签
      if (!isRelatedToNode && obj.parentConnection && obj.parentConnection.connectionData) {
        const connData = obj.parentConnection.connectionData
        if (connData.source === nodeId || connData.target === nodeId) {
          labelsToRemove.push(obj)
          return
        }
      }

      if (isRelatedToNode) {
        labelsToRemove.push(obj)
      }
    }
  })

  // 批量删除防火墙IP标签
  labelsToRemove.forEach(label => {
    topology.canvas.remove(label)
  })

  if (labelsToRemove.length > 0) {
    console.log(`🗑️ 已删除节点 ${nodeId} 相关的 ${labelsToRemove.length} 个防火墙IP标签`)
  }
}

// 更新节点标签位置（只更新节点下方的标签，不包括连线上的IP标签）
function updateNodeLabelsPosition(fabricNode) {
  if (!topology || !fabricNode) return

  const nodeId = fabricNode.nodeData?.scenarioData?.id || fabricNode.nodeData?.id || fabricNode.id

  // 更新Fabric.js自带的标签（NetworkTopology创建的）
  if (fabricNode.label) {
    fabricNode.label.set({
      left: fabricNode.left,
      top: fabricNode.top + fabricNode.height / 2 + 20
    })
    fabricNode.label.setCoords()
  }

  // 更新所有与该节点相关的标签位置（只更新节点下方的标签）
  topology.canvas.forEachObject((obj) => {
    // 更新IP标签位置
    if (obj.labelType === 'ip' && obj.nodeId === nodeId) {
      obj.set({
        left: fabricNode.left,
        top: fabricNode.top + 55 // 节点下方
      })
      obj.setCoords()
    }

    // 更新名称标签位置
    if (obj.labelType === 'name' && obj.nodeId === nodeId) {
      obj.set({
        left: fabricNode.left,
        top: fabricNode.top + 35 // 节点下方，在IP标签上方
      })
      obj.setCoords()
    }
  })

  // 注意：连线上的防火墙IP标签由updateConnectionsForNode函数处理，避免重复调用
}

// 删除节点的所有连接
function deleteNodeConnections(nodeId) {
  if (!topology) return

  const objectsToRemove = []
  const fabricNode = findDeviceByScenarioId(nodeId)

  try {
    // 1. 删除NetworkTopology原生连线
    if (topology.connections && fabricNode) {
      const connectionsToRemove = topology.connections.filter(conn =>
        conn.source === fabricNode || conn.target === fabricNode
      )

      connectionsToRemove.forEach(conn => {
        try {
          // 删除连线及其相关标签
          if (conn.firewallIPLabel) {
            topology.canvas.remove(conn.firewallIPLabel)
          }
          if (conn.labels) {
            conn.labels.forEach(label => topology.canvas.remove(label))
          }
          topology.canvas.remove(conn)

          // 从connections数组中移除
          const index = topology.connections.indexOf(conn)
          if (index > -1) {
            topology.connections.splice(index, 1)
          }
        } catch (error) {
          console.warn('删除NetworkTopology连线时出错:', error)
        }
      })

      if (connectionsToRemove.length > 0) {
        console.log(`🗑️ 删除了 ${connectionsToRemove.length} 条NetworkTopology连线`)
      }
    }

    // 2. 删除场景模式的网络连线和手动创建的连线
    topology.canvas.forEachObject((obj) => {
      try {
        // 删除有connectionData的连线（手动创建的）
        if (obj.type === 'line' && obj.connectionData) {
          const connData = obj.connectionData
          if (connData.source === nodeId || connData.target === nodeId) {
            objectsToRemove.push(obj)
          }
        }

        // 删除网络连线（场景模式的）
        if (obj.connectionType === 'network' &&
          (obj.sourceNodeId === nodeId || obj.targetNodeId === nodeId)) {
          objectsToRemove.push(obj)
        }

        // 删除其他类型的连线
        if (obj.type === 'connection') {
          const sourceId = obj.source?.nodeData?.scenarioData?.id || obj.source?.nodeData?.id || obj.source?.id
          const targetId = obj.target?.nodeData?.scenarioData?.id || obj.target?.nodeData?.id || obj.target?.id

          if (sourceId === nodeId || targetId === nodeId) {
            objectsToRemove.push(obj)
          }
        }

        // 删除连线上的防火墙IP标签（手动创建的）
        if (obj.type === 'text' && obj.labelType === 'firewall-ip') {
          // 检查标签是否与要删除的节点相关
          if (obj.sourceNodeId === nodeId || obj.targetNodeId === nodeId) {
            objectsToRemove.push(obj)
          }
        }

        // 删除连线上的IP标签背景（手动创建的）
        if (obj.type === 'rect' && obj.labelType === 'firewall-ip-bg') {
          // 检查背景是否与要删除的节点相关
          if (obj.sourceNodeId === nodeId || obj.targetNodeId === nodeId) {
            objectsToRemove.push(obj)
          }
        }

        // 删除场景模式的防火墙IP标签
        if (obj.type === 'text' && obj.labelType === 'ip-on-connection') {
          // 检查标签是否与要删除的节点相关
          if (obj.nodeId === nodeId || obj.sourceNodeId === nodeId || obj.targetNodeId === nodeId) {
            objectsToRemove.push(obj)
          }
        }

        // 删除场景模式的IP标签背景
        if (obj.type === 'rect' && obj.labelType === 'ip-bg') {
          // 检查背景是否与要删除的节点相关
          if (obj.nodeId === nodeId || obj.sourceNodeId === nodeId || obj.targetNodeId === nodeId) {
            objectsToRemove.push(obj)
          }
        }

        // 删除其他与节点相关的连线标签
        if (obj.connectionSourceId === nodeId || obj.connectionTargetId === nodeId) {
          objectsToRemove.push(obj)
        }

        // 删除通过parentConnection关联的标签
        if (obj.parentConnection && obj.parentConnection.connectionData) {
          const connData = obj.parentConnection.connectionData
          if (connData.source === nodeId || connData.target === nodeId) {
            objectsToRemove.push(obj)
          }
        }
      } catch (error) {
        console.warn('检查连线时出错:', error)
      }
    })

    // 批量删除
    objectsToRemove.forEach(obj => {
      try {
        topology.canvas.remove(obj)
      } catch (error) {
        console.warn('删除连线时出错:', error)
      }
    })

    if (objectsToRemove.length > 0) {
      logInfo('系统', `已删除 ${objectsToRemove.length} 条相关连接`)
    }
  } catch (error) {
    console.error('删除节点连接时出错:', error)
    logError('系统', `删除连接时出错: ${error.message}`)
  }
}

// 开始添加节点模式
function startAddingNode(nodeType) {
  console.log('🎯 开始添加节点模式:', nodeType)

  // 先停止之前的添加模式（如果有）
  if (isAddingNode.value) {
    console.log('🔄 停止之前的添加模式')
    stopAddingNode()
  }

  isAddingNode.value = true
  selectedNodeType.value = nodeType

  // 确保拓扑图处于选择模式
  topology.setMode('select')

  // 延迟设置监听器，确保状态更新完成
  setTimeout(() => {
    console.log('⏰ 延迟设置监听器, isAddingNode:', isAddingNode.value)

    if (!isAddingNode.value) {
      console.log('❌ 状态已变化，取消设置监听器')
      return
    }

    // 移除之前的监听器（如果存在）
    topology.canvas.off('mouse:down', handleCanvasClickForAddNode)
    topology.canvas.off('mouse:up', handleCanvasClickForAddNode)

    // 尝试多种事件监听方式
    topology.canvas.on('mouse:up', handleCanvasClickForAddNode)

    // 同时在DOM元素上添加监听器作为备用
    const canvasElement = topology.canvas.getElement()
    if (canvasElement) {
      canvasElement.addEventListener('click', handleDOMClickForAddNode)
      console.log('✅ DOM点击监听器已设置')
    }

    console.log('✅ 画布点击监听器已设置 (mouse:up)')
  }, 100)

  logInfo('系统', `开始添加 ${nodeType.name} 节点，请在画布上点击位置`)
}

// DOM点击处理函数
async function handleDOMClickForAddNode(domEvent) {
  console.log('🖱️ DOM点击事件触发:', domEvent)

  if (!isAddingNode.value || !selectedNodeType.value) {
    console.log('❌ 添加节点条件不满足，退出')
    return
  }

  // 获取画布相对坐标
  const rect = topology.canvas.getElement().getBoundingClientRect()
  const x = domEvent.clientX - rect.left
  const y = domEvent.clientY - rect.top

  console.log('📍 DOM点击位置:', { x, y })

  // 创建模拟的Fabric事件对象
  const fabricEvent = {
    e: domEvent,
    target: null
  }

  // 设置指针位置
  topology.canvas.setPointer({ x, y })

  // 调用原始处理函数
  await handleCanvasClickForAddNode(fabricEvent)
}

// 处理画布点击添加节点
async function handleCanvasClickForAddNode(event) {
  console.log('🖱️ 画布点击事件触发:', {
    isAddingNode: isAddingNode.value,
    selectedNodeType: selectedNodeType.value,
    target: event.target,
    event: event
  })

  if (!isAddingNode.value || !selectedNodeType.value) {
    console.log('❌ 添加节点条件不满足，退出')
    return
  }

  // 如果点击的是现有设备，不创建新节点
  if (event.target && (event.target.type === 'device' || event.target.nodeData)) {
    console.log('🚫 点击了现有设备，不创建新节点')
    return
  }

  // 获取点击位置
  let pointer
  if (event.e) {
    pointer = topology.canvas.getPointer(event.e)
  } else {
    // 如果没有原始事件，使用当前鼠标位置
    pointer = topology.canvas.getPointer()
  }
  console.log('📍 点击位置:', pointer)

  // 创建新节点 - 使用 createDevice 方法
  const newNodeId = `node_${Date.now()}`
  const deviceType = mapNodeTypeToDeviceType(selectedNodeType.value.type)

  // 增加该类型节点的计数器
  nodeTypeCounters.value[selectedNodeType.value.type]++
  const nodeNumber = nodeTypeCounters.value[selectedNodeType.value.type]

  // 生成规范的节点名称
  const nodeName = `${selectedNodeType.value.name}${nodeNumber}`

  console.log(`🎯 在位置 (${pointer.x}, ${pointer.y}) 创建新节点:`, {
    nodeType: selectedNodeType.value.type,
    deviceType: deviceType,
    nodeId: newNodeId,
    nodeName: nodeName
  })

  const newNode = await topology.createDevice(deviceType, {
    left: pointer.x,
    top: pointer.y,
    deviceData: {
      id: newNodeId, // 设置节点数据的ID
      name: nodeName,
      ip: '192.168.1.100', // 默认IP，用户可以后续修改
      description: `${selectedNodeType.value.name} - 手动添加`,
      // 保存场景数据
      scenarioData: {
        id: newNodeId,
        networks: ['default_network'],
        ip_addresses: { 'default_network': '192.168.1.100' },
        status: 'virtual',
        type: selectedNodeType.value.type
      }
    }
  })

  // 确保Fabric.js对象也使用相同的ID
  newNode.set('id', newNodeId)

  // 设置半透明样式
  newNode.set({
    opacity: 0.5,
    strokeDashArray: [5, 5],
    stroke: '#bdc3c7',
    selectable: true,  // 确保节点可选择
    moveable: true,    // 确保节点可移动
    evented: true      // 确保节点可响应事件
  })

  // 添加到虚拟节点集合
  virtualNodes.value.add(newNodeId)
  // 强制触发Vue响应式更新
  virtualNodes.value = new Set(virtualNodes.value)

  // 重新渲染画布
  topology.canvas.requestRenderAll()

  // 结束添加模式
  stopAddingNode()

  logInfo('系统', `已添加 ${selectedNodeType.value.name} 节点到位置 (${Math.round(pointer.x)}, ${Math.round(pointer.y)})`)
  console.log('✅ 新节点创建成功:', newNode)


}



// 停止添加节点模式
function stopAddingNode() {
  console.log('🛑 stopAddingNode 被调用，调用栈:', new Error().stack)

  isAddingNode.value = false
  selectedNodeType.value = null

  // 移除画布点击监听
  topology.canvas.off('mouse:down', handleCanvasClickForAddNode)
  topology.canvas.off('mouse:up', handleCanvasClickForAddNode)

  // 移除DOM监听器
  const canvasElement = topology.canvas.getElement()
  if (canvasElement) {
    canvasElement.removeEventListener('click', handleDOMClickForAddNode)
    console.log('🛑 DOM点击监听器已移除')
  }

  console.log('🛑 画布点击监听器已移除')
}

// 开始连接节点模式
function startConnectingNodes() {
  isConnectingNodes.value = true
  selectedNodeForConnection.value = null

  // 禁用选中功能，避免与连接模式冲突
  topology.canvas.selection = false
  topology.canvas.forEachObject(obj => {
    if (obj.type === 'device' || obj.nodeData) {
      obj.selectable = false
    }
  })

  // 设置节点点击监听
  topology.canvas.on('mouse:down', handleNodeClickForConnection)

  logInfo('系统', '开始连接节点模式，请依次点击两个节点')
}

// 处理节点点击连接
function handleNodeClickForConnection(event) {
  if (!isConnectingNodes.value) return

  const target = event.target
  if (!target || (!target.nodeData && target.type !== 'device')) {
    console.log('🔗 点击的不是设备节点:', target)
    return
  }

  const nodeId = target.nodeData?.scenarioData?.id || target.nodeData?.id || target.id
  console.log('🔗 点击节点进行连接:', { nodeId, target })

  if (!selectedNodeForConnection.value) {
    // 选择第一个节点
    selectedNodeForConnection.value = target
    target.set({ stroke: '#e74c3c', strokeWidth: 4 })
    topology.canvas.requestRenderAll()
    logInfo('系统', `已选择第一个节点: ${target.nodeData?.name || nodeId}，请选择第二个节点`)
  } else {
    // 选择第二个节点，创建连接
    if (selectedNodeForConnection.value === target) {
      logWarning('系统', '不能连接同一个节点')
      return
    }

    createConnection(selectedNodeForConnection.value, target)
    stopConnectingNodes()
  }
}

// 创建节点间连接
function createConnection(sourceNode, targetNode) {
  const sourceId = sourceNode.nodeData?.scenarioData?.id || sourceNode.nodeData?.id || sourceNode.id
  const targetId = targetNode.nodeData?.scenarioData?.id || targetNode.nodeData?.id || targetNode.id

  console.log('🔗 创建连接:', { sourceId, targetId, sourceNode, targetNode })

  // 检查是否已存在连接
  let connectionExists = false

  // 检查NetworkTopology的连接数组
  if (topology.connections) {
    topology.connections.forEach(conn => {
      if ((conn.source === sourceNode && conn.target === targetNode) ||
        (conn.source === targetNode && conn.target === sourceNode)) {
        connectionExists = true
      }
    })
  }

  if (connectionExists) {
    logWarning('系统', '节点间已存在连接')
    return
  }

  try {
    // 使用NetworkTopology的addConnection方法
    const connection = topology.addConnection(sourceNode, targetNode, 'ethernet')

    if (connection) {
      // 为连接添加防火墙IP标签（如果其中一个节点是防火墙）
      addFirewallIPLabelForConnection(sourceNode, targetNode, connection)

      // 清理重复的防火墙IP标签和NetworkTopology自动生成的黄色标签
      setTimeout(() => {
        removeNetworkTopologyIPLabels()
        cleanupDuplicateFirewallIPLabels()
      }, 100)

      logInfo('系统', `已创建连接: ${sourceNode.nodeData?.name || sourceId} -> ${targetNode.nodeData?.name || targetId}`)
      console.log('✅ 连接创建成功:', connection)
    } else {
      logError('系统', '连接创建失败')
    }
  } catch (error) {
    console.error('❌ 创建连接时出错:', error)
    logError('系统', `创建连接失败: ${error.message}`)
  }
}

// 停止连接节点模式
function stopConnectingNodes() {
  isConnectingNodes.value = false

  // 恢复第一个节点的样式
  if (selectedNodeForConnection.value) {
    const node = selectedNodeForConnection.value
    const status = node.nodeData?.status || 'virtual'
    node.set({
      stroke: ScenarioDataService.getNodeStrokeColor(status),
      strokeWidth: status === 'virtual' ? 2 : 3
    })
    selectedNodeForConnection.value = null
  }

  // 恢复选中功能
  topology.canvas.selection = true
  topology.canvas.forEachObject(obj => {
    if (obj.type === 'device' || obj.nodeData) {
      obj.selectable = true
    }
  })

  // 移除节点点击监听
  topology.canvas.off('mouse:down', handleNodeClickForConnection)

  topology.canvas.requestRenderAll()
}

// 为连接添加防火墙IP标签
function addFirewallIPLabelForConnection(sourceNode, targetNode, connection) {
  // 检查哪个节点是防火墙
  let firewallNode = null
  let deviceNode = null

  if (isFirewallNode(sourceNode)) {
    firewallNode = sourceNode
    deviceNode = targetNode
  } else if (isFirewallNode(targetNode)) {
    firewallNode = targetNode
    deviceNode = sourceNode
  }

  // 如果没有防火墙节点，不添加IP标签
  if (!firewallNode || !deviceNode) return

  // 根据设备的网络段获取防火墙IP
  const deviceNetwork = deviceNode.nodeData?.network
  if (!deviceNetwork) {
    console.warn(`⚠️ 设备节点 ${deviceNode.nodeData?.name || deviceNode.id} 没有设置网络段，无法确定防火墙IP`)
    return
  }

  const firewallIP = getFirewallIPForNetwork(deviceNetwork)
  if (!firewallIP) {
    console.warn(`⚠️ 网络段 ${deviceNetwork} 没有对应的防火墙IP`)
    return
  }

  console.log(`🔥 为防火墙连接添加IP标签: ${firewallIP} (网络段: ${deviceNetwork})`)

  // 在连接线上添加防火墙IP标签
  const midX = (sourceNode.left + targetNode.left) / 2
  const midY = (sourceNode.top + targetNode.top) / 2

  // 计算偏移位置
  const angle = Math.atan2(targetNode.top - sourceNode.top, targetNode.left - sourceNode.left)
  const offsetDistance = 15
  const offsetX = Math.sin(angle) * offsetDistance
  const offsetY = -Math.cos(angle) * offsetDistance

  // 获取节点ID用于标签关联
  const sourceNodeId = sourceNode.nodeData?.scenarioData?.id || sourceNode.nodeData?.id || sourceNode.id
  const targetNodeId = targetNode.nodeData?.scenarioData?.id || targetNode.nodeData?.id || targetNode.id

  // 创建IP标签背景
  const labelBg = new fabric.Rect({
    left: midX + offsetX,
    top: midY + offsetY,
    width: firewallIP.length * 6 + 8,
    height: 16,
    fill: 'rgba(0, 0, 0, 0.7)',
    rx: 3,
    ry: 3,
    originX: 'center',
    originY: 'center',
    selectable: false,
    evented: false,
    labelType: 'firewall-ip-bg',
    connectionId: connection.connectionData?.id,
    sourceNodeId: sourceNodeId,
    targetNodeId: targetNodeId,
    // 绑定到连接线
    parentConnection: connection
  })

  // 创建IP标签文本
  const ipLabel = new fabric.Text(firewallIP, {
    left: midX + offsetX,
    top: midY + offsetY,
    fontSize: 9,
    fill: '#ffffff',
    textAlign: 'center',
    originX: 'center',
    originY: 'center',
    selectable: false,
    evented: false,
    labelType: 'firewall-ip',
    connectionId: connection.connectionData?.id,
    sourceNodeId: sourceNodeId,
    targetNodeId: targetNodeId,
    // 绑定到连接线
    parentConnection: connection
  })

  // 设置标签移动监听器
  const updateLabelPosition = () => {
    const midX = (sourceNode.left + targetNode.left) / 2
    const midY = (sourceNode.top + targetNode.top) / 2
    const angle = Math.atan2(targetNode.top - sourceNode.top, targetNode.left - sourceNode.left)
    const offsetDistance = 15
    const offsetX = Math.sin(angle) * offsetDistance
    const offsetY = -Math.cos(angle) * offsetDistance

    labelBg.set({
      left: midX + offsetX,
      top: midY + offsetY
    })
    labelBg.setCoords()

    ipLabel.set({
      left: midX + offsetX,
      top: midY + offsetY
    })
    ipLabel.setCoords()

    topology.canvas.requestRenderAll()
  }

  // 为两个节点添加移动事件监听器
  sourceNode.on('moving', updateLabelPosition)
  targetNode.on('moving', updateLabelPosition)

  // 将更新函数保存到标签对象上，便于后续清理
  labelBg.updatePosition = updateLabelPosition
  ipLabel.updatePosition = updateLabelPosition
  labelBg.sourceNode = sourceNode
  labelBg.targetNode = targetNode
  ipLabel.sourceNode = sourceNode
  ipLabel.targetNode = targetNode

  topology.canvas.add(labelBg)
  topology.canvas.add(ipLabel)

  // 将标签引用保存到连接线上
  if (!connection.labels) {
    connection.labels = []
  }
  connection.labels.push(labelBg, ipLabel)

  console.log(`🏷️ 为连接添加防火墙IP标签: ${firewallIP}，已设置移动监听器`)
}

// 清理所有黄色的NetworkTopology自动生成的IP标签
function removeNetworkTopologyIPLabels() {
  if (!topology) return

  const labelsToRemove = []

  topology.canvas.forEachObject((obj) => {
    // 删除NetworkTopology自动生成的黄色IP标签
    if (obj.type === 'text' && obj.fill === '#ffcc00' && obj.backgroundColor === 'rgba(0,0,0,0.5)') {
      labelsToRemove.push(obj)
    }
  })

  labelsToRemove.forEach(label => {
    topology.canvas.remove(label)
  })

  if (labelsToRemove.length > 0) {
    console.log(`🧹 已清理 ${labelsToRemove.length} 个NetworkTopology自动生成的黄色IP标签`)
    topology.canvas.requestRenderAll()
  }
}

// 清理重复的防火墙IP标签
function cleanupDuplicateFirewallIPLabels() {
  if (!topology) return

  const allLabels = topology.canvas.getObjects().filter(obj =>
    obj.labelType === 'firewall-ip' || obj.labelType === 'ip-on-connection'
  )

  const labelGroups = new Map()

  // 按连接分组标签
  allLabels.forEach(label => {
    const sourceId = label.sourceNodeId
    const targetId = label.targetNodeId

    if (sourceId && targetId) {
      const key = [sourceId, targetId].sort().join('-')
      if (!labelGroups.has(key)) {
        labelGroups.set(key, [])
      }
      labelGroups.get(key).push(label)
    }
  })

  // 删除重复的标签，保留手动创建的白色标签（firewall-ip）
  let removedCount = 0
  labelGroups.forEach((labels, key) => {
    if (labels.length > 1) {
      // 优先保留手动创建的白色标签
      const manualLabels = labels.filter(l => l.labelType === 'firewall-ip')
      const sceneLabels = labels.filter(l => l.labelType === 'ip-on-connection')

      if (manualLabels.length > 0 && sceneLabels.length > 0) {
        // 删除场景标签（黄色），保留手动标签（白色）
        sceneLabels.forEach(label => {
          // 同时删除对应的背景标签
          const bgLabel = topology.canvas.getObjects().find(obj =>
            obj.labelType === 'ip-bg' &&
            obj.sourceNodeId === label.sourceNodeId &&
            obj.targetNodeId === label.targetNodeId
          )
          if (bgLabel) {
            topology.canvas.remove(bgLabel)
            removedCount++
          }
          topology.canvas.remove(label)
          removedCount++
        })
      } else if (labels.length > 2) {
        // 如果有多个同类型标签，保留第一个
        labels.slice(1).forEach(label => {
          topology.canvas.remove(label)
          removedCount++
        })
      }
    }
  })

  if (removedCount > 0) {
    console.log(`🧹 已清理 ${removedCount} 个重复的防火墙IP标签`)
    topology.canvas.requestRenderAll()
  }
}

// 检查节点是否为防火墙
function isFirewallNode(node) {
  return node.nodeData?.type === 'firewall' ||
    node.deviceType === 'firewall' ||
    (node.nodeData?.id && node.nodeData.id.includes('firewall'))
}

// 根据网络段获取防火墙IP
function getFirewallIPForNetwork(networkId) {
  const firewallIPs = {
    'dmz_segment': '172.16.100.254',
    'server_segment': '192.168.200.254',
    'user_segment': '192.168.100.254',
    'db_segment': '192.168.214.254',
    'medical_segment': '192.168.101.254'
  }
  return firewallIPs[networkId] || null
}

// 编辑选中节点的IP
function editSelectedNodeIP() {
  const activeObject = topology.canvas.getActiveObject()
  if (!activeObject || (!activeObject.nodeData && activeObject.type !== 'device')) {
    logWarning('系统', '请先选择一个节点')
    return
  }

  const nodeData = activeObject.nodeData || activeObject
  editingNode.value = {
    id: nodeData.id || activeObject.id,
    name: nodeData.name || activeObject.id || '未命名节点',
    ip: nodeData.ip || '',
    network: nodeData.network || ''
  }

  showIPDialog.value = true
}

// 保存节点IP设置
function saveNodeIP() {
  // 验证节点名称
  if (!editingNode.value.name || editingNode.value.name.trim() === '') {
    logWarning('系统', '请输入节点名称')
    return
  }

  if (!editingNode.value.ip) {
    logWarning('系统', '请输入IP地址')
    return
  }

  // IP地址格式验证
  const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/
  if (!ipRegex.test(editingNode.value.ip)) {
    logWarning('系统', 'IP地址格式不正确')
    return
  }

  const activeObject = topology.canvas.getActiveObject()
  if (activeObject) {
    const oldName = activeObject.nodeData?.name || activeObject.id || '未命名节点'
    const newName = editingNode.value.name.trim()

    // 更新节点数据
    if (activeObject.nodeData) {
      activeObject.nodeData.name = newName
      activeObject.nodeData.ip = editingNode.value.ip
      activeObject.nodeData.network = editingNode.value.network
    } else {
      // 为新添加的节点创建nodeData
      activeObject.nodeData = {
        id: activeObject.id,
        name: newName,
        ip: editingNode.value.ip,
        network: editingNode.value.network,
        type: activeObject.deviceType || 'workstation'
      }
    }

    // 更新节点显示名称
    updateNodeDisplayName(activeObject, newName)

    // 更新或创建IP标签
    updateNodeIPLabel(activeObject)

    // 记录更新日志
    if (oldName !== newName) {
      logSuccess('系统', `节点名称已从 "${oldName}" 更新为 "${newName}"`)
    }
    logInfo('系统', `已更新节点 ${newName} 的IP: ${editingNode.value.ip}`)
  }

  closeIPDialog()
}

// 更新节点显示名称
function updateNodeDisplayName(fabricNode, newName) {
  if (!topology || !fabricNode) return

  const nodeId = fabricNode.nodeData?.scenarioData?.id || fabricNode.nodeData?.id || fabricNode.id

  // 1. 更新Fabric.js自带的标签（NetworkTopology创建的）
  if (fabricNode.label) {
    fabricNode.label.set('text', newName)
    fabricNode.label.setCoords()
  }

  // 2. 查找并更新所有与该节点相关的名称标签
  const labelsToUpdate = []

  topology.canvas.forEachObject((obj) => {
    // 更新名称标签
    if (obj.labelType === 'name' && obj.nodeId === nodeId) {
      labelsToUpdate.push(obj)
    }
    // 更新Fabric.js自带的文本标签
    if (obj.type === 'text' && obj.nodeId === nodeId && !obj.labelType) {
      labelsToUpdate.push(obj)
    }
  })

  // 批量更新标签文本
  labelsToUpdate.forEach(label => {
    label.set('text', newName)
    label.setCoords()
  })

  // 3. 如果没有找到名称标签，创建一个新的
  if (labelsToUpdate.length === 0 && !fabricNode.label) {
    const nameLabel = new fabric.Text(newName, {
      left: fabricNode.left,
      top: fabricNode.top + fabricNode.height / 2 + 35, // 在IP标签下方
      fontSize: 10,
      fill: '#ffffff',
      textAlign: 'center',
      originX: 'center',
      originY: 'top',
      selectable: false,
      evented: false,
      nodeId: nodeId,
      labelType: 'name'
    })

    // 设置名称标签跟随节点移动
    const updateNameLabelPosition = () => {
      nameLabel.set({
        left: fabricNode.left,
        top: fabricNode.top + fabricNode.height / 2 + 35
      })
      nameLabel.setCoords()
    }

    // 为节点添加移动事件监听器
    fabricNode.on('moving', updateNameLabelPosition)

    // 将更新函数保存到标签对象上
    nameLabel.updatePosition = updateNameLabelPosition
    nameLabel.parentNode = fabricNode

    topology.canvas.add(nameLabel)
    console.log(`📝 为节点 ${nodeId} 创建新的名称标签: ${newName}`)
  }

  topology.canvas.requestRenderAll()
  console.log(`📝 已更新节点 ${nodeId} 的显示名称为: ${newName}`)
}

// 关闭IP设置对话框
function closeIPDialog() {
  showIPDialog.value = false
  editingNode.value = {
    id: null,
    name: '',
    ip: '',
    network: ''
  }
}

// 更新节点IP标签
function updateNodeIPLabel(fabricNode) {
  const nodeId = fabricNode.nodeData?.scenarioData?.id || fabricNode.nodeData?.id || fabricNode.id

  // 移除旧的IP标签
  const existingLabels = topology.canvas.getObjects().filter(obj =>
    obj.labelType === 'ip' && obj.nodeId === nodeId
  )
  existingLabels.forEach(label => topology.canvas.remove(label))

  // 创建新的IP标签
  if (fabricNode.nodeData?.ip) {
    const ipLabel = new fabric.Text(fabricNode.nodeData.ip, {
      left: fabricNode.left,
      top: fabricNode.top + 55,
      fontSize: 10,
      fill: '#ffffff',
      textAlign: 'center',
      originX: 'center',
      originY: 'top',
      selectable: false,
      evented: false,
      nodeId: nodeId,
      labelType: 'ip',
      // 绑定到父节点，确保一起移动
      parentNode: fabricNode
    })

    // 设置IP标签跟随节点移动
    const updateIPLabelPosition = () => {
      ipLabel.set({
        left: fabricNode.left,
        top: fabricNode.top + 55
      })
      ipLabel.setCoords()
    }

    // 为节点添加移动事件监听器
    fabricNode.on('moving', updateIPLabelPosition)

    // 将更新函数保存到标签对象上
    ipLabel.updatePosition = updateIPLabelPosition

    topology.canvas.add(ipLabel)

    // 将标签引用保存到节点上
    if (!fabricNode.labels) {
      fabricNode.labels = []
    }
    fabricNode.labels.push(ipLabel)
  }

  topology.canvas.requestRenderAll()
}

// 部署场景容器
async function deployScenarioContainers() {
  try {
    logInfo('系统', '开始部署场景容器...')

    // 1. 检查是否有场景数据
    if (!scenarioData.value) {
      logWarning('系统', '没有场景数据，请先生成场景')
      return
    }

    // 2. 收集当前拓扑图中的所有虚拟节点
    const virtualNodesList = Array.from(virtualNodes.value)
    console.log('🔍 发现虚拟节点:', virtualNodesList)
    console.log('🔍 虚拟节点集合大小:', virtualNodes.value.size)

    // 3. 如果没有虚拟节点，从场景数据中获取所有节点
    let nodesToDeploy = virtualNodesList
    if (nodesToDeploy.length === 0 && scenarioData.value.nodes) {
      nodesToDeploy = scenarioData.value.nodes
        .filter(node => node.status === 'virtual')
        .map(node => node.id)
      console.log('📋 从场景数据中获取虚拟节点:', nodesToDeploy)
    }

    if (nodesToDeploy.length === 0) {
      logWarning('系统', '没有发现需要部署的虚拟节点')
      return
    }

    // 4. 为每个节点设置启动状态
    nodesToDeploy.forEach(nodeId => {
      updateNodeScenarioStatus(nodeId, 'starting')
    })

    // 5. 直接启动apt-ready.yml文件（已经生成好的）
    const containerInfo = await TopologyService.deployAptReadyScenario()

    // 处理场景智能体返回的数据
    console.log('🔍 容器部署响应:', containerInfo)

    if (containerInfo && containerInfo.status === 'success') {
      const deploymentData = containerInfo.data

      // 将所有场景中的虚拟节点标记为运行中
      if (scenarioData.value && scenarioData.value.nodes) {
        const deployedCount = scenarioData.value.nodes.filter(node => {
          if (node.status === 'virtual') {
            updateNodeScenarioStatus(node.id, 'running')
            logInfo('系统', `节点 ${node.id} 已启动`)
            return true
          }
          return false
        }).length

        logSuccess('系统', `apt-ready场景容器部署完成，${deployedCount} 个节点已启动`)
      } else {
        // 如果没有场景数据，尝试从部署响应中获取信息
        if (deploymentData && deploymentData.running_services) {
          deploymentData.running_services.forEach(service => {
            // 根据服务名映射到节点ID
            const nodeId = mapServiceNameToNodeId(service.name)
            if (nodeId) {
              updateNodeScenarioStatus(nodeId, 'running')
              logInfo('系统', `容器 ${service.name} (节点: ${nodeId}) 已启动`)
            }
          })
          logSuccess('系统', `场景容器部署完成，${deploymentData.running_services.length} 个容器运行中`)
        } else {
          logSuccess('系统', 'apt-ready场景容器部署完成')
        }
      }
    } else {
      throw new Error(containerInfo?.message || '容器启动失败，未返回有效信息')
    }

  } catch (error) {
    console.error('部署场景容器失败:', error)
    logError('系统', `容器部署失败: ${error.message}`)

    // 将所有启动中的节点状态重置为虚拟状态
    const virtualNodesList = Array.from(virtualNodes.value)
    virtualNodesList.forEach(nodeId => {
      updateNodeScenarioStatus(nodeId, 'virtual')
    })

    throw error
  }
}

// 生成拓扑数据用于场景智能体
function generateTopologyDataForScenario() {
  if (!topology || !topology.canvas) {
    console.error('❌ 拓扑图未初始化')
    return null
  }

  const devices = topology.canvas.getObjects().filter(obj => obj.type === 'device')
  const nodes = []

  console.log('🔍 生成拓扑数据 - 当前画布设备数量:', devices.length)
  console.log('🔍 生成拓扑数据 - 当前虚拟节点:', Array.from(virtualNodes.value))
  const networks = [
    { id: 'internet', name: 'Internet', subnet: '172.203.100.0/24' },
    { id: 'dmz_segment', name: 'DMZ', subnet: '172.16.100.0/24' },
    { id: 'user_segment', name: 'User', subnet: '192.168.100.0/24' },
    { id: 'server_segment', name: 'Server', subnet: '192.168.200.0/24' },
    { id: 'db_segment', name: 'Database', subnet: '192.168.214.0/24' },
    { id: 'medical_segment', name: 'Medical', subnet: '192.168.101.0/24' },
    { id: 'siem_segment', name: 'SIEM', subnet: '192.168.66.0/24' }
  ]

  // 为每个虚拟节点生成节点数据
  devices.forEach(device => {
    const deviceData = device.nodeData || device.deviceData || {}
    const nodeId = deviceData.scenarioData?.id || deviceData.id || device.id

    // 检查所有可能的节点ID
    const possibleIds = [
      nodeId,
      device.id,
      deviceData.id,
      deviceData.scenarioData?.id
    ].filter(id => id)

    // 只处理虚拟节点 - 检查所有可能的ID
    const isVirtualNode = possibleIds.some(id => virtualNodes.value.has(id))
    if (!isVirtualNode) {
      console.log(`🚫 跳过非虚拟节点: ${nodeId} (可能的ID: ${possibleIds.join(', ')})`)
      return
    }

    // 额外验证：确保节点确实存在于画布上且未被标记为删除
    if (device._deleted || device.isDeleted) {
      console.log(`🚫 跳过已删除的节点: ${nodeId}`)
      return
    }

    const ip = deviceData.ip || '192.168.1.100'
    const networkSegment = determineNetworkSegment(ip)

    nodes.push({
      id: nodeId,
      name: deviceData.name || nodeId,
      type: device.deviceType || 'workstation',
      networks: [networkSegment],
      ip_addresses: {
        [networkSegment]: ip
      },
      status: 'virtual'
    })

    console.log(`📦 添加节点: ${nodeId} -> ${ip} (${networkSegment})`)
  })

  return {
    nodes: nodes,
    networks: networks,
    metadata: {
      scenario: 'dynamic-deployment',
      description: '动态部署场景',
      nodeCount: nodes.length,
      networkCount: networks.length
    }
  }
}

// 生成动态场景配置（保留用于备用）
function generateDynamicScenarioConfig() {
  if (!topology || !topology.canvas) {
    console.error('❌ 拓扑图未初始化')
    return null
  }

  const devices = topology.canvas.getObjects().filter(obj => obj.type === 'device')
  const services = {}
  const networks = {
    'internet': {
      driver: 'bridge',
      ipam: {
        config: [{ subnet: '172.203.100.0/24', gateway: '172.203.100.1' }]
      }
    },
    'dmz_segment': {
      driver: 'bridge',
      ipam: {
        config: [{ subnet: '172.16.100.0/24', gateway: '172.16.100.1' }]
      }
    },
    'user_segment': {
      driver: 'bridge',
      ipam: {
        config: [{ subnet: '192.168.100.0/24', gateway: '192.168.100.1' }]
      }
    },
    'server_segment': {
      driver: 'bridge',
      ipam: {
        config: [{ subnet: '192.168.200.0/24', gateway: '192.168.200.1' }]
      }
    },
    'db_segment': {
      driver: 'bridge',
      ipam: {
        config: [{ subnet: '192.168.214.0/24', gateway: '192.168.214.1' }]
      }
    },
    'medical_segment': {
      driver: 'bridge',
      ipam: {
        config: [{ subnet: '192.168.101.0/24', gateway: '192.168.101.1' }]
      }
    },
    'siem_segment': {
      driver: 'bridge',
      ipam: {
        config: [{ subnet: '192.168.66.0/24', gateway: '192.168.66.1' }]
      }
    }
  }

  // 为每个设备生成服务配置
  devices.forEach(device => {
    const deviceData = device.nodeData || device.deviceData || {}
    const scenarioData = deviceData.scenarioData || {}
    const nodeId = deviceData.id || scenarioData.id || device.id

    console.log(`🔍 检查设备: ${nodeId}, 虚拟节点集合包含: ${virtualNodes.value.has(nodeId)}`)

    // 只处理虚拟节点
    if (!virtualNodes.value.has(nodeId)) {
      console.log(`⏭️ 跳过非虚拟节点: ${nodeId}`)
      return
    }

    const serviceName = generateServiceName(nodeId, device.deviceType)
    const ip = deviceData.ip || '192.168.1.100'
    const networkSegment = determineNetworkSegment(ip)

    // 保存服务名到节点ID的映射
    serviceToNodeMap.value.set(serviceName, nodeId)

    services[serviceName] = {
      build: `../images/${getDockerImageName(device.deviceType)}`,
      container_name: serviceName,
      environment: generateEnvironmentVars(deviceData, device.deviceType),
      networks: {
        [networkSegment]: {
          ipv4_address: ip
        }
      }
    }

    console.log(`📦 生成服务配置: ${serviceName} -> ${ip} (${networkSegment})`)
    console.log(`🗺️ 映射: ${serviceName} -> ${nodeId}`)
  })

  return {
    version: '3.8',
    services: services,
    networks: networks
  }
}

// 生成服务名称
function generateServiceName(nodeId, deviceType) {
  // 移除特殊字符，确保符合Docker服务名规范
  const cleanNodeId = nodeId.replace(/[^a-zA-Z0-9-_]/g, '-')
  return `${cleanNodeId}-${Date.now()}`
}

// 根据IP地址确定网络段
function determineNetworkSegment(ip) {
  if (ip.startsWith('172.203.100.')) return 'internet'
  if (ip.startsWith('172.16.100.')) return 'dmz_segment'
  if (ip.startsWith('192.168.100.')) return 'user_segment'
  if (ip.startsWith('192.168.200.')) return 'server_segment'
  if (ip.startsWith('192.168.214.')) return 'db_segment'
  if (ip.startsWith('192.168.101.')) return 'medical_segment'
  if (ip.startsWith('192.168.66.')) return 'siem_segment'
  return 'user_segment' // 默认网段
}

// 获取Docker镜像名称
function getDockerImageName(deviceType) {
  const imageMap = {
    'firewall': 'fw',
    'web_server': 'ws-apache',
    'database': 'db-mysql',
    'workstation': 'ws-ubuntu',
    'server': 'srv-ubuntu',
    'attacker': 'attack-node'
  }
  return imageMap[deviceType] || 'ws-ubuntu'
}

// 生成环境变量
function generateEnvironmentVars(deviceData, deviceType) {
  const baseEnv = {
    COMPANY: 'ACME_CORP',
    USERNAME: 'admin',
    PASSWORD: 'admin123',
    DEPARTMENT: '信息技术部',
    ROLE: '系统管理员',
    HOST_TYPE: deviceType.toUpperCase(),
    EMAIL: 'admin@acmecorp.com'
  }

  // 根据设备类型添加特定环境变量
  if (deviceType === 'database') {
    baseEnv.MYSQL_ROOT_PASSWORD = 'root123'
    baseEnv.MYSQL_DATABASE = 'company_db'
  }

  return Object.entries(baseEnv).map(([key, value]) => `${key}=${value}`)
}

// 服务名到节点ID的映射
function mapServiceNameToNodeId(serviceName) {
  // 首先尝试从映射表中获取
  if (serviceToNodeMap.value.has(serviceName)) {
    return serviceToNodeMap.value.get(serviceName)
  }

  // 如果映射表中没有，尝试从服务名中提取节点ID（移除时间戳后缀）
  const match = serviceName.match(/^(.+)-\d+$/)
  if (match) {
    return match[1] // 保持原始格式
  }
  return serviceName
}

// 从当前拓扑图创建简化的场景数据（用于优化连线）
function createSimplifiedScenarioFromTopology() {
  if (!topology || !topology.canvas) {
    console.error('❌ 拓扑图未初始化')
    return null
  }

  const devices = topology.canvas.getObjects().filter(obj => obj.type === 'device')
  console.log(`📊 从拓扑图中找到 ${devices.length} 个设备`)

  const nodes = []
  const networks = [
    { id: 'internet', name: 'Internet', subnet: '172.203.100.0/24' },
    { id: 'dmz_segment', name: 'DMZ', subnet: '172.16.100.0/24' },
    { id: 'user_segment', name: 'User', subnet: '192.168.100.0/24' },
    { id: 'server_segment', name: 'Server', subnet: '192.168.200.0/24' },
    { id: 'siem_segment', name: 'SIEM', subnet: '192.168.66.0/24' },
    { id: 'vpn_segment', name: 'VPN', subnet: '192.168.110.0/24' },
    { id: 'db_segment', name: 'Database', subnet: '192.168.214.0/24' }
  ]

  devices.forEach(device => {
    const deviceData = device.deviceData || {}
    const ip = deviceData.ip || '192.168.1.100'

    // 根据IP地址判断设备所属网络
    let deviceNetworks = []
    let deviceType = 'server'

    // 根据设备名称和IP确定类型和网络
    if (deviceData.name?.includes('防火墙') || deviceData.name?.includes('firewall')) {
      deviceType = 'firewall'
      // 防火墙连接多个网络
      if (deviceData.name?.includes('内部') || deviceData.name?.includes('internal')) {
        deviceNetworks = ['server_segment', 'user_segment', 'siem_segment', 'vpn_segment', 'db_segment']
      } else if (deviceData.name?.includes('外部') || deviceData.name?.includes('border') || deviceData.name?.includes('dmz')) {
        deviceNetworks = ['internet', 'dmz_segment']
      }
    } else {
      // 根据IP地址确定网络
      if (ip.startsWith('172.203.100.')) {
        deviceNetworks = ['internet']
        deviceType = 'network'
      } else if (ip.startsWith('172.16.100.')) {
        deviceNetworks = ['dmz_segment']
        deviceType = deviceData.name?.includes('web') || deviceData.name?.includes('Apache') || deviceData.name?.includes('WordPress') ? 'web_server' : 'server'
      } else if (ip.startsWith('192.168.100.')) {
        deviceNetworks = ['user_segment']
        deviceType = 'workstation'
      } else if (ip.startsWith('192.168.200.')) {
        deviceNetworks = ['server_segment']
        deviceType = deviceData.name?.includes('数据库') || deviceData.name?.includes('SQL') ? 'database' : 'server'
      } else if (ip.startsWith('192.168.66.')) {
        deviceNetworks = ['siem_segment']
        deviceType = 'server'
      } else if (ip.startsWith('192.168.110.')) {
        deviceNetworks = ['vpn_segment']
        deviceType = 'server'
      } else if (ip.startsWith('192.168.214.')) {
        deviceNetworks = ['db_segment']
        deviceType = 'database'
      }
    }

    const node = {
      id: deviceData.name?.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase() || `device-${nodes.length}`,
      name: deviceData.name || 'Unknown Device',
      type: deviceType,
      networks: deviceNetworks,
      ip_addresses: {}
    }

    // 为每个网络设置IP地址
    deviceNetworks.forEach(network => {
      node.ip_addresses[network] = ip
    })

    nodes.push(node)
    console.log(`📍 添加设备: ${node.name} (${node.type}) -> ${deviceNetworks.join(', ')}`)
  })

  const scenarioData = {
    nodes,
    networks,
    // 明确不包含预定义连接，让优化的连线逻辑处理
    connections: []
  }
  console.log('📊 创建的简化场景数据:', scenarioData)
  return scenarioData
}

// 优化的网络连线渲染函数（只包含防火墙连线逻辑，不包含预定义连接）
async function renderOptimizedNetworkConnections(scenarioTopology) {
  if (!topology || !topology.canvas) {
    console.error('❌ 拓扑图未初始化')
    return
  }

  console.log('🔗 开始渲染优化的网络连线...')

  const { nodes } = scenarioTopology

  // 网络颜色映射
  const networkColors = {
    'internet': '#ff6b6b',
    'dmz_segment': '#4ecdc4',
    'user_segment': '#45b7d1',
    'server_segment': '#f9ca24',
    'db_segment': '#6c5ce7',
    'medical_segment': '#a29bfe',
    'siem_segment': '#fd79a8',
    'vpn_segment': '#74b9ff'
  }

  // 1. 为非防火墙节点添加IP标签（显示在节点下方）
  console.log('📍 添加节点IP标签...')
  nodes.forEach(node => {
    // 跳过防火墙节点，防火墙的IP只显示在连线上
    if (node.type === 'firewall') {
      console.log(`🔥 跳过防火墙节点 ${node.id}，IP将显示在连线上`)
      return
    }

    const fabricNode = findDeviceByScenarioId(node.id)
    if (fabricNode && node.ip_addresses) {
      const primaryNetwork = node.networks?.[0]
      const primaryIP = node.ip_addresses[primaryNetwork]

      if (primaryIP) {
        // 创建IP标签
        const ipLabel = new fabric.Text(primaryIP, {
          left: fabricNode.left,
          top: fabricNode.top + 55, // 节点下方
          fontSize: 10,
          fill: '#ffffff',
          textAlign: 'center',
          originX: 'center',
          originY: 'top',
          selectable: false,
          evented: false,
          nodeId: node.id,
          labelType: 'ip'
        })

        // 设置IP标签跟随节点移动
        const updateIPLabelPosition = () => {
          ipLabel.set({
            left: fabricNode.left,
            top: fabricNode.top + 55
          })
          ipLabel.setCoords()
        }

        // 为节点添加移动事件监听器
        fabricNode.on('moving', updateIPLabelPosition)

        // 将更新函数保存到标签对象上
        ipLabel.updatePosition = updateIPLabelPosition
        ipLabel.parentNode = fabricNode

        topology.canvas.add(ipLabel)
        console.log(`📍 为节点 ${node.id} 添加IP标签: ${primaryIP}，已设置移动监听器`)
      }
    }
  })

  // 2. 创建简化的防火墙连线（避免重复连接）
  console.log('🔗 创建简化的防火墙连线...')

  // 找到所有防火墙节点
  const firewallNodes = nodes.filter(node => node.type === 'firewall')
  console.log(`🔥 找到 ${firewallNodes.length} 个防火墙节点:`, firewallNodes.map(f => f.id))

  // 记录已连接的设备，避免重复连接
  const connectedDevices = new Set()

  // 按防火墙优先级排序（边界防火墙优先）
  const sortedFirewalls = firewallNodes.sort((a, b) => {
    if (a.id.includes('border') || a.id.includes('外部')) return -1
    if (b.id.includes('border') || b.id.includes('外部')) return 1
    if (a.id.includes('internal') || a.id.includes('内部')) return -1
    if (b.id.includes('internal') || b.id.includes('内部')) return 1
    return 0
  })

  // 为每个防火墙创建连线
  sortedFirewalls.forEach(firewallNode => {
    console.log(`🔥 处理防火墙: ${firewallNode.id}`)

    // 获取防火墙连接的所有网络
    const firewallNetworks = firewallNode.networks || []

    firewallNetworks.forEach(networkId => {
      // 找到同一网络中的其他设备（非防火墙）
      const networkDevices = nodes.filter(node =>
        node.id !== firewallNode.id &&
        node.type !== 'firewall' &&  // 排除其他防火墙
        node.networks &&
        node.networks.includes(networkId) &&
        !connectedDevices.has(node.id)  // 避免重复连接
      )

      // 为防火墙与每个非防火墙设备创建连线
      networkDevices.forEach(device => {
        const networkColor = networkColors[networkId] || '#95a5a6'
        console.log(`🔗 创建防火墙连接: ${firewallNode.id} -> ${device.id} (${networkId})`)
        createNetworkConnection(firewallNode, device, networkId, networkColor)
        connectedDevices.add(device.id)  // 标记为已连接
      })
    })
  })

  // 特殊处理：防火墙之间的连接（只连接相邻层级）
  const borderFirewall = firewallNodes.find(fw => fw.id.includes('border') || fw.id.includes('外部'))
  const internalFirewall = firewallNodes.find(fw => fw.id.includes('internal') || fw.id.includes('内部'))

  if (borderFirewall && internalFirewall) {
    // 检查两个防火墙是否有共同网络
    const commonNetworks = borderFirewall.networks?.filter(net =>
      internalFirewall.networks?.includes(net)
    ) || []

    if (commonNetworks.length > 0) {
      const networkId = commonNetworks[0] // 使用第一个共同网络
      const networkColor = networkColors[networkId] || '#95a5a6'
      console.log(`🔗 创建防火墙间连接: ${borderFirewall.id} -> ${internalFirewall.id} (${networkId})`)
      createNetworkConnection(borderFirewall, internalFirewall, networkId, networkColor)
    }
  }

  console.log('✅ 优化的网络连线渲染完成')
}

// 生成场景 (调用后端并渲染拓扑)
async function generateScenario() {
  if (!topology) return
  try {
    // 显示加载动画
    const loadingEl = document.getElementById('topology-loading')
    if (loadingEl) {
      loadingEl.style.display = 'flex'
    }

    // 🔄 重置节点状态 - 在生成场景时自动重置所有节点状态
    console.log('🔄 生成场景时自动重置节点状态...')
    if (eventMonitorRef.value) {
      // 调用 EventMonitor 的重置方法
      eventMonitorRef.value.resetAllNodeStatus()
      logInfo('系统', '已重置所有节点状态')
    }

    // 检查是否是场景模式
    if (isScenarioMode.value && scenarioData.value) {
      // 场景模式：启动容器，将虚拟节点变为实体
      await deployScenarioContainers()
    } else {
      // 普通模式：创建预设拓扑图（半透明状态）
      await TopologyGenerator.createCompanyTopology(topology, true)

      // 🔧 应用优化后的连线逻辑：清除旧连线并重新创建
      console.log('🔧 应用优化后的连线逻辑...')

      // 清除现有连线
      if (typeof window.clearNetworkConnections === 'function') {
        window.clearNetworkConnections()
        console.log('🧹 已清除预设拓扑的旧连线')
      }

      // 创建简化的场景数据用于连线渲染
      const simplifiedScenario = createSimplifiedScenarioFromTopology()
      if (simplifiedScenario) {
        console.log('🔗 使用优化逻辑重新创建连线...')
        // 直接调用优化的连线逻辑，避免调用renderScenarioTopology
        await renderOptimizedNetworkConnections(simplifiedScenario)
      }
    }

    // 只在普通模式下执行容器启动
    if (!isScenarioMode.value) {
      logInfo('系统', '开始生成场景...')

      try {
        // 向后端请求启动预设的 docker-compose 文件
        const containerInfo = await TopologyService.startTopology('company-topology')

        // 更新设备状态
        TopologyGenerator.updateDevicesWithContainerInfo(topology, containerInfo)

        // 强制更新所有设备的视觉状态
        TopologyGenerator.forceUpdateDevicesVisualState(topology)

        // 🔄 生成场景成功后，再次刷新节点状态以确保与容器状态同步
        if (eventMonitorRef.value) {
          setTimeout(() => {
            eventMonitorRef.value.refreshNodeStatusFromContainers()
            logInfo('系统', '已同步容器状态到节点状态')
          }, 2000) // 等待2秒让容器完全启动
        }

        // 显示成功消息
        logSuccess('系统', '场景生成成功')
      } catch (error) {
        console.error('生成场景失败', error)
        logError('系统', `生成场景失败: ${error.message}`)

        // 如果是超时错误，尝试获取当前容器状态
        if (error.name === 'AbortError') {
          logWarning('系统', '请求超时，尝试获取当前容器状态...')
        }
      }
    } else {
      // 场景模式下显示成功消息
      logSuccess('系统', 'APT场景容器部署完成')
    }

  } catch (error) {
    console.error('生成场景失败', error)
    logError('系统', `生成场景失败: ${error.message}`)

    // 如果是超时错误，尝试获取当前容器状态
    if (error.name === 'AbortError') {
      logWarning('系统', '请求超时，尝试获取当前容器状态...')
    }
  } finally {
    // 隐藏加载动画
    const loadingEl = document.getElementById('topology-loading')
    if (loadingEl) {
      loadingEl.style.display = 'none'
    }
  }
}

// 销毁场景
async function destroyScenario() {
  if (!topology) return

  // 显示加载动画
  const loadingEl = document.getElementById('topology-loading')
  if (loadingEl) {
    loadingEl.style.display = 'flex'
  }

  try {
    logInfo('系统', '开始销毁场景...')

    // 发送请求销毁容器
    await TopologyService.stopTopology()

    logSuccess('系统', '场景销毁成功')
  } catch (e) {
    console.error('销毁场景失败', e)
    logError('系统', `销毁场景失败: ${e.message}`)
  } finally {
    // 无论成功失败，都清空画布
    topology.clear()
    topologyStore.devices = {}
    topologyStore.connections = []

    // 隐藏加载动画
    if (loadingEl) {
      loadingEl.style.display = 'none'
    }
  }
}



// 日志记录函数
function logMessage(level, source, message, fromWebSocket = false) {
  if (!message) {
    message = source
    source = '系统'
  }

  // 添加到系统日志
  const eventMonitor = document.querySelector('.event-monitor')
  if (eventMonitor && eventMonitor.__vue__) {
    eventMonitor.__vue__.addLog({
      level: level,
      source: source,
      message: message,
      timestamp: new Date().toLocaleTimeString(),
      fromWebSocket: fromWebSocket
    })
  } else if (eventMonitorRef.value) {
    // 使用ref引用
    eventMonitorRef.value.addLog({
      level: level,
      source: source,
      message: message,
      timestamp: new Date().toLocaleTimeString(),
      fromWebSocket: fromWebSocket
    })
  } else {
    // 如果无法找到组件，则使用控制台记录
    console.log(`[${level.toUpperCase()}] [${source}] ${message} ${fromWebSocket ? '[WebSocket]' : ''}`)
  }

  // 如果是重要事件，也添加到关键事件
  if (level === 'error' || level === 'warning' || level === 'success') {
    addEvent({
      type: level === 'error' ? 'failure' :
        level === 'warning' ? 'warning' :
          level === 'success' ? 'success' : 'system',
      message: `[${source}] ${message}`
    })
  }
}

// 添加关键事件
function addEvent(event) {
  // 确保事件对象有fromWebSocket属性
  if (event.fromWebSocket === undefined) {
    event.fromWebSocket = false;
  }

  if (eventMonitorRef.value) {
    // 使用ref引用
    eventMonitorRef.value.addEvent(event)
  } else {
    // 尝试使用DOM查询作为备选方案
    const eventMonitor = document.querySelector('.event-monitor')
    if (eventMonitor && eventMonitor.__vue__) {
      eventMonitor.__vue__.addEvent(event)
    } else {
      // 如果无法找到组件，则使用控制台记录
      console.log(`[EVENT] ${event.type}: ${event.message} ${event.fromWebSocket ? '[WebSocket]' : ''}`)
    }
  }
}

// 添加攻击事件
function addAttackEvent(message, fromWebSocket = false) {
  addEvent({
    type: 'attack',
    message: message,
    fromWebSocket: fromWebSocket
  })
}



function logInfo(source, message) {
  logMessage('info', source, message)
}

function logWarning(source, message) {
  logMessage('warning', source, message)
}

function logError(source, message) {
  logMessage('error', source, message)
}

function logSuccess(source, message) {
  logMessage('success', source, message)
}

function logDebug(source, message) {
  logMessage('debug', source, message)
}

// 获取设备图标
function getDeviceIcon(type) {
  const iconMap = {
    'router': '/图标/路由器.svg',
    'firewall': '/图标/防火墙.svg',
    'switch': '/图标/交换机.svg',
    'server': '/图标/服务器.svg',
    'pc': '/图标/pc.svg',
    'db': '/图标/数据库服务器.svg',
    'web': '/图标/Web服务器.svg',
    'app': '/图标/应用服务器.svg',
    'file': '/图标/文件服务器.svg',
    'mail': '/图标/邮件服务器.svg',
    'vpn': '/图标/VPN.svg',
    'dns': '/图标/DNS服务器.svg',
    'proxy': '/图标/代理服务器.svg',
    'load': '/图标/负载均衡.svg'
  }

  return iconMap[type] || ''
}

// 获取设备类型名称
function getDeviceTypeName(type) {
  const typeMap = {
    'router': '路由器',
    'firewall': '防火墙',
    'switch': '交换机',
    'server': '服务器',
    'pc': 'PC',
    'db': '数据库',
    'web': 'Web服务器',
    'app': '应用服务器',
    'file': '文件服务器',
    'mail': '邮件服务器',
    'vpn': 'VPN网关',
    'dns': 'DNS服务器',
    'proxy': '代理服务器',
    'load': '负载均衡'
  }

  return typeMap[type] || type
}

// 处理节点状态重置
const handleNodesStatusReset = () => {
  console.log('🔄 处理节点状态重置事件')

  // 重置拓扑图中所有节点的视觉状态
  if (window.topologyFabricCanvas) {
    const canvas = window.topologyFabricCanvas
    const objects = canvas.getObjects()

    objects.forEach(obj => {
      if (obj.deviceData) {
        // 重置节点的视觉状态
        obj.set({
          stroke: '#ffffff',
          strokeWidth: 1,
          strokeDashArray: null,
          opacity: 1,
          filters: []
        })

        // 重置设备数据状态
        if (obj.deviceData) {
          obj.deviceData.status = 'normal'
          obj.deviceData.compromised = false
          obj.deviceData.attackLevel = 0
        }
      }
    })

    canvas.requestRenderAll()
    console.log('✅ 拓扑图节点状态已重置')
  }
}

// ===================== 虚拟时间轴事件处理 =====================

// 时间轴启动事件
const onTimelineStarted = () => {
  console.log('🕒 虚拟时间轴已启动')

  // 添加时间轴启动事件到攻击事件记录
  if (virtualTimelineRef.value) {
    virtualTimelineRef.value.addEvent({
      phase: '准备',
      type: 'info',
      message: 'APT攻击演练时间轴已启动',
      details: {
        '时间倍速': virtualTimelineRef.value.timeMultiplier + 'x',
        '演练模式': 'APT医疗场景'
      }
    })
  }
}

// 时间轴暂停事件
const onTimelinePaused = () => {
  console.log('⏸️ 虚拟时间轴已暂停')

  if (virtualTimelineRef.value) {
    virtualTimelineRef.value.addEvent({
      phase: '暂停',
      type: 'warning',
      message: '攻击演练已暂停',
      details: {
        '暂停时间': new Date().toLocaleTimeString()
      }
    })
  }
}

// 时间轴重置事件
const onTimelineReset = () => {
  console.log('🔄 虚拟时间轴已重置')

  // 重置攻击可视化效果
  if (attackVisualization) {
    attackVisualization.clearAllEffects()
  }

  // 重置节点状态
  if (eventMonitorRef.value) {
    eventMonitorRef.value.resetAllNodeStatus()
  }
}

// 攻击阶段变更事件
const onPhaseChanged = (newPhase) => {
  console.log('📊 攻击阶段变更:', newPhase)

  // 更新攻击可视化的当前阶段
  if (attackVisualization) {
    attackVisualization.currentPhase = newPhase
  }

  // 添加阶段变更事件
  if (virtualTimelineRef.value) {
    virtualTimelineRef.value.addEvent({
      phase: newPhase,
      type: 'success',
      message: `进入${newPhase}阶段`,
      details: {
        '阶段': newPhase,
        '时间': new Date().toLocaleString()
      }
    })
  }
}

// 时间倍速变更事件
const onSpeedChanged = (newSpeed) => {
  console.log('⚡ 时间倍速已调整:', newSpeed + 'x')

  if (virtualTimelineRef.value) {
    virtualTimelineRef.value.addEvent({
      phase: '设置',
      type: 'info',
      message: `时间倍速调整为 ${newSpeed}x`,
      details: {
        '新倍速': newSpeed + 'x',
        '说明': newSpeed === 1 ? '真实时间' : `1分钟 = ${Math.floor(newSpeed / 60)}小时`
      }
    })
  }
}

// ===================== 虚拟时间轴辅助函数 =====================

// 将攻击阶段转换为显示名称
function getPhaseDisplayName(stage) {
  const phaseMap = {
    'reconnaissance': '侦察',
    'weaponization': '武器化',
    'delivery': '投递',
    'exploitation': '利用',
    'installation': '安装',
    'command_and_control': '命令控制',
    'actions_on_objectives': '行动'
  }
  return phaseMap[stage] || stage
}

// 将日志级别转换为事件类型
function getEventType(level) {
  const typeMap = {
    'info': 'info',
    'warning': 'warning',
    'success': 'success',
    'error': 'error'
  }
  return typeMap[level] || 'info'
}

// 更新受攻陷资产数量
function updateCompromisedAssetsCount() {
  if (!virtualTimelineRef.value) return

  // 统计被攻陷的节点数量
  let compromisedCount = 0
  if (window.topologyFabricCanvas) {
    const canvas = window.topologyFabricCanvas
    const objects = canvas.getObjects()

    objects.forEach(obj => {
      if (obj.deviceData && obj.compromised) {
        compromisedCount++
      }
    })
  }

  virtualTimelineRef.value.updateCompromisedAssets(compromisedCount)
  console.log('📊 更新受攻陷资产数量:', compromisedCount)
}

// 处理节点状态刷新
const handleNodesStatusRefreshed = (networkNodes) => {
  console.log('🔄 处理节点状态刷新事件', networkNodes)

  // 根据刷新后的状态更新拓扑图节点
  if (window.topologyFabricCanvas && networkNodes) {
    const canvas = window.topologyFabricCanvas
    const objects = canvas.getObjects()

    objects.forEach(obj => {
      if (obj.deviceData && obj.deviceData.name) {
        // 查找对应的网络节点状态
        const nodeStatus = Object.values(networkNodes).find(node =>
          node.name === obj.deviceData.name ||
          node.id === obj.deviceData.id
        )

        if (nodeStatus) {
          // 根据状态更新节点视觉效果
          updateNodeVisualStatus(obj, nodeStatus.status)

          // 更新设备数据
          obj.deviceData.status = nodeStatus.status
          obj.deviceData.compromised = nodeStatus.compromised
          obj.deviceData.attackLevel = nodeStatus.attackLevel
        }
      }
    })

    canvas.requestRenderAll()
    console.log('✅ 拓扑图节点状态已刷新')
  }
}

// 更新节点视觉状态
const updateNodeVisualStatus = (node, status) => {
  switch (status) {
    case 'normal':
      node.set({
        stroke: '#ffffff',
        strokeWidth: 1,
        strokeDashArray: null,
        opacity: 1,
        filters: []
      })
      break
    case 'compromised':
      node.set({
        stroke: '#ff0000',
        strokeWidth: 3,
        strokeDashArray: [5, 5],
        opacity: 1
      })
      break
    case 'under_attack':
      node.set({
        stroke: '#ff6600',
        strokeWidth: 2,
        opacity: 1
      })
      break
    case 'failed':
      node.set({
        stroke: '#ff0000',
        strokeWidth: 1,
        opacity: 0.7
      })
      break
  }
}
</script>

<style scoped>
.topology-view {
  height: 100%;
}

.device-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.device-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.device-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.device-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 4px;
}

.device-name {
  font-size: 12px;
  text-align: center;
}

.topology-container {
  width: 100%;
  height: 600px;
  background-color: #1e1e2f;
  border-radius: 8px;
  overflow: hidden;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #ffffff;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 虚拟时间轴区域 */
.virtual-timeline-section {
  margin-top: 20px;
  padding: 0 16px;
  background: transparent;
}

.event-monitor-container {
  position: absolute;
  bottom: 16px;
  right: 16px;
  width: 300px;
  /* 设置为大约五分之一的宽度 */
  z-index: 10;
  display: flex;
  flex-direction: column;
}

/* 拓扑攻击可视化覆盖层 */
.topology-attack-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
  /* 设置为最低层，确保不会覆盖拓扑图 */
  background: transparent;
}
</style>
// 显示胜负结果

function showBattleResult(resultType, message){
  console.log('🏆 显示胜负结果:', resultType, message);
  
  // 创建胜负结果通知
  const resultConfig = {
    attack_victory: {
      title: '🔴 攻击方胜利！',
      type: 'error',
      duration: 10000,
      color: '#dc2626'
    },
    defense_victory: {
      title: '🟢 防御方胜利！',
      type: 'success', 
      duration: 10000,
      color: '#16a34a'
    },
    battle_start: {
      title: '🚀 攻防演练开始',
      type: 'info',
      duration: 5000,
      color: '#2563eb'
    }
  };

  const config = resultConfig[resultType];
  if (config) {
    // 添加到关键事件区域
    addEvent({
      type: resultType === 'attack_victory' ? 'failure' : 
            resultType === 'defense_victory' ? 'success' : 'system',
      message: `${config.title} ${message}`,
      fromWebSocket: true,
      important: true
    });

    // 在拓扑图上显示结果动画
    if (topology && topology.canvas) {
      showBattleResultAnimation(resultType, config);
    }

    // 记录到日志
    const logLevel = resultType === 'attack_victory' ? 'error' : 
                    resultType === 'defense_victory' ? 'success' : 'info';
    logMessage(logLevel, '攻防演练裁判', `${config.title} ${message}`, true);
  }
}

// 显示胜负结果动画
function showBattleResultAnimation(resultType, config) {
  try {
    const canvas = topology.canvas;
    const canvasCenter = {
      x: canvas.width / 2,
      y: canvas.height / 2
    };

    // 创建结果文字
    const resultText = new fabric.Text(config.title, {
      left: canvasCenter.x,
      top: canvasCenter.y - 50,
      fontSize: 48,
      fontWeight: 'bold',
      fill: config.color,
      textAlign: 'center',
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0,
      shadow: new fabric.Shadow({
        color: 'rgba(0,0,0,0.5)',
        blur: 10,
        offsetX: 2,
        offsetY: 2
      })
    });

    canvas.add(resultText);

    // 文字出现动画
    const textAnimation = resultText.animate({
      opacity: 1,
      fontSize: 56,
      top: canvasCenter.y - 60
    }, {
      duration: 1000,
      easing: fabric.util.ease.easeOutBounce,
      onChange: () => canvas.renderAll(),
      onComplete: () => {
        // 延迟后淡出
        setTimeout(() => {
          const fadeOut = resultText.animate({
            opacity: 0,
            fontSize: 48
          }, {
            duration: 2000,
            onChange: () => canvas.renderAll(),
            onComplete: () => {
              canvas.remove(resultText);
              canvas.renderAll();
            }
          });
        }, 5000);
      }
    });

    // 添加背景效果
    if (resultType === 'attack_victory') {
      // 攻击方胜利 - 红色警告效果
      createWarningEffect(canvas, '#dc2626');
    } else if (resultType === 'defense_victory') {
      // 防御方胜利 - 绿色成功效果
      createSuccessEffect(canvas, '#16a34a');
    }

  } catch (error) {
    console.error('显示胜负结果动画失败:', error);
  }
}

// 创建警告效果
function createWarningEffect(canvas, color) {
  const overlay = new fabric.Rect({
    left: 0,
    top: 0,
    width: canvas.width,
    height: canvas.height,
    fill: color,
    opacity: 0,
    selectable: false,
    evented: false
  });

  canvas.add(overlay);

  // 闪烁效果
  let flashCount = 0;
  const flashInterval = setInterval(() => {
    const targetOpacity = flashCount % 2 === 0 ? 0.2 : 0;
    overlay.animate({ opacity: targetOpacity }, {
      duration: 300,
      onChange: () => canvas.renderAll()
    });
    
    flashCount++;
    if (flashCount >= 6) {
      clearInterval(flashInterval);
      canvas.remove(overlay);
      canvas.renderAll();
    }
  }, 400);
}

// 创建成功效果
function createSuccessEffect(canvas, color) {
  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;

  // 创建扩散圆圈
  const circle = new fabric.Circle({
    left: centerX,
    top: centerY,
    radius: 10,
    fill: 'transparent',
    stroke: color,
    strokeWidth: 4,
    originX: 'center',
    originY: 'center',
    selectable: false,
    evented: false,
    opacity: 0.8
  });

  canvas.add(circle);

  // 扩散动画
  circle.animate({
    radius: 200,
    opacity: 0
  }, {
    duration: 2000,
    easing: fabric.util.ease.easeOutQuad,
    onChange: () => canvas.renderAll(),
    onComplete: () => {
      canvas.remove(circle);
      canvas.renderAll();
    }
  });
}

// 显示战报
function showBattleReport(reportMessage) {
  console.log('📊 显示战报:', reportMessage);
  
  try {
    // 尝试解析JSON格式的战报
    const jsonMatch = reportMessage.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const reportData = JSON.parse(jsonMatch[0]);
      
      // 格式化战报显示
      const formattedReport = formatBattleReport(reportData);
      
      // 添加到关键事件区域
      addEvent({
        type: 'system',
        message: `📊 攻防演练战报:\n${formattedReport}`,
        fromWebSocket: true,
        important: true
      });
      
      // 记录到日志
      logMessage('info', '攻防演练裁判', `战报生成完成`, true);
    } else {
      // 直接显示原始战报消息
      addEvent({
        type: 'system',
        message: `📊 ${reportMessage}`,
        fromWebSocket: true
      });
    }
  } catch (error) {
    console.error('解析战报失败:', error);
    // 显示原始消息
    addEvent({
      type: 'system',
      message: `📊 ${reportMessage}`,
      fromWebSocket: true
    });
  }
}

// 格式化战报
function formatBattleReport(reportData) {
  const lines = [];
  
  if (reportData.battle_duration) {
    lines.push(`⏱️ 演练时长: ${reportData.battle_duration}`);
  }
  
  if (reportData.attack_stages_completed !== undefined) {
    lines.push(`🎯 攻击阶段完成: ${reportData.attack_stages_completed}/7`);
  }
  
  if (reportData.defense_actions_taken !== undefined) {
    lines.push(`🛡️ 防御行动执行: ${reportData.defense_actions_taken}/6`);
  }
  
  if (reportData.compromised_assets && reportData.compromised_assets.length > 0) {
    lines.push(`💥 被攻陷资产: ${reportData.compromised_assets.join(', ')}`);
  }
  
  if (reportData.recovered_assets && reportData.recovered_assets.length > 0) {
    lines.push(`🔧 已恢复资产: ${reportData.recovered_assets.join(', ')}`);
  }
  
  if (reportData.blocked_ips && reportData.blocked_ips.length > 0) {
    lines.push(`🚫 阻断IP数量: ${reportData.blocked_ips.length}`);
  }
  
  if (reportData.patched_vulnerabilities && reportData.patched_vulnerabilities.length > 0) {
    lines.push(`🔒 修复漏洞数量: ${reportData.patched_vulnerabilities.length}`);
  }
  
  if (reportData.final_result) {
    const resultText = reportData.final_result === 'attack_victory' ? '攻击方胜利' : 
                      reportData.final_result === 'defense_victory' ? '防御方胜利' : '演练进行中';
    lines.push(`🏆 最终结果: ${resultText}`);
  }
  
  return lines.join('\n');
}