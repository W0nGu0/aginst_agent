<template>
  <div class="service-config-panel">
    <!-- 简单的数据状态显示 -->
    <div class="debug-status" style="background: #1e1e2f; padding: 8px; margin-bottom: 16px; border-radius: 4px; font-size: 12px; color: #a9a9a9;">
      服务数据: 服务={{ serviceConfig.services.length }}, 端口={{ serviceConfig.ports.length }}, 监控={{ serviceConfig.monitoring.enabled ? '启用' : '禁用' }}
    </div>
    
    <div class="config-section">
      <h4>⚙️ 服务管理</h4>

      <!-- 服务操作栏 -->
      <div class="services-actions">
        <button class="btn btn-primary" @click="refreshServices">🔄 刷新服务</button>
        <button class="btn btn-secondary" @click="startAllServices">▶️ 启动全部</button>
        <button class="btn btn-secondary" @click="stopAllServices">⏹️ 停止全部</button>
        <div class="services-stats">
          <span>总服务: {{ serviceConfig.services.length }}</span>
          <span>运行中: {{ runningServicesCount }}</span>
          <span>已停止: {{ stoppedServicesCount }}</span>
        </div>
      </div>

      <!-- 服务列表 -->
      <div class="services-table">
        <div class="services-header">
          <span>服务名称</span>
          <span>状态</span>
          <span>端口</span>
          <span>自动启动</span>
          <span>CPU使用率</span>
          <span>内存使用</span>
          <span>描述</span>
          <span>操作</span>
        </div>

        <div v-for="(service, index) in serviceConfig.services" :key="index" class="service-row"
          :class="{ 'service-running': service.status === 'running' }">
          <span class="service-name">
            <i :class="getServiceIcon(service.name)"></i>
            {{ service.name }}
          </span>
          <span class="service-status" :class="service.status">
            <span class="status-indicator" :class="service.status"></span>
            {{ getStatusText(service.status) }}
          </span>
          <span class="service-port">
            <span v-for="port in service.ports" :key="port" class="port-badge">
              {{ port }}
            </span>
          </span>
          <span class="service-autostart">
            <label class="toggle-switch">
              <input type="checkbox" v-model="service.autostart" @change="markChanged('services')">
              <span class="toggle-slider"></span>
            </label>
          </span>
          <span class="service-cpu">{{ service.cpuUsage || '0%' }}</span>
          <span class="service-memory">{{ service.memoryUsage || '0MB' }}</span>
          <span class="service-description">{{ service.description || '-' }}</span>
          <span class="service-actions">
            <button v-if="service.status === 'stopped'" class="btn btn-sm btn-success" @click="startService(index)">
              启动
            </button>
            <button v-if="service.status === 'running'" class="btn btn-sm btn-warning" @click="stopService(index)">
              停止
            </button>
            <button v-if="service.status === 'running'" class="btn btn-sm btn-info" @click="restartService(index)">
              重启
            </button>
            <button class="btn btn-sm btn-outline" @click="configureService(index)">配置</button>
            <button class="btn btn-sm btn-info" @click="viewServiceLogs(index)">日志</button>
          </span>
        </div>

        <div v-if="serviceConfig.services.length === 0" class="empty-services">
          <p>暂无服务信息</p>
          <button class="btn btn-primary" @click="refreshServices">刷新服务列表</button>
        </div>
      </div>
    </div>

    <div class="config-section">
      <h4>🔌 端口管理</h4>

      <!-- 端口操作栏 -->
      <div class="ports-actions">
        <button class="btn btn-primary" @click="addPort">+ 开放端口</button>
        <button class="btn btn-secondary" @click="scanPorts">🔍 扫描端口</button>
        <div class="ports-filter">
          <select v-model="portFilter" class="form-control-sm">
            <option value="all">全部端口</option>
            <option value="open">开放端口</option>
            <option value="closed">关闭端口</option>
            <option value="listening">监听端口</option>
          </select>
        </div>
      </div>

      <!-- 端口列表 -->
      <div class="ports-table">
        <div class="ports-header">
          <span>端口</span>
          <span>协议</span>
          <span>状态</span>
          <span>服务</span>
          <span>进程</span>
          <span>描述</span>
          <span>操作</span>
        </div>

        <div v-for="(port, index) in filteredPorts" :key="index" class="port-row">
          <span class="port-number">{{ port.port }}</span>
          <span class="port-protocol">{{ port.protocol.toUpperCase() }}</span>
          <span class="port-status" :class="port.status">
            <span class="status-indicator" :class="port.status"></span>
            {{ getPortStatusText(port.status) }}
          </span>
          <span class="port-service">{{ port.service || '-' }}</span>
          <span class="port-process">{{ port.process || '-' }}</span>
          <span class="port-description">{{ port.description || '-' }}</span>
          <span class="port-actions">
            <button v-if="port.status === 'closed'" class="btn btn-sm btn-success" @click="openPort(index)">
              开放
            </button>
            <button v-if="port.status === 'open'" class="btn btn-sm btn-warning" @click="closePort(index)">
              关闭
            </button>
            <button class="btn btn-sm btn-outline" @click="editPort(index)">编辑</button>
            <button class="btn btn-sm btn-danger" @click="deletePort(index)">删除</button>
          </span>
        </div>
      </div>
    </div>

    <div class="config-section">
      <h4>📊 性能监控</h4>

      <div class="monitoring-grid">
        <div class="monitor-item">
          <div class="monitor-label">CPU使用率</div>
          <div class="monitor-value">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: serviceConfig.monitoring.cpuUsage + '%' }"></div>
            </div>
            <span>{{ serviceConfig.monitoring.cpuUsage }}%</span>
          </div>
        </div>

        <div class="monitor-item">
          <div class="monitor-label">内存使用</div>
          <div class="monitor-value">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: serviceConfig.monitoring.memoryUsage + '%' }"></div>
            </div>
            <span>{{ serviceConfig.monitoring.memoryUsed }}MB / {{ serviceConfig.monitoring.memoryTotal }}MB</span>
          </div>
        </div>

        <div class="monitor-item">
          <div class="monitor-label">网络流量</div>
          <div class="monitor-value">
            <span>↑ {{ serviceConfig.monitoring.networkOut }}</span>
            <span>↓ {{ serviceConfig.monitoring.networkIn }}</span>
          </div>
        </div>

        <div class="monitor-item">
          <div class="monitor-label">磁盘使用</div>
          <div class="monitor-value">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: serviceConfig.monitoring.diskUsage + '%' }"></div>
            </div>
            <span>{{ serviceConfig.monitoring.diskUsage }}%</span>
          </div>
        </div>
      </div>

      <div class="monitoring-settings">
        <h5>监控设置</h5>
        <div class="config-grid">
          <div class="config-item">
            <label class="checkbox-label">
              <input type="checkbox" v-model="serviceConfig.monitoring.enabled" @change="markChanged('monitoring')">
              启用性能监控
            </label>
          </div>

          <div class="config-item">
            <label>监控间隔</label>
            <select v-model="serviceConfig.monitoring.interval" class="form-control"
              @change="markChanged('monitoring')">
              <option value="5">5秒</option>
              <option value="10">10秒</option>
              <option value="30">30秒</option>
              <option value="60">1分钟</option>
            </select>
          </div>

          <div class="config-item">
            <label class="checkbox-label">
              <input type="checkbox" v-model="serviceConfig.monitoring.alertEnabled"
                @change="markChanged('monitoring')">
              启用告警
            </label>
          </div>

          <div class="config-item">
            <label>CPU告警阈值</label>
            <div class="input-group">
              <input type="number" v-model="serviceConfig.monitoring.cpuThreshold" class="form-control" min="0"
                max="100" @input="markChanged('monitoring')">
              <span class="input-addon">%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 服务日志显示区域 -->
    <div v-if="diagnosticResult" class="diagnostic-result">
      <h4>📋 服务日志</h4>
      <pre class="result-output">{{ diagnosticResult }}</pre>
      <div class="log-actions">
        <button class="btn btn-sm btn-secondary" @click="diagnosticResult = ''">关闭日志</button>
        <button class="btn btn-sm btn-outline" @click="downloadLogs">下载日志</button>
      </div>
    </div>

    <!-- 变更预览 -->
    <div v-if="hasChanges" class="changes-preview">
      <h4>📋 待应用的更改</h4>
      <div class="changes-list">
        <div v-for="change in pendingChanges" :key="change.field" class="change-item">
          <span class="change-field">{{ getFieldDisplayName(change.field) }}</span>
          <span class="change-arrow">→</span>
          <span class="change-value">{{ change.newValue }}</span>
        </div>
      </div>
    </div>

    <!-- 服务配置对话框 -->
    <div v-if="showServiceDialog" class="service-dialog-overlay" @click="closeServiceDialog">
      <div class="service-dialog" @click.stop>
        <div class="dialog-header">
          <h3>配置服务 - {{ editingService.name }}</h3>
          <button class="close-btn" @click="closeServiceDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>服务描述</label>
            <input type="text" v-model="editingService.description" class="form-control">
          </div>
          <div class="form-group">
            <label>启动命令</label>
            <input type="text" v-model="editingService.command" class="form-control">
          </div>
          <div class="form-group">
            <label>工作目录</label>
            <input type="text" v-model="editingService.workdir" class="form-control">
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="editingService.autostart">
              开机自动启动
            </label>
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="editingService.restartOnFailure">
              失败时自动重启
            </label>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-primary" @click="saveServiceConfig">保存</button>
          <button class="btn btn-secondary" @click="closeServiceDialog">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ServiceConfigPanel',
  emits: ['update', 'message'],
  props: {
    container: {
      type: Object,
      required: true
    },
    containerInfo: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      serviceConfig: {
        services: [],
        ports: [],
        monitoring: {
          enabled: true,
          interval: 10,
          alertEnabled: true,
          cpuThreshold: 80,
          cpuUsage: 0,
          memoryUsage: 0,
          memoryUsed: 0,
          memoryTotal: 0,
          networkIn: '0KB/s',
          networkOut: '0KB/s',
          diskUsage: 0
        }
      },
      originalConfig: {},
      changedFields: new Set(),
      portFilter: 'all',
      showServiceDialog: false,
      editingService: {},
      editingServiceIndex: -1,
      diagnosticResult: ''
    }
  },
  computed: {
    hasChanges() {
      return this.changedFields.size > 0
    },
    pendingChanges() {
      return Array.from(this.changedFields).map(field => ({
        field,
        newValue: this.formatFieldValue(field, this.serviceConfig[field])
      }))
    },
    runningServicesCount() {
      return this.serviceConfig.services.filter(service => service.status === 'running').length
    },
    stoppedServicesCount() {
      return this.serviceConfig.services.filter(service => service.status === 'stopped').length
    },
    filteredPorts() {
      if (this.portFilter === 'all') {
        return this.serviceConfig.ports
      }
      return this.serviceConfig.ports.filter(port => port.status === this.portFilter)
    }
  },
  watch: {
    containerInfo: {
      immediate: true,
      handler(newVal) {
        console.log('🔄 ServiceConfigPanel: containerInfo 变化', newVal)
        if (newVal) {
          this.loadServiceConfig()
        }
      }
    }
  },
  mounted() {
    console.log('🚀 ServiceConfigPanel mounted, containerInfo:', this.containerInfo)
    // 如果已经有容器信息，立即加载配置
    if (this.containerInfo && Object.keys(this.containerInfo).length > 0) {
      this.loadServiceConfig()
    }
  },
  methods: {
    loadServiceConfig() {
      console.log('⚙️ ServiceConfigPanel: 加载服务配置', this.containerInfo)

      const info = this.containerInfo
      this.serviceConfig = {
        services: info.services || this.generateMockServices(),
        ports: info.ports || this.generateMockPorts(),
        monitoring: {
          enabled: info.monitoringEnabled !== false,
          interval: info.monitoringInterval || 10,
          alertEnabled: info.alertEnabled !== false,
          cpuThreshold: info.cpuThreshold || 80,
          cpuUsage: info.cpuUsage || Math.floor(Math.random() * 100),
          memoryUsage: info.memoryUsage || Math.floor(Math.random() * 100),
          memoryUsed: info.memoryUsed || Math.floor(Math.random() * 2048),
          memoryTotal: info.memoryTotal || 4096,
          networkIn: info.networkIn || '1.2KB/s',
          networkOut: info.networkOut || '0.8KB/s',
          diskUsage: info.diskUsage || Math.floor(Math.random() * 100)
        }
      }

      console.log('✅ ServiceConfigPanel: 服务配置已加载', this.serviceConfig)

      this.originalConfig = JSON.parse(JSON.stringify(this.serviceConfig))
      this.changedFields.clear()
    },

    generateMockServices() {
      const containerName = this.container.deviceData?.name || ''
      const services = []

      if (containerName.includes('Web') || containerName.includes('web')) {
        services.push(
          { name: 'nginx', status: 'running', ports: [80, 443], autostart: true, cpuUsage: '2.1%', memoryUsage: '45MB', description: 'Web服务器' },
          { name: 'php-fpm', status: 'running', ports: [9000], autostart: true, cpuUsage: '1.8%', memoryUsage: '32MB', description: 'PHP处理器' }
        )
      } else if (containerName.includes('数据库') || containerName.includes('database')) {
        services.push(
          { name: 'mysql', status: 'running', ports: [3306], autostart: true, cpuUsage: '5.2%', memoryUsage: '128MB', description: 'MySQL数据库' },
          { name: 'redis', status: 'stopped', ports: [6379], autostart: false, cpuUsage: '0%', memoryUsage: '0MB', description: 'Redis缓存' }
        )
      } else if (containerName.includes('防火墙') || containerName.includes('firewall')) {
        services.push(
          { name: 'iptables', status: 'running', ports: [], autostart: true, cpuUsage: '0.5%', memoryUsage: '8MB', description: '防火墙服务' },
          { name: 'fail2ban', status: 'running', ports: [], autostart: true, cpuUsage: '0.3%', memoryUsage: '12MB', description: '入侵防护' }
        )
      } else {
        services.push(
          { name: 'ssh', status: 'running', ports: [22], autostart: true, cpuUsage: '0.1%', memoryUsage: '5MB', description: 'SSH服务' },
          { name: 'cron', status: 'running', ports: [], autostart: true, cpuUsage: '0.1%', memoryUsage: '2MB', description: '定时任务' }
        )
      }

      return services
    },

    generateMockPorts() {
      return [
        { port: 22, protocol: 'tcp', status: 'open', service: 'ssh', process: 'sshd', description: 'SSH远程访问' },
        { port: 80, protocol: 'tcp', status: 'open', service: 'http', process: 'nginx', description: 'HTTP Web服务' },
        { port: 443, protocol: 'tcp', status: 'closed', service: 'https', process: '', description: 'HTTPS Web服务' },
        { port: 3306, protocol: 'tcp', status: 'listening', service: 'mysql', process: 'mysqld', description: 'MySQL数据库' }
      ]
    },

    markChanged(field) {
      this.changedFields.add(field)
      this.emitUpdate()
    },

    emitUpdate() {
      const changes = {}
      this.changedFields.forEach(field => {
        changes[field] = this.serviceConfig[field]
      })
      this.$emit('update', changes)
    },

    async refreshServices() {
      this.$emit('message', { type: 'info', text: '正在刷新服务列表...' })
      // TODO: 实际调用API刷新服务信息
      setTimeout(() => {
        this.loadServiceConfig()
        this.$emit('message', { type: 'success', text: '服务列表已刷新' })
      }, 1000)
    },

    async startService(index) {
      const service = this.serviceConfig.services[index]
      this.$emit('message', { type: 'info', text: `正在启动服务 ${service.name}...` })

      // TODO: 实际调用API启动服务
      setTimeout(() => {
        service.status = 'running'
        this.markChanged('services')
        this.$emit('message', { type: 'success', text: `服务 ${service.name} 已启动` })
      }, 1000)
    },

    async stopService(index) {
      const service = this.serviceConfig.services[index]
      this.$emit('message', { type: 'info', text: `正在停止服务 ${service.name}...` })

      // TODO: 实际调用API停止服务
      setTimeout(() => {
        service.status = 'stopped'
        service.cpuUsage = '0%'
        this.markChanged('services')
        this.$emit('message', { type: 'success', text: `服务 ${service.name} 已停止` })
      }, 1000)
    },

    async restartService(index) {
      const service = this.serviceConfig.services[index]
      this.$emit('message', { type: 'info', text: `正在重启服务 ${service.name}...` })

      // TODO: 实际调用API重启服务
      setTimeout(() => {
        this.$emit('message', { type: 'success', text: `服务 ${service.name} 已重启` })
      }, 1500)
    },

    configureService(index) {
      this.editingService = { ...this.serviceConfig.services[index] }
      this.editingServiceIndex = index
      this.showServiceDialog = true
    },

    saveServiceConfig() {
      if (this.editingServiceIndex >= 0) {
        this.serviceConfig.services[this.editingServiceIndex] = { ...this.editingService }
        this.markChanged('services')
      }
      this.closeServiceDialog()
    },

    closeServiceDialog() {
      this.showServiceDialog = false
    },

    viewServiceLogs(index) {
      const service = this.serviceConfig.services[index]
      this.$emit('message', { type: 'info', text: `正在获取 ${service.name} 服务日志...` })

      // 模拟服务日志
      setTimeout(() => {
        const logs = this.generateServiceLogs(service.name)
        this.diagnosticResult = logs
        this.$emit('message', { type: 'success', text: `${service.name} 服务日志获取完成` })
      }, 1000)
    },

    generateServiceLogs(serviceName) {
      const now = new Date()
      const logs = []

      // 生成最近的日志条目
      for (let i = 10; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 60000) // 每分钟一条日志
        const timeStr = time.toLocaleString('zh-CN')

        switch (serviceName) {
          case 'nginx':
            logs.push(`${timeStr} [info] nginx: worker process started`)
            if (i % 3 === 0) {
              logs.push(`${timeStr} [access] 192.168.1.100 - - "GET / HTTP/1.1" 200 1234`)
            }
            break
          case 'mysql':
            logs.push(`${timeStr} [Note] mysqld: ready for connections`)
            if (i % 4 === 0) {
              logs.push(`${timeStr} [Warning] Aborted connection 123 to db: 'test' user: 'root'`)
            }
            break
          case 'ssh':
            logs.push(`${timeStr} sshd[1234]: Server listening on 0.0.0.0 port 22`)
            if (i % 5 === 0) {
              logs.push(`${timeStr} sshd[5678]: Accepted publickey for user from 192.168.1.50`)
            }
            break
          default:
            logs.push(`${timeStr} [info] ${serviceName}: service running normally`)
            if (i % 6 === 0) {
              logs.push(`${timeStr} [debug] ${serviceName}: processing request`)
            }
        }
      }

      return logs.join('\n')
    },

    downloadLogs() {
      if (!this.diagnosticResult) return

      const blob = new Blob([this.diagnosticResult], { type: 'text/plain' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `service-logs-${new Date().toISOString().slice(0, 10)}.txt`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)

      this.$emit('message', { type: 'success', text: '日志文件已下载' })
    },

    async startAllServices() {
      this.$emit('message', { type: 'info', text: '正在启动所有服务...' })
      // TODO: 实际调用API
    },

    async stopAllServices() {
      this.$emit('message', { type: 'info', text: '正在停止所有服务...' })
      // TODO: 实际调用API
    },

    addPort() {
      // TODO: 实现添加端口功能
      this.$emit('message', { type: 'info', text: '添加端口功能开发中...' })
    },

    scanPorts() {
      this.$emit('message', { type: 'info', text: '正在扫描端口...' })
      // TODO: 实际调用API扫描端口
    },

    openPort(index) {
      const port = this.serviceConfig.ports[index]
      port.status = 'open'
      this.markChanged('ports')
      this.$emit('message', { type: 'success', text: `端口 ${port.port} 已开放` })
    },

    closePort(index) {
      const port = this.serviceConfig.ports[index]
      port.status = 'closed'
      this.markChanged('ports')
      this.$emit('message', { type: 'success', text: `端口 ${port.port} 已关闭` })
    },

    editPort(index) {
      // TODO: 实现编辑端口功能
      this.$emit('message', { type: 'info', text: '编辑端口功能开发中...' })
    },

    deletePort(index) {
      if (confirm('确定要删除这个端口配置吗？')) {
        this.serviceConfig.ports.splice(index, 1)
        this.markChanged('ports')
      }
    },

    getServiceIcon(serviceName) {
      const icons = {
        'nginx': '🌐',
        'apache': '🌐',
        'mysql': '🗄️',
        'redis': '📦',
        'ssh': '🔐',
        'cron': '⏰',
        'iptables': '🔥',
        'fail2ban': '🛡️'
      }
      return icons[serviceName] || '⚙️'
    },

    getStatusText(status) {
      const statusMap = {
        'running': '运行中',
        'stopped': '已停止',
        'failed': '失败',
        'starting': '启动中',
        'stopping': '停止中'
      }
      return statusMap[status] || status
    },

    getPortStatusText(status) {
      const statusMap = {
        'open': '开放',
        'closed': '关闭',
        'listening': '监听',
        'filtered': '过滤'
      }
      return statusMap[status] || status
    },

    getFieldDisplayName(field) {
      const displayNames = {
        services: '服务配置',
        ports: '端口配置',
        monitoring: '监控设置'
      }
      return displayNames[field] || field
    },

    formatFieldValue(field, value) {
      if (field === 'services') {
        return `${value.length} 个服务`
      }
      if (field === 'ports') {
        return `${value.length} 个端口`
      }
      if (field === 'monitoring') {
        return value.enabled ? '已启用' : '已禁用'
      }
      return String(value)
    }
  }
}
</script>

<style scoped>
/* 继承基础样式，添加服务管理特有样式 */
.service-config-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.services-actions,
.ports-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;
}

.services-stats {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #a9a9a9;
}

.services-table,
.ports-table {
  border: 1px solid #2c2c40;
  border-radius: 6px;
  overflow: hidden;
}

.services-header,
.ports-header {
  display: grid;
  gap: 8px;
  padding: 12px 8px;
  background-color: #1e1e2f;
  font-weight: 500;
  color: #a9a9a9;
  font-size: 12px;
}

.services-header {
  grid-template-columns: 150px 100px 100px 80px 80px 80px 150px 120px;
}

.ports-header {
  grid-template-columns: 80px 80px 100px 120px 120px 150px 120px;
}

.service-row,
.port-row {
  display: grid;
  gap: 8px;
  padding: 12px 8px;
  border-top: 1px solid #2c2c40;
  align-items: center;
  font-size: 12px;
}

.service-row {
  grid-template-columns: 150px 100px 100px 80px 80px 80px 150px 120px;
}

.port-row {
  grid-template-columns: 80px 80px 100px 120px 120px 150px 120px;
}

.service-row.service-running {
  background-color: rgba(0, 242, 195, 0.05);
}

.service-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.service-status,
.port-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-indicator.running,
.status-indicator.open,
.status-indicator.listening {
  background-color: #00f2c3;
}

.status-indicator.stopped,
.status-indicator.closed {
  background-color: #fd5d93;
}

.status-indicator.failed {
  background-color: #ff6b6b;
}

.port-badge {
  display: inline-block;
  background-color: #1d8cf8;
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 10px;
  margin-right: 4px;
}

.monitoring-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.monitor-item {
  background-color: #1e1e2f;
  padding: 16px;
  border-radius: 6px;
}

.monitor-label {
  color: #a9a9a9;
  font-size: 12px;
  margin-bottom: 8px;
}

.monitor-value {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ffffff;
  font-size: 14px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background-color: #2c2c40;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #1d8cf8;
  transition: width 0.3s ease;
}

.monitoring-settings h5 {
  margin: 0 0 16px 0;
  color: #ffffff;
  font-size: 14px;
}

.input-addon {
  background-color: #2c2c40;
  color: #a9a9a9;
  padding: 8px 12px;
  border: 1px solid #2c2c40;
  border-left: none;
  border-radius: 0 4px 4px 0;
  font-size: 12px;
}

.empty-services {
  text-align: center;
  padding: 40px;
  color: #a9a9a9;
}

.service-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1001;
}

.service-dialog {
  background-color: #1e1e2f;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.diagnostic-result {
  margin-top: 20px;
  background-color: #1e1e2f;
  padding: 16px;
  border-radius: 6px;
  border-left: 4px solid #17a2b8;
}

.diagnostic-result h4 {
  margin: 0 0 12px 0;
  color: #17a2b8;
  font-size: 16px;
}

.result-output {
  background-color: #0d1117;
  color: #c9d1d9;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 11px;
  line-height: 1.4;
  white-space: pre-wrap;
  overflow-x: auto;
  margin: 0 0 12px 0;
  border: 1px solid #2c2c40;
  max-height: 300px;
  overflow-y: auto;
}

.log-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
</style>
