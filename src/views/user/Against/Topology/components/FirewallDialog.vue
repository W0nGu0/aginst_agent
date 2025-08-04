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
            <p><strong>名称:</strong> border_firewall</p>
            <p><strong>状态:</strong> <span style="color: #00f2c3;">运行中</span></p>
            <p><strong>接口数量:</strong> 5</p>
          </div>
          
          <!-- 标签页 -->
          <div class="tabs">
            <button 
              class="tab-btn" 
              :class="{ active: activeTab === 'interfaces' }" 
              @click="activeTab = 'interfaces'"
            >
              接口
            </button>
            <button 
              class="tab-btn" 
              :class="{ active: activeTab === 'rules' }" 
              @click="activeTab = 'rules'"
            >
              访问规则
            </button>
            <button 
              class="tab-btn" 
              :class="{ active: activeTab === 'blacklist' }" 
              @click="activeTab = 'blacklist'"
            >
              黑名单
            </button>
            <button 
              class="tab-btn" 
              :class="{ active: activeTab === 'whitelist' }" 
              @click="activeTab = 'whitelist'"
            >
              白名单
            </button>
            <button 
              class="tab-btn" 
              :class="{ active: activeTab === 'logs' }" 
              @click="activeTab = 'logs'"
            >
              日志
            </button>
          </div>
          
          <!-- 内容区域 -->
          <div class="tab-content">
            <!-- 接口标签页 -->
            <div v-show="activeTab === 'interfaces'" class="content-panel">
              <h4>网络接口配置</h4>
              <div class="content-list">
                <div class="content-item">
                  <strong>eth0</strong> - 192.168.200.254/24 (服务器网段) - <span style="color: #00f2c3;">活跃</span>
                </div>
                <div class="content-item">
                  <strong>eth1</strong> - 192.168.100.254/24 (用户网段) - <span style="color: #00f2c3;">活跃</span>
                </div>
                <div class="content-item">
                  <strong>eth2</strong> - 192.168.66.254/24 (SIEM网段) - <span style="color: #00f2c3;">活跃</span>
                </div>
                <div class="content-item">
                  <strong>eth3</strong> - 192.168.110.254/24 (VPN网段) - <span style="color: #00f2c3;">活跃</span>
                </div>
                <div class="content-item">
                  <strong>eth4</strong> - 192.168.214.254/24 (数据库网段) - <span style="color: #00f2c3;">活跃</span>
                </div>
              </div>
            </div>
            
            <!-- 访问规则标签页 -->
            <div v-show="activeTab === 'rules'" class="content-panel">
              <h4>访问控制规则</h4>
              <div class="content-list">
                <div class="content-item">
                  <span class="rule-badge allow">允许</span> any → any (ICMP) - 允许ICMP协议
                </div>
                <div class="content-item">
                  <span class="rule-badge allow">允许</span> 192.168.100.0/24 → 192.168.200.0/24 (TCP:80,443) - 允许用户访问Web服务
                </div>
                <div class="content-item">
                  <span class="rule-badge deny">拒绝</span> any → 192.168.200.23 (TCP:3306) - 拒绝外部访问数据库
                </div>
                <div class="content-item">
                  <span class="rule-badge allow">允许</span> 192.168.100.0/24 → 192.168.200.6 (TCP:445) - 允许文件共享
                </div>
                <div class="content-item">
                  <span class="rule-badge block">阻断</span> 199.203.100.0/24 → 192.168.0.0/16 (any) - 阻断可疑外网访问
                </div>
                <div class="content-item">
                  <span class="rule-badge allow">允许</span> 192.168.66.0/24 → any (TCP:514) - 允许SIEM日志收集
                </div>
              </div>
            </div>
            
            <!-- 黑名单标签页 -->
            <div v-show="activeTab === 'blacklist'" class="content-panel">
              <h4>IP/域名黑名单</h4>
              <div class="content-list">
                <div class="content-item">
                  <span class="type-badge ip">IP</span> 203.0.113.15 - 恶意IP地址 - <span style="color: #00f2c3;">启用</span>
                </div>
                <div class="content-item">
                  <span class="type-badge domain">域名</span> malicious-site.com - 恶意域名 - <span style="color: #00f2c3;">启用</span>
                </div>
                <div class="content-item">
                  <span class="type-badge subnet">网段</span> 198.51.100.0/24 - 可疑网段 - <span style="color: #00f2c3;">启用</span>
                </div>
                <div class="content-item">
                  <span class="type-badge ip">IP</span> 192.0.2.100 - 攻击源IP - <span style="color: #6c757d;">禁用</span>
                </div>
              </div>
            </div>
            
            <!-- 白名单标签页 -->
            <div v-show="activeTab === 'whitelist'" class="content-panel">
              <h4>IP/域名白名单</h4>
              <div class="content-list">
                <div class="content-item">
                  <span class="type-badge ip">IP</span> 8.8.8.8 - Google DNS - <span style="color: #00f2c3;">启用</span>
                </div>
                <div class="content-item">
                  <span class="type-badge domain">域名</span> trusted-partner.com - 可信合作伙伴 - <span style="color: #00f2c3;">启用</span>
                </div>
                <div class="content-item">
                  <span class="type-badge subnet">网段</span> 192.168.0.0/16 - 内网网段 - <span style="color: #00f2c3;">启用</span>
                </div>
                <div class="content-item">
                  <span class="type-badge ip">IP</span> 1.1.1.1 - Cloudflare DNS - <span style="color: #00f2c3;">启用</span>
                </div>
              </div>
            </div>
            
            <!-- 日志标签页 -->
            <div v-show="activeTab === 'logs'" class="content-panel">
              <h4>防火墙访问日志</h4>
              <div class="content-list">
                <div class="content-item">
                  <span class="rule-badge allow">允许</span> 2025-01-08 17:42:15 - 192.168.100.9 → 192.168.200.23 (TCP:80)
                </div>
                <div class="content-item">
                  <span class="rule-badge deny">拒绝</span> 2025-01-08 17:41:32 - 199.203.100.10 → 192.168.200.23 (TCP:3306)
                </div>
                <div class="content-item">
                  <span class="rule-badge allow">允许</span> 2025-01-08 17:40:18 - 192.168.100.34 → 192.168.200.6 (TCP:445)
                </div>
                <div class="content-item">
                  <span class="rule-badge block">阻断</span> 2025-01-08 17:39:45 - 199.203.100.10 → 172.16.100.53 (UDP:53)
                </div>
                <div class="content-item">
                  <span class="rule-badge block">阻断</span> 2025-01-08 17:38:22 - 203.0.113.15 → 192.168.200.23 (TCP:22)
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
  data() {
    return {
      activeTab: 'interfaces'
    }
  },
  methods: {
    closeDialog() {
      this.$emit('close')
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
</style>