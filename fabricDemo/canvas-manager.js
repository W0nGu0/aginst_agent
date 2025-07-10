// 网络拓扑编辑器 - 画布管理器
// 负责画布初始化、缩放、平移和序列化等功能

const CanvasManager = {
    // 画布实例
    canvas: null,
    
    // 初始化画布
    init: function() {
        // 创建Fabric.js画布
        this.canvas = new fabric.Canvas('network-canvas', {
            preserveObjectStacking: true,
            selection: true,
            defaultCursor: 'default',
            backgroundColor: '#f8f9fa',
            stopContextMenu: true // 阻止右键菜单
        });
        
        // 调整画布大小以适应容器
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        
        // 设置画布事件监听
        this.setupEventListeners();
        
        console.log('画布管理器初始化完成');
    },
    
    // 调整画布大小
    resizeCanvas: function() {
        const container = document.querySelector('.canvas-container');
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        this.canvas.setWidth(width);
        this.canvas.setHeight(height);
        this.canvas.renderAll();
        
        console.log(`画布大小已调整为 ${width}x${height}`);
    },
    
    // 设置画布事件监听
    setupEventListeners: function() {
        // 选择对象
        this.canvas.on('selection:created', (e) => {
            if (app.mode === 'select') {
                app.selectObject(e.selected[0]);
            }
        });
        
        this.canvas.on('selection:updated', (e) => {
            if (app.mode === 'select') {
                app.selectObject(e.selected[0]);
            }
        });
        
        this.canvas.on('selection:cleared', () => {
            if (app.mode === 'select') {
                app.selectObject(null);
            }
        });
        
        // 移动对象
        this.canvas.on('object:moving', (e) => {
            if (e.target.type === 'device') {
                ConnectionManager.updateConnections(e.target);
            }
        });
        
        // 移动完成后确保连接更新
        this.canvas.on('object:moved', (e) => {
            if (e.target.type === 'device') {
                ConnectionManager.updateConnections(e.target);
                // 强制重新渲染画布
                this.canvas.requestRenderAll();
            }
        });
        
        // 鼠标滚轮缩放
        this.canvas.on('mouse:wheel', (opt) => {
            if (opt.e.ctrlKey || opt.e.metaKey) {
                const delta = opt.e.deltaY;
                let zoom = this.canvas.getZoom();
                zoom *= 0.999 ** delta;
                
                // 限制缩放范围
                if (zoom > 5) zoom = 5;
                if (zoom < 0.1) zoom = 0.1;
                
                // 以鼠标位置为中心进行缩放
                const point = {
                    x: opt.e.offsetX,
                    y: opt.e.offsetY
                };
                
                this.canvas.zoomToPoint(point, zoom);
                
                // 更新状态栏
                app.view.zoom = zoom;
                UIManager.updateStatusBar();
                
                opt.e.preventDefault();
                opt.e.stopPropagation();
            }
        });
        
        // 平移画布
        let isDragging = false;
        let lastPosX, lastPosY;
        
        this.canvas.on('mouse:down', (opt) => {
            // 阻止默认行为，防止文本选择
            opt.e.preventDefault();
            opt.e.stopPropagation();
            
            if (app.mode === 'pan' || opt.e.altKey || opt.e.which === 2) { // 中键按下或Alt+左键
                isDragging = true;
                this.canvas.selection = false;
                lastPosX = opt.e.clientX;
                lastPosY = opt.e.clientY;
                this.canvas.setCursor('grabbing');
                
                // 阻止浏览器默认的拖动行为
                document.body.style.cursor = 'grabbing';
            }
        });
        
        this.canvas.on('mouse:move', (opt) => {
            // 阻止默认行为
            if (isDragging) {
                opt.e.preventDefault();
                opt.e.stopPropagation();
                
                const vpt = this.canvas.viewportTransform;
                vpt[4] += opt.e.clientX - lastPosX;
                vpt[5] += opt.e.clientY - lastPosY;
                this.canvas.requestRenderAll();
                
                lastPosX = opt.e.clientX;
                lastPosY = opt.e.clientY;
                
                // 更新状态栏
                app.view.pan = { x: vpt[4], y: vpt[5] };
                UIManager.updateStatusBar();
            }
            
            // 更新光标位置
            const pointer = this.canvas.getPointer(opt.e);
            UIManager.updateCursorPosition(pointer.x, pointer.y);
        });
        
        this.canvas.on('mouse:up', (opt) => {
            // 阻止默认行为
            opt.e.preventDefault();
            opt.e.stopPropagation();
            
            isDragging = false;
            this.canvas.setCursor('default');
            document.body.style.cursor = 'default';
            this.canvas.selection = app.mode === 'select';
        });
        
        // 禁用浏览器默认的拖动行为
        document.querySelector('.canvas-container').addEventListener('dragstart', (e) => {
            e.preventDefault();
            return false;
        });
        
        // 键盘事件
        document.addEventListener('keydown', (e) => {
            // 空格键：临时切换到平移模式
            if (e.code === 'Space' && !e.repeat && app.mode !== 'connect') {
                this.tempPanMode = app.mode;
                app.setMode('pan');
                this.canvas.setCursor('grab');
                e.preventDefault(); // 阻止空格键的默认行为（滚动页面）
            }
        });
        
        document.addEventListener('keyup', (e) => {
            // 空格键释放：恢复之前的模式
            if (e.code === 'Space' && this.tempPanMode) {
                app.setMode(this.tempPanMode);
                this.tempPanMode = null;
                this.canvas.setCursor('default');
                e.preventDefault();
            }
        });
    },
    
    // 序列化画布为JSON
    serializeCanvas: function() {
        return this.canvas.toJSON(['id', 'deviceType', 'deviceData', 'connectionType', 'sourceDevice', 'targetDevice', 'sourcePort', 'targetPort']);
    },
    
    // 从JSON加载画布
    loadFromJSON: function(json) {
        this.canvas.loadFromJSON(json, () => {
            // 重新建立设备和连接的引用关系
            DeviceManager.rebuildDeviceReferences();
            ConnectionManager.rebuildConnectionReferences();
            
            this.canvas.renderAll();
            console.log('画布已从JSON加载');
        });
    },
    
    // 清空画布
    clearCanvas: function() {
        this.canvas.clear();
        this.canvas.backgroundColor = '#f8f9fa';
        this.canvas.renderAll();
        console.log('画布已清空');
    },
    
    // 适应画布内容
    zoomToFit: function() {
        if (this.canvas.getObjects().length === 0) return;
        
        // 获取所有对象的边界
        const objects = this.canvas.getObjects();
        let minX = Number.MAX_VALUE;
        let minY = Number.MAX_VALUE;
        let maxX = Number.MIN_VALUE;
        let maxY = Number.MIN_VALUE;
        
        objects.forEach(obj => {
            const bounds = obj.getBoundingRect();
            minX = Math.min(minX, bounds.left);
            minY = Math.min(minY, bounds.top);
            maxX = Math.max(maxX, bounds.left + bounds.width);
            maxY = Math.max(maxY, bounds.top + bounds.height);
        });
        
        // 计算缩放比例
        const width = maxX - minX;
        const height = maxY - minY;
        const scaleX = (this.canvas.width - 100) / width;
        const scaleY = (this.canvas.height - 100) / height;
        const scale = Math.min(scaleX, scaleY, 1);
        
        // 计算中心点
        const centerX = (minX + maxX) / 2;
        const centerY = (minY + maxY) / 2;
        
        // 重置视图变换
        this.canvas.setViewportTransform([1, 0, 0, 1, 0, 0]);
        
        // 缩放和平移
        this.canvas.setZoom(scale);
        this.canvas.absolutePan({
            x: centerX * scale - this.canvas.width / 2,
            y: centerY * scale - this.canvas.height / 2
        });
        
        // 更新状态
        app.view.zoom = scale;
        UIManager.updateStatusBar();
    },
    
    // 添加对象到画布
    addObject: function(obj) {
        this.canvas.add(obj);
        this.canvas.renderAll();
    },
    
    // 移除对象
    removeObject: function(obj) {
        this.canvas.remove(obj);
        this.canvas.renderAll();
    },
    
    // 获取画布中心点
    getCenter: function() {
        return {
            x: this.canvas.width / 2,
            y: this.canvas.height / 2
        };
    }
}; 