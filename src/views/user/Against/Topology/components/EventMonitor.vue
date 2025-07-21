<template>
  <div class="event-monitor">
    <div class="event-monitor-header">
      <h3>演练过程记录</h3>
      <div class="event-monitor-controls">
        <button class="btn btn-sm" @click="clearAll">清空</button>
        <button class="btn btn-sm" @click="toggleExpand">
          {{ expanded ? '收起' : '展开' }}
        </button>
      </div>
    </div>
    <div class="event-monitor-content" :class="{ 'expanded': expanded }">
      <!-- 关键事件 -->
      <div class="event-section">
        <div class="section-header">
          <h4>关键事件</h4>
          <button class="btn btn-xs" @click="clearEvents">清空</button>
        </div>
        <div class="event-list" ref="eventList">
          <div v-for="(event, index) in events" :key="index" class="event-item" :class="event.type">
            <div class="event-time">{{ event.timestamp }}</div>
            <div class="event-icon">
              <i :class="getEventIcon(event.type)"></i>
            </div>
            <div class="event-message">{{ event.message }}</div>
          </div>
          <div v-if="events.length === 0" class="no-events">
            暂无关键事件
          </div>
        </div>
      </div>

      <!-- 系统日志 -->
      <div class="event-section">
        <div class="section-header">
          <h4>系统日志</h4>
          <button class="btn btn-xs" @click="clearLogs">清空</button>
        </div>
        <div class="log-list" ref="logList">
          <div v-for="(log, index) in logs" :key="index" class="log-item" :class="getLogLevelClass(log.level)">
            <div class="log-time">{{ log.timestamp }}</div>
            <div class="log-level">{{ log.level }}</div>
            <div class="log-source">{{ log.source }}</div>
            <div class="log-message">{{ log.message }}</div>
          </div>
          <div v-if="logs.length === 0" class="no-logs">
            暂无系统日志
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EventMonitor',
  props: {
    initialExpanded: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      expanded: this.initialExpanded,
      events: [],
      logs: []
    };
  },
  watch: {
    events() {
      this.$nextTick(() => {
        this.scrollToBottom('eventList');
      });
    },
    logs() {
      this.$nextTick(() => {
        this.scrollToBottom('logList');
      });
    }
  },
  methods: {
    toggleExpand() {
      this.expanded = !this.expanded;
    },
    clearAll() {
      this.clearEvents();
      this.clearLogs();
    },
    clearEvents() {
      this.events = [];
    },
    clearLogs() {
      this.logs = [];
    },
    addEvent(event) {
      // 添加时间戳
      if (!event.timestamp) {
        event.timestamp = new Date().toLocaleTimeString();
      }

      this.events.push(event);

      // 限制事件数量，避免内存占用过多
      if (this.events.length > 50) {
        this.events.shift();
      }
    },
    addLog(log) {
      // 添加时间戳
      if (!log.timestamp) {
        log.timestamp = new Date().toLocaleTimeString();
      }

      // 添加详细信息
      if (!log.details) {
        log.details = '';
      }

      // 添加日志ID
      log.id = Date.now() + Math.floor(Math.random() * 1000);

      this.logs.push(log);

      // 限制日志数量，避免内存占用过多
      if (this.logs.length > 200) {
        this.logs.shift();
      }

      // 如果是重要日志，也添加到关键事件
      if (log.level === 'error' || log.level === 'warning' || log.level === 'success') {
        this.addEvent({
          type: log.level === 'error' ? 'failure' :
            log.level === 'warning' ? 'warning' :
              log.level === 'success' ? 'success' : 'system',
          message: `[${log.source}] ${log.message}`
        });
      }
    },
    scrollToBottom(refName) {
      if (this.$refs[refName]) {
        this.$refs[refName].scrollTop = this.$refs[refName].scrollHeight;
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
        case 'success':
          return 'log-success';
        default:
          return '';
      }
    },
    getEventIcon(type) {
      switch (type) {
        case 'attack':
          return 'fas fa-bomb';
        case 'defense':
          return 'fas fa-shield-alt';
        case 'system':
          return 'fas fa-cog';
        case 'success':
          return 'fas fa-check-circle';
        case 'failure':
          return 'fas fa-times-circle';
        case 'warning':
          return 'fas fa-exclamation-triangle';
        default:
          return 'fas fa-info-circle';
      }
    }
  }
};
</script>

<style scoped>
.event-monitor {
  background-color: #1e1e2f;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
}

.event-monitor-header {
  padding: 8px 12px;
  border-bottom: 1px solid #2c2c40;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.event-monitor-header h3 {
  margin: 0;
  font-size: 14px;
  color: #ffffff;
}

.event-monitor-controls {
  display: flex;
  gap: 4px;
}

.event-monitor-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: height 0.3s;
}

.event-monitor-content.expanded {
  height: 400px;
}

.event-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid #2c2c40;
}

.event-section:last-child {
  border-bottom: none;
}

.section-header {
  padding: 6px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.2);
}

.section-header h4 {
  margin: 0;
  font-size: 12px;
  color: #a9a9a9;
}

.event-list,
.log-list {
  flex-grow: 1;
  overflow-y: auto;
  padding: 4px;
  max-height: 150px;
}

.event-item {
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  font-size: 12px;
}

.event-time {
  color: #a9a9a9;
  margin-right: 8px;
  white-space: nowrap;
  font-size: 10px;
}

.event-icon {
  margin-right: 8px;
  width: 16px;
  text-align: center;
}

.event-message {
  flex-grow: 1;
  word-break: break-word;
}

.event-item.attack {
  background-color: rgba(253, 93, 147, 0.1);
  color: #fd5d93;
}

.event-item.defense {
  background-color: rgba(0, 242, 195, 0.1);
  color: #00f2c3;
}

.event-item.system {
  background-color: rgba(29, 140, 248, 0.1);
  color: #1d8cf8;
}

.event-item.success {
  background-color: rgba(0, 242, 195, 0.1);
  color: #00f2c3;
}

.event-item.failure {
  background-color: rgba(253, 93, 147, 0.1);
  color: #fd5d93;
}

.event-item.warning {
  background-color: rgba(255, 214, 102, 0.1);
  color: #ffd666;
}

.log-item {
  padding: 2px 8px;
  border-radius: 4px;
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  font-size: 11px;
}

.log-time {
  color: #a9a9a9;
  margin-right: 4px;
  white-space: nowrap;
  font-size: 10px;
}

.log-level {
  width: 40px;
  text-align: center;
  padding: 0px 4px;
  border-radius: 2px;
  margin-right: 4px;
  font-weight: bold;
  text-transform: uppercase;
  font-size: 9px;
}

.log-source {
  color: #1d8cf8;
  margin-right: 4px;
  white-space: nowrap;
  font-size: 10px;
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

.log-success {
  background-color: rgba(0, 242, 195, 0.1);
}

.log-success .log-level {
  background-color: #00f2c3;
  color: #1e1e2f;
}

.no-events,
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

.btn-xs {
  padding: 1px 4px;
  font-size: 10px;
}
</style>