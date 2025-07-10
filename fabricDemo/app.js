// 网络拓扑编辑器 - 主应用程序
// 作者: Claude
// 版本: 1.0

// 全局应用状态
const app = {
    // 当前模式: 'select', 'connect', 'pan'
    mode: 'select',
    // 当前选中的设备或连接
    selectedObject: null,
    // 历史记录用于撤销/重做
    history: {
        undoStack: [],
        redoStack: []
    },
    // 项目元数据
    project: {
        name: '未命名项目',
        lastSaved: null,
        modified: false
    },
    // 视图状态
    view: {
        zoom: 1,
        pan: { x: 0, y: 0 }
    },
    // 网络模拟状态
    simulation: {
        active: false,
        results: {}
    }
};

// 等待所有资源加载完成
document.addEventListener('DOMContentLoaded', () => {
    // 初始化各个管理器
    CanvasManager.init();
    DeviceManager.init();
    ConnectionManager.init();
    UIManager.init();
    
    // 设置初始模式
    app.setMode('select');
    
    // 禁用整个应用的文本选择和默认拖动行为
    app.disableDefaultBrowserBehaviors();
    
    console.log('网络拓扑编辑器初始化完成');
});

// 禁用浏览器默认行为
app.disableDefaultBrowserBehaviors = function() {
    // 禁用文本选择
    document.querySelectorAll('.app-container, .canvas-container, .sidebar, .toolbar').forEach(el => {
        el.addEventListener('mousedown', (e) => {
            // 允许输入框中的文本选择
            if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA' && e.target.tagName !== 'SELECT') {
                e.preventDefault();
            }
        });
        
        // 禁用拖动
        el.addEventListener('dragstart', (e) => {
            e.preventDefault();
            return false;
        });
    });
    
    // 禁用上下文菜单（可选）
    document.querySelector('.canvas-container').addEventListener('contextmenu', (e) => {
        e.preventDefault();
        return false;
    });
};

// 应用程序方法
app.setMode = function(mode) {
    // 退出之前的模式
    if (app.mode === 'connect' && mode !== 'connect') {
        ConnectionManager.exitConnectMode();
    }
    
    // 设置新模式
    app.mode = mode;
    
    // 更新UI
    UIManager.updateModeUI(mode);
    
    console.log(`已切换到${mode}模式`);
};

app.selectObject = function(obj) {
    // 取消之前的选择
    if (app.selectedObject) {
        UIManager.deselectObject(app.selectedObject);
    }
    
    // 设置新的选择
    app.selectedObject = obj;
    
    // 更新UI
    if (obj) {
        UIManager.selectObject(obj);
    }
};

app.saveState = function(action) {
    // 保存当前状态用于撤销
    const state = CanvasManager.serializeCanvas();
    app.history.undoStack.push({
        action: action,
        state: state
    });
    
    // 清空重做栈
    app.history.redoStack = [];
    
    // 标记项目为已修改
    app.project.modified = true;
    UIManager.updateProjectStatus();
};

app.undo = function() {
    if (app.history.undoStack.length > 0) {
        // 保存当前状态到重做栈
        const currentState = CanvasManager.serializeCanvas();
        app.history.redoStack.push({
            action: '重做',
            state: currentState
        });
        
        // 恢复上一个状态
        const lastAction = app.history.undoStack.pop();
        CanvasManager.loadFromJSON(lastAction.state);
        
        console.log(`撤销: ${lastAction.action}`);
        UIManager.showToast(`已撤销: ${lastAction.action}`);
    }
};

app.redo = function() {
    if (app.history.redoStack.length > 0) {
        // 保存当前状态到撤销栈
        const currentState = CanvasManager.serializeCanvas();
        app.history.undoStack.push({
            action: '撤销',
            state: currentState
        });
        
        // 恢复下一个状态
        const nextAction = app.history.redoStack.pop();
        CanvasManager.loadFromJSON(nextAction.state);
        
        console.log(`重做: ${nextAction.action}`);
        UIManager.showToast(`已重做: ${nextAction.action}`);
    }
};

app.newProject = function() {
    if (app.project.modified) {
        if (confirm('当前项目未保存，是否继续？')) {
            CanvasManager.clearCanvas();
            app.resetProjectState();
        }
    } else {
        CanvasManager.clearCanvas();
        app.resetProjectState();
    }
};

app.resetProjectState = function() {
    app.project = {
        name: '未命名项目',
        lastSaved: null,
        modified: false
    };
    app.history.undoStack = [];
    app.history.redoStack = [];
    UIManager.updateProjectStatus();
};

app.saveProject = function() {
    const projectData = {
        name: app.project.name,
        canvas: CanvasManager.serializeCanvas(),
        timestamp: new Date().toISOString()
    };
    
    const jsonData = JSON.stringify(projectData);
    const blob = new Blob([jsonData], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `${app.project.name || '网络拓扑'}.json`;
    a.click();
    
    app.project.lastSaved = new Date();
    app.project.modified = false;
    UIManager.updateProjectStatus();
    UIManager.showToast('项目已保存');
};

app.loadProject = function(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const projectData = JSON.parse(e.target.result);
            app.project.name = projectData.name;
            CanvasManager.loadFromJSON(projectData.canvas);
            app.project.lastSaved = new Date();
            app.project.modified = false;
            app.history.undoStack = [];
            app.history.redoStack = [];
            UIManager.updateProjectStatus();
            UIManager.showToast('项目已加载');
        } catch (error) {
            console.error('加载项目失败:', error);
            UIManager.showToast('加载项目失败', 'error');
        }
    };
    reader.readAsText(file);
};

// 导出网络拓扑为图片
app.exportTopologyAsImage = function(format = 'png') {
    // 准备导出选项
    const options = {
        format: format,
        quality: 1,
        multiplier: 2, // 提高导出图像的分辨率
        enableRetinaScaling: true,
        withoutTransform: false,
        withoutShadow: false
    };
    
    // 获取当前时间作为文件名的一部分
    const now = new Date();
    const timestamp = now.getFullYear() + 
                     ('0' + (now.getMonth() + 1)).slice(-2) + 
                     ('0' + now.getDate()).slice(-2) + '_' +
                     ('0' + now.getHours()).slice(-2) + 
                     ('0' + now.getMinutes()).slice(-2);
    
    // 生成文件名
    const filename = `${app.project.name || '网络拓扑'}_${timestamp}.${format}`;
    
    try {
        // 导出画布为数据URL
        const dataURL = CanvasManager.canvas.toDataURL(options);
        
        // 创建下载链接
        const link = document.createElement('a');
        link.download = filename;
        link.href = dataURL;
        
        // 触发下载
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        UIManager.showToast(`已导出为 ${format.toUpperCase()} 图像`, 'success');
    } catch (error) {
        console.error('导出图像失败:', error);
        UIManager.showToast('导出图像失败', 'error');
    }
};

// 导出网络拓扑为SVG
app.exportTopologyAsSVG = function() {
    try {
        // 获取SVG数据
        const svgData = CanvasManager.canvas.toSVG();
        
        // 创建Blob对象
        const blob = new Blob([svgData], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        
        // 获取当前时间作为文件名的一部分
        const now = new Date();
        const timestamp = now.getFullYear() + 
                         ('0' + (now.getMonth() + 1)).slice(-2) + 
                         ('0' + now.getDate()).slice(-2) + '_' +
                         ('0' + now.getHours()).slice(-2) + 
                         ('0' + now.getMinutes()).slice(-2);
        
        // 生成文件名
        const filename = `${app.project.name || '网络拓扑'}_${timestamp}.svg`;
        
        // 创建下载链接
        const link = document.createElement('a');
        link.download = filename;
        link.href = url;
        
        // 触发下载
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // 释放URL对象
        URL.revokeObjectURL(url);
        
        UIManager.showToast('已导出为SVG图像', 'success');
    } catch (error) {
        console.error('导出SVG失败:', error);
        UIManager.showToast('导出SVG失败', 'error');
    }
};

// Initialize the canvas
const canvas = new fabric.Canvas('c');

// Device creation functions
function addDevice(deviceType, options) {
    let device;
    const defaultOptions = {
        left: 100,
        top: 100,
        fill: 'white',
        stroke: 'black',
        strokeWidth: 2,
        originX: 'center',
        originY: 'center'
    };
    const finalOptions = Object.assign({}, defaultOptions, options);

    let label = new fabric.Text(deviceType, {
        fontSize: 14,
        originX: 'center',
        originY: 'center',
        top: finalOptions.top + 35
    });

    if (deviceType === 'Router') {
        device = new fabric.Circle({
            ...finalOptions,
            radius: 30,
        });
    } else if (deviceType === 'Switch') {
        device = new fabric.Rect({
            ...finalOptions,
            width: 80,
            height: 40,
        });
        label.set({ top: finalOptions.top + 30 });
    } else if (deviceType === 'PC') {
        device = new fabric.Rect({
             ...finalOptions,
            width: 50,
            height: 30,
        });
    }

    const group = new fabric.Group([device, label], {
        left: finalOptions.left,
        top: finalOptions.top,
        // custom properties
        deviceType: deviceType,
        connections: []
    });

    canvas.add(group);
}

// Event Listeners for Toolbar
document.getElementById('add-router').addEventListener('click', () => {
    addDevice('Router', { top: 100, left: 100 });
});

document.getElementById('add-switch').addEventListener('click', () => {
    addDevice('Switch', { top: 200, left: 100 });
});

document.getElementById('add-pc').addEventListener('click', () => {
    addDevice('PC', { top: 300, left: 100 });
});

// Delete selected object
document.getElementById('delete').addEventListener('click', () => {
    const activeObject = canvas.getActiveObject();
    if (activeObject) {
        // also remove connections
        if (activeObject.connections) {
            activeObject.connections.forEach(conn => {
                canvas.remove(conn.line);
                const otherDevice = conn.target;
                otherDevice.connections = otherDevice.connections.filter(c => c.target !== activeObject);
            });
        }
        canvas.remove(activeObject);
    }
});

// Connection Logic
let connectMode = false;
let lineStartingPoint = null;
const connectModeBtn = document.getElementById('connect-mode');

connectModeBtn.addEventListener('click', () => {
    connectMode = !connectMode;
    if (connectMode) {
        connectModeBtn.textContent = '退出连接模式';
        connectModeBtn.style.backgroundColor = 'lightblue';
        canvas.selection = false; // Disable group selection
        canvas.forEachObject(obj => {
            obj.selectable = false;
        });
    } else {
        connectModeBtn.textContent = '连接模式';
        connectModeBtn.style.backgroundColor = '';
        canvas.selection = true;
        canvas.forEachObject(obj => {
            obj.selectable = true;
        });
        if (lineStartingPoint) {
            // Reset visual feedback if we exit mode mid-connection
            lineStartingPoint.item(0).set({ stroke: 'black' });
            lineStartingPoint = null;
            canvas.renderAll();
        }
    }
});

canvas.on('object:moving', (e) => {
    const device = e.target;
    if (device && device.connections) {
        const center = device.getCenterPoint();
        device.connections.forEach(conn => {
            const line = conn.line;
            if (line.device1 === device) {
                line.set({ x1: center.x, y1: center.y });
            } else if (line.device2 === device) {
                line.set({ x2: center.x, y2: center.y });
            }
        });
        canvas.renderAll();
    }
});

canvas.on('mouse:down', (options) => {
    if (connectMode && options.target && options.target.deviceType) {
        const device = options.target;
        if (lineStartingPoint === null) {
            // First device selected
            lineStartingPoint = device;
            device.item(0).set({ stroke: 'red' }); // Visual feedback
            canvas.renderAll();
        } else {
            // Second device selected
            if (lineStartingPoint !== device) {
                const start = lineStartingPoint;
                const end = device;

                const line = new fabric.Line(
                    [start.getCenterPoint().x, start.getCenterPoint().y, end.getCenterPoint().x, end.getCenterPoint().y],
                    {
                        stroke: 'black',
                        strokeWidth: 2,
                        selectable: false,
                        evented: false,
                        // custom properties
                        device1: start,
                        device2: end
                    }
                );
                canvas.add(line);
                line.sendToBack();

                // Store connection info on devices
                start.connections.push({ line: line, target: end });
                end.connections.push({ line: line, target: start });

                // Reset for next connection
                start.item(0).set({ stroke: 'black' });
                lineStartingPoint = null;
                canvas.renderAll();
            } else {
                // Clicked the same device twice, cancel
                lineStartingPoint.item(0).set({ stroke: 'black' });
                lineStartingPoint = null;
                canvas.renderAll();
            }
        }
    } else if (connectMode) {
        // Clicked on canvas background, cancel
        if (lineStartingPoint) {
            lineStartingPoint.item(0).set({ stroke: 'black' });
            lineStartingPoint = null;
            canvas.renderAll();
        }
    }
});

// 网络模拟功能
app.startNetworkSimulation = function() {
    if (app.simulation.active) {
        UIManager.showToast('模拟已经在运行中', 'warning');
        return;
    }
    
    // 重置之前的模拟结果
    app.simulation.results = {};
    app.simulation.active = true;
    
    // 获取所有设备
    const devices = CanvasManager.canvas.getObjects().filter(obj => obj.type === 'device');
    
    // 检查设备IP地址配置
    let hasInvalidConfig = false;
    devices.forEach(device => {
        // 验证IP地址
        if (device.deviceData.ipAddress) {
            const isValid = app.validateIPAddress(device.deviceData.ipAddress);
            if (!isValid) {
                UIManager.showToast(`设备 ${device.deviceData.name} 的IP地址无效`, 'error');
                hasInvalidConfig = true;
            }
        }
    });
    
    if (hasInvalidConfig) {
        app.simulation.active = false;
        return;
    }
    
    // 显示模拟开始提示
    UIManager.showToast('网络模拟开始运行', 'info');
    UIManager.updateSimulationUI(true);
    
    // 模拟网络连通性
    app.simulateNetworkConnectivity(devices);
};

app.stopNetworkSimulation = function() {
    if (!app.simulation.active) {
        return;
    }
    
    app.simulation.active = false;
    UIManager.showToast('网络模拟已停止', 'info');
    UIManager.updateSimulationUI(false);
    
    // 清除模拟结果显示
    app.clearSimulationResults();
};

app.validateIPAddress = function(ipAddress) {
    // 简单的IPv4地址验证
    const ipv4Pattern = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipv4Pattern.test(ipAddress);
};

app.simulateNetworkConnectivity = function(devices) {
    // 创建网络图
    const networkGraph = {};
    
    // 初始化图
    devices.forEach(device => {
        networkGraph[device.deviceData.id] = {
            device: device,
            connections: []
        };
    });
    
    // 添加连接
    devices.forEach(device => {
        if (device.connections) {
            device.connections.forEach(conn => {
                networkGraph[device.deviceData.id].connections.push(conn.target.deviceData.id);
            });
        }
    });
    
    // 为每个设备执行连通性测试
    devices.forEach(sourceDevice => {
        // 只对有IP地址的设备进行测试
        if (!sourceDevice.deviceData.ipAddress) return;
        
        const sourceId = sourceDevice.deviceData.id;
        app.simulation.results[sourceId] = {};
        
        devices.forEach(targetDevice => {
            // 跳过自身和没有IP地址的设备
            if (sourceDevice === targetDevice || !targetDevice.deviceData.ipAddress) return;
            
            const targetId = targetDevice.deviceData.id;
            
            // 检查两个设备之间是否有路径
            const hasPath = app.findPath(networkGraph, sourceId, targetId);
            app.simulation.results[sourceId][targetId] = hasPath;
            
            // 更新连接线状态
            if (hasPath) {
                app.highlightConnectedDevices(sourceDevice, targetDevice);
            }
        });
    });
    
    // 显示模拟结果
    app.displaySimulationResults();
};

app.findPath = function(graph, start, end, visited = {}) {
    // 如果起点和终点相同
    if (start === end) return true;
    
    // 标记当前节点为已访问
    visited[start] = true;
    
    // 遍历所有相邻节点
    for (const neighbor of graph[start].connections) {
        // 如果邻居节点未访问过
        if (!visited[neighbor]) {
            // 递归检查是否有路径
            if (app.findPath(graph, neighbor, end, visited)) {
                return true;
            }
        }
    }
    
    return false;
};

app.highlightConnectedDevices = function(sourceDevice, targetDevice) {
    // 在实际实现中，可以高亮显示连通的设备或连接线
    // 这里只是一个示例，可以根据需要扩展
    console.log(`设备 ${sourceDevice.deviceData.name} 可以连接到 ${targetDevice.deviceData.name}`);
};

app.displaySimulationResults = function() {
    // 创建结果面板
    const resultsPanel = document.createElement('div');
    resultsPanel.className = 'simulation-results';
    resultsPanel.innerHTML = '<h4>网络连通性测试结果</h4>';
    
    // 创建结果表格
    const table = document.createElement('table');
    table.className = 'results-table';
    
    // 获取所有有IP地址的设备
    const devices = CanvasManager.canvas.getObjects()
        .filter(obj => obj.type === 'device' && obj.deviceData.ipAddress);
    
    // 创建表头
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    headerRow.innerHTML = '<th>源设备</th><th>目标设备</th><th>状态</th>';
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // 创建表体
    const tbody = document.createElement('tbody');
    
    // 填充结果
    for (const sourceId in app.simulation.results) {
        const sourceDevice = DeviceManager.findDeviceById(sourceId);
        
        for (const targetId in app.simulation.results[sourceId]) {
            const targetDevice = DeviceManager.findDeviceById(targetId);
            const isConnected = app.simulation.results[sourceId][targetId];
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${sourceDevice.deviceData.name} (${sourceDevice.deviceData.ipAddress})</td>
                <td>${targetDevice.deviceData.name} (${targetDevice.deviceData.ipAddress})</td>
                <td class="${isConnected ? 'connected' : 'disconnected'}">${isConnected ? '连通' : '不通'}</td>
            `;
            
            tbody.appendChild(row);
        }
    }
    
    table.appendChild(tbody);
    resultsPanel.appendChild(table);
    
    // 添加到属性面板
    const propertiesPanel = document.querySelector('.properties-panel');
    
    // 清除之前的结果
    const oldResults = propertiesPanel.querySelector('.simulation-results');
    if (oldResults) {
        propertiesPanel.removeChild(oldResults);
    }
    
    propertiesPanel.appendChild(resultsPanel);
};

app.clearSimulationResults = function() {
    // 清除结果显示
    const propertiesPanel = document.querySelector('.properties-panel');
    const resultsPanel = propertiesPanel.querySelector('.simulation-results');
    
    if (resultsPanel) {
        propertiesPanel.removeChild(resultsPanel);
    }
    
    // 重置模拟状态
    app.simulation.results = {};
}; 