/**
 * 增强版攻击可视化类
 * 使用 fabric.js 实现高级动画效果
 */
import { fabric } from 'fabric';

class EnhancedAttackVisualization {
  constructor(topology) {
    this.topology = topology;
    this.canvas = topology.canvas;
    this.animations = [];
    this.attackPaths = [];
    this.particles = [];
  }

  /**
   * 可视化攻击路径
   * @param {Object} attackData - 攻击数据
   * @param {Object} attackData.attacker - 攻击者设备
   * @param {Object} attackData.target - 目标设备
   * @param {string} attackData.attackType - 攻击类型
   * @returns {Promise} - 返回动画完成的Promise
   */
  visualizeAttack(attackData) {
    return new Promise((resolve) => {
      const { attacker, target, attackType } = attackData;
      
      // 清除之前的攻击路径
      this.clearAttackPaths();
      
      // 确定攻击路径（可能需要经过防火墙等中间设备）
      const path = this._findAttackPath(attacker, target);
      
      // 创建攻击路径可视化
      this._createAttackPathVisualization(path, attackType);
      
      // 创建攻击动画
      this._createAttackAnimation(path, attackType);
      
      // 3秒后完成动画
      setTimeout(() => {
        resolve();
      }, 3000);
    });
  }

  /**
   * 可视化钓鱼攻击
   * @param {Object} attackData - 攻击数据
   * @returns {Promise} - 返回动画完成的Promise
   */
  visualizePhishingAttack(attackData) {
    return new Promise((resolve) => {
      const { attacker, target, attackType } = attackData;
      
      // 清除之前的攻击路径
      this.clearAttackPaths();
      
      // 确定攻击路径（可能需要经过防火墙等中间设备）
      const path = this._findAttackPath(attacker, target);
      
      // 创建攻击路径可视化
      this._createAttackPathVisualization(path, attackType);
      
      // 创建钓鱼攻击特定的动画
      this._createPhishingAnimation(path, attackType);
      
      // 5秒后完成动画
      setTimeout(() => {
        resolve();
      }, 5000);
    });
  }

  /**
   * 清除所有攻击路径可视化
   */
  clearAttackPaths() {
    // 移除所有粒子
    this.particles.forEach(particle => {
      this.canvas.remove(particle);
    });
    this.particles = [];
    
    // 移除所有攻击路径
    this.attackPaths.forEach(path => {
      this.canvas.remove(path);
    });
    this.attackPaths = [];
    
    // 重新渲染画布
    this.canvas.requestRenderAll();
  }
  
  /**
   * 绘制攻击路径
   * @param {Array} points - 路径上的点数组，每个点包含 x 和 y 坐标
   * @param {string} color - 路径颜色
   * @param {number} width - 路径宽度
   */
  drawAttackPath(points, color = '#ff0000', width = 2) {
    if (!points || points.length < 2) return;
    
    // 创建路径点数组
    const pathPoints = [];
    
    // 添加所有点
    for (let i = 0; i < points.length; i++) {
      pathPoints.push(points[i].x);
      pathPoints.push(points[i].y);
    }
    
    // 创建路径线
    const line = new fabric.Polyline(pathPoints, {
      stroke: color,
      strokeWidth: width,
      strokeDashArray: [5, 5],
      fill: 'transparent',
      selectable: false,
      evented: false,
      hoverCursor: 'default'
    });
    
    // 添加到画布
    this.canvas.add(line);
    
    // 将线发送到设备后面
    line.sendToBack();
    
    // 保存路径引用
    this.attackPaths.push(line);
    
    // 重新渲染画布
    this.canvas.requestRenderAll();
    
    // 创建沿路径移动的粒子
    this._createPathParticles(points, color);
    
    return line;
  }
  
  /**
   * 创建沿路径移动的粒子
   * @private
   * @param {Array} points - 路径上的点数组
   * @param {string} color - 粒子颜色
   */
  _createPathParticles(points, color) {
    // 创建5个粒子
    for (let i = 0; i < 5; i++) {
      // 创建粒子
      const particle = new fabric.Circle({
        left: points[0].x,
        top: points[0].y,
        radius: 4,
        fill: color,
        stroke: 'rgba(255, 255, 255, 0.5)',
        strokeWidth: 1,
        selectable: false,
        evented: false,
        hoverCursor: 'default',
        originX: 'center',
        originY: 'center'
      });
      
      // 添加到画布
      this.canvas.add(particle);
      
      // 保存粒子引用
      this.particles.push(particle);
      
      // 设置动画
      const duration = 2000;
      const delay = i * 400;
      
      // 延迟开始动画
      setTimeout(() => {
        this._animateParticleAlongPath(particle, points, duration);
      }, delay);
    }
  }
  
  /**
   * 沿路径移动粒子
   * @private
   * @param {Object} particle - 粒子对象
   * @param {Array} points - 路径上的点数组
   * @param {number} duration - 动画持续时间
   */
  _animateParticleAlongPath(particle, points, duration) {
    // 计算路径总长度
    let totalLength = 0;
    const segments = [];
    
    for (let i = 0; i < points.length - 1; i++) {
      const dx = points[i + 1].x - points[i].x;
      const dy = points[i + 1].y - points[i].y;
      const length = Math.sqrt(dx * dx + dy * dy);
      
      totalLength += length;
      segments.push({
        start: points[i],
        end: points[i + 1],
        length: length
      });
    }
    
    // 设置动画
    let startTime = Date.now();
    
    const animate = () => {
      const now = Date.now();
      const elapsed = now - startTime;
      
      if (elapsed >= duration) {
        // 动画完成，重新开始
        startTime = now;
        particle.left = points[0].x;
        particle.top = points[0].y;
        this.canvas.requestRenderAll();
        requestAnimationFrame(animate);
        return;
      }
      
      // 计算当前位置
      const progress = elapsed / duration;
      const distance = totalLength * progress;
      
      // 找到当前所在的线段
      let currentDistance = 0;
      let currentSegment = segments[0];
      
      for (const segment of segments) {
        if (currentDistance + segment.length >= distance) {
          currentSegment = segment;
          break;
        }
        currentDistance += segment.length;
      }
      
      // 计算在当前线段上的位置
      const segmentProgress = (distance - currentDistance) / currentSegment.length;
      
      particle.left = currentSegment.start.x + (currentSegment.end.x - currentSegment.start.x) * segmentProgress;
      particle.top = currentSegment.start.y + (currentSegment.end.y - currentSegment.start.y) * segmentProgress;
      
      this.canvas.requestRenderAll();
      requestAnimationFrame(animate);
    };
    
    requestAnimationFrame(animate);
  }

  /**
   * 查找从攻击者到目标的路径
   * @private
   * @param {Object} attacker - 攻击者设备
   * @param {Object} target - 目标设备
   * @returns {Array} - 返回路径上的设备数组
   */
  _findAttackPath(attacker, target) {
    // 简单实现：查找连接攻击者和目标的所有设备
    const path = [attacker];
    
    // 查找连接攻击者的防火墙
    const attackerFirewall = this._findConnectedFirewall(attacker);
    if (attackerFirewall) {
      path.push(attackerFirewall);
    }
    
    // 查找连接目标的防火墙（如果与攻击者的防火墙不同）
    const targetFirewall = this._findConnectedFirewall(target);
    if (targetFirewall && targetFirewall !== attackerFirewall) {
      path.push(targetFirewall);
    }
    
    // 添加目标
    path.push(target);
    
    return path;
  }

  /**
   * 查找与设备连接的防火墙
   * @private
   * @param {Object} device - 设备对象
   * @returns {Object|null} - 返回连接的防火墙，如果没有则返回null
   */
  _findConnectedFirewall(device) {
    for (const connection of this.topology.connections) {
      if (connection.source === device && connection.target.deviceType === 'firewall') {
        return connection.target;
      }
      if (connection.target === device && connection.source.deviceType === 'firewall') {
        return connection.source;
      }
    }
    return null;
  }

  /**
   * 创建攻击路径可视化
   * @private
   * @param {Array} path - 攻击路径
   * @param {string} attackType - 攻击类型
   */
  _createAttackPathVisualization(path, attackType) {
    // 根据攻击类型选择颜色
    const colors = {
      'port_scan': '#3498db',  // 蓝色
      'brute_force': '#f39c12', // 橙色
      'exploit': '#e74c3c',    // 红色
      'ddos': '#9b59b6',       // 紫色
      'phishing': '#2ecc71',   // 绿色
      'social_engineering': '#1abc9c' // 青色
    };
    const color = colors[attackType] || '#3498db';
    
    // 为路径上的每对设备创建连接线
    for (let i = 0; i < path.length - 1; i++) {
      const source = path[i];
      const target = path[i + 1];
      
      // 创建攻击路径线
      const line = new fabric.Line([
        source.left,
        source.top,
        target.left,
        target.top
      ], {
        stroke: color,
        strokeWidth: 3,
        strokeDashArray: [5, 5],
        selectable: false,
        evented: false,
        hoverCursor: 'default'
      });
      
      // 添加到画布
      this.canvas.add(line);
      
      // 将线发送到设备后面
      line.sendToBack();
      
      // 保存路径引用
      this.attackPaths.push(line);
    }
    
    // 重新渲染画布
    this.canvas.requestRenderAll();
  }

  /**
   * 创建攻击动画
   * @private
   * @param {Array} path - 攻击路径
   * @param {string} attackType - 攻击类型
   */
  _createAttackAnimation(path, attackType) {
    // 根据攻击类型选择颜色和大小
    const colors = {
      'port_scan': '#3498db',  // 蓝色
      'brute_force': '#f39c12', // 橙色
      'exploit': '#e74c3c',    // 红色
      'ddos': '#9b59b6',       // 紫色
      'phishing': '#2ecc71',   // 绿色
      'social_engineering': '#1abc9c' // 青色
    };
    const color = colors[attackType] || '#3498db';
    
    const sizes = {
      'port_scan': 4,
      'brute_force': 5,
      'exploit': 6,
      'ddos': 3,
      'phishing': 5,
      'social_engineering': 4
    };
    const size = sizes[attackType] || 4;
    
    // 为路径上的每段创建粒子动画
    for (let i = 0; i < path.length - 1; i++) {
      const source = path[i];
      const target = path[i + 1];
      
      // 创建多个粒子
      const particleCount = attackType === 'ddos' ? 20 : 5;
      
      for (let j = 0; j < particleCount; j++) {
        // 创建粒子
        const particle = new fabric.Circle({
          left: source.left,
          top: source.top,
          radius: size,
          fill: color,
          stroke: 'rgba(255, 255, 255, 0.5)',
          strokeWidth: 1,
          selectable: false,
          evented: false,
          hoverCursor: 'default',
          originX: 'center',
          originY: 'center'
        });
        
        // 添加到画布
        this.canvas.add(particle);
        
        // 保存粒子引用
        this.particles.push(particle);
        
        // 设置动画
        const duration = attackType === 'ddos' ? 500 + Math.random() * 500 : 1000 + Math.random() * 500;
        const delay = j * 100;
        
        // 使用fabric.js的动画API
        fabric.util.animate({
          startValue: 0,
          endValue: 1,
          duration: duration,
          onChange: (value) => {
            particle.left = source.left + (target.left - source.left) * value;
            particle.top = source.top + (target.top - source.top) * value;
            this.canvas.requestRenderAll();
          },
          onComplete: () => {
            // 动画完成后移除粒子
            this.canvas.remove(particle);
            this.particles = this.particles.filter(p => p !== particle);
          },
          easing: fabric.util.ease.easeInOutQuad
        });
        
        // 延迟开始动画
        setTimeout(() => {
          // 动画已经开始
        }, delay);
      }
    }
  }

  /**
   * 创建钓鱼攻击特定的动画
   * @private
   * @param {Array} path - 攻击路径
   * @param {string} attackType - 攻击类型
   */
  _createPhishingAnimation(path, attackType) {
    // 钓鱼攻击的颜色和大小
    const color = attackType === 'phishing' ? '#2ecc71' : '#1abc9c';
    const size = 5;
    
    // 第一阶段：发送邮件
    const source = path[0]; // 攻击者
    const target = path[path.length - 1]; // 目标
    
    // 创建邮件图标
    const emailIcon = new fabric.Text('✉', {
      left: source.left,
      top: source.top,
      fontSize: 24,
      fill: color,
      selectable: false,
      evented: false,
      hoverCursor: 'default',
      originX: 'center',
      originY: 'center'
    });
    
    // 添加到画布
    this.canvas.add(emailIcon);
    this.particles.push(emailIcon);
    
    // 设置动画
    fabric.util.animate({
      startValue: 0,
      endValue: 1,
      duration: 2000,
      onChange: (value) => {
        emailIcon.left = source.left + (target.left - source.left) * value;
        emailIcon.top = source.top + (target.top - source.top) * value;
        this.canvas.requestRenderAll();
      },
      onComplete: () => {
        // 邮件到达后，创建一个闪烁效果
        this._createBlinkEffect(target, color);
        
        // 第二阶段：数据窃取
        setTimeout(() => {
          // 创建数据图标
          const dataIcon = new fabric.Text('🔑', {
            left: target.left,
            top: target.top,
            fontSize: 24,
            fill: '#e74c3c',
            selectable: false,
            evented: false,
            hoverCursor: 'default',
            originX: 'center',
            originY: 'center'
          });
          
          // 添加到画布
          this.canvas.add(dataIcon);
          this.particles.push(dataIcon);
          
          // 设置动画
          fabric.util.animate({
            startValue: 0,
            endValue: 1,
            duration: 2000,
            onChange: (value) => {
              dataIcon.left = target.left + (source.left - target.left) * value;
              dataIcon.top = target.top + (source.top - target.top) * value;
              this.canvas.requestRenderAll();
            },
            onComplete: () => {
              // 动画完成后移除图标
              this.canvas.remove(dataIcon);
              this.particles = this.particles.filter(p => p !== dataIcon);
              
              // 在攻击者处创建一个成功效果
              this._createSuccessEffect(source);
            },
            easing: fabric.util.ease.easeInOutQuad
          });
        }, 1000);
      },
      easing: fabric.util.ease.easeInOutQuad
    });
  }

  /**
   * 创建闪烁效果
   * @private
   * @param {Object} target - 目标设备
   * @param {string} color - 颜色
   */
  _createBlinkEffect(target, color) {
    // 创建圆圈
    const circle = new fabric.Circle({
      left: target.left,
      top: target.top,
      radius: 30,
      fill: 'transparent',
      stroke: color,
      strokeWidth: 3,
      selectable: false,
      evented: false,
      hoverCursor: 'default',
      originX: 'center',
      originY: 'center'
    });
    
    // 添加到画布
    this.canvas.add(circle);
    this.attackPaths.push(circle);
    
    // 设置闪烁动画
    let opacity = 1;
    const blinkInterval = setInterval(() => {
      opacity = opacity === 1 ? 0.2 : 1;
      circle.set('opacity', opacity);
      this.canvas.requestRenderAll();
    }, 300);
    
    // 3秒后停止闪烁并移除圆圈
    setTimeout(() => {
      clearInterval(blinkInterval);
      this.canvas.remove(circle);
      this.attackPaths = this.attackPaths.filter(p => p !== circle);
    }, 3000);
  }

  /**
   * 创建成功效果
   * @private
   * @param {Object} target - 目标设备
   */
  _createSuccessEffect(target) {
    // 创建成功图标
    const successIcon = new fabric.Text('✓', {
      left: target.left,
      top: target.top - 40,
      fontSize: 36,
      fill: '#2ecc71',
      selectable: false,
      evented: false,
      hoverCursor: 'default',
      originX: 'center',
      originY: 'center',
      opacity: 0
    });
    
    // 添加到画布
    this.canvas.add(successIcon);
    this.attackPaths.push(successIcon);
    
    // 设置动画
    fabric.util.animate({
      startValue: 0,
      endValue: 1,
      duration: 500,
      onChange: (value) => {
        successIcon.opacity = value;
        this.canvas.requestRenderAll();
      },
      onComplete: () => {
        // 2秒后淡出
        setTimeout(() => {
          fabric.util.animate({
            startValue: 1,
            endValue: 0,
            duration: 500,
            onChange: (value) => {
              successIcon.opacity = value;
              this.canvas.requestRenderAll();
            },
            onComplete: () => {
              this.canvas.remove(successIcon);
              this.attackPaths = this.attackPaths.filter(p => p !== successIcon);
            },
            easing: fabric.util.ease.easeInOutQuad
          });
        }, 2000);
      },
      easing: fabric.util.ease.easeInOutQuad
    });
  }
}

export default EnhancedAttackVisualization;