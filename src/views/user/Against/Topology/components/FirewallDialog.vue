<template>
  <div class="firewall-dialog">
    <div v-if="show" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>防火墙配置</h3>
          <button class="close-btn" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="firewall-info">
            <div class="info-item">
              <span class="label">名称:</span>
              <span class="value">{{ firewall.deviceData?.name }}</span>
            </div>
            <div class="info-item">
              <span class="label">状态:</span>
              <span class="value" :class="statusClass">{{ statusText }}</span>
            </div>
            <div class="info-item">
              <span class="label">接口数量:</span>
              <span class="value">{{ interfaces.length }}</span>
            </div>
          </div>

          <div class="tabs">
            <div 
              class="tab" 
              :class="{ active: activeTab === 'interfaces' }"
              @click="activeTab = 'interfaces'"
            >
              接口
            </div>
            <div 
              class="tab" 
              :class="{ active: activeTab === 'rules' }"
              @click="activeTab = 'rules'"
            >
              规则
            </div>
            <div 
              class="tab" 
              :class="{ active: activeTab === 'logs' }"
              @click="activeTab = 'logs'"
            >
              日志
            </div>
          </div>

          <div class="tab-content">
            <!-- 接口选项卡 -->
            <div v-if="activeTab === 'interfaces'" class="interfaces-tab">
              <table class="interfaces-table">
                <thead>
                  <tr>
                    <th>接口名称</th>
                    <th>IP地址</th>
                    <th>网段</th>
                    <th>状态</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(iface, index) in interfaces" :key="index">
                    <td>{{ iface.name }}</td>
                    <td>{{ iface.ip }}</td>
                    <td>{{ iface.subnet }}</td>
                    <td>
                      <span class="status-badge" :class="{ 'active': iface.active }">
                        {{ iface.active ? '活跃' : '禁用' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- 规则选项卡 -->
            <div v-if="activeTab === 'rules'" class="rules-tab">
              <div class="rules-actions">
                <button class="btn btn-primary" @click="addRule">添加规则</button>
              </div>
              <table class="rules-table">
                <thead>
                  <tr>
                    <th>序号</th>
                    <th>动作</th>
                    <th>源地址</th>
                    <th>目标地址</th>
                    <th>协议</th>
                    <th>端口</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(rule, index) in rules" :key="index">
                    <td>{{ index + 1 }}</td>
                    <td>
                      <span class="action-badge" :class="rule.action">
                        {{ rule.action === 'allow' ? '允许' : '拒绝' }}
                      </span>
                    </td>
                    <td>{{ rule.source }}</td>
                    <td>{{ rule.destination }}</td>
                    <td>{{ rule.protocol }}</td>
                    <td>{{ rule.port }}</td>
                    <td>
                      <button class="btn btn-sm btn-danger" @click="deleteRule(index)">删除</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- 日志选项卡 -->
            <div v-if="activeTab === 'logs'" class="logs-tab">
              <div class="log-filters">
                <select v-model="logFilter" class="log-filter-select">
                  <option value="all">全部日志</option>
                  <option value="allow">允许</option>
                  <option value="deny">拒绝</option>
                </select>
                <button class="btn btn-secondary" @click="refreshLogs">刷新</button>
              </div>
              <div class="log-entries">
                <div 
                  v-for="(log, index) in filteredLogs" 
                  :key="index"
                  class="log-entry"
                  :class="{ 'allow': log.action === 'allow', 'deny': log.action === 'deny' }"
                >
                  <div class="log-time">{{ log.timestamp }}</div>
                  <div class="log-message">
                    <span class="action-badge" :class="log.action">
                      {{ log.action === 'allow' ? '允许' : '拒绝' }}
                    </span>
                    <span>{{ log.source }} → {{ log.destination }}</span>
                    <span>{{ log.protocol }} {{ log.port ? ':' + log.port : '' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-primary" @click="saveChanges">保存更改</button>
          <button class="btn btn-secondary" @click="closeDialog">取消</button>
        </div>
      </div>
    </div>

    <!-- 添加规则对话框 -->
    <div v-if="showAddRuleDialog" class="dialog-overlay" @click="showAddRuleDialog = false">
      <div class="dialog-content add-rule-dialog" @click.stop>
        <div class="dialog-header">
          <h3>添加防火墙规则</h3>
          <button class="close-btn" @click="showAddRuleDialog = false">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>动作</label>
            <select v-model="newRule.action" class="form-control">
              <option value="allow">允许</option>
              <option value="deny">拒绝</option>
            </select>
          </div>
          <div class="form-group">
            <label>源地址</label>
            <input type="text" v-model="newRule.source" class="form-control" placeholder="例如: 192.168.1.0/24, any">
          </div>
          <div class="form-group">
            <label>目标地址</label>
            <input type="text" v-model="newRule.destination" class="form-control" placeholder="例如: 10.0.0.1, any">
          </div>
          <div class="form-group">
            <label>协议</label>
            <select v-model="newRule.protocol" class="form-control">
              <option value="any">任意</option>
              <option value="tcp">TCP</option>
              <option value="udp">UDP</option>
              <option value="icmp">ICMP</option>
            </select>
          </div>
          <div class="form-group">
            <label>端口</label>
            <input type="text" v-model="newRule.port" class="form-control" placeholder="例如: 80, 443, 1-1024">
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-primary" @click="confirmAddRule">添加</button>
          <button class="btn btn-secondary" @click="showAddRuleDialog = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FirewallDialog',
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
  data() {
    return {
      activeTab: 'interfaces',
      interfaces: [],
      rules: [],
      logs: [],
      logFilter: 'all',
      showAddRuleDialog: false,
      newRule: {
        action: 'allow',
        source: 'any',
        destination: 'any',
        protocol: 'any',
        port: ''
      }
    };
  },
  computed: {
    statusText() {
      if (!this.firewall.deviceData) return '未知';
      return this.firewall.deviceData.status === 'running' ? '运行中' : 
             this.firewall.deviceData.status === 'failed' ? '失败' : '已停止';
    },
    statusClass() {
      if (!this.firewall.deviceData) return '';
      return this.firewall.deviceData.status === 'running' ? 'status-running' : 
             this.firewall.deviceData.status === 'failed' ? 'status-failed' : 'status-stopped';
    },
    filteredLogs() {
      if (this.logFilter === 'all') return this.logs;
      return this.logs.filter(log => log.action === this.logFilter);
    }
  },
  watch: {
    firewall: {
      immediate: true,
      handler(newVal) {
        if (newVal && newVal.id) {
          this.loadFirewallData();
        }
      }
    },
    show(newVal) {
      if (newVal) {
        this.loadFirewallData();
      }
    }
  },
  methods: {
    loadFirewallData() {
      // 在实际应用中，这里应该从后端API获取防火墙数据
      // 这里使用模拟数据进行演示
      this.loadInterfaces();
      this.loadRules();
      this.loadLogs();
    },
    loadInterfaces() {
      // 模拟从后端获取接口数据
      const firewallName = this.firewall.deviceData?.name || '';
      
      if (firewallName === '内部防火墙') {
        this.interfaces = [
          { name: 'eth0', ip: '192.168.200.254', subnet: '192.168.200.0/24', active: true },
          { name: 'eth1', ip: '192.168.100.254', subnet: '192.168.100.0/24', active: true },
          { name: 'eth2', ip: '192.168.66.254', subnet: '192.168.66.0/24', active: true },
          { name: 'eth3', ip: '192.168.110.254', subnet: '192.168.110.0/24', active: true },
          { name: 'eth4', ip: '192.168.214.254', subnet: '192.168.214.0/24', active: true },
          { name: 'eth5', ip: '192.168.254.3', subnet: '192.168.254.0/29', active: true }
        ];
      } else if (firewallName === '外部防火墙') {
        this.interfaces = [
          { name: 'eth0', ip: '172.16.100.254', subnet: '172.16.100.0/24', active: true },
          { name: 'eth1', ip: '199.203.100.2', subnet: '199.203.100.0/24', active: true },
          { name: 'eth2', ip: '192.168.254.2', subnet: '192.168.254.0/29', active: true }
        ];
      } else {
        this.interfaces = [];
      }
    },
    loadRules() {
      // 模拟从后端获取规则数据
      this.rules = [
        { action: 'allow', source: 'any', destination: 'any', protocol: 'icmp', port: '' },
        { action: 'allow', source: '192.168.100.0/24', destination: '192.168.200.0/24', protocol: 'tcp', port: '80,443' },
        { action: 'deny', source: 'any', destination: '192.168.200.23', protocol: 'tcp', port: '3306' }
      ];
    },
    loadLogs() {
      // 模拟从后端获取日志数据
      this.logs = [
        { timestamp: '2025-07-18 17:42:15', action: 'allow', source: '192.168.100.9', destination: '192.168.200.23', protocol: 'TCP', port: '80' },
        { timestamp: '2025-07-18 17:41:32', action: 'deny', source: '199.203.100.10', destination: '192.168.200.23', protocol: 'TCP', port: '3306' },
        { timestamp: '2025-07-18 17:40:18', action: 'allow', source: '192.168.100.34', destination: '192.168.200.6', protocol: 'TCP', port: '445' },
        { timestamp: '2025-07-18 17:39:45', action: 'deny', source: '199.203.100.10', destination: '172.16.100.53', protocol: 'UDP', port: '53' }
      ];
    },
    refreshLogs() {
      // 在实际应用中，这里应该从后端API刷新日志数据
      this.loadLogs();
    },
    addRule() {
      this.newRule = {
        action: 'allow',
        source: 'any',
        destination: 'any',
        protocol: 'any',
        port: ''
      };
      this.showAddRuleDialog = true;
    },
    confirmAddRule() {
      this.rules.push({ ...this.newRule });
      this.showAddRuleDialog = false;
    },
    deleteRule(index) {
      this.rules.splice(index, 1);
    },
    saveChanges() {
      // 在实际应用中，这里应该将更改保存到后端API
      this.$emit('save', {
        interfaces: this.interfaces,
        rules: this.rules
      });
      this.closeDialog();
    },
    closeDialog() {
      this.$emit('close');
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
  width: 800px;
  max-width: 90%;
  max-height: 90%;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
}

.add-rule-dialog {
  width: 500px;
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

.firewall-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  align-items: center;
}

.label {
  font-weight: bold;
  margin-right: 8px;
  color: #a9a9a9;
}

.value {
  color: #ffffff;
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

.tabs {
  display: flex;
  border-bottom: 1px solid #2c2c40;
}

.tab {
  padding: 8px 16px;
  cursor: pointer;
  color: #a9a9a9;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab:hover {
  color: #ffffff;
}

.tab.active {
  color: #ffffff;
  border-bottom-color: #1d8cf8;
}

.tab-content {
  padding: 16px 0;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid #2c2c40;
}

th {
  color: #a9a9a9;
  font-weight: normal;
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  background-color: #6c757d;
  color: white;
}

.status-badge.active {
  background-color: #00f2c3;
}

.action-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  color: white;
}

.action-badge.allow {
  background-color: #00f2c3;
}

.action-badge.deny {
  background-color: #fd5d93;
}

.rules-actions {
  margin-bottom: 16px;
}

.log-filters {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.log-filter-select {
  padding: 6px 12px;
  border-radius: 4px;
  background-color: #27293d;
  border: 1px solid #2c2c40;
  color: #ffffff;
}

.log-entries {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.log-entry {
  padding: 8px;
  border-radius: 4px;
  background-color: #27293d;
  display: flex;
  flex-direction: column;
}

.log-time {
  font-size: 12px;
  color: #a9a9a9;
  margin-bottom: 4px;
}

.log-message {
  display: flex;
  gap: 8px;
  align-items: center;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  color: #a9a9a9;
}

.form-control {
  width: 100%;
  padding: 8px;
  border-radius: 4px;
  background-color: #27293d;
  border: 1px solid #2c2c40;
  color: #ffffff;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: bold;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
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

.btn-danger {
  background-color: #fd5d93;
  color: white;
}

.btn-danger:hover {
  background-color: #fd77a4;
}
</style>