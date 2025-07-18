<template>
  <div class="topology-view">
    <div class="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-6">
      <!-- 左侧控制面板 -->
      <div class="bg-base-100 rounded-lg p-4 border border-base-300/30 mb-6">
        <h2 class="text-xl font-semibold mb-4 flex items-center">
          <span class="text-primary mr-2">#</span>设备库
        </h2>
        
        <div class="device-grid">
          <div 
            v-for="(color, type) in deviceTypes" 
            :key="type"
            class="device-item" 
            @click="createDevice(type)">
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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useTopologyStore } from '../../../../stores/topology'
import { fabric } from 'fabric'

const topologyStore = useTopologyStore()
let topology = null
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
  'cloud': '#00bcd4',       // 云服务/互联网
  'vpn': '#009688',         // VPN网关
  'dns': '#8bc34a',         // DNS服务器
  'proxy': '#ff5722',       // 代理服务器
  'load': '#673AB7'         // 负载均衡器
}

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
    // 监听事件
    topology.on('objectSelected', (data) => {
      topologyStore.setSelectedObject(data.object)
    })
    
    // 初始化canvas
    topologyStore.setCanvas(topology.canvas)
  }).catch(err => {
    console.error('拓扑图初始化失败:', err)
  })
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
    await createCompanyTopology(true)
    
    // 向后端请求启动预设的 docker-compose 文件
    const resp = await fetch('/api/topology', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'start',
        template: 'company-topology' // 指定使用哪个预设模板
      })
    })
    
    const data = await resp.json()
    console.log('后端返回的容器信息', data)
    
    // 隐藏加载动画
    if (loadingEl) {
      loadingEl.style.display = 'none'
    }
    
    // 更新设备状态（变为实色）
    updateDevicesWithContainerInfo(data)
  } catch (e) {
    console.error('生成场景失败', e)
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
  try {
    await fetch('/api/topology', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({action:'stop'}) })
  } catch (e) {
    console.error('销毁场景失败', e)
  }
  // 清空画布
  topology.clear()
  topologyStore.devices = {}
  topologyStore.connections = []
}

// 根据容器信息更新设备
function updateDevicesWithContainerInfo(containerInfo) {
  if (!containerInfo || !containerInfo.running_services) return
  
  // 遍历所有设备，更新状态
  for (const [id, device] of Object.entries(topology.devices)) {
    const deviceName = device.deviceData.name
    
    // 查找对应的容器信息
    const containerData = containerInfo.running_services.find(
      service => service.name === deviceName || service.name.includes(deviceName)
    )
    
    if (containerData) {
      // 更新设备数据
      device.deviceData.status = 'running'
      device.deviceData.containerId = containerData.id
      device.deviceData.containerIp = containerData.ip || device.deviceData.ip
      
      // 更新设备标签，显示IP
      topology._updateLabel(device, `${device.deviceData.name}\n${device.deviceData.containerIp}`)
      
      // 可以添加视觉指示器表示设备正在运行
      device.set({ opacity: 1 })
    } else {
      // 设备未运行
      device.deviceData.status = 'stopped'
      device.set({ opacity: 0.6 })
    }
  }
  
  // 刷新画布
  topology.canvas.requestRenderAll()
}

// 根据 docker-compose 文件创建公司拓扑图
async function createCompanyTopology(isTransparent = false) {
  // 防止重复生成
  topology.clear()
  
  // 设置透明度
  const opacity = isTransparent ? 0.6 : 1
  
  // 创建防火墙设备
  const internalFW = await topology.createDevice('firewall', { 
    left: 400, 
    top: 300, 
    deviceData: { 
      name: '内部防火墙', 
      ip: '192.168.200.254',
      description: '内部网络防火墙'
    }
  })
  internalFW.set({ opacity })
  
  const externalFW = await topology.createDevice('firewall', { 
    left: 650, 
    top: 300, 
    deviceData: { 
      name: '外部防火墙', 
      ip: '199.203.100.2',
      description: 'DMZ区域防火墙'
    }
  })
  externalFW.set({ opacity })
  
  // 连接两个防火墙
  topology.addConnection(internalFW, externalFW)
  
  // 创建服务器段设备
  const sqlServer = await topology.createDevice('db', { 
    left: 200, 
    top: 150, 
    deviceData: { 
      name: '数据库', 
      ip: '192.168.200.23',
      description: 'MySQL数据库服务器'
    }
  })
  sqlServer.set({ opacity })
  
  const fileServer = await topology.createDevice('file', { 
    left: 200, 
    top: 250, 
    deviceData: { 
      name: '文件服务器', 
      ip: '192.168.200.6',
      description: '企业文件存储服务器'
    }
  })
  fileServer.set({ opacity })
  
  // 创建邮件服务器
  const syslogServer = await topology.createDevice('server', { 
    left: 200, 
    top: 350, 
    deviceData: { 
      name: '邮件服务器', 
      ip: '192.168.66.20',
      description: '邮件存储服务器'
    }
  })
  syslogServer.set({ opacity })
  
  // 创建用户段设备
  const workstation1 = await topology.createDevice('pc', { 
    left: 200, 
    top: 450, 
    deviceData: { 
      name: 'PC-1', 
      ip: '192.168.100.9',
      description: '开发人员工作站'
    }
  })
  workstation1.set({ opacity })
  
  const workstation2 = await topology.createDevice('pc', { 
    left: 200, 
    top: 550, 
    deviceData: { 
      name: 'PC-2', 
      ip: '192.168.100.34',
      description: 'QA测试工作站'
    }
  })
  workstation2.set({ opacity })
  
  // 创建 VPN 设备
  const vpnServer = await topology.createDevice('vpn', { 
    left: 400, 
    top: 150, 
    deviceData: { 
      name: 'VPN网关', 
      ip: '192.168.110.5',
      description: '远程访问VPN服务器'
    }
  })
  vpnServer.set({ opacity })
  
  // 创建数据库段设备
  const pgdbServer = await topology.createDevice('db', { 
    left: 400, 
    top: 450, 
    deviceData: { 
      name: 'PostgreSQL', 
      ip: '192.168.214.10',
      description: 'PostgreSQL数据库服务器'
    }
  })
  pgdbServer.set({ opacity })
  
  // 连接内部设备到内部防火墙
  ;[sqlServer, fileServer, syslogServer, workstation1, workstation2, vpnServer, pgdbServer].forEach(dev => {
    topology.addConnection(internalFW, dev)
  })
  
  // 创建 DMZ 段设备
  const wpServer = await topology.createDevice('web', { 
    left: 850, 
    top: 150, 
    deviceData: { 
      name: 'WordPress网站', 
      ip: '172.16.100.10',
      description: '企业WordPress网站'
    }
  })
  wpServer.set({ opacity })
  
  const apacheServer = await topology.createDevice('web', { 
    left: 850, 
    top: 250, 
    deviceData: { 
      name: 'Apache_web服务器', 
      ip: '172.16.100.11',
      description: 'Apache Web服务器'
    }
  })
  apacheServer.set({ opacity })
  
  const dnsServer = await topology.createDevice('dns', { 
    left: 850, 
    top: 350, 
    deviceData: { 
      name: 'DNS服务器', 
      ip: '172.16.100.53',
      description: '域名解析服务器'
    }
  })
  dnsServer.set({ opacity })
  
  const mailServer = await topology.createDevice('mail', { 
    left: 850, 
    top: 450, 
    deviceData: { 
      name: '邮件服务器', 
      ip: '172.16.100.25',
      description: '企业邮件中继服务器'
    }
  })
  mailServer.set({ opacity })
  
  // 创建互联网
  const internet = await topology.createDevice('cloud', { 
    left: 850, 
    top: 550, 
    deviceData: { 
      name: '互联网', 
      ip: '199.203.100.1',
      description: '外部互联网'
    }
  })
  internet.set({ opacity })
  
  // 创建攻击者
  const attacker = await topology.createDevice('pc', { 
    left: 1000, 
    top: 350, 
    deviceData: { 
      name: '攻击者', 
      ip: '199.203.100.10',
      description: '外部攻击者'
    }
  })
  attacker.set({ opacity })
  
  const attackNode = await topology.createDevice('pc', { 
    left: 1000, 
    top: 450, 
    deviceData: { 
      name: '攻击节点', 
      ip: '199.203.100.11',
      description: '攻击跳板机'
    }
  })
  attackNode.set({ opacity })
  
  // 连接 DMZ 设备到外部防火墙
  ;[wpServer, apacheServer, dnsServer, mailServer].forEach(dev => {
    topology.addConnection(externalFW, dev)
  })
  
  // 连接互联网和攻击者
  topology.addConnection(externalFW, internet)
  topology.addConnection(internet, attacker)
  topology.addConnection(internet, attackNode)
  
  return {
    internalFW, externalFW, sqlServer, fileServer, syslogServer, workstation1, workstation2,
    vpnServer, pgdbServer, wpServer, apacheServer, dnsServer, mailServer, internet,
    attacker, attackNode
  }
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
    'cloud': '/图标/互联网.svg',
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
    'cloud': '互联网',
    'vpn': 'VPN网关',
    'dns': 'DNS服务器',
    'proxy': '代理服务器',
    'load': '负载均衡'
  }

  return typeMap[type] || type
}

// 网络拓扑图类
class NetworkTopology {
  constructor(options = {}) {
    this.options = Object.assign({
      canvasId: 'network-topology',
      width: 1280,
      height: 720,
      backgroundColor: 'rgba(30, 30, 47, 0.5)'
    }, options);

    // 状态
    this.mode = 'select'; // 'select', 'connect', 'pan'
    this.devices = {};
    this.connections = [];
    this.selectedObject = null;
    this.connecting = null; // 用于连接模式

    // 设备颜色
    this.deviceColors = topologyStore.deviceColors;

    // 连接类型
    this.connectionTypes = topologyStore.connectionTypes;

    // 事件监听器
    this.eventListeners = {};
  }

  // 初始化拓扑图
  initialize() {
    return new Promise((resolve, reject) => {
      try {
        // 调试 - 检查canvas元素是否存在
        const canvasEl = document.getElementById(this.options.canvasId);
        if (!canvasEl) {
          throw new Error(`找不到ID为${this.options.canvasId}的canvas元素`);
        }

        // 创建Canvas
        this.canvas = new fabric.Canvas(this.options.canvasId, {
          backgroundColor: this.options.backgroundColor,
          selection: true,
          width: this.options.width,
          height: this.options.height
        });

        this.resizeCanvas(this.options.width, this.options.height);

        // 设置事件
        this._setupEvents();

        // 隐藏加载动画
        const loadingEl = document.getElementById('topology-loading');
        if (loadingEl) {
          loadingEl.style.display = 'none';
        }

        // 触发初始化完成事件
        this._triggerEvent('initialized');
        resolve(this);

      } catch (error) {
        console.error('拓扑图初始化失败:', error);
        reject(error);
      }
    });
  }

  // 调整画布尺寸
  resizeCanvas(w, h) {
    if (!this.canvas) return;
    this.canvas.setWidth(w);
    this.canvas.setHeight(h);
    this.canvas.requestRenderAll();
  }

  // 设置模式
  setMode(mode) {
    if (['select', 'connect', 'pan'].includes(mode)) {
      this.mode = mode;

      // 重置连接状态
      if (mode !== 'connect') {
        this.connecting = null;
      }

      // 设置画布交互状态
      if (mode === 'pan') {
        this.canvas.selection = false;
        this.canvas.forEachObject(function (obj) {
          obj.selectable = false;
        });
      } else {
        this.canvas.selection = true;
        this.canvas.forEachObject(function (obj) {
          obj.selectable = true;
        });
      }

      // 触发模式改变事件
      this._triggerEvent('modeChange', { mode });
      return true;
    }
    return false;
  }

  // 创建设备（使用图标）
  createDevice(type, options = {}) {
    return new Promise((resolve) => {
      const deviceType = type || 'server';
      const defaults = {
        left: 100 + Math.random() * 400,
        top: 100 + Math.random() * 200,
        size: 64,
        name: this._getDefaultName(deviceType),
        ip: this._generateRandomIP()
      };

      const deviceOptions = Object.assign({}, defaults, options);

      const iconPath = getDeviceIcon(deviceType);

      const finalizeDevice = (fabricObj) => {
        fabricObj.set({
          left: deviceOptions.left,
          top: deviceOptions.top,
          width: deviceOptions.size,
          height: deviceOptions.size,
          type: 'device',
          deviceType: deviceType,
          deviceData: {
            name: deviceOptions.deviceData?.name || deviceOptions.name,
            ip: deviceOptions.deviceData?.ip || deviceOptions.ip,
            mac: deviceOptions.deviceData?.mac || this._generateRandomMAC(),
            description: deviceOptions.deviceData?.description || ''
          }
        });

        // 居中锚点
        fabricObj.set({ originX: 'center', originY: 'center' });

        // 添加到Canvas
        this.canvas.add(fabricObj);

        // 添加标签
        this._addLabel(fabricObj, fabricObj.deviceData.name);

        // 创建ID
        const deviceId = `device_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
        this.devices[deviceId] = fabricObj;
        fabricObj.id = deviceId;

        topologyStore.addDevice(fabricObj, deviceId);

        // 触发事件
        this._triggerEvent('deviceCreated', { device: fabricObj, id: deviceId });

        resolve(fabricObj);
      };

      if (iconPath) {
        fabric.Image.fromURL(iconPath, (img) => {
          // 调整尺寸
          const scale = deviceOptions.size / Math.max(img.width, img.height);
          img.scale(scale);
          
          // 创建背景矩形，使图标更美观
          const bgColor = this.deviceColors[deviceType] || '#EFF6FF';
          const rect = new fabric.Rect({
            width: deviceOptions.size,
            height: deviceOptions.size,
            fill: bgColor,
            rx: 12,
            ry: 12,
            stroke: '#E2E8F0',
            strokeWidth: 1
          });
          
          // 创建图标组合
          const group = new fabric.Group([rect, img], {
            left: 0,
            top: 0,
            originX: 'center',
            originY: 'center'
          });
          
          finalizeDevice(group);
        }, { crossOrigin: 'anonymous' });
      } else {
        // 无图标时使用矩形
        const rect = new fabric.Rect({
          width: deviceOptions.size,
          height: deviceOptions.size,
          fill: '#EFF6FF',
          rx: 12,
          ry: 12,
          stroke: '#E2E8F0',
          strokeWidth: 1
        });
        finalizeDevice(rect);
      }
    });
  }

  // 清空拓扑
  clear() {
    if (this.canvas) {
      this.canvas.clear();
    }
    this.devices = {};
    this.connections = [];
  }

  // 添加连接
  addConnection(source, target, type = 'ethernet') {
    if (!source || !target || source === target) {
      return null;
    }

    const connType = this.connectionTypes[type] || this.connectionTypes.ethernet;

    // 创建连接线
    const line = new fabric.Line([
      source.left,
      source.top,
      target.left,
      target.top
    ], {
      stroke: connType.color,
      strokeWidth: connType.width,
      strokeDashArray: connType.dash,
      selectable: true,
      type: 'connection',
      connectionType: type,
      source: source,
      target: target
    });

    // 添加到Canvas
    this.canvas.add(line);
    line.sendToBack();

    // 添加到连接数组
    this.connections.push(line);

    // 添加到状态管理
    topologyStore.addConnection(line);

    // 添加移动事件
    this._setupConnectionEvents(line, source, target);

    // 触发连接创建事件
    this._triggerEvent('connectionCreated', { connection: line, source, target });

    return line;
  }

  // 删除选中对象
  deleteSelected() {
    const obj = this.canvas.getActiveObject();
    if (!obj) return false;

    // 如果是设备，同时删除标签和相关连接
    if (obj.type === 'device') {
      // 删除标签
      if (obj.label) {
        this.canvas.remove(obj.label);
      }

      // 删除相关连接
      const connectionsToRemove = this.connections.filter(
        conn => conn.source === obj || conn.target === obj
      );

      connectionsToRemove.forEach(conn => {
        this.canvas.remove(conn);
        this.connections = this.connections.filter(c => c !== conn);
        topologyStore.removeConnection(conn);
      });

      // 从设备集合中移除
      for (let id in this.devices) {
        if (this.devices[id] === obj) {
          delete this.devices[id];
          topologyStore.removeDevice(id);
          break;
        }
      }
    }

    // 如果是连接
    if (obj.type === 'connection') {
      this.connections = this.connections.filter(conn => conn !== obj);
      topologyStore.removeConnection(obj);
    }

    // 从Canvas中移除
    this.canvas.remove(obj);

    // 清空选择
    topologyStore.setSelectedObject(null);

    // 刷新Canvas
    this.canvas.requestRenderAll();

    return true;
  }

  // 缩放控制
  zoomIn() {
    const zoom = this.canvas.getZoom();
    this.canvas.setZoom(zoom * 1.1);
  }

  zoomOut() {
    const zoom = this.canvas.getZoom();
    this.canvas.setZoom(zoom * 0.9);
  }

  resetView() {
    this.canvas.setZoom(1);
    this.canvas.setViewportTransform([1, 0, 0, 1, 0, 0]);
  }

  // 注册事件监听
  on(eventName, callback) {
    if (!this.eventListeners[eventName]) {
      this.eventListeners[eventName] = [];
    }
    this.eventListeners[eventName].push(callback);
  }

  // 添加标签
  _addLabel(device, text) {
    // 如果已有标签，先删除
    if (device.label) {
      this.canvas.remove(device.label);
    }

    const label = new fabric.Text(text, {
      left: device.left,
      top: device.top + device.height / 2 + 10,
      fontSize: 14,
      fill: '#ffffff',
      textAlign: 'center',
      originX: 'center',
      originY: 'center'
    });

    this.canvas.add(label);
    label.associatedDevice = device;
    device.label = label;

    return label;
  }

  // 更新标签
  _updateLabel(device, text) {
    if (device.label) {
      device.label.set({
        text: text
      });
    } else {
      this._addLabel(device, text);
    }
  }

  // 设置连接事件
  _setupConnectionEvents(connection, source, target) {
    // 在设备移动时更新连接
    source.on('moving', () => this._updateConnection(connection));
    target.on('moving', () => this._updateConnection(connection));
  }

  // 更新连接
  _updateConnection(connection) {
    if (!connection || !connection.source || !connection.target) return;

    connection.set({
      x1: connection.source.left,
      y1: connection.source.top,
      x2: connection.target.left,
      y2: connection.target.top
    });

    connection.setCoords();
    this.canvas.requestRenderAll();
  }

  // 设置事件
  _setupEvents() {
    if (!this.canvas) return;

    // 对象选择事件
    this.canvas.on('selection:created', (e) => {
      this.selectedObject = e.selected[0];
      this._triggerEvent('objectSelected', { object: this.selectedObject });
    });

    this.canvas.on('selection:updated', (e) => {
      this.selectedObject = e.selected[0];
      this._triggerEvent('objectSelected', { object: this.selectedObject });
    });

    this.canvas.on('selection:cleared', () => {
      this.selectedObject = null;
      this._triggerEvent('objectSelected', { object: null });
    });

    // 对象点击事件 - 用于连接模式
    this.canvas.on('mouse:down', (e) => {
      if (this.mode !== 'connect' || !e.target || e.target.type !== 'device') return;

      if (!this.connecting) {
        // 开始连接
        this.connecting = e.target;
      } else if (this.connecting !== e.target) {
        // 完成连接
        this.addConnection(this.connecting, e.target);
        this.connecting = null;
      }
    });

    // 平移模式
    this.canvas.on('mouse:down', (e) => {
      if (this.mode !== 'pan') return;

      this.isPanning = true;
      this.lastPosX = e.e.clientX;
      this.lastPosY = e.e.clientY;
    });

    this.canvas.on('mouse:move', (e) => {
      if (!this.isPanning) return;

      const vpt = this.canvas.viewportTransform;
      vpt[4] += e.e.clientX - this.lastPosX;
      vpt[5] += e.e.clientY - this.lastPosY;
      this.canvas.requestRenderAll();
      this.lastPosX = e.e.clientX;
      this.lastPosY = e.e.clientY;
    });

    this.canvas.on('mouse:up', () => {
      this.isPanning = false;
    });

    // 标签移动事件
    this.canvas.on('object:moving', (e) => {
      const obj = e.target;

      // 如果是设备，同时移动标签
      if (obj.type === 'device' && obj.label) {
        obj.label.set({
          left: obj.left,
          top: obj.top + obj.height / 2 + 10
        });
      }
    });
  }

  // 触发事件
  _triggerEvent(eventName, data = {}) {
    if (!this.eventListeners[eventName]) return;

    this.eventListeners[eventName].forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`事件监听器错误 (${eventName}):`, error);
      }
    });
  }

  // 获取默认设备名称
  _getDefaultName(deviceType) {
    const nameMap = {
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
      'cloud': '互联网',
      'vpn': 'VPN网关',
      'dns': 'DNS服务器',
      'proxy': '代理服务器',
      'load': '负载均衡'
    };

    return `${nameMap[deviceType] || '设备'}-${Math.floor(Math.random() * 100 + 1)}`;
  }

  // 生成随机IP
  _generateRandomIP() {
    return `192.168.${Math.floor(Math.random() * 254 + 1)}.${Math.floor(Math.random() * 254 + 1)}`;
  }

  // 生成随机MAC
  _generateRandomMAC() {
    const hexDigits = "0123456789ABCDEF";
    let mac = "";
    for (let i = 0; i < 6; i++) {
      mac += hexDigits.charAt(Math.round(Math.random() * 15));
      mac += hexDigits.charAt(Math.round(Math.random() * 15));
      if (i != 5) mac += ":";
    }
    return mac;
  }
}
</script>

<style scoped>
.device-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 15px;
}

.device-item {
  padding: 10px;
  background-color: #2a2a45;
  border: 1px solid #36365a;
  border-radius: 4px;
  text-align: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.device-item:hover {
  background-color: #36365a;
}

.device-icon {
  width: 36px;
  height: 36px;
  margin: 0 auto 5px;
  border-radius: 5px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.device-name {
  font-size: 12px;
  color: #e4e6eb;
}

.form-control {
  width: 100%;
  padding: 8px;
  background-color: #1a1a30;
  border: 1px solid #36365a;
  border-radius: 4px;
  color: #e4e6eb;
  font-size: 14px;
  box-sizing: border-box;
  margin-bottom: 10px;
}

.form-label {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  color: #a8aabc;
}

.topology-container {
  width: 100%;
  height: 720px;
  background-color: #1a1a30;
  border: 1px solid #36365a;
  position: relative;
  border-radius: 5px;
  overflow: hidden;
}

.btn.active {
  @apply bg-primary text-white;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(74, 158, 255, 0.3);
  border-radius: 50%;
  border-top-color: var(--primary);
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>