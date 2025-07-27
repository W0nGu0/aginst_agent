#!/bin/bash

echo "==================================="
echo "启动备份服务器"
echo "==================================="

# 启动SSH服务
service ssh start

# 启动Apache服务
service apache2 start

# 启动Samba服务
service smbd start
service nmbd start

# 创建备份目录结构
mkdir -p /var/backup/data
mkdir -p /var/backup/logs
mkdir -p /var/backup/scripts
mkdir -p /var/backup/config
mkdir -p /var/backup/temp

# 创建示例备份文件
echo "创建示例备份文件..."

# 医疗数据库备份示例
cat > /var/backup/data/medical_db_backup_20240127.sql << EOF
-- 医疗数据库备份文件
-- 备份时间: $(date)
-- 数据库: medical_db
-- 用户: backup_user
-- 密码: backup_db_pass_2024

CREATE TABLE patients (
    patient_id VARCHAR(20) PRIMARY KEY,
    patient_name VARCHAR(100),
    id_number VARCHAR(18),
    birth_date DATE,
    gender VARCHAR(10),
    phone VARCHAR(20),
    address TEXT
);

INSERT INTO patients VALUES 
('P001', '张三', '110101199001011234', '1990-01-01', '男', '13800138001', '北京市朝阳区'),
('P002', '李四', '110101199002021235', '1990-02-02', '女', '13800138003', '北京市海淀区');

-- 敏感信息：用户密码表
CREATE TABLE user_passwords (
    username VARCHAR(50),
    password VARCHAR(100),
    role VARCHAR(20)
);

INSERT INTO user_passwords VALUES 
('admin', 'admin123', 'administrator'),
('doctor', 'doctor123', 'physician'),
('nurse', 'nurse123', 'nurse');
EOF

# HIS系统备份示例
tar -czf /var/backup/data/his_system_backup_20240127.tar.gz -C /tmp --files-from=/dev/null 2>/dev/null || true

# 创建配置文件备份
cat > /var/backup/config/database_config.conf << EOF
# 数据库配置备份
[main_database]
host = medical-database
port = 5432
database = medical_db
username = med_admin
password = MedDB2024!

[backup_database]
host = backup-server
port = 5432
database = backup_db
username = backup_admin
password = backup_db_pass_2024

[api_keys]
internal_api = med_api_key_12345_secret
external_service = ext_service_token_abcdef
admin_api = admin_api_super_secret_key
EOF

# 创建敏感文件备份
cat > /var/backup/data/sensitive_backup_20240127.tar.gz.txt << EOF
# 敏感文件备份清单
# 警告：此文件包含系统敏感信息

备份内容:
- /etc/passwd - 系统用户信息
- /etc/shadow - 用户密码哈希
- /var/dev/secrets/ - 开发环境密钥
- /var/api/keys/ - API密钥文件

SSH密钥:
- /root/.ssh/id_rsa
- /home/backupadmin/.ssh/id_rsa

数据库密码:
- medical_db: MedDB2024!
- backup_db: backup_db_pass_2024
- api_gateway_db: gateway_db_pass_123

API密钥:
- 内部API: med_api_key_12345_secret
- 外部服务: ext_service_token_abcdef
- 管理API: admin_api_super_secret_key
EOF

# 创建备份脚本的定时任务
cat > /var/backup/scripts/cron_backup.sh << EOF
#!/bin/bash
# 定时备份脚本

# 每日凌晨2点执行备份
0 2 * * * /var/backup/scripts/backup_script.sh >> /var/backup/logs/cron.log 2>&1

# 每周日凌晨1点执行完整备份
0 1 * * 0 /var/backup/scripts/full_backup.sh >> /var/backup/logs/cron.log 2>&1
EOF

chmod +x /var/backup/scripts/backup_script.sh
chmod +x /var/backup/scripts/cron_backup.sh

# 设置不安全的权限（预设漏洞）
chmod 777 /var/backup/data
chmod 777 /var/backup/logs
chmod 777 /var/backup/config
chmod 777 /var/backup/temp
chmod 644 /var/backup/config/database_config.conf
chmod 644 /var/backup/data/medical_db_backup_20240127.sql

# 创建Samba用户（预设漏洞：弱密码）
echo -e "backup2024\nbackup2024" | smbpasswd -a backupadmin -s
echo -e "guest\nguest" | smbpasswd -a guest -s

# 创建日志文件
touch /var/backup/logs/backup.log
touch /var/backup/logs/samba.log
touch /var/backup/logs/access.log

cat > /var/backup/logs/backup.log << EOF
$(date): 备份服务器启动
$(date): Samba服务已启动
$(date): 备份目录已创建
$(date): 示例备份文件已生成
$(date): 权限设置完成（警告：使用了不安全的权限）
$(date): SMB用户已创建（警告：使用了弱密码）
EOF

# 启动定时任务
cron

# 创建FTP服务（如果需要）
# service vsftpd start

# 输出服务器信息
echo "==================================="
echo "备份服务器已启动"
echo "Web界面: http://localhost"
echo "SMB共享: \\\\localhost\\backup"
echo "SSH访问: ssh backupadmin@localhost"
echo ""
echo "SMB共享列表:"
echo "  - \\\\localhost\\backup - 备份文件"
echo "  - \\\\localhost\\config - 配置文件"
echo "  - \\\\localhost\\logs - 日志文件"
echo "  - \\\\localhost\\scripts - 脚本文件"
echo "  - \\\\localhost\\temp - 临时文件"
echo "  - \\\\localhost\\root - 系统根目录 (危险)"
echo ""
echo "预设漏洞:"
echo "  - 弱密码: backupadmin/backup2024"
echo "  - SMB配置不当: 允许匿名访问"
echo "  - 权限过宽: 备份文件777权限"
echo "  - 敏感文件暴露: 数据库密码、API密钥"
echo "  - 命令注入: 备份命令执行功能"
echo "  - 目录遍历: 文件下载功能"
echo "  - 根目录共享: 整个文件系统可访问"
echo "  - 备份未加密: 敏感数据明文存储"
echo "  - 详细日志: 可能泄露敏感信息"
echo "==================================="

# 保持容器运行
tail -f /var/backup/logs/backup.log
