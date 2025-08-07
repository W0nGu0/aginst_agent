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
   * 创建威胁阻断动画
   * @param {fabric.Object} targetNode - 目标节点
   * @param {string} threatType - 威胁类型
   */
  createThreatBlockingAnimation(targetNode, threatType = 'malicious_ip') {
    const config = this.config.threatBlocking;
    const center = targetNode.getCenterPoint();

    // 创建现代化的防护盾牌 - 使用更美观的SVG路径
    const shield = new fabric.Path(
      'M12 2L4 7V13C4 19.08 7.05 24.68 12 26C16.95 24.68 20 19.08 20 13V7L12 2Z',
      {
        left: center.x,
        top: center.y - 60, // 提高位置避免与名称重叠
        fill: config.shieldColor,
        stroke: '#ffffff',
        strokeWidth: 1.5,
        scaleX: 2,
        scaleY: 2,
        originX: 'center',
        originY: 'center',
        selectable: false,
        evented: false,
        opacity: 0,
        shadow: new fabric.Shadow({
          color: 'rgba(16, 185, 129, 0.4)',
          blur: 8,
          offsetX: 0,
          offsetY: 2
        })
      }
    );

    this.canvas.add(shield);
    this.defenseEffects.push(shield);

    // 盾牌出现动画
    const shieldAnimation = shield.animate({
      opacity: 1,
      scaleX: 2,
      scaleY: 2
    }, {
      duration: 500,
      easing: fabric.util.ease.easeOutBack,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => {
        // 创建阻断效果
        this.createBlockEffect(center, threatType);
        
        // 延迟移除盾牌
        setTimeout(() => {
          const fadeOut = shield.animate({
            opacity: 0,
            scaleX: 1,
            scaleY: 1
          }, {
            duration: 500,
            onChange: () => this.canvas.renderAll(),
            onComplete: () => this.removeDefenseEffect(shield)
          });
          this.activeDefenseAnimations.push(fadeOut);
        }, 2000);
      }
    });

    this.activeDefenseAnimations.push(shieldAnimation);

    // 添加阻断文字 - 放在节点上方
    const blockText = new fabric.Text(`🛡️ 威胁已阻断`, {
      left: center.x,
      top: center.y - 90, // 放在节点上方
      fontSize: 16,
      fill: config.shieldColor,
      fontWeight: 'bold',
      textAlign: 'center',
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      padding: 8,
      cornerStyle: 'round',
      cornerSize: 4
    });

    this.canvas.add(blockText);
    this.defenseEffects.push(blockText);

    // 文字动画
    const textAnimation = blockText.animate({ opacity: 1 }, {
      duration: 300,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => {
        setTimeout(() => {
          const textFadeOut = blockText.animate({ opacity: 0 }, {
            duration: 500,
            onChange: () => this.canvas.renderAll(),
            onComplete: () => this.removeDefenseEffect(blockText)
          });
          this.activeDefenseAnimations.push(textFadeOut);
        }, 2000);
      }
    });

    this.activeDefenseAnimations.push(textAnimation);
  }

  /**
   * 创建阻断效果
   * @param {Object} center - 中心点坐标
   * @param {string} threatType - 威胁类型
   */
  createBlockEffect(center, threatType) {
    const config = this.config.threatBlocking;

    // 创建现代化的阻断标志 - 使用圆形背景
    const blockBg = new fabric.Circle({
      left: center.x + 40,
      top: center.y - 40,
      radius: 18,
      fill: '#dc2626',
      stroke: '#ffffff',
      strokeWidth: 2,
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0,
      shadow: new fabric.Shadow({
        color: 'rgba(220, 38, 38, 0.4)',
        blur: 6,
        offsetX: 0,
        offsetY: 2
      })
    });

    const blockSymbol = new fabric.Text('✕', {
      left: center.x + 40,
      top: center.y - 40,
      fontSize: 20,
      fill: '#ffffff',
      fontWeight: 'bold',
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0
    });

    this.canvas.add(blockBg);
    this.canvas.add(blockSymbol);
    this.defenseEffects.push(blockBg, blockSymbol);

    // 背景和符号同时出现动画
    const bgAnimation = blockBg.animate({
      opacity: 0.9,
      scaleX: 1.2,
      scaleY: 1.2
    }, {
      duration: 400,
      easing: fabric.util.ease.easeOutBack,
      onChange: () => this.canvas.renderAll()
    });

    const symbolAnimation = blockSymbol.animate({
      opacity: 1,
      scaleX: 1.1,
      scaleY: 1.1
    }, {
      duration: 400,
      easing: fabric.util.ease.easeOutBack,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => {
        setTimeout(() => {
          const bgFadeOut = blockBg.animate({
            opacity: 0,
            scaleX: 1,
            scaleY: 1
          }, {
            duration: 600,
            onChange: () => this.canvas.renderAll(),
            onComplete: () => this.removeDefenseEffect(blockBg)
          });
          
          const symbolFadeOut = blockSymbol.animate({
            opacity: 0,
            scaleX: 1,
            scaleY: 1
          }, {
            duration: 600,
            onChange: () => this.canvas.renderAll(),
            onComplete: () => this.removeDefenseEffect(blockSymbol)
          });
          
          this.activeDefenseAnimations.push(bgFadeOut, symbolFadeOut);
        }, 2000);
      }
    });

    this.activeDefenseAnimations.push(symbolAnimation);
  }

  /**
   * 创建漏洞修复动画
   * @param {fabric.Object} targetNode - 目标节点
   * @param {string} vulnerabilityType - 漏洞类型
   */
  createVulnerabilityFixAnimation(targetNode, vulnerabilityType = 'security_patch') {
    const config = this.config.vulnerabilityFix;
    const center = targetNode.getCenterPoint();

    // 恢复节点正常状态（移除攻陷效果）
    this.restoreNodeToNormalState(targetNode);

    // 创建修复工具图标 - 放在节点上方
    const repairTool = new fabric.Text('🔧', {
      left: center.x,
      top: center.y - 70, // 提高位置
      fontSize: config.toolSize + 4,
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0,
      angle: 0,
      shadow: new fabric.Shadow({
        color: 'rgba(59, 130, 246, 0.4)',
        blur: 6,
        offsetX: 0,
        offsetY: 2
      })
    });

    this.canvas.add(repairTool);
    this.defenseEffects.push(repairTool);

    // 工具出现和旋转动画
    const toolAnimation = repairTool.animate({
      opacity: 1,
      angle: 360
    }, {
      duration: 1000,
      easing: fabric.util.ease.easeInOutQuad,
      onChange: () => this.canvas.renderAll()
    });

    this.activeDefenseAnimations.push(toolAnimation);

    // 创建修复进度条
    this.createRepairProgressBar(center, config);

    // 添加修复文字 - 放在节点上方
    const repairText = new fabric.Text('🔒 系统加固中...', {
      left: center.x,
      top: center.y - 100, // 放在节点上方
      fontSize: 14,
      fill: config.repairColor,
      fontWeight: 'bold',
      textAlign: 'center',
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      padding: 6,
      cornerStyle: 'round',
      cornerSize: 4
    });

    this.canvas.add(repairText);
    this.defenseEffects.push(repairText);

    // 文字动画
    const textAnimation = repairText.animate({ opacity: 1 }, {
      duration: 300,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => {
        // 修复完成后更新文字
        setTimeout(() => {
          repairText.set({ text: '✅ 修复完成', fill: config.progressColor });
          this.canvas.renderAll();
          
          // 延迟移除所有效果
          setTimeout(() => {
            this.removeDefenseEffect(repairTool);
            this.removeDefenseEffect(repairText);
          }, 1500);
        }, 2000);
      }
    });

    this.activeDefenseAnimations.push(textAnimation);
  }

  /**
   * 创建修复进度条
   * @param {Object} center - 中心点坐标
   * @param {Object} config - 配置对象
   */
  createRepairProgressBar(center, config) {
    // 进度条背景 - 放在节点上方
    const progressBg = new fabric.Rect({
      left: center.x - 50,
      top: center.y - 45, // 放在节点上方
      width: 100,
      height: 8,
      fill: '#374151',
      rx: 4,
      ry: 4,
      selectable: false,
      evented: false,
      stroke: '#6b7280',
      strokeWidth: 1
    });

    // 进度条前景
    const progressFg = new fabric.Rect({
      left: center.x - 50,
      top: center.y - 45,
      width: 0,
      height: 8,
      fill: config.progressColor,
      rx: 4,
      ry: 4,
      selectable: false,
      evented: false,
      shadow: new fabric.Shadow({
        color: 'rgba(34, 197, 94, 0.4)',
        blur: 4,
        offsetX: 0,
        offsetY: 1
      })
    });

    this.canvas.add(progressBg);
    this.canvas.add(progressFg);
    this.defenseEffects.push(progressBg, progressFg);

    // 进度条动画 - 更流畅的进度效果
    const progressAnimation = progressFg.animate({ width: 100 }, {
      duration: 2500,
      easing: fabric.util.ease.easeInOutQuad,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => {
        // 进度完成后闪烁效果
        let flashCount = 0;
        const flashInterval = setInterval(() => {
          progressFg.set({ opacity: flashCount % 2 === 0 ? 1 : 0.3 });
          this.canvas.renderAll();
          flashCount++;
          if (flashCount >= 4) {
            clearInterval(flashInterval);
            setTimeout(() => {
              this.removeDefenseEffect(progressBg);
              this.removeDefenseEffect(progressFg);
            }, 500);
          }
        }, 200);
      }
    });

    this.activeDefenseAnimations.push(progressAnimation);
  }

  /**
   * 创建攻击溯源动画
   * @param {fabric.Object} sourceNode - 源节点
   * @param {fabric.Object} targetNode - 目标节点
   * @param {Array} attackPath - 攻击路径
   */
  createAttackTracingAnimation(sourceNode, targetNode, attackPath = []) {
    const config = this.config.attackTracing;

    // 创建溯源分析图标
    const analyzeIcon = new fabric.Text('🔍', {
      left: targetNode.getCenterPoint().x,
      top: targetNode.getCenterPoint().y - 40,
      fontSize: 24,
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0
    });

    this.canvas.add(analyzeIcon);
    this.defenseEffects.push(analyzeIcon);

    // 分析图标动画
    const iconAnimation = analyzeIcon.animate({
      opacity: 1,
      fontSize: 32
    }, {
      duration: 500,
      easing: fabric.util.ease.easeOutBack,
      onChange: () => this.canvas.renderAll()
    });

    this.activeDefenseAnimations.push(iconAnimation);

    // 创建溯源路径
    if (sourceNode && targetNode) {
      this.createTracePath(sourceNode, targetNode, config);
    }

    // 添加溯源文字
    const traceText = new fabric.Text('🎯 攻击溯源中...', {
      left: targetNode.getCenterPoint().x,
      top: targetNode.getCenterPoint().y + 50,
      fontSize: 12,
      fill: config.traceColor,
      fontWeight: 'bold',
      textAlign: 'center',
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0
    });

    this.canvas.add(traceText);
    this.defenseEffects.push(traceText);

    // 文字动画
    const textAnimation = traceText.animate({ opacity: 1 }, {
      duration: 300,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => {
        // 溯源完成后更新文字
        setTimeout(() => {
          traceText.set({ text: '📍 溯源完成', fill: '#22c55e' });
          this.canvas.renderAll();
          
          // 延迟移除效果
          setTimeout(() => {
            this.removeDefenseEffect(analyzeIcon);
            this.removeDefenseEffect(traceText);
          }, 2000);
        }, 1500);
      }
    });

    this.activeDefenseAnimations.push(textAnimation);
  }

  /**
   * 创建溯源路径
   * @param {fabric.Object} sourceNode - 源节点
   * @param {fabric.Object} targetNode - 目标节点
   * @param {Object} config - 配置对象
   */
  createTracePath(sourceNode, targetNode, config) {
    const sourceCenter = sourceNode.getCenterPoint();
    const targetCenter = targetNode.getCenterPoint();

    // 创建溯源路径线
    const traceLine = new fabric.Line([
      targetCenter.x, targetCenter.y,
      targetCenter.x, targetCenter.y
    ], {
      stroke: config.traceColor,
      strokeWidth: config.pathWidth,
      strokeDashArray: [8, 4],
      selectable: false,
      evented: false,
      opacity: 0.8
    });

    this.canvas.add(traceLine);
    this.defenseEffects.push(traceLine);

    // 路径动画
    const pathAnimation = traceLine.animate({
      x2: sourceCenter.x,
      y2: sourceCenter.y
    }, {
      duration: config.duration,
      easing: fabric.util.ease.easeInOutQuad,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => {
        // 在源节点显示攻击者标记
        this.markAttackerSource(sourceNode);
        
        // 延迟移除路径
        setTimeout(() => {
          this.removeDefenseEffect(traceLine);
        }, 2000);
      }
    });

    this.activeDefenseAnimations.push(pathAnimation);
  }

  /**
   * 标记攻击者来源
   * @param {fabric.Object} sourceNode - 源节点
   */
  markAttackerSource(sourceNode) {
    const center = sourceNode.getCenterPoint();

    // 创建攻击者标记
    const attackerMark = new fabric.Text('⚠️', {
      left: center.x + 25,
      top: center.y - 25,
      fontSize: 20,
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0
    });

    this.canvas.add(attackerMark);
    this.defenseEffects.push(attackerMark);

    // 标记动画
    const markAnimation = attackerMark.animate({
      opacity: 1,
      fontSize: 24
    }, {
      duration: 300,
      easing: fabric.util.ease.easeOutBounce,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => {
        // 持续显示一段时间后移除
        setTimeout(() => {
          const fadeOut = attackerMark.animate({ opacity: 0 }, {
            duration: 500,
            onChange: () => this.canvas.renderAll(),
            onComplete: () => this.removeDefenseEffect(attackerMark)
          });
          this.activeDefenseAnimations.push(fadeOut);
        }, 3000);
      }
    });

    this.activeDefenseAnimations.push(markAnimation);
  }

  /**
   * 创建防火墙更新动画
   * @param {fabric.Object} firewallNode - 防火墙节点
   * @param {string} updateType - 更新类型
   */
  createFirewallUpdateAnimation(firewallNode, updateType = 'rule_update') {
    const config = this.config.firewallUpdate;
    const center = firewallNode.getCenterPoint();

    // 创建更新指示器
    const updateIndicator = new fabric.Circle({
      left: center.x,
      top: center.y,
      radius: 5,
      fill: config.updateColor,
      stroke: '#ffffff',
      strokeWidth: 2,
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0.8
    });

    this.canvas.add(updateIndicator);
    this.defenseEffects.push(updateIndicator);

    // 更新动画
    const updateAnimation = updateIndicator.animate({
      radius: 30,
      opacity: 0
    }, {
      duration: config.duration,
      easing: fabric.util.ease.easeOutQuad,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => this.removeDefenseEffect(updateIndicator)
    });

    this.activeDefenseAnimations.push(updateAnimation);

    // 添加更新文字
    const updateText = new fabric.Text('🔄 防火墙规则更新', {
      left: center.x,
      top: center.y - 50,
      fontSize: 12,
      fill: config.updateColor,
      fontWeight: 'bold',
      textAlign: 'center',
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0
    });

    this.canvas.add(updateText);
    this.defenseEffects.push(updateText);

    // 文字动画
    const textAnimation = updateText.animate({ opacity: 1 }, {
      duration: 300,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => {
        setTimeout(() => {
          const textFadeOut = updateText.animate({ opacity: 0 }, {
            duration: 500,
            onChange: () => this.canvas.renderAll(),
            onComplete: () => this.removeDefenseEffect(updateText)
          });
          this.activeDefenseAnimations.push(textFadeOut);
        }, 1500);
      }
    });

    this.activeDefenseAnimations.push(textAnimation);
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
  clearAllDefenseEffects() {
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

  /**
   * 根据防御日志触发对应动画
   * @param {Object} logEntry - 日志条目
   * @param {fabric.Object} targetNode - 目标节点
   */
  triggerDefenseAnimationFromLog(logEntry, targetNode) {
    const { level, source, message } = logEntry;

    if (source.includes('威胁阻断') || message.includes('阻断') || message.includes('封锁')) {
      this.createThreatBlockingAnimation(targetNode, 'threat_blocked');
    } else if (source.includes('漏洞修复') || message.includes('修复') || message.includes('补丁')) {
      this.createVulnerabilityFixAnimation(targetNode, 'vulnerability_fixed');
    } else if (source.includes('攻击溯源') || message.includes('溯源') || message.includes('分析')) {
      // 需要找到攻击源节点
      const sourceNode = this.findNodeByType('internet') || targetNode;
      this.createAttackTracingAnimation(sourceNode, targetNode);
    } else if (message.includes('防火墙') || message.includes('规则')) {
      const firewallNode = this.findNodeByType('firewall') || targetNode;
      this.createFirewallUpdateAnimation(firewallNode, 'rule_update');
    }
  }

  /**
   * 恢复节点到正常状态
   * @param {fabric.Object} targetNode - 目标节点
   */
  restoreNodeToNormalState(targetNode) {
    if (!targetNode) return;

    // 移除攻陷状态的视觉效果
    targetNode.set({
      stroke: '#ffffff',
      strokeWidth: 1,
      strokeDashArray: null,
      opacity: 1.0
    });

    // 移除红色脉冲动画
    if (targetNode._pulseAnimation) {
      targetNode._pulseAnimation.cancel();
      delete targetNode._pulseAnimation;
    }

    // 添加绿色恢复脉冲效果
    this.createRecoveryPulse(targetNode);

    this.canvas.renderAll();
  }

  /**
   * 创建恢复脉冲效果
   * @param {fabric.Object} targetNode - 目标节点
   */
  createRecoveryPulse(targetNode) {
    const center = targetNode.getCenterPoint();
    
    // 创建绿色脉冲圆圈
    const pulse = new fabric.Circle({
      left: center.x,
      top: center.y,
      radius: 5,
      fill: 'transparent',
      stroke: '#22c55e',
      strokeWidth: 3,
      originX: 'center',
      originY: 'center',
      selectable: false,
      evented: false,
      opacity: 0.8
    });

    this.canvas.add(pulse);
    this.defenseEffects.push(pulse);

    // 脉冲动画
    const pulseAnimation = pulse.animate({
      radius: 40,
      opacity: 0
    }, {
      duration: 1500,
      easing: fabric.util.ease.easeOutQuad,
      onChange: () => this.canvas.renderAll(),
      onComplete: () => this.removeDefenseEffect(pulse)
    });

    this.activeDefenseAnimations.push(pulseAnimation);
  }

  /**
   * 根据类型查找节点
   * @param {string} nodeType - 节点类型
   * @returns {fabric.Object|null} - 找到的节点
   */
  findNodeByType(nodeType) {
    const objects = this.canvas.getObjects();
    return objects.find(obj => 
      obj.type === 'device' && 
      (obj.deviceType === nodeType || obj.nodeData?.type === nodeType)
    ) || null;
  }
}

export default FabricDefenseVisualization;