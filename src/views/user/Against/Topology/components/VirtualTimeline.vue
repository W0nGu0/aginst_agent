<template>
  <div class="virtual-timeline">
    <!-- 时间轴头部 -->
    <div class="timeline-header">
      <div class="timeline-title">
        <h3>🕒 APT攻击时间轴</h3>
        <div class="timeline-subtitle">模拟真实攻击持续时间</div>
      </div>
      <div class="timeline-controls">
        <button @click="toggleTimeline" :class="['control-btn', isRunning ? 'pause' : 'play']">
          {{ isRunning ? '⏸️ 暂停攻击' : '🎯 开始攻击' }}
        </button>
        <button @click="resetTimeline" class="control-btn reset">
          🔄 重置
        </button>
        <div class="speed-control">
          <label>时间倍速:</label>
          <select v-model="timeMultiplier" @change="updateTimeSpeed">
            <option value="1">1x (真实)</option>
            <option value="60">60x (1分钟=1小时)</option>
            <option value="300">300x (1分钟=5小时)</option>
            <option value="1440">1440x (1分钟=1天)</option>
            <option value="10080">10080x (1分钟=1周)</option>
            <option value="50400">50400x (1分钟=5周)</option>
            <option value="100800">100800x (1分钟=10周)</option>
          </select>
        </div>
      </div>
    </div>

    <!-- 当前时间显示 -->
    <div class="current-time">
      <div class="virtual-time">
        <span class="time-label">虚拟时间:</span>
        <span class="time-value">{{ formatVirtualTime(currentVirtualTime) }}</span>
      </div>
      <div class="real-time">
        <span class="time-label">实际时间:</span>
        <span class="time-value">{{ formatRealTime(currentRealTime) }}</span>
      </div>
      <div class="elapsed-time">
        <span class="time-label">攻击持续:</span>
        <span class="time-value">{{ isAttackStarted ? formatDuration(elapsedVirtualTime) : '未开始' }}</span>
      </div>
    </div>

    <!-- 时间轴进度条 -->
    <div class="timeline-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
        <div class="progress-markers">
          <div 
            v-for="phase in aptPhases" 
            :key="phase.name"
            class="phase-marker"
            :class="{ active: currentPhase === phase.name, completed: isPhaseCompleted(phase.name) }"
            :style="{ left: phase.position + '%' }"
            :title="phase.description"
          >
            <div class="marker-icon">{{ phase.icon }}</div>
            <div class="marker-label">{{ phase.name }}</div>
            <div class="marker-time">{{ phase.expectedTime }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 攻击事件时间线 -->
    <div class="events-timeline">
      <div class="events-header">
        <h4>🎯 攻击事件记录</h4>
        <div class="events-stats">
          总事件: {{ attackEvents.length }} | 活跃阶段: {{ currentPhase || '准备中' }}
        </div>
      </div>
      <div class="events-list" ref="eventsList">
        <div 
          v-for="event in attackEvents" 
          :key="event.id"
          class="event-item"
          :class="['event-' + event.type, { 'event-current': event.id === currentEventId }]"
        >
          <div class="event-time">{{ formatVirtualTime(event.virtualTime) }}</div>
          <div class="event-content">
            <div class="event-phase" v-if="event.phase">{{ event.phase }}</div>
            <div class="event-message">{{ event.message }}</div>
            <div class="event-details" v-if="event.details">
              <span class="detail-item" v-for="(value, key) in event.details" :key="key">
                {{ key }}: {{ value }}
              </span>
            </div>
          </div>
          <div class="event-duration">{{ formatDuration(event.duration) }}</div>
        </div>
      </div>
    </div>

    <!-- 时间轴统计 -->
    <div class="timeline-stats">
      <div class="stat-item">
        <div class="stat-label">攻击阶段</div>
        <div class="stat-value">{{ completedPhases }}/{{ aptPhases.length }}</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">检测延迟</div>
        <div class="stat-value">{{ detectionDelay }}</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">驻留时间</div>
        <div class="stat-value">{{ dwellTime }}</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">影响范围</div>
        <div class="stat-value">{{ compromisedAssets }} 资产</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VirtualTimeline',
  props: {
    startTime: {
      type: Date,
      default: () => new Date()
    },
    autoStart: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      // 时间控制
      isRunning: false,
      isAttackStarted: false, // 新增：标记攻击是否已开始
      timeMultiplier: 300, // 默认300倍速 (1分钟=5小时)
      startVirtualTime: new Date(),
      startRealTime: new Date(),
      attackStartTime: null, // 新增：攻击开始时间
      currentVirtualTime: new Date(),
      currentRealTime: new Date(),
      timeInterval: null,
      
      // 攻击阶段定义
      aptPhases: [
        {
          name: '侦察',
          icon: '🔍',
          position: 5,
          expectedTime: '数天-数周',
          description: '收集目标信息，识别攻击面'
        },
        {
          name: '武器化',
          icon: '⚔️',
          position: 15,
          expectedTime: '数小时-数天',
          description: '制作恶意载荷和攻击工具'
        },
        {
          name: '投递',
          icon: '📧',
          position: 25,
          expectedTime: '数分钟-数小时',
          description: '将恶意载荷投递到目标'
        },
        {
          name: '利用',
          icon: '💥',
          position: 35,
          expectedTime: '数秒-数分钟',
          description: '利用漏洞获得初始访问权限'
        },
        {
          name: '安装',
          icon: '🔧',
          position: 45,
          expectedTime: '数分钟-数小时',
          description: '安装恶意软件和后门'
        },
        {
          name: '命令控制',
          icon: '🎮',
          position: 60,
          expectedTime: '持续数月',
          description: '建立远程控制通道'
        },
        {
          name: '行动',
          icon: '🎯',
          position: 85,
          expectedTime: '数天-数月',
          description: '执行最终攻击目标'
        }
      ],
      
      // 当前状态
      currentPhase: null,
      currentEventId: null,
      attackEvents: [],
      completedPhases: 0,
      compromisedAssets: 0,
      
      // 统计数据
      detectionDelay: '未检测',
      dwellTime: '0天'
    }
  },
  computed: {
    elapsedVirtualTime() {
      // 只有在攻击开始后才计算持续时间
      if (!this.isAttackStarted || !this.attackStartTime) {
        return 0
      }
      return this.currentVirtualTime - this.attackStartTime
    },
    elapsedRealTime() {
      return this.currentRealTime - this.startRealTime
    },
    progressPercentage() {
      // 基于已完成的攻击阶段计算进度
      return Math.min((this.completedPhases / this.aptPhases.length) * 100, 100)
    }
  },
  mounted() {
    this.initializeTimeline()
    if (this.autoStart) {
      this.startTimeline()
    }
    
    // 监听攻击事件
    document.addEventListener('attack-event', this.handleAttackEvent)
    document.addEventListener('phase-change', this.handlePhaseChange)
    document.addEventListener('key-event', this.handleKeyEvent)
  },
  beforeUnmount() {
    this.stopTimeline()
    document.removeEventListener('attack-event', this.handleAttackEvent)
    document.removeEventListener('phase-change', this.handlePhaseChange)
    document.removeEventListener('key-event', this.handleKeyEvent)
  },
  methods: {
    initializeTimeline() {
      const now = new Date()
      this.startVirtualTime = new Date(now)
      this.startRealTime = new Date(now)
      this.currentVirtualTime = new Date(now)
      this.currentRealTime = new Date(now)
      // 确保攻击状态被重置
      this.isAttackStarted = false
      this.attackStartTime = null

      console.log('🕒 虚拟时间轴已初始化')
    },
    
    startTimeline() {
      if (this.isRunning) return

      this.isRunning = true
      // 如果是第一次启动，标记为攻击开始
      if (!this.isAttackStarted) {
        this.isAttackStarted = true
        this.attackStartTime = new Date(this.currentVirtualTime)
        console.log('🎯 攻击开始！')
      }

      this.timeInterval = setInterval(() => {
        this.updateTime()
      }, 1000) // 每秒更新一次

      console.log('▶️ 虚拟时间轴已启动')
      this.$emit('timeline-started')
    },
    
    stopTimeline() {
      if (!this.isRunning) return
      
      this.isRunning = false
      if (this.timeInterval) {
        clearInterval(this.timeInterval)
        this.timeInterval = null
      }
      
      console.log('⏸️ 虚拟时间轴已暂停')
      this.$emit('timeline-paused')
    },
    
    resetTimeline() {
      this.stopTimeline()
      this.initializeTimeline()
      this.attackEvents = []
      this.currentPhase = null
      this.currentEventId = null
      this.completedPhases = 0
      this.compromisedAssets = 0
      this.detectionDelay = '未检测'
      this.dwellTime = '0天'
      // 重置攻击状态
      this.isAttackStarted = false
      this.attackStartTime = null

      console.log('🔄 虚拟时间轴已重置')
      this.$emit('timeline-reset')
    },
    
    toggleTimeline() {
      if (this.isRunning) {
        this.stopTimeline()
      } else {
        this.startTimeline()
      }
    },
    
    updateTime() {
      const now = new Date()
      this.currentRealTime = new Date(now)
      
      // 计算虚拟时间（加速）
      const realElapsed = now - this.startRealTime
      const virtualElapsed = realElapsed * this.timeMultiplier
      this.currentVirtualTime = new Date(this.startVirtualTime.getTime() + virtualElapsed)
      
      // 更新驻留时间
      this.updateDwellTime()
    },
    
    updateTimeSpeed() {
      console.log(`⚡ 时间倍速已调整为: ${this.timeMultiplier}x`)
      this.$emit('speed-changed', this.timeMultiplier)
    },
    
    updateDwellTime() {
      const days = Math.floor(this.elapsedVirtualTime / (1000 * 60 * 60 * 24))
      const hours = Math.floor((this.elapsedVirtualTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
      
      if (days > 0) {
        this.dwellTime = `${days}天${hours}小时`
      } else {
        this.dwellTime = `${hours}小时`
      }
    },
    
    handleAttackEvent(event) {
      const attackEvent = {
        id: Date.now() + Math.random(),
        virtualTime: new Date(this.currentVirtualTime),
        realTime: new Date(this.currentRealTime),
        phase: event.detail.phase || this.currentPhase || this.inferPhaseFromMessage(event.detail.message || ''),
        type: event.detail.type || 'info',
        message: event.detail.message || '',
        details: event.detail.details || null,
        duration: this.elapsedVirtualTime
      }

      this.attackEvents.push(attackEvent)
      this.currentEventId = attackEvent.id

      // 智能更新当前阶段
      if (attackEvent.phase !== '未知' && attackEvent.phase !== this.currentPhase) {
        this.updateCurrentPhase(attackEvent.phase)
      }

      // 检查是否是攻击完成事件
      const message = attackEvent.message || ''
      if (message.includes('攻击任务已完成') ||
          message.includes('攻击完成') ||
          message.includes('任务完成') ||
          message.includes('COMPLETE') ||
          attackEvent.type === 'complete') {
        console.log('🎯 检测到攻击完成，自动停止时间轴')
        this.stopTimeline()
        this.$emit('attack-completed', attackEvent)
      }

      // 自动滚动到最新事件
      this.$nextTick(() => {
        const eventsList = this.$refs.eventsList
        if (eventsList) {
          eventsList.scrollTop = eventsList.scrollHeight
        }
      })

      console.log('🎯 新攻击事件:', attackEvent)
    },
    
    handlePhaseChange(event) {
      const newPhase = event.detail.phase
      if (newPhase !== this.currentPhase) {
        this.currentPhase = newPhase
        
        // 更新完成阶段数
        const phaseIndex = this.aptPhases.findIndex(p => p.name === newPhase)
        if (phaseIndex >= 0) {
          this.completedPhases = phaseIndex + 1
        }
        
        console.log('📊 攻击阶段变更:', newPhase)
        this.$emit('phase-changed', newPhase)
      }
    },

    handleKeyEvent(event) {
      const keyEvent = event.detail
      const message = keyEvent.message || keyEvent.content || ''

      console.log('🔑 关键事件:', message)

      // 检查是否是攻击完成的关键事件
      if (message.includes('攻击任务已完成') ||
          message.includes('攻击完成') ||
          message.includes('任务完成') ||
          message.includes('COMPLETE') ||
          keyEvent.type === 'complete' ||
          keyEvent.status === 'completed') {
        console.log('🎯 检测到攻击完成关键事件，自动停止时间轴')
        this.stopTimeline()
        this.$emit('attack-completed', keyEvent)

        // 添加完成事件到攻击事件列表
        const completionEvent = {
          id: Date.now() + Math.random(),
          virtualTime: new Date(this.currentVirtualTime),
          realTime: new Date(this.currentRealTime),
          phase: '完成',
          type: 'success',
          message: '🎯 攻击任务已完成',
          details: keyEvent.details || null,
          duration: this.elapsedVirtualTime
        }
        this.attackEvents.push(completionEvent)
        this.currentEventId = completionEvent.id
      }
    },

    isPhaseCompleted(phaseName) {
      const phaseIndex = this.aptPhases.findIndex(p => p.name === phaseName)
      return phaseIndex < this.completedPhases
    },

    // 根据消息内容智能推断攻击阶段
    inferPhaseFromMessage(message) {
      if (!message) return null // 返回null而不是'未知'

      const msg = message.toLowerCase()

      // 侦察阶段关键词
      if (msg.includes('扫描') || msg.includes('侦察') || msg.includes('收集') ||
          msg.includes('探测') || msg.includes('枚举') || msg.includes('信息收集') ||
          msg.includes('scan') || msg.includes('reconnaissance') || msg.includes('discovery') ||
          msg.includes('端口') || msg.includes('服务') || msg.includes('版本') ||
          msg.includes('目标分析') || msg.includes('网络拓扑')) {
        return '侦察'
      }

      // 武器化阶段关键词
      if (msg.includes('生成') || msg.includes('制作') || msg.includes('构造') ||
          msg.includes('钓鱼') || msg.includes('载荷') || msg.includes('恶意软件') ||
          msg.includes('payload') || msg.includes('malware') || msg.includes('weaponization') ||
          msg.includes('木马') || msg.includes('后门') || msg.includes('病毒')) {
        return '武器化'
      }

      // 投递阶段关键词
      if (msg.includes('发送') || msg.includes('投递') || msg.includes('邮件') ||
          msg.includes('附件') || msg.includes('链接') || msg.includes('下载') ||
          msg.includes('delivery') || msg.includes('email') || msg.includes('phishing') ||
          msg.includes('钓鱼邮件') || msg.includes('社会工程')) {
        return '投递'
      }

      // 利用阶段关键词
      if (msg.includes('利用') || msg.includes('漏洞') || msg.includes('exploit') ||
          msg.includes('vulnerability') || msg.includes('攻击') || msg.includes('入侵') ||
          msg.includes('渗透') || msg.includes('突破') || msg.includes('权限') ||
          msg.includes('执行') || msg.includes('代码') || msg.includes('命令') ||
          msg.includes('command executed') || msg.includes('successfully')) {
        return '利用'
      }

      // 安装阶段关键词
      if (msg.includes('安装') || msg.includes('部署') || msg.includes('植入') ||
          msg.includes('持久化') || msg.includes('驻留') || msg.includes('installation') ||
          msg.includes('persistence') || msg.includes('implant') || msg.includes('backdoor') ||
          msg.includes('启动项') || msg.includes('服务') || msg.includes('计划任务')) {
        return '安装'
      }

      // 命令控制阶段关键词
      if (msg.includes('连接') || msg.includes('通信') || msg.includes('控制') ||
          msg.includes('c2') || msg.includes('c&c') || msg.includes('command') ||
          msg.includes('control') || msg.includes('远程') || msg.includes('回连') ||
          msg.includes('心跳') || msg.includes('指令') || msg.includes('会话') ||
          msg.includes('智能体') || msg.includes('agent')) {
        return '命令控制'
      }

      // 行动阶段关键词
      if (msg.includes('窃取') || msg.includes('泄露') || msg.includes('下载') ||
          msg.includes('上传') || msg.includes('数据') || msg.includes('文件') ||
          msg.includes('exfiltration') || msg.includes('steal') || msg.includes('download') ||
          msg.includes('横向移动') || msg.includes('提权') || msg.includes('目标达成') ||
          msg.includes('任务完成') || msg.includes('攻击完成')) {
        return '行动'
      }

      // 如果都不匹配，返回null（不显示阶段）
      return null
    },

    // 更新当前攻击阶段
    updateCurrentPhase(newPhase) {
      if (newPhase && newPhase !== this.currentPhase) {
        const phaseIndex = this.aptPhases.findIndex(p => p.name === newPhase)
        if (phaseIndex >= 0) {
          // 只允许阶段向前推进，不允许倒退
          const currentIndex = this.aptPhases.findIndex(p => p.name === this.currentPhase)
          if (currentIndex < 0 || phaseIndex >= currentIndex) {
            this.currentPhase = newPhase
            this.completedPhases = Math.max(this.completedPhases, phaseIndex + 1)

            console.log(`📊 智能更新攻击阶段: ${newPhase} (${phaseIndex + 1}/${this.aptPhases.length})`)
            this.$emit('phase-changed', newPhase)
          }
        }
      }
    },

    formatVirtualTime(time) {
      return time.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },
    
    formatRealTime(time) {
      return time.toLocaleTimeString('zh-CN')
    },
    
    formatDuration(milliseconds) {
      const days = Math.floor(milliseconds / (1000 * 60 * 60 * 24))
      const hours = Math.floor((milliseconds % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
      const minutes = Math.floor((milliseconds % (1000 * 60 * 60)) / (1000 * 60))
      
      if (days > 0) {
        return `${days}天${hours}小时`
      } else if (hours > 0) {
        return `${hours}小时${minutes}分钟`
      } else {
        return `${minutes}分钟`
      }
    },
    
    // 公共方法供外部调用
    addEvent(eventData) {
      const event = new CustomEvent('attack-event', { detail: eventData })
      document.dispatchEvent(event)
    },
    
    setPhase(phase) {
      const event = new CustomEvent('phase-change', { detail: { phase } })
      document.dispatchEvent(event)
    },
    
    updateCompromisedAssets(count) {
      this.compromisedAssets = count
    },

    // 测试阶段推断功能
    testPhaseInference() {
      const testMessages = [
        '开始扫描目标网络',
        '生成钓鱼邮件载荷',
        '发送钓鱼邮件到目标',
        '利用漏洞获取权限',
        '安装后门程序',
        '建立C2连接',
        '窃取敏感数据'
      ]

      console.log('🧪 测试阶段推断功能:')
      testMessages.forEach(msg => {
        const phase = this.inferPhaseFromMessage(msg)
        console.log(`  "${msg}" -> ${phase}`)
      })
    },
    
    setDetectionDelay(delay) {
      this.detectionDelay = delay
    }
  }
}
</script>

<style scoped>
.virtual-timeline {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  padding: 24px;
  color: #ffffff;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(100, 255, 218, 0.2);
  margin: 16px 0;
  backdrop-filter: blur(10px);
}

/* 时间轴头部 */
.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(100, 255, 218, 0.2);
  gap: 20px;
  flex-wrap: wrap;
}

.timeline-title h3 {
  margin: 0;
  color: #64ffda;
  font-size: 1.4em;
  font-weight: 600;
}

.timeline-subtitle {
  color: #b0bec5;
  font-size: 0.9em;
  margin-top: 4px;
}

.timeline-controls {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  min-width: 0;
  flex-shrink: 0;
}

.control-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 500;
  transition: all 0.3s ease;
}

.control-btn.play {
  background: linear-gradient(135deg, #4caf50, #45a049);
  color: white;
}

.control-btn.pause {
  background: linear-gradient(135deg, #ff9800, #f57c00);
  color: white;
}

.control-btn.reset {
  background: linear-gradient(135deg, #607d8b, #546e7a);
  color: white;
}

.control-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #b0bec5;
  font-size: 0.9em;
}

.speed-control select {
  background: rgba(30, 41, 59, 0.9);
  border: 1px solid rgba(100, 255, 218, 0.3);
  border-radius: 6px;
  color: #ffffff;
  padding: 6px 12px;
  font-size: 0.9em;
  min-width: 160px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.speed-control select:hover {
  border-color: rgba(100, 255, 218, 0.6);
  background: rgba(30, 41, 59, 1);
  box-shadow: 0 0 10px rgba(100, 255, 218, 0.2);
}

.speed-control select:focus {
  outline: none;
  border-color: #64ffda;
  box-shadow: 0 0 15px rgba(100, 255, 218, 0.4);
}

.speed-control select option {
  background: #1e293b;
  color: #ffffff;
  padding: 8px;
}

/* 当前时间显示 */
.current-time {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 28px;
  padding: 24px;
  background: rgba(100, 255, 218, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(100, 255, 218, 0.2);
  backdrop-filter: blur(5px);
}

.virtual-time, .real-time, .elapsed-time {
  text-align: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.time-label {
  display: block;
  color: #b0bec5;
  font-size: 0.85em;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.time-value {
  display: block;
  color: #64ffda;
  font-size: 1.2em;
  font-weight: 600;
  font-family: 'Courier New', monospace;
  line-height: 1.3;
  word-break: break-all;
}

/* 时间轴进度条 */
.timeline-progress {
  margin-bottom: 60px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.progress-bar {
  position: relative;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: visible;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50, #64ffda);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.progress-markers {
  position: relative;
  height: 120px;
  margin-top: 20px;
  overflow: visible;
}

.phase-marker {
  position: absolute;
  transform: translateX(-50%);
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 80px;
  max-width: 120px;
  z-index: 1;
}

.marker-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  margin: 0 auto 4px;
  transition: all 0.3s ease;
}

.phase-marker.active .marker-icon {
  background: linear-gradient(135deg, #64ffda, #4caf50);
  border-color: #64ffda;
  box-shadow: 0 0 12px rgba(100, 255, 218, 0.5);
}

.phase-marker.completed .marker-icon {
  background: linear-gradient(135deg, #4caf50, #45a049);
  border-color: #4caf50;
}

.marker-label {
  font-size: 0.75em;
  color: #b0bec5;
  margin-bottom: 4px;
  font-weight: 600;
  white-space: nowrap;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
}

.marker-time {
  font-size: 0.65em;
  color: #78909c;
  white-space: nowrap;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  line-height: 1.2;
  margin-top: 2px;
}

.phase-marker:hover {
  transform: translateX(-50%) translateY(-2px);
}

/* 攻击事件时间线 */
.events-timeline {
  margin-bottom: 24px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.events-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.events-header h4 {
  margin: 0;
  color: #64ffda;
  font-size: 1.1em;
}

.events-stats {
  color: #b0bec5;
  font-size: 0.8em;
}

.events-list {
  max-height: 320px;
  overflow-y: auto;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.event-item {
  display: grid;
  grid-template-columns: 140px 1fr 90px;
  gap: 20px;
  padding: 16px 20px;
  margin-bottom: 12px;
  border-radius: 8px;
  border-left: 4px solid transparent;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  min-height: 60px;
  align-items: start;
}

.event-item:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.event-item.event-current {
  background: rgba(100, 255, 218, 0.15);
  border-left-color: #64ffda;
  box-shadow: 0 0 20px rgba(100, 255, 218, 0.3);
}

.event-info { border-left-color: #2196f3; }
.event-warning { border-left-color: #ff9800; }
.event-success { border-left-color: #4caf50; }
.event-error { border-left-color: #f44336; }

.event-time {
  font-family: 'Courier New', monospace;
  font-size: 0.8em;
  color: #b0bec5;
  font-weight: 600;
  white-space: nowrap;
  padding-top: 2px;
  line-height: 1.3;
}

.event-content {
  min-width: 0;
  overflow: hidden;
  padding-top: 2px;
}

.event-phase {
  font-size: 0.7em;
  color: #64ffda;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 4px;
  font-weight: 700;
  line-height: 1.2;
}

.event-message {
  font-size: 0.85em;
  color: #ffffff;
  margin-bottom: 6px;
  line-height: 1.4;
  word-wrap: break-word;
}

.event-details {
  font-size: 0.7em;
  color: #78909c;
}

.detail-item {
  margin-right: 12px;
}

.event-duration {
  font-size: 0.75em;
  color: #b0bec5;
  text-align: right;
  padding-top: 2px;
  line-height: 1.3;
  white-space: nowrap;
}

/* 时间轴统计 */
.timeline-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  padding: 20px 0;
  margin-top: 16px;
  border-top: 2px solid rgba(100, 255, 218, 0.2);
}

.stat-item {
  text-align: center;
  padding: 16px 12px;
  background: rgba(100, 255, 218, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(100, 255, 218, 0.2);
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.stat-item:hover {
  background: rgba(100, 255, 218, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(100, 255, 218, 0.2);
}

.stat-label {
  font-size: 0.8em;
  color: #b0bec5;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 1.2em;
  color: #64ffda;
  font-weight: 600;
}

/* 滚动条样式 */
.events-list::-webkit-scrollbar {
  width: 6px;
}

.events-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.events-list::-webkit-scrollbar-thumb {
  background: rgba(100, 255, 218, 0.3);
  border-radius: 3px;
}

.events-list::-webkit-scrollbar-thumb:hover {
  background: rgba(100, 255, 218, 0.5);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .timeline-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .timeline-controls {
    justify-content: center;
  }

  .current-time {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
}

@media (max-width: 768px) {
  .virtual-timeline {
    padding: 16px;
    margin: 8px 0;
  }

  .timeline-header {
    gap: 12px;
  }

  .current-time {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .event-item {
    grid-template-columns: 1fr;
    gap: 8px;
    text-align: left;
  }

  .event-duration {
    text-align: left;
  }

  .timeline-stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .virtual-timeline {
    padding: 12px;
  }

  .timeline-controls {
    flex-direction: column;
    gap: 8px;
  }

  .timeline-stats {
    grid-template-columns: 1fr;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .timeline-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .timeline-controls {
    justify-content: center;
  }

  .current-time {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .timeline-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .event-item {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}
</style>
