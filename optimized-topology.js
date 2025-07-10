/**
 * 优化版网络拓扑图模块
 * 使用本地Fabric.js库实现
 */

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
        this.deviceColors = {
            'router': '#4CAF50',
            'firewall': '#F44336',
            'switch': '#2196F3',
            'server': '#FF9800',
            'pc': '#9C27B0',
            'ids': '#673AB7'
        };
        
        // 连接类型
        this.connectionTypes = {
            'ethernet': { color: '#2196F3', width: 2, dash: [] },
            'fiber': { color: '#FF9800', width: 2, dash: [] },
            'wireless': { color: '#4CAF50', width: 2, dash: [3, 3] }
        };
    }
    
    // 初始化拓扑图
    initialize() {
        return new Promise((resolve, reject) => {
            try {
                // 检查Fabric.js是否加载
                if (typeof fabric === 'undefined') {
                    throw new Error('Fabric.js未加载，请确保正确引入Fabric.js库');
                }
                
                // 在Fabric.js 6.x中，版本属性可能有变化
                console.log(`Fabric.js已加载成功`);
                console.log('Fabric对象类型: ', typeof fabric);
                console.log('Fabric.Canvas是否存在: ', typeof fabric.Canvas === 'function');
                
                // 调试 - 检查canvas元素是否存在
                const canvasEl = document.getElementById(this.options.canvasId);
                if (!canvasEl) {
                    throw new Error(`找不到ID为${this.options.canvasId}的canvas元素`);
                }
                console.log(`Canvas元素已找到：#${this.options.canvasId}`);
                
                // 创建Canvas
                this.canvas = new fabric.Canvas(this.options.canvasId, {
                    backgroundColor: this.options.backgroundColor,
                    selection: true,
                    width: this.options.width,
                    height: this.options.height
                });
                
                // 设置事件
                this._setupEvents();
                
                // 隐藏加载动画（如果有）
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
            });
            
            // 从设备集合中移除
            for (let id in this.devices) {
                if (this.devices[id] === obj) {
                    delete this.devices[id];
                    break;
                }
            }
        }
        
        // 如果是连接
        if (obj.type === 'connection') {
            this.connections = this.connections.filter(conn => conn !== obj);
        }
        
        // 从Canvas中移除
        this.canvas.remove(obj);
        this.canvas.discardActiveObject();
        this.canvas.renderAll();
        
        // 触发删除事件
        this._triggerEvent('objectDeleted', { object: obj });
        
        return true;
    }
    
    // 缩放操作
    zoomIn() {
        let zoom = this.canvas.getZoom();
        zoom *= 1.2;
        if (zoom > 5) zoom = 5;
        this.canvas.setZoom(zoom);
        this._triggerEvent('zoom', { level: zoom });
        return zoom;
    }
    
    zoomOut() {
        let zoom = this.canvas.getZoom();
        zoom *= 0.8;
        if (zoom < 0.1) zoom = 0.1;
        this.canvas.setZoom(zoom);
        this._triggerEvent('zoom', { level: zoom });
        return zoom;
    }
    
    resetView() {
        this.canvas.setZoom(1);
        this.canvas.setViewportTransform([1, 0, 0, 1, 0, 0]);
        this._triggerEvent('viewReset');
        return true;
    }
    
    // 创建示例拓扑图
    createSampleTopology() {
        // 创建设备
        const router = this.createDevice('router', { 
            left: 200, top: 150, name: '边界路由器', ip: '192.168.1.1' 
        });
        
        const firewall = this.createDevice('firewall', { 
            left: 400, top: 150, name: '边界防火墙', ip: '192.168.1.254' 
        });
        
        const switchDev = this.createDevice('switch', { 
            left: 600, top: 150, width: 100, height: 60, name: '核心交换机', ip: '10.0.0.1' 
        });
        
        const server = this.createDevice('server', { 
            left: 800, top: 150, width: 60, height: 80, name: 'Web服务器', ip: '10.0.1.10' 
        });
        
        // 创建连接
        this.addConnection(router, firewall);
        this.addConnection(firewall, switchDev);
        this.addConnection(switchDev, server);
        
        this._triggerEvent('sampleCreated');
        return true;
    }
    
    // 添加事件监听
    on(eventName, callback) {
        if (!this._eventHandlers) {
            this._eventHandlers = {};
        }
        
        if (!this._eventHandlers[eventName]) {
            this._eventHandlers[eventName] = [];
        }
        
        this._eventHandlers[eventName].push(callback);
    }
    
    // ===== 私有方法 =====
    
    // 添加标签
    _addLabel(device, text) {
        const label = new fabric.Text(text, {
            left: device.left + device.width/2,
            top: device.top + device.height + 15,
            fontSize: 14,
            fill: '#fff',
            originX: 'center',
            selectable: false
        });
        
        this.canvas.add(label);
        device.label = label;
        
        // 设备移动时更新标签位置
        device.on('moving', () => {
            label.set({
                left: device.left + device.width/2,
                top: device.top + device.height + 15
            });
            this.canvas.renderAll();
        });
    }
    
    // 设置连接事件
    _setupConnectionEvents(connection, source, target) {
        // 当设备移动时更新连接线
        source.on('moving', () => this._updateConnection(connection));
        target.on('moving', () => this._updateConnection(connection));
    }
    
    // 更新连接线
    _updateConnection(connection) {
        if (connection.source && connection.target) {
            connection.set({
                x1: connection.source.left + connection.source.width/2,
                y1: connection.source.top + connection.source.height/2,
                x2: connection.target.left + connection.target.width/2,
                y2: connection.target.top + connection.target.height/2
            });
            this.canvas.renderAll();
        }
    }
    
    // 设置Canvas事件
    _setupEvents() {
        const canvas = this.canvas;
        const self = this;
        
        // 选择对象
        canvas.on('selection:created', (e) => {
            if (self.mode === 'select' && e.selected && e.selected.length > 0) {
                self.selectedObject = e.selected[0];
                self._triggerEvent('selectionChanged', { object: self.selectedObject });
            }
        });
        
        canvas.on('selection:updated', (e) => {
            if (self.mode === 'select' && e.selected && e.selected.length > 0) {
                self.selectedObject = e.selected[0];
                self._triggerEvent('selectionChanged', { object: self.selectedObject });
            }
        });
        
        canvas.on('selection:cleared', () => {
            if (self.mode === 'select') {
                self.selectedObject = null;
                self._triggerEvent('selectionChanged', { object: null });
            }
        });
        
        // 鼠标点击
        canvas.on('mouse:down', (options) => {
            if (self.mode === 'connect' && options.target && options.target.type === 'device') {
                // 连接模式，点击设备时处理
                if (!self.connecting) {
                    // 开始连接
                    self.connecting = options.target;
                    self._triggerEvent('connectionStart', { device: options.target });
                } else {
                    // 完成连接
                    const source = self.connecting;
                    const target = options.target;
                    
                    if (source !== target) {
                        const connection = self.addConnection(source, target);
                        if (connection) {
                            self._triggerEvent('connectionComplete', { connection, source, target });
                        }
                    } else {
                        self._triggerEvent('connectionFailed', { reason: '不能与自身连接' });
                    }
                    
                    // 重置连接状态
                    self.connecting = null;
                }
            } else if (self.mode === 'pan') {
                // 平移模式
                canvas.isDragging = true;
                canvas.lastPosX = options.e.clientX;
                canvas.lastPosY = options.e.clientY;
            }
        });
        
        // 鼠标移动
        canvas.on('mouse:move', (options) => {
            if (self.mode === 'pan' && canvas.isDragging) {
                // 平移画布
                const e = options.e;
                const deltaX = e.clientX - canvas.lastPosX;
                const deltaY = e.clientY - canvas.lastPosY;
                
                canvas.relativePan(new fabric.Point(deltaX, deltaY));
                
                canvas.lastPosX = e.clientX;
                canvas.lastPosY = e.clientY;
            }
        });
        
        // 鼠标释放
        canvas.on('mouse:up', () => {
            canvas.isDragging = false;
        });
        
        // 鼠标滚轮缩放
        canvas.on('mouse:wheel', (opt) => {
            if (opt.e.ctrlKey || opt.e.metaKey) {
                const delta = opt.e.deltaY;
                let zoom = canvas.getZoom();
                zoom *= 0.999 ** delta;
                
                // 限制缩放范围
                if (zoom > 5) zoom = 5;
                if (zoom < 0.1) zoom = 0.1;
                
                // 以鼠标位置为中心进行缩放
                const point = {
                    x: opt.e.offsetX,
                    y: opt.e.offsetY
                };
                
                canvas.zoomToPoint(point, zoom);
                self._triggerEvent('zoom', { level: zoom });
                
                opt.e.preventDefault();
                opt.e.stopPropagation();
            }
        });
    }
    
    // 触发事件
    _triggerEvent(eventName, data = {}) {
        if (!this._eventHandlers || !this._eventHandlers[eventName]) {
            return;
        }
        
        this._eventHandlers[eventName].forEach(handler => {
            try {
                handler(data);
            } catch (e) {
                console.error(`事件处理错误(${eventName}):`, e);
            }
        });
    }
    
    // 获取默认设备名称
    _getDefaultName(deviceType) {
        const prefix = {
            'router': 'Router-',
            'firewall': 'FW-',
            'switch': 'Switch-',
            'server': 'Server-',
            'pc': 'PC-',
            'ids': 'IDS-'
        }[deviceType] || 'Device-';
        
        return prefix + Math.floor(Math.random() * 100);
    }
    
    // 生成随机IP
    _generateRandomIP() {
        return `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`;
    }
    
    // 生成随机MAC地址
    _generateRandomMAC() {
        const hexDigits = '0123456789ABCDEF';
        let mac = '';
        
        for (let i = 0; i < 6; i++) {
            let segment = '';
            for (let j = 0; j < 2; j++) {
                segment += hexDigits.charAt(Math.floor(Math.random() * 16));
            }
            mac += (i > 0 ? ':' : '') + segment;
        }
        
        return mac;
    }
}

// 导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { NetworkTopology };
} else {
    window.NetworkTopology = NetworkTopology;
} 