# 修复攻击动画和日志减少问题

## 问题描述
修改外部防火墙IP从 `172.203.100.2` 到 `172.203.100.254` 后，攻击动画变得不丰富，防御动画也减少，日志条数变少。

## 根本原因分析
1. Docker容器可能仍在使用旧的IP配置
2. 后端服务需要重启以应用新配置
3. 攻击智能体可能需要重新初始化网络拓扑

## 解决步骤

### 步骤1：重新部署Docker容器
```bash
# 停止所有容器
docker-compose down

# 清理网络
docker network prune -f

# 重新构建并启动容器
docker-compose up -d --force-recreate
```

### 步骤2：重启后端服务
```bash
# 重启后端主服务
cd backend
python main.py

# 重启攻击智能体
cd agents/attack_agent
python main.py

# 重启防御智能体
cd agents/defense_agent
python main.py
```

### 步骤3：清理前端缓存
1. 刷新浏览器页面（Ctrl+F5 强制刷新）
2. 清理WebSocket连接缓存
3. 重新生成拓扑图

### 步骤4：验证配置
检查以下文件确保IP地址已正确更新：
- `docker/compose-templates/company-topology.yml`
- `docker/compose-templates/base-infrastructure.yml`
- `src/views/user/Against/Topology/core/TopologyGenerator.js`
- `src/views/user/Against/Topology/core/NetworkTopology.js`

## 预防措施
1. 在修改IP地址后，始终重新部署整个环境
2. 确保所有相关服务都重启
3. 验证WebSocket连接正常工作