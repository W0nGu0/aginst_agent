# 🎬 基于日志的攻击动画系统

## 📋 系统概述

新的动画系统完全基于后端发送的日志内容，实现了日志与动画的完全同步。系统会自动解析后端日志中的攻击信息，并触发对应的可视化动画。

## 🔄 工作流程

```
后端日志 → EventMonitor解析 → 触发动画事件 → TopologyView处理 → Fabric.js动画
```

### 1. 后端日志格式

后端发送的日志应包含以下结构：

```javascript
{
  level: 'info|success|warning|error',
  source: '攻击智能体|系统|防火墙',
  message: '具体的操作描述',
  timestamp: '2025-01-27T10:30:00Z',
  attack_info: {  // 可选：结构化攻击信息
    stage: 'reconnaissance|weaponization|delivery|exploitation|installation|command_and_control|actions_on_objectives',
    technique: '具体的攻击技术',
    source_node: 'internet|firewall|dmz-web',
    target_node: 'firewall|dmz-web|internal-db',
    status: 'starting|in_progress|completed|failed',
    progress: 0-100
  }
}
```

### 2. 动画触发机制

#### 方式一：结构化攻击信息（推荐）
```javascript
// 后端发送包含 attack_info 的日志
{
  level: 'info',
  source: '攻击智能体',
  message: '开始对防火墙进行端口扫描',
  attack_info: {
    stage: 'reconnaissance',
    technique: 'port_scan',
    source_node: 'internet',
    target_node: 'firewall',
    status: 'starting',
    progress: 10
  }
}
```

#### 方式二：基于消息内容的智能匹配
```javascript
// 后端发送普通日志，系统自动解析
{
  level: 'info',
  source: '攻击智能体',
  message: '正在扫描目标防火墙的开放端口'
}
// 系统会自动识别"扫描"关键词，触发扫描动画
```

## 🎯 攻击阶段动画映射

### 1. 侦察阶段 (Reconnaissance)
**关键词**: `扫描`, `侦察`, `情报收集`, `端口扫描`

| 技术 | 动画效果 | 描述 |
|------|----------|------|
| `port_scan` | 连续扫描脉冲 | 多层蓝色脉冲波，带"扫描中..."文字 |
| `vulnerability_scan` | 橙色扫描脉冲 | 漏洞扫描的特殊颜色标识 |
| `info_gathering` | 加载动画 | 攻击者节点显示思考/加载动画 |

**示例日志**:
```javascript
{
  level: 'info',
  source: '攻击智能体',
  message: '[侦察阶段] 开始对目标网络进行端口扫描',
  attack_info: {
    stage: 'reconnaissance',
    technique: 'port_scan',
    target_node: 'firewall',
    status: 'starting'
  }
}
```

### 2. 武器化阶段 (Weaponization)
**关键词**: `武器化`, `生成`, `钓鱼邮件`, `恶意软件`

| 技术 | 动画效果 | 描述 |
|------|----------|------|
| `phishing_email` | 加载动画(3秒) | 生成钓鱼邮件的思考过程 |
| `malware_generation` | 加载动画(4秒) | 恶意软件生成过程 |
| `exploit_creation` | 加载动画(3秒) | 漏洞利用代码创建 |

### 3. 投递阶段 (Delivery)
**关键词**: `投递`, `发送`, `邮件`, `传输`

| 技术 | 动画效果 | 描述 |
|------|----------|------|
| `email_delivery` | 蓝色攻击路径 | 邮件从攻击者到目标的传输路径 |
| `web_delivery` | 绿色攻击路径 | Web方式投递 |
| `usb_delivery` | 目标节点加载动画 | USB插入动画 |

### 4. 利用阶段 (Exploitation)
**关键词**: `利用`, `漏洞`, `攻击`, `入侵`

| 技术 | 动画效果 | 描述 |
|------|----------|------|
| `buffer_overflow` | 红色扫描脉冲 + 节点状态变化 | 缓冲区溢出攻击 |
| `sql_injection` | 数据窃取动画 | SQL注入攻击 |
| `credential_theft` | 数据流动画 | 凭据窃取过程 |

### 5. 安装阶段 (Installation)
**关键词**: `安装`, `后门`, `持久化`, `权限提升`

| 技术 | 动画效果 | 描述 |
|------|----------|------|
| `backdoor_install` | 节点状态变为已攻陷 + 加载动画 | 后门安装过程 |
| `persistence_mechanism` | 节点状态变化 | 持久化机制建立 |
| `privilege_escalation` | 红色脉冲 + 状态变化 | 权限提升 |

### 6. 命令控制阶段 (Command & Control)
**关键词**: `命令`, `控制`, `C2`, `远程访问`

| 技术 | 动画效果 | 描述 |
|------|----------|------|
| `c2_communication` | 持续网络流量 | C2服务器通信 |
| `remote_access` | 紫色攻击路径 | 远程访问建立 |
| `lateral_movement` | 橙色攻击路径 | 横向移动 |

### 7. 行动目标阶段 (Actions on Objectives)
**关键词**: `数据窃取`, `攻陷`, `破坏`, `目标达成`

| 技术 | 动画效果 | 描述 |
|------|----------|------|
| `data_theft` | 连续数据窃取动画(4秒) | 大量数据传输 |
| `system_compromise` | 成功动画 + 节点状态变化 | 系统完全攻陷 |
| `data_destruction` | 失败动画 | 数据销毁 |

## 🎨 动画效果详解

### 1. 扫描动画
```javascript
// 多层脉冲效果
- 第1层：蓝色脉冲 (#3b82f6)
- 第2层：绿色脉冲 (#10b981) 
- 第3层：橙色脉冲 (#f59e0b)
- 文字提示："扫描中..."
- 持续时间：1.5秒
```

### 2. 攻击路径动画
```javascript
// 动态路径绘制
- 起始：攻击者位置
- 终点：目标位置
- 效果：虚线路径逐渐延伸
- 后续：数据包传输 + 撞击效果
```

### 3. 节点状态变化
```javascript
// 状态颜色映射
- normal: 默认颜色
- targeted: 橙色光晕 (#f59e0b)
- compromised: 红色光晕 + 脉冲 (#dc2626)
```

### 4. 连续动画
```javascript
// 避免动画空档期
- 连续扫描：每3秒循环
- 网络流量：每800ms生成数据包
- 动画队列：有序执行，支持循环
```

## 🔧 配置选项

### 动画配置
```javascript
const config = {
  scanning: {
    duration: 1500,
    continuousInterval: 3000,
    pulseRadius: 30
  },
  networkTraffic: {
    interval: 800,
    packetColors: ['#4ade80', '#60a5fa', '#f472b6', '#fbbf24']
  },
  attackPath: {
    duration: 2000,
    color: '#ff4444',
    dashArray: [10, 5]
  }
}
```

### 节点映射（根据实际后端代码）
```javascript
const nodeMapping = {
  // 后端实际使用的节点ID -> 前端设备名称
  'internet': ['攻击者', '攻击节点'],
  'firewall': ['内部防火墙', '外部防火墙', '防火墙'],
  'target_host': ['PC-1', 'PC-2'],           // 后端主要使用这个
  'pc-user': ['PC-1', 'PC-2'],              // 备选映射
  'internal-server': ['服务器', 'WordPress网站', 'Apache_web服务器'],
  'internal-db': ['数据库', 'PostgreSQL'],
  'internal-file': ['文件服务器'],
  'dmz-web': ['WordPress网站', 'Apache_web服务器'],
  'dmz-dns': ['DNS服务器'],
  'dmz-mail': ['邮件服务器'],
  'vpn': ['VPN网关']
}
```

**重要说明**：
- 后端主要使用 `target_host` 而不是 `pc-user`
- 每个后端节点ID对应多个可能的前端设备名称
- 系统会自动进行精确匹配和模糊匹配

## 📊 使用示例

### 完整攻击序列
```javascript
// 后端发送的攻击序列日志
[
  {
    level: 'info',
    source: '攻击智能体',
    message: '开始网络侦察',
    attack_info: {
      stage: 'reconnaissance',
      technique: 'port_scan',
      target_node: 'firewall',
      status: 'starting'
    }
  },
  {
    level: 'info', 
    source: '攻击智能体',
    message: '生成钓鱼邮件',
    attack_info: {
      stage: 'weaponization',
      technique: 'phishing_email',
      target_node: 'pc-user',
      status: 'in_progress'
    }
  },
  {
    level: 'success',
    source: '攻击智能体', 
    message: '成功攻陷目标系统',
    attack_info: {
      stage: 'actions_on_objectives',
      technique: 'system_compromise',
      target_node: 'internal-db',
      status: 'completed',
      progress: 100
    }
  }
]
```

### 对应的动画效果
1. **侦察阶段**: 防火墙节点出现连续扫描脉冲
2. **武器化阶段**: 攻击者节点显示3秒加载动画
3. **行动目标阶段**: 数据库节点变为已攻陷状态，显示成功动画

## 🚀 最佳实践

### 1. 后端日志建议
- 使用结构化的 `attack_info` 字段
- 提供准确的节点ID映射
- 包含攻击进度信息
- 使用标准的攻击阶段和技术名称

### 2. 动画性能优化
- 限制同时运行的动画数量
- 及时清理完成的动画效果
- 根据设备性能调整动画质量

### 3. 用户体验
- 提供动画开关选项
- 支持动画速度调节
- 显示当前攻击阶段进度

## 🔍 调试和监控

### 控制台日志
```javascript
// 动画触发日志
🎬 收到拓扑动画事件: {stage: 'reconnaissance', technique: 'port_scan'}
🎯 触发攻击步骤动画: {sourceNode: '攻击者', targetNode: '防火墙'}
🔍 侦察阶段动画: {technique: 'port_scan', status: 'starting'}
```

### 性能监控
```javascript
// 动画性能统计
const stats = {
  activeAnimations: attackVisualization.activeAnimations.length,
  continuousAnimations: attackVisualization.continuousAnimations.size,
  effectsCount: attackVisualization.attackEffects.length
}
```

## 📞 故障排除

### 常见问题
1. **动画不触发**: 检查节点映射和事件监听器
2. **坐标不准确**: 确认拓扑节点已正确初始化
3. **性能问题**: 检查连续动画是否正确停止
4. **日志格式错误**: 验证 attack_info 字段格式

### 解决方案
- 查看浏览器控制台日志
- 使用演示页面测试动画效果
- 检查 EventMonitor 组件的日志解析逻辑
- 验证 WebSocket 连接状态
