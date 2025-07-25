/**
 * 基于Fabric.js的攻击可视化类
 * 使用fabric.js原生动画实现攻击效果
 */
import { fabric } from 'fabric';

class FabricAttackVisualization {
  constructor(topology) {
    this.topology = topology;
    this.canvas = topology.canvas;
    this.activeAnimations = [];
    this.attackEffects = [];
    this.continuousAnimations = new Map(); // 存储连续动画
    this.animationQueues = new Map(); // 动画队列

    // 动画配置
    this.config = {
      // 攻击路径动画
      attackPath: {
        duration: 2000,
        color: '#ff4444',
        width: 3,
        dashArray: [10, 5]
      },
      // 扫描动画
      scanning: {
        duration: 1500,
        pulseColor: '#3b82f6',
        pulseRadius: 30,
        continuousInterval: 3000 // 连续扫描间隔
      },
      // 数据包动画
      packet: {
        duration: 1000,
        size: 8,
        color: '#ff6b6b'
      },
      // 节点状态动画
      nodeStatus: {
        duration: 800,
        compromisedColor: '#dc2626',
        targetedColor: '#f59e0b'
      },
      // 网络流量动画
      networkTraffic: {
        interval: 800,
        packetColors: ['#4ade80', '#60a5fa', '#f472b6', '#fbbf24'],
        duration: 1500
      },
      // 加载动画
      loading: {
        rotationSpeed: 1000, // 旋转一圈的时间
        pulseInterval: 2000  // 脉冲间隔
      }
    };
  }

  /**
   * 创建攻击路径动画
   * @param {fabric.Object} source - 源节点
   * @param {fabric.Object} target - 目标节点
   * @param {Object} options - 动画选项
   */
  createAttackPath(source, target, options = {}) {
    const config = { ...this.config.attackPath, ...options };
    
    // 计算路径坐标
    const sourceCenter = source.getCenterPoint();
    const targetCenter = target.getCenterPoint();
    
    // 创建攻击路径线
    const attackLine = new fabric.Line([
      sourceCenter.x, sourceCenter.y,
      sourceCenter.x, sourceCenter.y  // 初始长度为0
    ], {
      stroke: config.color,
      strokeWidth: config.width,
      strokeDashArray: config.dashArray,
      selectable: false,
      evented: false,
      opacity: 0.8
    });
    
    this.canvas.add(attackLine);
    this.attackEffects.push(attackLine);
    
    // 动画扩展到目标
    const animation = attackLine.animate({
      x2: targetCenter.x,
      y2: targetCenter.y,
      opacity: 1
    }, {
      duration: config.duration,
      easing: fabric.util.ease.easeOutCubic,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => {
        // 创建数据包动画
        this.createPacketAnimation(sourceCenter, targetCenter);
        
        // 延迟移除攻击路径
        setTimeout(() => {
          this.removeEffect(attackLine);
        }, 1000);
      }
    });
    
    this.activeAnimations.push(animation);
    return animation;
  }

  /**
   * 创建数据包动画
   * @param {Object} start - 起始坐标 {x, y}
   * @param {Object} end - 结束坐标 {x, y}
   */
  createPacketAnimation(start, end) {
    const config = this.config.packet;
    
    // 创建数据包对象
    const packet = new fabric.Circle({
      left: start.x,
      top: start.y,
      radius: config.size,
      fill: config.color,
      selectable: false,
      evented: false,
      originX: 'center',
      originY: 'center'
    });
    
    this.canvas.add(packet);
    this.attackEffects.push(packet);
    
    // 动画移动到目标
    const animation = packet.animate({
      left: end.x,
      top: end.y
    }, {
      duration: config.duration,
      easing: fabric.util.ease.easeInOutQuad,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => {
        // 创建爆炸效果
        this.createImpactEffect(end);
        this.removeEffect(packet);
      }
    });
    
    this.activeAnimations.push(animation);
  }

  /**
   * 创建扫描脉冲动画
   * @param {fabric.Object} node - 节点对象
   * @param {Object} options - 动画选项
   */
  createScanningPulse(node, options = {}) {
    const config = { ...this.config.scanning, ...options };
    const center = node.getCenterPoint();

    // 创建多层扫描脉冲
    for (let i = 0; i < 3; i++) {
      setTimeout(() => {
        const pulse = new fabric.Circle({
          left: center.x,
          top: center.y,
          radius: 5,
          fill: 'transparent',
          stroke: i === 0 ? config.pulseColor : i === 1 ? '#10b981' : '#f59e0b',
          strokeWidth: 3,
          selectable: false,
          evented: false,
          originX: 'center',
          originY: 'center',
          opacity: 0.8
        });

        this.canvas.add(pulse);
        this.attackEffects.push(pulse);

        // 脉冲扩散动画
        const animation = pulse.animate({
          radius: config.pulseRadius + i * 10,
          opacity: 0
        }, {
          duration: config.duration,
          easing: fabric.util.ease.easeOutQuad,
          onChange: () => this.canvas.renderAll(),
          onComplete: () => this.removeEffect(pulse)
        });

        this.activeAnimations.push(animation);
      }, i * 200);
    }

    // 添加扫描文字提示
    const scanText = new fabric.Text('扫描中...', {
      left: center.x,
      top: center.y - 50,
      fontSize: 12,
      fill: config.pulseColor,
      fontWeight: 'bold',
      textAlign: 'center',
      originX: 'center',
      selectable: false,
      evented: false,
      opacity: 0
    });

    this.canvas.add(scanText);
    this.attackEffects.push(scanText);

    // 文字淡入淡出
    const textAnimation = scanText.animate({ opacity: 1 }, {
      duration: 300,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => {
        setTimeout(() => {
          const fadeOut = scanText.animate({ opacity: 0 }, {
            duration: 300,
            onChange: () => this.canvas.renderAll(),
            onComplete: () => this.removeEffect(scanText)
          });
          this.activeAnimations.push(fadeOut);
        }, 1500);
      }
    });

    this.activeAnimations.push(textAnimation);
  }

  /**
   * 开始连续扫描动画
   * @param {fabric.Object[]} nodes - 要扫描的节点数组
   * @param {string} scanId - 扫描ID，用于停止扫描
   */
  startContinuousScanning(nodes, scanId = 'default') {
    if (!nodes || nodes.length === 0) return;

    let currentIndex = 0;
    const config = this.config.scanning;

    const scanNext = () => {
      if (!this.continuousAnimations.has(scanId)) return; // 检查是否已停止

      const node = nodes[currentIndex];
      this.createScanningPulse(node);

      currentIndex = (currentIndex + 1) % nodes.length;

      // 设置下次扫描
      const timeoutId = setTimeout(scanNext, config.continuousInterval);
      this.continuousAnimations.set(scanId, timeoutId);
    };

    // 开始扫描
    this.continuousAnimations.set(scanId, true);
    scanNext();
  }

  /**
   * 停止连续扫描
   * @param {string} scanId - 扫描ID
   */
  stopContinuousScanning(scanId = 'default') {
    const timeoutId = this.continuousAnimations.get(scanId);
    if (timeoutId && typeof timeoutId === 'number') {
      clearTimeout(timeoutId);
    }
    this.continuousAnimations.delete(scanId);
  }

  /**
   * 创建撞击效果
   * @param {Object} position - 撞击位置 {x, y}
   */
  createImpactEffect(position) {
    // 创建多个扩散圆圈
    for (let i = 0; i < 3; i++) {
      setTimeout(() => {
        const impact = new fabric.Circle({
          left: position.x,
          top: position.y,
          radius: 2,
          fill: 'transparent',
          stroke: '#ff4444',
          strokeWidth: 2,
          selectable: false,
          evented: false,
          originX: 'center',
          originY: 'center',
          opacity: 0.6
        });
        
        this.canvas.add(impact);
        this.attackEffects.push(impact);
        
        const animation = impact.animate({
          radius: 15 + i * 5,
          opacity: 0
        }, {
          duration: 600,
          easing: fabric.util.ease.easeOutQuad,
          onChange: () => this.canvas.renderAll(),
          onComplete: () => this.removeEffect(impact)
        });
        
        this.activeAnimations.push(animation);
      }, i * 100);
    }
  }

  /**
   * 更新节点状态（被攻击/被攻陷）
   * @param {fabric.Object} node - 节点对象
   * @param {string} status - 状态：'targeted', 'compromised', 'normal'
   */
  updateNodeStatus(node, status) {
    const config = this.config.nodeStatus;
    
    // 移除之前的状态效果
    this.removeNodeStatusEffects(node);
    
    switch (status) {
      case 'targeted':
        this.addNodeGlow(node, config.targetedColor);
        break;
      case 'compromised':
        this.addNodeGlow(node, config.compromisedColor);
        this.addNodePulse(node, config.compromisedColor);
        break;
      case 'normal':
        // 恢复正常状态
        break;
    }
  }

  /**
   * 添加节点光晕效果
   * @param {fabric.Object} node - 节点对象
   * @param {string} color - 光晕颜色
   */
  addNodeGlow(node, color) {
    const center = node.getCenterPoint();
    const radius = Math.max(node.width, node.height) / 2 + 10;
    
    const glow = new fabric.Circle({
      left: center.x,
      top: center.y,
      radius: radius,
      fill: 'transparent',
      stroke: color,
      strokeWidth: 3,
      selectable: false,
      evented: false,
      originX: 'center',
      originY: 'center',
      opacity: 0.6
    });
    
    // 标记为节点状态效果
    glow.nodeStatusEffect = true;
    glow.targetNode = node;
    
    this.canvas.add(glow);
    this.attackEffects.push(glow);
  }

  /**
   * 移除效果对象
   * @param {fabric.Object} effect - 效果对象
   */
  removeEffect(effect) {
    if (effect && this.canvas.contains(effect)) {
      this.canvas.remove(effect);
    }
    
    // 从效果数组中移除
    const index = this.attackEffects.indexOf(effect);
    if (index > -1) {
      this.attackEffects.splice(index, 1);
    }
  }

  /**
   * 清除所有攻击效果
   */
  clearAllEffects() {
    // 停止所有动画
    this.activeAnimations.forEach(animation => {
      if (animation && typeof animation.cancel === 'function') {
        animation.cancel();
      }
    });
    this.activeAnimations = [];

    // 停止所有连续动画
    this.continuousAnimations.forEach((value, key) => {
      if (typeof value === 'number') {
        clearTimeout(value);
        clearInterval(value);
      }
    });
    this.continuousAnimations.clear();

    // 清空动画队列
    this.animationQueues.clear();

    // 移除所有效果对象
    this.attackEffects.forEach(effect => {
      if (this.canvas.contains(effect)) {
        this.canvas.remove(effect);
      }
    });
    this.attackEffects = [];

    this.canvas.renderAll();
  }

  /**
   * 创建动画队列，确保动画按顺序执行
   * @param {string} queueId - 队列ID
   * @param {Array} animations - 动画函数数组
   * @param {number} interval - 动画间隔（毫秒）
   */
  createAnimationQueue(queueId, animations, interval = 1000) {
    if (this.animationQueues.has(queueId)) {
      this.stopAnimationQueue(queueId);
    }

    let currentIndex = 0;

    const executeNext = () => {
      if (currentIndex < animations.length && this.animationQueues.has(queueId)) {
        const animation = animations[currentIndex];
        if (typeof animation === 'function') {
          animation();
        }
        currentIndex++;

        if (currentIndex < animations.length) {
          const timeoutId = setTimeout(executeNext, interval);
          this.animationQueues.set(queueId, timeoutId);
        } else {
          // 队列完成，可以选择循环
          if (this.animationQueues.get(queueId + '_loop')) {
            currentIndex = 0;
            const timeoutId = setTimeout(executeNext, interval);
            this.animationQueues.set(queueId, timeoutId);
          } else {
            this.animationQueues.delete(queueId);
          }
        }
      }
    };

    this.animationQueues.set(queueId, true);
    executeNext();
  }

  /**
   * 停止动画队列
   * @param {string} queueId - 队列ID
   */
  stopAnimationQueue(queueId) {
    const timeoutId = this.animationQueues.get(queueId);
    if (timeoutId && typeof timeoutId === 'number') {
      clearTimeout(timeoutId);
    }
    this.animationQueues.delete(queueId);
    this.animationQueues.delete(queueId + '_loop');
  }

  /**
   * 设置动画队列为循环模式
   * @param {string} queueId - 队列ID
   * @param {boolean} loop - 是否循环
   */
  setAnimationQueueLoop(queueId, loop = true) {
    if (loop) {
      this.animationQueues.set(queueId + '_loop', true);
    } else {
      this.animationQueues.delete(queueId + '_loop');
    }
  }

  /**
   * 移除节点状态效果
   * @param {fabric.Object} node - 节点对象
   */
  removeNodeStatusEffects(node) {
    const effectsToRemove = this.attackEffects.filter(effect =>
      effect.nodeStatusEffect && effect.targetNode === node
    );

    effectsToRemove.forEach(effect => this.removeEffect(effect));
  }

  /**
   * 添加节点脉冲效果
   * @param {fabric.Object} node - 节点对象
   * @param {string} color - 脉冲颜色
   */
  addNodePulse(node, color) {
    const center = node.getCenterPoint();
    const baseRadius = Math.max(node.width, node.height) / 2;

    // 创建连续脉冲效果
    const createPulse = () => {
      const pulse = new fabric.Circle({
        left: center.x,
        top: center.y,
        radius: baseRadius,
        fill: 'transparent',
        stroke: color,
        strokeWidth: 2,
        selectable: false,
        evented: false,
        originX: 'center',
        originY: 'center',
        opacity: 0.8
      });

      pulse.nodeStatusEffect = true;
      pulse.targetNode = node;

      this.canvas.add(pulse);
      this.attackEffects.push(pulse);

      const animation = pulse.animate({
        radius: baseRadius + 20,
        opacity: 0
      }, {
        duration: 1000,
        easing: fabric.util.ease.easeOutQuad,
        onChange: () => this.canvas.renderAll(),
        onComplete: () => {
          this.removeEffect(pulse);
          // 继续下一个脉冲
          setTimeout(createPulse, 500);
        }
      });

      this.activeAnimations.push(animation);
    };

    createPulse();
  }

  /**
   * 创建加载动画（节点上方显示加载指示器）
   * @param {fabric.Object} node - 节点对象
   * @param {number} duration - 持续时间（秒）
   */
  createThinkingAnimation(node, duration = 3) {
    const center = node.getCenterPoint();
    const loadingY = center.y - node.height / 2 - 35;

    // 创建加载圆环背景
    const loadingBg = new fabric.Circle({
      left: center.x,
      top: loadingY,
      radius: 18,
      fill: 'transparent',
      stroke: 'rgba(255, 255, 255, 0.3)',
      strokeWidth: 3,
      selectable: false,
      evented: false,
      originX: 'center',
      originY: 'center',
      opacity: 0
    });

    // 创建加载进度圆环
    const loadingProgress = new fabric.Circle({
      left: center.x,
      top: loadingY,
      radius: 18,
      fill: 'transparent',
      stroke: '#4CAF50',
      strokeWidth: 3,
      strokeDashArray: [20, 100],
      selectable: false,
      evented: false,
      originX: 'center',
      originY: 'center',
      opacity: 0,
      angle: 0
    });

    // 创建中心加载图标
    const loadingIcon = new fabric.Text('⚙️', {
      left: center.x,
      top: loadingY,
      fontSize: 16,
      selectable: false,
      evented: false,
      originX: 'center',
      originY: 'center',
      opacity: 0,
      angle: 0
    });

    this.canvas.add(loadingBg);
    this.canvas.add(loadingProgress);
    this.canvas.add(loadingIcon);
    this.attackEffects.push(loadingBg, loadingProgress, loadingIcon);

    // 淡入动画
    const fadeIn = fabric.util.animate({
      startValue: 0,
      endValue: 1,
      duration: 300,
      onChange: (value) => {
        loadingBg.set('opacity', value);
        loadingProgress.set('opacity', value);
        loadingIcon.set('opacity', value);
        this.canvas.renderAll();
      }
    });

    // 旋转动画 - 圆环
    const rotateProgress = () => {
      if (loadingProgress.opacity > 0) {
        const animation = loadingProgress.animate('angle', loadingProgress.angle + 360, {
          duration: 1000,
          easing: fabric.util.ease.easeInOutQuad,
          onChange: () => this.canvas.renderAll(),
          onComplete: rotateProgress
        });
        this.activeAnimations.push(animation);
      }
    };

    // 旋转动画 - 中心图标
    const rotateIcon = () => {
      if (loadingIcon.opacity > 0) {
        const animation = loadingIcon.animate('angle', loadingIcon.angle + 180, {
          duration: 800,
          easing: fabric.util.ease.easeInOutQuad,
          onChange: () => this.canvas.renderAll(),
          onComplete: rotateIcon
        });
        this.activeAnimations.push(animation);
      }
    };

    // 开始旋转
    setTimeout(() => {
      rotateProgress();
      rotateIcon();
    }, 300);

    // 延迟淡出
    setTimeout(() => {
      const fadeOut = fabric.util.animate({
        startValue: 1,
        endValue: 0,
        duration: 500,
        onChange: (value) => {
          loadingBg.set('opacity', value);
          loadingProgress.set('opacity', value);
          loadingIcon.set('opacity', value);
          this.canvas.renderAll();
        },
        onComplete: () => {
          this.removeEffect(loadingBg);
          this.removeEffect(loadingProgress);
          this.removeEffect(loadingIcon);
        }
      });
      this.activeAnimations.push(fadeOut);
    }, duration * 1000);

    this.activeAnimations.push(fadeIn);
  }

  /**
   * 创建加载动画的别名方法
   * @param {fabric.Object} node - 节点对象
   * @param {number} duration - 持续时间（秒）
   */
  createLoadingAnimation(node, duration = 3) {
    return this.createThinkingAnimation(node, duration);
  }

  /**
   * 开始网络流量动画
   * @param {fabric.Object[]} nodes - 网络节点数组
   * @param {string} trafficId - 流量ID
   */
  startNetworkTraffic(nodes, trafficId = 'default') {
    if (!nodes || nodes.length < 2) return;

    const config = this.config.networkTraffic;

    const createTrafficPacket = () => {
      if (!this.continuousAnimations.has(trafficId)) return;

      const source = nodes[Math.floor(Math.random() * nodes.length)];
      const target = nodes[Math.floor(Math.random() * nodes.length)];

      if (source === target) return;

      const sourceCenter = source.getCenterPoint();
      const targetCenter = target.getCenterPoint();

      const packet = new fabric.Circle({
        left: sourceCenter.x,
        top: sourceCenter.y,
        radius: 3,
        fill: config.packetColors[Math.floor(Math.random() * config.packetColors.length)],
        selectable: false,
        evented: false,
        originX: 'center',
        originY: 'center'
      });

      this.canvas.add(packet);
      this.attackEffects.push(packet);

      const animation = packet.animate({
        left: targetCenter.x,
        top: targetCenter.y
      }, {
        duration: config.duration + Math.random() * 500,
        easing: fabric.util.ease.easeInOutQuad,
        onChange: () => this.canvas.renderAll(),
        onComplete: () => this.removeEffect(packet)
      });

      this.activeAnimations.push(animation);
    };

    // 开始流量生成
    const intervalId = setInterval(() => {
      createTrafficPacket();
      if (Math.random() > 0.7) createTrafficPacket(); // 有时创建多个包
    }, config.interval);

    this.continuousAnimations.set(trafficId, intervalId);
  }

  /**
   * 停止网络流量
   * @param {string} trafficId - 流量ID
   */
  stopNetworkTraffic(trafficId = 'default') {
    const intervalId = this.continuousAnimations.get(trafficId);
    if (intervalId) {
      clearInterval(intervalId);
      this.continuousAnimations.delete(trafficId);
    }
  }

  /**
   * 根据日志内容触发对应动画
   * @param {Object} logEntry - 日志条目
   * @param {fabric.Object} sourceNode - 源节点
   * @param {fabric.Object} targetNode - 目标节点
   */
  triggerAnimationFromLog(logEntry, sourceNode, targetNode = null) {
    const { level, source, message } = logEntry;

    // 根据日志内容匹配动画
    if (message.includes('扫描') || message.includes('scan')) {
      this.createScanningPulse(targetNode || sourceNode);
    } else if (message.includes('攻击') || message.includes('attack')) {
      if (targetNode) {
        this.createAttackPath(sourceNode, targetNode);
      }
    } else if (message.includes('加载') || message.includes('分析') || message.includes('处理')) {
      this.createThinkingAnimation(sourceNode, 2);
    } else if (message.includes('数据') || message.includes('窃取') || message.includes('传输')) {
      if (targetNode) {
        this.createDataTheftAnimation(targetNode, sourceNode, 2);
      }
    } else if (message.includes('成功') || message.includes('完成')) {
      this.createSuccessAnimation(sourceNode, 1.5);
    } else if (message.includes('失败') || message.includes('错误')) {
      this.createFailureAnimation(sourceNode);
    } else {
      // 默认显示思考动画
      this.createThinkingAnimation(sourceNode, 1);
    }
  }

  /**
   * 创建失败动画
   * @param {fabric.Object} node - 节点对象
   */
  createFailureAnimation(node) {
    const center = node.getCenterPoint();

    const failureIcon = new fabric.Text('❌', {
      left: center.x,
      top: center.y - 40,
      fontSize: 24,
      selectable: false,
      evented: false,
      originX: 'center',
      originY: 'center',
      opacity: 0
    });

    this.canvas.add(failureIcon);
    this.attackEffects.push(failureIcon);

    // 摇摆动画
    const shake = () => {
      const shakeAnimation = failureIcon.animate({
        left: center.x + (Math.random() - 0.5) * 10
      }, {
        duration: 100,
        onChange: () => this.canvas.renderAll(),
        onComplete: () => {
          failureIcon.animate({
            left: center.x
          }, {
            duration: 100,
            onChange: () => this.canvas.renderAll()
          });
        }
      });
      this.activeAnimations.push(shakeAnimation);
    };

    // 淡入
    const fadeIn = failureIcon.animate({ opacity: 1 }, {
      duration: 200,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => {
        // 摇摆几次
        for (let i = 0; i < 3; i++) {
          setTimeout(shake, i * 200);
        }

        // 延迟淡出
        setTimeout(() => {
          const fadeOut = failureIcon.animate({ opacity: 0 }, {
            duration: 300,
            onChange: () => this.canvas.renderAll(),
            onComplete: () => this.removeEffect(failureIcon)
          });
          this.activeAnimations.push(fadeOut);
        }, 1500);
      }
    });

    this.activeAnimations.push(fadeIn);
  }

  /**
   * 创建数据窃取动画
   * @param {fabric.Object} source - 源节点
   * @param {fabric.Object} target - 目标节点
   * @param {number} duration - 持续时间（秒）
   */
  createDataTheftAnimation(source, target, duration = 3) {
    const sourceCenter = source.getCenterPoint();
    const targetCenter = target.getCenterPoint();

    // 创建多个数据包连续传输
    const createDataPacket = (delay = 0) => {
      setTimeout(() => {
        const dataPacket = new fabric.Rect({
          left: sourceCenter.x,
          top: sourceCenter.y,
          width: 12,
          height: 8,
          fill: '#4ade80',
          selectable: false,
          evented: false,
          originX: 'center',
          originY: 'center'
        });

        this.canvas.add(dataPacket);
        this.attackEffects.push(dataPacket);

        const animation = dataPacket.animate({
          left: targetCenter.x,
          top: targetCenter.y
        }, {
          duration: 800,
          easing: fabric.util.ease.easeInOutQuad,
          onChange: () => this.canvas.renderAll(),
          onComplete: () => this.removeEffect(dataPacket)
        });

        this.activeAnimations.push(animation);
      }, delay);
    };

    // 创建多个数据包
    for (let i = 0; i < Math.floor(duration * 2); i++) {
      createDataPacket(i * 500);
    }
  }

  /**
   * 创建成功动画
   * @param {fabric.Object} node - 节点对象
   * @param {number} duration - 持续时间（秒）
   */
  createSuccessAnimation(node, duration = 2) {
    const center = node.getCenterPoint();

    // 创建成功标志
    const successIcon = new fabric.Text('✅', {
      left: center.x,
      top: center.y - 40,
      fontSize: 30,
      selectable: false,
      evented: false,
      originX: 'center',
      originY: 'center',
      opacity: 0,
      scaleX: 0.5,
      scaleY: 0.5
    });

    this.canvas.add(successIcon);
    this.attackEffects.push(successIcon);

    // 弹出动画
    const popIn = successIcon.animate({
      opacity: 1,
      scaleX: 1.2,
      scaleY: 1.2
    }, {
      duration: 300,
      easing: fabric.util.ease.easeOutBack,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => {
        // 缩回正常大小
        const normalize = successIcon.animate({
          scaleX: 1,
          scaleY: 1
        }, {
          duration: 200,
          easing: fabric.util.ease.easeInOutQuad,
          onChange: () => this.canvas.renderAll()
        });
        this.activeAnimations.push(normalize);
      }
    });

    // 延迟淡出
    setTimeout(() => {
      const fadeOut = successIcon.animate({
        opacity: 0,
        top: center.y - 60
      }, {
        duration: 500,
        easing: fabric.util.ease.easeInQuad,
        onChange: () => this.canvas.renderAll(),
        onComplete: () => this.removeEffect(successIcon)
      });
      this.activeAnimations.push(fadeOut);
    }, duration * 1000);

    this.activeAnimations.push(popIn);
  }

  /**
   * 创建复杂攻击序列
   * @param {fabric.Object} attacker - 攻击者节点
   * @param {fabric.Object[]} targets - 目标节点数组
   * @param {string} attackType - 攻击类型
   */
  createAttackSequence(attacker, targets, attackType = 'auto') {
    let delay = 0;

    targets.forEach((target, index) => {
      setTimeout(() => {
        // 1. 扫描阶段
        this.createScanningPulse(target);

        setTimeout(() => {
          // 2. 攻击路径
          this.createAttackPath(attacker, target);

          setTimeout(() => {
            // 3. 更新目标状态
            this.updateNodeStatus(target, 'compromised');

            // 4. 如果是最后一个目标，显示成功动画
            if (index === targets.length - 1) {
              setTimeout(() => {
                this.createSuccessAnimation(attacker);
              }, 1000);
            }
          }, 2000);
        }, 1500);
      }, delay);

      delay += 3000; // 每个目标间隔3秒
    });
  }
}

export default FabricAttackVisualization;
