<template>
  <div class="topology-view">
    <div class="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-6">
      <!-- 左侧控制面板 -->
      <div class="bg-base-100 rounded-lg p-4 border border-base-300/30 mb-6">
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

      <!-- 右侧拓扑图区域 -->
      <div class="bg-base-100 rounded-lg p-4 border border-base-300/30">
        <h2 class="text-xl font-semibold mb-4 flex items-center justify-between">
          <div>
            <span class="text-primary mr-2">#</span>网络拓扑图
          </div>
          <div class="flex gap-2">
            <button @click="saveTopology" class="btn btn-sm btn-primary">保存拓扑图</button>
            <button @click="generateScenario" class="btn btn-sm btn-success">生成场景</button>
            <button @click="destroyScenario" class="btn btn-sm btn-error">销毁场景</button>
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
            <EventMonitor ref="eventMonitor" />
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

    <!-- 钓鱼攻击可视化 -->
    <SimplePhishingVisualization :show="showPhishingAttackVisualization" :attacker="selectedAttacker"
      :target="selectedPhishingTarget" :attackType="currentAttackType"
      @close="showPhishingAttackVisualization = false" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useTopologyStore } from '../../../../stores/topology'
import NetworkTopology from './core/NetworkTopology'
import TopologyGenerator from './core/TopologyGenerator'
import EnhancedAttackVisualization from './core/EnhancedAttackVisualization'
import TopologyService from './services/TopologyService'
import AttackService from './services/AttackService'
import PhishingService from './services/PhishingService'
import AttackerDialog from './components/AttackerDialog.vue'
import FirewallDialog from './components/FirewallDialog.vue'
import HostInfoDialog from './components/HostInfoDialog.vue'
import SimplePhishingVisualization from './components/SimplePhishingVisualization.vue'
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
const showPhishingAttackVisualization = ref(false)
const selectedAttacker = ref(null)
const selectedFirewall = ref(null)
const selectedHost = ref(null)
const selectedPhishingTarget = ref(null)
const currentAttackType = ref('phishing')
const attackTargets = ref([])

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
  initializeTopology()
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

  topology = new NetworkTopology({
    canvasId: 'network-topology'
  })

  topology.initialize().then(() => {
    console.log('拓扑图初始化完成')

    // 初始化攻击可视化
    attackVisualization = new EnhancedAttackVisualization(topology)

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
  }).catch(err => {
    console.error('拓扑图初始化失败:', err)
  })
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
      logDebug('攻击智能体', '正在扫描网络拓扑结构...')
      await simulateDelay(1000)
      
      logDebug('攻击智能体', '识别到潜在目标：内部网络服务器、数据库服务器')
      await simulateDelay(800)
      
      logDebug('攻击智能体', '分析防火墙规则和网络隔离策略...')
      await simulateDelay(1200)
      
      logDebug('攻击智能体', '确定最佳攻击路径：外部防火墙 → Web服务器 → 内部防火墙 → 数据库服务器')
      await simulateDelay(500)
      
      // 选择第一个目标（例如Web服务器）
      const firstTarget = Object.values(topology.devices).find(d => 
        d.deviceData.name.includes('Web') || d.deviceType === 'web'
      )
      
      if (!firstTarget) {
        logWarning('攻击智能体', '未找到合适的初始目标，尝试选择其他目标')
        // 选择任意一个非攻击者的设备作为目标
        const anyTarget = Object.values(topology.devices).find(d => 
          d !== attackData.attacker && d.deviceData.name !== '攻击节点'
        )
        
        if (!anyTarget) {
          throw new Error('无法找到任何攻击目标')
        }
        
        // 执行钓鱼攻击
        await executePhishingAttack(attackData.attacker, anyTarget)
      } else {
        // 执行第一阶段攻击：钓鱼攻击Web服务器管理员
        await executePhishingAttack(attackData.attacker, firstTarget)
        
        // 等待一段时间后执行第二阶段攻击
        await simulateDelay(3000)
        
        // 寻找数据库服务器作为第二阶段目标
        const secondTarget = Object.values(topology.devices).find(d => 
          d.deviceData.name.includes('数据库') || d.deviceType === 'db'
        )
        
        if (secondTarget) {
          // 执行第二阶段攻击：利用Web服务器漏洞攻击数据库
          logInfo('攻击智能体', `开始第二阶段攻击：从已攻陷的Web服务器横向移动到数据库服务器`)
          
          // 添加到关键事件
          addAttackEvent(`开始横向移动：从Web服务器向数据库服务器发起攻击`)
          
          // 使用标准可视化
          await attackVisualization.visualizeAttack({
            attacker: firstTarget,
            target: secondTarget,
            attackType: 'exploit',
            attackName: '横向移动攻击'
          })
          
          // 模拟攻击结果
          await simulateDelay(2000)
          
          // 记录攻击结果
          const success = Math.random() > 0.3 // 70%的成功率
          
          if (success) {
            logSuccess('攻击智能体', `成功攻陷数据库服务器`)
            addAttackEvent(`横向移动成功：数据库服务器已被攻陷`)
          } else {
            logError('攻击智能体', `攻击数据库服务器失败：内部防火墙阻止了连接`)
            addAttackEvent(`横向移动失败：内部防火墙阻止了从Web服务器到数据库服务器的连接`)
          }
        }
      }
    } else if (attackData.attackType === 'phishing' || attackData.attackType === 'social_engineering') {
      // 钓鱼攻击或社会工程学攻击
      await executePhishingAttack(attackData.attacker, attackData.target, attackData.attackType)
    } else {
      // 其他类型的攻击
      // 记录日志
      logInfo('攻击', `${attackData.attacker.deviceData.name} 开始对 ${attackData.target.deviceData.name} 发起 ${attackData.attackName} 攻击`)

      // 添加到关键事件
      addAttackEvent(`${attackData.attacker.deviceData.name} 开始对 ${attackData.target.deviceData.name} 发起 ${attackData.attackName} 攻击`)

      // 使用标准可视化
      await attackVisualization.visualizeAttack(attackData)

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
  } finally {
    // 清除攻击可视化
    setTimeout(() => {
      attackVisualization.clearAttackPaths()
    }, 3000)
  }
}

// 执行钓鱼攻击
async function executePhishingAttack(attacker, target, attackType = 'phishing') {
  // 记录日志
  logInfo('攻击', `${attacker.deviceData.name} 开始对 ${target.deviceData.name} 发起钓鱼攻击`)
  
  // 添加详细日志
  logDebug('钓鱼攻击', `正在收集目标 ${target.deviceData.name} 的信息...`)
  await simulateDelay(800)
  
  logDebug('钓鱼攻击', `生成针对目标的定制化钓鱼邮件...`)
  await simulateDelay(1000)
  
  // 添加到关键事件
  addAttackEvent(`${attacker.deviceData.name} 向 ${target.deviceData.name} 发送钓鱼邮件`)

  // 显示钓鱼攻击可视化
  selectedPhishingTarget.value = target
  currentAttackType.value = attackType
  showPhishingAttackVisualization.value = true

  // 使用钓鱼服务执行攻击
  const result = await PhishingService.simulatePhishingAttack({
    attacker,
    target,
    attackType
  })

  // 记录攻击结果
  if (result.success) {
    logSuccess('钓鱼攻击', `成功对 ${target.deviceData.name} 发起钓鱼攻击`)
    addAttackEvent(`钓鱼攻击成功：${target.deviceData.name} 的凭据已被窃取`)
    
    // 添加详细日志
    logDebug('钓鱼攻击', `获取到目标凭据：${target.deviceData.name}的管理员账号`)
    await simulateDelay(500)
    
    logDebug('钓鱼攻击', `尝试使用获取的凭据登录目标系统...`)
    await simulateDelay(800)
    
    logDebug('钓鱼攻击', `成功登录目标系统，获取控制权限`)
  } else {
    logError('钓鱼攻击', `对 ${target.deviceData.name} 的钓鱼攻击失败`)
    addAttackEvent(`钓鱼攻击失败：${target.deviceData.name} 识别出了钓鱼邮件`)
    
    // 添加详细日志
    logDebug('钓鱼攻击', `目标未点击钓鱼链接，攻击失败`)
  }
  
  return result
}

// 模拟延迟
function simulateDelay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

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

// 生成场景 (调用后端并渲染拓扑)
async function generateScenario() {
  if (!topology) return
  try {
    // 清空当前拓扑图
    topology.clear()

    // 显示加载动画
    const loadingEl = document.getElementById('topology-loading')
    if (loadingEl) {
      loadingEl.style.display = 'flex'
    }

    // 创建预设拓扑图（半透明状态）
    await TopologyGenerator.createCompanyTopology(topology, true)

    logInfo('系统', '开始生成场景...')

    try {
      // 向后端请求启动预设的 docker-compose 文件
      const containerInfo = await TopologyService.startTopology('company-topology')

      // 更新设备状态
      TopologyGenerator.updateDevicesWithContainerInfo(topology, containerInfo)

      // 强制更新所有设备的视觉状态
      TopologyGenerator.forceUpdateDevicesVisualState(topology)

      // 显示成功消息
      logSuccess('系统', '场景生成成功')
    } catch (error) {
      console.error('生成场景失败', error)
      logError('系统', `生成场景失败: ${error.message}`)

      // 如果是超时错误，尝试获取当前容器状态
      if (error.name === 'AbortError') {
        logWarning('系统', '请求超时，尝试获取当前容器状态...')
      }
    } finally {
      // 隐藏加载动画
      if (loadingEl) {
        loadingEl.style.display = 'none'
      }
    }
  } catch (e) {
    console.error('生成场景失败', e)
    logError('系统', `生成场景失败: ${e.message}`)

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
function logMessage(level, source, message) {
  if (!message) {
    message = source
    source = '系统'
  }

  // 添加到系统日志
  const eventMonitorRef = document.querySelector('.event-monitor')
  if (eventMonitorRef && eventMonitorRef.__vue__) {
    eventMonitorRef.__vue__.addLog({
      level: level,
      source: source,
      message: message
    })
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
  const eventMonitorRef = document.querySelector('.event-monitor')
  if (eventMonitorRef && eventMonitorRef.__vue__) {
    eventMonitorRef.__vue__.addEvent(event)
  }
}

// 添加攻击事件
function addAttackEvent(message) {
  addEvent({
    type: 'attack',
    message: message
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
</style>