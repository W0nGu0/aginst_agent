<template>
  <div class="topology-view">
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- 左侧控制面板 -->
      <div class="lg:col-span-1">
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
        
        <div class="bg-base-100 rounded-lg p-4 border border-base-300/30 mb-6">
          <h2 class="text-xl font-semibold mb-4 flex items-center">
            <span class="text-primary mr-2">#</span>工具栏
          </h2>
          
          <div class="toolbar flex flex-wrap gap-2 mb-4">
            <button 
              @click="setMode('select')"
              :class="{'active': topologyStore.mode === 'select'}"
              class="btn btn-sm">
              选择
            </button>
            <button 
              @click="setMode('connect')"
              :class="{'active': topologyStore.mode === 'connect'}"
              class="btn btn-sm">
              连接
            </button>
            <button 
              @click="setMode('pan')"
              :class="{'active': topologyStore.mode === 'pan'}"
              class="btn btn-sm">
              平移
            </button>
            <button 
              @click="deleteSelected"
              class="btn btn-sm btn-error">
              删除
            </button>
          </div>
          
          <div class="toolbar flex flex-wrap gap-2">
            <button 
              @click="zoomIn"
              class="btn btn-sm">
              放大
            </button>
            <button 
              @click="zoomOut"
              class="btn btn-sm">
              缩小
            </button>
            <button 
              @click="resetView"
              class="btn btn-sm">
              重置视图
            </button>
          </div>
        </div>
        
        <div class="bg-base-100 rounded-lg p-4 border border-base-300/30">
          <h2 class="text-xl font-semibold mb-4 flex items-center">
            <span class="text-primary mr-2">#</span>属性设置
          </h2>
          
          <div v-if="selectedDevice">
            <div class="form-group">
              <label class="form-label">设备名称</label>
              <input 
                type="text" 
                v-model="selectedDevice.deviceData.name"
                @change="updateDeviceProperty"
                class="form-control" />
            </div>
            <div class="form-group">
              <label class="form-label">IP地址</label>
              <input 
                type="text" 
                v-model="selectedDevice.deviceData.ip"
                @change="updateDeviceProperty"
                class="form-control" />
            </div>
            <div class="form-group">
              <label class="form-label">MAC地址</label>
              <input 
                type="text" 
                v-model="selectedDevice.deviceData.mac"
                @change="updateDeviceProperty"
                class="form-control" />
            </div>
            <div class="form-group">
              <label class="form-label">描述</label>
              <textarea 
                v-model="selectedDevice.deviceData.description"
                @change="updateDeviceProperty"
                class="form-control h-24"></textarea>
            </div>
          </div>
          
          <div v-else-if="selectedConnection">
            <div class="form-group">
              <label class="form-label">连接类型</label>
              <select 
                v-model="selectedConnection.connectionType"
                @change="updateConnectionType"
                class="form-control">
                <option value="ethernet">以太网</option>
                <option value="fiber">光纤</option>
                <option value="wireless">无线</option>
              </select>
            </div>
          </div>
          
          <div v-else>
            <p class="text-base-content/50 text-center py-4">
              请选择设备或连接线以编辑属性
            </p>
          </div>
        </div>
      </div>
      
      <!-- 右侧拓扑图区域 -->
      <div class="lg:col-span-3">
        <div class="bg-base-100 rounded-lg p-4 border border-base-300/30">
          <h2 class="text-xl font-semibold mb-4 flex items-center justify-between">
            <div>
              <span class="text-primary mr-2">#</span>网络拓扑图
            </div>
            <button 
              @click="saveTopology"
              class="btn btn-sm btn-primary">
              保存拓扑图
            </button>
          </h2>
          
          <div class="topology-container relative">
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useTopologyStore } from '../stores/topology'

const topologyStore = useTopologyStore()
let topology = null
let fabricLoaded = false

// 设备类型及其颜色
const deviceTypes = {
  'router': '#4CAF50',
  'firewall': '#F44336',
  'switch': '#2196F3',
  'server': '#FF9800',
  'pc': '#9C27B0',
  'ids': '#673AB7'
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
  if (typeof fabric !== 'undefined') {
    console.log('Fabric.js已加载')
    fabricLoaded = true
    return
  }
  
  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js'
    script.async = true
    script.onload = () => {
      console.log('Fabric.js加载成功')
      fabricLoaded = true
      resolve()
    }
    script.onerror = reject
    document.head.appendChild(script)
  })
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

// 保存拓扑图
function saveTopology() {
  if (!topology) return
  
  // TODO: 实现保存功能
  console.log('保存拓扑图')
}

// 获取设备图标
function getDeviceIcon(type) {
  const iconMap = {
    'router': '/public/图标/路由器.svg',
    'firewall': '/public/图标/防火墙.svg',
    'switch': '/public/图标/交换机.svg',
    'server': '/public/图标/服务器.svg',
    'pc': '/public/图标/PC.svg',
    'ids': '/public/图标/入侵检测系统(IDS).svg'
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
    'pc': '计算机',
    'ids': '入侵检测'
  }
  
  return typeMap[type] || type
}

// 网络拓扑图类
class NetworkTopology {
  constructor(options = {}) {
    this.options = Object.assign({
      canvasId: 'network-topology',
      width: 800,
      height: 500,
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
        this.canvas.forEachObject(function(obj) {
          obj.selectable = false;
        });
      } else {
        this.canvas.selection = true;
        this.canvas.forEachObject(function(obj) {
          obj.selectable = true;
        });
      }
      
      // 触发模式改变事件
      this._triggerEvent('modeChange', { mode });
      return true;
    }
    return false;
  }
  
  // 创建设备
  createDevice(type, options = {}) {
    const deviceType = type || 'server';
    const color = this.deviceColors[deviceType] || '#999999';
    
    const defaults = {
      left: 100 + Math.random() * 400,
      top: 100 + Math.random() * 200,
      width: 80,
      height: 80,
      name: this._getDefaultName(deviceType),
      ip: this._generateRandomIP()
    };
    
    const deviceOptions = Object.assign({}, defaults, options);
    
    // 创建设备形状
    const device = new fabric.Rect({
      left: deviceOptions.left,
      top: deviceOptions.top,
      width: deviceOptions.width,
      height: deviceOptions.height,
      fill: color,
      stroke: '#fff',
      strokeWidth: 2,
      rx: 10,
      ry: 10,
      type: 'device',
      deviceType: deviceType,
      deviceData: {
        name: deviceOptions.name,
        ip: deviceOptions.ip,
        mac: deviceOptions.mac || this._generateRandomMAC(),
        description: deviceOptions.description || ''
      }
    });
    
    // 添加到Canvas
    this.canvas.add(device);
    
    // 添加标签
    this._addLabel(device, device.deviceData.name);
    
    // 为设备创建唯一ID
    const deviceId = `device_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
    this.devices[deviceId] = device;
    device.id = deviceId;
    
    // 添加到状态管理
    topologyStore.addDevice(device, deviceId);
    
    // 触发设备创建事件
    this._triggerEvent('deviceCreated', { device, id: deviceId });
    
    return device;
  }
  
  // 添加连接
  addConnection(source, target, type = 'ethernet') {
    if (!source || !target || source === target) {
      return null;
    }
    
    const connType = this.connectionTypes[type] || this.connectionTypes.ethernet;
    
    // 创建连接线
    const line = new fabric.Line([
      source.left + source.width/2,
      source.top + source.height/2,
      target.left + target.width/2,
      target.top + target.height/2
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
    this.canvas.setViewportTransform([1,0,0,1,0,0]);
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
      left: device.left + device.width / 2,
      top: device.top + device.height + 10,
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
      x1: connection.source.left + connection.source.width / 2,
      y1: connection.source.top + connection.source.height / 2,
      x2: connection.target.left + connection.target.width / 2,
      y2: connection.target.top + connection.target.height / 2
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
          left: obj.left + obj.width / 2,
          top: obj.top + obj.height + 10
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
    const prefixMap = {
      'router': 'R',
      'firewall': 'FW',
      'switch': 'SW',
      'server': 'SRV',
      'pc': 'PC',
      'ids': 'IDS'
    };
    
    const prefix = prefixMap[deviceType] || 'DEV';
    return `${prefix}-${Math.floor(Math.random() * 900 + 100)}`;
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
  height: 500px;
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