#!/bin/bash

# 备份脚本 - 包含预设漏洞
# 医疗系统数据备份脚本

echo "==================================="
echo "医疗系统备份脚本"
echo "开始时间: $(date)"
echo "==================================="

# 预设漏洞：硬编码密码
DB_HOST="medical-database"
DB_USER="backup_user"
DB_PASS="backup_db_pass_2024"
BACKUP_DIR="/var/backup/data"
LOG_FILE="/var/backup/logs/backup.log"

# 创建备份目录
mkdir -p $BACKUP_DIR
mkdir -p /var/backup/logs

# 预设漏洞：不安全的权限设置
chmod 777 $BACKUP_DIR
chmod 666 $LOG_FILE

echo "$(date): 开始备份医疗数据库" >> $LOG_FILE

# 备份医疗数据库
echo "备份医疗数据库..."
BACKUP_FILE="$BACKUP_DIR/medical_db_backup_$(date +%Y%m%d_%H%M%S).sql"

# 预设漏洞：密码在命令行中可见
pg_dump -h $DB_HOST -U $DB_USER -d medical_db > $BACKUP_FILE 2>/dev/null
if [ $? -eq 0 ]; then
    echo "$(date): 医疗数据库备份成功: $BACKUP_FILE" >> $LOG_FILE
    echo "医疗数据库备份完成"
else
    echo "$(date): 医疗数据库备份失败" >> $LOG_FILE
    echo "医疗数据库备份失败"
fi

# 备份HIS系统文件
echo "备份HIS系统文件..."
HIS_BACKUP="$BACKUP_DIR/his_system_backup_$(date +%Y%m%d).tar.gz"
tar -czf $HIS_BACKUP /var/his/ 2>/dev/null
echo "$(date): HIS系统备份完成: $HIS_BACKUP" >> $LOG_FILE

# 备份PACS影像数据
echo "备份PACS影像数据..."
PACS_BACKUP="$BACKUP_DIR/pacs_images_backup_$(date +%Y%m%d).tar"
tar -cf $PACS_BACKUP /var/pacs/images/ 2>/dev/null
echo "$(date): PACS影像备份完成: $PACS_BACKUP" >> $LOG_FILE

# 备份LIS数据
echo "备份LIS数据..."
LIS_BACKUP="$BACKUP_DIR/lis_data_backup_$(date +%Y%m%d).zip"
zip -r $LIS_BACKUP /var/lis/ 2>/dev/null
echo "$(date): LIS数据备份完成: $LIS_BACKUP" >> $LOG_FILE

# 备份配置文件
echo "备份系统配置文件..."
CONFIG_BACKUP="$BACKUP_DIR/config_backup_$(date +%Y%m%d).tar.gz"
tar -czf $CONFIG_BACKUP /etc/ /var/dev/config/ /var/api/config/ 2>/dev/null
echo "$(date): 配置文件备份完成: $CONFIG_BACKUP" >> $LOG_FILE

# 预设漏洞：备份敏感文件
echo "备份敏感文件..."
SENSITIVE_BACKUP="$BACKUP_DIR/sensitive_backup_$(date +%Y%m%d).tar.gz"
tar -czf $SENSITIVE_BACKUP /etc/passwd /etc/shadow /var/dev/secrets/ /var/api/keys/ 2>/dev/null
echo "$(date): 敏感文件备份完成: $SENSITIVE_BACKUP" >> $LOG_FILE

# 创建备份清单
echo "创建备份清单..."
MANIFEST_FILE="$BACKUP_DIR/backup_manifest_$(date +%Y%m%d).txt"
cat > $MANIFEST_FILE << EOF
备份清单 - $(date)
=================================

医疗数据库备份:
- 文件: $(basename $BACKUP_FILE)
- 大小: $(du -h $BACKUP_FILE 2>/dev/null | cut -f1)
- 数据库: medical_db
- 用户: $DB_USER
- 密码: $DB_PASS

HIS系统备份:
- 文件: $(basename $HIS_BACKUP)
- 大小: $(du -h $HIS_BACKUP 2>/dev/null | cut -f1)
- 路径: /var/his/

PACS影像备份:
- 文件: $(basename $PACS_BACKUP)
- 大小: $(du -h $PACS_BACKUP 2>/dev/null | cut -f1)
- 路径: /var/pacs/images/

LIS数据备份:
- 文件: $(basename $LIS_BACKUP)
- 大小: $(du -h $LIS_BACKUP 2>/dev/null | cut -f1)
- 路径: /var/lis/

配置文件备份:
- 文件: $(basename $CONFIG_BACKUP)
- 大小: $(du -h $CONFIG_BACKUP 2>/dev/null | cut -f1)
- 路径: /etc/, /var/dev/config/, /var/api/config/

敏感文件备份:
- 文件: $(basename $SENSITIVE_BACKUP)
- 大小: $(du -h $SENSITIVE_BACKUP 2>/dev/null | cut -f1)
- 内容: 密码文件, 密钥文件, 配置文件

备份服务器信息:
- 主机: $(hostname)
- IP地址: $(hostname -I)
- 备份时间: $(date)
- 备份用户: $(whoami)

数据库连接信息:
- 主机: $DB_HOST
- 用户: $DB_USER
- 密码: $DB_PASS
- 端口: 5432

注意: 此备份未加密，包含敏感信息
EOF

echo "$(date): 备份清单创建完成: $MANIFEST_FILE" >> $LOG_FILE

# 预设漏洞：清理旧备份时的命令注入风险
RETENTION_DAYS=30
echo "清理超过 $RETENTION_DAYS 天的旧备份..."

# 漏洞：如果RETENTION_DAYS来自用户输入，可能导致命令注入
find $BACKUP_DIR -name "*.sql" -mtime +$RETENTION_DAYS -delete 2>/dev/null
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null
find $BACKUP_DIR -name "*.tar" -mtime +$RETENTION_DAYS -delete 2>/dev/null
find $BACKUP_DIR -name "*.zip" -mtime +$RETENTION_DAYS -delete 2>/dev/null

echo "$(date): 旧备份清理完成" >> $LOG_FILE

# 同步到远程备份服务器（预设漏洞：无加密传输）
REMOTE_SERVER="backup.company.com"
REMOTE_USER="backup"
REMOTE_PASS="remote_backup_pass_123"

echo "同步到远程备份服务器..."
# 预设漏洞：使用不安全的传输方式
rsync -av --password-file=<(echo $REMOTE_PASS) $BACKUP_DIR/ $REMOTE_USER@$REMOTE_SERVER:/backup/ 2>/dev/null
echo "$(date): 远程同步完成" >> $LOG_FILE

# 发送备份报告邮件（预设漏洞：邮件包含敏感信息）
EMAIL_TO="admin@company.com"
EMAIL_SUBJECT="医疗系统备份报告 - $(date +%Y-%m-%d)"

cat > /tmp/backup_report.txt << EOF
医疗系统备份报告

备份时间: $(date)
备份服务器: $(hostname)
备份状态: 成功

备份文件:
- 医疗数据库: $(basename $BACKUP_FILE)
- HIS系统: $(basename $HIS_BACKUP)
- PACS影像: $(basename $PACS_BACKUP)
- LIS数据: $(basename $LIS_BACKUP)
- 配置文件: $(basename $CONFIG_BACKUP)

数据库连接信息:
- 主机: $DB_HOST
- 用户: $DB_USER
- 密码: $DB_PASS

备份路径: $BACKUP_DIR
远程同步: 已完成

注意: 备份文件未加密，请妥善保管
EOF

# 预设漏洞：邮件发送包含敏感信息
mail -s "$EMAIL_SUBJECT" $EMAIL_TO < /tmp/backup_report.txt 2>/dev/null
rm -f /tmp/backup_report.txt

echo "==================================="
echo "备份完成时间: $(date)"
echo "备份文件位置: $BACKUP_DIR"
echo "日志文件: $LOG_FILE"
echo "==================================="

echo "$(date): 备份脚本执行完成" >> $LOG_FILE
