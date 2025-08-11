# Docker Compose容器化部署指南

本文档提供基于Docker Compose的AI Agent攻防推演平台容器化部署方案，适用于开发、测试和小规模生产环境。

## 📋 Docker Compose架构

### 🏗️ 服务架构图
```
┌─────────────────────────────────────────────────────────┐
│                Docker Compose 服务栈                    │
├─────────────────────────────────────────────────────────┤
│  Nginx (反向代理)                                       │
│  ├── 前端静态文件服务                                   │
│  └── API请求代理                                        │
├─────────────────────────────────────────────────────────┤
│  Frontend (前端服务)                                    │
│  └── Vue.js 应用 (构建后的静态文件)                     │
├─────────────────────────────────────────────────────────┤
│  Backend Services (后端服务层)                          │
│  ├── Backend API (8080)                                │
│  └── Central Agent (8006)                              │
├─────────────────────────────────────────────────────────┤
│  AI Agents (智能代理层)                                 │
│  ├── Scenario Agent (8007)                             │
│  ├── Attack Agent (8004)                               │
│  ├── Evaluate Agent (8014)                             │
│  └── Victim Host Agent (8015)                          │
├─────────────────────────────────────────────────────────┤
│  MCP Services (微服务层)                                │
│  ├── Scenario Service (8002)                           │
│  ├── Attack Service (8001)                             │
│  └── Evaluate Service (8005)                           │
├─────────────────────────────────────────────────────────┤
│  Data Layer (数据层)                                    │
│  ├── PostgreSQL (5432)                                 │
│  ├── Redis (6379)                                      │
│  └── Persistent Volumes                                │
└─────────────────────────────────────────────────────────┘
```

## 🔧 环境要求

### 系统要求
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **系统内存**: 8GB以上 (推荐16GB)
- **磁盘空间**: 50GB以上
- **CPU**: 4核心以上

### 网络端口
- **80**: Nginx反向代理
- **443**: HTTPS (可选)
- **5432**: PostgreSQL (内部)
- **6379**: Redis (内部)

## 📦 Docker Compose配置

### 1. 主配置文件

创建 `docker-compose.yml`:
```yaml
version: '3.8'

services:
  # Nginx反向代理
  nginx:
    image: nginx:alpine
    container_name: sec_agent_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - frontend_dist:/usr/share/nginx/html:ro
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
    networks:
      - frontend_net
      - backend_net

  # 前端构建服务
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: sec_agent_frontend
    volumes:
      - frontend_dist:/app/dist
    command: npm run build
    networks:
      - frontend_net

  # 后端API服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: sec_agent_backend
    environment:
      - DEBUG=False
      - LOG_LEVEL=INFO
      - DATABASE_URL=postgresql://sec_agent:${DB_PASSWORD}@postgres:5432/sec_agent
      - REDIS_URL=redis://redis:6379/0
      - CORS_ORIGINS=http://localhost,https://localhost
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - backend_net
      - data_net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 中央控制智能体
  central_agent:
    build:
      context: ./agents/central_agent
      dockerfile: Dockerfile
    container_name: sec_agent_central
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - backend_net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 场景智能体
  scenario_agent:
    build:
      context: ./agents/scenario_agent
      dockerfile: Dockerfile
    container_name: sec_agent_scenario
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - backend_net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 攻击智能体
  attack_agent:
    build:
      context: ./agents/attack_agent
      dockerfile: Dockerfile
    container_name: sec_agent_attack
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - backend_net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 评估智能体
  evaluate_agent:
    build:
      context: ./agents/evaluate_agent
      dockerfile: Dockerfile
    container_name: sec_agent_evaluate
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - backend_net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 场景服务
  scenario_service:
    build:
      context: ./services/scenario_service
      dockerfile: Dockerfile
    container_name: sec_agent_scenario_svc
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - backend_net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/mcp/"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 攻击服务
  attack_service:
    build:
      context: ./services/attack_service
      dockerfile: Dockerfile
    container_name: sec_agent_attack_svc
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - backend_net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/mcp/"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 评估服务
  evaluate_service:
    build:
      context: ./services/evaluate_service
      dockerfile: Dockerfile
    container_name: sec_agent_evaluate_svc
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - backend_net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/mcp/"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL数据库
  postgres:
    image: postgres:15-alpine
    container_name: sec_agent_postgres
    environment:
      - POSTGRES_DB=sec_agent
      - POSTGRES_USER=sec_agent
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    networks:
      - data_net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sec_agent"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: sec_agent_redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - data_net
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  redis_data:
  frontend_dist:

networks:
  frontend_net:
    driver: bridge
  backend_net:
    driver: bridge
  data_net:
    driver: bridge
```

### 2. 环境变量配置

创建 `.env` 文件:
```env
# 数据库配置
DB_PASSWORD=your_secure_database_password_here
REDIS_PASSWORD=your_secure_redis_password_here

# AI API配置
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 应用配置
DOMAIN=localhost
SSL_ENABLED=false

# 日志配置
LOG_LEVEL=INFO
DEBUG=false

# 安全配置
JWT_SECRET=your_jwt_secret_key_here
```

### 3. Nginx配置

创建 `nginx/nginx.conf`:
```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # 性能优化
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # 上游服务器
    upstream backend {
        server backend:8080;
        keepalive 32;
    }

    upstream scenario_agent {
        server scenario_agent:8000;
        keepalive 16;
    }

    upstream attack_agent {
        server attack_agent:8000;
        keepalive 16;
    }

    upstream evaluate_agent {
        server evaluate_agent:8000;
        keepalive 16;
    }

    # 主服务器配置
    server {
        listen 80;
        server_name localhost;

        # 前端静态文件
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
            
            # 缓存静态资源
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }

        # 后端API代理
        location /api/ {
            proxy_pass http://backend/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket代理
        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # AI智能代理代理
        location /agents/scenario/ {
            proxy_pass http://scenario_agent/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /agents/attack/ {
            proxy_pass http://attack_agent/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /agents/evaluate/ {
            proxy_pass http://evaluate_agent/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # 健康检查
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

## 🚀 部署流程

### 1. 准备工作

#### 创建项目目录结构
```bash
mkdir -p sec_agent_docker
cd sec_agent_docker

# 创建必要目录
mkdir -p {nginx,logs,uploads,backups}
mkdir -p nginx/ssl
```

#### 复制项目文件
```bash
# 复制项目源代码到当前目录
cp -r /path/to/your/sec_agent/* .

# 确保Dockerfile存在
ls -la */Dockerfile
```

### 2. 配置环境

#### 创建环境变量文件
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
nano .env
```

#### 设置API密钥
```bash
# 在.env文件中设置DeepSeek API密钥
echo "DEEPSEEK_API_KEY=sk-your-api-key-here" >> .env
```

### 3. 构建和启动

#### 构建所有镜像
```bash
# 构建所有服务镜像
docker-compose build

# 查看构建的镜像
docker images | grep sec_agent
```

#### 启动服务栈
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

#### 查看启动日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f scenario_agent
```

### 4. 验证部署

#### 检查服务健康状态
```bash
# 检查所有容器状态
docker-compose ps

# 检查健康检查状态
docker-compose exec backend curl -f http://localhost:8080/health
docker-compose exec scenario_agent curl -f http://localhost:8000/health
```

#### 测试前端访问
```bash
# 测试前端页面
curl -I http://localhost

# 测试API接口
curl http://localhost/api/health
```

## 🔧 运维管理

### 1. 服务管理

#### 启动/停止服务
```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启特定服务
docker-compose restart backend

# 停止并删除所有容器和网络
docker-compose down --volumes
```

#### 扩缩容管理
```bash
# 扩展后端服务副本
docker-compose up -d --scale backend=3

# 扩展AI智能代理
docker-compose up -d --scale scenario_agent=2
```

### 2. 日志管理

#### 查看日志
```bash
# 实时查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f --tail=100 backend

# 查看错误日志
docker-compose logs --since=1h | grep ERROR
```

#### 日志轮转配置
```yaml
# 在docker-compose.yml中添加日志配置
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 3. 数据管理

#### 数据备份
```bash
# 备份PostgreSQL数据
docker-compose exec postgres pg_dump -U sec_agent sec_agent > backups/backup_$(date +%Y%m%d_%H%M%S).sql

# 备份Redis数据
docker-compose exec redis redis-cli --rdb /data/dump.rdb
```

#### 数据恢复
```bash
# 恢复PostgreSQL数据
docker-compose exec -T postgres psql -U sec_agent sec_agent < backups/backup_20241201_120000.sql

# 恢复Redis数据
docker-compose exec redis redis-cli --rdb /data/dump.rdb
```

### 4. 更新部署

#### 滚动更新
```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build

# 滚动更新服务
docker-compose up -d --no-deps backend
docker-compose up -d --no-deps scenario_agent
```

#### 版本回滚
```bash
# 查看镜像历史
docker images | grep sec_agent

# 回滚到指定版本
docker tag sec_agent_backend:v1.0.0 sec_agent_backend:latest
docker-compose up -d --no-deps backend
```

## 📊 监控和告警

### 1. 健康检查监控

创建 `monitoring/health-check.sh`:
```bash
#!/bin/bash

services=("backend" "scenario_agent" "attack_agent" "evaluate_agent" "postgres" "redis")

for service in "${services[@]}"; do
    if docker-compose ps $service | grep -q "Up (healthy)"; then
        echo "✅ $service: 健康"
    else
        echo "❌ $service: 异常"
        # 发送告警通知
        curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
             -d "chat_id=$CHAT_ID" \
             -d "text=🚨 服务异常: $service"
    fi
done
```

### 2. 资源监控

创建 `monitoring/resource-monitor.sh`:
```bash
#!/bin/bash

# 检查容器资源使用
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# 检查磁盘使用
df -h | grep -E "(docker|overlay)"

# 检查网络连接
netstat -tulpn | grep -E "(80|443|5432|6379)"
```

## 🔐 安全配置

### 1. 网络安全

#### 防火墙配置
```bash
# 只开放必要端口
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 5432  # 禁止外部访问数据库
sudo ufw deny 6379  # 禁止外部访问Redis
```

#### SSL/TLS配置
```bash
# 生成自签名证书 (开发环境)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/server.key \
    -out nginx/ssl/server.crt

# 或使用Let's Encrypt (生产环境)
certbot certonly --standalone -d your-domain.com
```

### 2. 容器安全

#### 安全扫描
```bash
# 扫描镜像漏洞
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image sec_agent_backend:latest

# 扫描容器配置
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    docker/docker-bench-security
```

## 📋 故障排除

### 常见问题

#### 1. 容器启动失败
```bash
# 查看容器日志
docker-compose logs container_name

# 检查容器状态
docker-compose ps

# 重新构建镜像
docker-compose build --no-cache container_name
```

#### 2. 网络连接问题
```bash
# 检查网络配置
docker network ls
docker network inspect sec_agent_backend_net

# 测试容器间连通性
docker-compose exec backend ping postgres
```

#### 3. 存储问题
```bash
# 检查卷使用情况
docker volume ls
docker system df

# 清理未使用的卷
docker volume prune
```

## 🎯 性能优化

### 1. 资源限制
```yaml
# 在docker-compose.yml中添加资源限制
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```

### 2. 缓存优化
```dockerfile
# 在Dockerfile中优化构建缓存
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

---

**版本**: v1.0.0
**更新日期**: 2024年12月
**维护团队**: AI Agent攻防推演平台开发团队

通过本指南，您可以使用Docker Compose快速部署完整的AI Agent攻防推演平台。
```
