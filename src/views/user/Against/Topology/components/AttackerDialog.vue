<template>
  <div class="attacker-dialog">
    <div v-if="show" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3>攻击控制面板</h3>
          <button class="close-btn" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="target-selection">
            <h4>选择攻击目标</h4>
            <div class="target-list">
              <div 
                v-for="target in availableTargets" 
                :key="target.id"
                class="target-item"
                :class="{ 'selected': selectedTarget === target.id }"
                @click="selectTarget(target.id)"
              >
                <div class="target-icon">
                  <img :src="getDeviceIcon(target.type)" alt="">
                </div>
                <div class="target-info">
                  <div class="target-name">{{ target.name }}</div>
                  <div class="target-ip">{{ target.ip }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="attack-selection">
            <h4>选择攻击方式</h4>
            <div class="attack-list">
              <div 
                v-for="attack in availableAttacks" 
                :key="attack.id"
                class="attack-item"
                :class="{ 'selected': selectedAttack === attack.id, 'disabled': !attack.available }"
                @click="selectAttack(attack.id)"
              >
                <div class="attack-icon">
                  <i :class="attack.icon"></i>
                </div>
                <div class="attack-info">
                  <div class="attack-name">{{ attack.name }}</div>
                  <div class="attack-desc">{{ attack.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button 
            class="btn btn-danger" 
            :disabled="!canAttack"
            @click="launchAttack"
          >
            发起攻击
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
      selectedTarget: null,
      selectedAttack: null,
      availableAttacks: [
        {
          id: 'port_scan',
          name: '端口扫描',
          description: '扫描目标主机开放的端口',
          icon: 'fas fa-search',
          available: true
        },
        {
          id: 'brute_force',
          name: '暴力破解',
          description: '尝试暴力破解目标主机的登录凭证',
          icon: 'fas fa-key',
          available: true
        },
        {
          id: 'exploit',
          name: '漏洞利用',
          description: '利用已知漏洞攻击目标主机',
          icon: 'fas fa-bug',
          available: true
        },
        {
          id: 'ddos',
          name: 'DDoS攻击',
          description: '对目标主机发起分布式拒绝服务攻击',
          icon: 'fas fa-bomb',
          available: true
        }
      ]
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
    },
    canAttack() {
      return this.selectedTarget && this.selectedAttack;
    }
  },
  methods: {
    selectTarget(targetId) {
      this.selectedTarget = targetId;
    },
    selectAttack(attackId) {
      const attack = this.availableAttacks.find(a => a.id === attackId);
      if (attack && attack.available) {
        this.selectedAttack = attackId;
      }
    },
    launchAttack() {
      if (!this.canAttack) return;
      
      const target = this.targets.find(t => t.id === this.selectedTarget);
      const attack = this.availableAttacks.find(a => a.id === this.selectedAttack);
      
      this.$emit('attack', {
        attacker: this.attacker,
        target: target,
        attackType: this.selectedAttack,
        attackName: attack.name
      });
      
      this.closeDialog();
    },
    closeDialog() {
      this.$emit('close');
      this.selectedTarget = null;
      this.selectedAttack = null;
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

.target-selection,
.attack-selection {
  margin-bottom: 16px;
}

.target-list,
.attack-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 8px;
  margin-top: 8px;
}

.target-item,
.attack-item {
  display: flex;
  align-items: center;
  padding: 8px;
  border-radius: 4px;
  background-color: #27293d;
  cursor: pointer;
  transition: background-color 0.2s;
}

.target-item:hover,
.attack-item:hover {
  background-color: #2c2c40;
}

.target-item.selected,
.attack-item.selected {
  background-color: #1d8cf8;
}

.attack-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.target-icon,
.attack-icon {
  width: 32px;
  height: 32px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 8px;
}

.target-icon img {
  max-width: 100%;
  max-height: 100%;
}

.target-info,
.attack-info {
  flex-grow: 1;
}

.target-name,
.attack-name {
  font-weight: bold;
  color: #ffffff;
}

.target-ip,
.attack-desc {
  font-size: 12px;
  color: #a9a9a9;
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