<template>
  <div class="network-config-panel">
    <!-- 简单的数据状态显示 -->
    <div class="debug-status" style="background: #1e1e2f; padding: 8px; margin-bottom: 16px; border-radius: 4px; font-size: 12px; color: #a9a9a9;">
      数据状态: containerInfo={{ Object.keys(containerInfo).length }} 项, networkConfig={{ Object.keys(networkConfig).length }} 项
      <button class="btn btn-xs" style="margin-left: 8px;" @click="loadNetworkConfig">🔄 重载</button>
      <button class="btn btn-xs" style="margin-left: 4px;" @click="testData">🧪 测试</button>
    </div>
    
    <div class="config-section">
      <h4>🌐 IP地址配置</h4>
      <div class="config-grid">
        <div class="config-item">
          <label>主IP地址</label>
          <div class="input-group">
            <input type="text" v-model="networkConfig.primaryIP" class="form-control" placeholder="192.168.1.100"
              @input="markChanged('primaryIP')">
            <button class="btn btn-sm btn-outline" @click="validateIP('primaryIP')">验证</button>
          </div>
          <small class="help-text">容器的主要IP地址</small>
        </div>

        <div class="config-item">
          <label>网络段</label>
          <select v-model="networkConfig.network" class="form-control" @change="markChanged('network')">
            <option value="">选择网络段</option>
            <option value="dmz_segment">DMZ段 (172.16.100.0/24)</option>
            <option value="server_segment">服务器段 (192.168.200.0/24)</option>
            <option value="user_segment">用户段 (192.168.100.0/24)</option>
            <option value="db_segment">数据库段 (192.168.214.0/24)</option>
            <option value="medical_segment">医疗段 (192.168.101.0/24)</option>
            <option value="siem_segment">SIEM段 (192.168.66.0/24)</option>
            <option value="vpn_segment">VPN段 (192.168.110.0/24)</option>
          </select>
          <small class="help-text">选择容器所属的网络段</small>
        </div>

        <div class="config-item">
          <label>子网掩码</label>
          <input type="text" v-model="networkConfig.netmask" class="form-control" placeholder="255.255.255.0"
            @input="markChanged('netmask')">
          <small class="help-text">网络子网掩码</small>
        </div>

        <div class="config-item">
          <label>默认网关</label>
          <input type="text" v-model="networkConfig.gateway" class="form-control" placeholder="192.168.1.1"
            @input="markChanged('gateway')">
          <small class="help-text">默认网关地址</small>
        </div>
      </div>
    </div>

    <div class="config-section">
      <h4>🔗 端口映射</h4>
      <div class="port-mappings">
        <div class="port-mapping-header">
          <span>容器端口</span>
          <span>主机端口</span>
          <span>协议</span>
          <span>描述</span>
          <span>操作</span>
        </div>

        <div v-for="(mapping, index) in networkConfig.portMappings" :key="index" class="port-mapping-row">
          <input type="number" v-model="mapping.containerPort" class="form-control-sm" placeholder="80"
            @input="markChanged('portMappings')">
          <input type="number" v-model="mapping.hostPort" class="form-control-sm" placeholder="8080"
            @input="markChanged('portMappings')">
          <select v-model="mapping.protocol" class="form-control-sm" @change="markChanged('portMappings')">
            <option value="tcp">TCP</option>
            <option value="udp">UDP</option>
          </select>
          <input type="text" v-model="mapping.description" class="form-control-sm" placeholder="HTTP服务"
            @input="markChanged('portMappings')">
          <button class="btn btn-sm btn-danger" @click="removePortMapping(index)">删除</button>
        </div>

        <div class="port-mapping-actions">
          <button class="btn btn-sm btn-primary" @click="addPortMapping">+ 添加端口映射</button>
        </div>
      </div>
    </div>

    <div class="config-section">
      <h4>🌍 DNS配置</h4>
      <div class="config-grid">
        <div class="config-item">
          <label>主DNS服务器</label>
          <input type="text" v-model="networkConfig.primaryDNS" class="form-control" placeholder="8.8.8.8"
            @input="markChanged('primaryDNS')">
          <small class="help-text">主要DNS服务器地址</small>
        </div>

        <div class="config-item">
          <label>备用DNS服务器</label>
          <input type="text" v-model="networkConfig.secondaryDNS" class="form-control" placeholder="8.8.4.4"
            @input="markChanged('secondaryDNS')">
          <small class="help-text">备用DNS服务器地址</small>
        </div>

        <div class="config-item full-width">
          <label>DNS搜索域</label>
          <input type="text" v-model="networkConfig.searchDomains" class="form-control"
            placeholder="company.local, internal.com" @input="markChanged('searchDomains')">
          <small class="help-text">DNS搜索域列表，用逗号分隔</small>
        </div>
      </div>
    </div>

    <div class="config-section">
      <h4>🔧 高级网络设置</h4>
      <div class="config-grid">
        <div class="config-item">
          <label class="checkbox-label">
            <input type="checkbox" v-model="networkConfig.enableIPv6" @change="markChanged('enableIPv6')">
            启用IPv6
          </label>
          <small class="help-text">启用IPv6网络支持</small>
        </div>

        <div class="config-item">
          <label class="checkbox-label">
            <input type="checkbox" v-model="networkConfig.enableBridge" @change="markChanged('enableBridge')">
            桥接模式
          </label>
          <small class="help-text">启用网络桥接模式</small>
        </div>

        <div class="config-item">
          <label>MTU大小</label>
          <input type="number" v-model="networkConfig.mtu" class="form-control" placeholder="1500" min="68" max="9000"
            @input="markChanged('mtu')">
          <small class="help-text">最大传输单元大小</small>
        </div>

        <div class="config-item">
          <label>网络优先级</label>
          <select v-model="networkConfig.priority" class="form-control" @change="markChanged('priority')">
            <option value="low">低</option>
            <option value="normal">正常</option>
            <option value="high">高</option>
            <option value="critical">关键</option>
          </select>
          <small class="help-text">网络流量优先级</small>
        </div>

        <div class="config-item">
          <label class="checkbox-label">
            <input type="checkbox" v-model="networkConfig.enableNAT" @change="markChanged('enableNAT')">
            启用NAT
          </label>
          <small class="help-text">启用网络地址转换</small>
        </div>

        <div class="config-item">
          <label class="checkbox-label">
            <input type="checkbox" v-model="networkConfig.enableDHCP" @change="markChanged('enableDHCP')">
            启用DHCP
          </label>
          <small class="help-text">启用动态主机配置协议</small>
        </div>

        <div class="config-item">
          <label>带宽限制</label>
          <div class="input-group">
            <input type="number" v-model="networkConfig.bandwidthLimit" class="form-control" placeholder="100" min="1"
              @input="markChanged('bandwidthLimit')">
            <span class="input-addon">Mbps</span>
          </div>
          <small class="help-text">网络带宽限制</small>
        </div>

        <div class="config-item">
          <label>网络模式</label>
          <select v-model="networkConfig.networkMode" class="form-control" @change="markChanged('networkMode')">
            <option value="bridge">桥接模式</option>
            <option value="host">主机模式</option>
            <option value="none">无网络</option>
            <option value="container">容器模式</option>
          </select>
          <small class="help-text">容器网络连接模式</small>
        </div>
      </div>
    </div>

    <div class="config-section">
      <h4>🔍 网络诊断工具</h4>
      <div class="diagnostic-tools">
        <div class="tool-group">
          <h5>连通性测试</h5>
          <div class="tool-actions">
            <div class="input-group">
              <input type="text" v-model="diagnosticTarget" class="form-control" placeholder="输入IP地址或域名">
              <button class="btn btn-primary" @click="pingTest">Ping测试</button>
            </div>
          </div>
        </div>

        <div class="tool-group">
          <h5>端口扫描</h5>
          <div class="tool-actions">
            <div class="input-group">
              <input type="text" v-model="scanTarget" class="form-control" placeholder="目标IP地址">
              <input type="text" v-model="scanPorts" class="form-control" placeholder="端口范围 (如: 1-1000)">
              <button class="btn btn-secondary" @click="portScan">扫描端口</button>
            </div>
          </div>
        </div>

        <div class="tool-group">
          <h5>网络状态</h5>
          <div class="tool-actions">
            <button class="btn btn-info" @click="showNetworkStats">查看网络统计</button>
            <button class="btn btn-info" @click="showRoutingTable">查看路由表</button>
            <button class="btn btn-info" @click="showARPTable">查看ARP表</button>
          </div>
        </div>
      </div>

      <!-- 诊断结果显示区域 -->
      <div v-if="diagnosticResult" class="diagnostic-result">
        <h5>诊断结果</h5>
        <pre class="result-output">{{ diagnosticResult }}</pre>
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
  </div>
</template>

<script>
export default {
  name: 'NetworkConfigPanel',
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
      networkConfig: {
        primaryIP: '',
        network: '',
        netmask: '255.255.255.0',
        gateway: '',
        portMappings: [],
        primaryDNS: '8.8.8.8',
        secondaryDNS: '8.8.4.4',
        searchDomains: '',
        enableIPv6: false,
        enableBridge: true,
        enableNAT: false,
        enableDHCP: false,
        mtu: 1500,
        priority: 'normal',
        bandwidthLimit: 100,
        networkMode: 'bridge'
      },
      originalConfig: {},
      changedFields: new Set(),
      diagnosticTarget: '',
      scanTarget: '',
      scanPorts: '1-1000',
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
        newValue: this.formatFieldValue(field, this.networkConfig[field])
      }))
    }
  },
  watch: {
    containerInfo: {
      immediate: true,
      handler(newVal) {
        console.log('🔄 NetworkConfigPanel: containerInfo 变化', newVal)
        if (newVal) {
          this.loadNetworkConfig()
        }
      }
    }
  },
  mounted() {
    console.log('🚀 NetworkConfigPanel mounted, containerInfo:', this.containerInfo)
    // 如果已经有容器信息，立即加载配置
    if (this.containerInfo && Object.keys(this.containerInfo).length > 0) {
      this.loadNetworkConfig()
    }
  },
  methods: {
    loadNetworkConfig() {
      console.log('🌐 NetworkConfigPanel: 加载网络配置', this.containerInfo)
      
      // 从容器信息中加载网络配置
      const info = this.containerInfo
      this.networkConfig = {
        primaryIP: info.ip || this.container.deviceData?.ip || '',
        network: info.network || this.container.deviceData?.network || '',
        netmask: info.netmask || '255.255.255.0',
        gateway: info.gateway || '',
        portMappings: info.portMappings || [],
        primaryDNS: info.primaryDNS || '8.8.8.8',
        secondaryDNS: info.secondaryDNS || '8.8.4.4',
        searchDomains: info.searchDomains || '',
        enableIPv6: info.enableIPv6 || false,
        enableBridge: info.enableBridge !== false,
        enableNAT: info.enableNAT || false,
        enableDHCP: info.enableDHCP || false,
        mtu: info.mtu || 1500,
        priority: info.priority || 'normal',
        bandwidthLimit: info.bandwidthLimit || 100,
        networkMode: info.networkMode || 'bridge'
      }

      console.log('✅ NetworkConfigPanel: 网络配置已加载', this.networkConfig)

      // 保存原始配置用于比较
      this.originalConfig = JSON.parse(JSON.stringify(this.networkConfig))
      this.changedFields.clear()
    },

    markChanged(field) {
      this.changedFields.add(field)
      this.emitUpdate()
    },

    emitUpdate() {
      const changes = {}
      this.changedFields.forEach(field => {
        changes[field] = this.networkConfig[field]
      })
      this.$emit('update', changes)
    },

    addPortMapping() {
      this.networkConfig.portMappings.push({
        containerPort: '',
        hostPort: '',
        protocol: 'tcp',
        description: ''
      })
      this.markChanged('portMappings')
    },

    removePortMapping(index) {
      this.networkConfig.portMappings.splice(index, 1)
      this.markChanged('portMappings')
    },

    validateIP(field) {
      const ip = this.networkConfig[field]
      const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/

      if (ipRegex.test(ip)) {
        this.$emit('message', { type: 'success', text: 'IP地址格式正确' })
      } else {
        this.$emit('message', { type: 'error', text: 'IP地址格式不正确' })
      }
    },

    getFieldDisplayName(field) {
      const displayNames = {
        primaryIP: '主IP地址',
        network: '网络段',
        netmask: '子网掩码',
        gateway: '默认网关',
        portMappings: '端口映射',
        primaryDNS: '主DNS服务器',
        secondaryDNS: '备用DNS服务器',
        searchDomains: 'DNS搜索域',
        enableIPv6: 'IPv6支持',
        enableBridge: '桥接模式',
        mtu: 'MTU大小',
        priority: '网络优先级'
      }
      return displayNames[field] || field
    },

    formatFieldValue(field, value) {
      if (field === 'portMappings') {
        return `${value.length} 个映射`
      }
      if (typeof value === 'boolean') {
        return value ? '启用' : '禁用'
      }
      return String(value)
    },

    // 网络诊断工具方法
    async pingTest() {
      if (!this.diagnosticTarget.trim()) {
        this.$emit('message', { type: 'warning', text: '请输入目标地址' })
        return
      }

      this.$emit('message', { type: 'info', text: `正在ping ${this.diagnosticTarget}...` })

      // 模拟ping测试结果
      setTimeout(() => {
        const target = this.diagnosticTarget
        const results = [
          `PING ${target} (${target}): 56 data bytes`,
          `64 bytes from ${target}: icmp_seq=0 ttl=64 time=1.234 ms`,
          `64 bytes from ${target}: icmp_seq=1 ttl=64 time=1.456 ms`,
          `64 bytes from ${target}: icmp_seq=2 ttl=64 time=1.123 ms`,
          `64 bytes from ${target}: icmp_seq=3 ttl=64 time=1.567 ms`,
          ``,
          `--- ${target} ping statistics ---`,
          `4 packets transmitted, 4 packets received, 0.0% packet loss`,
          `round-trip min/avg/max/stddev = 1.123/1.345/1.567/0.189 ms`
        ]
        this.diagnosticResult = results.join('\n')
        this.$emit('message', { type: 'success', text: 'Ping测试完成' })
      }, 2000)
    },

    async portScan() {
      if (!this.scanTarget.trim()) {
        this.$emit('message', { type: 'warning', text: '请输入扫描目标' })
        return
      }

      this.$emit('message', { type: 'info', text: `正在扫描 ${this.scanTarget} 的端口...` })

      // 模拟端口扫描结果
      setTimeout(() => {
        const target = this.scanTarget
        const ports = this.scanPorts
        const results = [
          `端口扫描结果 - 目标: ${target}`,
          `端口范围: ${ports}`,
          `扫描时间: ${new Date().toLocaleString()}`,
          ``,
          `开放端口:`,
          `22/tcp   open  ssh`,
          `80/tcp   open  http`,
          `443/tcp  open  https`,
          `3306/tcp open  mysql`,
          ``,
          `关闭端口:`,
          `21/tcp   closed ftp`,
          `23/tcp   closed telnet`,
          `25/tcp   closed smtp`,
          ``,
          `扫描完成 - 发现 4 个开放端口`
        ]
        this.diagnosticResult = results.join('\n')
        this.$emit('message', { type: 'success', text: '端口扫描完成' })
      }, 3000)
    },

    async showNetworkStats() {
      this.$emit('message', { type: 'info', text: '正在获取网络统计信息...' })

      setTimeout(() => {
        const results = [
          `网络接口统计信息`,
          `时间: ${new Date().toLocaleString()}`,
          ``,
          `eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500`,
          `        inet ${this.networkConfig.primaryIP}  netmask ${this.networkConfig.netmask}  broadcast 192.168.1.255`,
          `        inet6 fe80::42:acff:fe11:2  prefixlen 64  scopeid 0x20<link>`,
          `        ether 02:42:ac:11:00:02  txqueuelen 0  (Ethernet)`,
          `        RX packets 1234  bytes 567890 (554.5 KiB)`,
          `        RX errors 0  dropped 0  overruns 0  frame 0`,
          `        TX packets 987  bytes 123456 (120.5 KiB)`,
          `        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0`,
          ``,
          `lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536`,
          `        inet 127.0.0.1  netmask 255.0.0.0`,
          `        inet6 ::1  prefixlen 128  scopeid 0x10<host>`,
          `        loop  txqueuelen 1000  (Local Loopback)`,
          `        RX packets 0  bytes 0 (0.0 B)`,
          `        RX errors 0  dropped 0  overruns 0  frame 0`,
          `        TX packets 0  bytes 0 (0.0 B)`,
          `        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0`
        ]
        this.diagnosticResult = results.join('\n')
        this.$emit('message', { type: 'success', text: '网络统计信息获取完成' })
      }, 1000)
    },

    async showRoutingTable() {
      this.$emit('message', { type: 'info', text: '正在获取路由表信息...' })

      setTimeout(() => {
        const results = [
          `内核路由表`,
          `目标            网关            子网掩码        标志  跃点   引用  使用 接口`,
          `0.0.0.0         ${this.networkConfig.gateway}         0.0.0.0         UG    0      0        0 eth0`,
          `${this.networkConfig.network}   0.0.0.0         255.255.255.0   U     0      0        0 eth0`,
          `127.0.0.0       0.0.0.0         255.0.0.0       U     0      0        0 lo`,
          `169.254.0.0     0.0.0.0         255.255.0.0     U     1000   0        0 eth0`
        ]
        this.diagnosticResult = results.join('\n')
        this.$emit('message', { type: 'success', text: '路由表信息获取完成' })
      }, 1000)
    },

    async showARPTable() {
      this.$emit('message', { type: 'info', text: '正在获取ARP表信息...' })

      setTimeout(() => {
        const results = [
          `ARP表`,
          `地址                     类型    硬件地址            标志  掩码            接口`,
          `${this.networkConfig.gateway}              ether   02:42:ac:11:00:01   C                     eth0`,
          `192.168.1.100            ether   aa:bb:cc:dd:ee:ff   C                     eth0`,
          `192.168.1.200            ether   11:22:33:44:55:66   C                     eth0`
        ]
        this.diagnosticResult = results.join('\n')
        this.$emit('message', { type: 'success', text: 'ARP表信息获取完成' })
      }, 1000)
    },

    testData() {
      console.log('🧪 NetworkConfigPanel 测试数据:')
      console.log('  - container:', this.container)
      console.log('  - containerInfo:', this.containerInfo)
      console.log('  - networkConfig:', this.networkConfig)
      this.$emit('message', { type: 'info', text: '测试数据已输出到控制台' })
    }
  }
}
</script>

<style scoped>
.network-config-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.config-section {
  background-color: #27293d;
  border-radius: 8px;
  padding: 16px;
}

.config-section h4 {
  margin: 0 0 16px 0;
  color: #ffffff;
  font-size: 16px;
  border-bottom: 1px solid #2c2c40;
  padding-bottom: 8px;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.config-item.full-width {
  grid-column: 1 / -1;
}

.config-item label {
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  margin: 0;
}

.form-control,
.form-control-sm {
  background-color: #1e1e2f;
  border: 1px solid #2c2c40;
  border-radius: 4px;
  color: #ffffff;
  padding: 8px 12px;
  font-size: 14px;
}

.form-control-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.form-control:focus,
.form-control-sm:focus {
  outline: none;
  border-color: #1d8cf8;
  box-shadow: 0 0 0 2px rgba(29, 140, 248, 0.2);
}

.input-group {
  display: flex;
  gap: 8px;
}

.input-group .form-control {
  flex: 1;
}

.help-text {
  color: #a9a9a9;
  font-size: 12px;
}

.port-mappings {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.port-mapping-header {
  display: grid;
  grid-template-columns: 1fr 1fr 80px 2fr 80px;
  gap: 8px;
  padding: 8px;
  background-color: #1e1e2f;
  border-radius: 4px;
  font-weight: 500;
  color: #a9a9a9;
  font-size: 12px;
}

.port-mapping-row {
  display: grid;
  grid-template-columns: 1fr 1fr 80px 2fr 80px;
  gap: 8px;
  align-items: center;
}

.port-mapping-actions {
  margin-top: 8px;
}

.changes-preview {
  background-color: #27293d;
  border-radius: 8px;
  padding: 16px;
  border-left: 4px solid #1d8cf8;
}

.changes-preview h4 {
  margin: 0 0 12px 0;
  color: #1d8cf8;
  font-size: 14px;
}

.changes-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.change-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.change-field {
  color: #a9a9a9;
  min-width: 100px;
}

.change-arrow {
  color: #1d8cf8;
}

.change-value {
  color: #ffffff;
  font-weight: 500;
}

.btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  font-size: 12px;
  transition: all 0.3s ease;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 11px;
}

.btn-primary {
  background-color: #1d8cf8;
  color: white;
}

.btn-primary:hover {
  background-color: #3a9cfa;
}

.btn-danger {
  background-color: #fd5d93;
  color: white;
}

.btn-danger:hover {
  background-color: #ff7aa3;
}

.btn-outline {
  background-color: transparent;
  color: #1d8cf8;
  border: 1px solid #1d8cf8;
}

.btn-outline:hover {
  background-color: #1d8cf8;
  color: white;
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

.diagnostic-tools {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.tool-group {
  background-color: #1e1e2f;
  padding: 16px;
  border-radius: 6px;
}

.tool-group h5 {
  margin: 0 0 12px 0;
  color: #ffffff;
  font-size: 14px;
  border-bottom: 1px solid #2c2c40;
  padding-bottom: 8px;
}

.tool-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tool-actions .input-group {
  flex: 1;
  min-width: 200px;
}

.diagnostic-result {
  margin-top: 20px;
  background-color: #1e1e2f;
  padding: 16px;
  border-radius: 6px;
  border-left: 4px solid #1d8cf8;
}

.diagnostic-result h5 {
  margin: 0 0 12px 0;
  color: #1d8cf8;
  font-size: 14px;
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
  margin: 0;
  border: 1px solid #2c2c40;
}

.btn-info {
  background-color: #17a2b8;
  color: white;
}

.btn-info:hover {
  background-color: #138496;
}
</style>
