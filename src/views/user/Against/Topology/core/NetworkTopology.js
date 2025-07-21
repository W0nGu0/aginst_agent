/**
 * 网络拓扑类
 * 负责管理拓扑图的画布、设备和连接
 */
import { fabric } from 'fabric';

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
    this.deviceColors = {
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
    };

    // 连接类型
    this.connectionTypes = {
      'ethernet': { color: '#2196F3', width: 2, dash: null },
      'wireless': { color: '#4CAF50', width: 2, dash: [5, 5] },
      'vpn': { color: '#9C27B0', width: 2, dash: [10, 5] },
      'wan': { color: '#FF9800', width: 3, dash: null }
    };

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

      const iconPath = this._getDeviceIcon(deviceType);

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

        // 触发事件
        this._triggerEvent('deviceCreated', { device: fabricObj, id: deviceId });

        resolve(fabricObj);
      };

      if (iconPath) {
        fabric.Image.fromURL(iconPath, (img) => {
          // 调整尺寸
          const scale = (deviceOptions.size * 0.6) / Math.max(img.width, img.height);
          img.scale(scale);

          // 创建背景矩形
          const rect = new fabric.Rect({
            width: deviceOptions.size,
            height: deviceOptions.size,
            fill: '#FFFFFF',  // 统一使用白色背景
            rx: 12,
            ry: 12,
            stroke: '#E2E8F0',
            strokeWidth: 1,
            originX: 'center',
            originY: 'center'
          });

          // 计算图标在背景中的居中位置
          const imgWidth = img.getScaledWidth();
          const imgHeight = img.getScaledHeight();

          // 设置图标位置为居中
          img.set({
            originX: 'center',
            originY: 'center',
            left: 0,
            top: 0
          });

          // 创建图标组合
          const group = new fabric.Group([rect, img], {
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
  addConnection(source, target, type = 'ethernet', networkInfo = null) {
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

    // 自动确定网络信息（如果未提供）
    if (!networkInfo && (source.deviceType === 'firewall' || target.deviceType === 'firewall')) {
      // 确定哪个是防火墙
      const firewall = source.deviceType === 'firewall' ? source : target;
      const device = source.deviceType === 'firewall' ? target : source;
      
      // 根据设备IP确定网段
      const deviceIP = device.deviceData.ip;
      if (deviceIP) {
        const ipParts = deviceIP.split('.');
        if (ipParts.length === 4) {
          const subnet = `${ipParts[0]}.${ipParts[1]}.${ipParts[2]}.0/24`;
          
          // 确定防火墙在该网段的IP
          let firewallIP = '';
          
          // 根据网段确定防火墙IP
          if (deviceIP.startsWith('192.168.200.')) {
            firewallIP = '192.168.200.254'; // 服务器段
          } else if (deviceIP.startsWith('192.168.100.')) {
            firewallIP = '192.168.100.254'; // 用户段
          } else if (deviceIP.startsWith('192.168.66.')) {
            firewallIP = '192.168.66.254'; // SIEM段
          } else if (deviceIP.startsWith('192.168.110.')) {
            firewallIP = '192.168.110.254'; // VPN段
          } else if (deviceIP.startsWith('192.168.214.')) {
            firewallIP = '192.168.214.254'; // 数据库段
          } else if (deviceIP.startsWith('172.16.100.')) {
            firewallIP = '172.16.100.254'; // DMZ段
          } else if (deviceIP.startsWith('199.203.100.')) {
            firewallIP = '199.203.100.2'; // 互联网段
          }
          
          if (firewallIP) {
            networkInfo = {
              subnet: subnet,
              firewallIP: firewallIP,
              deviceIP: deviceIP
            };
          }
        }
      }
    }

    // 如果有网络信息，添加网络标签
    if (networkInfo) {
      this._addNetworkLabels(line, source, target, networkInfo);
    }

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
      top: device.top + device.height / 2 + 20, // 将标签位置向下移动，避免与图标重叠
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
    // 对于防火墙设备，只显示名称，不显示IP
    if (device.deviceType === 'firewall') {
      // 确保只显示名称部分（不包含IP）
      const firewallName = device.deviceData.name;
      text = firewallName;
    }
    
    if (device.label) {
      device.label.set({
        text: text
      });
    } else {
      this._addLabel(device, text);
    }
  }

  // 添加网络标签到连接线
  _addNetworkLabels(line, source, target, networkInfo) {
    // 计算连接线的中点
    const midX = (source.left + target.left) / 2;
    const midY = (source.top + target.top) / 2;

    // 计算连接线的角度
    const angle = Math.atan2(target.top - source.top, target.left - source.left) * 180 / Math.PI;
    
    // 确定哪个是防火墙
    const isSourceFirewall = source.deviceType === 'firewall';
    const firewall = isSourceFirewall ? source : target;
    const device = isSourceFirewall ? target : source;
    
    // 只有当一端是防火墙时才添加IP标签
    if (firewall.deviceType === 'firewall') {
      // 创建防火墙IP标签（显示在线的中间）
      if (networkInfo.firewallIP) {
        const firewallIPLabel = new fabric.Text(networkInfo.firewallIP, {
          left: midX,
          top: midY - 15,
          fontSize: 11,
          fill: '#ffcc00',
          backgroundColor: 'rgba(0,0,0,0.5)',
          padding: 3,
          originX: 'center',
          originY: 'center',
          angle: angle > 90 || angle < -90 ? angle + 180 : angle // 根据连接线角度调整标签角度
        });
        
        this.canvas.add(firewallIPLabel);
        line.firewallIPLabel = firewallIPLabel;
        firewallIPLabel.moveTo(this.canvas.getObjects().indexOf(line) + 1);
      }
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

    const source = connection.source;
    const target = connection.target;

    connection.set({
      x1: source.left,
      y1: source.top,
      x2: target.left,
      y2: target.top
    });

    connection.setCoords();

    // 更新网络标签位置
    this._updateNetworkLabels(connection, source, target);

    this.canvas.requestRenderAll();
  }

  // 更新网络标签位置
  _updateNetworkLabels(connection, source, target) {
    // 计算连接线的中点
    const midX = (source.left + target.left) / 2;
    const midY = (source.top + target.top) / 2;

    // 计算连接线的角度
    const angle = Math.atan2(target.top - source.top, target.left - source.left) * 180 / Math.PI;

    // 确定哪个是防火墙
    const isSourceFirewall = source.deviceType === 'firewall';

    // 更新防火墙IP标签 - 始终显示在连接线的中间
    if (connection.firewallIPLabel) {
      connection.firewallIPLabel.set({
        left: midX,
        top: midY - 15,
        angle: angle > 90 || angle < -90 ? angle + 180 : angle // 根据连接线角度调整标签角度
      });
      connection.firewallIPLabel.setCoords();
    }
  }

  // 设置事件
  _setupEvents() {
    if (!this.canvas) return;

    // 选择事件
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
      this._triggerEvent('objectDeselected');
    });

    // 鼠标事件
    this.canvas.on('mouse:down', (e) => {
      if (this.mode === 'connect' && e.target && e.target.type === 'device') {
        if (!this.connecting) {
          // 开始连接
          this.connecting = e.target;
        } else if (this.connecting !== e.target) {
          // 完成连接
          this.addConnection(this.connecting, e.target);
          this.connecting = null;
        }
      }
    });

    // 标签移动事件
    this.canvas.on('object:moving', (e) => {
      const obj = e.target;

      // 如果是设备，同时移动标签
      if (obj.type === 'device' && obj.label) {
        obj.label.set({
          left: obj.left,
          top: obj.top + obj.height / 2 + 20  // 增加距离，避免与图标重叠
        });
        obj.label.setCoords(); // 确保标签坐标更新
        
        // 更新与该设备相关的所有连接线及其标签
        this.connections.forEach(conn => {
          if (conn.source === obj || conn.target === obj) {
            this._updateConnection(conn);
          }
        });
      }
    });
  }

  // 触发事件
  _triggerEvent(eventName, data = {}) {
    if (this.eventListeners[eventName]) {
      this.eventListeners[eventName].forEach(callback => {
        callback(data);
      });
    }
  }

  // 获取设备图标
  _getDeviceIcon(type) {
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
    };

    return iconMap[type] || '';
  }

  // 获取设备类型名称
  _getDeviceTypeName(type) {
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
    };

    return typeMap[type] || type;
  }

  // 生成默认设备名称
  _getDefaultName(type) {
    const typeName = this._getDeviceTypeName(type);
    const count = Object.values(this.devices).filter(d => d.deviceType === type).length + 1;
    return `${typeName}-${count}`;
  }

  // 生成随机IP
  _generateRandomIP() {
    const segments = [];
    for (let i = 0; i < 4; i++) {
      segments.push(Math.floor(Math.random() * 254) + 1);
    }
    return segments.join('.');
  }

  // 生成随机MAC
  _generateRandomMAC() {
    const hexDigits = '0123456789ABCDEF';
    let mac = '';
    for (let i = 0; i < 6; i++) {
      let segment = '';
      for (let j = 0; j < 2; j++) {
        segment += hexDigits.charAt(Math.floor(Math.random() * 16));
      }
      mac += (i === 0 ? '' : ':') + segment;
    }
    return mac;
  }
}

export default NetworkTopology;