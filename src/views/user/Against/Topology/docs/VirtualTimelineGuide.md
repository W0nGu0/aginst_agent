# 🕒 虚拟时间轴系统指南

## 📋 概述

虚拟时间轴系统是为APT攻击演练设计的时间模拟组件，用于模拟真实APT攻击的持续性特征。由于真实APT攻击可能持续数月甚至数年，而演练时间通常只有几分钟，因此需要通过时间加速来模拟真实的时间流逝。

## 🎯 核心功能

### 1. 时间加速模拟
- **多倍速选择**：1x (真实时间) 到 10080x (1分钟=1周)
- **虚拟时间显示**：显示模拟的攻击时间线
- **实际时间对比**：同时显示真实演练时间
- **持续时间统计**：计算攻击的虚拟持续时间

### 2. APT攻击阶段追踪
- **7个标准阶段**：侦察 → 武器化 → 投递 → 利用 → 安装 → 命令控制 → 行动
- **阶段进度显示**：可视化当前攻击进展
- **阶段时间估算**：显示每个阶段的预期持续时间
- **自动阶段切换**：基于攻击事件自动更新当前阶段

### 3. 攻击事件记录
- **实时事件流**：记录所有攻击活动
- **事件分类**：info、warning、success、error
- **详细信息**：包含技术、源/目标节点、状态等
- **时间戳记录**：精确记录事件发生的虚拟时间

### 4. 统计分析
- **攻击阶段完成度**：显示已完成的攻击阶段数
- **检测延迟**：模拟安全系统的检测时间
- **驻留时间**：攻击者在系统中的停留时间
- **影响范围**：被攻陷的资产数量

## 🔧 技术实现

### 组件结构
```
VirtualTimeline.vue
├── 时间轴头部 (控制面板)
├── 当前时间显示 (虚拟/实际/持续时间)
├── 时间轴进度条 (APT阶段标记)
├── 攻击事件时间线 (事件列表)
└── 时间轴统计 (关键指标)
```

### 核心数据结构
```javascript
// APT攻击阶段定义
aptPhases: [
  {
    name: '侦察',
    icon: '🔍',
    position: 5,
    expectedTime: '数天-数周',
    description: '收集目标信息，识别攻击面'
  },
  // ... 其他阶段
]

// 攻击事件结构
attackEvent: {
  id: 'unique_id',
  virtualTime: Date,
  realTime: Date,
  phase: '侦察',
  type: 'info',
  message: '攻击者开始网络扫描',
  details: {
    '技术': 'port_scan',
    '目标节点': 'firewall',
    '状态': 'in_progress'
  },
  duration: 'elapsed_time'
}
```

## 🚀 使用方法

### 1. 基本集成
```vue
<template>
  <VirtualTimeline 
    ref="virtualTimelineRef"
    :auto-start="false"
    @timeline-started="onTimelineStarted"
    @timeline-paused="onTimelinePaused"
    @timeline-reset="onTimelineReset"
    @phase-changed="onPhaseChanged"
    @speed-changed="onSpeedChanged"
  />
</template>

<script>
import VirtualTimeline from './components/VirtualTimeline.vue'

export default {
  components: { VirtualTimeline },
  methods: {
    onTimelineStarted() {
      console.log('时间轴已启动')
    },
    // ... 其他事件处理
  }
}
</script>
```

### 2. 添加攻击事件
```javascript
// 方法1：通过组件引用
this.$refs.virtualTimelineRef.addEvent({
  phase: '侦察',
  type: 'info',
  message: '攻击者开始网络扫描',
  details: {
    '技术': 'port_scan',
    '目标': 'firewall'
  }
})

// 方法2：通过自定义事件
const event = new CustomEvent('attack-event', {
  detail: {
    phase: '侦察',
    type: 'info',
    message: '攻击者开始网络扫描',
    details: { /* ... */ }
  }
})
document.dispatchEvent(event)
```

### 3. 更新攻击阶段
```javascript
// 方法1：通过组件引用
this.$refs.virtualTimelineRef.setPhase('武器化')

// 方法2：通过自定义事件
const event = new CustomEvent('phase-change', {
  detail: { phase: '武器化' }
})
document.dispatchEvent(event)
```

## 📊 与攻击系统集成

### 1. WebSocket消息处理
```javascript
// 在TopologyView.vue中集成
if (message.attack_info) {
  // 添加到虚拟时间轴
  if (virtualTimelineRef.value) {
    virtualTimelineRef.value.addEvent({
      phase: getPhaseDisplayName(message.attack_info.stage),
      type: getEventType(message.level),
      message: message.message,
      details: {
        '技术': message.attack_info.technique,
        '源节点': message.attack_info.source_node,
        '目标节点': message.attack_info.target_node,
        '状态': message.attack_info.status,
        '进度': message.attack_info.progress + '%'
      }
    })
  }
}
```

### 2. 攻击开始时自动启动
```javascript
// 攻击成功启动时
if (result.success) {
  // 启动虚拟时间轴
  if (virtualTimelineRef.value) {
    virtualTimelineRef.value.startTimeline()
    console.log('🕒 APT攻击开始，自动启动虚拟时间轴')
  }
}
```

## 🎨 样式定制

### 主题色彩
- **主色调**：深蓝渐变背景 (#1a1a2e → #16213e)
- **强调色**：青色 (#64ffda) 用于重要信息
- **状态色**：
  - 成功：绿色 (#4caf50)
  - 警告：橙色 (#ff9800)
  - 错误：红色 (#f44336)
  - 信息：蓝色 (#2196f3)

### 响应式设计
- **桌面端**：完整功能布局
- **平板端**：调整控制面板布局
- **移动端**：垂直堆叠，简化显示

## 🧪 测试验证

### 测试页面
使用 `VirtualTimelineTest.html` 进行功能测试：

1. **时间轴控制测试**
   - 启动/暂停/重置功能
   - 时间倍速调整
   - 时间显示准确性

2. **攻击事件模拟**
   - 各阶段事件添加
   - 事件详情显示
   - 阶段自动切换

3. **统计功能验证**
   - 进度计算准确性
   - 资产统计更新
   - 时间统计正确性

### 性能考虑
- **事件数量限制**：最多保留200个事件记录
- **动画优化**：使用CSS3硬件加速
- **内存管理**：定期清理过期事件

## 🔮 未来扩展

### 计划功能
1. **时间轴回放**：支持攻击过程回放
2. **事件过滤**：按阶段、类型过滤事件
3. **导出功能**：导出时间轴报告
4. **多场景支持**：支持不同APT场景的时间轴模板
5. **AI分析**：基于时间轴数据的智能分析

### 集成扩展
1. **防御时间轴**：集成防御agent的响应时间轴
2. **对抗可视化**：攻防双方的时间轴对比
3. **威胁情报**：集成外部威胁情报时间线
4. **合规报告**：生成符合安全标准的时间轴报告

## 📝 最佳实践

### 1. 时间倍速选择
- **演示场景**：使用300x-1440x倍速
- **培训场景**：使用60x-300x倍速
- **详细分析**：使用1x-60x倍速

### 2. 事件记录
- **关键事件**：必须记录的重要攻击步骤
- **详细信息**：提供足够的技术细节
- **时间准确性**：确保事件时间戳的准确性

### 3. 用户体验
- **渐进式披露**：根据用户需求显示详细信息
- **实时反馈**：及时响应用户操作
- **错误处理**：优雅处理异常情况

---

**注意**：虚拟时间轴系统是APT攻击演练的核心组件，正确使用能够显著提升演练的真实感和教育价值。
