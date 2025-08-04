<template>
  <div class="attacker-dialog">
    <div v-if="show" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content" ref="dialogContent" @click.stop>
        <div class="dialog-header" @mousedown="startDrag">
          <h3>攻击控制面板</h3>
          <button class="close-btn" @click="closeDialog">&times;</button>
        </div>
        <div class="dialog-body">
          <!-- 攻击者信息 -->
          <div class="attacker-info">
            <div class="attacker-icon">
              <i class="fas fa-user-secret"></i>
            </div>
            <div class="attacker-details">
              <h4>{{ attacker.deviceData?.name || '攻击者' }}</h4>
              <p>IP: {{ attacker.deviceData?.ip || '未知' }}</p>
              <p>类型: 恶意攻击者</p>
            </div>
          </div>

          <!-- 攻击类型选择 -->
          <div class="attack-type-selection">
            <h4>选择攻击类型</h4>
            <div class="attack-types">
              <div 
                class="attack-type-card" 
                :class="{ active: selectedAttackType === 'auto' }"
                @click="selectedAttackType = 'auto'"
              >
                <div class="attack-icon">🤖</div>
                <div class="attack-info">
                  <h5>自动攻击</h5>
                  <p>AI智能体自动分析并执行最优攻击路径</p>
                </div>
              </div>
              

            </div>
          </div>

          <!-- 目标选择 -->
          <div class="target-selection" v-if="selectedAttackType !== 'auto'">
            <h4>选择攻击目标</h4>
            <div class="target-list">
              <div 
                v-for="target in availableTargets" 
                :key="target.id"
                class="target-item"
                :class="{ selected: selectedTarget?.id === target.id }"
                @click="selectedTarget = target"
              >
                <div class="target-icon">
                  <img :src="getDeviceIcon(target.type)" :alt="target.type" />
                </div>
                <div class="target-info">
                  <div class="target-name">{{ target.name }}</div>
                  <div class="target-ip">{{ target.ip }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- APT攻击配置 -->
          <div v-if="selectedAttackType === 'apt'" class="apt-config">
            <h4>APT攻击配置</h4>
            <div class="config-row">
              <label>持续时间:</label>
              <select v-model="aptConfig.duration">
                <option value="short">短期 (1-7天)</option>
                <option value="medium">中期 (1-4周)</option>
                <option value="long">长期 (1-6个月)</option>
              </select>
            </div>
            <div class="config-row">
              <label>隐蔽级别:</label>
              <select v-model="aptConfig.stealthLevel">
                <option value="medium">中等</option>
                <option value="high">高</option>
                <option value="very_high">极高</option>
              </select>
            </div>
            <div class="config-row">
              <label>攻击目标:</label>
              <div class="checkbox-group">
                <label><input type="checkbox" v-model="aptConfig.targets.credentials"> 凭据窃取</label>
                <label><input type="checkbox" v-model="aptConfig.targets.data"> 数据外泄</label>
                <label><input type="checkbox" v-model="aptConfig.targets.persistence"> 建立持久化</label>
                <label><input type="checkbox" v-model="aptConfig.targets.lateral"> 横向移动</label>
              </div>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-danger" @click="launchAttack" :disabled="!canLaunchAttack">
            <i class="fas fa-rocket"></i> 
            {{ getAttackButtonText() }}
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
  emits: ['close', 'attack'],
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
      selectedAttackType: 'auto',
      selectedTarget: null,
      // 拖动相关状态
      isDragging: false,
      dragOffset: { x: 0, y: 0 },
      position: { x: 0, y: 0 }
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
    canLaunchAttack() {
      if (this.selectedAttackType === 'auto') {
        return true;
      }
      return this.selectedTarget !== null;
    }
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
  methods: {
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
    },

    // 发起攻击
    launchAttack() {
      const attackData = {
        attacker: this.attacker,
        target: this.selectedTarget,
        attackType: this.selectedAttackType,
        attackName: this.getAttackName()
      };

      this.$emit('attack', attackData);
      this.closeDialog();
    },

    getAttackName() {
      const nameMap = {
        auto: '自动攻击'
      };
      return nameMap[this.selectedAttackType] || '自动攻击';
    },

    getAttackButtonText() {
      const textMap = {
        auto: '启动自动攻击'
      };
      return textMap[this.selectedAttackType] || '启动自动攻击';
    },

    closeDialog() {
      this.$emit('close');
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

      return iconMap[type] || '/图标/服务器.svg';
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
  width: 700px;
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
  cursor: grab;
}

.dialog-header:active {
  cursor: grabbing;
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
  padding: 20px;
  flex-grow: 1;
}

.dialog-footer {
  padding: 16px;
  border-top: 1px solid #2c2c40;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 攻击者信息 */
.attacker-info {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px;
  background-color: #27293d;
  border-radius: 8px;
  border: 1px solid #2c2c40;
}

.attacker-icon {
  font-size: 32px;
  color: #fd5d93;
  margin-right: 16px;
}

.attacker-details h4 {
  margin: 0 0 8px 0;
  color: #ffffff;
  font-size: 18px;
}

.attacker-details p {
  margin: 4px 0;
  color: #a9a9a9;
  font-size: 14px;
}

/* 攻击类型选择 */
.attack-type-selection {
  margin-bottom: 24px;
}

.attack-type-selection h4 {
  margin: 0 0 16px 0;
  color: #ffffff;
  font-size: 16px;
}

.attack-types {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attack-type-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background-color: #27293d;
  border: 2px solid #2c2c40;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.attack-type-card:hover {
  border-color: #1d8cf8;
}

.attack-type-card.active {
  border-color: #1d8cf8;
  background-color: rgba(29, 140, 248, 0.1);
}

.attack-icon {
  font-size: 24px;
  margin-right: 16px;
  min-width: 40px;
}

.attack-info h5 {
  margin: 0 0 4px 0;
  color: #ffffff;
  font-size: 16px;
}

.attack-info p {
  margin: 0;
  color: #a9a9a9;
  font-size: 14px;
}

/* 目标选择 */
.target-selection {
  margin-bottom: 24px;
}

.target-selection h4 {
  margin: 0 0 16px 0;
  color: #ffffff;
  font-size: 16px;
}

.target-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.target-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background-color: #27293d;
  border: 2px solid #2c2c40;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.target-item:hover {
  border-color: #1d8cf8;
}

.target-item.selected {
  border-color: #1d8cf8;
  background-color: rgba(29, 140, 248, 0.1);
}

.target-icon {
  width: 32px;
  height: 32px;
  margin-right: 12px;
}

.target-icon img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.target-name {
  color: #ffffff;
  font-weight: bold;
  font-size: 14px;
}

.target-ip {
  color: #a9a9a9;
  font-size: 12px;
}

/* APT配置 */
.apt-config {
  margin-bottom: 24px;
}

.apt-config h4 {
  margin: 0 0 16px 0;
  color: #ffffff;
  font-size: 16px;
}

.config-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.config-row label {
  min-width: 100px;
  color: #a9a9a9;
  font-size: 14px;
}

.config-row select {
  flex: 1;
  padding: 8px;
  background-color: #27293d;
  border: 1px solid #2c2c40;
  border-radius: 4px;
  color: #ffffff;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  color: #ffffff;
  font-size: 14px;
  min-width: auto;
}

.checkbox-group input[type="checkbox"] {
  margin-right: 8px;
}

/* 按钮样式 */
.btn {
  padding: 10px 20px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger {
  background-color: #fd5d93;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #fd77a4;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}
</style>