<template>
  <div class="phishing-attack-visualization" v-if="show">
    <div class="visualization-container">
      <div class="attack-flow">
        <div class="attacker-node">
          <div class="node-icon">🕵️</div>
          <div class="node-label">攻击者</div>
        </div>
        
        <div class="attack-path">
          <div class="attack-stage" v-for="(stage, index) in currentStages" :key="index">
            <div class="stage-icon">{{ stage.icon }}</div>
            <div class="stage-name">{{ stage.name }}</div>
          </div>
          <div class="path-line" :class="{'active': animationActive}"></div>
        </div>
        
        <div class="target-node">
          <div class="node-icon">💻</div>
          <div class="node-label">{{ targetName }}</div>
        </div>
      </div>
      
      <div class="attack-details">
        <div class="attack-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{width: `${progress}%`}"></div>
          </div>
          <div class="progress-text">{{ currentStageName }}</div>
        </div>
        
        <div class="attack-result" v-if="attackCompleted">
          <div class="result-icon" :class="{'success': attackSuccess, 'failure': !attackSuccess}">
            {{ attackSuccess ? '✓' : '✗' }}
          </div>
          <div class="result-message">
            {{ attackSuccess ? '攻击成功！已获取目标凭据。' : '攻击失败！目标识别出了钓鱼邮件。' }}
          </div>
          <button class="close-btn" @click="$emit('close')">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SimplePhishingVisualization',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    attacker: {
      type: Object,
      default: () => ({})
    },
    target: {
      type: Object,
      default: () => ({})
    },
    attackType: {
      type: String,
      default: 'phishing'
    }
  },
  
  data() {
    return {
      stages: [
        { name: '侦察', icon: '🔍', description: '收集目标信息' },
        { name: '制作钓鱼邮件', icon: '✉️', description: '根据目标信息制作定制化钓鱼邮件' },
        { name: '发送邮件', icon: '📤', description: '将钓鱼邮件发送给目标' },
        { name: '目标接收', icon: '📥', description: '目标接收并查看邮件' },
        { name: '点击链接', icon: '🖱️', description: '目标点击邮件中的恶意链接' },
        { name: '凭据窃取', icon: '🔑', description: '获取目标的登录凭据' },
        { name: '攻击完成', icon: '🏁', description: '攻击流程结束' }
      ],
      currentStageIndex: 0,
      animationActive: false,
      attackCompleted: false,
      attackSuccess: false,
      progress: 0,
      animationTimer: null
    }
  },
  
  computed: {
    targetName() {
      return this.target?.deviceData?.name || '目标'
    },
    
    currentStages() {
      return this.stages.slice(0, this.currentStageIndex + 1)
    },
    
    currentStageName() {
      return this.currentStageIndex < this.stages.length 
        ? this.stages[this.currentStageIndex].name 
        : '攻击完成'
    }
  },
  
  watch: {
    show(newVal) {
      if (newVal) {
        this.resetAnimation()
        this.startAnimation()
      } else {
        this.stopAnimation()
      }
    }
  },
  
  methods: {
    resetAnimation() {
      this.currentStageIndex = 0
      this.animationActive = false
      this.attackCompleted = false
      this.progress = 0
      this.stopAnimation()
    },
    
    startAnimation() {
      this.animationActive = true
      this.progress = 0
      
      // 模拟攻击进度
      this.animationTimer = setInterval(() => {
        this.progress += 2
        
        // 阶段切换
        if (this.progress >= 100) {
          this.currentStageIndex++
          this.progress = 0
          
          // 攻击完成
          if (this.currentStageIndex >= this.stages.length) {
            this.completeAttack()
          }
        }
      }, 100)
    },
    
    stopAnimation() {
      if (this.animationTimer) {
        clearInterval(this.animationTimer)
        this.animationTimer = null
      }
    },
    
    completeAttack() {
      this.stopAnimation()
      this.attackCompleted = true
      
      // 随机决定攻击是否成功，但偏向成功
      this.attackSuccess = Math.random() > 0.3
      
      // 通知父组件攻击结果
      this.$emit('attack-result', {
        success: this.attackSuccess,
        target: this.target,
        attacker: this.attacker,
        attackType: this.attackType
      })
    }
  },
  
  beforeUnmount() {
    this.stopAnimation()
  }
}
</script>

<style scoped>
.phishing-attack-visualization {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}

.visualization-container {
  background-color: #1e1e2f;
  border-radius: 8px;
  width: 800px;
  max-width: 90%;
  height: 500px;
  max-height: 90%;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.attack-flow {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.attacker-node, .target-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100px;
}

.node-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #27293d;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 30px;
  margin-bottom: 10px;
}

.node-label {
  color: white;
  font-size: 14px;
}

.attack-path {
  flex: 1;
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.path-line {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 3px;
  background-color: #3498db;
  transform: translateY(-50%);
}

.path-line.active {
  background: linear-gradient(90deg, #3498db 50%, transparent 50%);
  background-size: 20px 3px;
  animation: movePathLine 1s linear infinite;
}

@keyframes movePathLine {
  from { background-position: 0 0; }
  to { background-position: 20px 0; }
}

.attack-stage {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.stage-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #27293d;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 20px;
  margin-bottom: 5px;
}

.stage-name {
  color: white;
  font-size: 12px;
  white-space: nowrap;
}

.attack-details {
  height: 100px;
}

.attack-progress {
  margin-bottom: 20px;
}

.progress-bar {
  height: 10px;
  background-color: #27293d;
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background-color: #3498db;
  transition: width 0.1s linear;
}

.progress-text {
  color: white;
  font-size: 14px;
  text-align: center;
}

.attack-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: fadeIn 0.5s ease-in-out;
}

.result-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 30px;
  margin-bottom: 10px;
}

.result-icon.success {
  background-color: #2ecc71;
}

.result-icon.failure {
  background-color: #e74c3c;
}

.result-message {
  color: white;
  font-size: 16px;
  text-align: center;
  margin-bottom: 20px;
}

.close-btn {
  padding: 8px 16px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.close-btn:hover {
  background-color: #2980b9;
}
</style>