#!/bin/bash

echo "Starting APT C2 Server - Campaign: $CAMPAIGN_NAME"
echo "Target Sector: $TARGET_SECTOR"
echo "Domain: $C2_DOMAIN"

# 创建必要的目录
mkdir -p /var/c2/data /var/c2/logs

# 生成自签名SSL证书（用于HTTPS C2通信）
if [ ! -f ssl_cert.pem ]; then
    echo "Generating SSL certificate..."
    openssl req -x509 -newkey rsa:2048 -keyout ssl_key.pem -out ssl_cert.pem -days 365 -nodes \
        -subj "/C=US/ST=CA/L=SF/O=Medical Updates/CN=$C2_DOMAIN"
fi

# 启动Nginx（用于HTTPS前端）
echo "Starting Nginx..."
nginx

# 记录启动日志
echo "$(date) - C2 Server started - Campaign: $CAMPAIGN_NAME" >> /var/c2/logs/c2.log

# 启动Python C2服务器
echo "Starting C2 Python server..."
python3 c2_server.py
