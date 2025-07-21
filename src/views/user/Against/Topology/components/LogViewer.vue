<template>
  <div class="log-viewer" :class="{ 'expanded': expanded }">
    <div class="log-header" @click="toggleExpand">
      <h3>系统日志</h3>
      <div class="log-controls">
        <button class="btn btn-sm" @click.stop="clearLogs">清空</button>
        <button class="btn btn-sm" @click.stop="toggleExpand">
          {{ expanded ? '收起' : '展开' }}
        </button>
      </div>
    </div>
    <div class="log-content">
      <div class="log-entries" ref="logEntries">
        <div 
          v-for="(log, index) in logs" 
          :key="index"
          class="log-entry"
          :class="getLogLevelClass(log.level)"
        >
          <div class="log-time">{{ log.timestamp }}</div>
          <div class="log-level">{{ log.level }}</div>
          <div class="log-source">{{ log.source }}</div>
          <div class="log-message">{{ log.message }}</div>
        </div>
        <div v-if="logs.length === 0" class="no-logs">
          暂无日志记录
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LogViewer',
  props: {
    initialExpanded: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      expanded: this.initialExpanded,
      logs: []
    };
  },
  watch: {
    logs() {
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    }
  },
  methods: {
    toggleExpand() {
      this.expanded = !this.expanded;
    },
    clearLogs() {
      this.logs = [];
    },
    addLog(log) {
      // 添加时间戳
      if (!log.timestamp) {
        log.timestamp = new Date().toLocaleTimeString();
      }
      
      this.logs.push(log);
      
      // 限制日志数量，避免内存占用过多
      if (this.logs.length > 100) {
        this.logs.shift();
      }
    },
    scrollToBottom() {
      if (this.$refs.logEntries) {
        this.$refs.logEntries.scrollTop = this.$refs.logEntries.scrollHeight;
      }
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
        default:
          return '';
      }
    }
  }
};
</script>

<style scoped>
.log-viewer {
  background-color: #1e1e2f;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  height: 200px;
  transition: height 0.3s;
}

.log-viewer.expanded {
  height: 400px;
}

.log-header {
  padding: 8px 16px;
  border-bottom: 1px solid #2c2c40;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.log-header h3 {
  margin: 0;
  font-size: 16px;
  color: #ffffff;
}

.log-controls {
  display: flex;
  gap: 8px;
}

.log-content {
  flex-grow: 1;
  overflow: hidden;
}

.log-entries {
  height: 100%;
  overflow-y: auto;
  padding: 8px;
}

.log-entry {
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  font-family: monospace;
  font-size: 12px;
}

.log-time {
  color: #a9a9a9;
  margin-right: 8px;
  white-space: nowrap;
}

.log-level {
  width: 60px;
  text-align: center;
  padding: 2px 4px;
  border-radius: 4px;
  margin-right: 8px;
  font-weight: bold;
  text-transform: uppercase;
}

.log-source {
  color: #1d8cf8;
  margin-right: 8px;
  white-space: nowrap;
}

.log-message {
  flex-grow: 1;
  word-break: break-word;
}

.log-error {
  background-color: rgba(253, 93, 147, 0.1);
}

.log-error .log-level {
  background-color: #fd5d93;
  color: white;
}

.log-warning {
  background-color: rgba(255, 214, 102, 0.1);
}

.log-warning .log-level {
  background-color: #ffd666;
  color: #1e1e2f;
}

.log-info {
  background-color: rgba(29, 140, 248, 0.1);
}

.log-info .log-level {
  background-color: #1d8cf8;
  color: white;
}

.log-debug {
  background-color: rgba(0, 242, 195, 0.1);
}

.log-debug .log-level {
  background-color: #00f2c3;
  color: #1e1e2f;
}

.no-logs {
  color: #a9a9a9;
  text-align: center;
  padding: 16px;
}

.btn {
  padding: 4px 8px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 12px;
  background-color: #27293d;
  color: #ffffff;
}

.btn:hover {
  background-color: #2c2c40;
}
</style>