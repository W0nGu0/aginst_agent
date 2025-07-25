# 项目总体结构说明

## 目录结构

```
.
├── agents/                    # 智能Agent服务，负责编排和决策
│   ├── central_agent/         # 中央Agent，负责协调其他Agent
│   └── social_engineering_agent/ # 社会工程学攻击Agent
├── services/                  # MCP服务，提供各种功能API
│   ├── attack_service/        # 攻击工具服务
│   ├── scenario_service/      # 场景生成服务
│   └── social_engineering_service/ # 社会工程学工具服务
├── docker/                    # Docker相关资源
│   ├── compose-templates/     # Docker Compose模板
│   ├── images/                # 自定义镜像
│   │   ├── ubuntu/           # Ubuntu基础镜像
│   │   ├── debian/           # Debian基础镜像
│   │   └── centos/           # CentOS基础镜像
│   └── networks/              # 网络配置
```

## 组件说明

### Agent (智能代理)

Agent是系统的智能决策层，通过调用不同的MCP服务来完成复杂任务。每个Agent都有特定的功能领域：

- **central_agent**: 中央协调者，接收用户指令并分派任务
- **social_engineering_agent**: 专注于社会工程学攻击的智能代理

### Services (服务)

Services是系统的功能支撑层，提供各种独立的API服务：

- **attack_service**: 提供各种攻击工具和漏洞利用功能
- **scenario_service**: 负责场景生成和环境编排
- **social_engineering_service**: 提供社会工程学攻击相关工具

### Docker资源

项目使用Docker进行两个层面的容器化：

1. **应用服务容器化**: 我们的Agent和Service都通过Docker容器部署
2. **模拟环境容器化**: 通过Docker Compose创建各种安全实验场景

#### Docker Compose模板

- **network-segmentation.yml**: 演示如何创建多网段、网络隔离的环境

## 运行方式

### 启动社会工程学攻击模拟

1. 启动MCP服务:

```bash
cd services/social_engineering_service
docker build -t social_eng_service .
docker run -p 8003:8003 social_eng_service
```

2. 启动Agent:

```bash
cd agents/social_engineering_agent
docker build -t social_eng_agent .
docker run -p 8004:8004 --env SOCIAL_ENGINEERING_SERVICE_URL=http://host.docker.internal:8003 social_eng_agent
```

3. 调用Agent API:

```bash
curl -X POST http://localhost:8004/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": "为王小明生成一封薪资调整的钓鱼邮件，恶意链接是http://malicious.com"}'
```
