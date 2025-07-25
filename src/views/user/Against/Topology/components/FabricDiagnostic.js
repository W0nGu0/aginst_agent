/**
 * Fabric.js 诊断工具
 * 用于诊断 Fabric.js Canvas 实例的问题
 */

class FabricDiagnostic {
  static diagnose() {
    console.log('🔍 开始 Fabric.js 诊断...')
    
    // 1. 检查 Fabric.js 库是否加载
    console.log('📋 Fabric.js 库检查:')
    console.log(`   window.fabric: ${!!window.fabric}`)
    if (window.fabric) {
      console.log(`   fabric.version: ${window.fabric.version || '未知'}`)
      console.log(`   fabric.Canvas: ${!!window.fabric.Canvas}`)
    }
    
    // 2. 检查 Canvas 元素
    const canvas = document.querySelector('#network-topology')
    console.log('📋 Canvas 元素检查:')
    console.log(`   元素存在: ${!!canvas}`)
    if (canvas) {
      console.log(`   tagName: ${canvas.tagName}`)
      console.log(`   id: ${canvas.id}`)
      console.log(`   width: ${canvas.width}`)
      console.log(`   height: ${canvas.height}`)
      console.log(`   clientWidth: ${canvas.clientWidth}`)
      console.log(`   clientHeight: ${canvas.clientHeight}`)
    }
    
    // 3. 检查所有可能的 Fabric 实例属性
    if (canvas) {
      console.log('📋 Fabric 实例属性检查:')
      const possibleProps = [
        '__fabric', 'fabric', '_fabric', 'fabricCanvas', 
        '__fabricCanvas', '_fabricCanvas', 'canvas'
      ]
      
      possibleProps.forEach(prop => {
        const value = canvas[prop]
        console.log(`   ${prop}: ${!!value} ${value ? `(${value.constructor?.name})` : ''}`)
        if (value && typeof value === 'object') {
          console.log(`     getObjects: ${typeof value.getObjects}`)
          console.log(`     renderAll: ${typeof value.renderAll}`)
        }
      })
      
      // 检查所有属性
      console.log('📋 Canvas 元素所有属性:')
      const props = Object.getOwnPropertyNames(canvas)
      const fabricProps = props.filter(prop => 
        prop.toLowerCase().includes('fabric') || 
        prop.toLowerCase().includes('canvas')
      )
      console.log(`   Fabric 相关属性: ${fabricProps.join(', ')}`)
    }
    
    // 4. 检查全局 topology 对象
    console.log('📋 全局对象检查:')
    console.log(`   window.topology: ${!!window.topology}`)
    if (window.topology) {
      console.log(`     topology.canvas: ${!!window.topology.canvas}`)
      console.log(`     topology.devices: ${Object.keys(window.topology.devices || {}).length}`)
      if (window.topology.canvas) {
        console.log(`     canvas.getObjects: ${typeof window.topology.canvas.getObjects}`)
        if (typeof window.topology.canvas.getObjects === 'function') {
          const objects = window.topology.canvas.getObjects()
          console.log(`     objects.length: ${objects.length}`)
        }
      }
    }
    
    // 5. 检查 Fabric.js 全局实例
    if (window.fabric && window.fabric.Canvas) {
      console.log('📋 Fabric.js 全局实例检查:')
      console.log(`   fabric.Canvas.getActiveCanvas: ${typeof window.fabric.Canvas.getActiveCanvas}`)
      if (typeof window.fabric.Canvas.getActiveCanvas === 'function') {
        const activeCanvas = window.fabric.Canvas.getActiveCanvas()
        console.log(`   activeCanvas: ${!!activeCanvas}`)
      }
    }
    
    return {
      fabricLoaded: !!window.fabric,
      canvasElement: !!canvas,
      topologyObject: !!window.topology,
      topologyCanvas: !!(window.topology?.canvas)
    }
  }
  
  static findFabricInstance() {
    console.log('🔍 尝试查找 Fabric.js 实例...')
    
    const canvas = document.querySelector('#network-topology')
    if (!canvas) {
      console.log('❌ Canvas 元素不存在')
      return null
    }
    
    // 方法1: 从 DOM 元素属性获取
    const possibleProps = [
      '__fabric', 'fabric', '_fabric', 'fabricCanvas', 
      '__fabricCanvas', '_fabricCanvas'
    ]
    
    for (const prop of possibleProps) {
      const instance = canvas[prop]
      if (instance && typeof instance.getObjects === 'function') {
        console.log(`✅ 找到 Fabric 实例: canvas.${prop}`)
        return instance
      }
    }
    
    // 方法2: 从全局对象获取
    if (window.topology?.canvas && typeof window.topology.canvas.getObjects === 'function') {
      console.log('✅ 找到 Fabric 实例: window.topology.canvas')
      return window.topology.canvas
    }
    
    // 方法3: 从 Fabric.js 全局获取
    if (window.fabric?.Canvas?.getActiveCanvas) {
      const activeCanvas = window.fabric.Canvas.getActiveCanvas()
      if (activeCanvas && typeof activeCanvas.getObjects === 'function') {
        console.log('✅ 找到 Fabric 实例: fabric.Canvas.getActiveCanvas()')
        return activeCanvas
      }
    }
    
    console.log('❌ 未找到 Fabric.js 实例')
    return null
  }
  
  static testFabricInstance() {
    const instance = this.findFabricInstance()
    if (!instance) {
      console.log('❌ 无法测试，未找到 Fabric 实例')
      return false
    }
    
    console.log('🧪 测试 Fabric 实例功能...')
    
    try {
      const objects = instance.getObjects()
      console.log(`✅ getObjects() 成功，对象数量: ${objects.length}`)
      
      const deviceObjects = objects.filter(obj => obj.deviceData)
      console.log(`✅ 设备对象数量: ${deviceObjects.length}`)
      
      if (deviceObjects.length > 0) {
        console.log('📋 设备对象示例:')
        deviceObjects.slice(0, 3).forEach((obj, index) => {
          console.log(`   ${index + 1}. ${obj.deviceData?.name || '未知'} at (${obj.left}, ${obj.top})`)
        })
      }
      
      return true
    } catch (error) {
      console.error('❌ Fabric 实例测试失败:', error)
      return false
    }
  }
  
  static waitForFabric(maxWait = 30000, interval = 500) {
    console.log(`⏳ 等待 Fabric.js 实例准备就绪 (最多等待 ${maxWait/1000} 秒)...`)
    
    return new Promise((resolve, reject) => {
      const startTime = Date.now()
      
      const check = () => {
        const instance = this.findFabricInstance()
        if (instance) {
          const objects = instance.getObjects()
          const deviceObjects = objects.filter(obj => obj.deviceData)
          
          if (deviceObjects.length > 0) {
            console.log(`✅ Fabric.js 实例准备就绪，设备数量: ${deviceObjects.length}`)
            resolve(instance)
            return
          }
        }
        
        const elapsed = Date.now() - startTime
        if (elapsed >= maxWait) {
          console.log('⏰ 等待超时')
          reject(new Error('Fabric.js 实例等待超时'))
          return
        }
        
        setTimeout(check, interval)
      }
      
      check()
    })
  }
}

// 导出到全局
if (typeof window !== 'undefined') {
  window.FabricDiagnostic = FabricDiagnostic
  
  console.log('🔧 Fabric.js 诊断工具已加载:')
  console.log('   - FabricDiagnostic.diagnose(): 完整诊断')
  console.log('   - FabricDiagnostic.findFabricInstance(): 查找实例')
  console.log('   - FabricDiagnostic.testFabricInstance(): 测试实例')
  console.log('   - FabricDiagnostic.waitForFabric(): 等待实例准备')
}

export default FabricDiagnostic
