<template>
  <div class="container-config-dialog">
    <div v-if="show" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content" ref="dialogContent" @click.stop>
        <div class="dialog-header" @mousedown="startDrag">
          <h3>容器配置 - {{ container.deviceData?.name || '未知容器' }}</h3>
          <button class="close-btn" @click="closeDialog">&times;</button>
        </div>

        <div class="dialog-body">
          <!-- 容器基本信息 -->
          <div class="container-info">
            <div class="info-item">
              <span class="label">容器ID:</span>
              <span class="value">{{ containerInfo.id || '未知' }}</span>
            </div>
            <div class="info-item">
              <span class="label">状态:</span>
              <span class="value" :class="statusClass">{{ statusText }}</span>
            </div>
            <div class="info-item">
              <span class="label">IP地址:</span>
              <span class="value">{{ containerInfo.ip || container.deviceData?.ip || '未知' }}</span>
            </div>
          </div>

          <!-- 标签页导航 -->
          <div class="tabs">
            <div class="tab" :class="{ active: activeTab === 'network' }" @click="activeTab = 'network'">
              🌐 网络配置
            </div>
            <div class="tab" :class="{ active: activeTab === 'firewall' }" @click="activeTab = 'firewall'">
              🔥 防火墙规则
            </div>
            <div class="tab" :class="{ active: activeTab === 'services' }" @click="activeTab = 'services'">
              ⚙️ 服务管理
            </div>
            <div class="tab" :class="{ active: activeTab === 'debug' }" @click="activeTab = 'debug'">
              🐛 调试
            </div>
          </div>

          <!-- 标签页内容 -->
          <div class="tab-content">
            <!-- 调试信息 -->
            <div v-if="activeTab === 'debug'" class="debug-info">
              <h4>调试信息</h4>
              <div class="debug-section">
                <h5>容器对象 (container):</h5>
                <pre>{{ JSON.stringify(container, null, 2) }}</pre>
              </div>
              <div class="debug-section">
                <h5>容器信息 (containerInfo):</h5>
                <pre>{{ JSON.stringify(containerInfo, null, 2) }}</pre>
              </div>
              <div class="debug-section">
                <h5>当前标签页:</h5>
                <pre>{{ activeTab }}</pre>
              </div>
              <div class="debug-actions">
                <button class="btn btn-sm btn-primary" @click="loadContainerInfo">🔄 重新加载数据</button>
                <button class="btn btn-sm btn-secondary" @click="resetPendingChanges">🧹 清空变更</button>
              </div>
            </div>

            <!-- 网络配置标签页 -->
            <NetworkConfigPanel v-if="activeTab === 'network'" :container="container" :containerInfo="containerInfo"
              @update="handleNetworkUpdate" @message="handlePanelMessage" />

            <!-- 防火墙规则标签页 -->
            <FirewallConfigPanel v-if="activeTab === 'firewall'" :container="container" :containerInfo="containerInfo"
              @update="handleFirewallUpdate" @message="handlePanelMessage" />

            <!-- 服务管理标签页 -->
            <ServiceConfigPanel v-if="activeTab === 'services'" :container="container" :containerInfo="containerInfo"
              @update="handleServiceUpdate" @message="handlePanelMessage" />
          </div>
        </div>

        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="refreshInfo">🔄 刷新信息</button>
          <button class="btn btn-primary" @click="applyChanges">💾 应用更改</button>
          <button class="btn btn-ghost" @click="closeDialog">❌ 关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NetworkConfigPanel from './NetworkConfigPanel.vue'
import FirewallConfigPanel from './FirewallConfigPanel.vue'
import ServiceConfigPanel from './ServiceConfigPanel.vue'
import ContainerConfigService from '../services/ContainerConfigService'

export default {
  name: 'ContainerConfigDialog',
  components: {
    NetworkConfigPanel,
    FirewallConfigPanel,
    ServiceConfigPanel
  },
  emits: ['close', 'message'],
  props: {
    show: {
      type: Boolean,
      default: false
    },
    container: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      activeTab: 'network',
      containerInfo: {},
      pendingChanges: {
        network: {},
        firewall: {},
        services: {}
      },
      // 拖动相关状态
      isDragging: false,
      dragOffset: { x: 0, y: 0 },
      position: { x: 0, y: 0 }
    }
  },
  mounted() {
    document.addEventListener('mousemove', this.onMouseMove)
    document.addEventListener('mouseup', this.onMouseUp)
  },
  beforeUnmount() {
    document.removeEventListener('mousemove', this.onMouseMove)
    document.removeEventListener('mouseup', this.onMouseUp)
  },
  computed: {
    statusText() {
      if (!this.containerInfo.status) return '未知'
      const statusMap = {
        'running': '运行中',
        'stopped': '已停止',
        'paused': '已暂停',
        'restarting': '重启中',
        'dead': '已死亡',
        'created': '已创建'
      }
      return statusMap[this.containerInfo.status] || this.containerInfo.status
    },
    statusClass() {
      if (!this.containerInfo.status) return ''
      const classMap = {
        'running': 'status-running',
        'stopped': 'status-stopped',
        'paused': 'status-paused',
        'restarting': 'status-restarting',
        'dead': 'status-dead',
        'created': 'status-created'
      }
      return classMap[this.containerInfo.status] || ''
    }
  },
  watch: {
    container: {
      immediate: true,
      handler(newVal) {
        if (newVal && (newVal.id || newVal.deviceData)) {
          this.loadContainerInfo()
        }
      }
    },
    show(newVal) {
      if (newVal) {
        // 延迟加载，确保DOM已渲染
        this.$nextTick(() => {
          this.loadContainerInfo()
          this.resetPendingChanges()
        })
      }
    }
  },
  methods: {
    async loadContainerInfo() {
      try {
        console.log('🔍 开始加载容器信息:', this.container)
        this.containerInfo = await ContainerConfigService.getContainerInfo(this.container)
        console.log('✅ 容器信息加载成功:', this.containerInfo)

        // 强制触发子组件更新
        this.$nextTick(() => {
          console.log('🔄 强制触发子组件数据更新')
        })
      } catch (error) {
        console.error('❌ 加载容器信息失败:', error)
        this.containerInfo = {}
      }
    },

    resetPendingChanges() {
      this.pendingChanges = {
        network: {},
        firewall: {},
        services: {}
      }
    },

    handleNetworkUpdate(changes) {
      this.pendingChanges.network = { ...this.pendingChanges.network, ...changes }
    },

    handleFirewallUpdate(changes) {
      this.pendingChanges.firewall = { ...this.pendingChanges.firewall, ...changes }
    },

    handleServiceUpdate(changes) {
      this.pendingChanges.services = { ...this.pendingChanges.services, ...changes }
    },

    async applyChanges() {
      try {
        const hasChanges = Object.values(this.pendingChanges).some(changes =>
          Object.keys(changes).length > 0
        )

        if (!hasChanges) {
          this.$emit('message', { type: 'warning', text: '没有需要应用的更改' })
          return
        }

        this.$emit('message', { type: 'info', text: '正在应用配置更改...' })

        const result = await ContainerConfigService.applyContainerConfig(
          this.container,
          this.pendingChanges
        )

        if (result.success) {
          this.$emit('message', { type: 'success', text: '配置更改已成功应用' })
          this.resetPendingChanges()
          await this.loadContainerInfo() // 刷新信息
        } else {
          this.$emit('message', { type: 'error', text: `应用配置失败: ${result.error}` })
        }
      } catch (error) {
        console.error('应用配置更改失败:', error)
        this.$emit('message', { type: 'error', text: `应用配置失败: ${error.message}` })
      }
    },

    async refreshInfo() {
      await this.loadContainerInfo()
      this.$emit('message', { type: 'info', text: '容器信息已刷新' })
    },

    handlePanelMessage(message) {
      // 将配置面板的消息转发给父组件
      this.$emit('message', message)
    },

    closeDialog() {
      this.$emit('close')
    },

    // 拖动相关方法
    startDrag(event) {
      if (event.target.classList.contains('close-btn')) return

      this.isDragging = true
      const dialogRect = this.$refs.dialogContent.getBoundingClientRect()

      this.dragOffset = {
        x: event.clientX - dialogRect.left,
        y: event.clientY - dialogRect.top
      }

      if (this.position.x === 0 && this.position.y === 0) {
        this.position = {
          x: dialogRect.left,
          y: dialogRect.top
        }
      }

      this.$refs.dialogContent.style.transition = 'none'
      this.$refs.dialogContent.style.cursor = 'grabbing'
    },

    onMouseMove(event) {
      if (!this.isDragging) return

      this.position = {
        x: event.clientX - this.dragOffset.x,
        y: event.clientY - this.dragOffset.y
      }

      this.applyPosition()
    },

    onMouseUp() {
      if (!this.isDragging) return

      this.isDragging = false

      if (this.$refs.dialogContent) {
        this.$refs.dialogContent.style.transition = ''
        this.$refs.dialogContent.style.cursor = ''
      }
    },

    applyPosition() {
      if (!this.$refs.dialogContent) return

      const windowWidth = window.innerWidth
      const windowHeight = window.innerHeight
      const dialogRect = this.$refs.dialogContent.getBoundingClientRect()

      let x = this.position.x
      let y = this.position.y

      if (x < 0) x = 0
      if (x + dialogRect.width > windowWidth) x = windowWidth - dialogRect.width
      if (y < 0) y = 0
      if (y + dialogRect.height > windowHeight) y = windowHeight - dialogRect.height

      this.position = { x, y }

      this.$refs.dialogContent.style.position = 'fixed'
      this.$refs.dialogContent.style.left = `${x}px`
      this.$refs.dialogContent.style.top = `${y}px`
      this.$refs.dialogContent.style.margin = '0'
      this.$refs.dialogContent.style.transform = 'none'
    }
  }
}
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
  width: 800px;
  max-width: 95%;
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
  cursor: grab;
}

.dialog-header h3 {
  margin: 0;
  color: #ffffff;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #ffffff;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
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

.container-info {
  display: flex;
  gap: 24px;
  padding: 12px;
  background-color: #27293d;
  border-radius: 6px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label {
  color: #a9a9a9;
  font-size: 12px;
  font-weight: 500;
}

.value {
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
}

.status-running {
  color: #00f2c3;
}

.status-stopped {
  color: #fd5d93;
}

.status-paused {
  color: #ffa726;
}

.status-restarting {
  color: #42a5f5;
}

.status-dead {
  color: #ef5350;
}

.status-created {
  color: #ab47bc;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #2c2c40;
  margin-bottom: 16px;
}

.tab {
  padding: 12px 16px;
  cursor: pointer;
  color: #a9a9a9;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
  font-weight: 500;
}

.tab:hover {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.05);
}

.tab.active {
  color: #1d8cf8;
  border-bottom-color: #1d8cf8;
  background-color: rgba(29, 140, 248, 0.1);
}

.tab-content {
  flex-grow: 1;
  min-height: 400px;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s ease;
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

.btn-ghost {
  background-color: transparent;
  color: #a9a9a9;
  border: 1px solid #2c2c40;
}

.btn-ghost:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: #ffffff;
}

.debug-info {
  padding: 16px;
  background-color: #0d1117;
  border-radius: 6px;
  color: #c9d1d9;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
  overflow-x: auto;
}

.debug-info h4 {
  color: #58a6ff;
  margin: 0 0 12px 0;
}

.debug-info pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 200px;
  overflow-y: auto;
  background-color: #0d1117;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #2c2c40;
}

.debug-section {
  margin-bottom: 16px;
}

.debug-section h5 {
  color: #58a6ff;
  margin: 0 0 8px 0;
  font-size: 14px;
}

.debug-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}
</style>
