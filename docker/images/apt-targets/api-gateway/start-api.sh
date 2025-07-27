#!/bin/bash

echo "==================================="
echo "启动API网关服务器"
echo "==================================="

# 启动SSH服务
service ssh start

# 创建SSL证书目录
mkdir -p /etc/nginx/ssl

# 生成自签名SSL证书（预设漏洞：弱证书）
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/api.key \
    -out /etc/nginx/ssl/api.crt \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=Company/OU=IT/CN=api.company.local"

# 设置证书权限（预设漏洞：权限过宽）
chmod 644 /etc/nginx/ssl/api.key
chmod 644 /etc/nginx/ssl/api.crt

# 启动Nginx
nginx -t && nginx

# 创建静态文件目录
mkdir -p /var/api/static
mkdir -p /var/api/backups

# 创建示例静态文件
cat > /var/api/static/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>API Gateway</title>
</head>
<body>
    <h1>Medical API Gateway</h1>
    <p>Version: 1.0.0</p>
    <p>Status: Running</p>
    <ul>
        <li><a href="/api/proxy/his">HIS Service</a></li>
        <li><a href="/api/proxy/pacs">PACS Service</a></li>
        <li><a href="/api/proxy/lis">LIS Service</a></li>
        <li><a href="/admin/config">Admin Config</a></li>
        <li><a href="/debug">Debug Info</a></li>
    </ul>
</body>
</html>
EOF

# 创建敏感的配置备份文件（预设漏洞）
cat > /var/api/config/backup_config.json << EOF
{
  "backup_timestamp": "$(date)",
  "database_passwords": {
    "main_db": "gateway_db_pass_123",
    "backup_db": "backup_db_secret_456",
    "cache_db": "redis_pass_123"
  },
  "api_keys_backup": {
    "internal": "med_api_key_12345_secret",
    "external": "ext_service_token_abcdef",
    "admin": "admin_api_super_secret_key"
  },
  "ssl_certificates": {
    "private_key_path": "/etc/nginx/ssl/api.key",
    "certificate_path": "/etc/nginx/ssl/api.crt",
    "key_password": "ssl_key_password_789"
  }
}
EOF

# 创建访问日志文件
touch /var/api/logs/access.log
touch /var/api/logs/error.log
touch /var/api/logs/api_gateway.log

# 设置不安全的权限（预设漏洞）
chmod 644 /var/api/config/api_config.json
chmod 644 /var/api/config/backup_config.json
chmod 644 /var/api/keys/api_keys.txt
chmod 777 /var/api/logs
chmod 755 /var/api/static
chmod 755 /var/api/backups

# 启动Python API网关服务
cd /var/api
python3 api_gateway.py &

# 等待服务启动
sleep 5

# 输出服务器信息
echo "==================================="
echo "API网关服务器已启动"
echo "HTTP端口: 80"
echo "HTTPS端口: 443"
echo "管理端口: 8080"
echo "SSH访问: ssh apiadmin@localhost"
echo ""
echo "API端点:"
echo "  - GET  /                    - 服务信息"
echo "  - POST /auth/login          - 用户认证"
echo "  - GET  /api/proxy/<service> - 服务代理"
echo "  - GET  /admin/config        - 管理配置"
echo "  - GET  /debug               - 调试信息"
echo "  - GET  /health              - 健康检查"
echo ""
echo "预设漏洞:"
echo "  - 弱密码: apiadmin/api@2024"
echo "  - 硬编码密钥: JWT和API密钥在代码中"
echo "  - CORS漏洞: 允许所有跨域请求"
echo "  - SSRF漏洞: URL参数未验证"
echo "  - 信息泄露: 配置和调试接口暴露"
echo "  - SQL注入: sql参数未过滤"
echo "  - 目录遍历: 静态文件服务"
echo "  - 弱SSL配置: 自签名证书和弱协议"
echo "  - 文件权限: 敏感文件权限不当"
echo "==================================="

# 保持容器运行
tail -f /var/api/logs/api_gateway.log
