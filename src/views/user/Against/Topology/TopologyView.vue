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
            <button
              @click="deleteSelectedNode"
              class="btn btn-sm btn-error"
              :disabled="!topology?.getActiveObject()"
            >
              🗑️ 删除节点
            </button>
            <button
              @click="startConnectingNodes"
              class="btn btn-sm btn-warning"
              :class="{ 'btn-active': isConnectingNodes }"
            >
              🔗 连接节点
            </button>
            <button
              v-if="isConnectingNodes"
              @click="stopConnectingNodes"
              class="btn btn-sm btn-ghost"
            >
              ❌ 取消连接
            </button>
          </div>

          <!-- 节点添加区域 -->
          <div class="mb-4">
            <h4 class="font-medium mb-2">添加节点:</h4>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="nodeType in availableNodeTypes"
                :key="nodeType.type"
                @click="startAddingNode(nodeType)"
                class="btn btn-sm btn-outline"
                :class="{ 'btn-active': isAddingNode && selectedNodeType?.type === nodeType.type }"
              >
                {{ nodeType.name }}
              </button>
            </div>
            <button
              v-if="isAddingNode"
              @click="stopAddingNode"
              class="btn btn-sm btn-ghost mt-2 w-full"
            >
              ❌ 取消添加
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
              <button
                @click="generateScenario"
                class="btn btn-sm btn-success"
                :disabled="virtualNodes.size === 0"
              >
                🚀 部署容器
              </button>
              <button
                @click="disableEditMode"
                class="btn btn-sm btn-ghost"
              >
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



          <!-- 攻击可视化现在直接在Canvas中实现，无需额外组件 -->

          <!-- 事件监控器 -->
          <div class="event-monitor-container">
            <EventMonitor
              ref="eventMonitorRef"
              :attackTaskStatus="currentAttackTaskStatus"
              @nodes-status-reset="handleNodesStatusReset"
              @nodes-status-refreshed="handleNodesStatusRefreshed"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 攻击者对话框 -->
    <AttackerDialog :show="showAttackerDialog" :attacker="selectedAttacker" :targets="attackTargets"
      @close="showAttackerDialog = false" @attack="handleAttack" />

    <!-- 防火墙对话框 -->
    <FirewallDialog :show="showFirewallDialog" :firewall="selectedFirewall" @close="showFirewallDialog = false"
      @save="handleFirewallSave" />

    <!-- 主机信息对话框 -->
    <HostInfoDialog :show="showHostInfoDialog" :host="selectedHost" @close="showHostInfoDialog = false" />

    <!-- 钓鱼攻击可视化 - 暂时禁用，使用新的 TopologyAttackVisualizer -->
    <!-- <SimplePhishingVisualization :show="showPhishingAttackVisualization" :attacker="selectedAttacker"
      :target="selectedPhishingTarget" :attackType="currentAttackType"
      @close="showPhishingAttackVisualization = false" /> -->



    <!-- 不再使用全屏的攻击进度监控，而是在EventMonitor中显示 -->
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useTopologyStore } from '../../../../stores/topology'
import NetworkTopology from './core/NetworkTopology'
import TopologyGenerator from './core/TopologyGenerator'
import FabricAttackVisualization from './core/FabricAttackVisualization'
import {
  handleReconnaissanceAnimation,
  handleWeaponizationAnimation,
  handleDeliveryAnimation,
  handleExploitationAnimation,
  handleInstallationAnimation,
  handleCommandControlAnimation,
  handleActionsAnimation,
  handleLogBasedAnimation
} from './core/AttackStageAnimations'
import TopologyService from './services/TopologyService'
import AttackService from './services/AttackService'
import ScenarioDataService from './services/ScenarioDataService'

import AttackAgentService from './services/AttackAgentService'
import AttackTaskService from './services/AttackTaskService'
import WebSocketService from './services/WebSocketService'
import AttackerDialog from './components/AttackerDialog.vue'
import FirewallDialog from './components/FirewallDialog.vue'
import HostInfoDialog from './components/HostInfoDialog.vue'
import EventMonitor from './components/EventMonitor.vue'

const topologyStore = useTopologyStore()
let topology = null
let attackVisualization = null
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
const selectedAttacker = ref(null)
const selectedFirewall = ref(null)
const selectedHost = ref(null)
const attackTargets = ref([])
const eventMonitorRef = ref(null)

// 攻击任务状态
const currentAttackTaskId = ref('')
const currentAttackTaskStatus = ref(null)

// 场景模式状态
const isScenarioMode = ref(false)
const scenarioData = ref(null)
const virtualNodes = ref(new Set())
const runningNodes = ref(new Set())

// 节点编辑状态
const isEditMode = ref(false)
const isAddingNode = ref(false)
const isConnectingNodes = ref(false)
const selectedNodeForConnection = ref(null)
const selectedNodeType = ref(null)
const availableNodeTypes = ref([
  { type: 'workstation', name: '工作站', icon: '/icons/workstation.svg' },
  { type: 'server', name: '服务器', icon: '/icons/server.svg' },
  { type: 'database', name: '数据库', icon: '/icons/database.svg' },
  { type: 'firewall', name: '防火墙', icon: '/icons/firewall.svg' },
  { type: 'router', name: '路由器', icon: '/icons/router.svg' },
  { type: 'switch', name: '交换机', icon: '/icons/switch.svg' }
])



// 计算属性
const selectedDevice = computed(() => {
  const obj = topologyStore.selectedObject
  return obj && obj.type === 'device' ? obj : null
})

const selectedConnection = computed(() => {
  const obj = topologyStore.selectedObject
  return obj && obj.type === 'connection' ? obj : null
})

// 初始化拓扑图
onMounted(async () => {
  await loadFabric()

  // 检查是否是场景模式
  const urlParams = new URLSearchParams(window.location.search)
  const mode = urlParams.get('mode')

  if (mode === 'scenario') {
    // 尝试从sessionStorage获取场景数据
    const scenarioDataStr = sessionStorage.getItem('scenarioData')
    if (scenarioDataStr) {
      try {
        const storedData = JSON.parse(scenarioDataStr)
        console.log('📋 检测到场景模式，加载场景数据:', storedData)

        // 初始化拓扑图
        initializeTopology()

        // 等待拓扑图初始化完成后加载场景
        setTimeout(async () => {
          const success = await loadAptMedicalScenario()
          if (success) {
            enableEditMode()
            logInfo('系统', `场景模式已激活: ${storedData.prompt}`)
          }
        }, 1000)

        // 清理sessionStorage
        sessionStorage.removeItem('scenarioData')
      } catch (error) {
        console.error('解析场景数据失败:', error)
        initializeTopology()
      }
    } else {
      console.warn('场景模式但未找到场景数据，使用普通模式')
      initializeTopology()
    }
  } else {
    // 普通模式
    initializeTopology()
  }

  // 添加攻击进度和完成事件监听
  window.addEventListener('attack-progress', handleAttackProgress)
  window.addEventListener('attack-completed', handleAttackCompleted)

  // 添加拓扑动画事件监听
  document.addEventListener('topology-animation', handleTopologyAnimationEvent)

  // 初始化WebSocket连接
  await initWebSocketConnection()
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

// 初始化拓扑图
function initializeTopology() {
  if (!fabricLoaded) {
    console.error('Fabric.js未加载，无法初始化拓扑图')
    return
  }

  console.log('🚀 开始创建 NetworkTopology 实例...')

  try {
    topology = new NetworkTopology({
      canvasId: 'network-topology'
    })

    console.log('✅ NetworkTopology 实例创建成功:', topology)

    // 将 topology 对象暴露到全局，供调试使用
    window.topology = topology

    topology.initialize().then(() => {
      console.log('✅ 拓扑图初始化完成')
      console.log('📊 Topology canvas:', topology.canvas)

      // 验证 Fabric.js 实例是否正确创建
      const canvas = document.querySelector('#network-topology')
      if (canvas && topology.canvas) {
        console.log('🔗 将 Fabric 实例附加到 DOM 元素...')
        // 手动设置 Fabric 实例到 DOM 元素
        canvas.__fabric = topology.canvas
        canvas.fabric = topology.canvas
        console.log('✅ Fabric 实例已附加到 DOM')
      }

    // 使用新的基于Fabric.js的攻击可视化系统
    try {
      attackVisualization = new FabricAttackVisualization(topology)
      console.log('✅ Fabric攻击可视化初始化成功')
    } catch (error) {
      console.error('❌ Fabric攻击可视化初始化失败:', error)
      attackVisualization = null
    }

    // 监听事件
    topology.on('objectSelected', (data) => {
      topologyStore.setSelectedObject(data.object)

      // 处理设备点击事件
      if (data.object.type === 'device') {
        handleDeviceClick(data.object)
      }
    })

    // 初始化canvas
    topologyStore.setCanvas(topology.canvas)

    // 运行 Fabric.js 诊断
    console.log('🔍 运行 Fabric.js 诊断...')
    setTimeout(() => {
      if (window.FabricDiagnostic) {
        window.FabricDiagnostic.diagnose()
        window.FabricDiagnostic.testFabricInstance()
      }
    }, 1000)

    // 触发拓扑图初始化完成事件，通知攻击可视化组件
    const initEvent = new CustomEvent('topology-initialized', {
      detail: {
        topology: topology,
        canvas: topology.canvas,
        timestamp: new Date()
      }
    })
    document.dispatchEvent(initEvent)
    console.log('🎉 拓扑图初始化完成事件已触发')

    }).catch(err => {
      console.error('❌ 拓扑图初始化失败:', err)
    })

  } catch (error) {
    console.error('❌ NetworkTopology 实例创建失败:', error)
  }
}

// 处理设备点击事件
function handleDeviceClick(device) {
  // 如果是攻击者，显示攻击对话框
  if (device.deviceData.name === '攻击者') {
    selectedAttacker.value = device
    // 获取所有可能的攻击目标（除了攻击者自己）
    attackTargets.value = Object.values(topology.devices).filter(d =>
      d !== device && d.deviceData.name !== '攻击节点'
    )
    showAttackerDialog.value = true
  }

  // 如果是防火墙，显示防火墙对话框
  if (device.deviceType === 'firewall') {
    selectedFirewall.value = device
    showFirewallDialog.value = true
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
          d !== selectedAttacker.value && d.deviceData.name !== '攻击节点'
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

// 根据攻击步骤触发动画
function triggerAttackStepAnimation(attackInfo, log) {
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

  // 根据攻击阶段和技术选择动画
  switch (stage) {
    case 'reconnaissance':
      handleReconnaissanceAnimation(technique, sourceNode, targetNode, status, progress, attackVisualization)
      break
    case 'weaponization':
      handleWeaponizationAnimation(technique, sourceNode, targetNode, status, progress, attackVisualization)
      break
    case 'delivery':
      handleDeliveryAnimation(technique, sourceNode, targetNode, status, progress, attackVisualization)
      break
    case 'exploitation':
      handleExploitationAnimation(technique, sourceNode, targetNode, status, progress, attackVisualization)
      break
    case 'installation':
      handleInstallationAnimation(technique, sourceNode, targetNode, status, progress, attackVisualization)
      break
    case 'command_and_control':
      handleCommandControlAnimation(technique, sourceNode, targetNode, status, progress, attackVisualization)
      break
    case 'actions_on_objectives':
      handleActionsAnimation(technique, sourceNode, targetNode, status, progress, attackVisualization)
      break
    default:
      // 默认动画：根据日志内容触发
      if (log) {
        handleLogBasedAnimation(log, sourceNode || targetNode, targetNode, attackVisualization)
      }
  }
}

// 查找拓扑节点
function findTopologyNode(nodeId) {
  if (!topology || !nodeId) return null

  console.log('🔍 查找节点:', nodeId)

  // 节点ID映射 - 根据后端实际使用的ID和前端实际设备名称
  const nodeMapping = {
    // 后端使用的ID -> 前端设备名称的可能匹配
    'internet': ['攻击者', '攻击节点'],
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
    d !== attacker && d.deviceData.name !== '攻击节点'
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
    // 检查是否为自动攻击模式
    if (attackData.attackType === 'auto') {
      // 记录自动攻击开始
      logInfo('攻击智能体', `${attackData.attacker.deviceData.name} 开始自动分析网络拓扑并规划攻击路径`)

      // 添加到关键事件
      addAttackEvent(`攻击智能体启动：开始自动分析网络拓扑并规划攻击路径`)

      // 记录详细日志
      logDebug('攻击智能体', '向中央智能体发送攻击指令...')

      // 在拓扑图上显示思考动画 - 使用新的 Fabric.js 动画系统
      if (attackVisualization && attackVisualization.createThinkingAnimation) {
        attackVisualization.createThinkingAnimation(attackData.attacker, 3)
      }

      try {
        // 调用攻击智能体服务，执行自动攻击
        const result = await AttackAgentService.executeAutoAttack(attackData)

        if (result.success) {
          // 更新当前任务ID和状态
          currentAttackTaskId.value = result.taskId
          currentAttackTaskStatus.value = result.details

          // 不再显示全屏攻击进度监控，而是使用EventMonitor中的攻击链阶段

          // 记录成功消息
          logSuccess('中央智能体', '成功向攻击智能体下达攻击指令')
          logInfo('攻击智能体', '开始执行自动攻击流程')

          // 添加到关键事件
          addAttackEvent(`中央智能体成功向攻击智能体下达攻击指令`)

          // 在拓扑图上可视化攻击路径
          visualizeAttackPath(attackData.attacker)
        } else {
          logError('中央智能体', `向攻击智能体下达指令失败: ${result.message}`)
          addEvent({
            type: 'failure',
            message: `攻击指令下达失败: ${result.message}`
          })
        }
      } catch (error) {
        logError('中央智能体', `与攻击智能体通信失败: ${error.message}`)
        addEvent({
          type: 'failure',
          message: `与攻击智能体通信失败: ${error.message}`
        })

        // 不再使用前端模拟攻击流程
        logWarning('系统', '后端通信失败，请检查网络连接或后端服务状态')
      }
    } else if (attackData.attackType === 'phishing' || attackData.attackType === 'social_engineering') {
      // 钓鱼攻击或社会工程学攻击
      try {
        // 调用攻击智能体服务，执行社会工程学攻击
        const result = await AttackAgentService.executeSocialEngineeringAttack(attackData)

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

          // 在拓扑图上可视化攻击路径
          visualizeAttackPath(attackData.attacker, attackData.target)
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

      // 在拓扑图上可视化攻击路径
      visualizeAttackPath(attackData.attacker, attackData.target)

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

// 在拓扑图上可视化攻击路径 - 使用新的 Fabric.js 动画系统
function visualizeAttackPath(attacker, target = null) {
  if (!topology || !attackVisualization) {
    console.log('⚠️ 拓扑图或攻击可视化未初始化')
    return
  }

  console.log('🎯 开始 Fabric.js 攻击路径可视化')

  // 如果没有指定目标，寻找合适的目标
  if (!target) {
    const devices = Object.values(topology.devices)
    target = devices.find(d =>
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
    // 找到所有可能的目标
    const allTargets = Object.values(topology.devices).filter(d =>
      d !== attacker && d.deviceData.name !== '攻击节点'
    )

    attackVisualization.createAttackSequence(attacker, allTargets.slice(0, 3), 'auto')

    // 开始连续扫描
    if (allTargets.length > 0) {
      attackVisualization.startContinuousScanning(allTargets, 'main-scan')
    }

    // 开始网络流量模拟
    const allNodes = Object.values(topology.devices)
    if (allNodes.length > 1) {
      attackVisualization.startNetworkTraffic(allNodes, 'background-traffic')
    }
  } else if (attackVisualization.createAttackPath) {
    // 回退到单个攻击路径
    attackVisualization.createAttackPath(attacker, target)
  }

  if (!topology || !attackVisualization) return

  // 如果没有指定目标，则寻找可能的目标
  if (!target) {
    // 查找Web服务器作为第一个目标
    target = Object.values(topology.devices).find(d =>
      d.deviceData.name.includes('Web') || d.deviceType === 'web'
    )

    // 如果没有Web服务器，选择任意一个非攻击者的设备
    if (!target) {
      target = Object.values(topology.devices).find(d =>
        d !== attacker && d.deviceData.name !== '攻击节点'
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

// 前端模拟攻击流程已移除，现在使用 Fabric.js 动画系统

// 钓鱼攻击功能已移除，现在使用 Fabric.js 动画系统

// 攻击模拟功能已移除，现在使用 Fabric.js 动画系统

// 处理防火墙保存事件
function handleFirewallSave(firewallData) {
  logInfo('防火墙', `${selectedFirewall.value.deviceData.name} 配置已更新`)
  console.log('防火墙配置已更新:', firewallData)
}

// 设置模式
function setMode(mode) {
  if (!topology) return

  topology.setMode(mode)
  topologyStore.setMode(mode)
}

// 创建设备
function createDevice(type) {
  if (!topology) return

  topology.createDevice(type)
}

// 删除选中对象
function deleteSelected() {
  if (!topology) return

  topology.deleteSelected()
  topologyStore.setSelectedObject(null)
}

// 更新设备属性
function updateDeviceProperty() {
  if (!topology || !selectedDevice.value) return

  // 更新设备标签
  topology._updateLabel(selectedDevice.value, selectedDevice.value.deviceData.name)

  // 更新画布
  topology.canvas.requestRenderAll()
}

// 更新连接类型
function updateConnectionType() {
  if (!topology || !selectedConnection.value) return

  const connType = topology.connectionTypes[selectedConnection.value.connectionType] || topology.connectionTypes.ethernet

  selectedConnection.value.set({
    stroke: connType.color,
    strokeDashArray: connType.dash
  })

  topology.canvas.requestRenderAll()
}

// 缩放控制
function zoomIn() {
  if (!topology) return
  topology.zoomIn()
}

function zoomOut() {
  if (!topology) return
  topology.zoomOut()
}

function resetView() {
  if (!topology) return
  topology.resetView()
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

  // TODO: 实现保存功能
  console.log('保存拓扑图')
  logInfo('系统', '拓扑图已保存')
}

// 加载APT医疗场景数据
async function loadAptMedicalScenario() {
  try {
    console.log('🔄 加载APT医疗场景数据...')
    logInfo('系统', '正在加载APT医疗场景...')

    // 从场景数据服务获取数据
    const aptScenario = await ScenarioDataService.getAptMedicalScenario()

    if (aptScenario && aptScenario.nodes) {
      scenarioData.value = aptScenario
      isScenarioMode.value = true

      // 记录虚拟节点
      virtualNodes.value.clear()
      aptScenario.nodes.forEach(node => {
        if (node.status === 'virtual') {
          virtualNodes.value.add(node.id)
        }
      })

      // 渲染半透明拓扑图
      renderScenarioTopology(aptScenario)

      logInfo('系统', `APT医疗场景加载成功，包含 ${aptScenario.nodes.length} 个节点`)
      return true
    } else {
      throw new Error('场景数据格式错误')
    }
  } catch (error) {
    console.error('加载APT医疗场景失败:', error)
    logError('系统', `加载场景失败: ${error.message}`)
    return false
  }
}

// 渲染场景拓扑图（半透明模式）
function renderScenarioTopology(scenarioTopology) {
  if (!topology) return

  try {
    // 清空当前拓扑图
    topology.clear()

    console.log('🎨 渲染半透明场景拓扑图...')

    // 添加节点
    scenarioTopology.nodes.forEach(nodeData => {
      const fabricNode = topology.createNode(
        nodeData.type,
        nodeData.x,
        nodeData.y,
        {
          id: nodeData.id,
          name: nodeData.displayName || nodeData.name,
          // 半透明样式
          fill: nodeData.fill,
          stroke: nodeData.stroke,
          strokeWidth: nodeData.strokeWidth || 2,
          opacity: nodeData.opacity || 0.5,
          strokeDashArray: nodeData.strokeDashArray || [5, 5],
          // 场景数据
          networks: nodeData.networks,
          ipAddresses: nodeData.ipAddresses,
          status: nodeData.status || 'virtual'
        }
      )

      // 添加到画布
      topology.canvas.add(fabricNode)
    })

    // 添加连接
    scenarioTopology.connections.forEach(connData => {
      const sourceNode = topology.findNodeById(connData.source)
      const targetNode = topology.findNodeById(connData.target)

      if (sourceNode && targetNode) {
        const connection = topology.createConnection(
          sourceNode,
          targetNode,
          {
            stroke: connData.stroke,
            strokeWidth: connData.strokeWidth || 2,
            strokeDashArray: connData.strokeDashArray || [],
            opacity: connData.opacity || 0.7,
            network: connData.network
          }
        )

        topology.canvas.add(connection)
      }
    })

    // 重新渲染画布
    topology.canvas.requestRenderAll()

    logInfo('系统', '半透明拓扑图渲染完成')

  } catch (error) {
    console.error('渲染场景拓扑图失败:', error)
    logError('系统', `渲染失败: ${error.message}`)
  }
}

// 切换节点场景状态（虚拟 -> 实体）
function updateNodeScenarioStatus(nodeId, newStatus) {
  if (!topology) return

  const node = topology.findNodeById(nodeId)
  if (!node) return

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
      break
    case 'starting':
      node.set({
        opacity: 0.8,
        strokeDashArray: [3, 3],
        stroke: '#f39c12',
        strokeWidth: 3
      })
      break
    case 'stopped':
      node.set({
        opacity: 0.6,
        strokeDashArray: [5, 5],
        stroke: '#e74c3c',
        strokeWidth: 2
      })
      runningNodes.value.delete(nodeId)
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
      break
  }

  // 更新节点状态数据
  if (node.nodeData) {
    node.nodeData.status = newStatus
  }

  topology.canvas.requestRenderAll()
}

// 启用编辑模式
function enableEditMode() {
  isEditMode.value = true
  logInfo('系统', '已启用拓扑编辑模式')
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
  if (!topology || !topology.getActiveObject()) {
    logWarning('系统', '请先选择要删除的节点')
    return
  }

  const selectedObject = topology.getActiveObject()

  if (selectedObject.type === 'device' || selectedObject.nodeData) {
    const nodeId = selectedObject.nodeData?.id || selectedObject.id

    // 确认删除
    if (confirm(`确定要删除节点 "${selectedObject.nodeData?.name || nodeId}" 吗？`)) {
      // 删除相关连接
      deleteNodeConnections(nodeId)

      // 删除节点
      topology.canvas.remove(selectedObject)

      // 从虚拟节点集合中移除
      virtualNodes.value.delete(nodeId)
      runningNodes.value.delete(nodeId)

      topology.canvas.requestRenderAll()
      logInfo('系统', `已删除节点: ${selectedObject.nodeData?.name || nodeId}`)
    }
  } else {
    logWarning('系统', '选中的对象不是节点')
  }
}

// 删除节点的所有连接
function deleteNodeConnections(nodeId) {
  if (!topology) return

  const objectsToRemove = []

  topology.canvas.forEachObject((obj) => {
    if (obj.type === 'line' && obj.connectionData) {
      const connData = obj.connectionData
      if (connData.source === nodeId || connData.target === nodeId) {
        objectsToRemove.push(obj)
      }
    }
  })

  objectsToRemove.forEach(obj => {
    topology.canvas.remove(obj)
  })

  if (objectsToRemove.length > 0) {
    logInfo('系统', `已删除 ${objectsToRemove.length} 条相关连接`)
  }
}

// 开始添加节点模式
function startAddingNode(nodeType) {
  isAddingNode.value = true
  selectedNodeType.value = nodeType

  // 设置画布点击监听
  topology.canvas.on('mouse:down', handleCanvasClickForAddNode)

  logInfo('系统', `开始添加 ${nodeType.name} 节点，请在画布上点击位置`)
}

// 处理画布点击添加节点
function handleCanvasClickForAddNode(event) {
  if (!isAddingNode.value || !selectedNodeType.value) return

  const pointer = topology.canvas.getPointer(event.e)

  // 创建新节点
  const newNodeId = `node_${Date.now()}`
  const newNode = topology.createNode(
    selectedNodeType.value.type,
    pointer.x,
    pointer.y,
    {
      id: newNodeId,
      name: `${selectedNodeType.value.name}_${Date.now()}`,
      status: 'virtual',
      fill: ScenarioDataService.getNodeColor(selectedNodeType.value.type),
      stroke: '#bdc3c7',
      strokeWidth: 2,
      opacity: 0.5,
      strokeDashArray: [5, 5]
    }
  )

  // 添加到画布
  topology.canvas.add(newNode)

  // 添加到虚拟节点集合
  virtualNodes.value.add(newNodeId)

  // 结束添加模式
  stopAddingNode()

  topology.canvas.requestRenderAll()
  logInfo('系统', `已添加新节点: ${newNode.nodeData.name}`)
}

// 停止添加节点模式
function stopAddingNode() {
  isAddingNode.value = false
  selectedNodeType.value = null

  // 移除画布点击监听
  topology.canvas.off('mouse:down', handleCanvasClickForAddNode)
}

// 开始连接节点模式
function startConnectingNodes() {
  isConnectingNodes.value = true
  selectedNodeForConnection.value = null

  // 设置节点点击监听
  topology.canvas.on('mouse:down', handleNodeClickForConnection)

  logInfo('系统', '开始连接节点模式，请依次点击两个节点')
}

// 处理节点点击连接
function handleNodeClickForConnection(event) {
  if (!isConnectingNodes.value) return

  const target = event.target
  if (!target || (!target.nodeData && target.type !== 'device')) return

  const nodeId = target.nodeData?.id || target.id

  if (!selectedNodeForConnection.value) {
    // 选择第一个节点
    selectedNodeForConnection.value = target
    target.set({ stroke: '#f39c12', strokeWidth: 4 })
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
  const sourceId = sourceNode.nodeData?.id || sourceNode.id
  const targetId = targetNode.nodeData?.id || targetNode.id

  // 检查是否已存在连接
  let connectionExists = false
  topology.canvas.forEachObject((obj) => {
    if (obj.type === 'line' && obj.connectionData) {
      const connData = obj.connectionData
      if ((connData.source === sourceId && connData.target === targetId) ||
          (connData.source === targetId && connData.target === sourceId)) {
        connectionExists = true
      }
    }
  })

  if (connectionExists) {
    logWarning('系统', '节点间已存在连接')
    return
  }

  // 创建连接线
  const connection = topology.createConnection(
    sourceNode,
    targetNode,
    {
      stroke: '#95a5a6',
      strokeWidth: 2,
      opacity: 0.7,
      connectionData: {
        id: `${sourceId}-${targetId}`,
        source: sourceId,
        target: targetId,
        type: 'ethernet'
      }
    }
  )

  topology.canvas.add(connection)
  topology.canvas.requestRenderAll()

  logInfo('系统', `已创建连接: ${sourceNode.nodeData?.name || sourceId} -> ${targetNode.nodeData?.name || targetId}`)
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

  // 移除节点点击监听
  topology.canvas.off('mouse:down', handleNodeClickForConnection)

  topology.canvas.requestRenderAll()
}

// 部署场景容器
async function deployScenarioContainers() {
  try {
    logInfo('系统', '开始部署场景容器...')

    // 调用后端启动apt-ready场景
    const containerInfo = await TopologyService.startTopology('apt-ready')

    if (containerInfo && containerInfo.running_services) {
      // 更新节点状态为运行中
      containerInfo.running_services.forEach(service => {
        updateNodeScenarioStatus(service.name, 'running')
        logInfo('系统', `容器 ${service.name} 已启动`)
      })

      // 更新失败的服务
      if (containerInfo.failed_services) {
        containerInfo.failed_services.forEach(service => {
          updateNodeScenarioStatus(service.name, 'stopped')
          logWarning('系统', `容器 ${service.name} 启动失败`)
        })
      }

      logSuccess('系统', `场景容器部署完成，${containerInfo.running_services.length} 个容器运行中`)
    } else {
      throw new Error('容器启动失败，未返回有效信息')
    }

  } catch (error) {
    console.error('部署场景容器失败:', error)
    logError('系统', `容器部署失败: ${error.message}`)
    throw error
  }
}

// 创建预设拓扑图（普通模式）
async function createPresetTopology() {
  await TopologyGenerator.createCompanyTopology(topology, true)
  logInfo('系统', '预设拓扑图创建完成')
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

// 添加防御事件
function addDefenseEvent(message) {
  addEvent({
    type: 'defense',
    message: message
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