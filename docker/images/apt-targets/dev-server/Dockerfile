FROM ubuntu:20.04

# 设置非交互模式
ENV DEBIAN_FRONTEND=noninteractive

# 安装开发工具和服务
RUN apt-get update && apt-get install -y \
    apache2 \
    php \
    php-mysql \
    nodejs \
    npm \
    python3 \
    python3-pip \
    git \
    vim \
    nano \
    curl \
    wget \
    openssh-server \
    mysql-client \
    redis-tools \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# 安装开发相关的Python包
RUN pip3 install flask django requests

# 创建开发环境目录
RUN mkdir -p /var/dev/code \
    && mkdir -p /var/dev/secrets \
    && mkdir -p /var/dev/config \
    && mkdir -p /var/dev/logs \
    && mkdir -p /var/www/html/dev

# 复制开发环境文件
COPY dev_dashboard.php /var/www/html/index.php
COPY git_repo/ /var/dev/code/medical_app/
COPY config_files/ /var/dev/config/
COPY secret_files/ /var/dev/secrets/

# 设置Apache配置
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# 创建开发用户（预设漏洞：弱密码）
RUN useradd -m -s /bin/bash developer \
    && echo "developer:dev123" | chpasswd \
    && usermod -aG sudo developer

# 创建Git仓库（预设漏洞：包含敏感信息）
RUN cd /var/dev/code/medical_app && \
    git init && \
    git config user.email "dev@company.com" && \
    git config user.name "Developer" && \
    git add . && \
    git commit -m "Initial commit with secrets"

# 设置SSH（预设漏洞：弱配置）
RUN mkdir /var/run/sshd \
    && echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config \
    && echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config \
    && echo 'PermitEmptyPasswords yes' >> /etc/ssh/sshd_config

# 设置不安全的权限（预设漏洞）
RUN chmod 777 /var/dev/code \
    && chmod 644 /var/dev/secrets/* \
    && chmod 644 /var/dev/config/*

# 创建启动脚本
COPY start-dev.sh /start-dev.sh
RUN chmod +x /start-dev.sh

# 暴露端口
EXPOSE 80 22 3000 9000

# 启动服务
CMD ["/start-dev.sh"]
