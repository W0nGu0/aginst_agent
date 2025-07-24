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
            <button class="btn btn-xs btn-expand" @click="openEventsDialog" title="放大查看">
              <i class="fas fa-expand-alt"></i> 放大
            </button>
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
            <button class="btn btn-xs btn-expand" @click="openLogsDialog" title="放大查看">
              <i class="fas fa-expand-alt"></i> 放大
            </button>
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
            <button class="btn btn-xs btn-expand" @click="openAttackChainDialog" title="放大查看">
              <i class="fas fa-expand-alt"></i> 放大
            </button>
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

    <!-- 弹窗组件 -->
    <!-- 关键事件弹窗 -->
    <div v-if="showEventsDialog" class="dialog-overlay" @mousedown.self="closeEventsDialog">
      <div class="dialog-container"
        :style="{ left: dialogPosition.x, top: dialogPosition.y, width: dialogSize.width, height: dialogSize.height }"
        @mousedown="startDrag($event, 'events')">
        <div class="dialog-header">
          <h3>关键事件</h3>
          <div class="dialog-controls">
            <button class="btn btn-xs" @click="closeEventsDialog" title="关闭">
              <i class="fas fa-times"></i> 关闭
            </button>
          </div>
        </div>
        <div class="dialog-content">
          <div class="event-list dialog-event-list">
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
        <div class="resize-handle resize-handle-se" @mousedown.stop="startResize($event, 'se', 'events')"></div>
      </div>
    </div>

    <!-- 系统日志弹窗 -->
    <div v-if="showLogsDialog" class="dialog-overlay" @mousedown.self="closeLogsDialog">
      <div class="dialog-container"
        :style="{ left: dialogPosition.x, top: dialogPosition.y, width: dialogSize.width, height: dialogSize.height }"
        @mousedown="startDrag($event, 'logs')">
        <div class="dialog-header">
          <h3>系统日志</h3>
          <div class="dialog-controls">
            <select v-model="logFilter" class="log-filter">
              <option value="all">全部</option>
              <option value="info">信息</option>
              <option value="success">成功</option>
              <option value="warning">警告</option>
              <option value="error">错误</option>
              <option value="debug">调试</option>
            </select>
            <button class="btn btn-xs" @click="closeLogsDialog" title="关闭">
              <i class="fas fa-times"></i> 关闭
            </button>
          </div>
        </div>
        <div class="dialog-content">
          <div class="log-list dialog-log-list">
            <div v-for="(log, index) in filteredLogs" :key="index" class="log-item"
              :class="getLogLevelClass(log.level)">
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
        <div class="resize-handle resize-handle-se" @mousedown.stop="startResize($event, 'se', 'logs')"></div>
      </div>
    </div>

    <!-- 攻击链阶段弹窗 -->
    <div v-if="showAttackChainDialog" class="dialog-overlay" @mousedown.self="closeAttackChainDialog">
      <div class="dialog-container"
        :style="{ left: dialogPosition.x, top: dialogPosition.y, width: dialogSize.width, height: dialogSize.height }"
        @mousedown="startDrag($event, 'attackChain')">
        <div class="dialog-header">
          <h3>攻击链阶段</h3>
          <div class="dialog-controls">
            <button class="btn btn-xs" @click="closeAttackChainDialog" title="关闭">
              <i class="fas fa-times"></i> 关闭
            </button>
          </div>
        </div>
        <div class="dialog-content">
          <div class="attack-chain-detailed">
            <div v-for="(stage, index) in attackChainStages" :key="index" class="attack-stage-detailed"
              :class="{ 'active': stage.active, 'completed': stage.completed }">
              <div class="stage-header">
                <div class="stage-icon">
                  <i :class="stage.icon"></i>
                </div>
                <div class="stage-name">{{ stage.name }}</div>
                <div class="stage-status">
                  <i v-if="stage.completed" class="fas fa-check"></i>
                  <i v-else-if="stage.active" class="fas fa-spinner fa-spin"></i>
                </div>
              </div>
              <div class="stage-logs">
                <div v-for="(log, logIndex) in stage.logs" :key="logIndex" class="stage-log-item">
                  <div class="log-time">{{ log.timestamp }}</div>
                  <div class="log-message">{{ log.message }}</div>
                </div>
                <div v-if="stage.logs.length === 0" class="no-stage-logs">
                  暂无该阶段日志
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="resize-handle resize-handle-se" @mousedown.stop="startResize($event, 'se', 'attackChain')"></div>
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
        { name: '侦察', icon: 'fas fa-search', active: false, completed: false, logs: [] },
        { name: '武器化', icon: 'fas fa-wrench', active: false, completed: false, logs: [] },
        { name: '投递', icon: 'fas fa-paper-plane', active: false, completed: false, logs: [] },
        { name: '利用', icon: 'fas fa-bug', active: false, completed: false, logs: [] },
        { name: '安装', icon: 'fas fa-download', active: false, completed: false, logs: [] },
        { name: '命令控制', icon: 'fas fa-terminal', active: false, completed: false, logs: [] },
        { name: '行动目标', icon: 'fas fa-flag', active: false, completed: false, logs: [] }
      ],
      // 简化攻击链控制标志
      currentAttackPhase: -1,
      // 标记是否是从WebSocket接收的日志
      isWebSocketLog: false,
      // 是否已清除前端模拟日志
      hasCleanedSimulatedLogs: false,
      // 弹窗相关
      showEventsDialog: false,
      showLogsDialog: false,
      showAttackChainDialog: false,
      dialogPosition: { x: '25%', y: '25%' },
      dialogSize: { width: '50%', height: '50%' },
      isDragging: false,
      dragOffset: { x: 0, y: 0 },
      isResizing: false,
      resizeDirection: '',
      currentDialog: null
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
  mounted() {
    // 组件挂载时清空所有日志和事件
    this.clearAll();

    // 重置攻击链阶段
    this.resetAttackChain();

    // 标记已清除
    this.hasCleanedSimulatedLogs = true;

    // 添加一条初始化日志
    this.addLog({
      level: 'info',
      source: '系统',
      message: '演练过程记录组件已初始化，等待后端日志推送...',
      timestamp: new Date().toLocaleTimeString(),
      fromWebSocket: true // 标记为WebSocket日志，避免被清除
    });

    // 禁用任务状态自动更新攻击链
    this.disableTaskStatusUpdate = true;
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

      // 事件已经在 addEvent 方法中处理攻击链更新
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

      // 不再根据日志内容更新攻击链阶段，只依赖关键事件
      // this.updateAttackChainFromLogs();

      // 如果收到了WebSocket日志，并且还没有清除模拟日志，则清除
      if (!this.hasCleanedSimulatedLogs && this.logs.some(log => log.fromWebSocket)) {
        this.cleanSimulatedLogs();
      }
    },
    attackTaskStatus: {
      handler(newStatus) {
        if (newStatus) {
          // 如果有新的日志，添加到日志列表
          if (newStatus.logs && newStatus.logs.length > 0) {
            // 获取最新的日志
            const latestLog = newStatus.logs[newStatus.logs.length - 1];

            // 检查是否已经存在相同ID的日志
            const existingLog = this.logs.find(log => log.id === latestLog.id);
            if (!existingLog) {
              this.addLog({
                ...latestLog,
                fromWebSocket: true // 标记为WebSocket日志
              });
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

      // 添加来源标记
      if (event.fromWebSocket === undefined) {
        event.fromWebSocket = false;
      }

      // 检查是否有重复事件（相同类型和消息内容）
      const isDuplicate = this.events.some(existingEvent => {
        // 检查最近5秒内的事件，避免长时间的重复检查
        const timeDiff = Math.abs(new Date(existingEvent.timestamp) - new Date(event.timestamp));
        if (timeDiff > 5000) return false;

        return existingEvent.type === event.type &&
          existingEvent.message === event.message;
      });

      // 如果是重复事件，不添加
      if (isDuplicate) {
        console.log('跳过重复事件:', event.message);
        return;
      }

      // 添加到事件列表
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

      // 如果是关键攻击事件，更新攻击链阶段
      if (event.fromWebSocket) {
        this.updateAttackChainFromEvent(event);
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

      // 标记日志来源
      if (log.fromWebSocket === undefined) {
        // 如果没有明确标记，默认为非WebSocket日志
        log.fromWebSocket = false;
      }

      // 如果已经清除了模拟日志，且当前日志不是来自WebSocket，则不添加
      if (this.hasCleanedSimulatedLogs && !log.fromWebSocket) {
        console.log('跳过非WebSocket日志:', log.message);
        return;
      }

      // 检查是否有重复日志（相同来源和消息内容）
      const isDuplicate = this.logs.some(existingLog => {
        // 检查最近5秒内的日志，避免长时间的重复检查
        const timeDiff = Math.abs(new Date(existingLog.timestamp) - new Date(log.timestamp));
        if (timeDiff > 5000) return false;

        return existingLog.source === log.source &&
          existingLog.message === log.message &&
          existingLog.level === log.level;
      });

      // 如果是重复日志，不添加
      if (isDuplicate) {
        console.log('跳过重复日志:', log.message);
        return;
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
          message: `[${log.source}] ${log.message}`,
          fromWebSocket: log.fromWebSocket
        });
      }

      // 检查是否是关键攻击事件，如果是，添加到关键事件区域
      if (this.isKeyAttackEvent(log)) {
        const eventType = this.determineEventType(log);
        this.addEvent({
          type: eventType,
          message: `[${log.source}] ${log.message}`,
          fromWebSocket: log.fromWebSocket
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
      console.log('重置攻击链状态');

      // 清空所有阶段状态
      this.attackChainStages.forEach(stage => {
        stage.active = false;
        stage.completed = false;
        stage.logs = [];
      });

      // 重置攻击链相关标志
      this.currentAttackPhase = -1;
    },



    // 根据事件内容更新攻击链阶段
    updateAttackChainFromEvent(event) {
      if (!event || !event.message) return;

      // 只处理来自WebSocket的事件
      if (!event.fromWebSocket) {
        return;
      }

      const message = event.message.toLowerCase();

      // 简化的忽略列表，只忽略一些明确不应该触发攻击链更新的消息
      const ignoreMessages = [
        'websocket连接已建立',
        '演练过程记录组件已初始化',
        '等待后端日志推送',
        '已清除所有日志'
      ];

      // 如果消息完全匹配忽略列表中的某一项，直接返回
      if (ignoreMessages.some(phrase => message === phrase)) {
        return;
      }

      // 检查是否是重置攻击链的事件
      if (message.includes('开始自动分析网络拓扑') ||
        message.includes('开始执行自动攻击') ||
        message.includes('攻击智能体启动') ||
        message.includes('收到攻击指令') ||
        (message.includes('开始对目标') && message.includes('执行'))) {
        console.log('检测到攻击开始事件，重置攻击链');
        this.resetAttackChain();
        return;
      }

      // 使用更宽松的匹配规则，确保能够捕获到攻击链的各个阶段

      // 侦察阶段 - 宽松匹配
      if (message.includes('侦察') ||
        message.includes('扫描') ||
        message.includes('情报收集') ||
        message.includes('元数据')) {
        console.log('匹配：激活侦察阶段:', message);
        this.activateStage(0, event.message);
        return;
      }

      // 武器化阶段 - 宽松匹配
      if (message.includes('武器化') ||
        message.includes('生成') ||
        message.includes('定制') ||
        message.includes('钓鱼邮件')) {
        console.log('匹配：激活武器化阶段:', message);
        this.activateStage(1, event.message);
        return;
      }

      // 投递阶段 - 宽松匹配
      if (message.includes('投递') ||
        message.includes('发送') ||
        message.includes('邮件已发送')) {
        console.log('匹配：激活投递阶段:', message);
        this.activateStage(2, event.message);
        return;
      }

      // 利用阶段 - 宽松匹配
      if (message.includes('利用') ||
        message.includes('点击') ||
        message.includes('漏洞') ||
        message.includes('凭据')) {
        console.log('匹配：激活利用阶段:', message);
        this.activateStage(3, event.message);
        return;
      }

      // 安装阶段 - 宽松匹配
      if (message.includes('安装') ||
        message.includes('持久') ||
        message.includes('访问')) {
        console.log('匹配：激活安装阶段:', message);
        this.activateStage(4, event.message);
        return;
      }

      // 命令控制阶段 - 宽松匹配
      if (message.includes('命令') ||
        message.includes('控制') ||
        message.includes('远程连接')) {
        console.log('匹配：激活命令控制阶段:', message);
        this.activateStage(5, event.message);
        return;
      }

      // 行动目标阶段 - 宽松匹配
      if (message.includes('目标') ||
        message.includes('数据') ||
        message.includes('完全控制') ||
        message.includes('攻陷')) {
        console.log('匹配：激活行动目标阶段:', message);
        this.activateStage(6, event.message);
        return;
      }
    },




    // 激活特定阶段
    activateStage(index, logMessage = null) {
      // 确保索引有效
      if (index < 0 || index >= this.attackChainStages.length) return;

      console.log(`激活攻击链阶段: ${index} - ${this.attackChainStages[index].name}`);

      // 更新当前阶段索引
      if (index > this.currentAttackPhase) {
        this.currentAttackPhase = index;
      }

      // 激活当前阶段
      this.attackChainStages[index].active = true;

      // 完成之前的所有阶段
      for (let i = 0; i < index; i++) {
        this.attackChainStages[i].active = false;
        this.attackChainStages[i].completed = true;
      }

      // 重置后面的阶段
      for (let i = index + 1; i < this.attackChainStages.length; i++) {
        this.attackChainStages[i].active = false;
        this.attackChainStages[i].completed = false;
      }

      // 如果提供了日志消息，添加到对应阶段的日志中
      if (logMessage) {
        // 创建日志对象
        const stageLog = {
          timestamp: new Date().toLocaleTimeString(),
          message: logMessage
        };

        // 添加到对应阶段的日志中
        this.attackChainStages[index].logs.push(stageLog);

        // 限制日志数量
        if (this.attackChainStages[index].logs.length > 20) {
          this.attackChainStages[index].logs.shift();
        }
      }
    },

    // 根据攻击任务状态更新攻击链阶段 - 已禁用，只依赖关键事件
    updateAttackChainFromTaskStatus(taskStatus) {
      // 禁用任务状态自动更新攻击链，只依赖关键事件
      return;
    },

    // 清除前端模拟的日志，只保留WebSocket日志
    cleanSimulatedLogs() {
      if (this.hasCleanedSimulatedLogs) return;

      console.log('清除前端模拟日志，只保留WebSocket日志');

      // 清空所有日志和事件
      this.logs = [];
      this.events = [];

      // 重置攻击链阶段
      this.resetAttackChain();

      // 标记已清除
      this.hasCleanedSimulatedLogs = true;

      // 添加一条清除日志的记录
      this.addLog({
        level: 'info',
        source: '系统',
        message: '已清除所有日志，等待后端实时日志推送...',
        timestamp: new Date().toLocaleTimeString(),
        fromWebSocket: true
      });
    },

    // 判断是否是关键攻击事件
    isKeyAttackEvent(log) {
      const msg = log.message.toLowerCase();
      const source = log.source.toLowerCase();

      // 关键词列表
      const keyPhrases = [
        '开始侦察', '扫描目标', '情报收集', '元数据',
        '武器化', '生成钓鱼', '定制钓鱼',
        '投递', '发送邮件', '邮件已发送',
        '利用', '漏洞', '点击链接', '凭据',
        '安装', '持久化', '访问权限',
        '命令控制', '远程连接', '横向移动',
        '目标行动', '数据窃取', '攻陷', '完成'
      ];

      // 检查消息是否包含关键词
      return keyPhrases.some(phrase => msg.includes(phrase)) ||
        log.level === 'success' ||
        log.level === 'error' ||
        source.includes('攻击智能体') ||
        source.includes('中央智能体');
    },

    // 确定事件类型
    determineEventType(log) {
      const level = log.level?.toLowerCase();
      const msg = log.message?.toLowerCase() || '';

      if (level === 'error') {
        return 'failure';
      } else if (level === 'warning') {
        return 'warning';
      } else if (level === 'success') {
        return 'success';
      } else if (msg.includes('攻击') || msg.includes('侦察') || msg.includes('扫描') ||
        msg.includes('武器化') || msg.includes('投递') || msg.includes('利用') ||
        msg.includes('安装') || msg.includes('命令') || msg.includes('控制') ||
        msg.includes('目标')) {
        return 'attack';
      } else if (msg.includes('防御') || msg.includes('阻止') || msg.includes('检测')) {
        return 'defense';
      } else {
        return 'system';
      }
    },

    // 弹窗相关方法
    // 打开关键事件弹窗
    openEventsDialog() {
      this.showEventsDialog = true;
      this.currentDialog = 'events';
      // 添加全局事件监听
      document.addEventListener('mousemove', this.handleMouseMove);
      document.addEventListener('mouseup', this.handleMouseUp);
    },

    // 关闭关键事件弹窗
    closeEventsDialog() {
      this.showEventsDialog = false;
      if (this.currentDialog === 'events') {
        this.currentDialog = null;
        // 移除全局事件监听
        document.removeEventListener('mousemove', this.handleMouseMove);
        document.removeEventListener('mouseup', this.handleMouseUp);
      }
    },

    // 打开系统日志弹窗
    openLogsDialog() {
      this.showLogsDialog = true;
      this.currentDialog = 'logs';
      // 添加全局事件监听
      document.addEventListener('mousemove', this.handleMouseMove);
      document.addEventListener('mouseup', this.handleMouseUp);
    },

    // 关闭系统日志弹窗
    closeLogsDialog() {
      this.showLogsDialog = false;
      if (this.currentDialog === 'logs') {
        this.currentDialog = null;
        // 移除全局事件监听
        document.removeEventListener('mousemove', this.handleMouseMove);
        document.removeEventListener('mouseup', this.handleMouseUp);
      }
    },

    // 打开攻击链阶段弹窗
    openAttackChainDialog() {
      this.showAttackChainDialog = true;
      this.currentDialog = 'attackChain';
      // 添加全局事件监听
      document.addEventListener('mousemove', this.handleMouseMove);
      document.addEventListener('mouseup', this.handleMouseUp);
    },

    // 关闭攻击链阶段弹窗
    closeAttackChainDialog() {
      this.showAttackChainDialog = false;
      if (this.currentDialog === 'attackChain') {
        this.currentDialog = null;
        // 移除全局事件监听
        document.removeEventListener('mousemove', this.handleMouseMove);
        document.removeEventListener('mouseup', this.handleMouseUp);
      }
    },

    // 开始拖动
    startDrag(event, dialogType) {
      if (event.target.closest('.dialog-header')) {
        this.isDragging = true;
        this.currentDialog = dialogType;
        const dialogElement = event.currentTarget;
        const rect = dialogElement.getBoundingClientRect();
        this.dragOffset = {
          x: event.clientX - rect.left,
          y: event.clientY - rect.top
        };
        event.preventDefault();
      }
    },

    // 开始调整大小
    startResize(event, direction, dialogType) {
      this.isResizing = true;
      this.resizeDirection = direction;
      this.currentDialog = dialogType;
      event.preventDefault();
    },

    // 处理鼠标移动
    handleMouseMove(event) {
      if (this.isDragging) {
        // 计算新位置
        const x = `${event.clientX - this.dragOffset.x}px`;
        const y = `${event.clientY - this.dragOffset.y}px`;

        // 更新位置
        this.dialogPosition = { x, y };
      } else if (this.isResizing) {
        // 获取当前对话框元素
        let dialogElement;
        if (this.currentDialog === 'events' && this.showEventsDialog) {
          dialogElement = document.querySelector('.dialog-container');
        } else if (this.currentDialog === 'logs' && this.showLogsDialog) {
          dialogElement = document.querySelector('.dialog-container');
        } else if (this.currentDialog === 'attackChain' && this.showAttackChainDialog) {
          dialogElement = document.querySelector('.dialog-container');
        }

        if (dialogElement) {
          const rect = dialogElement.getBoundingClientRect();

          // 根据调整方向计算新尺寸
          if (this.resizeDirection === 'se') {
            const width = `${event.clientX - rect.left}px`;
            const height = `${event.clientY - rect.top}px`;
            this.dialogSize = { width, height };
          }
        }
      }
    },

    // 处理鼠标松开
    handleMouseUp() {
      this.isDragging = false;
      this.isResizing = false;
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

/* 弹窗样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}

.dialog-container {
  position: absolute;
  background-color: #1e1e2f;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  min-width: 300px;
  min-height: 200px;
  max-width: 90%;
  max-height: 90%;
  overflow: hidden;
}

.dialog-header {
  padding: 8px 12px;
  border-bottom: 1px solid #2c2c40;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: move;
}

.dialog-header h3 {
  margin: 0;
  font-size: 14px;
  color: #ffffff;
}

.dialog-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.dialog-content {
  flex-grow: 1;
  overflow: auto;
  padding: 8px;
}

.dialog-event-list,
.dialog-log-list {
  max-height: none;
  overflow-y: auto;
}

.resize-handle {
  position: absolute;
  width: 10px;
  height: 10px;
  background-color: #1d8cf8;
  border-radius: 50%;
}

.resize-handle-se {
  bottom: 0;
  right: 0;
  cursor: se-resize;
}

/* 攻击链详细视图样式 */
.attack-chain-detailed {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 8px;
}

.attack-stage-detailed {
  border: 1px solid #2c2c40;
  border-radius: 8px;
  padding: 8px;
  opacity: 0.7;
  transition: all 0.3s ease;
}

.attack-stage-detailed.active {
  opacity: 1;
  border-color: #1d8cf8;
  box-shadow: 0 0 10px rgba(29, 140, 248, 0.3);
}

.attack-stage-detailed.completed {
  opacity: 1;
  border-color: #00f2c3;
  box-shadow: 0 0 10px rgba(0, 242, 195, 0.3);
}

.stage-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #2c2c40;
}

.stage-logs {
  margin-top: 8px;
  max-height: 150px;
  overflow-y: auto;
}

.stage-log-item {
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 2px;
  font-size: 11px;
  display: flex;
}

.stage-log-item .log-time {
  color: #a9a9a9;
  margin-right: 8px;
  white-space: nowrap;
  font-size: 10px;
}

.stage-log-item .log-message {
  flex-grow: 1;
  word-break: break-word;
}

.no-stage-logs {
  color: #a9a9a9;
  text-align: center;
  padding: 8px;
  font-size: 11px;
}

.btn-expand {
  padding: 1px 4px;
  font-size: 10px;
}
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

/* 弹窗样式 */
.dialog-overlay {
position: fixed;
top: 0;
left: 0;
right: 0;
bottom: 0;
background-color: rgba(0, 0, 0, 0.5);
z-index: 1000;
display: flex;
justify-content: center;
align-items: center;
}

.dialog-container {
position: absolute;
background-color: #1e1e2f;
border-radius: 8px;
box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
display: flex;
flex-direction: column;
min-width: 300px;
min-height: 200px;
max-width: 90%;
max-height: 90%;
overflow: hidden;
}

.dialog-header {
padding: 8px 12px;
border-bottom: 1px solid #2c2c40;
display: flex;
justify-content: space-between;
align-items: center;
cursor: move;
}

.dialog-header h3 {
margin: 0;
font-size: 14px;
color: #ffffff;
}

.dialog-controls {
display: flex;
gap: 8px;
align-items: center;
}

.dialog-content {
flex-grow: 1;
overflow: auto;
padding: 8px;
}

.dialog-event-list,
.dialog-log-list {
max-height: none;
overflow-y: auto;
}

.resize-handle {
position: absolute;
width: 10px;
height: 10px;
background-color: #1d8cf8;
border-radius: 50%;
}

.resize-handle-se {
bottom: 0;
right: 0;
cursor: se-resize;
}

/* 攻击链详细视图样式 */
.attack-chain-detailed {
display: flex;
flex-direction: column;
gap: 16px;
padding: 8px;
}

.attack-stage-detailed {
border: 1px solid #2c2c40;
border-radius: 8px;
padding: 8px;
opacity: 0.7;
transition: all 0.3s ease;
}

.attack-stage-detailed.active {
opacity: 1;
border-color: #1d8cf8;
box-shadow: 0 0 10px rgba(29, 140, 248, 0.3);
}

.attack-stage-detailed.completed {
opacity: 1;
border-color: #00f2c3;
box-shadow: 0 0 10px rgba(0, 242, 195, 0.3);
}

.stage-header {
display: flex;
align-items: center;
gap: 8px;
padding-bottom: 8px;
border-bottom: 1px solid #2c2c40;
}

.stage-logs {
margin-top: 8px;
max-height: 150px;
overflow-y: auto;
}

.stage-log-item {
padding: 4px 8px;
border-radius: 4px;
margin-bottom: 2px;
font-size: 11px;
display: flex;
}

.stage-log-item .log-time {
color: #a9a9a9;
margin-right: 8px;
white-space: nowrap;
font-size: 10px;
}

.stage-log-item .log-message {
flex-grow: 1;
word-break: break-word;
}

.no-stage-logs {
color: #a9a9a9;
text-align: center;
padding: 8px;
font-size: 11px;
}

.btn-expand {
padding: 1px 4px;
font-size: 10px;
}
</style>