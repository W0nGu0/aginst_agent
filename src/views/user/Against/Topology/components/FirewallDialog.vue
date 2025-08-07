<template>
  <div v-if="show" class="firewall-dialog">
    <div class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content" @click.stop>
        <!-- 标题栏 -->
        <div class="dialog-header">
          <h3>防火墙配置</h3>
          <button class="close-btn" @click="closeDialog">&times;</button>
        </div>

        <!-- 基本信息 -->
        <div class="dialog-body">
          <div class="basic-info">
            <p><strong>名称:</strong> {{ firewallData.name }}</p>
            <p><strong>状态:</strong>
              <span :style="{ color: firewallData.status === 'running' ? '#00f2c3' : '#ff6b6b' }">
                {{ firewallData.status === 'running' ? '运行中' : '已停止' }}
              </span>
            </p>
            <p><strong>接口数量:</strong> {{ firewallData.interfaces.length }}</p>
          </div>

          <!-- 标签页 -->
          <div class="tabs">
            <button class="tab-btn" :class="{ active: activeTab === 'interfaces' }" @click="activeTab = 'interfaces'">
              接口
            </button>
            <button class="tab-btn" :class="{ active: activeTab === 'rules' }" @click="activeTab = 'rules'">
              访问规则
            </button>
            <button class="tab-btn" :class="{ active: activeTab === 'blacklist' }" @click="activeTab = 'blacklist'">
              黑名单
            </button>
            <button class="tab-btn" :class="{ active: activeTab === 'whitelist' }" @click="activeTab = 'whitelist'">
              白名单
            </button>
            <button class="tab-btn" :class="{ active: activeTab === 'logs' }" @click="activeTab = 'logs'">
              日志
            </button>
          </div>

          <!-- 内容区域 -->
          <div class="tab-content">
            <!-- 接口标签页 -->
            <div v-show="activeTab === 'interfaces'" class="content-panel">
              <h4>网络接口配置</h4>
              <div class="content-list">
                <div v-for="(networkInterface, index) in firewallData.interfaces" :key="index" class="content-item">
                  <strong>{{ networkInterface.name }}</strong> - {{ networkInterface.ip }} ({{ networkInterface.network
                  }}) -
                  <span :style="{ color: networkInterface.status === 'up' ? '#00f2c3' : '#ff6b6b' }">
                    {{ networkInterface.status === 'up' ? '活跃' : '停用' }}
                  </span>
                </div>
                <div v-if="firewallData.interfaces.length === 0" class="content-item text-center text-gray-500">
                  暂无接口配置
                </div>
              </div>
            </div>

            <!-- 访问规则标签页 -->
            <div v-show="activeTab === 'rules'" class="content-panel">
              <h4>访问控制规则</h4>
              <div class="content-list">
                <div v-for="(rule, index) in firewallData.rules" :key="index" class="content-item">
                  <span class="rule-badge" :class="rule.action">{{ rule.action === 'allow' ? '允许' : rule.action ===
                    'deny' ? '拒绝' : '阻断' }}</span>
                  {{ rule.source }} → {{ rule.dest }} ({{ rule.port }}) - {{ rule.desc }}
                </div>
                <div v-if="firewallData.rules.length === 0" class="content-item text-center text-gray-500">
                  暂无访问规则
                </div>
              </div>
            </div>

            <!-- 黑名单标签页 -->
            <div v-show="activeTab === 'blacklist'" class="content-panel">
              <div class="panel-header">
                <h4>IP/域名黑名单</h4>
                <button class="btn btn-sm btn-primary" @click="refreshBlacklist">
                  🔄 刷新
                </button>
              </div>
              <div class="content-list">
                <div v-for="(item, index) in blacklistItems" :key="index" class="content-item">
                  <span class="type-badge ip">{{ item.type }}</span>
                  {{ item.address }} - {{ item.reason }} -
                  <span :style="{ color: item.enabled ? '#00f2c3' : '#6c757d' }">
                    {{ item.enabled ? '启用' : '禁用' }}
                  </span>
                  <button class="btn btn-xs btn-error ml-2" @click="removeFromBlacklist(item.address)">
                    移除
                  </button>
                </div>
                <div v-if="blacklistItems.length === 0" class="content-item text-center text-gray-500">
                  暂无黑名单条目
                </div>
              </div>
              <div class="add-item-form">
                <input v-model="newBlacklistItem" type="text" placeholder="输入IP地址或域名" class="input input-sm">
                <input v-model="newBlacklistReason" type="text" placeholder="阻断原因" class="input input-sm">
                <button class="btn btn-sm btn-error" @click="addToBlacklist">添加到黑名单</button>
              </div>
            </div>

            <!-- 白名单标签页 -->
            <div v-show="activeTab === 'whitelist'" class="content-panel">
              <div class="panel-header">
                <h4>IP/域名白名单</h4>
                <button class="btn btn-sm btn-primary" @click="refreshWhitelist">
                  🔄 刷新
                </button>
              </div>
              <div class="content-list">
                <div v-for="(item, index) in whitelistItems" :key="index" class="content-item">
                  <span class="type-badge ip">{{ item.type }}</span>
                  {{ item.address }} - {{ item.description }} -
                  <span :style="{ color: item.enabled ? '#00f2c3' : '#6c757d' }">
                    {{ item.enabled ? '启用' : '禁用' }}
                  </span>
                  <button class="btn btn-xs btn-warning ml-2" @click="removeFromWhitelist(item.address)">
                    移除
                  </button>
                </div>
                <div v-if="whitelistItems.length === 0" class="content-item text-center text-gray-500">
                  暂无白名单条目
                </div>
              </div>
              <div class="add-item-form">
                <input v-model="newWhitelistItem" type="text" placeholder="输入IP地址或域名" class="input input-sm">
                <input v-model="newWhitelistDescription" type="text" placeholder="描述信息" class="input input-sm">
                <button class="btn btn-sm btn-success" @click="addToWhitelist">添加到白名单</button>
              </div>
            </div>

            <!-- 日志标签页 -->
            <div v-show="activeTab === 'logs'" class="content-panel">
              <h4>防火墙访问日志</h4>
              <div class="content-list">
                <div v-for="(log, index) in firewallData.logs" :key="index" class="content-item">
                  <span class="rule-badge" :class="log.action">{{ log.action === 'allow' ? '允许' : log.action === 'deny'
                    ? '拒绝' : '阻断' }}</span>
                  {{ log.time }} - {{ log.source }} → {{ log.dest }} ({{ log.port }})
                </div>
                <div v-if="firewallData.logs.length === 0" class="content-item text-center text-gray-500">
                  暂无访问日志
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部按钮 -->
        <div class="dialog-footer">
          <button class="btn btn-primary">保存更改</button>
          <button class="btn btn-secondary" @click="closeDialog">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FirewallDialog',
  emits: ['close'],
  props: {
    show: {
      type: Boolean,
      default: false
    },
    firewall: {
      type: Object,
      default: () => ({})
    }
  },
  watch: {
    show(newVal) {
      if (newVal && this.firewall) {
        this.loadFirewallData();
      }
    },
    firewall: {
      handler(newVal) {
        if (newVal && this.show) {
          this.loadFirewallData();
        }
      },
      deep: true
    }
  },
  data() {
    return {
      activeTab: 'interfaces',
      firewallData: {
        name: '',
        status: '',
        interfaces: [],
        rules: [],
        blacklist: [],
        whitelist: [],
        logs: []
      },
      blacklistItems: [],
      whitelistItems: [],
      newBlacklistItem: '',
      newBlacklistReason: '',
      newWhitelistItem: '',
      newWhitelistDescription: '',
      loading: false
    }
  },
  methods: {
    closeDialog() {
      this.$emit('close')
    },

    loadFirewallData() {
      if (!this.firewall || !this.firewall.deviceData) {
        console.warn('防火墙数据不完整:', this.firewall);
        this.loadDefaultData();
        return;
      }

      console.log('加载防火墙数据:', this.firewall);

      // 从防火墙设备数据中加载信息
      const deviceData = this.firewall.deviceData;
      const scenarioData = deviceData.scenarioData || {};

      this.firewallData = {
        name: deviceData.name || 'border_firewall',
        status: scenarioData.status || 'running',
        interfaces: this.generateInterfaceData(scenarioData),
        rules: this.generateRuleData(scenarioData),
        blacklist: scenarioData.blacklist || [],
        whitelist: scenarioData.whitelist || [],
        logs: this.generateLogData()
      };

      // 更新黑白名单显示数据
      this.blacklistItems = this.firewallData.blacklist.map(item => ({
        type: this.isValidIP(item.address) ? 'IP' : '域名',
        address: item.address,
        reason: item.reason || '未知原因',
        enabled: item.enabled !== false
      }));

      this.whitelistItems = this.firewallData.whitelist.map(item => ({
        type: this.isValidIP(item.address) ? 'IP' : '域名',
        address: item.address,
        description: item.description || '无描述',
        enabled: item.enabled !== false
      }));

      console.log('防火墙数据加载完成:', this.firewallData);
    },

    loadDefaultData() {
      // 加载默认数据
      this.firewallData = {
        name: 'border_firewall',
        status: 'running',
        interfaces: [
          { name: 'eth0', ip: '192.168.100.1', network: 'user_segment', status: 'up' },
          { name: 'eth1', ip: '192.168.200.1', network: 'server_segment', status: 'up' },
          { name: 'eth2', ip: '172.16.100.1', network: 'dmz_segment', status: 'up' },
          { name: 'eth3', ip: '172.203.100.1', network: 'internet', status: 'up' },
          { name: 'eth4', ip: '192.168.101.1', network: 'medical_segment', status: 'up' }
        ],
        rules: [
          { action: 'allow', source: '192.168.100.0/24', dest: '172.16.100.0/24', port: 'TCP:80,443', desc: '用户访问DMZ Web服务' },
          { action: 'deny', source: '192.168.100.0/24', dest: '192.168.200.0/24', port: 'TCP:3306', desc: '禁止用户直接访问数据库' },
          { action: 'allow', source: '172.16.100.0/24', dest: '192.168.200.0/24', port: 'TCP:3306', desc: 'DMZ访问内网数据库' }
        ],
        blacklist: [
          { address: '203.0.113.15', reason: '恶意IP地址', enabled: true },
          { address: 'malicious-site.com', reason: '恶意域名', enabled: true }
        ],
        whitelist: [
          { address: '192.168.100.50', description: '用户PC', enabled: true },
          { address: '8.8.8.8', description: 'Google DNS', enabled: true }
        ],
        logs: []
      };

      this.blacklistItems = [...this.firewallData.blacklist];
      this.whitelistItems = [...this.firewallData.whitelist];
    },

    generateInterfaceData(scenarioData) {
      // 根据场景数据生成接口信息
      const networks = scenarioData.networks || ['user_segment', 'server_segment', 'dmz_segment', 'internet', 'medical_segment'];
      const ipAddresses = scenarioData.ip_addresses || {};

      return networks.map((network, index) => ({
        name: `eth${index}`,
        ip: ipAddresses[network] || `192.168.${100 + index * 100}.1`,
        network: network,
        status: 'up'
      }));
    },

    generateRuleData(scenarioData) {
      // 生成默认防火墙规则
      return [
        { action: 'allow', source: '192.168.100.0/24', dest: '172.16.100.0/24', port: 'TCP:80,443', desc: '用户访问DMZ Web服务' },
        { action: 'deny', source: '192.168.100.0/24', dest: '192.168.200.0/24', port: 'TCP:3306', desc: '禁止用户直接访问数据库' },
        { action: 'allow', source: '172.16.100.0/24', dest: '192.168.200.0/24', port: 'TCP:3306', desc: 'DMZ访问内网数据库' },
        { action: 'allow', source: '192.168.200.0/24', dest: '192.168.66.0/24', port: 'TCP:514', desc: '允许SIEM日志收集' }
      ];
    },

    generateLogData() {
      // 生成模拟日志数据
      const now = new Date();
      const logs = [];

      for (let i = 0; i < 10; i++) {
        const time = new Date(now.getTime() - i * 60000); // 每分钟一条
        const actions = ['allow', 'deny', 'block'];
        const action = actions[Math.floor(Math.random() * actions.length)];

        logs.push({
          time: time.toLocaleString(),
          action: action,
          source: `192.168.${Math.floor(Math.random() * 3) + 1}00.${Math.floor(Math.random() * 254) + 1}`,
          dest: `192.168.${Math.floor(Math.random() * 3) + 1}00.${Math.floor(Math.random() * 254) + 1}`,
          port: `TCP:${[80, 443, 22, 3306, 53][Math.floor(Math.random() * 5)]}`
        });
      }

      return logs;
    },

    async refreshBlacklist() {
      try {
        // 这里可以调用防火墙控制服务获取最新的黑名单
        console.log('刷新黑名单数据')
        // 模拟API调用
        // const response = await fetch('/api/firewall/blacklist')
        // this.blacklistItems = await response.json()
      } catch (error) {
        console.error('刷新黑名单失败:', error)
      }
    },

    async refreshWhitelist() {
      try {
        // 这里可以调用防火墙控制服务获取最新的白名单
        console.log('刷新白名单数据')
        // 模拟API调用
        // const response = await fetch('/api/firewall/whitelist')
        // this.whitelistItems = await response.json()
      } catch (error) {
        console.error('刷新白名单失败:', error)
      }
    },

    addToBlacklist() {
      if (this.newBlacklistItem.trim() && this.newBlacklistReason.trim()) {
        const newItem = {
          type: this.isValidIP(this.newBlacklistItem) ? 'IP' : '域名',
          address: this.newBlacklistItem.trim(),
          reason: this.newBlacklistReason.trim(),
          enabled: true
        }

        // 检查是否已存在
        const exists = this.blacklistItems.some(item => item.address === newItem.address)
        if (!exists) {
          this.blacklistItems.push(newItem)

          // 从白名单中移除（如果存在）
          this.whitelistItems = this.whitelistItems.filter(item => item.address !== newItem.address)

          // 清空输入框
          this.newBlacklistItem = ''
          this.newBlacklistReason = ''

          // 触发防御动画
          this.$emit('firewall-updated', { action: 'blacklist_add', item: newItem })
        } else {
          alert('该地址已在黑名单中')
        }
      }
    },

    addToWhitelist() {
      if (this.newWhitelistItem.trim() && this.newWhitelistDescription.trim()) {
        const newItem = {
          type: this.isValidIP(this.newWhitelistItem) ? 'IP' : '域名',
          address: this.newWhitelistItem.trim(),
          description: this.newWhitelistDescription.trim(),
          enabled: true
        }

        // 检查是否已存在
        const exists = this.whitelistItems.some(item => item.address === newItem.address)
        if (!exists) {
          this.whitelistItems.push(newItem)

          // 从黑名单中移除（如果存在）
          this.blacklistItems = this.blacklistItems.filter(item => item.address !== newItem.address)

          // 清空输入框
          this.newWhitelistItem = ''
          this.newWhitelistDescription = ''

          // 触发防御动画
          this.$emit('firewall-updated', { action: 'whitelist_add', item: newItem })
        } else {
          alert('该地址已在白名单中')
        }
      }
    },

    removeFromBlacklist(address) {
      if (confirm(`确定要从黑名单中移除 ${address} 吗？`)) {
        const item = this.blacklistItems.find(item => item.address === address)
        this.blacklistItems = this.blacklistItems.filter(item => item.address !== address)

        // 触发防御动画
        this.$emit('firewall-updated', { action: 'blacklist_remove', item })
      }
    },

    removeFromWhitelist(address) {
      if (confirm(`确定要从白名单中移除 ${address} 吗？`)) {
        const item = this.whitelistItems.find(item => item.address === address)
        this.whitelistItems = this.whitelistItems.filter(item => item.address !== address)

        // 触发防御动画
        this.$emit('firewall-updated', { action: 'whitelist_remove', item })
      }
    },

    isValidIP(ip) {
      const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
      return ipRegex.test(ip)
    }
  },

  mounted() {
    if (this.show && this.firewall) {
      this.loadFirewallData();
    }
  }
}
</script>

<style scoped>
.firewall-dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
}

.dialog-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.dialog-content {
  background-color: #1e1e2f;
  border-radius: 8px;
  width: 700px;
  max-width: 90%;
  max-height: 80vh;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dialog-header {
  padding: 16px 20px;
  border-bottom: 1px solid #2c2c40;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #1e1e2f;
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
  border-radius: 4px;
}

.close-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.dialog-body {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
  background-color: #1e1e2f;
}

.basic-info {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #27293d;
  border-radius: 6px;
  border: 1px solid #2c2c40;
}

.basic-info p {
  margin: 8px 0;
  color: #ffffff;
  font-size: 14px;
}

.basic-info strong {
  color: #a9a9a9;
  margin-right: 8px;
}

.tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #2c2c40;
}

.tab-btn {
  padding: 10px 16px;
  background: none;
  border: none;
  color: #a9a9a9;
  cursor: pointer;
  font-size: 14px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #ffffff;
}

.tab-btn.active {
  color: #ffffff;
  border-bottom-color: #1d8cf8;
}

.tab-content {
  min-height: 300px;
}

.content-panel {
  display: block;
}

.content-panel h4 {
  margin: 0 0 16px 0;
  color: #1d8cf8;
  font-size: 16px;
}

.content-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.content-item {
  background-color: #27293d;
  border: 1px solid #2c2c40;
  border-radius: 6px;
  padding: 12px 16px;
  color: #ffffff;
  font-size: 14px;
  line-height: 1.4;
}

.rule-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  margin-right: 8px;
  min-width: 40px;
  text-align: center;
}

.rule-badge.allow {
  background-color: #00f2c3;
  color: #000;
}

.rule-badge.deny {
  background-color: #fd5d93;
  color: white;
}

.rule-badge.block {
  background-color: #ef4444;
  color: white;
}

.type-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  margin-right: 8px;
  min-width: 35px;
  text-align: center;
}

.type-badge.ip {
  background-color: #3b82f6;
  color: white;
}

.type-badge.domain {
  background-color: #10b981;
  color: white;
}

.type-badge.subnet {
  background-color: #8b5cf6;
  color: white;
}

.dialog-footer {
  padding: 16px 20px;
  border-top: 1px solid #2c2c40;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  background-color: #1e1e2f;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
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

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.panel-header h4 {
  margin: 0;
}

.add-item-form {
  display: flex;
  gap: 8px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #374151;
}

.add-item-form .input {
  flex: 1;
  background: #1f2937;
  border: 1px solid #374151;
  color: #ffffff;
  padding: 6px 12px;
  border-radius: 4px;
}

.add-item-form .input::placeholder {
  color: #9ca3af;
}

.add-item-form .btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 12px;
  white-space: nowrap;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn-xs {
  padding: 2px 6px;
  font-size: 10px;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-error {
  background: #ef4444;
  color: white;
}

.btn-warning {
  background: #f59e0b;
  color: white;
}

.btn:hover {
  opacity: 0.8;
}

.ml-2 {
  margin-left: 8px;
}

.text-center {
  text-align: center;
}

.text-gray-500 {
  color: #6b7280;
}
</style>