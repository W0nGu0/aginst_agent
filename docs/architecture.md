# 安全攻防平台架构设计

## 1. 总体架构

安全攻防平台采用多智能体协作的架构，由中控智能体统一调度，各个专业智能体负责不同的功能模块。整个系统分为三层：

1. **智能体层**：包括中控智能体、攻击智能体、防御智能体等
2. **服务层**：包括各种MCP服务，为智能体提供工具和能力
3. **基础设施层**：包括容器化环境、网络拓扑等

![架构图](../architecture.png)

## 2. 智能体设计

### 2.1 中控智能体

- **职责**：总体调度、任务分配、结果汇总、评估分析
- **技术栈**：DeepSeek LLM、FastAPI
- **位置**：`agents/central_agent/main.py`

### 2.2 攻击智能体

- **职责**：执行各种攻击任务，包括侦察、钓鱼攻击、漏洞利用等
- **技术栈**：DeepSeek LLM、FastAPI
- **位置**：`agents/attack_agent/main.py`
- **调用服务**：`services/attack_service/main.py`

### 2.3 受害主机智能体

- **职责**：模拟受害主机的行为，响应攻击
- **技术栈**：FastAPI
- **位置**：`agents/victim_host_agent/main.py`

## 3. MCP服务设计

### 3.1 攻击服务

- **职责**：提供各种攻击工具，如端口扫描、钓鱼邮件生成、漏洞利用等
- **技术栈**：FastAPI、FastMCP
- **位置**：`services/attack_service/main.py`
- **主要工具**：
  - `run_nmap`: 端口扫描工具
  - `fetch_url_content`: 获取URL内容
  - `craft_phishing_email`: 生成钓鱼邮件
  - `send_payload_to_victim`: 发送攻击载荷
  - `search_exploit`: 搜索漏洞利用模块
  - `execute_exploit_module`: 执行漏洞利用
  - `execute_shell_command`: 执行Shell命令
  - `get_network_info`: 获取网络信息

### 3.2 场景服务

- **职责**：管理攻防场景，生成网络拓扑
- **技术栈**：FastAPI、FastMCP
- **位置**：`services/scenario_service/main.py`

## 4. 前端设计

### 4.1 网络拓扑可视化

- **职责**：展示网络拓扑，支持交互操作
- **技术栈**：Vue.js、Fabric.js
- **位置**：`src/views/user/Against/Topology/TopologyView.vue`

### 4.2 攻击可视化

- **职责**：可视化展示攻击过程和结果
- **技术栈**：Vue.js、D3.js、GSAP
- **位置**：`src/views/user/Against/Topology/components/PhishingAttackVisualization.vue`

## 5. 数据流设计

### 5.1 攻击流程

1. 中控智能体下达攻击指令
2. 攻击智能体接收指令，规划攻击路径
3. 攻击智能体调用攻击服务的工具执行攻击
4. 受害主机智能体接收攻击并响应
5. 攻击结果返回给攻击智能体
6. 攻击智能体将结果报告给中控智能体
7. 前端展示攻击过程和结果

### 5.2 钓鱼攻击流程

1. 攻击智能体接收钓鱼攻击指令
2. 攻击智能体调用`fetch_url_content`获取目标信息
3. 攻击智能体调用`craft_phishing_email`生成钓鱼邮件
4. 攻击智能体调用`send_payload_to_victim`发送钓鱼邮件
5. 受害主机智能体接收钓鱼邮件并响应
6. 攻击结果返回给攻击智能体
7. 前端展示钓鱼攻击过程和结果

## 6. 容器化部署

### 6.1 容器设计

- **攻击容器**：包含攻击智能体和攻击服务
- **受害主机容器**：包含受害主机智能体
- **中控容器**：包含中控智能体
- **前端容器**：包含Vue.js前端应用

### 6.2 网络设计

- 创建独立的攻击网络和目标网络
- 使用Docker网络隔离不同的网段
- 通过防火墙容器控制网络访问

## 7. 下一步计划

1. 完善攻击服务的钓鱼攻击功能
2. 实现攻击智能体调用攻击服务的流程
3. 完善前端钓鱼攻击可视化
4. 测试端到端的钓鱼攻击流程
5. 扩展其他类型的攻击