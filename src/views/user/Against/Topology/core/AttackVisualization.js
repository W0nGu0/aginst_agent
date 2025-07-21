/**
 * 攻击可视化类
 * 负责在拓扑图上可视化攻击过程
 */
import { fabric } from 'fabric';

class AttackVisualization {
  constructor(topology) {
    this.topology = topology;
    this.canvas = topology.canvas;
    this.animations = [];
    this.attackPaths = [];
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
      const animation = this._createAttackAnimation(path, attackType);
      
      // 启动动画
      animation.start();
      
      // 动画完成后返回
      animation.onComplete = () => {
        resolve();
      };
    });
  }

  /**
   * 清除所有攻击路径可视化
   */
  clearAttackPaths() {
    // 停止所有动画
    this.animations.forEach(animation => {
      if (animation.stop) {
        animation.stop();
      }
    });
    this.animations = [];
    
    // 移除所有攻击路径
    this.attackPaths.forEach(path => {
      this.canvas.remove(path);
    });
    this.attackPaths = [];
    
    // 重新渲染画布
    this.canvas.requestRenderAll();
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
      'ddos': '#9b59b6'        // 紫色
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
        selectable: false
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
   * @returns {Object} - 返回动画对象
   */
  _createAttackAnimation(path, attackType) {
    // 创建动画对象
    const animation = {
      path: path,
      packets: [],
      running: false,
      
      // 开始动画
      start: () => {
        animation.running = true;
        animation._animate();
      },
      
      // 停止动画
      stop: () => {
        animation.running = false;
        animation.packets.forEach(packet => {
          this.canvas.remove(packet);
        });
        animation.packets = [];
        this.canvas.requestRenderAll();
      },
      
      // 动画循环
      _animate: () => {
        if (!animation.running) return;
        
        // 创建新的数据包
        animation._createPacket();
        
        // 移动现有数据包
        animation._movePackets();
        
        // 移除超出路径的数据包
        animation._removeOutOfBoundsPackets();
        
        // 重新渲染画布
        this.canvas.requestRenderAll();
        
        // 继续动画循环
        requestAnimationFrame(animation._animate);
      },
      
      // 创建数据包
      _createPacket: () => {
        // 根据攻击类型决定创建频率
        const packetFrequency = {
          'port_scan': 0.1,    // 10%几率
          'brute_force': 0.05, // 5%几率
          'exploit': 0.02,     // 2%几率
          'ddos': 0.3          // 30%几率
        };
        
        const frequency = packetFrequency[attackType] || 0.1;
        
        // 随机决定是否创建新数据包
        if (Math.random() > frequency) return;
        
        // 根据攻击类型选择颜色和大小
        const colors = {
          'port_scan': '#3498db',  // 蓝色
          'brute_force': '#f39c12', // 橙色
          'exploit': '#e74c3c',    // 红色
          'ddos': '#9b59b6'        // 紫色
        };
        const color = colors[attackType] || '#3498db';
        
        const sizes = {
          'port_scan': 4,
          'brute_force': 5,
          'exploit': 6,
          'ddos': 3
        };
        const size = sizes[attackType] || 4;
        
        // 创建数据包（圆形）
        const packet = new fabric.Circle({
          left: path[0].left,
          top: path[0].top,
          radius: size,
          fill: color,
          stroke: 'rgba(255, 255, 255, 0.5)',
          strokeWidth: 1,
          selectable: false,
          originX: 'center',
          originY: 'center',
          // 添加动画数据
          animationData: {
            pathIndex: 0,
            progress: 0,
            speed: Math.random() * 0.01 + 0.01 // 随机速度
          }
        });
        
        // 添加到画布
        this.canvas.add(packet);
        
        // 保存数据包引用
        animation.packets.push(packet);
      },
      
      // 移动数据包
      _movePackets: () => {
        animation.packets.forEach(packet => {
          const data = packet.animationData;
          
          // 如果已经到达路径末尾，不再移动
          if (data.pathIndex >= path.length - 1) return;
          
          // 获取当前路径段的起点和终点
          const source = path[data.pathIndex];
          const target = path[data.pathIndex + 1];
          
          // 更新进度
          data.progress += data.speed;
          
          // 如果到达当前路径段终点
          if (data.progress >= 1) {
            data.pathIndex++;
            data.progress = 0;
            
            // 如果到达路径末尾，不再移动
            if (data.pathIndex >= path.length - 1) return;
          }
          
          // 计算当前位置
          const currentSource = path[data.pathIndex];
          const currentTarget = path[data.pathIndex + 1];
          
          packet.set({
            left: currentSource.left + (currentTarget.left - currentSource.left) * data.progress,
            top: currentSource.top + (currentTarget.top - currentSource.top) * data.progress
          });
        });
      },
      
      // 移除超出路径的数据包
      _removeOutOfBoundsPackets: () => {
        const packetsToRemove = [];
        
        animation.packets.forEach(packet => {
          const data = packet.animationData;
          
          // 如果数据包到达目标，标记为移除
          if (data.pathIndex >= path.length - 1 && data.progress >= 1) {
            packetsToRemove.push(packet);
          }
        });
        
        // 移除数据包
        packetsToRemove.forEach(packet => {
          this.canvas.remove(packet);
          animation.packets = animation.packets.filter(p => p !== packet);
        });
      },
      
      // 动画完成回调
      onComplete: null
    };
    
    // 保存动画引用
    this.animations.push(animation);
    
    return animation;
  }
}

export default AttackVisualization;