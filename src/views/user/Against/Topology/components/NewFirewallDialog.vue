<template>
  <div v-if="show" class="firewall-dialog-overlay" @click="handleOverlayClick">
    <div class="firewall-dialog-container" @click.stop>
      <!-- 标题栏 -->
      <div class="dialog-header">
        <div class="header-left">
          <div class="firewall-icon">🛡️</div>
          <div class="header-info">
            <h3>{{ firewallData.name || '防火墙配置' }}</h3>
            <div class="status-indicator" :class="statusClass">
              <span class="status-dot"></span>
              {{ statusText }}
            </div>
          </div>
        </div>
        <button class="close-button" @click="closeDialog">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- 主要内容区域 -->
      <div class="dialog-content">
        <!-- 基本信息卡片 -->
        <div class="info-card">
          <h4>基本信息</h4>
          <div class="info-grid">
            <div class="info-item">
              <label>设备名称</label>
              <span>{{ firewallData.name }}</span>
            </div>
            <div class="info-item">
              <label>设备类型</label>
              <span>{{ firewallData.type || '边界防火墙' }}</span>
            </div>
            <div class="info-item">
              <label>管理IP</label>
              <span>{{ firewallData.managementIP }}</span>
            </div>
            <div class="info-item">
              <label>运行状态</label>
              <span :class="statusClass">{{ statusText }}</span>
            </div>
          </div>
        </div>

        <!-- 标签页导航 -->
        <div class="tab-navigation">
          <button v-for="tab in tabs" :key="tab.id" class="tab-button" :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id">
            <i :class="tab.icon"></i>
            {{ tab.name }}
          </button>
        </div>

        <!-- 标签页内容 -->
        <div class="tab-content">
          <!-- 网络接口 -->
          <div v-show="activeTab === 'interfaces'" class="tab-panel">
            <div class="panel-header">
              <h4>网络接口配置</h4>
              <span class="interface-count">{{ interfaces.length }} 个接口</span>
            </div>
            <div class="interface-list">
              <div v-for="(networkInterface, index) in interfaces" :key="index" class="interface-item">
                <div class="interface-info">
                  <div class="interface-name">{{ networkInterface.name }}</div>
                  <div class="interface-details">
                    <span class="ip-address">{{ networkInterface.ip }}</span>
                    <span class="network-name">{{ networkInterface.network }}</span>
                  </div>
                </div>
                <div class="interface-status" :class="networkInterface.status">
                  <span class="status-dot"></span>
                  {{ networkInterface.status === 'up' ? '活跃' : '停用' }}
                </div>
              </div>
            </div>
          </div>

          <!-- 防火墙规则 -->
          <div v-show="activeTab === 'rules'" class="tab-panel">
            <div class="panel-header">
              <h4>访问控制规则</h4>
              <span class="rule-count">{{ rules.length }} 条规则</span>
            </div>
            <div class="rules-list">
              <div v-for="(rule, index) in rules" :key="index" class="rule-item">
                <div class="rule-action" :class="rule.action">
                  {{ getActionText(rule.action) }}
                </div>
                <div class="rule-details">
                  <div class="rule-flow">
                    <span class="source">{{ rule.source }}</span>
                    <i class="fas fa-arrow-right"></i>
                    <span class="destination">{{ rule.destination }}</span>
                  </div>
                  <div class="rule-info">
                    <span class="port">{{ rule.port }}</span>
                    <span class="protocol">{{ rule.protocol }}</span>
                  </div>
                  <div class="rule-description">{{ rule.description }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 安全策略 -->
          <div v-show="activeTab === 'security'" class="tab-panel">
            <div class="security-section">
              <h4>威胁防护</h4>
              <div class="security-features">
                <div class="feature-item" :class="{ enabled: features.intrusion_detection }">
                  <i class="fas fa-shield-alt"></i>
                  <span>入侵检测</span>
                  <div class="feature-status">{{ features.intrusion_detection ? '启用' : '禁用' }}</div>
                </div>
                <div class="feature-item" :class="{ enabled: features.malware_protection }">
                  <i class="fas fa-virus"></i>
                  <span>恶意软件防护</span>
                  <div class="feature-status">{{ features.malware_protection ? '启用' : '禁用' }}</div>
                </div>
                <div class="feature-item" :class="{ enabled: features.ddos_protection }">
                  <i class="fas fa-ban"></i>
                  <span>DDoS防护</span>
                  <div class="feature-status">{{ features.ddos_protection ? '启用' : '禁用' }}</div>
                </div>
              </div>
            </div>

            <div class="security-section">
              <h4>访问控制</h4>
              <div class="access-stats">
                <div class="stat-item">
                  <div class="stat-value">{{ stats.blocked_attempts }}</div>
                  <div class="stat-label">已阻止攻击</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ stats.allowed_connections }}</div>
                  <div class="stat-label">允许连接</div>
                </div>
                <div class="stat-item">
                  <div class="stat-value">{{ stats.active_sessions }}</div>
                  <div class="stat-label">活跃会话</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 实时日志 -->
          <div v-show="activeTab === 'logs'" class="tab-panel">
            <div class="panel-header">
              <h4>实时访问日志</h4>
              <button class="refresh-button" @click="refreshLogs">
                <i class="fas fa-sync-alt"></i>
                刷新
              </button>
            </div>
            <div class="logs-container">
              <div v-for="(log, index) in logs" :key="index" class="log-entry" :class="log.action">
                <div class="log-time">{{ log.timestamp }}</div>
                <div class="log-action" :class="log.action">
                  {{ getActionText(log.action) }}
                </div>
                <div class="log-details">
                  <span class="log-source">{{ log.source }}</span>
                  <i class="fas fa-arrow-right"></i>
                  <span class="log-destination">{{ log.destination }}</span>
                  <span class="log-port">:{{ log.port }}</span>
                </div>
                <div class="log-protocol">{{ log.protocol }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部操作栏 -->
      <div class="dialog-footer">
        <div class="footer-info">
          <span class="last-update">最后更新: {{ lastUpdateTime }}</span>
        </div>
        <div class="footer-actions">
          <button class="action-button secondary" @click="closeDialog">
            关闭
          </button>
          <button class="action-button primary" @click="saveConfiguration">
            <i class="fas fa-save"></i>
            保存配置
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

// Props
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  firewallDevice: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['close', 'save'])

// Reactive data
const activeTab = ref('interfaces')
const firewallData = ref({
  name: '',
  type: '',
  managementIP: '',
  status: 'unknown'
})
const interfaces = ref([])
const rules = ref([])
const features = ref({
  intrusion_detection: true,
  malware_protection: true,
  ddos_protection: false
})
const stats = ref({
  blocked_attempts: 0,
  allowed_connections: 0,
  active_sessions: 0
})
const logs = ref([])
const lastUpdateTime = ref('')
const tabs = ref([
  { id: 'interfaces', name: '网络接口', icon: 'fas fa-network-wired' },
  { id: 'rules', name: '访问规则', icon: 'fas fa-list-ul' },
  { id: 'security', name: '安全策略', icon: 'fas fa-shield-alt' },
  { id: 'logs', name: '实时日志', icon: 'fas fa-file-alt' }
])

// Computed properties
const statusClass = computed(() => {
  const status = firewallData.value.status;
  if (status === 'running' || status === 'active') return 'status-active';
  if (status === 'stopped' || status === 'inactive') return 'status-inactive';
  return 'status-unknown';
})

const statusText = computed(() => {
  const status = firewallData.value.status;
  if (status === 'running' || status === 'active') return '运行中';
  if (status === 'stopped' || status === 'inactive') return '已停止';
  return '未知状态';
})

// Watchers
watch(() => props.show, (newVal) => {
  if (newVal) {
    loadFirewallData();
    updateLastUpdateTime();
  }
})

watch(() => props.firewallDevice, () => {
  if (props.show) {
    loadFirewallData();
  }
}, { deep: true })

// Methods
const handleOverlayClick = () => {
  closeDialog();
}

const closeDialog = () => {
  emit('close');
}

const saveConfiguration = () => {
  emit('save', {
    interfaces: interfaces.value,
    rules: rules.value,
    features: features.value
  });
  closeDialog();
}

const loadFirewallData = () => {
  if (!props.firewallDevice || !props.firewallDevice.deviceData) {
    loadDefaultData();
    return;
  }

  const deviceData = props.firewallDevice.deviceData;
  const scenarioData = deviceData.scenarioData || {};

  // 基本信息
  firewallData.value = {
    name: deviceData.name || '边界防火墙',
    type: getFirewallType(deviceData.name),
    managementIP: deviceData.ip || '192.168.1.1',
    status: scenarioData.status || 'running'
  };

  // 网络接口
  interfaces.value = generateInterfaces(deviceData);

  // 防火墙规则
  rules.value = generateRules();

  // 统计信息
  generateStats();

  // 日志
  generateLogs();
}

const loadDefaultData = () => {
  firewallData.value = {
    name: '边界防火墙',
    type: '企业级防火墙',
    managementIP: '192.168.1.1',
    status: 'running'
  };

  interfaces.value = [
    { name: 'eth0', ip: '192.168.100.254', network: '用户网段', status: 'up' },
    { name: 'eth1', ip: '192.168.200.254', network: '服务器网段', status: 'up' },
    { name: 'eth2', ip: '172.16.100.254', network: 'DMZ网段', status: 'up' },
    { name: 'eth3', ip: '172.203.100.254', network: '互联网', status: 'up' }
  ];

  rules.value = generateRules();
  generateStats();
  generateLogs();
}

const getFirewallType = (name) => {
  if (name && name.includes('外部')) return '边界防火墙';
  if (name && name.includes('内部')) return '内网防火墙';
  return '企业级防火墙';
}

const generateInterfaces = (deviceData) => {
  const interfaceList = [];
  const name = deviceData.name || '';

  if (name.includes('外部') || name.includes('border')) {
    interfaceList.push(
      { name: 'eth0', ip: '192.168.100.254', network: '用户网段', status: 'up' },
      { name: 'eth1', ip: '192.168.200.254', network: '服务器网段', status: 'up' },
      { name: 'eth2', ip: '172.16.100.254', network: 'DMZ网段', status: 'up' },
      { name: 'eth3', ip: '172.203.100.254', network: '互联网', status: 'up' }
    );
  } else {
    interfaceList.push(
      { name: 'eth0', ip: '192.168.100.1', network: '用户网段', status: 'up' },
      { name: 'eth1', ip: '192.168.200.1', network: '服务器网段', status: 'up' }
    );
  }

  return interfaceList;
}

const generateRules = () => {
  return [
    {
      action: 'allow',
      source: '192.168.100.0/24',
      destination: '172.16.100.0/24',
      port: '80,443',
      protocol: 'TCP',
      description: '允许用户访问DMZ Web服务'
    },
    {
      action: 'deny',
      source: '192.168.100.0/24',
      destination: '192.168.200.0/24',
      port: '3306',
      protocol: 'TCP',
      description: '禁止用户直接访问数据库'
    },
    {
      action: 'allow',
      source: '172.16.100.0/24',
      destination: '192.168.200.0/24',
      port: '3306',
      protocol: 'TCP',
      description: '允许DMZ访问内网数据库'
    },
    {
      action: 'block',
      source: '0.0.0.0/0',
      destination: '192.168.0.0/16',
      port: '22',
      protocol: 'TCP',
      description: '阻止外网SSH访问内网'
    }
  ];
}

const generateStats = () => {
  stats.value = {
    blocked_attempts: Math.floor(Math.random() * 100) + 50,
    allowed_connections: Math.floor(Math.random() * 500) + 200,
    active_sessions: Math.floor(Math.random() * 50) + 10
  };
}

const generateLogs = () => {
  const actions = ['allow', 'deny', 'block'];
  const sources = ['192.168.100.50', '172.203.100.10', '203.0.113.15', '192.168.200.23'];
  const destinations = ['172.16.100.10', '192.168.200.23', '8.8.8.8', '192.168.100.1'];
  const ports = [80, 443, 22, 3306, 53, 25];
  const protocols = ['TCP', 'UDP', 'ICMP'];

  logs.value = [];
  const now = new Date();

  for (let i = 0; i < 20; i++) {
    const timestamp = new Date(now.getTime() - i * 30000); // 每30秒一条
    logs.value.push({
      timestamp: timestamp.toLocaleTimeString(),
      action: actions[Math.floor(Math.random() * actions.length)],
      source: sources[Math.floor(Math.random() * sources.length)],
      destination: destinations[Math.floor(Math.random() * destinations.length)],
      port: ports[Math.floor(Math.random() * ports.length)],
      protocol: protocols[Math.floor(Math.random() * protocols.length)]
    });
  }
}

const refreshLogs = () => {
  generateLogs();
  updateLastUpdateTime();
}

const updateLastUpdateTime = () => {
  lastUpdateTime.value = new Date().toLocaleString();
}

const getActionText = (action) => {
  const actionMap = {
    'allow': '允许',
    'deny': '拒绝',
    'block': '阻断'
  };
  return actionMap[action] || action;
}

// Lifecycle
onMounted(() => {
  if (props.show) {
    loadFirewallData();
    updateLastUpdateTime();
  }
})
</script>

<style scoped>
.firewall-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.firewall-dialog-container {
  background: linear-gradient(135deg, #1e1e2f 0%, #27293d 100%);
  border-radius: 12px;
  width: 900px;
  max-width: 95vw;
  max-height: 90vh;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  border: 1px solid #3a3d5c;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dialog-header {
  padding: 20px 24px;
  border-bottom: 1px solid #3a3d5c;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(90deg, #1e1e2f 0%, #2a2d47 100%);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.firewall-icon {
  font-size: 32px;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-info h3 {
  margin: 0 0 4px 0;
  color: #ffffff;
  font-size: 20px;
  font-weight: 600;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-active {
  color: #4CAF50;
}

.status-active .status-dot {
  background: #4CAF50;
  box-shadow: 0 0 8px rgba(76, 175, 80, 0.5);
}

.status-inactive {
  color: #f44336;
}

.status-inactive .status-dot {
  background: #f44336;
}

.status-unknown {
  color: #ff9800;
}

.status-unknown .status-dot {
  background: #ff9800;
}

.close-button {
  background: none;
  border: none;
  color: #a0a0a0;
  font-size: 18px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.dialog-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.info-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.info-card h4 {
  margin: 0 0 16px 0;
  color: #4CAF50;
  font-size: 16px;
  font-weight: 600;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item label {
  color: #a0a0a0;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item span {
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
}

.tab-navigation {
  display: flex;
  border-bottom: 1px solid #3a3d5c;
  margin-bottom: 24px;
}

.tab-button {
  background: none;
  border: none;
  padding: 12px 20px;
  color: #a0a0a0;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-button:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.05);
}

.tab-button.active {
  color: #4CAF50;
  border-bottom-color: #4CAF50;
}

.tab-content {
  min-height: 400px;
}

.tab-panel {
  display: block;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.panel-header h4 {
  margin: 0;
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
}

.interface-count,
.rule-count {
  color: #a0a0a0;
  font-size: 14px;
}

.interface-list,
.rules-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.interface-item,
.rule-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.interface-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.interface-name {
  color: #ffffff;
  font-weight: 600;
  font-size: 16px;
}

.interface-details {
  display: flex;
  gap: 12px;
  align-items: center;
}

.ip-address {
  color: #4CAF50;
  font-family: monospace;
  font-size: 14px;
}

.network-name {
  color: #a0a0a0;
  font-size: 14px;
}

.interface-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.interface-status.up {
  color: #4CAF50;
}

.interface-status.up .status-dot {
  background: #4CAF50;
}

.interface-status.down {
  color: #f44336;
}

.interface-status.down .status-dot {
  background: #f44336;
}

.rule-action {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  min-width: 60px;
  text-align: center;
}

.rule-action.allow {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
  border: 1px solid #4CAF50;
}

.rule-action.deny {
  background: rgba(255, 152, 0, 0.2);
  color: #ff9800;
  border: 1px solid #ff9800;
}

.rule-action.block {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
  border: 1px solid #f44336;
}

.rule-details {
  flex: 1;
  margin-left: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rule-flow {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ffffff;
  font-family: monospace;
  font-size: 14px;
}

.rule-info {
  display: flex;
  gap: 12px;
  color: #a0a0a0;
  font-size: 12px;
}

.rule-description {
  color: #a0a0a0;
  font-size: 13px;
}

.security-section {
  margin-bottom: 32px;
}

.security-section h4 {
  margin: 0 0 16px 0;
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
}

.security-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.feature-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.2s;
}

.feature-item.enabled {
  border-color: #4CAF50;
  background: rgba(76, 175, 80, 0.1);
}

.feature-item i {
  font-size: 20px;
  color: #a0a0a0;
}

.feature-item.enabled i {
  color: #4CAF50;
}

.feature-item span {
  flex: 1;
  color: #ffffff;
  font-weight: 500;
}

.feature-status {
  color: #a0a0a0;
  font-size: 12px;
}

.feature-item.enabled .feature-status {
  color: #4CAF50;
}

.access-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.stat-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #4CAF50;
  margin-bottom: 4px;
}

.stat-label {
  color: #a0a0a0;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.refresh-button {
  background: rgba(76, 175, 80, 0.2);
  border: 1px solid #4CAF50;
  color: #4CAF50;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.refresh-button:hover {
  background: rgba(76, 175, 80, 0.3);
}

.logs-container {
  max-height: 400px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-entry {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  padding: 12px 16px;
  border-left: 3px solid transparent;
  display: grid;
  grid-template-columns: 80px 60px 1fr 60px;
  gap: 12px;
  align-items: center;
  font-size: 13px;
}

.log-entry.allow {
  border-left-color: #4CAF50;
}

.log-entry.deny {
  border-left-color: #ff9800;
}

.log-entry.block {
  border-left-color: #f44336;
}

.log-time {
  color: #a0a0a0;
  font-family: monospace;
}

.log-action {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  text-align: center;
}

.log-action.allow {
  background: rgba(76, 175, 80, 0.2);
  color: #4CAF50;
}

.log-action.deny {
  background: rgba(255, 152, 0, 0.2);
  color: #ff9800;
}

.log-action.block {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

.log-details {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #ffffff;
  font-family: monospace;
}

.log-protocol {
  color: #a0a0a0;
  font-size: 11px;
  text-align: center;
}

.dialog-footer {
  padding: 20px 24px;
  border-top: 1px solid #3a3d5c;
  background: rgba(0, 0, 0, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-info {
  color: #a0a0a0;
  font-size: 12px;
}

.footer-actions {
  display: flex;
  gap: 12px;
}

.action-button {
  padding: 10px 20px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.action-button.primary {
  background: #4CAF50;
  color: white;
}

.action-button.primary:hover {
  background: #45a049;
}

.action-button.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.action-button.secondary:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 滚动条样式 */
.logs-container::-webkit-scrollbar,
.dialog-content::-webkit-scrollbar {
  width: 6px;
}

.logs-container::-webkit-scrollbar-track,
.dialog-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.logs-container::-webkit-scrollbar-thumb,
.dialog-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.logs-container::-webkit-scrollbar-thumb:hover,
.dialog-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
</style>