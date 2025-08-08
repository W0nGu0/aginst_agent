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
            <div class="log-level">{{ formatLogLevel(log.level) }}</div>
            <div class="log-source">{{ formatLogSource(log.source) }}</div>
            <div class="log-message">{{ formatLogMessage(log.message) }}</div>
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
              <div class="log-level">{{ formatLogLevel(log.level) }}</div>
              <div class="log-source">{{ formatLogSource(log.source) }}</div>
              <div class="log-message">{{ formatLogMessage(log.message) }}</div>
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
  emits: ['nodes-status-reset', 'nodes-status-refreshed'],
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
        {
          name: '侦察',
          icon: 'fas fa-search',
          active: false,
          completed: false,
          logs: [],
          // 新增字段用于可视化增强
          targetNodes: [], // 当前阶段涉及的目标节点
          attackPath: [], // 攻击路径 [{from: 'internet', to: 'firewall', technique: 'port_scan'}]
          currentProgress: 0, // 当前阶段进度 0-100
          techniques: [], // 使用的攻击技术 ['port_scan', 'vulnerability_scan']
          timeline: [], // 时间线事件
          status: 'pending', // pending, active, success, failed
          duration: 0, // 阶段持续时间（秒）
          startTime: null, // 开始时间
          endTime: null // 结束时间
        },
        {
          name: '武器化',
          icon: 'fas fa-wrench',
          active: false,
          completed: false,
          logs: [],
          targetNodes: [],
          attackPath: [],
          currentProgress: 0,
          techniques: [],
          timeline: [],
          status: 'pending',
          duration: 0,
          startTime: null,
          endTime: null
        },
        {
          name: '投递',
          icon: 'fas fa-paper-plane',
          active: false,
          completed: false,
          logs: [],
          targetNodes: [],
          attackPath: [],
          currentProgress: 0,
          techniques: [],
          timeline: [],
          status: 'pending',
          duration: 0,
          startTime: null,
          endTime: null
        },
        {
          name: '利用',
          icon: 'fas fa-bug',
          active: false,
          completed: false,
          logs: [],
          targetNodes: [],
          attackPath: [],
          currentProgress: 0,
          techniques: [],
          timeline: [],
          status: 'pending',
          duration: 0,
          startTime: null,
          endTime: null
        },
        {
          name: '安装',
          icon: 'fas fa-download',
          active: false,
          completed: false,
          logs: [],
          targetNodes: [],
          attackPath: [],
          currentProgress: 0,
          techniques: [],
          timeline: [],
          status: 'pending',
          duration: 0,
          startTime: null,
          endTime: null
        },
        {
          name: '命令控制',
          icon: 'fas fa-terminal',
          active: false,
          completed: false,
          logs: [],
          targetNodes: [],
          attackPath: [],
          currentProgress: 0,
          techniques: [],
          timeline: [],
          status: 'pending',
          duration: 0,
          startTime: null,
          endTime: null
        },
        {
          name: '行动目标',
          icon: 'fas fa-flag',
          active: false,
          completed: false,
          logs: [],
          targetNodes: [],
          attackPath: [],
          currentProgress: 0,
          techniques: [],
          timeline: [],
          status: 'pending',
          duration: 0,
          startTime: null,
          endTime: null
        }
      ],
      // 简化攻击链控制标志
      currentAttackPhase: -1,
      // 标记是否是从WebSocket接收的日志
      isWebSocketLog: false,
      // 是否已清除前端模拟日志
      hasCleanedSimulatedLogs: false,
      // 新增：网络节点状态管理
      networkNodes: {
        'internet': {
          id: 'internet',
          name: '互联网',
          status: 'normal',
          compromised: false,
          attackLevel: 0,
          lastActivity: null,
          attackHistory: []
        },
        'firewall': {
          id: 'firewall',
          name: '防火墙',
          status: 'normal',
          compromised: false,
          attackLevel: 0,
          lastActivity: null,
          attackHistory: []
        },
        'dmz-web': {
          id: 'dmz-web',
          name: 'DMZ Web服务器',
          status: 'normal',
          compromised: false,
          attackLevel: 0,
          lastActivity: null,
          attackHistory: []
        },
        'dmz-dns': {
          id: 'dmz-dns',
          name: 'DMZ DNS服务器',
          status: 'normal',
          compromised: false,
          attackLevel: 0,
          lastActivity: null,
          attackHistory: []
        },
        'internal-db': {
          id: 'internal-db',
          name: '内网数据库',
          status: 'normal',
          compromised: false,
          attackLevel: 0,
          lastActivity: null,
          attackHistory: []
        },
        'internal-file': {
          id: 'internal-file',
          name: '内网文件服务器',
          status: 'normal',
          compromised: false,
          attackLevel: 0,
          lastActivity: null,
          attackHistory: []
        },
        'pc-user': {
          id: 'pc-user',
          name: '用户PC',
          status: 'normal',
          compromised: false,
          attackLevel: 0,
          lastActivity: null,
          attackHistory: []
        }
      },
      // 新增：攻击路径记录
      attackPaths: [],
      // 新增：当前活跃的攻击连接
      activeConnections: [],
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

      // 移除事件数量限制，保留所有关键事件和系统日志
      // if (this.events.length > 50) {
      //   this.events.shift();
      // }

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

      // 确保log是对象且有必要的属性
      if (!log || typeof log !== 'object') {
        console.warn('无效的日志对象:', log);
        return;
      }

      // 确保message是字符串
      if (typeof log.message !== 'string') {
        if (typeof log.message === 'object') {
          log.message = JSON.stringify(log.message);
        } else {
          log.message = String(log.message || '');
        }
      }

      // 确保source是字符串
      if (typeof log.source !== 'string') {
        log.source = String(log.source || '未知');
      }

      // 确保level是字符串
      if (typeof log.level !== 'string') {
        log.level = String(log.level || 'info');
      }

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

      // 处理新的结构化攻击信息
      if (log.attack_info) {
        // 保存原始攻击信息
        log.attackInfo = log.attack_info;

        // 更新网络节点状态
        this.updateNetworkNodeStatus(log.attack_info);

        // 记录攻击路径
        this.recordAttackPath(log.attack_info);

        // 触发拓扑动画事件
        this.emitTopologyAnimationEvent(log.attack_info, log);
      }

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

    // 格式化日志级别显示
    formatLogLevel(level) {
      if (!level || typeof level !== 'string') {
        return 'INFO';
      }
      return level.toUpperCase();
    },

    // 格式化日志来源显示
    formatLogSource(source) {
      if (!source || typeof source !== 'string') {
        return '未知';
      }
      // 如果来源过长，截断显示
      if (source.length > 20) {
        return source.substring(0, 17) + '...';
      }
      return source;
    },

    // 格式化日志消息显示
    formatLogMessage(message) {
      if (!message) {
        return '';
      }

      // 如果是对象，转换为字符串
      if (typeof message === 'object') {
        try {
          return JSON.stringify(message, null, 2);
        } catch (e) {
          return String(message);
        }
      }

      // 如果是字符串但包含特殊字符，进行清理
      let formattedMessage = String(message);

      // 移除多余的空白字符
      formattedMessage = formattedMessage.replace(/\s+/g, ' ').trim();

      // 如果消息过长，截断显示
      if (formattedMessage.length > 200) {
        formattedMessage = formattedMessage.substring(0, 197) + '...';
      }

      return formattedMessage;
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



    // 根据事件内容更新攻击链阶段 - 增强版
    updateAttackChainFromEvent(event) {
      if (!event || !event.message) return;

      // 只处理来自WebSocket的事件
      if (!event.fromWebSocket) {
        return;
      }

      const source = event.source || ''
      const message = event.message.toLowerCase();

      // 只允许"攻击智能体"的日志更新攻击链
      if (!source.includes('攻击智能体')) {
        console.log('🚫 只允许攻击智能体的日志更新攻击链，忽略:', source)
        return
      }

      console.log('✅ 允许更新攻击链的日志来源:', source)

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

      // 解析增强的攻击事件信息
      const attackEvent = this.parseEnhancedAttackEvent({
        message: event.message,
        source: event.source || '系统',
        level: event.level || 'info',
        timestamp: event.timestamp
      });

      console.log('🔍 解析攻击事件:', {
        source: event.source,
        message: event.message,
        attackEvent: attackEvent
      });

      // 添加详细的解析结果日志
      if (attackEvent.stage) {
        console.log('✅ 成功解析攻击阶段:', {
          stage: attackEvent.stage,
          targetNode: attackEvent.targetNode,
          status: attackEvent.status,
          progress: attackEvent.progress
        });
      } else {
        console.log('❌ 未能解析攻击阶段，消息内容:', event.message);
      }

      // 根据解析结果更新攻击链
      if (attackEvent.stage) {
        const stageIndex = this.getStageIndex(attackEvent.stage);
        if (stageIndex !== -1) {
          console.log(`增强匹配：激活${this.attackChainStages[stageIndex].name}阶段:`, JSON.stringify({
            technique: attackEvent.technique,
            targetNode: attackEvent.targetNode,
            progress: attackEvent.progress,
            status: attackEvent.status
          }, null, 2));

          // 使用增强的激活方法
          this.activateStageEnhanced(stageIndex, attackEvent);
          return;
        }
      }

      // 如果增强解析失败，回退到原有的宽松匹配
      console.log('🔄 使用回退匹配机制');
      this.fallbackStageMatching(message, event);
    },

    // 获取阶段索引
    getStageIndex(stageName) {
      const stageMap = {
        'reconnaissance': 0,
        'weaponization': 1,
        'delivery': 2,
        'exploitation': 3,
        'installation': 4,
        'command_and_control': 5,
        'actions_on_objectives': 6
      };
      return stageMap[stageName] !== undefined ? stageMap[stageName] : -1;
    },

    // 回退到原有的宽松匹配
    fallbackStageMatching(message, event) {
      console.log('🔄 执行回退匹配，消息:', message);

      // 侦察阶段 - 扩展关键词
      if (message.includes('侦察') || message.includes('扫描') || message.includes('情报收集') ||
        message.includes('元数据') || message.includes('网络拓扑') || message.includes('分析网络') ||
        message.includes('收集信息') || message.includes('目标识别') || message.includes('端口扫描')) {
        console.log('✅ 回退匹配：激活侦察阶段:', message);
        this.activateStage(0, event.message);
        return;
      }

      // 武器化阶段 - 扩展关键词
      if (message.includes('武器化') || message.includes('生成') || message.includes('定制') ||
        message.includes('钓鱼邮件') || message.includes('制作') || message.includes('准备攻击') ||
        message.includes('恶意载荷') || message.includes('攻击工具')) {
        console.log('✅ 回退匹配：激活武器化阶段:', message);
        this.activateStage(1, event.message);
        return;
      }

      // 投递阶段 - 扩展关键词
      if (message.includes('投递') || message.includes('发送') || message.includes('邮件已发送') ||
        message.includes('传输') || message.includes('投放') || message.includes('分发')) {
        console.log('✅ 回退匹配：激活投递阶段:', message);
        this.activateStage(2, event.message);
        return;
      }

      // 利用阶段 - 扩展关键词
      if (message.includes('利用') || message.includes('点击') || message.includes('漏洞') ||
        message.includes('凭据') || message.includes('执行') || message.includes('触发') ||
        message.includes('获得') || message.includes('权限') || message.includes('访问权限')) {
        console.log('✅ 回退匹配：激活利用阶段:', message);
        this.activateStage(3, event.message);
        return;
      }

      // 安装阶段 - 扩展关键词
      if (message.includes('安装') || message.includes('持久') || message.includes('访问') ||
        message.includes('后门') || message.includes('植入') || message.includes('驻留') ||
        message.includes('建立') || message.includes('部署')) {
        console.log('✅ 回退匹配：激活安装阶段:', message);
        this.activateStage(4, event.message);
        return;
      }

      // 命令控制阶段 - 扩展关键词
      if (message.includes('命令') || message.includes('控制') || message.includes('远程连接') ||
        message.includes('C2') || message.includes('通信') || message.includes('连接') ||
        message.includes('指令') || message.includes('远程')) {
        console.log('✅ 回退匹配：激活命令控制阶段:', message);
        this.activateStage(5, event.message);
        return;
      }

      // 行动目标阶段 - 扩展关键词
      if (message.includes('目标') || message.includes('数据') || message.includes('完全控制') ||
        message.includes('攻陷') || message.includes('窃取') || message.includes('获取') ||
        message.includes('收集') || message.includes('下载') || message.includes('完成')) {
        console.log('✅ 回退匹配：激活行动目标阶段:', message);
        this.activateStage(6, event.message);
        return;
      }

      console.log('⚠️ 回退匹配未找到匹配的攻击阶段:', message);
    },




    // 激活特定阶段 - 基础版本（保持向后兼容）
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
      this.attackChainStages[index].status = 'active';

      // 设置开始时间
      if (!this.attackChainStages[index].startTime) {
        this.attackChainStages[index].startTime = new Date();
      }

      // 完成之前的所有阶段
      for (let i = 0; i < index; i++) {
        this.attackChainStages[i].active = false;
        this.attackChainStages[i].completed = true;
        this.attackChainStages[i].status = 'success';
        this.attackChainStages[i].currentProgress = 100;

        // 设置结束时间
        if (!this.attackChainStages[i].endTime) {
          this.attackChainStages[i].endTime = new Date();
          this.attackChainStages[i].duration = Math.floor((this.attackChainStages[i].endTime - this.attackChainStages[i].startTime) / 1000);
        }
      }

      // 重置后面的阶段
      for (let i = index + 1; i < this.attackChainStages.length; i++) {
        this.attackChainStages[i].active = false;
        this.attackChainStages[i].completed = false;
        this.attackChainStages[i].status = 'pending';
        this.attackChainStages[i].currentProgress = 0;
        this.attackChainStages[i].startTime = null;
        this.attackChainStages[i].endTime = null;
        this.attackChainStages[i].duration = 0;
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

    // 新增：更新网络节点状态
    updateNetworkNodeStatus(attackInfo) {
      const targetNode = attackInfo.target_node;
      if (targetNode && this.networkNodes[targetNode]) {
        const node = this.networkNodes[targetNode];

        // 更新节点状态
        if (attackInfo.status === 'starting') {
          node.status = 'scanning';
          node.attackLevel = Math.max(node.attackLevel, 10);
        } else if (attackInfo.status === 'in_progress') {
          node.status = 'under_attack';
          node.attackLevel = Math.max(node.attackLevel, attackInfo.progress || 50);
        } else if (attackInfo.status === 'completed') {
          node.status = 'compromised';
          node.attackLevel = 100;
          node.compromised = true;
        } else if (attackInfo.status === 'failed') {
          node.status = 'normal';
          node.attackLevel = Math.max(0, node.attackLevel - 20);
        }

        // 更新最后活动时间
        node.lastActivity = new Date();

        // 记录攻击历史
        node.attackHistory.push({
          timestamp: new Date(),
          stage: attackInfo.stage,
          technique: attackInfo.technique,
          status: attackInfo.status,
          progress: attackInfo.progress
        });

        // 限制历史记录数量
        if (node.attackHistory.length > 10) {
          node.attackHistory.shift();
        }

        console.log(`节点状态更新: ${targetNode} -> ${node.status} (${node.attackLevel}%)`);
      }
    },

    // 新增：重置所有节点状态
    resetAllNodeStatus() {
      console.log('🔄 重置所有节点状态...');
      Object.keys(this.networkNodes).forEach(nodeId => {
        const node = this.networkNodes[nodeId];
        node.status = 'normal';
        node.compromised = false;
        node.attackLevel = 0;
        node.lastActivity = null;
        node.attackHistory = [];
      });

      // 触发拓扑图状态更新
      this.$emit('nodes-status-reset');
      console.log('✅ 所有节点状态已重置');
    },

    // 新增：检查并刷新节点状态（基于实际容器状态）
    async refreshNodeStatusFromContainers() {
      console.log('🔍 检查容器状态并刷新节点状态...');

      try {
        // 调用后端API获取容器状态
        const response = await fetch('/api/topology', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            action: 'status',
            template: 'company-topology' // 使用正确的模板名称
          })
        });

        if (response.ok) {
          const data = await response.json();
          console.log('📊 容器状态数据:', data);

          // 根据容器状态更新节点状态
          if (data.running_services) {
            data.running_services.forEach(service => {
              const nodeId = this.mapServiceToNodeId(service.name);
              if (nodeId && this.networkNodes[nodeId]) {
                // 如果容器正在运行，且节点之前被标记为compromised，则重置状态
                if (this.networkNodes[nodeId].status === 'compromised' ||
                  this.networkNodes[nodeId].status === 'under_attack') {
                  console.log(`🔄 重置节点状态: ${nodeId} (容器 ${service.name} 正在运行)`);
                  this.networkNodes[nodeId].status = 'normal';
                  this.networkNodes[nodeId].compromised = false;
                  this.networkNodes[nodeId].attackLevel = 0;
                }
              }
            });
          }

          // 处理失败的服务
          if (data.failed_services) {
            data.failed_services.forEach(service => {
              const nodeId = this.mapServiceToNodeId(service.name);
              if (nodeId && this.networkNodes[nodeId]) {
                console.log(`❌ 标记节点为失败状态: ${nodeId} (容器 ${service.name} 失败)`);
                this.networkNodes[nodeId].status = 'failed';
                this.networkNodes[nodeId].compromised = false;
                this.networkNodes[nodeId].attackLevel = 0;
              }
            });
          }

          // 触发拓扑图更新
          this.$emit('nodes-status-refreshed', this.networkNodes);
          console.log('✅ 节点状态刷新完成');
        }
      } catch (error) {
        console.error('❌ 刷新节点状态失败:', error);
      }
    },

    // 新增：将服务名映射到节点ID
    mapServiceToNodeId(serviceName) {
      const serviceMapping = {
        'web-server': 'dmz-web',
        'dns-server': 'dmz-dns',
        'database': 'internal-db',
        'file-server': 'internal-file',
        'firewall': 'firewall',
        'workstation': 'internal-pc'
      };
      return serviceMapping[serviceName] || serviceName;
    },

    // 新增：记录攻击路径
    recordAttackPath(attackInfo) {
      const sourceNode = attackInfo.source_node;
      const targetNode = attackInfo.target_node;

      if (sourceNode && targetNode && sourceNode !== targetNode) {
        const pathId = `${sourceNode}-${targetNode}-${attackInfo.technique}`;

        // 检查是否已存在相同路径
        const existingPath = this.attackPaths.find(path => path.id === pathId);

        if (existingPath) {
          // 更新现有路径
          existingPath.status = attackInfo.status;
          existingPath.progress = attackInfo.progress;
          existingPath.lastUpdate = new Date();
        } else {
          // 创建新路径
          this.attackPaths.push({
            id: pathId,
            from: sourceNode,
            to: targetNode,
            technique: attackInfo.technique,
            stage: attackInfo.stage,
            status: attackInfo.status,
            progress: attackInfo.progress,
            createdAt: new Date(),
            lastUpdate: new Date()
          });
        }

        console.log(`攻击路径记录: ${sourceNode} -> ${targetNode} (${attackInfo.technique})`);
      }
    },

    // 新增：触发拓扑动画事件
    emitTopologyAnimationEvent(attackInfo, log) {
      // 创建自定义事件，供拓扑图组件监听
      const animationEvent = new CustomEvent('topology-animation', {
        detail: {
          type: 'attack_step',
          attackInfo: attackInfo,
          log: log,
          timestamp: new Date()
        }
      });

      // 分发事件到document，让拓扑图组件可以监听
      document.dispatchEvent(animationEvent);

      console.log('拓扑动画事件已触发:', JSON.stringify({
        stage: attackInfo.stage,
        technique: attackInfo.technique,
        from: attackInfo.source_node,
        to: attackInfo.target_node,
        status: attackInfo.status
      }, null, 2));
    },



    // 判断是否是关键攻击事件
    isKeyAttackEvent(message) {
      const msg = message.message.toLowerCase();
      const source = message.source.toLowerCase();

      // 攻击相关关键词
      const attackKeywords = [
        '攻击', '扫描', '漏洞', '利用', '入侵', '渗透',
        '钓鱼', '载荷', '后门', '提权', '横向移动',
        '数据窃取', '凭据', '会话', 'exploit', 'payload'
      ];

      // 检查消息内容
      const hasAttackKeyword = attackKeywords.some(keyword => msg.includes(keyword));

      // 检查来源
      const isAttackSource = source.includes('攻击') || source.includes('agent');

      return hasAttackKeyword || isAttackSource;
    },

    // 确定事件类型
    determineEventType(message) {
      const level = message.level.toLowerCase();
      const msg = message.message.toLowerCase();

      if (level === 'error' || msg.includes('失败') || msg.includes('错误')) {
        return 'failure';
      } else if (level === 'warning' || msg.includes('警告') || msg.includes('注意')) {
        return 'warning';
      } else if (level === 'success' || msg.includes('成功') || msg.includes('完成')) {
        return 'success';
      } else if (msg.includes('攻击') || msg.includes('利用') || msg.includes('入侵')) {
        return 'attack';
      } else if (msg.includes('防御') || msg.includes('阻止') || msg.includes('拦截')) {
        return 'defense';
      } else {
        return 'system';
      }
    },

    // 清除模拟日志
    cleanSimulatedLogs() {
      console.log('清除模拟日志，保留WebSocket日志');

      // 只保留来自WebSocket的日志
      this.logs = this.logs.filter(log => log.fromWebSocket);
      this.events = this.events.filter(event => event.fromWebSocket);

      // 标记已清除
      this.hasCleanedSimulatedLogs = true;

      // 添加清除日志的记录
      this.addLog({
        level: 'info',
        source: '系统',
        message: '已清除所有模拟日志，现在只显示实时WebSocket日志',
        timestamp: new Date().toLocaleTimeString(),
        fromWebSocket: true
      });
    },

    // 弹窗相关方法
    openEventsDialog() {
      this.showEventsDialog = true;
      this.currentDialog = 'events';
    },

    closeEventsDialog() {
      this.showEventsDialog = false;
      this.currentDialog = null;
    },

    openLogsDialog() {
      this.showLogsDialog = true;
      this.currentDialog = 'logs';
    },

    closeLogsDialog() {
      this.showLogsDialog = false;
      this.currentDialog = null;
    },

    openAttackChainDialog() {
      this.showAttackChainDialog = true;
      this.currentDialog = 'attackChain';
    },

    closeAttackChainDialog() {
      this.showAttackChainDialog = false;
      this.currentDialog = null;
    },

    // 拖拽相关方法
    startDrag(event, dialogType) {
      this.isDragging = true;
      this.currentDialog = dialogType;
      this.dragOffset.x = event.clientX - parseInt(this.dialogPosition.x);
      this.dragOffset.y = event.clientY - parseInt(this.dialogPosition.y);

      document.addEventListener('mousemove', this.handleDrag);
      document.addEventListener('mouseup', this.stopDrag);
    },

    handleDrag(event) {
      if (this.isDragging) {
        this.dialogPosition.x = (event.clientX - this.dragOffset.x) + 'px';
        this.dialogPosition.y = (event.clientY - this.dragOffset.y) + 'px';
      }
    },

    stopDrag() {
      this.isDragging = false;
      document.removeEventListener('mousemove', this.handleDrag);
      document.removeEventListener('mouseup', this.stopDrag);
    },

    // 调整大小相关方法
    startResize(event, direction, dialogType) {
      this.isResizing = true;
      this.resizeDirection = direction;
      this.currentDialog = dialogType;

      document.addEventListener('mousemove', this.handleResize);
      document.addEventListener('mouseup', this.stopResize);
    },

    handleResize(event) {
      if (this.isResizing) {
        const rect = event.target.getBoundingClientRect();
        if (this.resizeDirection === 'se') {
          this.dialogSize.width = (event.clientX - parseInt(this.dialogPosition.x)) + 'px';
          this.dialogSize.height = (event.clientY - parseInt(this.dialogPosition.y)) + 'px';
        }
      }
    },

    stopResize() {
      this.isResizing = false;
      document.removeEventListener('mousemove', this.handleResize);
      document.removeEventListener('mouseup', this.stopResize);
    },
    activateStageEnhanced(index, attackEvent) {
      // 确保索引有效
      if (index < 0 || index >= this.attackChainStages.length) return;

      const stage = this.attackChainStages[index];

      console.log(`增强激活攻击链阶段: ${index} - ${stage.name}`, JSON.stringify(attackEvent, null, 2));

      // 更新当前阶段索引
      if (index > this.currentAttackPhase) {
        this.currentAttackPhase = index;
      }

      // 激活当前阶段
      stage.active = true;
      stage.status = attackEvent.status || 'active';
      stage.currentProgress = attackEvent.progress || 25;

      // 设置开始时间
      if (!stage.startTime) {
        stage.startTime = new Date();
      }

      // 更新目标节点
      if (attackEvent.targetNode && !stage.targetNodes.includes(attackEvent.targetNode)) {
        stage.targetNodes.push(attackEvent.targetNode);
      }

      // 更新攻击技术
      if (attackEvent.technique && !stage.techniques.includes(attackEvent.technique)) {
        stage.techniques.push(attackEvent.technique);
      }

      // 记录攻击路径
      if (attackEvent.sourceNode && attackEvent.targetNode) {
        const pathExists = stage.attackPath.some(path =>
          path.from === attackEvent.sourceNode &&
          path.to === attackEvent.targetNode &&
          path.technique === attackEvent.technique
        );

        if (!pathExists) {
          stage.attackPath.push({
            from: attackEvent.sourceNode,
            to: attackEvent.targetNode,
            technique: attackEvent.technique,
            timestamp: new Date(),
            status: attackEvent.status
          });
        }
      }

      // 添加时间线事件
      stage.timeline.push({
        timestamp: new Date(),
        event: attackEvent.details,
        technique: attackEvent.technique,
        targetNode: attackEvent.targetNode,
        progress: attackEvent.progress,
        status: attackEvent.status
      });

      // 限制时间线事件数量
      if (stage.timeline.length > 50) {
        stage.timeline.shift();
      }

      // 完成之前的所有阶段
      for (let i = 0; i < index; i++) {
        this.attackChainStages[i].active = false;
        this.attackChainStages[i].completed = true;
        this.attackChainStages[i].status = 'success';
        this.attackChainStages[i].currentProgress = 100;

        // 设置结束时间
        if (!this.attackChainStages[i].endTime) {
          this.attackChainStages[i].endTime = new Date();
          this.attackChainStages[i].duration = Math.floor((this.attackChainStages[i].endTime - this.attackChainStages[i].startTime) / 1000);
        }
      }

      // 重置后面的阶段
      for (let i = index + 1; i < this.attackChainStages.length; i++) {
        this.attackChainStages[i].active = false;
        this.attackChainStages[i].completed = false;
        this.attackChainStages[i].status = 'pending';
        this.attackChainStages[i].currentProgress = 0;
        this.attackChainStages[i].startTime = null;
        this.attackChainStages[i].endTime = null;
        this.attackChainStages[i].duration = 0;
      }

      // 添加日志消息
      if (attackEvent.details) {
        const stageLog = {
          timestamp: new Date().toLocaleTimeString(),
          message: attackEvent.details,
          technique: attackEvent.technique,
          targetNode: attackEvent.targetNode,
          progress: attackEvent.progress,
          status: attackEvent.status
        };

        stage.logs.push(stageLog);

        // 限制日志数量
        if (stage.logs.length > 20) {
          stage.logs.shift();
        }
      }

      // 更新网络节点状态
      if (attackEvent.targetNode) {
        this.updateNetworkNodeStatus(
          attackEvent.targetNode,
          attackEvent.status === 'success' ? 'compromised' : 'under_attack',
          attackEvent.progress
        );
      }

      // 记录攻击路径
      if (attackEvent.sourceNode && attackEvent.targetNode) {
        this.recordAttackPath(
          attackEvent.sourceNode,
          attackEvent.targetNode,
          attackEvent.technique,
          attackEvent.status
        );
      }

      // 更新活跃连接
      if (attackEvent.sourceNode && attackEvent.targetNode) {
        this.updateActiveConnections(
          attackEvent.sourceNode,
          attackEvent.targetNode,
          'attack'
        );
      }

      // 触发可视化更新事件
      this.$emit('attack-stage-updated', {
        stageIndex: index,
        stage: stage,
        attackEvent: attackEvent,
        timestamp: new Date()
      });
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

    // 新增：解析增强的攻击事件信息
    parseEnhancedAttackEvent(log) {
      const message = log.message.toLowerCase();
      const source = log.source.toLowerCase();

      // 解析攻击事件的详细信息
      const attackEvent = {
        stage: null,
        sourceNode: null,
        targetNode: null,
        technique: null,
        progress: 0,
        status: 'unknown',
        timestamp: new Date(),
        details: log.message,
        rawLog: log
      };

      // 解析攻击阶段 - 与新的DMZ优先攻击流程精确匹配
      if (message.includes('nmap') || message.includes('扫描防火墙') || message.includes('发现开放端口') || message.includes('完成目标侦察') || message.includes('获取公司信息')) {
        attackEvent.stage = 'reconnaissance';
        attackEvent.technique = this.extractTechnique(message, ['port_scan', 'vulnerability_scan', 'info_gathering']);
      } else if (message.includes('完成恶意载荷制作') || message.includes('生成针对性钓鱼邮件') || message.includes('钓鱼邮件')) {
        attackEvent.stage = 'weaponization';
        attackEvent.technique = this.extractTechnique(message, ['phishing_email', 'malware_generation', 'exploit_creation']);
      } else if (message.includes('钓鱼邮件成功投递') || message.includes('邮件已发送至')) {
        attackEvent.stage = 'delivery';
        attackEvent.technique = this.extractTechnique(message, ['email_delivery', 'web_delivery', 'usb_delivery']);
      } else if (message.includes('攻击dmz web服务器') || message.includes('攻陷dmz web服务器') || message.includes('web应用漏洞被攻陷') || message.includes('dmz-web-01')) {
        attackEvent.stage = 'exploitation';
        attackEvent.technique = this.extractTechnique(message, ['web_exploit', 'dmz_attack', 'server_compromise']);
      } else if (message.includes('dmz web服务器安装后门') || message.includes('植入持久化木马') || message.includes('建立dmz服务器持久化访问') || message.includes('dmz-web-01植入')) {
        attackEvent.stage = 'installation';
        attackEvent.technique = this.extractTechnique(message, ['backdoor_install', 'persistence_mechanism', 'dmz_persistence']);
      } else if (message.includes('dmz服务器建立c2通信') || message.includes('远程控制dmz-web-01') || message.includes('从dmz扫描内网') || message.includes('发现内网应用服务器') || message.includes('攻陷内网应用服务器') || message.includes('横向移动通道') || message.includes('绕过内网防火墙')) {
        attackEvent.stage = 'command_and_control';
        attackEvent.technique = this.extractTechnique(message, ['c2_communication', 'lateral_movement', 'network_pivot']);
      } else if (message.includes('探测数据库网段') || message.includes('发现数据库服务器') || message.includes('突破数据库防火墙') || message.includes('访问数据库服务器') || message.includes('攻陷数据库服务器') || message.includes('窃取敏感数据') || message.includes('apt攻击目标达成')) {
        attackEvent.stage = 'actions_on_objectives';
        attackEvent.technique = this.extractTechnique(message, ['data_theft', 'database_compromise', 'data_exfiltration']);
      }

      // 解析目标节点
      attackEvent.targetNode = this.extractTargetNode(message);

      // 解析攻击源节点
      attackEvent.sourceNode = this.extractSourceNode(message);

      // 解析进度信息
      attackEvent.progress = this.extractProgress(message);

      // 解析状态
      attackEvent.status = this.extractStatus(message, log.level);

      return attackEvent;
    },

    // 提取攻击技术
    extractTechnique(message, possibleTechniques) {
      for (const technique of possibleTechniques) {
        const techniqueKeywords = {
          'port_scan': ['端口扫描', '扫描端口', 'nmap'],
          'vulnerability_scan': ['漏洞扫描', '脆弱性扫描', 'vulnerability'],
          'info_gathering': ['信息收集', '情报收集', '元数据'],
          'phishing_email': ['钓鱼邮件', '恶意邮件', 'phishing'],
          'malware_generation': ['恶意软件生成', '木马生成', 'malware'],
          'exploit_creation': ['漏洞利用创建', 'exploit'],
          'email_delivery': ['邮件投递', '邮件发送', 'email'],
          'web_delivery': ['网页投递', 'web'],
          'usb_delivery': ['USB投递', 'usb'],
          'buffer_overflow': ['缓冲区溢出', 'buffer overflow'],
          'sql_injection': ['SQL注入', 'sql injection'],
          'xss_attack': ['XSS攻击', 'cross-site scripting'],
          'backdoor_install': ['后门安装', 'backdoor'],
          'persistence_mechanism': ['持久化机制', 'persistence'],
          'privilege_escalation': ['权限提升', 'privilege escalation'],
          'c2_communication': ['C2通信', 'command and control'],
          'remote_access': ['远程访问', 'remote access'],
          'data_exfiltration': ['数据渗透', 'data exfiltration'],
          'data_theft': ['数据窃取', 'data theft'],
          'system_compromise': ['系统攻陷', 'system compromise'],
          'lateral_movement': ['横向移动', 'lateral movement']
        };

        const keywords = techniqueKeywords[technique] || [];
        if (keywords.some(keyword => message.includes(keyword))) {
          return technique;
        }
      }
      return null;
    },

    // 提取目标节点
    extractTargetNode(message) {
      const nodeKeywords = {
        'firewall': ['防火墙', 'firewall', 'border_firewall'],
        'ws-user-01': ['用户pc', 'user pc', '客户端', 'ws-user-01', '用户主机'],
        'dmz-web-01': ['dmz', 'web服务器', 'web server', 'dmz-web-01', 'dmz web服务器'],
        'dmz-dns-01': ['dns服务器', 'dns server', 'dmz-dns-01'],
        'app-server-01': ['应用服务器', 'app server', 'app-server-01', '内网应用服务器'],
        'internal-db-01': ['数据库', 'database', 'db', 'internal-db-01', '数据库服务器'],
        'internal-file-01': ['文件服务器', 'file server', 'internal-file-01']
      };

      for (const [nodeId, keywords] of Object.entries(nodeKeywords)) {
        if (keywords.some(keyword => message.includes(keyword))) {
          return nodeId;
        }
      }
      return null;
    },

    // 提取攻击源节点
    extractSourceNode(message) {
      if (message.includes('互联网') || message.includes('internet')) {
        return 'internet';
      }
      // 可以根据实际情况扩展更多源节点识别逻辑
      return 'internet'; // 默认从互联网发起攻击
    },

    // 提取进度信息
    extractProgress(message) {
      const progressMatch = message.match(/(\d+)%/);
      if (progressMatch) {
        return parseInt(progressMatch[1]);
      }

      // 根据关键词推断进度
      if (message.includes('开始') || message.includes('启动')) {
        return 10;
      } else if (message.includes('进行中') || message.includes('执行中')) {
        return 50;
      } else if (message.includes('完成') || message.includes('成功')) {
        return 100;
      } else if (message.includes('失败') || message.includes('错误')) {
        return 0;
      }

      return 25; // 默认进度
    },

    // 提取状态信息
    extractStatus(message, level) {
      if (level === 'error' || message.includes('失败') || message.includes('错误')) {
        return 'failed';
      } else if (level === 'success' || level === 'critical' || message.includes('成功') || message.includes('完成') || message.includes('攻陷') || message.includes('获得') || message.includes('建立')) {
        return 'success';
      } else if (message.includes('进行中') || message.includes('执行中') || message.includes('正在') || message.includes('开始')) {
        return 'in_progress';
      }
      return 'pending';
    },

    // 新增：更新网络节点状态
    updateNetworkNodeStatus(nodeId, status, attackLevel = 0) {
      if (this.networkNodes[nodeId]) {
        this.networkNodes[nodeId].status = status;
        this.networkNodes[nodeId].attackLevel = attackLevel;
        this.networkNodes[nodeId].lastActivity = new Date();

        console.log(`更新节点状态: ${nodeId} -> ${status} (攻击等级: ${attackLevel})`);

        // 触发网络拓扑图更新（后续实现）
        this.$emit('node-status-changed', {
          nodeId,
          status,
          attackLevel,
          timestamp: new Date()
        });
      }
    },

    // 新增：记录攻击路径
    recordAttackPath(sourceNode, targetNode, technique, status = 'active') {
      const attackPath = {
        id: `${sourceNode}-${targetNode}-${Date.now()}`,
        from: sourceNode,
        to: targetNode,
        technique,
        status,
        timestamp: new Date(),
        duration: 0
      };

      this.attackPaths.push(attackPath);

      // 限制攻击路径记录数量
      if (this.attackPaths.length > 100) {
        this.attackPaths.shift();
      }

      console.log('记录攻击路径:', attackPath);

      // 触发攻击路径可视化更新（后续实现）
      this.$emit('attack-path-added', attackPath);
    },

    // 新增：更新活跃连接
    updateActiveConnections(sourceNode, targetNode, connectionType = 'attack') {
      const connectionId = `${sourceNode}-${targetNode}`;

      // 检查是否已存在连接
      const existingIndex = this.activeConnections.findIndex(conn => conn.id === connectionId);

      if (existingIndex !== -1) {
        // 更新现有连接
        this.activeConnections[existingIndex].lastActivity = new Date();
        this.activeConnections[existingIndex].type = connectionType;
      } else {
        // 添加新连接
        this.activeConnections.push({
          id: connectionId,
          from: sourceNode,
          to: targetNode,
          type: connectionType,
          startTime: new Date(),
          lastActivity: new Date()
        });
      }

      // 清理超时的连接（5分钟无活动）
      const now = new Date();
      this.activeConnections = this.activeConnections.filter(conn => {
        return (now - conn.lastActivity) < 5 * 60 * 1000; // 5分钟
      });

      console.log('活跃连接更新:', this.activeConnections);

      // 触发连接可视化更新（后续实现）
      this.$emit('connections-updated', this.activeConnections);
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

.event-list {
  flex-grow: 1;
  overflow-y: auto;
  padding: 4px;
  max-height: 150px;
}

.log-list {
  flex-grow: 1;
  overflow-y: auto;
  overflow-x: auto;
  padding: 4px;
  max-height: 150px;
  min-width: 0;
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
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  font-size: 11px;
  min-height: 24px;
  gap: 6px;
  white-space: nowrap;
  min-width: max-content;
}

.log-time {
  color: #a9a9a9;
  margin-right: 4px;
  white-space: nowrap;
  font-size: 10px;
}

.log-level {
  min-width: 60px;
  max-width: 120px;
  text-align: center;
  padding: 2px 6px;
  border-radius: 3px;
  margin-right: 6px;
  font-weight: bold;
  text-transform: uppercase;
  font-size: 9px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
}

.log-source {
  color: #1d8cf8;
  margin-right: 6px;
  white-space: nowrap;
  font-size: 10px;
  min-width: 80px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
}

.log-message {
  flex-grow: 1;
  white-space: nowrap;
  min-width: max-content;
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

.event-list {
  flex-grow: 1;
  overflow-y: auto;
  padding: 4px;
  max-height: 150px;
}

.log-list {
  flex-grow: 1;
  overflow-y: auto;
  overflow-x: auto;
  padding: 4px;
  max-height: 150px;
  min-width: 0;
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
  padding: 4px 8px;
  border-radius: 4px;
  margin-bottom: 2px;
  display: flex;
  align-items: center;
  font-size: 11px;
  min-height: 24px;
  gap: 6px;
  white-space: nowrap;
  min-width: max-content;
}

.log-time {
  color: #a9a9a9;
  margin-right: 4px;
  white-space: nowrap;
  font-size: 10px;
}

.log-level {
  min-width: 60px;
  max-width: 120px;
  text-align: center;
  padding: 2px 6px;
  border-radius: 3px;
  margin-right: 6px;
  font-weight: bold;
  text-transform: uppercase;
  font-size: 9px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
}

.log-source {
  color: #1d8cf8;
  margin-right: 6px;
  white-space: nowrap;
  font-size: 10px;
  min-width: 80px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
}

.log-message {
  flex-grow: 1;
  white-space: nowrap;
  min-width: max-content;
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