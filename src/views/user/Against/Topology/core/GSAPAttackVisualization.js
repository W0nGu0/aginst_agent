/**
 * 基于GSAP的攻击可视化类
 * 使用GSAP实现高级动画效果
 */
import { gsap } from 'gsap';
import { fabric } from 'fabric';
// 导入GSAP插件
import { MotionPathPlugin } from 'gsap/MotionPathPlugin';

// 注册GSAP插件
gsap.registerPlugin(MotionPathPlugin);

class GSAPAttackVisualization {
  constructor(topology) {
    this.topology = topology;
    this.canvas = topology.canvas;
    this.animations = [];
    this.attackPaths = [];
    this.particles = [];
    this.icons = {};
    this.activeAnimations = [];
    
    // 预加载图标
    this.preloadIcons();
  }

  /**
   * 预加载图标
   */
  preloadIcons() {
    // 定义需要的图标
    const iconTypes = {
      'thinking': '💭',
      'scanning': '🔍',
      'writing': '✍️',
      'email': '✉️',
      'success': '✅',
      'failure': '❌',
      'warning': '⚠️',
      'attack': '💥',
      'defense': '🛡️',
      'key': '🔑',
      'lock': '🔒',
      'unlock': '🔓',
      'computer': '💻',
      'server': '🖥️',
      'database': '🗄️',
      'network': '🌐',
      'firewall': '🧱',
      'hacker': '👨‍💻'
    };
    
    // 创建图标对象
    for (const [type, symbol] of Object.entries(iconTypes)) {
      this.icons[type] = symbol;
    }
  }

  /**
   * 清除所有攻击路径可视化
   */
  clearAttackPaths() {
    // 停止所有活动的动画
    this.activeAnimations.forEach(animation => {
      if (animation.isActive()) {
        animation.kill();
      }
    });
    this.activeAnimations = [];
    
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
   * @returns {Object} - 返回创建的路径对象
   */
  drawAttackPath(points, color = '#ff0000', width = 2) {
    if (!points || points.length < 2) return null;
    
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
      hoverCursor: 'default',
      opacity: 0
    });
    
    // 添加到画布
    this.canvas.add(line);
    
    // 将线发送到设备后面
    line.sendToBack();
    
    // 保存路径引用
    this.attackPaths.push(line);
    
    // 使用GSAP创建淡入动画
    const animation = gsap.to(line, {
      opacity: 1,
      duration: 1,
      ease: 'power2.inOut',
      onUpdate: () => this.canvas.requestRenderAll()
    });
    
    this.activeAnimations.push(animation);
    
    return line;
  }

  /**
   * 创建思考动画
   * @param {Object} node - 节点对象
   * @param {number} duration - 动画持续时间（秒）
   * @returns {Object} - 返回创建的动画对象
   */
  createThinkingAnimation(node, duration = 5) {
    // 创建思考图标
    const thinkingIcon = new fabric.Text(this.icons.thinking, {
      left: node.left + 30,
      top: node.top - 30,
      fontSize: 24,
      fontFamily: 'Arial',
      selectable: false,
      evented: false,
      opacity: 0
    });
    
    // 添加到画布
    this.canvas.add(thinkingIcon);
    this.particles.push(thinkingIcon);
    
    // 创建动画时间线
    const timeline = gsap.timeline();
    
    // 添加淡入动画
    timeline.to(thinkingIcon, {
      opacity: 1,
      duration: 0.5,
      ease: 'power2.inOut',
      onUpdate: () => this.canvas.requestRenderAll()
    });
    
    // 添加脉动动画
    timeline.to(thinkingIcon, {
      scaleX: 1.2,
      scaleY: 1.2,
      duration: 0.8,
      repeat: Math.floor(duration / 0.8),
      yoyo: true,
      ease: 'power1.inOut',
      onUpdate: () => this.canvas.requestRenderAll()
    }, '<');
    
    // 添加淡出动画
    timeline.to(thinkingIcon, {
      opacity: 0,
      duration: 0.5,
      ease: 'power2.inOut',
      onUpdate: () => this.canvas.requestRenderAll(),
      onComplete: () => {
        this.canvas.remove(thinkingIcon);
        this.particles = this.particles.filter(p => p !== thinkingIcon);
      }
    }, `>-${duration}`);
    
    this.activeAnimations.push(timeline);
    
    return timeline;
  }

  /**
   * 创建扫描动画
   * @param {Object} source - 源节点对象
   * @param {Object} target - 目标节点对象
   * @param {number} duration - 动画持续时间（秒）
   * @returns {Object} - 返回创建的动画对象
   */
  createScanningAnimation(source, target, duration = 3) {
    // 创建扫描图标
    const scanningIcon = new fabric.Text(this.icons.scanning, {
      left: source.left,
      top: source.top,
      fontSize: 24,
      fontFamily: 'Arial',
      selectable: false,
      evented: false,
      opacity: 0
    });
    
    // 添加到画布
    this.canvas.add(scanningIcon);
    this.particles.push(scanningIcon);
    
    // 创建动画时间线
    const timeline = gsap.timeline();
    
    // 添加淡入动画
    timeline.to(scanningIcon, {
      opacity: 1,
      duration: 0.5,
      ease: 'power2.inOut',
      onUpdate: () => this.canvas.requestRenderAll()
    });
    
    // 添加移动动画
    timeline.to(scanningIcon, {
      left: target.left,
      top: target.top,
      duration: duration - 1,
      ease: 'power1.inOut',
      onUpdate: () => this.canvas.requestRenderAll()
    });
    
    // 添加淡出动画
    timeline.to(scanningIcon, {
      opacity: 0,
      duration: 0.5,
      ease: 'power2.inOut',
      onUpdate: () => this.canvas.requestRenderAll(),
      onComplete: () => {
        this.canvas.remove(scanningIcon);
        this.particles = this.particles.filter(p => p !== scanningIcon);
      }
    });
    
    this.activeAnimations.push(timeline);
    
    return timeline;
  }

  /**
   * 创建写邮件动画
   * @param {Object} node - 节点对象
   * @param {number} duration - 动画持续时间（秒）
   * @returns {Object} - 返回创建的动画对象
   */
  createWritingAnimation(node, duration = 4) {
    // 创建写邮件图标
    const writingIcon = new fabric.Text(this.icons.writing, {
      left: node.left + 30,
      top: node.top - 30,
      fontSize: 24,
      fontFamily: 'Arial',
      selectable: false,
      evented: false,
      opacity: 0
    });
    
    // 添加到画布
    this.canvas.add(writingIcon);
    this.particles.push(writingIcon);
    
    // 创建动画时间线
    const timeline = gsap.timeline();
    
    // 添加淡入动画
    timeline.to(writingIcon, {
      opacity: 1,
      duration: 0.5,
      ease: 'power2.inOut',
      onUpdate: () => this.canvas.requestRenderAll()
    });
    
    // 添加写字动画
    timeline.to(writingIcon, {
      rotation: -15,
      duration: 0.3,
      repeat: Math.floor(duration / 0.6),
      yoyo: true,
      ease: 'power1.inOut',
      onUpdate: () => this.canvas.requestRenderAll()
    }, '<');
    
    // 添加淡出动画
    timeline.to(writingIcon, {
      opacity: 0,
      duration: 0.5,
      ease: 'power2.inOut',
      onUpdate: () => this.canvas.requestRenderAll(),
      onComplete: () => {
        this.canvas.remove(writingIcon);
        this.particles = this.particles.filter(p => p !== writingIcon);
      }
    }, `>-${duration}`);
    
    this.activeAnimations.push(timeline);
    
    return timeline;
  }

  /**
   * 创建发送邮件动画
   * @param {Object} source - 源节点对象
   * @param {Object} target - 目标节点对象
   * @param {number} duration - 动画持续时间（秒）
   * @returns {Object} - 返回创建的动画对象
   */
  createSendEmailAnimation(source, target, duration = 3) {
    // 创建邮件图标
    const emailIcon = new fabric.Text(this.icons.email, {
      left: source.left,
      top: source.top,
      fontSize: 24,
      fontFamily: 'Arial',
      selectable: false,
      evented: false,
      opacity: 0
    });
    
    // 添加到画布
    this.canvas.add(emailIcon);
    this.particles.push(emailIcon);
    
    // 创建动画时间线
    const timeline = gsap.timeline();
    
    // 添加淡入动画
    timeline.to(emailIcon, {
      opacity: 1,
      duration: 0.5,
      ease: 'power2.inOut',
      onUpdate: () => this.canvas.requestRenderAll()
    });
    
    // 添加移动动画
    timeline.to(emailIcon, {
      left: target.left,
      top: target.top,
      duration: duration - 1,
      ease: 'power1.inOut',
      onUpdate: () => this.canvas.requestRenderAll()
    });
    
    // 添加淡出动画
    timeline.to(emailIcon, {
      opacity: 0,
      duration: 0.5,
      ease: 'power2.inOut',
      onUpdate: () => this.canvas.requestRenderAll(),
      onComplete: () => {
        this.canvas.remove(emailIcon);
        this.particles = this.particles.filter(p => p !== emailIcon);
      }
    });
    
    this.activeAnimations.push(timeline);
    
    return timeline;
  }

  /**
   * 创建攻击成功动画
   * @param {Object} node - 节点对象
   * @param {number} duration - 动画持续时间（秒）
   * @returns {Object} - 返回创建的动画对象
   */
  createSuccessAnimation(node, duration = 3) {
    // 创建成功图标
    const successIcon = new fabric.Text(this.icons.success, {
      left: node.left,
      top: node.top - 30,
      fontSize: 24,
      fontFamily: 'Arial',
      selectable: false,
      evented: false,
      opacity: 0
    });
    
    // 添加到画布
    this.canvas.add(successIcon);
    this.particles.push(successIcon);
    
    // 创建动画时间线
    const timeline = gsap.timeline();
    
    // 添加淡入动画
    timeline.to(successIcon, {
      opacity: 1,
      duration: 0.5,
      ease: 'power2.inOut',
      onUpdate: () => this.canvas.requestRenderAll()
    });
    
    // 添加放大动画
    timeline.to(successIcon, {
      scaleX: 1.5,
      scaleY: 1.5,
      duration: 0.5,
      ease: 'back.out(1.7)',
      onUpdate: () => this.canvas.requestRenderAll()
    }, '<');
    
    // 添加持续时间
    timeline.to(successIcon, {
      duration: duration - 1.5,
      onUpdate: () => this.canvas.requestRenderAll()
    });
    
    // 添加淡出动画
    timeline.to(successIcon, {
      opacity: 0,
      duration: 0.5,
      ease: 'power2.inOut',
      onUpdate: () => this.canvas.requestRenderAll(),
      onComplete: () => {
        this.canvas.remove(successIcon);
        this.particles = this.particles.filter(p => p !== successIcon);
      }
    });
    
    this.activeAnimations.push(timeline);
    
    return timeline;
  }

  /**
   * 创建攻击失败动画
   * @param {Object} node - 节点对象
   * @param {number} duration - 动画持续时间（秒）
   * @returns {Object} - 返回创建的动画对象
   */
  createFailureAnimation(node, duration = 3) {
    // 创建失败图标
    const failureIcon = new fabric.Text(this.icons.failure, {
      left: node.left,
      top: node.top - 30,
      fontSize: 24,
      fontFamily: 'Arial',
      selectable: false,
      evented: false,
      opacity: 0
    });
    
    // 添加到画布
    this.canvas.add(failureIcon);
    this.particles.push(failureIcon);
    
    // 创建动画时间线
    const timeline = gsap.timeline();
    
    // 添加淡入动画
    timeline.to(failureIcon, {
      opacity: 1,
      duration: 0.5,
      ease: 'power2.inOut',
      onUpdate: () => this.canvas.requestRenderAll()
    });
    
    // 添加摇晃动画
    timeline.to(failureIcon, {
      rotation: 15,
      duration: 0.1,
      repeat: 5,
      yoyo: true,
      ease: 'power1.inOut',
      onUpdate: () => this.canvas.requestRenderAll()
    }, '<');
    
    // 添加持续时间
    timeline.to(failureIcon, {
      duration: duration - 1.5,
      onUpdate: () => this.canvas.requestRenderAll()
    });
    
    // 添加淡出动画
    timeline.to(failureIcon, {
      opacity: 0,
      duration: 0.5,
      ease: 'power2.inOut',
      onUpdate: () => this.canvas.requestRenderAll(),
      onComplete: () => {
        this.canvas.remove(failureIcon);
        this.particles = this.particles.filter(p => p !== failureIcon);
      }
    });
    
    this.activeAnimations.push(timeline);
    
    return timeline;
  }

  /**
   * 创建数据窃取动画
   * @param {Object} source - 源节点对象
   * @param {Object} target - 目标节点对象
   * @param {number} duration - 动画持续时间（秒）
   * @returns {Object} - 返回创建的动画对象
   */
  createDataTheftAnimation(source, target, duration = 3) {
    // 创建钥匙图标
    const keyIcon = new fabric.Text(this.icons.key, {
      left: source.left,
      top: source.top,
      fontSize: 24,
      fontFamily: 'Arial',
      selectable: false,
      evented: false,
      opacity: 0
    });
    
    // 添加到画布
    this.canvas.add(keyIcon);
    this.particles.push(keyIcon);
    
    // 创建动画时间线
    const timeline = gsap.timeline();
    
    // 添加淡入动画
    timeline.to(keyIcon, {
      opacity: 1,
      duration: 0.5,
      ease: 'power2.inOut',
      onUpdate: () => this.canvas.requestRenderAll()
    });
    
    // 添加移动动画
    timeline.to(keyIcon, {
      left: target.left,
      top: target.top,
      duration: duration - 1,
      ease: 'power1.inOut',
      onUpdate: () => this.canvas.requestRenderAll()
    });
    
    // 添加淡出动画
    timeline.to(keyIcon, {
      opacity: 0,
      duration: 0.5,
      ease: 'power2.inOut',
      onUpdate: () => this.canvas.requestRenderAll(),
      onComplete: () => {
        this.canvas.remove(keyIcon);
        this.particles = this.particles.filter(p => p !== keyIcon);
      }
    });
    
    this.activeAnimations.push(timeline);
    
    return timeline;
  }

  /**
   * 创建攻击动画序列
   * @param {Object} attacker - 攻击者节点
   * @param {Object} target - 目标节点
   * @param {string} attackType - 攻击类型
   * @returns {Object} - 返回创建的动画时间线
   */
  createAttackSequence(attacker, target, attackType = 'phishing') {
    // 创建主时间线
    const mainTimeline = gsap.timeline();
    
    // 绘制攻击路径
    const path = this.drawAttackPath([
      { x: attacker.left, y: attacker.top },
      { x: target.left, y: target.top }
    ]);
    
    // 根据攻击类型创建不同的动画序列
    if (attackType === 'phishing' || attackType === 'social_engineering') {
      // 钓鱼攻击序列
      
      // 1. 思考动画
      mainTimeline.add(() => {
        return this.createThinkingAnimation(attacker, 3);
      });
      
      // 2. 写邮件动画
      mainTimeline.add(() => {
        return this.createWritingAnimation(attacker, 3);
      }, '>');
      
      // 3. 发送邮件动画
      mainTimeline.add(() => {
        return this.createSendEmailAnimation(attacker, target, 2);
      }, '>');
      
      // 4. 目标思考动画
      mainTimeline.add(() => {
        return this.createThinkingAnimation(target, 2);
      }, '>');
      
      // 5. 数据窃取动画
      mainTimeline.add(() => {
        return this.createDataTheftAnimation(target, attacker, 2);
      }, '>');
      
      // 6. 成功动画
      mainTimeline.add(() => {
        return this.createSuccessAnimation(attacker, 2);
      }, '>');
      
    } else if (attackType === 'exploit') {
      // 漏洞利用攻击序列
      
      // 1. 思考动画
      mainTimeline.add(() => {
        return this.createThinkingAnimation(attacker, 3);
      });
      
      // 2. 扫描动画
      mainTimeline.add(() => {
        return this.createScanningAnimation(attacker, target, 3);
      }, '>');
      
      // 3. 攻击动画
      mainTimeline.add(() => {
        // 创建攻击图标
        const attackIcon = new fabric.Text(this.icons.attack, {
          left: attacker.left,
          top: attacker.top,
          fontSize: 24,
          fontFamily: 'Arial',
          selectable: false,
          evented: false,
          opacity: 0
        });
        
        // 添加到画布
        this.canvas.add(attackIcon);
        this.particles.push(attackIcon);
        
        // 创建动画时间线
        const timeline = gsap.timeline();
        
        // 添加淡入动画
        timeline.to(attackIcon, {
          opacity: 1,
          duration: 0.5,
          ease: 'power2.inOut',
          onUpdate: () => this.canvas.requestRenderAll()
        });
        
        // 添加移动动画
        timeline.to(attackIcon, {
          left: target.left,
          top: target.top,
          duration: 1.5,
          ease: 'power1.inOut',
          onUpdate: () => this.canvas.requestRenderAll()
        });
        
        // 添加爆炸效果
        timeline.to(attackIcon, {
          scaleX: 2,
          scaleY: 2,
          opacity: 0,
          duration: 0.5,
          ease: 'power3.out',
          onUpdate: () => this.canvas.requestRenderAll(),
          onComplete: () => {
            this.canvas.remove(attackIcon);
            this.particles = this.particles.filter(p => p !== attackIcon);
          }
        });
        
        this.activeAnimations.push(timeline);
        
        return timeline;
      }, '>');
      
      // 4. 成功动画
      mainTimeline.add(() => {
        return this.createSuccessAnimation(target, 2);
      }, '>');
      
    } else {
      // 默认攻击序列
      
      // 1. 思考动画
      mainTimeline.add(() => {
        return this.createThinkingAnimation(attacker, 3);
      });
      
      // 2. 扫描动画
      mainTimeline.add(() => {
        return this.createScanningAnimation(attacker, target, 3);
      }, '>');
      
      // 3. 攻击动画
      mainTimeline.add(() => {
        return this.createSendEmailAnimation(attacker, target, 2);
      }, '>');
      
      // 4. 成功或失败动画
      const isSuccess = Math.random() > 0.3; // 70%的成功率
      mainTimeline.add(() => {
        return isSuccess ? 
          this.createSuccessAnimation(target, 2) : 
          this.createFailureAnimation(target, 2);
      }, '>');
    }
    
    this.activeAnimations.push(mainTimeline);
    
    return mainTimeline;
  }

  /**
   * 更新节点状态
   * @param {Object} node - 节点对象
   * @param {string} status - 状态：'normal', 'targeted', 'compromised'
   */
  updateNodeStatus(node, status) {
    if (!node) return;
    
    // 根据状态设置节点样式
    switch (status) {
      case 'targeted':
        // 目标被瞄准
        gsap.to(node, {
          strokeWidth: 2,
          duration: 0.5,
          onUpdate: () => {
            node.set({
              stroke: '#ff0000'
            });
            this.canvas.requestRenderAll();
          }
        });
        break;
      case 'compromised':
        // 目标已被攻陷
        gsap.to(node, {
          strokeWidth: 3,
          duration: 0.5,
          onUpdate: () => {
            node.set({
              stroke: '#ff0000',
              strokeDashArray: [5, 5]
            });
            this.canvas.requestRenderAll();
          }
        });
        break;
      case 'normal':
      default:
        // 恢复正常状态
        gsap.to(node, {
          strokeWidth: 1,
          duration: 0.5,
          onUpdate: () => {
            node.set({
              stroke: '#ffffff',
              strokeDashArray: null
            });
            this.canvas.requestRenderAll();
          }
        });
        break;
    }
  }
}

export default GSAPAttackVisualization;