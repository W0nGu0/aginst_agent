/**
 * 增强版攻击可视化类
 * 使用GSAP和高级动画效果实现更专业的攻击可视化
 */
import { gsap } from "gsap";
import { fabric } from "fabric";

class EnhancedAttackVisualization {
  constructor(topology) {
    this.topology = topology;
    this.canvas = topology.canvas;
    this.animations = [];
    this.attackPaths = [];
    this.particles = [];
    this.activeAnimations = [];

    // 预加载图标
    this.preloadIcons();
  }

  /**
   * 预加载图标
   */
  preloadIcons() {
    // 图标将在需要时动态创建
    this.iconColors = {
      scanning: "#00a8ff",
      thinking: "#9c88ff",
      writing: "#fbc531",
      email: "#4cd137",
      success: "#2ecc71",
      failure: "#e74c3c",
      warning: "#f39c12",
      attack: "#e84118",
      defense: "#273c75",
      key: "#f1c40f",
    };
  }

  /**
   * 清除所有攻击路径可视化
   */
  clearAttackPaths() {
    // 停止所有活动的动画
    this.activeAnimations.forEach((animation) => {
      if (animation.isActive && animation.isActive()) {
        animation.kill();
      }
    });
    this.activeAnimations = [];

    // 移除所有粒子
    this.particles.forEach((particle) => {
      this.canvas.remove(particle);
    });
    this.particles = [];

    // 移除所有攻击路径
    this.attackPaths.forEach((path) => {
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
  drawAttackPath(points, color = "#ff0000", width = 2) {
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
      fill: "transparent",
      selectable: false,
      evented: false,
      hoverCursor: "default",
      opacity: 0,
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
      ease: "power2.inOut",
      onUpdate: () => this.canvas.requestRenderAll(),
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
    // 创建思考图标 - 使用圆形
    const circle = new fabric.Circle({
      left: node.left + 30,
      top: node.top - 30,
      radius: 15,
      fill: this.iconColors.thinking,
      stroke: "#ffffff",
      strokeWidth: 2,
      selectable: false,
      evented: false,
      opacity: 0,
    });

    // 添加到画布
    this.canvas.add(circle);
    this.particles.push(circle);

    // 创建动画时间线
    const timeline = gsap.timeline();

    // 添加淡入动画
    timeline.to(circle, {
      opacity: 1,
      duration: 0.5,
      ease: "power2.inOut",
      onUpdate: () => this.canvas.requestRenderAll(),
    });

    // 添加脉动动画
    timeline.to(
      circle,
      {
        scaleX: 1.2,
        scaleY: 1.2,
        duration: 0.8,
        repeat: Math.floor(duration / 0.8),
        yoyo: true,
        ease: "power1.inOut",
        onUpdate: () => this.canvas.requestRenderAll(),
      },
      "<"
    );

    // 添加淡出动画
    timeline.to(
      circle,
      {
        opacity: 0,
        duration: 0.5,
        ease: "power2.inOut",
        onUpdate: () => this.canvas.requestRenderAll(),
        onComplete: () => {
          this.canvas.remove(circle);
          this.particles = this.particles.filter((p) => p !== circle);
        },
      },
      `>-${duration * 0.2}`
    );

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
    // 创建扫描图标 - 使用圆形
    const circle = new fabric.Circle({
      left: source.left,
      top: source.top,
      radius: 15,
      fill: this.iconColors.scanning,
      stroke: "#ffffff",
      strokeWidth: 2,
      selectable: false,
      evented: false,
      opacity: 0,
    });

    // 添加到画布
    this.canvas.add(circle);
    this.particles.push(circle);

    // 创建动画时间线
    const timeline = gsap.timeline();

    // 添加淡入动画
    timeline.to(circle, {
      opacity: 1,
      duration: 0.5,
      ease: "power2.inOut",
      onUpdate: () => this.canvas.requestRenderAll(),
    });

    // 添加移动动画
    timeline.to(circle, {
      left: target.left,
      top: target.top,
      duration: duration - 1,
      ease: "power1.inOut",
      onUpdate: () => this.canvas.requestRenderAll(),
    });

    // 添加淡出动画
    timeline.to(circle, {
      opacity: 0,
      duration: 0.5,
      ease: "power2.inOut",
      onUpdate: () => this.canvas.requestRenderAll(),
      onComplete: () => {
        this.canvas.remove(circle);
        this.particles = this.particles.filter((p) => p !== circle);
      },
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
    // 创建邮件图标 - 使用矩形
    const envelope = new fabric.Rect({
      left: node.left + 30,
      top: node.top - 30,
      width: 30,
      height: 20,
      fill: "#ffffff",
      stroke: this.iconColors.writing,
      strokeWidth: 2,
      rx: 2,
      ry: 2,
      selectable: false,
      evented: false,
      opacity: 0,
    });

    // 添加到画布
    this.canvas.add(envelope);
    this.particles.push(envelope);

    // 创建动画时间线
    const timeline = gsap.timeline();

    // 添加淡入动画
    timeline.to(envelope, {
      opacity: 1,
      duration: 0.5,
      ease: "power2.inOut",
      onUpdate: () => this.canvas.requestRenderAll(),
    });

    // 添加抖动动画
    timeline.to(
      envelope,
      {
        left: "+=2",
        duration: 0.1,
        repeat: Math.floor(duration / 0.2),
        yoyo: true,
        ease: "power1.inOut",
        onUpdate: () => this.canvas.requestRenderAll(),
      },
      "<"
    );

    // 添加淡出动画
    timeline.to(
      envelope,
      {
        opacity: 0,
        duration: 0.5,
        ease: "power2.inOut",
        onUpdate: () => this.canvas.requestRenderAll(),
        onComplete: () => {
          this.canvas.remove(envelope);
          this.particles = this.particles.filter((p) => p !== envelope);
        },
      },
      `>-${duration * 0.2}`
    );

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
    // 创建邮件图标 - 使用矩形
    const envelope = new fabric.Rect({
      left: source.left,
      top: source.top,
      width: 30,
      height: 20,
      fill: "#ffffff",
      stroke: this.iconColors.email,
      strokeWidth: 2,
      rx: 2,
      ry: 2,
      selectable: false,
      evented: false,
      opacity: 0,
    });

    // 添加到画布
    this.canvas.add(envelope);
    this.particles.push(envelope);

    // 创建动画时间线
    const timeline = gsap.timeline();

    // 添加淡入动画
    timeline.to(envelope, {
      opacity: 1,
      duration: 0.5,
      ease: "power2.inOut",
      onUpdate: () => this.canvas.requestRenderAll(),
    });

    // 添加移动动画
    timeline.to(envelope, {
      left: target.left,
      top: target.top,
      duration: duration - 1,
      ease: "power1.inOut",
      onUpdate: () => this.canvas.requestRenderAll(),
    });

    // 添加淡出动画
    timeline.to(envelope, {
      opacity: 0,
      duration: 0.5,
      ease: "power2.inOut",
      onUpdate: () => this.canvas.requestRenderAll(),
      onComplete: () => {
        this.canvas.remove(envelope);
        this.particles = this.particles.filter((p) => p !== envelope);
      },
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
    // 创建成功图标 - 使用圆形
    const circle = new fabric.Circle({
      left: node.left,
      top: node.top - 30,
      radius: 15,
      fill: this.iconColors.success,
      selectable: false,
      evented: false,
      opacity: 0,
    });

    // 添加到画布
    this.canvas.add(circle);
    this.particles.push(circle);

    // 创建动画时间线
    const timeline = gsap.timeline();

    // 添加淡入动画
    timeline.to(circle, {
      opacity: 1,
      duration: 0.5,
      ease: "power2.inOut",
      onUpdate: () => this.canvas.requestRenderAll(),
    });

    // 添加放大动画
    timeline.to(
      circle,
      {
        scaleX: 1.5,
        scaleY: 1.5,
        duration: 0.5,
        ease: "back.out(1.7)",
        onUpdate: () => this.canvas.requestRenderAll(),
      },
      "<"
    );

    // 添加持续时间
    timeline.to(
      {},
      {
        duration: duration - 1.5,
        onUpdate: () => this.canvas.requestRenderAll(),
      }
    );

    // 添加淡出动画
    timeline.to(circle, {
      opacity: 0,
      duration: 0.5,
      ease: "power2.inOut",
      onUpdate: () => this.canvas.requestRenderAll(),
      onComplete: () => {
        this.canvas.remove(circle);
        this.particles = this.particles.filter((p) => p !== circle);
      },
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
    // 创建失败图标 - 使用圆形
    const circle = new fabric.Circle({
      left: node.left,
      top: node.top - 30,
      radius: 15,
      fill: this.iconColors.failure,
      selectable: false,
      evented: false,
      opacity: 0,
    });

    // 添加到画布
    this.canvas.add(circle);
    this.particles.push(circle);

    // 创建动画时间线
    const timeline = gsap.timeline();

    // 添加淡入动画
    timeline.to(circle, {
      opacity: 1,
      duration: 0.5,
      ease: "power2.inOut",
      onUpdate: () => this.canvas.requestRenderAll(),
    });

    // 添加摇晃动画
    timeline.to(
      circle,
      {
        left: "+=5",
        duration: 0.1,
        repeat: 5,
        yoyo: true,
        ease: "power1.inOut",
        onUpdate: () => this.canvas.requestRenderAll(),
      },
      "<"
    );

    // 添加持续时间
    timeline.to(
      {},
      {
        duration: duration - 1.5,
        onUpdate: () => this.canvas.requestRenderAll(),
      }
    );

    // 添加淡出动画
    timeline.to(circle, {
      opacity: 0,
      duration: 0.5,
      ease: "power2.inOut",
      onUpdate: () => this.canvas.requestRenderAll(),
      onComplete: () => {
        this.canvas.remove(circle);
        this.particles = this.particles.filter((p) => p !== circle);
      },
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
    // 创建数据图标 - 使用矩形
    const dataRect = new fabric.Rect({
      left: source.left,
      top: source.top,
      width: 20,
      height: 25,
      fill: "#ffffff",
      stroke: this.iconColors.key,
      strokeWidth: 2,
      rx: 2,
      ry: 2,
      selectable: false,
      evented: false,
      opacity: 0,
    });

    // 添加到画布
    this.canvas.add(dataRect);
    this.particles.push(dataRect);

    // 创建动画时间线
    const timeline = gsap.timeline();

    // 添加淡入动画
    timeline.to(dataRect, {
      opacity: 1,
      duration: 0.5,
      ease: "power2.inOut",
      onUpdate: () => this.canvas.requestRenderAll(),
    });

    // 添加移动动画
    timeline.to(dataRect, {
      left: target.left,
      top: target.top,
      duration: duration - 1,
      ease: "power1.inOut",
      onUpdate: () => this.canvas.requestRenderAll(),
    });

    // 添加淡出动画
    timeline.to(dataRect, {
      opacity: 0,
      duration: 0.5,
      ease: "power2.inOut",
      onUpdate: () => this.canvas.requestRenderAll(),
      onComplete: () => {
        this.canvas.remove(dataRect);
        this.particles = this.particles.filter((p) => p !== dataRect);
      },
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
  createAttackSequence(attacker, target, attackType = "phishing") {
    // 创建主时间线
    const mainTimeline = gsap.timeline();

    // 绘制攻击路径
    const path = this.drawAttackPath(
      [
        { x: attacker.left, y: attacker.top },
        { x: target.left, y: target.top },
      ],
      attackType === "phishing" ? "#ff5722" : "#e91e63",
      2
    );

    // 根据攻击类型创建不同的动画序列
    if (attackType === "phishing" || attackType === "social_engineering") {
      // 钓鱼攻击序列

      // 1. 思考动画
      mainTimeline.add(() => {
        return this.createThinkingAnimation(attacker, 3);
      });

      // 2. 写邮件动画
      mainTimeline.add(() => {
        return this.createWritingAnimation(attacker, 3);
      }, ">");

      // 3. 发送邮件动画
      mainTimeline.add(() => {
        return this.createSendEmailAnimation(attacker, target, 2);
      }, ">");

      // 4. 目标思考动画
      mainTimeline.add(() => {
        return this.createThinkingAnimation(target, 2);
      }, ">");

      // 5. 数据窃取动画
      mainTimeline.add(() => {
        return this.createDataTheftAnimation(target, attacker, 2);
      }, ">");

      // 6. 成功动画
      mainTimeline.add(() => {
        return this.createSuccessAnimation(attacker, 2);
      }, ">");
    } else if (attackType === "exploit") {
      // 漏洞利用攻击序列

      // 1. 思考动画
      mainTimeline.add(() => {
        return this.createThinkingAnimation(attacker, 3);
      });

      // 2. 扫描动画
      mainTimeline.add(() => {
        return this.createScanningAnimation(attacker, target, 3);
      }, ">");

      // 3. 攻击动画
      mainTimeline.add(() => {
        return this.createSendEmailAnimation(attacker, target, 2);
      }, ">");

      // 4. 成功动画
      mainTimeline.add(() => {
        return this.createSuccessAnimation(target, 2);
      }, ">");
    } else {
      // 默认攻击序列

      // 1. 思考动画
      mainTimeline.add(() => {
        return this.createThinkingAnimation(attacker, 3);
      });

      // 2. 扫描动画
      mainTimeline.add(() => {
        return this.createScanningAnimation(attacker, target, 3);
      }, ">");

      // 3. 攻击动画
      mainTimeline.add(() => {
        return this.createSendEmailAnimation(attacker, target, 2);
      }, ">");

      // 4. 成功或失败动画
      const isSuccess = Math.random() > 0.3; // 70%的成功率
      mainTimeline.add(() => {
        return isSuccess
          ? this.createSuccessAnimation(target, 2)
          : this.createFailureAnimation(target, 2);
      }, ">");
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
      case "targeted":
        // 目标被瞄准
        gsap.to(node, {
          strokeWidth: 2,
          duration: 0.5,
          onUpdate: () => {
            node.set({
              stroke: "#ff5722",
            });
            this.canvas.requestRenderAll();
          },
        });
        break;
      case "compromised":
        // 目标已被攻陷
        gsap.to(node, {
          strokeWidth: 3,
          duration: 0.5,
          onUpdate: () => {
            node.set({
              stroke: "#e91e63",
              strokeDashArray: [5, 5],
            });
            this.canvas.requestRenderAll();
          },
        });
        break;
      case "normal":
      default:
        // 恢复正常状态
        gsap.to(node, {
          strokeWidth: 1,
          duration: 0.5,
          onUpdate: () => {
            node.set({
              stroke: "#ffffff",
              strokeDashArray: null,
            });
            this.canvas.requestRenderAll();
          },
        });
        break;
    }
  }
}

export default EnhancedAttackVisualization;
