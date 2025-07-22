<template>
  <div class="attack-progress-monitor" v-if="visible">
    <div class="progress-header">
      <h3>攻击进度监控</h3>
      <div class="progress-controls">
        <button class="btn btn-sm" @click="$emit('close')">关闭</button>
      </div>
    </div>
    
    <div class="progress-content">
      <!-- 攻击链进度条 -->
      <div class="attack-chain-progress">
        <div class="progress-title">攻击链进度</div>
        <div class="progress-bar-container">
          <div class="progress-bar" :style="{ width: `${progress}%` }"></div>
        </div>
        <div class="progress-percentage">{{ progress }}%</div>
      </div>
      
      <!-- 攻击链阶段 -->
      <div class="attack-chain-phases">
        <div 
          v-for="(phase, index) in phases" 
          :key="phase.id"
          class="phase-item"
          :class="{ 
            'active': currentPhase === phase.id, 
            'completed': isPhaseCompleted(phase.id) 
          }"
        >
          <div class="phase-icon">
            <i :class="phase.icon"></i>
          </div>
          <div class="phase-name">{{ phase.name }}</div>
          <div class="phase-status">
            <i v-if="isPhaseCompleted(phase.id)" class="fas fa-check"></i>
            <i v-else-if="currentPhase === phase.id" class="fas fa-spinner fa-spin"></i>
          </div>
        </div>
      </div>
      
      <!-- 最近日志 -->
      <div class="recent-logs">
        <div class="logs-title">最近日志</div>
        <div class="logs-container" ref="logsContainer">
          <div 
            v-for="(log, index) in recentLogs" 
            :key="index"
            class="log-item"
            :class="getLogLevelClass(log.level)"
          >
            <div class="log-time">{{ formatTime(log.timestamp) }}</div>
            <div class="log-source">{{ log.source }}</div>
            <div class="log-message">{{ log.message }}</div>
          </div>
          <div v-if="recentLogs.length === 0" class="no-logs">
            暂无日志
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AttackProgressMonitor',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    taskId: {
      type: String,
      default: ''
    },
    taskStatus: {
      type: Object,
      default: () => ({
        status: 'pending',
        phase: 'reconnaissance',
        progress: 0,
        logs: []
      })
    }
  },
  data() {
    return {
      phases: [
        { id: 'reconnaissance', name: '侦察', icon: 'fas fa-search' },
        { id: 'weaponization', name: '武器化', icon: 'fas fa-wrench' },
        { id: 'delivery', name: '投递', icon: 'fas fa-paper-plane' },
        { id: 'exploitation', name: '利用', icon: 'fas fa-bug' },
        { id: 'installation', name: '安装', icon: 'fas fa-download' },
        { id: 'command_and_control', name: '命令控制', icon: 'fas fa-terminal' },
        { id: 'actions_on_objectives', name: '目标行动', icon: 'fas fa-flag' }
      ],
      phaseOrder: [
        'reconnaissance',
        'weaponization',
        'delivery',
        'exploitation',
        'installation',
        'command_and_control',
        'actions_on_objectives'
      ]
    };
  },
  computed: {
    progress() {
      return this.taskStatus?.progress || 0;
    },
    currentPhase() {
      return this.taskStatus?.phase || 'reconnaissance';
    },
    recentLogs() {
      // 获取最近的10条日志
      return (this.taskStatus?.logs || []).slice(-10);
    }
  },
  watch: {
    recentLogs() {
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    }
  },
  methods: {
    isPhaseCompleted(phaseId) {
      const currentPhaseIndex = this.phaseOrder.indexOf(this.currentPhase);
      const phaseIndex = this.phaseOrder.indexOf(phaseId);
      
      return phaseIndex < currentPhaseIndex;
    },
    getLogLevelClass(level) {
      switch (level?.toLowerCase()) {
        case 'error':
          return 'log-error';
        case 'warning':
          return 'log-warning';
        case 'info':
          return 'log-info';
        case 'debug':
          return 'log-debug';
        case 'success':
          return 'log-success';
        default:
          return '';
      }
    },
    formatTime(timestamp) {
      if (!timestamp) return '';
      
      if (typeof timestamp === 'string') {
        return timestamp;
      }
      
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    },
    scrollToBottom() {
      if (this.$refs.logsContainer) {
        this.$refs.logsContainer.scrollTop = this.$refs.logsContainer.scrollHeight;
      }
    }
  }
};
</script>

<style scoped>
.attack-progress-monitor {
  background-color: #1e1e2f;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1000;
}

.progress-header {
  padding: 8px 12px;
  border-bottom: 1px solid #2c2c40;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-header h3 {
  margin: 0;
  font-size: 14px;
  color: #ffffff;
}

.progress-controls {
  display: flex;
  gap: 4px;
}

.progress-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  padding: 12px;
  overflow: auto;
}

.attack-chain-progress {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.progress-title {
  width: 100px;
  font-size: 12px;
  color: #a9a9a9;
}

.progress-bar-container {
  flex-grow: 1;
  height: 8px;
  background-color: #2c2c40;
  border-radius: 4px;
  overflow: hidden;
  margin: 0 12px;
}

.progress-bar {
  height: 100%;
  background-color: #1d8cf8;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-percentage {
  width: 40px;
  font-size: 12px;
  color: #a9a9a9;
  text-align: right;
}

.attack-chain-phases {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.phase-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
  position: relative;
  opacity: 0.5;
  transition: all 0.3s ease;
}

.phase-item:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 15px;
  right: -15px;
  width: 30px;
  height: 2px;
  background-color: #2c2c40;
}

.phase-item.active {
  opacity: 1;
}

.phase-item.completed {
  opacity: 1;
}

.phase-item.active .phase-icon {
  background-color: #1d8cf8;
  box-shadow: 0 0 10px rgba(29, 140, 248, 0.5);
}

.phase-item.completed .phase-icon {
  background-color: #00f2c3;
  box-shadow: 0 0 10px rgba(0, 242, 195, 0.5);
}

.phase-item.completed:not(:last-child)::after {
  background-color: #00f2c3;
}

.phase-item.active:not(:last-child)::after {
  background-color: #1d8cf8;
}

.phase-icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background-color: #2c2c40;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 5px;
  transition: all 0.3s ease;
}

.phase-name {
  font-size: 9px;
  color: #a9a9a9;
  text-align: center;
  max-width: 60px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.phase-status {
  position: absolute;
  top: -5px;
  right: -5px;
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background-color: #27293d;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 8px;
  color: #00f2c3;
}

.recent-logs {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.logs-title {
  font-size: 12px;
  color: #a9a9a9;
  margin-bottom: 8px;
}

.logs-container {
  flex-grow: 1;
  overflow-y: auto;
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  padding: 8px;
  max-height: 200px;
}

.log-item {
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  font-size: 11px;
}

.log-time {
  color: #a9a9a9;
  margin-right: 8px;
  white-space: nowrap;
  font-size: 10px;
}

.log-source {
  color: #1d8cf8;
  margin-right: 8px;
  white-space: nowrap;
  font-weight: bold;
  font-size: 10px;
}

.log-message {
  flex-grow: 1;
  word-break: break-word;
}

.log-error {
  background-color: rgba(253, 93, 147, 0.1);
  color: #fd5d93;
}

.log-warning {
  background-color: rgba(255, 214, 102, 0.1);
  color: #ffd666;
}

.log-info {
  background-color: rgba(29, 140, 248, 0.1);
  color: #1d8cf8;
}

.log-debug {
  background-color: rgba(0, 242, 195, 0.1);
  color: #00f2c3;
}

.log-success {
  background-color: rgba(0, 242, 195, 0.1);
  color: #00f2c3;
}

.no-logs {
  color: #a9a9a9;
  text-align: center;
  padding: 8px;
  font-size: 11px;
}

.btn {
  padding: 2px 6px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 11px;
  background-color: #27293d;
  color: #ffffff;
}

.btn:hover {
  background-color: #2c2c40;
}
</style>