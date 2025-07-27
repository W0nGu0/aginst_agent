#!/bin/bash

echo "Starting HIS (Hospital Information System)"
echo "Hospital: $HOSPITAL_NAME"
echo "Database: $PATIENT_DB"

# 创建必要的目录
mkdir -p /var/his/data /var/his/records /var/his/logs

# 等待数据库启动
echo "Waiting for database connection..."
while ! pg_isready -h medical-database -p 5432 -U med_admin; do
    echo "Database not ready, waiting..."
    sleep 2
done

echo "Database connected successfully"

# 启动Nginx
echo "Starting Nginx..."
nginx

# 记录启动日志
echo "$(date) - HIS System started - Hospital: $HOSPITAL_NAME" >> /var/his/logs/his.log

# 启动Python HIS应用
echo "Starting HIS Python application..."
python3 his_app.py
