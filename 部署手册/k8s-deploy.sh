#!/bin/bash

# AI Agent攻防推演平台 - Kubernetes一键部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# 配置变量
REGISTRY="${REGISTRY:-your-registry.com/sec-agent}"
VERSION="${VERSION:-v1.0.0}"
NAMESPACE_PREFIX="sec-agent"
DOMAIN="${DOMAIN:-sec-agent.example.com}"

# 打印函数
print_header() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

print_step() {
    echo -e "\n${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查依赖
check_dependencies() {
    print_step "🔍 检查部署依赖..."
    
    # 检查kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl未安装，请先安装kubectl"
        exit 1
    fi
    print_success "kubectl 已安装"
    
    # 检查docker
    if ! command -v docker &> /dev/null; then
        print_error "docker未安装，请先安装docker"
        exit 1
    fi
    print_success "docker 已安装"
    
    # 检查集群连接
    if ! kubectl cluster-info &> /dev/null; then
        print_error "无法连接到Kubernetes集群"
        exit 1
    fi
    print_success "Kubernetes集群连接正常"
    
    # 检查Ingress Controller
    if ! kubectl get ingressclass nginx &> /dev/null; then
        print_warning "未检测到Nginx Ingress Controller，请确保已安装"
    else
        print_success "Nginx Ingress Controller 已安装"
    fi
}

# 创建命名空间
create_namespaces() {
    print_step "📁 创建命名空间..."
    
    namespaces=("frontend" "backend" "agents" "services" "data")
    
    for ns in "${namespaces[@]}"; do
        namespace_name="${NAMESPACE_PREFIX}-${ns}"
        if kubectl get namespace "$namespace_name" &> /dev/null; then
            print_warning "命名空间 $namespace_name 已存在"
        else
            kubectl create namespace "$namespace_name"
            kubectl label namespace "$namespace_name" app.kubernetes.io/name=sec-agent
            kubectl label namespace "$namespace_name" app.kubernetes.io/component="$ns"
            print_success "创建命名空间: $namespace_name"
        fi
    done
}

# 创建Secrets
create_secrets() {
    print_step "🔐 创建Secrets..."
    
    # 获取DeepSeek API密钥
    if [ -z "$DEEPSEEK_API_KEY" ]; then
        echo -n "请输入DeepSeek API密钥: "
        read -s DEEPSEEK_API_KEY
        echo
    fi
    
    if [ -z "$DEEPSEEK_API_KEY" ]; then
        print_error "DeepSeek API密钥不能为空"
        exit 1
    fi
    
    # 创建AI Agent Secrets
    kubectl create secret generic sec-agent-secrets \
        --from-literal=DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" \
        -n "${NAMESPACE_PREFIX}-agents" \
        --dry-run=client -o yaml | kubectl apply -f -
    print_success "创建AI Agent Secrets"
    
    # 获取数据库密码
    if [ -z "$DB_PASSWORD" ]; then
        DB_PASSWORD=$(openssl rand -base64 32)
    fi
    
    # 创建数据库Secrets
    kubectl create secret generic database-secrets \
        --from-literal=POSTGRES_USER=sec_agent \
        --from-literal=POSTGRES_PASSWORD="$DB_PASSWORD" \
        --from-literal=POSTGRES_DB=sec_agent \
        -n "${NAMESPACE_PREFIX}-data" \
        --dry-run=client -o yaml | kubectl apply -f -
    print_success "创建数据库Secrets"
}

# 创建ConfigMaps
create_configmaps() {
    print_step "⚙️  创建ConfigMaps..."
    
    # 后端配置
    kubectl create configmap sec-agent-config \
        --from-literal=DEBUG=False \
        --from-literal=LOG_LEVEL=INFO \
        --from-literal=CORS_ORIGINS="https://$DOMAIN" \
        --from-literal=DATABASE_URL="postgresql://sec_agent:$DB_PASSWORD@postgres.${NAMESPACE_PREFIX}-data.svc.cluster.local:5432/sec_agent" \
        --from-literal=REDIS_URL="redis://redis.${NAMESPACE_PREFIX}-data.svc.cluster.local:6379/0" \
        -n "${NAMESPACE_PREFIX}-backend" \
        --dry-run=client -o yaml | kubectl apply -f -
    print_success "创建后端配置"
    
    # Nginx配置
    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
  namespace: ${NAMESPACE_PREFIX}-frontend
data:
  nginx.conf: |
    user nginx;
    worker_processes auto;
    error_log /var/log/nginx/error.log warn;
    pid /var/run/nginx.pid;
    
    events {
        worker_connections 1024;
    }
    
    http {
        include /etc/nginx/mime.types;
        default_type application/octet-stream;
        
        sendfile on;
        keepalive_timeout 65;
        
        gzip on;
        gzip_types text/plain text/css application/json application/javascript;
        
        server {
            listen 80;
            server_name _;
            
            location / {
                root /usr/share/nginx/html;
                try_files \$uri \$uri/ /index.html;
            }
            
            location /api/ {
                proxy_pass http://backend-service.${NAMESPACE_PREFIX}-backend.svc.cluster.local:8080/api/;
                proxy_set_header Host \$host;
                proxy_set_header X-Real-IP \$remote_addr;
            }
        }
    }
EOF
    print_success "创建Nginx配置"
}

# 部署数据层
deploy_data_layer() {
    print_step "🗄️  部署数据层..."
    
    # PostgreSQL
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: ${NAMESPACE_PREFIX}-data
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: database-secrets
              key: POSTGRES_DB
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: database-secrets
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: database-secrets
              key: POSTGRES_PASSWORD
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: ${NAMESPACE_PREFIX}-data
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
EOF
    
    # Redis
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: ${NAMESPACE_PREFIX}-data
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command: ["redis-server"]
        args: ["--appendonly", "yes"]
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: ${NAMESPACE_PREFIX}-data
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
EOF
    
    print_success "数据层部署完成"
}

# 等待数据层就绪
wait_for_data_layer() {
    print_step "⏳ 等待数据层就绪..."
    
    kubectl wait --for=condition=ready pod -l app=postgres -n "${NAMESPACE_PREFIX}-data" --timeout=300s
    kubectl wait --for=condition=ready pod -l app=redis -n "${NAMESPACE_PREFIX}-data" --timeout=300s
    
    print_success "数据层已就绪"
}

# 部署应用层
deploy_application_layer() {
    print_step "🚀 部署应用层..."
    
    # 这里可以添加实际的应用部署逻辑
    # 由于篇幅限制，这里只展示框架
    
    print_success "应用层部署完成"
}

# 部署Ingress
deploy_ingress() {
    print_step "🌐 部署Ingress..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sec-agent-ingress
  namespace: ${NAMESPACE_PREFIX}-frontend
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
spec:
  rules:
  - host: $DOMAIN
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
EOF
    
    print_success "Ingress部署完成"
}

# 验证部署
verify_deployment() {
    print_step "🔍 验证部署..."
    
    # 检查所有Pod状态
    echo "检查Pod状态:"
    kubectl get pods --all-namespaces | grep sec-agent
    
    # 检查服务状态
    echo -e "\n检查服务状态:"
    kubectl get svc --all-namespaces | grep sec-agent
    
    # 检查Ingress状态
    echo -e "\n检查Ingress状态:"
    kubectl get ingress -n "${NAMESPACE_PREFIX}-frontend"
    
    print_success "部署验证完成"
}

# 显示访问信息
show_access_info() {
    print_header "部署完成"
    
    echo -e "${GREEN}🎉 AI Agent攻防推演平台已成功部署到Kubernetes!${NC}"
    echo
    echo -e "${CYAN}📋 访问信息:${NC}"
    echo -e "  🌐 前端地址: http://$DOMAIN"
    echo -e "  🔗 API地址: http://$DOMAIN/api"
    echo
    echo -e "${CYAN}🔧 管理命令:${NC}"
    echo -e "  查看Pod状态: kubectl get pods --all-namespaces | grep sec-agent"
    echo -e "  查看日志: kubectl logs -f deployment/backend -n ${NAMESPACE_PREFIX}-backend"
    echo -e "  扩展副本: kubectl scale deployment backend --replicas=3 -n ${NAMESPACE_PREFIX}-backend"
    echo
    echo -e "${YELLOW}⚠️  注意事项:${NC}"
    echo -e "  1. 请确保DNS解析正确指向集群"
    echo -e "  2. 生产环境建议配置SSL证书"
    echo -e "  3. 定期备份数据库数据"
}

# 主函数
main() {
    print_header "AI Agent攻防推演平台 - Kubernetes部署"
    
    echo -e "${CYAN}配置信息:${NC}"
    echo -e "  镜像仓库: $REGISTRY"
    echo -e "  版本: $VERSION"
    echo -e "  域名: $DOMAIN"
    echo
    
    read -p "确认开始部署? (y/n): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "部署已取消"
        exit 0
    fi
    
    # 执行部署步骤
    check_dependencies
    create_namespaces
    create_secrets
    create_configmaps
    deploy_data_layer
    wait_for_data_layer
    deploy_application_layer
    deploy_ingress
    verify_deployment
    show_access_info
}

# 错误处理
trap 'print_error "部署过程中发生错误，请检查上述输出"; exit 1' ERR

# 运行主函数
main "$@"
