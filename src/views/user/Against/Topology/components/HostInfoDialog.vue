<template>
  <div class="host-info-dialog">
    <div v-if="show" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content" ref="dialogContent" @click.stop>
        <div class="dialog-header" @mousedown="startDrag">
          <h3>主机信息</h3>
          <button class="close-btn" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="host-info">
            <div class="info-section">
              <h4>基本信息</h4>
              <div class="info-grid">
                <div class="info-item">
                  <div class="info-label">主机名</div>
                  <div class="info-value">{{ host.deviceData?.name }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">IP地址</div>
                  <div class="info-value">{{ host.deviceData?.ip }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">MAC地址</div>
                  <div class="info-value">{{ host.deviceData?.mac }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">状态</div>
                  <div class="info-value" :class="statusClass">{{ statusText }}</div>
                </div>
              </div>
            </div>
            <div class="info-section">
              <h4>用户信息</h4>
              <div class="info-grid">
                <div class="info-item">
                  <div class="info-label">用户名</div>
                  <div class="info-value">{{ hostInfo.username || '未知' }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">公司</div>
                  <div class="info-value">{{ hostInfo.company || '未知' }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">部门</div>
                  <div class="info-value">{{ hostInfo.department || '未知' }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">职位</div>
                  <div class="info-value">{{ hostInfo.role || '未知' }}</div>
                </div>
              </div>
            </div>
            <div class="info-section">
              <h4>系统信息</h4>
              <div class="info-grid">
                <div class="info-item">
                  <div class="info-label">操作系统</div>
                  <div class="info-value">{{ hostInfo.os || '未知' }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">内核版本</div>
                  <div class="info-value">{{ hostInfo.kernel || '未知' }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">开放端口</div>
                  <div class="info-value">{{ hostInfo.openPorts?.join(', ') || '未知' }}</div>
                </div>
                <div class="info-item">
                  <div class="info-label">运行服务</div>
                  <div class="info-value">{{ hostInfo.services?.join(', ') || '未知' }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-primary" @click="refreshInfo">刷新信息</button>
          <button class="btn btn-secondary" @click="closeDialog">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import HostInfoService from '../services/HostInfoService';

export default {
  name: 'HostInfoDialog',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    host: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      hostInfo: {},
      // 拖动相关状态
      isDragging: false,
      dragOffset: { x: 0, y: 0 },
      position: { x: 0, y: 0 }
    };
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
  computed: {
    statusText() {
      if (!this.host.deviceData) return '未知';
      return this.host.deviceData.status === 'running' ? '运行中' : 
             this.host.deviceData.status === 'failed' ? '失败' : '已停止';
    },
    statusClass() {
      if (!this.host.deviceData) return '';
      return this.host.deviceData.status === 'running' ? 'status-running' : 
             this.host.deviceData.status === 'failed' ? 'status-failed' : 'status-stopped';
    }
  },
  watch: {
    host: {
      immediate: true,
      handler(newVal) {
        if (newVal && newVal.id) {
          this.loadHostInfo();
        }
      }
    },
    show(newVal) {
      if (newVal) {
        this.loadHostInfo();
      }
    }
  },
  methods: {
    async loadHostInfo() {
      try {
        // 使用HostInfoService获取主机信息
        this.hostInfo = await HostInfoService.getHostInfo(this.host);
      } catch (error) {
        console.error('加载主机信息失败:', error);
        this.hostInfo = {};
      }
    },
    refreshInfo() {
      this.loadHostInfo();
    },
    closeDialog() {
      this.$emit('close');
    },
    
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
.host-info {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.info-section {
  border-radius: 8px;
  background-color: #27293d;
  padding: 16px;
}
.info-section h4 {
  margin: 0 0 12px 0;
  color: #ffffff;
  font-size: 16px;
  border-bottom: 1px solid #2c2c40;
  padding-bottom: 8px;
}
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.info-label {
  color: #a9a9a9;
  font-size: 12px;
}
.info-value {
  color: #ffffff;
  font-size: 14px;
}
.status-running {
  color: #00f2c3;
}
.status-failed {
  color: #fd5d93;
}
.status-stopped {
  color: #fd5d93;
}
.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: bold;
}
.btn-primary {
  background-color: #1d8cf8;
  color: white;
}
.btn-primary:hover {
  background-color: #3a9cfa;
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.btn-secondary:hover {
  background-color: #5a6268;
}
</style>