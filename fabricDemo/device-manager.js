// 网络拓扑编辑器 - 设备管理器
// 负责设备创建、管理和配置

const DeviceManager = {
    // 设备计数器（用于生成唯一ID）
    deviceCounter: 0,
    
    // 设备图标配置
    deviceIcons: {
        'router': { icon: 'bi-router-fill', color: '#4CAF50', shape: 'circle' },
        'firewall': { icon: 'bi-shield-fill-check', color: '#F44336', shape: 'hexagon' },
        'switch': { icon: 'bi-ethernet', color: '#2196F3', shape: 'rectangle' },
        'hub': { icon: 'bi-hdd-network-fill', color: '#607D8B', shape: 'rectangle' },
        'pc': { icon: 'bi-pc-display', color: '#9C27B0', shape: 'rounded-rect' },
        'server': { icon: 'bi-server', color: '#FF9800', shape: 'rectangle-tall' },
        'laptop': { icon: 'bi-laptop', color: '#3F51B5', shape: 'rounded-rect' },
        'wireless-router': { icon: 'bi-wifi', color: '#00BCD4', shape: 'circle' },
        'access-point': { icon: 'bi-broadcast-pin', color: '#009688', shape: 'diamond' },
        'cloud': { icon: 'bi-cloud-fill', color: '#03A9F4', shape: 'cloud' }
    },
    
    // 端口配置
    portConfigs: {
        'router': { portCount: 8, portSpacing: 15 },
        'firewall': { portCount: 6, portSpacing: 15 },
        'switch': { portCount: 24, portSpacing: 8 },
        'hub': { portCount: 12, portSpacing: 10 },
        'pc': { portCount: 1, portSpacing: 0 },
        'server': { portCount: 4, portSpacing: 15 },
        'laptop': { portCount: 1, portSpacing: 0 },
        'wireless-router': { portCount: 5, portSpacing: 15 },
        'access-point': { portCount: 2, portSpacing: 20 },
        'cloud': { portCount: 1, portSpacing: 0 }
    },
    
    // 初始化设备管理器
    init: function() {
        this.setupEventListeners();
        console.log('设备管理器初始化完成');
    },
    
    // 设置事件监听
    setupEventListeners: function() {
        // 为设备面板中的设备项添加拖拽功能
        const deviceItems = document.querySelectorAll('.device-item');
        
        deviceItems.forEach(item => {
            item.addEventListener('mousedown', (e) => {
                const deviceType = item.getAttribute('data-device');
                
                // 创建预览元素
                const preview = document.createElement('div');
                preview.className = 'device-preview';
                preview.innerHTML = `<i class="bi ${this.deviceIcons[deviceType].icon}"></i>`;
                preview.style.position = 'absolute';
                preview.style.left = `${e.pageX}px`;
                preview.style.top = `${e.pageY}px`;
                preview.style.pointerEvents = 'none';
                preview.style.zIndex = '9999';
                preview.style.opacity = '0.7';
                document.body.appendChild(preview);
                
                // 鼠标移动时更新预览位置
                const moveHandler = (moveEvent) => {
                    preview.style.left = `${moveEvent.pageX}px`;
                    preview.style.top = `${moveEvent.pageY}px`;
                };
                
                document.addEventListener('mousemove', moveHandler);
                
                // 鼠标松开时处理放置
                const upHandler = (upEvent) => {
                    document.removeEventListener('mousemove', moveHandler);
                    document.removeEventListener('mouseup', upHandler);
                    document.body.removeChild(preview);
                    
                    // 检查是否放置在画布上
                    const canvasRect = document.querySelector('.canvas-container').getBoundingClientRect();
                    if (
                        upEvent.clientX >= canvasRect.left &&
                        upEvent.clientX <= canvasRect.right &&
                        upEvent.clientY >= canvasRect.top &&
                        upEvent.clientY <= canvasRect.bottom
                    ) {
                        // 计算画布上的位置
                        const canvasPoint = {
                            x: upEvent.clientX - canvasRect.left,
                            y: upEvent.clientY - canvasRect.top
                        };
                        
                        // 创建设备
                        this.createDevice(deviceType, canvasPoint);
                    }
                };
                
                document.addEventListener('mouseup', upHandler);
            });
        });
    },
    
    // 创建设备
    createDevice: function(deviceType, position) {
        // 生成唯一ID
        const deviceId = `device_${++this.deviceCounter}`;
        
        // 获取设备配置
        const iconConfig = this.deviceIcons[deviceType];
        const portConfig = this.portConfigs[deviceType];
        
        // 创建设备数据对象
        const deviceData = {
            id: deviceId,
            type: deviceType,
            name: this.getDefaultName(deviceType),
            ipAddress: '',
            macAddress: this.generateMacAddress(),
            description: '',
            ports: this.generatePorts(portConfig.portCount)
        };
        
        // 创建设备图形
        const device = this.createDeviceObject(deviceType, iconConfig, deviceData);
        
        // 设置位置
        device.left = position.x;
        device.top = position.y;
        
        // 添加到画布
        CanvasManager.addObject(device);
        
        // 保存状态
        app.saveState(`添加${deviceData.name}`);
        
        return device;
    },
    
    // 创建设备图形对象
    createDeviceObject: function(deviceType, iconConfig, deviceData) {
        // 设备尺寸
        const width = 80;
        const height = 80;
        
        // 创建背景形状
        let background;
        const shape = iconConfig.shape || 'circle';
        
        switch(shape) {
            case 'rectangle':
                background = new fabric.Rect({
                    width: width,
                    height: height * 0.6,
                    fill: '#ffffff',
                    stroke: iconConfig.color,
                    strokeWidth: 2,
                    rx: 4,
                    ry: 4,
                    shadow: new fabric.Shadow({
                        color: 'rgba(0,0,0,0.2)',
                        blur: 10,
                        offsetX: 0,
                        offsetY: 5
                    })
                });
                break;
                
            case 'rectangle-tall':
                background = new fabric.Rect({
                    width: width * 0.7,
                    height: height,
                    fill: '#ffffff',
                    stroke: iconConfig.color,
                    strokeWidth: 2,
                    rx: 4,
                    ry: 4,
                    shadow: new fabric.Shadow({
                        color: 'rgba(0,0,0,0.2)',
                        blur: 10,
                        offsetX: 0,
                        offsetY: 5
                    })
                });
                break;
                
            case 'rounded-rect':
                background = new fabric.Rect({
                    width: width,
                    height: height * 0.6,
                    fill: '#ffffff',
                    stroke: iconConfig.color,
                    strokeWidth: 2,
                    rx: 15,
                    ry: 15,
                    shadow: new fabric.Shadow({
                        color: 'rgba(0,0,0,0.2)',
                        blur: 10,
                        offsetX: 0,
                        offsetY: 5
                    })
                });
                break;
                
            case 'hexagon':
                const hexPoints = [
                    {x: -width/2 + width*0.15, y: -height/3},
                    {x: width/2 - width*0.15, y: -height/3},
                    {x: width/2, y: 0},
                    {x: width/2 - width*0.15, y: height/3},
                    {x: -width/2 + width*0.15, y: height/3},
                    {x: -width/2, y: 0}
                ];
                background = new fabric.Polygon(hexPoints, {
                    fill: '#ffffff',
                    stroke: iconConfig.color,
                    strokeWidth: 2,
                    shadow: new fabric.Shadow({
                        color: 'rgba(0,0,0,0.2)',
                        blur: 10,
                        offsetX: 0,
                        offsetY: 5
                    })
                });
                break;
                
            case 'diamond':
                const diamondPoints = [
                    {x: 0, y: -height/3},
                    {x: width/3, y: 0},
                    {x: 0, y: height/3},
                    {x: -width/3, y: 0}
                ];
                background = new fabric.Polygon(diamondPoints, {
                    fill: '#ffffff',
                    stroke: iconConfig.color,
                    strokeWidth: 2,
                    shadow: new fabric.Shadow({
                        color: 'rgba(0,0,0,0.2)',
                        blur: 10,
                        offsetX: 0,
                        offsetY: 5
                    })
                });
                break;
                
            case 'cloud':
                // 创建云形状的路径
                const cloudPath = 'M25,60 Q10,60 10,50 Q0,50 0,40 Q0,25 15,25 Q15,10 30,10 Q50,10 55,30 Q70,25 75,40 Q85,40 85,50 Q85,60 70,60 Z';
                background = new fabric.Path(cloudPath, {
                    fill: '#ffffff',
                    stroke: iconConfig.color,
                    strokeWidth: 2,
                    scaleX: 0.9,
                    scaleY: 0.9,
                    shadow: new fabric.Shadow({
                        color: 'rgba(0,0,0,0.2)',
                        blur: 10,
                        offsetX: 0,
                        offsetY: 5
                    })
                });
                break;
                
            case 'circle':
            default:
                background = new fabric.Circle({
                    radius: width / 2,
                    fill: '#ffffff',
                    stroke: iconConfig.color,
                    strokeWidth: 2,
                    shadow: new fabric.Shadow({
                        color: 'rgba(0,0,0,0.2)',
                        blur: 10,
                        offsetX: 0,
                        offsetY: 5
                    })
                });
        }
        
        // 创建图标背景（轻微的渐变效果）
        const iconBackground = new fabric.Circle({
            radius: 20,
            fill: iconConfig.color,
            opacity: 0.1,
            originX: 'center',
            originY: 'center',
            left: 0,
            top: -5
        });
        
        // 创建图标
        const iconText = new fabric.Text(String.fromCharCode(parseInt(iconConfig.icon.split('-')[1], 16)), {
            fontFamily: 'bootstrap-icons',
            fontSize: 30,
            fill: iconConfig.color,
            originX: 'center',
            originY: 'center',
            left: 0,
            top: -5
        });
        
        // 创建标签背景
        const labelBackground = new fabric.Rect({
            width: width + 20,
            height: 24,
            fill: 'rgba(255,255,255,0.8)',
            stroke: iconConfig.color,
            strokeWidth: 1,
            originX: 'center',
            originY: 'center',
            left: 0,
            top: 30,
            rx: 4,
            ry: 4
        });
        
        // 创建标签
        const label = new fabric.Text(deviceData.name, {
            fontSize: 14,
            fontWeight: 'bold',
            originX: 'center',
            originY: 'center',
            left: 0,
            top: 30,
            fill: '#333333'
        });
        
        // 组合所有元素
        const elements = [background, iconBackground, iconText, labelBackground, label];
        const group = new fabric.Group(elements, {
            width: width,
            height: height,
            originX: 'center',
            originY: 'center',
            selectable: true,
            hasControls: false,
            hasBorders: true,
            lockRotation: true,
            hoverCursor: 'move'
        });
        
        // 添加自定义属性
        group.set({
            type: 'device',
            deviceType: deviceType,
            deviceData: deviceData,
            connections: []
        });
        
        return group;
    },
    
    // 生成端口数据
    generatePorts: function(count) {
        const ports = [];
        for (let i = 0; i < count; i++) {
            ports.push({
                id: `port_${i}`,
                name: `端口 ${i + 1}`
            });
        }
        return ports;
    },
    
    // 获取设备默认名称
    getDefaultName: function(deviceType) {
        const typeNames = {
            'router': '路由器',
            'firewall': '防火墙',
            'switch': '交换机',
            'hub': '集线器',
            'pc': '工作站',
            'server': '服务器',
            'laptop': '笔记本',
            'wireless-router': '无线路由器',
            'access-point': '接入点',
            'cloud': '云'
        };
        
        return `${typeNames[deviceType]} ${this.deviceCounter}`;
    },
    
    // 生成随机MAC地址
    generateMacAddress: function() {
        const hexDigits = "0123456789ABCDEF";
        let macAddress = "";
        
        for (let i = 0; i < 6; i++) {
            let hex1 = hexDigits.charAt(Math.floor(Math.random() * 16));
            let hex2 = hexDigits.charAt(Math.floor(Math.random() * 16));
            macAddress += hex1 + hex2;
            if (i < 5) macAddress += ":";
        }
        
        return macAddress;
    },
    
    // 更新设备属性
    updateDeviceProperties: function(device, properties) {
        // 更新设备数据
        Object.assign(device.deviceData, properties);
        
        // 更新视觉表示
        if (properties.name) {
            // 查找标签对象（通常是组中的第三个对象）
            const label = device._objects[2];
            if (label && label.type === 'text') {
                label.set({ text: properties.name });
            }
        }
        
        // 重新渲染画布
        CanvasManager.canvas.renderAll();
        
        // 保存状态
        app.saveState(`更新${device.deviceData.name}属性`);
    },
    
    // 删除设备
    deleteDevice: function(device) {
        // 首先删除所有连接
        if (device.connections && device.connections.length > 0) {
            // 创建副本，因为我们会在迭代过程中修改数组
            const connections = [...device.connections];
            connections.forEach(conn => {
                ConnectionManager.deleteConnection(conn.line);
            });
        }
        
        // 从画布中移除设备
        CanvasManager.removeObject(device);
        
        // 保存状态
        app.saveState(`删除${device.deviceData.name}`);
    },
    
    // 重建设备引用
    rebuildDeviceReferences: function() {
        const devices = CanvasManager.canvas.getObjects().filter(obj => obj.type === 'device');
        devices.forEach(device => {
            // 确保设备有正确的属性
            if (!device.connections) device.connections = [];
        });
    },
    
    // 查找设备
    findDeviceById: function(id) {
        const devices = CanvasManager.canvas.getObjects().filter(obj => obj.type === 'device');
        return devices.find(device => device.deviceData && device.deviceData.id === id);
    },
    
    // 查找端口
    findPortById: function(device, portId) {
        // 当不需要具体的端口时，此方法可以简化或移除
        return null;
    }
}; 