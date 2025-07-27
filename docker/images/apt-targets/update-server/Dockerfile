FROM ubuntu:20.04

# 设置非交互模式
ENV DEBIAN_FRONTEND=noninteractive

# 安装基础软件
RUN apt-get update && apt-get install -y \
    apache2 \
    php \
    php-mysql \
    wget \
    curl \
    nano \
    net-tools \
    openssh-server \
    && rm -rf /var/lib/apt/lists/*

# 创建更新服务器目录结构
RUN mkdir -p /var/updates/packages \
    && mkdir -p /var/updates/logs \
    && mkdir -p /var/updates/config \
    && mkdir -p /var/www/html/updates

# 创建简单的更新服务器Web界面
COPY update_server.php /var/www/html/index.php
COPY config.php /var/updates/config/
COPY vulnerable_upload.php /var/www/html/upload.php

# 设置Apache配置
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# 创建预设漏洞：弱密码用户
RUN useradd -m -s /bin/bash updateadmin \
    && echo "updateadmin:update123" | chpasswd \
    && usermod -aG sudo updateadmin

# 设置SSH
RUN mkdir /var/run/sshd \
    && echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config \
    && echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# 创建启动脚本
COPY start.sh /start.sh
RUN chmod +x /start.sh

# 暴露端口
EXPOSE 80 443 22

# 启动服务
CMD ["/start.sh"]
