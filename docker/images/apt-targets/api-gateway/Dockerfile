FROM ubuntu:20.04

# 设置非交互模式
ENV DEBIAN_FRONTEND=noninteractive

# 安装基础软件
RUN apt-get update && apt-get install -y \
    nginx \
    python3 \
    python3-pip \
    curl \
    wget \
    nano \
    net-tools \
    openssh-server \
    && rm -rf /var/lib/apt/lists/*

# 安装Python库
RUN pip3 install flask flask-cors requests jwt

# 创建API网关目录
RUN mkdir -p /var/api/config \
    && mkdir -p /var/api/logs \
    && mkdir -p /var/api/keys

# 复制API网关文件
COPY api_gateway.py /var/api/api_gateway.py
COPY nginx.conf /etc/nginx/nginx.conf
COPY api_config.json /var/api/config/
COPY api_keys.txt /var/api/keys/

# 创建API用户（预设漏洞：弱密码）
RUN useradd -m -s /bin/bash apiadmin \
    && echo "apiadmin:api@2024" | chpasswd \
    && usermod -aG sudo apiadmin

# 设置SSH
RUN mkdir /var/run/sshd \
    && echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config \
    && echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# 设置不安全的权限（预设漏洞）
RUN chmod 644 /var/api/config/api_config.json \
    && chmod 644 /var/api/keys/api_keys.txt

# 创建启动脚本
COPY start-api.sh /start-api.sh
RUN chmod +x /start-api.sh

# 暴露端口
EXPOSE 80 443 5000 22

# 启动服务
CMD ["/start-api.sh"]
