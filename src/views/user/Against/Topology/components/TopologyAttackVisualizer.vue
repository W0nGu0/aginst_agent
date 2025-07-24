<template>
  <div class="topology-attack-visualizer">
    <!-- SVG 攻击效果覆盖层 - 只显示攻击动画，不显示拓扑图 -->
    <div class="attack-effects-container" ref="topologyContainer">
      <svg ref="topologySvg" class="attack-effects-svg" :width="svgWidth" :height="svgHeight" viewBox="0 0 1000 600">
        <!-- 定义渐变和滤镜 -->
        <defs>
          <!-- 攻击路径渐变 -->
          <linearGradient id="attackGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#ff6b6b;stop-opacity:0" />
            <stop offset="50%" style="stop-color:#ff6b6b;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#ff6b6b;stop-opacity:0" />
          </linearGradient>

          <!-- 扫描脉冲渐变 -->
          <radialGradient id="scanPulse" cx="50%" cy="50%" r="50%">
            <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:0.8" />
            <stop offset="70%" style="stop-color:#3b82f6;stop-opacity:0.3" />
            <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:0" />
          </radialGradient>

          <!-- 攻击成功渐变 -->
          <radialGradient id="compromisedGradient" cx="50%" cy="50%" r="50%">
            <stop offset="0%" style="stop-color:#dc2626;stop-opacity:0.9" />
            <stop offset="100%" style="stop-color:#991b1b;stop-opacity:0.6" />
          </radialGradient>

          <!-- 发光滤镜 -->
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur" />
            <feMerge>
              <feMergeNode in="coloredBlur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <!-- 移除网络连接线，使用原拓扑图的连接 -->

        <!-- 攻击路径动画 -->
        <g class="attack-paths">
          <g v-for="path in activePaths" :key="path.id">
            <!-- 攻击路径线 -->
            <line :x1="path.x1" :y1="path.y1" :x2="path.x2" :y2="path.y2" :stroke="path.color" stroke-width="4"
              class="attack-path-line" />

            <!-- 攻击数据包 -->
            <circle v-if="path.showPacket" :r="6" :fill="path.color" class="attack-packet" filter="url(#glow)">
              <animateMotion :dur="path.duration + 'ms'" repeatCount="indefinite"
                :path="`M ${path.x1} ${path.y1} L ${path.x2} ${path.y2}`" />
            </circle>
          </g>
        </g>

        <!-- 移除网络节点，使用原拓扑图的节点 -->

        <!-- 攻击进度指示器 -->
        <g v-if="currentAttackStep" class="attack-progress-indicator">
          <rect x="20" y="20" width="350" height="100" rx="10" fill="rgba(0,0,0,0.8)" stroke="#3b82f6"
            stroke-width="2" />
          <text x="40" y="45" class="step-title" fill="#3b82f6" font-size="16" font-weight="bold">
            {{ currentAttackStep.stage }}: {{ currentAttackStep.technique }}
          </text>
          <text x="40" y="70" class="step-description" fill="#9ca3af" font-size="12">
            {{ currentAttackStep.source_node }} → {{ currentAttackStep.target_node }}
          </text>
          <rect x="40" y="80" :width="currentAttackStep.progress * 2.7" height="6"
            :fill="getProgressColor(currentAttackStep.status)" rx="3" />
          <text x="40" y="100" class="progress-text" fill="#9ca3af" font-size="10">
            进度: {{ currentAttackStep.progress }}% - {{ currentAttackStep.status }}
          </text>
        </g>
      </svg>

      <!-- Canvas 层用于高性能动画效果 -->
      <canvas ref="animationCanvas" class="animation-canvas" :width="svgWidth" :height="svgHeight"></canvas>
    </div>


  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted } from 'vue'

export default {
  name: 'TopologyAttackVisualizer',
  props: {
    width: {
      type: Number,
      default: 1000
    },
    height: {
      type: Number,
      default: 600
    }
  },
  setup(props) {
    const topologyContainer = ref(null)
    const topologySvg = ref(null)
    const animationCanvas = ref(null)
    const svgWidth = ref(props.width)
    const svgHeight = ref(props.height)

    // 当前攻击步骤信息（与EventMonitor同步）
    const currentAttackStep = ref(null)

    // 动态获取节点位置的函数
    const getNodePosition = (nodeId) => {
      // 节点名称映射到真实拓扑图节点
      const nodeMapping = {
        'internet': ['互联网', 'Internet', '外网'],
        'firewall': ['防火墙', '内部防火墙', '外部防火墙'],
        'pc-user': ['PC-1', 'PC-2', '用户PC', '攻击者'],
        'internal-server': ['服务器', '内部服务器', 'Apache_web服务器', 'WordPress网站'],
        'internal-db': ['数据库', 'PostgreSQL', 'cnt-db'],
        'target_host': ['PC-1', 'PC-2', '用户PC'],
        'unknown': ['服务器', '数据库']
      }

      const possibleNames = nodeMapping[nodeId] || [nodeId]

      // 尝试从Fabric.js canvas获取节点位置
      const canvas = document.querySelector('#network-topology')
      if (canvas && canvas.__fabricCanvas) {
        const objects = canvas.__fabricCanvas.getObjects()

        for (const name of possibleNames) {
          const foundObject = objects.find(obj =>
            obj.deviceData?.name?.includes(name) ||
            obj.deviceData?.containerName?.includes(name.toLowerCase()) ||
            obj.text?.includes(name)
          )

          if (foundObject) {
            console.log(`✅ 找到节点 ${nodeId} -> ${name}:`, foundObject.left, foundObject.top)
            return {
              x: foundObject.left || 0,
              y: foundObject.top || 0
            }
          }
        }
      }

      // 如果找不到节点，返回默认位置
      console.warn(`❌ 未找到节点 ${nodeId} 的位置，使用默认位置`)
      return { x: 400, y: 300 }
    }

    // 活跃攻击路径
    const activePaths = reactive([])

    // 监听拓扑动画事件
    const handleTopologyAnimation = (event) => {
      const { attackInfo } = event.detail

      console.log('🎯 TopologyAttackVisualizer收到拓扑动画事件:', attackInfo)
      console.log('🎯 事件详情:', event.detail)

      // 更新当前攻击步骤
      currentAttackStep.value = {
        stage: getStageDisplayName(attackInfo.stage),
        technique: attackInfo.technique,
        source_node: attackInfo.source_node,
        target_node: attackInfo.target_node,
        progress: attackInfo.progress,
        status: getStatusDisplayName(attackInfo.status)
      }

      // 更新网络节点状态
      updateNodeStatus(attackInfo)

      // 创建攻击路径动画
      createAttackPathAnimation(attackInfo)
    }

    // 更新节点状态
    const updateNodeStatus = (attackInfo) => {
      const targetNode = findNodeById(attackInfo.target_node)
      if (!targetNode) return

      if (attackInfo.status === 'starting') {
        targetNode.status = 'scanning'
        targetNode.attackLevel = Math.max(targetNode.attackLevel, 10)
      } else if (attackInfo.status === 'in_progress') {
        targetNode.status = 'under_attack'
        targetNode.attackLevel = Math.max(targetNode.attackLevel, attackInfo.progress || 50)
      } else if (attackInfo.status === 'completed') {
        targetNode.status = 'compromised'
        targetNode.attackLevel = 100
      } else if (attackInfo.status === 'failed') {
        targetNode.status = 'normal'
        targetNode.attackLevel = Math.max(0, targetNode.attackLevel - 20)
      }
    }

    // 创建攻击路径动画
    const createAttackPathAnimation = (attackInfo) => {
      const sourceNode = findNodeById(attackInfo.source_node)
      const targetNode = findNodeById(attackInfo.target_node)

      if (!sourceNode || !targetNode) return

      const pathId = `${attackInfo.source_node}-${attackInfo.target_node}-${Date.now()}`

      const attackPath = {
        id: pathId,
        x1: sourceNode.x,
        y1: sourceNode.y,
        x2: targetNode.x,
        y2: targetNode.y,
        color: getAttackColor(attackInfo.stage),
        duration: 2000,
        showPacket: true
      }

      activePaths.push(attackPath)

      // 2秒后移除路径
      setTimeout(() => {
        const index = activePaths.findIndex(p => p.id === pathId)
        if (index > -1) {
          activePaths.splice(index, 1)
        }
      }, 3000)
    }

    // 工具函数
    const findNodeById = (id) => {
      const position = getNodePosition(id)
      return position ? { ...position, id } : null
    }

    const getStageDisplayName = (stage) => {
      const stageNames = {
        'reconnaissance': '侦察阶段',
        'weaponization': '武器化阶段',
        'delivery': '投递阶段',
        'exploitation': '利用阶段',
        'installation': '安装阶段',
        'command_and_control': '命令控制阶段',
        'actions_on_objectives': '行动目标阶段'
      }
      return stageNames[stage] || stage
    }

    const getStatusDisplayName = (status) => {
      const statusNames = {
        'starting': '开始',
        'in_progress': '进行中',
        'completed': '完成',
        'failed': '失败'
      }
      return statusNames[status] || status
    }

    const getAttackColor = (stage) => {
      const colors = {
        'reconnaissance': '#3b82f6',
        'weaponization': '#f59e0b',
        'delivery': '#ef4444',
        'exploitation': '#dc2626',
        'installation': '#7c2d12',
        'command_and_control': '#7c3aed',
        'actions_on_objectives': '#059669'
      }
      return colors[stage] || '#6b7280'
    }

    const getNodeFill = (node) => {
      switch (node.status) {
        case 'scanning': return '#fbbf24'
        case 'under_attack': return '#f87171'
        case 'compromised': return 'url(#compromisedGradient)'
        default: return '#10b981'
      }
    }

    const getNodeStroke = (node) => {
      switch (node.status) {
        case 'scanning': return '#f59e0b'
        case 'under_attack': return '#ef4444'
        case 'compromised': return '#dc2626'
        default: return '#059669'
      }
    }

    const getNodeIcon = (node) => {
      const iconMap = {
        'external': '/图标/互联网.svg',
        'security': '/图标/防火墙.svg',
        'server': '/图标/服务器.svg',
        'endpoint': '/图标/pc.svg'
      }
      return iconMap[node.type] || '/图标/服务器.svg'
    }

    const getAttackLevelColor = (level) => {
      if (level >= 80) return '#991b1b'
      if (level >= 60) return '#dc2626'
      if (level >= 40) return '#ef4444'
      if (level >= 20) return '#f59e0b'
      return '#10b981'
    }

    const getProgressColor = (status) => {
      switch (status) {
        case '完成': return '#10b981'
        case '失败': return '#ef4444'
        case '进行中': return '#3b82f6'
        default: return '#6b7280'
      }
    }

    // 生命周期
    onMounted(() => {
      // 立即初始化组件
      console.log('🚀 拓扑攻击可视化组件开始初始化...')

      // 监听拓扑动画事件
      document.addEventListener('topology-animation', handleTopologyAnimation)
      console.log('✅ 事件监听器已注册')

      // 等待拓扑图加载完成后再初始化
      const initializeWhenReady = () => {
        const canvas = document.querySelector('#network-topology')
        if (canvas && canvas.__fabricCanvas) {
          console.log('✅ 拓扑图已加载，攻击可视化组件准备就绪')
          // 可以在这里添加一些初始化逻辑
        } else {
          console.log('⏳ 等待拓扑图加载...')
          setTimeout(initializeWhenReady, 500)
        }
      }

      // 立即尝试初始化，如果拓扑图还没加载就等待
      initializeWhenReady()

      console.log('🎯 拓扑攻击可视化组件已初始化，等待真实攻击事件...')
    })

    // 重置动画状态
    const resetAnimation = () => {
      console.log('重置动画状态')

      // 清空攻击路径
      activePaths.splice(0, activePaths.length)

      // 清空当前攻击步骤
      currentAttackStep.value = null
    }

    onUnmounted(() => {
      // 清理事件监听器
      document.removeEventListener('topology-animation', handleTopologyAnimation)
    })

    return {
      topologyContainer,
      topologySvg,
      animationCanvas,
      svgWidth,
      svgHeight,
      currentAttackStep,
      activePaths,
      getNodeFill,
      getNodeStroke,
      getNodeIcon,
      getAttackLevelColor,
      getProgressColor,
      resetAnimation
    }
  }
}
</script>

<style scoped>
.topology-attack-visualizer {
  position: relative;
  width: 100%;
  height: 100%;
  background: transparent;
  /* 移除背景，让原拓扑图显示 */
  pointer-events: none;
  /* 不阻挡原拓扑图的交互 */
  overflow: hidden;
}

.topology-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.topology-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.animation-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  pointer-events: none;
}

.connection-line {
  transition: all 0.3s ease;
}

.network-node {
  cursor: pointer;
  transition: all 0.3s ease;
}

.node-icon {
  pointer-events: none;
}

.node-label {
  font-size: 12px;
  font-weight: 600;
  fill: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
}

.attack-path-line {
  stroke-dasharray: 10, 5;
  animation: dash 1s linear infinite;
  opacity: 0.8;
}

.attack-packet {
  animation: packet-glow 1s ease-in-out infinite alternate;
}

.attack-level-circle {
  animation: level-pulse 1.5s ease-in-out infinite;
}

@keyframes dash {
  to {
    stroke-dashoffset: -20;
  }
}

@keyframes packet-glow {
  0% {
    filter: drop-shadow(0 0 5px currentColor);
  }

  100% {
    filter: drop-shadow(0 0 15px currentColor);
  }
}

@keyframes level-pulse {

  0%,
  100% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.2);
  }
}

.scan-pulse {
  animation: scan-pulse 2s ease-in-out infinite;
}

@keyframes scan-pulse {
  0% {
    opacity: 0.8;
    transform: scale(1);
  }

  50% {
    opacity: 0.4;
    transform: scale(1.2);
  }

  100% {
    opacity: 0.8;
    transform: scale(1);
  }
}

/* 控制面板样式 */
.control-panel {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  gap: 10px;
  z-index: 10;
}

.demo-btn,
.reset-btn {
  padding: 10px 15px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.demo-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.demo-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.reset-btn {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.reset-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}
</style>