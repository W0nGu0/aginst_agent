<template>
  <div class="attacker-dialog">
    <div v-if="show" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content" ref="dialogContent" @click.stop>
        <div class="dialog-header" @mousedown="startDrag">
          <h3>攻击控制面板</h3>
          <button class="close-btn" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="attack-info-section">
            <div class="attack-info-icon">
              <i class="fas fa-robot"></i>
            </div>
            <div class="attack-info-text">
              <p>点击下方按钮启动自动攻击</p>
              <p class="attack-info-detail">系统将自动分析网络拓扑并执行最优攻击路径</p>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button 
            class="btn btn-danger"
            @click="launchAttack"
          >
            <i class="fas fa-skull"></i> 发起攻击
          </button>
          <button class="btn btn-secondary" @click="closeDialog">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AttackerDialog',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    attacker: {
      type: Object,
      default: () => ({})
    },
    targets: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      // 拖动相关状态
      isDragging: false,
      dragOffset: { x: 0, y: 0 },
      position: { x: 0, y: 0 }
    };
  },
  computed: {
    availableTargets() {
      return this.targets.map(target => ({
        id: target.id,
        name: target.deviceData.name,
        ip: target.deviceData.ip,
        type: target.deviceType
      }));
    }
  },
  mounted() {
    // 添加全局鼠标事件监听
    document.addEventListener('mousemove', this.onMouseMove);
    document.addEventListener('mouseup', this.onMouseUp);
  },
  beforeUnmount() {
    // 移除全局鼠标事件监听
    document.removeEventListener('mousemove', this.onMouseMove);
    document.removeEventListener('mouseup', this.onMouseUp);
  },
  methods: {
    // 开始拖动
    startDrag(event) {
      if (event.target.classList.contains('close-btn')) return;
      
      this.isDragging = true;
      const dialogRect = this.$refs.dialogContent.getBoundingClientRect();
      
      this.dragOffset = {
        x: event.clientX - dialogRect.left,
        y: event.clientY - dialogRect.top
      };
      
      // 设置初始位置
      if (this.position.x === 0 && this.position.y === 0) {
        this.position = {
          x: dialogRect.left,
          y: dialogRect.top
        };
      }
      
      // 添加拖动中的样式
      this.$refs.dialogContent.style.transition = 'none';
      this.$refs.dialogContent.style.cursor = 'grabbing';
    },
    
    // 拖动中
    onMouseMove(event) {
      if (!this.isDragging) return;
      
      // 计算新位置
      this.position = {
        x: event.clientX - this.dragOffset.x,
        y: event.clientY - this.dragOffset.y
      };
      
      // 应用新位置
      this.applyPosition();
    },
    
    // 结束拖动
    onMouseUp() {
      if (!this.isDragging) return;
      
      this.isDragging = false;
      
      // 恢复样式
      if (this.$refs.dialogContent) {
        this.$refs.dialogContent.style.transition = '';
        this.$refs.dialogContent.style.cursor = '';
      }
    },
    
    // 应用位置
    applyPosition() {
      if (!this.$refs.dialogContent) return;
      
      // 获取窗口尺寸
      const windowWidth = window.innerWidth;
      const windowHeight = window.innerHeight;
      const dialogRect = this.$refs.dialogContent.getBoundingClientRect();
      
      // 确保对话框不会超出窗口边界
      let x = this.position.x;
      let y = this.position.y;
      
      // 限制左右边界
      if (x < 0) x = 0;
      if (x + dialogRect.width > windowWidth) x = windowWidth - dialogRect.width;
      
      // 限制上下边界
      if (y < 0) y = 0;
      if (y + dialogRect.height > windowHeight) y = windowHeight - dialogRect.height;
      
      // 更新位置
      this.position = { x, y };
      
      // 应用样式
      this.$refs.dialogContent.style.position = 'fixed';
      this.$refs.dialogContent.style.left = `${x}px`;
      this.$refs.dialogContent.style.top = `${y}px`;
      this.$refs.dialogContent.style.margin = '0';
      this.$refs.dialogContent.style.transform = 'none';
    },
    
    // 发起攻击
    launchAttack() {
      // 发送自动攻击指令
      this.$emit('attack', {
        attacker: this.attacker,
        target: null, // 自动选择目标
        attackType: 'auto', // 自动攻击类型
        attackName: '自动攻击'
      });
      
      this.closeDialog();
    },
    
    closeDialog() {
      this.$emit('close');
    },
    getDeviceIcon(type) {
      const iconMap = {
        'router': '/图标/路由器.svg',
        'firewall': '/图标/防火墙.svg',
        'switch': '/图标/交换机.svg',
        'server': '/图标/服务器.svg',
        'pc': '/图标/pc.svg',
        'db': '/图标/数据库服务器.svg',
        'web': '/图标/Web服务器.svg',
        'app': '/图标/应用服务器.svg',
        'file': '/图标/文件服务器.svg',
        'mail': '/图标/邮件服务器.svg',
        'vpn': '/图标/VPN.svg',
        'dns': '/图标/DNS服务器.svg',
        'proxy': '/图标/代理服务器.svg',
        'load': '/图标/负载均衡.svg'
      };

      return iconMap[type] || '';
    }
  }
};
</script>

<style scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dialog-content {
  background-color: #1e1e2f;
  border-radius: 8px;
  width: 600px;
  max-width: 90%;
  max-height: 90%;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
}

.dialog-header {
  padding: 16px;
  border-bottom: 1px solid #2c2c40;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-header h3 {
  margin: 0;
  color: #ffffff;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #ffffff;
  cursor: pointer;
}

.dialog-body {
  padding: 16px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dialog-footer {
  padding: 16px;
  border-top: 1px solid #2c2c40;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.attack-info-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  text-align: center;
  background-color: #27293d;
  border-radius: 8px;
}

.attack-info-icon {
  font-size: 48px;
  color: #f5365c;
  margin-bottom: 16px;
}

.attack-info-text p {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #ffffff;
}

.attack-info-detail {
  font-size: 14px;
  color: #a9a9a9;
}

.dialog-header {
  cursor: grab;
}

.dialog-header:active {
  cursor: grabbing;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: bold;
}

.btn-danger {
  background-color: #f5365c;
  color: white;
}

.btn-danger:hover {
  background-color: #f3547d;
}

.btn-danger:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}
</style>