<template>
  <div class="firewall-config-panel">
    <!-- 简单的数据状态显示 -->
    <div class="debug-status" style="background: #1e1e2f; padding: 8px; margin-bottom: 16px; border-radius: 4px; font-size: 12px; color: #a9a9a9;">
      防火墙数据: 规则={{ firewallConfig.rules.length }}, 白名单={{ firewallConfig.whitelist.length }}, 黑名单={{ firewallConfig.blacklist.length }}
    </div>
    
    <div class="config-section">
      <h4>🔥 防火墙规则</h4>
      
      <!-- 规则操作栏 -->
      <div class="rules-actions">
        <button class="btn btn-primary" @click="addRule">+ 添加规则</button>
        <button class="btn btn-secondary" @click="importRules">📥 导入规则</button>
        <button class="btn btn-secondary" @click="exportRules">📤 导出规则</button>
        <div class="rules-stats">
          <span>总规则: {{ firewallConfig.rules.length }}</span>
          <span>允许: {{ allowRulesCount }}</span>
          <span>拒绝: {{ denyRulesCount }}</span>
        </div>
      </div>

      <!-- 规则列表 -->
      <div class="rules-table">
        <div class="rules-header">
          <span>序号</span>
          <span>动作</span>
          <span>源地址</span>
          <span>目标地址</span>
          <span>协议</span>
          <span>端口</span>
          <span>描述</span>
          <span>状态</span>
          <span>操作</span>
        </div>
        
        <div 
          v-for="(rule, index) in firewallConfig.rules" 
          :key="index"
          class="rule-row"
          :class="{ 'rule-disabled': !rule.enabled }"
        >
          <span class="rule-index">{{ index + 1 }}</span>
          <span class="rule-action" :class="rule.action">
            {{ rule.action === 'allow' ? '允许' : '拒绝' }}
          </span>
          <span class="rule-source">{{ rule.source }}</span>
          <span class="rule-destination">{{ rule.destination }}</span>
          <span class="rule-protocol">{{ rule.protocol.toUpperCase() }}</span>
          <span class="rule-port">{{ rule.port || 'ANY' }}</span>
          <span class="rule-description">{{ rule.description || '-' }}</span>
          <span class="rule-status">
            <label class="toggle-switch">
              <input 
                type="checkbox" 
                v-model="rule.enabled"
                @change="markChanged('rules')"
              >
              <span class="toggle-slider"></span>
            </label>
          </span>
          <span class="rule-actions">
            <button class="btn btn-sm btn-outline" @click="editRule(index)">编辑</button>
            <button class="btn btn-sm btn-danger" @click="deleteRule(index)">删除</button>
          </span>
        </div>

        <div v-if="firewallConfig.rules.length === 0" class="empty-rules">
          <p>暂无防火墙规则</p>
          <button class="btn btn-primary" @click="addRule">添加第一条规则</button>
        </div>
      </div>
    </div>

    <div class="config-section">
      <h4>📋 白名单/黑名单</h4>
      
      <div class="list-tabs">
        <div 
          class="list-tab" 
          :class="{ active: activeListTab === 'whitelist' }"
          @click="activeListTab = 'whitelist'"
        >
          ✅ 白名单
        </div>
        <div 
          class="list-tab" 
          :class="{ active: activeListTab === 'blacklist' }"
          @click="activeListTab = 'blacklist'"
        >
          ❌ 黑名单
        </div>
      </div>

      <!-- 白名单 -->
      <div v-if="activeListTab === 'whitelist'" class="ip-list">
        <div class="list-actions">
          <div class="input-group">
            <input 
              type="text" 
              v-model="newWhitelistIP" 
              class="form-control"
              placeholder="输入IP地址或CIDR (例如: 192.168.1.100 或 192.168.1.0/24)"
              @keyup.enter="addToWhitelist"
            >
            <button class="btn btn-primary" @click="addToWhitelist">添加</button>
          </div>
        </div>
        
        <div class="ip-items">
          <div 
            v-for="(ip, index) in firewallConfig.whitelist" 
            :key="index"
            class="ip-item whitelist-item"
          >
            <div class="ip-main-info">
              <span class="ip-address">{{ ip.address }}</span>
              <span class="ip-description">{{ ip.description || '无描述' }}</span>
            </div>
            <div class="ip-meta-info">
              <span class="ip-added-time">添加时间: {{ ip.addedAt || '未知' }}</span>
            </div>
            <span class="ip-actions">
              <button class="btn btn-sm btn-outline" @click="editWhitelistItem(index)">编辑</button>
              <button class="btn btn-sm btn-danger" @click="removeFromWhitelist(index)">删除</button>
            </span>
          </div>
          
          <div v-if="firewallConfig.whitelist.length === 0" class="empty-list">
            <p>暂无白名单条目</p>
            <small>白名单中的IP地址将被允许访问此容器</small>
          </div>
        </div>
      </div>

      <!-- 黑名单 -->
      <div v-if="activeListTab === 'blacklist'" class="ip-list">
        <div class="list-actions">
          <div class="input-group">
            <input 
              type="text" 
              v-model="newBlacklistIP" 
              class="form-control"
              placeholder="输入IP地址或CIDR (例如: 192.168.1.100 或 192.168.1.0/24)"
              @keyup.enter="addToBlacklist"
            >
            <button class="btn btn-primary" @click="addToBlacklist">添加</button>
          </div>
        </div>
        
        <div class="ip-items">
          <div 
            v-for="(ip, index) in firewallConfig.blacklist" 
            :key="index"
            class="ip-item blacklist-item"
          >
            <div class="ip-main-info">
              <span class="ip-address">{{ ip.address }}</span>
              <span class="ip-description">{{ ip.description || '无描述' }}</span>
            </div>
            <div class="ip-meta-info">
              <span class="ip-added-time">添加时间: {{ ip.addedAt || '未知' }}</span>
              <span class="ip-reason" v-if="ip.reason">原因: {{ ip.reason }}</span>
            </div>
            <span class="ip-actions">
              <button class="btn btn-sm btn-outline" @click="editBlacklistItem(index)">编辑</button>
              <button class="btn btn-sm btn-danger" @click="removeFromBlacklist(index)">删除</button>
            </span>
          </div>
          
          <div v-if="firewallConfig.blacklist.length === 0" class="empty-list">
            <p>暂无黑名单条目</p>
            <small>黑名单中的IP地址将被拒绝访问此容器</small>
          </div>
        </div>
      </div>
    </div>

    <div class="config-section">
      <h4>⚙️ 防火墙设置</h4>
      
      <div class="config-grid">
        <div class="config-item">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              v-model="firewallConfig.enabled"
              @change="markChanged('enabled')"
            >
            启用防火墙
          </label>
          <small class="help-text">启用或禁用防火墙功能</small>
        </div>

        <div class="config-item">
          <label>默认策略</label>
          <select v-model="firewallConfig.defaultPolicy" class="form-control" @change="markChanged('defaultPolicy')">
            <option value="allow">允许 (ACCEPT)</option>
            <option value="deny">拒绝 (DROP)</option>
            <option value="reject">拒绝并回复 (REJECT)</option>
          </select>
          <small class="help-text">未匹配规则时的默认动作</small>
        </div>

        <div class="config-item">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              v-model="firewallConfig.logEnabled"
              @change="markChanged('logEnabled')"
            >
            启用日志记录
          </label>
          <small class="help-text">记录防火墙活动日志</small>
        </div>

        <div class="config-item">
          <label>日志级别</label>
          <select v-model="firewallConfig.logLevel" class="form-control" @change="markChanged('logLevel')">
            <option value="debug">调试</option>
            <option value="info">信息</option>
            <option value="warning">警告</option>
            <option value="error">错误</option>
          </select>
          <small class="help-text">日志记录的详细程度</small>
        </div>
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

    <!-- 添加/编辑规则对话框 -->
    <div v-if="showRuleDialog" class="rule-dialog-overlay" @click="closeRuleDialog">
      <div class="rule-dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ editingRuleIndex >= 0 ? '编辑规则' : '添加规则' }}</h3>
          <button class="close-btn" @click="closeRuleDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>动作</label>
            <select v-model="editingRule.action" class="form-control">
              <option value="allow">允许</option>
              <option value="deny">拒绝</option>
            </select>
          </div>
          <div class="form-group">
            <label>源地址</label>
            <input type="text" v-model="editingRule.source" class="form-control" placeholder="例如: 192.168.1.0/24, any">
          </div>
          <div class="form-group">
            <label>目标地址</label>
            <input type="text" v-model="editingRule.destination" class="form-control" placeholder="例如: 192.168.1.100, any">
          </div>
          <div class="form-group">
            <label>协议</label>
            <select v-model="editingRule.protocol" class="form-control">
              <option value="any">任意</option>
              <option value="tcp">TCP</option>
              <option value="udp">UDP</option>
              <option value="icmp">ICMP</option>
            </select>
          </div>
          <div class="form-group">
            <label>端口</label>
            <input type="text" v-model="editingRule.port" class="form-control" placeholder="例如: 80, 80-90, any">
          </div>
          <div class="form-group">
            <label>描述</label>
            <input type="text" v-model="editingRule.description" class="form-control" placeholder="规则描述">
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="editingRule.enabled">
              启用此规则
            </label>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-primary" @click="saveRule">保存</button>
          <button class="btn btn-secondary" @click="closeRuleDialog">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FirewallConfigPanel',
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
      firewallConfig: {
        enabled: true,
        defaultPolicy: 'deny',
        logEnabled: true,
        logLevel: 'info',
        rules: [],
        whitelist: [],
        blacklist: []
      },
      originalConfig: {},
      changedFields: new Set(),
      activeListTab: 'whitelist',
      newWhitelistIP: '',
      newBlacklistIP: '',
      showRuleDialog: false,
      editingRule: {
        action: 'allow',
        source: 'any',
        destination: 'any',
        protocol: 'any',
        port: '',
        description: '',
        enabled: true
      },
      editingRuleIndex: -1
    }
  },
  computed: {
    hasChanges() {
      return this.changedFields.size > 0
    },
    pendingChanges() {
      return Array.from(this.changedFields).map(field => ({
        field,
        newValue: this.formatFieldValue(field, this.firewallConfig[field])
      }))
    },
    allowRulesCount() {
      return this.firewallConfig.rules.filter(rule => rule.action === 'allow').length
    },
    denyRulesCount() {
      return this.firewallConfig.rules.filter(rule => rule.action === 'deny').length
    }
  },
  watch: {
    containerInfo: {
      immediate: true,
      handler(newVal) {
        console.log('🔄 FirewallConfigPanel: containerInfo 变化', newVal)
        if (newVal) {
          this.loadFirewallConfig()
        }
      }
    }
  },
  mounted() {
    console.log('🚀 FirewallConfigPanel mounted, containerInfo:', this.containerInfo)
    // 如果已经有容器信息，立即加载配置
    if (this.containerInfo && Object.keys(this.containerInfo).length > 0) {
      this.loadFirewallConfig()
    }
  },
  methods: {
    loadFirewallConfig() {
      console.log('🔥 FirewallConfigPanel: 加载防火墙配置', this.containerInfo)
      
      const info = this.containerInfo
      this.firewallConfig = {
        enabled: info.firewallEnabled !== false,
        defaultPolicy: info.defaultPolicy || 'deny',
        logEnabled: info.logEnabled !== false,
        logLevel: info.logLevel || 'info',
        rules: info.firewallRules || [],
        whitelist: info.whitelist || [],
        blacklist: info.blacklist || []
      }
      
      console.log('✅ FirewallConfigPanel: 防火墙配置已加载', this.firewallConfig)
      
      this.originalConfig = JSON.parse(JSON.stringify(this.firewallConfig))
      this.changedFields.clear()
    },

    markChanged(field) {
      this.changedFields.add(field)
      this.emitUpdate()
    },

    emitUpdate() {
      const changes = {}
      this.changedFields.forEach(field => {
        changes[field] = this.firewallConfig[field]
      })
      this.$emit('update', changes)
    },

    addRule() {
      this.editingRule = {
        action: 'allow',
        source: 'any',
        destination: 'any',
        protocol: 'any',
        port: '',
        description: '',
        enabled: true
      }
      this.editingRuleIndex = -1
      this.showRuleDialog = true
    },

    editRule(index) {
      this.editingRule = { ...this.firewallConfig.rules[index] }
      this.editingRuleIndex = index
      this.showRuleDialog = true
    },

    saveRule() {
      if (this.editingRuleIndex >= 0) {
        this.firewallConfig.rules[this.editingRuleIndex] = { ...this.editingRule }
      } else {
        this.firewallConfig.rules.push({ ...this.editingRule })
      }
      this.markChanged('rules')
      this.closeRuleDialog()
    },

    deleteRule(index) {
      if (confirm('确定要删除这条规则吗？')) {
        this.firewallConfig.rules.splice(index, 1)
        this.markChanged('rules')
      }
    },

    closeRuleDialog() {
      this.showRuleDialog = false
    },

    addToWhitelist() {
      if (this.newWhitelistIP.trim()) {
        this.firewallConfig.whitelist.push({
          address: this.newWhitelistIP.trim(),
          description: '',
          addedAt: new Date().toLocaleString('zh-CN')
        })
        this.newWhitelistIP = ''
        this.markChanged('whitelist')
        this.$emit('message', { type: 'success', text: `已添加白名单: ${this.newWhitelistIP.trim()}` })
      }
    },

    editWhitelistItem(index) {
      const item = this.firewallConfig.whitelist[index]
      const newDescription = prompt('请输入描述信息:', item.description || '')
      if (newDescription !== null) {
        item.description = newDescription
        this.markChanged('whitelist')
        this.$emit('message', { type: 'success', text: '白名单条目已更新' })
      }
    },

    removeFromWhitelist(index) {
      if (confirm('确定要删除这个白名单条目吗？')) {
        const item = this.firewallConfig.whitelist[index]
        this.firewallConfig.whitelist.splice(index, 1)
        this.markChanged('whitelist')
        this.$emit('message', { type: 'success', text: `已删除白名单: ${item.address}` })
      }
    },

    addToBlacklist() {
      if (this.newBlacklistIP.trim()) {
        const reason = prompt('请输入加入黑名单的原因:', '手动添加')
        this.firewallConfig.blacklist.push({
          address: this.newBlacklistIP.trim(),
          description: '',
          reason: reason || '手动添加',
          addedAt: new Date().toLocaleString('zh-CN')
        })
        this.newBlacklistIP = ''
        this.markChanged('blacklist')
        this.$emit('message', { type: 'success', text: `已添加黑名单: ${this.newBlacklistIP.trim()}` })
      }
    },

    editBlacklistItem(index) {
      const item = this.firewallConfig.blacklist[index]
      const newDescription = prompt('请输入描述信息:', item.description || '')
      if (newDescription !== null) {
        const newReason = prompt('请输入原因:', item.reason || '')
        if (newReason !== null) {
          item.description = newDescription
          item.reason = newReason
          this.markChanged('blacklist')
          this.$emit('message', { type: 'success', text: '黑名单条目已更新' })
        }
      }
    },

    removeFromBlacklist(index) {
      if (confirm('确定要删除这个黑名单条目吗？')) {
        const item = this.firewallConfig.blacklist[index]
        this.firewallConfig.blacklist.splice(index, 1)
        this.markChanged('blacklist')
        this.$emit('message', { type: 'success', text: `已删除黑名单: ${item.address}` })
      }
    },

    importRules() {
      // TODO: 实现规则导入功能
      this.$emit('message', { type: 'info', text: '规则导入功能开发中...' })
    },

    exportRules() {
      // TODO: 实现规则导出功能
      this.$emit('message', { type: 'info', text: '规则导出功能开发中...' })
    },

    getFieldDisplayName(field) {
      const displayNames = {
        enabled: '防火墙状态',
        defaultPolicy: '默认策略',
        logEnabled: '日志记录',
        logLevel: '日志级别',
        rules: '防火墙规则',
        whitelist: '白名单',
        blacklist: '黑名单'
      }
      return displayNames[field] || field
    },

    formatFieldValue(field, value) {
      if (field === 'rules') {
        return `${value.length} 条规则`
      }
      if (field === 'whitelist') {
        return `${value.length} 个IP`
      }
      if (field === 'blacklist') {
        return `${value.length} 个IP`
      }
      if (typeof value === 'boolean') {
        return value ? '启用' : '禁用'
      }
      return String(value)
    }
  }
}
</script>

<style scoped>
/* 基础样式继承自NetworkConfigPanel，这里只添加特有样式 */
.firewall-config-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.rules-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;
}

.rules-stats {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #a9a9a9;
}

.rules-table {
  border: 1px solid #2c2c40;
  border-radius: 6px;
  overflow: hidden;
}

.rules-header {
  display: grid;
  grid-template-columns: 50px 80px 120px 120px 80px 80px 150px 80px 120px;
  gap: 8px;
  padding: 12px 8px;
  background-color: #1e1e2f;
  font-weight: 500;
  color: #a9a9a9;
  font-size: 12px;
}

.rule-row {
  display: grid;
  grid-template-columns: 50px 80px 120px 120px 80px 80px 150px 80px 120px;
  gap: 8px;
  padding: 12px 8px;
  border-top: 1px solid #2c2c40;
  align-items: center;
  font-size: 12px;
}

.rule-row.rule-disabled {
  opacity: 0.5;
}

.rule-action.allow {
  color: #00f2c3;
}

.rule-action.deny {
  color: #fd5d93;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #2c2c40;
  transition: .4s;
  border-radius: 20px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #1d8cf8;
}

input:checked + .toggle-slider:before {
  transform: translateX(20px);
}

.list-tabs {
  display: flex;
  margin-bottom: 16px;
  border-bottom: 1px solid #2c2c40;
}

.list-tab {
  padding: 8px 16px;
  cursor: pointer;
  color: #a9a9a9;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.list-tab:hover {
  color: #ffffff;
}

.list-tab.active {
  color: #1d8cf8;
  border-bottom-color: #1d8cf8;
}

.ip-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ip-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ip-item {
  display: grid;
  grid-template-columns: 1fr 120px;
  gap: 12px;
  padding: 12px;
  background-color: #1e1e2f;
  border-radius: 6px;
  font-size: 12px;
  border-left: 4px solid transparent;
}

.ip-item.whitelist-item {
  border-left-color: #00f2c3;
}

.ip-item.blacklist-item {
  border-left-color: #fd5d93;
}

.ip-main-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.ip-meta-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 4px;
}

.ip-address {
  font-family: monospace;
  color: #ffffff;
  font-weight: 600;
  font-size: 13px;
}

.ip-description {
  color: #a9a9a9;
  font-size: 11px;
}

.ip-added-time {
  color: #6c757d;
  font-size: 10px;
}

.ip-reason {
  color: #fd5d93;
  font-size: 10px;
  font-weight: 500;
}

.empty-list {
  text-align: center;
  padding: 40px 20px;
  color: #a9a9a9;
  background-color: #1e1e2f;
  border-radius: 6px;
  border: 2px dashed #2c2c40;
}

.empty-list p {
  margin: 0 0 8px 0;
  font-size: 14px;
}

.empty-list small {
  font-size: 11px;
  color: #6c757d;
}

.empty-rules {
  text-align: center;
  padding: 40px;
  color: #a9a9a9;
}

.rule-dialog-overlay {
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

.rule-dialog {
  background-color: #1e1e2f;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  color: #ffffff;
  font-size: 14px;
}
</style>
