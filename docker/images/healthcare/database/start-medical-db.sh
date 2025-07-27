#!/bin/bash

echo "==================================="
echo "启动医疗数据库服务器"
echo "==================================="

# 设置PostgreSQL配置
export PGDATA=/var/lib/postgresql/data

# 启动PostgreSQL
docker-entrypoint.sh postgres &

# 等待数据库启动
sleep 10

# 输出数据库信息
echo "==================================="
echo "医疗数据库已启动"
echo "数据库: medical_db, his_db, pacs_db, lis_db"
echo "主用户: med_admin / MedDB2024!"
echo "HIS用户: his_user / his_pass123"
echo "PACS用户: pacs_user / pacs_pass123"
echo "LIS用户: lis_user / lis_pass123"
echo ""
echo "预设漏洞:"
echo "  - 弱密码: 多个系统使用弱密码"
echo "  - 明文存储: 用户密码明文存储"
echo "  - 未加密数据: 敏感信息未加密"
echo "  - 权限过高: 只读角色可访问敏感数据"
echo "  - 备份暴露: 备份文件权限不当"
echo "==================================="

# 保持容器运行
wait
