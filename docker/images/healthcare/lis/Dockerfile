FROM ubuntu:20.04

# 设置非交互模式
ENV DEBIAN_FRONTEND=noninteractive

# 安装基础软件
RUN apt-get update && apt-get install -y \
    apache2 \
    php \
    php-mysql \
    python3 \
    python3-pip \
    wget \
    curl \
    nano \
    net-tools \
    openssh-server \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# 安装Python库
RUN pip3 install flask sqlite3 hl7

# 创建LIS目录结构
RUN mkdir -p /var/lis/data \
    && mkdir -p /var/lis/reports \
    && mkdir -p /var/lis/config \
    && mkdir -p /var/lis/temp \
    && mkdir -p /var/www/html/lis

# 复制LIS应用文件
COPY lis_server.py /var/lis/lis_server.py
COPY lis_web.php /var/www/html/index.php
COPY lab_results.php /var/www/html/results.php
COPY hl7_interface.php /var/www/html/hl7.php
COPY init_lis_db.sql /var/lis/init_lis_db.sql

# 设置Apache配置
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# 创建LIS用户（预设漏洞：弱密码）
RUN useradd -m -s /bin/bash lisadmin \
    && echo "lisadmin:lis123" | chpasswd \
    && usermod -aG sudo lisadmin

# 设置SSH
RUN mkdir /var/run/sshd \
    && echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config \
    && echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# 初始化SQLite数据库
RUN cd /var/lis && sqlite3 lis.db < init_lis_db.sql

# 设置不安全的权限（预设漏洞）
RUN chmod 777 /var/lis/data \
    && chmod 777 /var/lis/reports \
    && chmod 644 /var/lis/lis.db

# 创建启动脚本
COPY start-lis.sh /start-lis.sh
RUN chmod +x /start-lis.sh

# 暴露端口
EXPOSE 80 502 22

# 启动服务
CMD ["/start-lis.sh"]
