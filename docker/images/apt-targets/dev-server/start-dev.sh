#!/bin/bash

echo "==================================="
echo "启动开发环境服务器"
echo "==================================="

# 启动SSH服务
service ssh start

# 启动Apache服务
service apache2 start

# 创建开发环境目录结构
mkdir -p /var/dev/backup
mkdir -p /var/dev/temp
mkdir -p /var/dev/uploads

# 初始化Git仓库（如果不存在）
cd /var/dev/code/medical_app
if [ ! -d ".git" ]; then
    git init
    git config user.email "dev@company.com"
    git config user.name "Developer"
    git add .
    git commit -m "Initial commit with secrets"
fi

# 创建一些敏感的开发文件
cat > /var/dev/secrets/ssh_keys.txt << EOF
# SSH私钥文件 - 开发环境（预设漏洞）
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAFwAAAAdzc2gtcn
NhAAAAAwEAAQAAAQEA1234567890abcdef...
[这里是示例SSH私钥内容]
-----END OPENSSH PRIVATE KEY-----

# 生产服务器SSH密钥
PROD_SERVER_KEY=ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ...
PROD_SERVER_HOST=prod.company.com
PROD_SERVER_USER=root

# 开发服务器访问
DEV_SERVER_PASSWORD=dev_server_pass_123
STAGING_SERVER_PASSWORD=staging_pass_456
EOF

cat > /var/dev/config/app_secrets.conf << EOF
# 应用程序密钥配置（预设漏洞）
[application]
secret_key = app_secret_key_super_long_and_complex_2024
debug_mode = true
error_reporting = all
log_level = debug

[security]
csrf_protection = false
xss_protection = false
sql_injection_protection = false
file_upload_restrictions = false
session_timeout = 86400

[admin]
default_admin_user = admin
default_admin_pass = admin123
master_override_code = master_override_12345
emergency_access_token = emergency_token_xyz789

[external_apis]
payment_api_key = payment_live_key_12345
email_api_secret = email_service_secret_abc
sms_api_token = sms_service_token_def456
cloud_storage_key = cloud_storage_secret_ghi789
EOF

# 创建包含密码的脚本文件
cat > /var/dev/scripts/deploy.sh << EOF
#!/bin/bash
# 部署脚本 - 包含硬编码密码（预设漏洞）

PROD_DB_PASSWORD="prod_db_super_secret_2024"
STAGING_DB_PASSWORD="staging_db_pass_456"
API_SECRET_KEY="api_deployment_secret_xyz789"

echo "开始部署到生产环境..."
echo "数据库密码: \$PROD_DB_PASSWORD"
echo "API密钥: \$API_SECRET_KEY"

# 连接到生产数据库
mysql -h prod-db.company.com -u deploy_user -p\$PROD_DB_PASSWORD medical_prod << SQL
-- 部署SQL脚本
SQL

echo "部署完成"
EOF

chmod +x /var/dev/scripts/deploy.sh

# 设置不安全的权限（预设漏洞）
chmod 644 /var/dev/secrets/api_keys.txt
chmod 644 /var/dev/secrets/ssh_keys.txt
chmod 644 /var/dev/config/database.conf
chmod 644 /var/dev/config/app_secrets.conf
chmod 755 /var/dev/scripts/deploy.sh
chmod 777 /var/dev/temp
chmod 777 /var/dev/uploads

# 创建包含敏感信息的日志文件
cat > /var/dev/logs/app.log << EOF
[$(date)] INFO: 应用启动
[$(date)] DEBUG: 数据库连接 - 用户: med_admin, 密码: MedDB2024!
[$(date)] DEBUG: API密钥加载 - med_api_key_12345_secret
[$(date)] WARN: 调试模式已启用，生产环境请关闭
[$(date)] ERROR: 用户登录失败 - 用户名: admin, 密码: admin123
[$(date)] DEBUG: JWT密钥: jwt_super_secret_key_for_tokens_2024
[$(date)] INFO: 外部服务连接成功 - 令牌: ext_service_token_abcdef
EOF

# 输出服务器信息
echo "==================================="
echo "开发环境服务器已启动"
echo "Web界面: http://localhost"
echo "SSH访问: ssh developer@localhost"
echo ""
echo "预设漏洞:"
echo "  - 弱密码: developer/dev123, admin/admin123"
echo "  - 命令注入: 命令执行功能"
echo "  - 目录遍历: 文件读取功能"
echo "  - 敏感文件暴露: API密钥、SSH密钥、配置文件"
echo "  - Git信息泄露: .git目录可访问"
echo "  - 调试模式开启: 错误信息详细显示"
echo "  - 文件权限不当: 敏感文件可读"
echo "==================================="

# 保持容器运行
tail -f /var/log/apache2/access.log
