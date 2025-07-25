/**
 * 拓扑图调试助手
 * 用于诊断和调试拓扑图和攻击可视化的问题
 */

class TopologyDebugHelper {
  static checkTopologyStatus() {
    console.log('🔍 开始检查拓扑图状态...')
    
    // 检查 Canvas 元素
    const canvas = document.querySelector('#network-topology')
    console.log(`📋 Canvas 元素检查:`)
    console.log(`   存在: ${!!canvas}`)
    if (canvas) {
      console.log(`   ID: ${canvas.id}`)
      console.log(`   尺寸: ${canvas.width}x${canvas.height}`)
      console.log(`   样式尺寸: ${canvas.style.width} x ${canvas.style.height}`)
    }

    // 检查 Fabric.js 实例
    console.log(`📋 Fabric.js 实例检查:`)
    let fabricCanvas = null
    
    if (canvas) {
      // 检查各种可能的属性
      const fabricProps = ['__fabric', 'fabric', '_fabric']
      fabricProps.forEach(prop => {
        if (canvas[prop]) {
          console.log(`   ${prop}: 存在 (${canvas[prop].constructor?.name})`)
          fabricCanvas = canvas[prop]
        } else {
          console.log(`   ${prop}: 不存在`)
        }
      })
    }

    // 检查全局对象
    console.log(`📋 全局对象检查:`)
    console.log(`   window.topology: ${!!window.topology}`)
    if (window.topology) {
      console.log(`     canvas: ${!!window.topology.canvas}`)
      console.log(`     devices: ${Object.keys(window.topology.devices || {}).length}`)
      if (!fabricCanvas && window.topology.canvas) {
        fabricCanvas = window.topology.canvas
      }
    }
    
    console.log(`   window.topologyStore: ${!!window.topologyStore}`)
    if (window.topologyStore) {
      console.log(`     canvas: ${!!window.topologyStore.canvas}`)
    }

    // 检查 Fabric.js 对象
    if (fabricCanvas && fabricCanvas.getObjects) {
      console.log(`📋 Fabric.js 对象检查:`)
      const objects = fabricCanvas.getObjects()
      console.log(`   总对象数: ${objects.length}`)
      
      const deviceObjects = objects.filter(obj => obj.type !== 'connection' && obj.deviceData)
      const connectionObjects = objects.filter(obj => obj.type === 'connection')
      
      console.log(`   设备对象: ${deviceObjects.length}`)
      console.log(`   连接对象: ${connectionObjects.length}`)
      
      if (deviceObjects.length > 0) {
        console.log(`📋 设备对象详情:`)
        deviceObjects.forEach((obj, index) => {
          const deviceName = obj.deviceData?.name || '未知设备'
          const deviceType = obj.deviceData?.type || obj.type || '未知类型'
          const ip = obj.deviceData?.ip || ''
          console.log(`   ${index + 1}. "${deviceName}" [${deviceType}] ${ip ? `(${ip})` : ''} at (${Math.round(obj.left)}, ${Math.round(obj.top)})`)
        })
      }
    } else {
      console.log(`❌ 无法获取 Fabric.js 对象列表`)
    }

    return {
      canvas: !!canvas,
      fabricCanvas: !!fabricCanvas,
      objectCount: fabricCanvas?.getObjects?.()?.length || 0,
      deviceCount: fabricCanvas?.getObjects?.()?.filter(obj => obj.type !== 'connection' && obj.deviceData)?.length || 0
    }
  }

  static testNodeMapping() {
    console.log('🧪 开始测试节点映射...')
    
    const testNodes = ['internet', 'target_host', 'pc-user', 'internal-server', 'internal-db', 'unknown']
    
    testNodes.forEach(nodeId => {
      console.log(`\n🔍 测试节点: ${nodeId}`)
      
      // 模拟 TopologyAttackVisualizer 的节点映射逻辑
      const nodeMapping = {
        'internet': ['攻击者', '攻击节点', 'attacker', '外部攻击者'],
        'attacker': ['攻击者', '攻击节点', 'internet', '外部攻击者'],
        'target_host': ['PC-1', 'PC-2', '开发人员工作站', 'QA测试工作站'],
        'pc-user': ['PC-1', 'PC-2', '开发人员工作站', 'QA测试工作站'],
        'internal-server': ['服务器', 'Apache_web服务器', 'WordPress网站', 'Web服务器'],
        'internal-db': ['数据库', 'PostgreSQL', 'MySQL数据库服务器'],
        'unknown': [
          'PC-1', 'PC-2', '服务器', '数据库', 'PostgreSQL', 
          'Apache_web服务器', 'WordPress网站', 'DNS服务器'
        ]
      }
      
      const possibleNames = nodeMapping[nodeId] || [nodeId]
      console.log(`   可能的节点名称: ${possibleNames.join(', ')}`)
      
      // 尝试在拓扑图中查找
      const canvas = document.querySelector('#network-topology')
      let fabricCanvas = null
      
      if (canvas) {
        fabricCanvas = canvas.__fabric || canvas.fabric || canvas._fabric || window.topology?.canvas
      }
      
      if (fabricCanvas && fabricCanvas.getObjects) {
        const objects = fabricCanvas.getObjects()
        const deviceObjects = objects.filter(obj => obj.type !== 'connection' && obj.deviceData)
        
        let found = false
        for (const name of possibleNames) {
          const foundObject = deviceObjects.find(obj => {
            const deviceName = obj.deviceData?.name || obj.text || ''
            const containerName = obj.deviceData?.containerName || ''
            const description = obj.deviceData?.description || ''

            return deviceName === name ||
              deviceName.includes(name) ||
              containerName.includes(name.toLowerCase()) ||
              description.includes(name) ||
              name.includes(deviceName)
          })
          
          if (foundObject) {
            const centerX = foundObject.left + (foundObject.width || 50) / 2
            const centerY = foundObject.top + (foundObject.height || 50) / 2
            console.log(`   ✅ 匹配成功: "${foundObject.deviceData.name}" at (${Math.round(centerX)}, ${Math.round(centerY)})`)
            found = true
            break
          }
        }
        
        if (!found) {
          console.log(`   ❌ 未找到匹配的节点`)
        }
      } else {
        console.log(`   ⚠️ Fabric.js 实例不可用`)
      }
    })
  }

  static simulateAttackEvent(sourceNode = 'internet', targetNode = 'target_host') {
    console.log(`🎬 模拟攻击事件: ${sourceNode} -> ${targetNode}`)
    
    const attackInfo = {
      stage: 'reconnaissance',
      technique: '端口扫描',
      source_node: sourceNode,
      target_node: targetNode,
      progress: 50,
      status: 'in_progress'
    }
    
    const animationEvent = new CustomEvent('topology-animation', {
      detail: {
        type: 'attack_step',
        attackInfo: attackInfo,
        log: {
          timestamp: Date.now(),
          level: 'info',
          source: '调试助手',
          message: `[${attackInfo.stage}] ${attackInfo.technique}`,
          attack_info: attackInfo
        },
        timestamp: new Date()
      }
    })
    
    document.dispatchEvent(animationEvent)
    console.log('✅ 攻击事件已发送')
  }

  static clearAllAnimations() {
    console.log('🧹 清理所有动画...')
    
    // 触发重置事件
    const resetEvent = new CustomEvent('topology-reset-animations')
    document.dispatchEvent(resetEvent)
    
    console.log('✅ 动画清理完成')
  }

  static getTopologyInfo() {
    const status = this.checkTopologyStatus()
    
    return {
      ready: status.canvas && status.fabricCanvas && status.deviceCount > 0,
      canvas: status.canvas,
      fabricCanvas: status.fabricCanvas,
      objectCount: status.objectCount,
      deviceCount: status.deviceCount,
      timestamp: new Date().toISOString()
    }
  }
}

// 导出到全局对象
if (typeof window !== 'undefined') {
  window.TopologyDebugHelper = TopologyDebugHelper
  
  console.log('🔧 拓扑图调试助手已加载:')
  console.log('   - TopologyDebugHelper.checkTopologyStatus(): 检查拓扑图状态')
  console.log('   - TopologyDebugHelper.testNodeMapping(): 测试节点映射')
  console.log('   - TopologyDebugHelper.simulateAttackEvent(): 模拟攻击事件')
  console.log('   - TopologyDebugHelper.clearAllAnimations(): 清理所有动画')
  console.log('   - TopologyDebugHelper.getTopologyInfo(): 获取拓扑图信息')
}

export default TopologyDebugHelper
