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
          <div class="section-controls">
            <span class="event-count">{{ events.length }} 事件</span>
            <button class="btn btn-xs" @click="clearEvents">清空</button>
          </div>
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
          <div class="section-controls">
            <span class="log-count">{{ logs.length }} 日志</span>
            <select v-model="logFilter" class="log-filter">
              <option value="all">全部</option>
              <option value="info">信息</option>
              <option value="success">成功</option>
              <option value="warning">警告</option>
              <option value="error">错误</option>
              <option value="debug">调试</option>
            </select>
            <button class="btn btn-xs" @click="clearLogs">清空</button>
          </div>
        </div>
        <div class="log-list" ref="logList">
          <div v-for="(log, index) in filteredLogs" :key="index" class="log-item" :class="getLogLevelClass(log.level)">
            <div class="log-time">{{ log.timestamp }}</div>
            <div class="log-level">{{ log.level }}</div>
            <div class="log-source">{{ log.source }}</div>
            <div class="log-message">{{ log.message }}</div>
            <div v-if="log.details" class="log-details" @click="toggleDetails(log)">
              <i class="fas" :class="log.showDetails ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            </div>
          </div>
          <div v-if="filteredLogs.length === 0" class="no-logs">
            {{ logs.length > 0 ? '没有匹配的日志' : '暂无系统日志' }}
          </div>
        </div>
      </div>

      <!-- 攻击链阶段 -->
      <div class="event-section">
        <div class="section-header">
          <h4>攻击链阶段</h4>
          <div class="section-controls">
            <button class="btn btn-xs" @click="resetAttackChain">重置</button>
          </div>
        </div>
        <div class="attack-chain">
          <div v-for="(stage, index) in attackChainStages" :key="index" class="attack-stage"
            :class="{ 'active': stage.active, 'completed': stage.completed }">
            <div class="stage-icon">
              <i :class="stage.icon"></i>
            </div>
            <div class="stage-name">{{ stage.name }}</div>
            <div class="stage-status">
              <i v-if="stage.completed" class="fas fa-check"></i>
              <i v-else-if="stage.active" class="fas fa-spinner fa-spin"></i>
            </div>
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
    },
    attackTaskStatus: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      expanded: this.initialExpanded,
      events: [],
      logs: [],
      logFilter: 'all',
      attackChainStages: [
        { name: '侦察', icon: 'fas fa-search', active: false, completed: false },
        { name: '武器化', icon: 'fas fa-wrench', active: false, completed: false },
        { name: '投递', icon: 'fas fa-paper-plane', active: false, completed: false },
        { name: '利用', icon: 'fas fa-bug', active: false, completed: false },
        { name: '安装', icon: 'fas fa-download', active: false, completed: false },
        { name: '命令控制', icon: 'fas fa-terminal', active: false, completed: false },
        { name: '行动目标', icon: 'fas fa-flag', active: false, completed: false }
      ]
    };
  },
  computed: {
    filteredLogs() {
      if (this.logFilter === 'all') {
        return this.logs;
      }
      return this.logs.filter(log => log.level === this.logFilter);
    }
  },
  watch: {
    events() {
      // 保存当前滚动状态
      const wasAtBottom = this.isScrolledToBottom('eventList');
      
      this.$nextTick(() => {
        // 只有当之前在底部时，才自动滚动到底部
        if (wasAtBottom) {
          this.scrollToBottom('eventList');
        }
      });

      // 根据事件内容更新攻击链阶段
      this.updateAttackChainFromEvents();
    },
    logs() {
      // 保存当前滚动状态
      const wasAtBottom = this.isScrolledToBottom('logList');
      
      this.$nextTick(() => {
        // 只有当之前在底部时，才自动滚动到底部
        if (wasAtBottom) {
          this.scrollToBottom('logList');
        }
      });

      // 根据日志内容更新攻击链阶段
      this.updateAttackChainFromLogs();
    },
    attackTaskStatus: {
      handler(newStatus) {
        if (newStatus) {
          // 根据攻击任务状态更新攻击链阶段
          this.updateAttackChainFromTaskStatus(newStatus);
          
          // 如果有新的日志，添加到日志列表
          if (newStatus.logs && newStatus.logs.length > 0) {
            // 获取最新的日志
            const latestLog = newStatus.logs[newStatus.logs.length - 1];
            
            // 检查是否已经存在相同ID的日志
            const existingLog = this.logs.find(log => log.id === latestLog.id);
            if (!existingLog) {
              this.addLog(latestLog);
            }
          }
        }
      },
      deep: true
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
      // 检查滚动条是否在底部
      const wasAtBottom = this.isScrolledToBottom('eventList');
      
      // 添加时间戳
      if (!event.timestamp) {
        event.timestamp = new Date().toLocaleTimeString();
      }

      this.events.push(event);

      // 限制事件数量，避免内存占用过多
      if (this.events.length > 50) {
        this.events.shift();
      }
      
      // 如果之前在底部，则在下一个渲染周期滚动到底部
      if (wasAtBottom) {
        this.$nextTick(() => {
          this.scrollToBottom('eventList');
        });
      }
    },
    addLog(log) {
      // 检查滚动条是否在底部
      const wasAtBottom = this.isScrolledToBottom('logList');
      
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

      // 如果之前在底部，则在下一个渲染周期滚动到底部
      if (wasAtBottom) {
        this.$nextTick(() => {
          this.scrollToBottom('logList');
        });
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
    // 检查滚动条是否在底部或接近底部
    isScrolledToBottom(refName) {
      if (!this.$refs[refName]) return false;
      
      const element = this.$refs[refName];
      // 如果滚动条位置在距离底部5像素内，认为是在底部
      return element.scrollHeight - element.scrollTop - element.clientHeight < 5;
    },
    
    // 滚动到底部
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
    },

    // 切换日志详情显示
    toggleDetails(log) {
      log.showDetails = !log.showDetails;
    },

    // 重置攻击链状态
    resetAttackChain() {
      this.attackChainStages.forEach(stage => {
        stage.active = false;
        stage.completed = false;
      });
    },

    // 根据事件内容更新攻击链阶段
    updateAttackChainFromEvents() {
      // 检查最近的事件
      const recentEvents = this.events.slice(-5);

      for (const event of recentEvents) {
        const message = event.message.toLowerCase();

        // 侦察阶段
        if (message.includes('侦察') || message.includes('扫描') || message.includes('情报收集') || message.includes('元数据')) {
          this.activateStage(0);
        }

        // 武器化阶段
        if (message.includes('武器化') || message.includes('生成') || message.includes('定制') || message.includes('钓鱼邮件')) {
          this.activateStage(1);
        }

        // 投递阶段
        if (message.includes('投递') || message.includes('发送') || message.includes('邮件已发送')) {
          this.activateStage(2);
        }

        // 利用阶段
        if (message.includes('利用') || message.includes('点击') || message.includes('漏洞') || message.includes('凭据')) {
          this.activateStage(3);
        }

        // 安装阶段
        if (message.includes('安装') || message.includes('持久') || message.includes('访问')) {
          this.activateStage(4);
        }

        // 命令控制阶段
        if (message.includes('命令') || message.includes('控制') || message.includes('远程连接')) {
          this.activateStage(5);
        }

        // 行动目标阶段
        if (message.includes('目标') || message.includes('数据') || message.includes('完全控制') || message.includes('攻陷')) {
          this.activateStage(6);
        }
      }
    },

    // 根据日志内容更新攻击链阶段
    updateAttackChainFromLogs() {
      // 检查最近的日志
      const recentLogs = this.logs.slice(-10);

      for (const log of recentLogs) {
        const source = log.source.toLowerCase();
        const message = log.message.toLowerCase();

        // 侦察阶段
        if (source.includes('侦察') || message.includes('扫描') || message.includes('情报') || message.includes('元数据')) {
          this.activateStage(0);
        }

        // 武器化阶段
        if (source.includes('武器化') || message.includes('生成') || message.includes('定制') || message.includes('钓鱼邮件')) {
          this.activateStage(1);
        }

        // 投递阶段
        if (source.includes('投递') || message.includes('发送') || message.includes('邮件')) {
          this.activateStage(2);
        }

        // 利用阶段
        if (source.includes('利用') || message.includes('点击') || message.includes('漏洞') || message.includes('凭据')) {
          this.activateStage(3);
        }

        // 安装阶段
        if (source.includes('安装') || message.includes('持久') || message.includes('访问')) {
          this.activateStage(4);
        }

        // 命令控制阶段
        if (source.includes('命令') || message.includes('控制') || message.includes('远程')) {
          this.activateStage(5);
        }

        // 行动目标阶段
        if (source.includes('目标') || message.includes('数据') || message.includes('控制') || message.includes('攻陷')) {
          this.activateStage(6);
        }
      }
    },

    // 激活特定阶段
    activateStage(index) {
      // 确保索引有效
      if (index < 0 || index >= this.attackChainStages.length) return;

      // 激活当前阶段
      this.attackChainStages[index].active = true;

      // 完成之前的所有阶段
      for (let i = 0; i < index; i++) {
        this.attackChainStages[i].active = false;
        this.attackChainStages[i].completed = true;
      }
    },
    
    // 根据攻击任务状态更新攻击链阶段
    updateAttackChainFromTaskStatus(taskStatus) {
      if (!taskStatus || !taskStatus.phase || !taskStatus.progress) return;
      
      // 阶段映射
      const phaseMap = {
        'reconnaissance': 0,
        'weaponization': 1,
        'delivery': 2,
        'exploitation': 3,
        'installation': 4,
        'command_and_control': 5,
        'actions_on_objectives': 6
      };
      
      // 获取当前阶段索引
      const currentPhaseIndex = phaseMap[taskStatus.phase];
      
      if (currentPhaseIndex !== undefined) {
        // 重置所有阶段
        this.resetAttackChain();
        
        // 激活当前阶段
        this.attackChainStages[currentPhaseIndex].active = true;
        
        // 完成之前的所有阶段
        for (let i = 0; i < currentPhaseIndex; i++) {
          this.attackChainStages[i].completed = true;
        }
        
        // 如果进度达到100%，完成所有阶段
        if (taskStatus.progress >= 100) {
          for (let i = 0; i < this.attackChainStages.length; i++) {
            this.attackChainStages[i].active = false;
            this.attackChainStages[i].completed = true;
          }
        }
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

/* 新增样式 */
.section-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.event-count,
.log-count {
  font-size: 10px;
  color: #a9a9a9;
}

.log-filter {
  background-color: #27293d;
  color: #ffffff;
  border: 1px solid #2c2c40;
  border-radius: 3px;
  padding: 1px 4px;
  font-size: 10px;
  outline: none;
}

.log-details {
  margin-left: 4px;
  cursor: pointer;
  color: #a9a9a9;
  width: 16px;
  text-align: center;
}

/* 攻击链样式 */
.attack-chain {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  padding: 10px;
  overflow-x: auto;
}

.attack-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
  position: relative;
  opacity: 0.5;
  transition: all 0.3s ease;
}

.attack-stage:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 15px;
  right: -15px;
  width: 30px;
  height: 2px;
  background-color: #2c2c40;
}

.attack-stage.active {
  opacity: 1;
}

.attack-stage.completed {
  opacity: 1;
}

.attack-stage.active .stage-icon {
  background-color: #1d8cf8;
  box-shadow: 0 0 10px rgba(29, 140, 248, 0.5);
}

.attack-stage.completed .stage-icon {
  background-color: #00f2c3;
  box-shadow: 0 0 10px rgba(0, 242, 195, 0.5);
}

.attack-stage.completed:not(:last-child)::after {
  background-color: #00f2c3;
}

.attack-stage.active:not(:last-child)::after {
  background-color: #1d8cf8;
}

.stage-icon {
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

.stage-name {
  font-size: 9px;
  color: #a9a9a9;
  text-align: center;
  max-width: 60px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stage-status {
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
</style>