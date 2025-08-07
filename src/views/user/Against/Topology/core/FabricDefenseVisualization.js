/**
 * 基于Fabric.js的防御可视化类
 * 用于显示防御Agent的各种防御动作
 */
import { fabric } from 'fabric';

class FabricDefenseVisualization {
  constructor(topology) {
    this.topology = topology;
    this.canvas = topology.canvas;
    this.activeDefenseAnimations = [];
    this.defenseEffects = [];
    this.continuousDefenseAnimations = new Map();

    // 防御动画配置
    this.config = {
      // 威胁阻断动画
      threatBlocking: {
        duration: 1500,
        shieldColor: '#10b981',
        blockColor: '#dc2626',
        pulseRadius: 25
      },
      // 漏洞修复动画
      vulnerabilityFix: {
        duration: 3000,
        repairColor: '#3b82f6',
        progressColor: '#22c55e',
        toolSize: 20
      },
      // 攻击溯源动画
      attackTracing: {
        duration: 2000,
        traceColor: '#f59e0b',
        pathWidth: 3,
        analyzeRadius: 30
      },
      // 防火墙更新动画
      firewallUpdate: {
        duration: 1000,
        updateColor: '#8b5cf6',
        ruleColor: '#06b6d4'
      }
    };
  }

  /**
   * 创建节点隔离动画
   * @param {fabric.Object} targetNode - 目标节点
   */
  createNodeIsolationAnimation(targetNode) {
    console.log('🔒 创建节点隔离动画:', targetNode.deviceData?.name || targetNode.id);

    const center = targetNode.getCenterPoint();
    const nodeRadius = Math.max(targetNode.width, targetNode.height) / 2;

    // 创建隔离屏障圈
    const isolationBarrier = new fabric.Circle({
      left: center.x,
      top: center.y,
      radius: nodeRadius + 15,
      fill: 'transparent',
      stroke: '#dc2626',
      strokeWidth: 4,
      strokeDashArray: [8, 4],
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0
    });

    // 创建隔离警告图标
    const warningIcon = new fabric.Text('⚠️', {
      left: center.x + nodeRadius + 25,
      top: center.y - nodeRadius - 25,
      fontSize: 24,
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0
    });

    // 创建隔离标签
    const isolationLabel = new fabric.Text('已隔离', {
      left: center.x,
      top: center.y + nodeRadius + 35,
      fontSize: 14,
      fill: '#dc2626',
      fontWeight: 'bold',
      textAlign: 'center',
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0,
      backgroundColor: 'rgba(220, 38, 38, 0.1)',
      padding: 4
    });

    this.canvas.add(isolationBarrier);
    this.canvas.add(warningIcon);
    this.canvas.add(isolationLabel);
    this.defenseEffects.push(isolationBarrier, warningIcon, isolationLabel);

    // 隔离屏障出现动画
    isolationBarrier.animate('opacity', 0.8, {
      duration: 600,
      onChange: () => this.canvas.renderAll()
    });

    // 警告图标弹出
    setTimeout(() => {
      warningIcon.animate({
        opacity: 1,
        scaleX: 1.2,
        scaleY: 1.2
      }, {
        duration: 400,
        easing: fabric.util.ease.easeOutBack,
        onChange: () => this.canvas.renderAll()
      });
    }, 300);

    // 标签淡入
    setTimeout(() => {
      isolationLabel.animate('opacity', 1, {
        duration: 400,
        onChange: () => this.canvas.renderAll()
      });
    }, 600);

    // 创建持续的隔离脉冲
    this.createIsolationPulse(targetNode, isolationBarrier);

    // 标记节点为隔离状态
    targetNode.isolated = true;
    targetNode.isolationTime = new Date();
  }

  /**
   * 创建隔离脉冲动画
   * @param {fabric.Object} targetNode - 目标节点
   * @param {fabric.Object} barrier - 隔离屏障
   */
  createIsolationPulse(targetNode, barrier) {
    const center = targetNode.getCenterPoint();
    const baseRadius = Math.max(targetNode.width, targetNode.height) / 2;

    const createPulse = () => {
      if (!targetNode.isolated) return;

      const pulse = new fabric.Circle({
        left: center.x,
        top: center.y,
        radius: baseRadius + 15,
        fill: 'transparent',
        stroke: '#dc2626',
        strokeWidth: 2,
        originX: 'center',
        originY: 'center',
        selectable: false,
        evented: false,
        opacity: 0.6
      });

      this.canvas.add(pulse);
      this.defenseEffects.push(pulse);

      pulse.animate({
        radius: baseRadius + 35,
        opacity: 0
      }, {
        duration: 2000,
        easing: fabric.util.ease.easeOutQuad,
        onChange: () => this.canvas.renderAll(),
        onComplete: () => {
          this.removeDefenseEffect(pulse);
          if (targetNode.isolated) {
            setTimeout(createPulse, 1000);
          }
        }
      });
    };

    createPulse();
  }

  /**
   * 创建威胁阻断动画
   * @param {fabric.Object} sourceNode - 威胁源节点
   * @param {fabric.Object} targetNode - 目标节点
   * @param {string} threatType - 威胁类型
   */
  createThreatBlockingAnimation(sourceNode, targetNode, threatType = 'malicious_traffic') {
    console.log('🛡️ 创建威胁阻断动画:', threatType);

    const sourceCenter = sourceNode.getCenterPoint();
    const targetCenter = targetNode.getCenterPoint();
    const midPoint = {
      x: (sourceCenter.x + targetCenter.x) / 2,
      y: (sourceCenter.y + targetCenter.y) / 2
    };

    // 创建威胁路径（红色虚线）
    const threatPath = new fabric.Line([
      sourceCenter.x, sourceCenter.y,
      targetCenter.x, targetCenter.y
    ], {
      stroke: '#dc2626',
      strokeWidth: 3,
      strokeDashArray: [8, 4],
      selectable: false,
      evented: false,
      opacity: 0.7
    });

    this.canvas.add(threatPath);
    this.defenseEffects.push(threatPath);

    // 创建阻断盾牌
    const blockShield = new fabric.Circle({
      left: midPoint.x,
      top: midPoint.y,
      radius: 25,
      fill: '#10b981',
      stroke: '#ffffff',
      strokeWidth: 3,
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0,
      shadow: new fabric.Shadow({
        color: 'rgba(16, 185, 129, 0.5)',
        blur: 10,
        offsetX: 0,
        offsetY: 0
      })
    });

    // 创建阻断图标
    const blockIcon = new fabric.Text('🛡️', {
      left: midPoint.x,
      top: midPoint.y,
      fontSize: 20,
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0
    });

    this.canvas.add(blockShield);
    this.canvas.add(blockIcon);
    this.defenseEffects.push(blockShield, blockIcon);

    // 盾牌出现动画
    blockShield.animate({
      opacity: 1,
      scaleX: 1.2,
      scaleY: 1.2
    }, {
      duration: 400,
      easing: fabric.util.ease.easeOutBack,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => {
        // 图标出现
        blockIcon.animate('opacity', 1, {
          duration: 200,
          onChange: () => this.canvas.renderAll()
        });

        // 创建阻断冲击波
        this.createBlockShockwave(midPoint);
      }
    });

    // 威胁路径被阻断效果
    setTimeout(() => {
      threatPath.animate({
        opacity: 0,
        strokeDashArray: [2, 8]
      }, {
        duration: 800,
        onChange: () => this.canvas.renderAll()
      });
    }, 600);

    // 延迟清理
    setTimeout(() => {
      [threatPath, blockShield, blockIcon].forEach(obj => {
        this.removeDefenseEffect(obj);
      });
    }, 3000);
  }

  /**
   * 创建阻断冲击波
   * @param {Object} center - 中心点 {x, y}
   */
  createBlockShockwave(center) {
    for (let i = 0; i < 3; i++) {
      setTimeout(() => {
        const shockwave = new fabric.Circle({
          left: center.x,
          top: center.y,
          radius: 5,
          fill: 'transparent',
          stroke: '#10b981',
          strokeWidth: 2,
          originX: 'center',
          originY: 'center',
          selectable: false,
          evented: false,
          opacity: 0.8
        });

        this.canvas.add(shockwave);
        this.defenseEffects.push(shockwave);

        shockwave.animate({
          radius: 40 + i * 10,
          opacity: 0
        }, {
          duration: 1000,
          easing: fabric.util.ease.easeOutQuad,
          onChange: () => this.canvas.renderAll(),
          onComplete: () => this.removeDefenseEffect(shockwave)
        });
      }, i * 200);
    }
  }

  /**
   * 创建IP黑名单阻断动画
   * @param {string} maliciousIP - 恶意IP地址
   * @param {fabric.Object} firewallNode - 防火墙节点
   */
  createIPBlacklistAnimation(maliciousIP, firewallNode) {
    console.log('🚫 创建IP黑名单阻断动画:', maliciousIP);

    const center = firewallNode.getCenterPoint();

    // 创建IP地址标签
    const ipLabel = new fabric.Text(maliciousIP, {
      left: center.x,
      top: center.y - 60,
      fontSize: 14,
      fill: '#dc2626',
      fontFamily: 'monospace',
      textAlign: 'center',
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0,
      backgroundColor: 'rgba(220, 38, 38, 0.1)',
      padding: 6
    });

    // 创建禁止图标
    const banIcon = new fabric.Text('🚫', {
      left: center.x + 80,
      top: center.y - 60,
      fontSize: 24,
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0
    });

    // 创建黑名单标签
    const blacklistLabel = new fabric.Text('已加入黑名单', {
      left: center.x,
      top: center.y - 30,
      fontSize: 12,
      fill: '#ffffff',
      textAlign: 'center',
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      padding: 4
    });

    this.canvas.add(ipLabel);
    this.canvas.add(banIcon);
    this.canvas.add(blacklistLabel);
    this.defenseEffects.push(ipLabel, banIcon, blacklistLabel);

    // 动画序列
    ipLabel.animate('opacity', 1, {
      duration: 400,
      onChange: () => this.canvas.renderAll()
    });

    setTimeout(() => {
      banIcon.animate({
        opacity: 1,
        scaleX: 1.3,
        scaleY: 1.3
      }, {
        duration: 300,
        easing: fabric.util.ease.easeOutBack,
        onChange: () => this.canvas.renderAll()
      });
    }, 200);

    setTimeout(() => {
      blacklistLabel.animate('opacity', 1, {
        duration: 400,
        onChange: () => this.canvas.renderAll()
      });
    }, 500);

    // 延迟清理
    setTimeout(() => {
      [ipLabel, banIcon, blacklistLabel].forEach(obj => {
        this.removeDefenseEffect(obj);
      });
    }, 4000);
  }

  /**
   * 创建攻击溯源动画
   * @param {fabric.Object} sourceNode - 源节点（攻击者）
   * @param {fabric.Object} targetNode - 目标节点
   */
  createAttackTracingAnimation(sourceNode, targetNode) {
    console.log('🔍 创建攻击溯源动画');

    const sourceCenter = sourceNode.getCenterPoint();
    const targetCenter = targetNode.getCenterPoint();
    const config = this.config.attackTracing;

    // 创建溯源路径
    const tracePath = new fabric.Line([
      sourceCenter.x, sourceCenter.y,
      targetCenter.x, targetCenter.y
    ], {
      stroke: config.traceColor,
      strokeWidth: config.pathWidth,
      strokeDashArray: [10, 5],
      selectable: false,
      evented: false,
      opacity: 0
    });

    this.canvas.add(tracePath);
    this.defenseEffects.push(tracePath);

    // 创建分析脉冲
    const analysisPulse = new fabric.Circle({
      left: targetCenter.x,
      top: targetCenter.y,
      radius: 5,
      fill: 'transparent',
      stroke: config.traceColor,
      strokeWidth: 2,
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0
    });

    this.canvas.add(analysisPulse);
    this.defenseEffects.push(analysisPulse);

    // 创建溯源标签
    const traceLabel = new fabric.Text('攻击溯源中...', {
      left: (sourceCenter.x + targetCenter.x) / 2,
      top: (sourceCenter.y + targetCenter.y) / 2 - 20,
      fontSize: 12,
      fill: config.traceColor,
      fontWeight: 'bold',
      textAlign: 'center',
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0,
      backgroundColor: 'rgba(245, 158, 11, 0.1)',
      padding: 4
    });

    this.canvas.add(traceLabel);
    this.defenseEffects.push(traceLabel);

    // 路径出现动画
    tracePath.animate('opacity', 0.8, {
      duration: 600,
      onChange: () => this.canvas.renderAll()
    });

    // 标签出现
    setTimeout(() => {
      traceLabel.animate('opacity', 1, {
        duration: 400,
        onChange: () => this.canvas.renderAll()
      });
    }, 300);

    // 分析脉冲动画
    setTimeout(() => {
      analysisPulse.animate({
        opacity: 0.8,
        radius: config.analyzeRadius
      }, {
        duration: 800,
        onChange: () => this.canvas.renderAll(),
        onComplete: () => {
          // 脉冲消失
          analysisPulse.animate({
            opacity: 0,
            radius: config.analyzeRadius + 20
          }, {
            duration: 600,
            onChange: () => this.canvas.renderAll()
          });
        }
      });
    }, 600);

    // 溯源完成
    setTimeout(() => {
      traceLabel.set('text', '溯源完成');
      traceLabel.set('fill', '#10b981');
      this.canvas.renderAll();

      // 延迟清理
      setTimeout(() => {
        [tracePath, analysisPulse, traceLabel].forEach(obj => {
          this.removeDefenseEffect(obj);
        });
      }, 2000);
    }, config.duration);
  }

  /**
   * 创建漏洞修复动画
   * @param {fabric.Object} targetNode - 目标节点
   * @param {string} fixType - 修复类型
   */
  createVulnerabilityFixAnimation(targetNode, fixType = 'vulnerability_fixed') {
    console.log('🔧 创建漏洞修复动画:', fixType);

    const center = targetNode.getCenterPoint();
    const config = this.config.vulnerabilityFix;

    // 创建修复工具图标
    const repairTool = new fabric.Text('🔧', {
      left: center.x - 30,
      top: center.y - 30,
      fontSize: config.toolSize,
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0,
      angle: 0
    });

    // 创建进度圆环
    const progressRing = new fabric.Circle({
      left: center.x,
      top: center.y,
      radius: 25,
      fill: 'transparent',
      stroke: config.repairColor,
      strokeWidth: 4,
      strokeDashArray: [0, 157], // 圆周长约157
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0,
      angle: -90
    });

    // 创建修复标签
    const fixLabel = new fabric.Text('修复中...', {
      left: center.x,
      top: center.y + 45,
      fontSize: 12,
      fill: config.repairColor,
      textAlign: 'center',
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0
    });

    this.canvas.add(repairTool);
    this.canvas.add(progressRing);
    this.canvas.add(fixLabel);
    this.defenseEffects.push(repairTool, progressRing, fixLabel);

    // 工具出现并旋转
    repairTool.animate({
      opacity: 1,
      angle: 360
    }, {
      duration: 800,
      easing: fabric.util.ease.easeOutBack,
      onChange: () => this.canvas.renderAll()
    });

    // 进度环出现
    setTimeout(() => {
      progressRing.animate('opacity', 0.8, {
        duration: 400,
        onChange: () => this.canvas.renderAll()
      });
    }, 200);

    // 标签出现
    setTimeout(() => {
      fixLabel.animate('opacity', 1, {
        duration: 400,
        onChange: () => this.canvas.renderAll()
      });
    }, 400);

    // 进度动画
    setTimeout(() => {
      progressRing.animate('strokeDashArray', [157, 0], {
        duration: config.duration - 1000,
        onChange: () => this.canvas.renderAll(),
        onComplete: () => {
          // 修复完成
          progressRing.set('stroke', config.progressColor);
          fixLabel.set('text', '修复完成');
          fixLabel.set('fill', config.progressColor);
          this.canvas.renderAll();

          // 成功图标
          const successIcon = new fabric.Text('✅', {
            left: center.x + 30,
            top: center.y - 30,
            fontSize: 20,
            originX: 'center',
            originY: 'center',
            selectable: false,
            evented: false,
            opacity: 0
          });

          this.canvas.add(successIcon);
          this.defenseEffects.push(successIcon);

          successIcon.animate({
            opacity: 1,
            scaleX: 1.2,
            scaleY: 1.2
          }, {
            duration: 400,
            easing: fabric.util.ease.easeOutBack,
            onChange: () => this.canvas.renderAll()
          });

          // 延迟清理
          setTimeout(() => {
            [repairTool, progressRing, fixLabel, successIcon].forEach(obj => {
              this.removeDefenseEffect(obj);
            });
          }, 2000);
        }
      });
    }, 800);
  }

  /**
   * 创建防火墙规则更新动画
   * @param {fabric.Object} firewallNode - 防火墙节点
   * @param {string} ruleType - 规则类型
   */
  createFirewallRuleUpdateAnimation(firewallNode, ruleType = 'block_rule') {
    console.log('🔧 创建防火墙规则更新动画:', ruleType);

    const center = firewallNode.getCenterPoint();

    // 创建更新指示器
    const updateIndicator = new fabric.Circle({
      left: center.x,
      top: center.y,
      radius: 30,
      fill: 'transparent',
      stroke: '#3b82f6',
      strokeWidth: 3,
      strokeDashArray: [6, 3],
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0
    });

    // 创建齿轮图标
    const gearIcon = new fabric.Text('⚙️', {
      left: center.x,
      top: center.y,
      fontSize: 24,
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0,
      angle: 0
    });

    // 创建更新标签
    const updateLabel = new fabric.Text('规则更新中...', {
      left: center.x,
      top: center.y + 50,
      fontSize: 12,
      fill: '#3b82f6',
      textAlign: 'center',
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0
    });

    this.canvas.add(updateIndicator);
    this.canvas.add(gearIcon);
    this.canvas.add(updateLabel);
    this.defenseEffects.push(updateIndicator, gearIcon, updateLabel);

    // 指示器出现
    updateIndicator.animate('opacity', 0.8, {
      duration: 400,
      onChange: () => this.canvas.renderAll()
    });

    // 齿轮出现并旋转
    gearIcon.animate('opacity', 1, {
      duration: 300,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => {
        // 持续旋转
        const rotate = () => {
          if (gearIcon.opacity > 0) {
            gearIcon.animate('angle', gearIcon.angle + 360, {
              duration: 1000,
              onChange: () => this.canvas.renderAll(),
              onComplete: rotate
            });
          }
        };
        rotate();
      }
    });

    // 标签出现
    setTimeout(() => {
      updateLabel.animate('opacity', 1, {
        duration: 400,
        onChange: () => this.canvas.renderAll()
      });
    }, 200);

    // 更新完成
    setTimeout(() => {
      updateLabel.set('text', '规则更新完成');
      updateLabel.set('fill', '#10b981');
      this.canvas.renderAll();

      // 延迟清理
      setTimeout(() => {
        [updateIndicator, gearIcon, updateLabel].forEach(obj => {
          this.removeDefenseEffect(obj);
        });
      }, 2000);
    }, 2500);
  }

  /**
   * 移除防御效果
   * @param {fabric.Object} effect - 效果对象
   */
  removeDefenseEffect(effect) {
    if (effect && this.canvas.contains(effect)) {
      this.canvas.remove(effect);
    }
    
    const index = this.defenseEffects.indexOf(effect);
    if (index > -1) {
      this.defenseEffects.splice(index, 1);
    }
  }

  /**
   * 清除所有防御效果
   */
  clearAllEffects() {
    // 停止所有动画
    this.activeDefenseAnimations.forEach(animation => {
      if (animation && typeof animation.cancel === 'function') {
        animation.cancel();
      }
    });
    this.activeDefenseAnimations = [];

    // 停止所有连续动画
    this.continuousDefenseAnimations.forEach((value, key) => {
      if (typeof value === 'number') {
        clearTimeout(value);
        clearInterval(value);
      }
    });
    this.continuousDefenseAnimations.clear();

    // 移除所有效果对象
    this.defenseEffects.forEach(effect => {
      if (this.canvas.contains(effect)) {
        this.canvas.remove(effect);
      }
    });
    this.defenseEffects = [];

    this.canvas.renderAll();
  }
}

export default FabricDefenseVisualization;