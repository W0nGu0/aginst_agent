FROM ubuntu:20.04

# 设置非交互模式
ENV DEBIAN_FRONTEND=noninteractive

# 安装基础软件
RUN apt-get update && apt-get install -y \
    apache2 \
    php \
    samba \
    rsync \
    cron \
    curl \
    wget \
    nano \
    net-tools \
    openssh-server \
    && rm -rf /var/lib/apt/lists/*

# 创建备份目录
RUN mkdir -p /var/backup/data \
    && mkdir -p /var/backup/logs \
    && mkdir -p /var/backup/scripts \
    && mkdir -p /var/www/html/backup

# 复制备份服务器文件
COPY backup_web.php /var/www/html/index.php
COPY backup_script.sh /var/backup/scripts/
COPY smb.conf /etc/samba/smb.conf

# 设置Apache配置
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

# 创建备份用户（预设漏洞：弱密码）
RUN useradd -m -s /bin/bash backupadmin \
    && echo "backupadmin:backup2024" | chpasswd \
    && usermod -aG sudo backupadmin

# 设置Samba用户（预设漏洞：弱密码）
RUN echo -e "backup2024\nbackup2024" | smbpasswd -a backupadmin

# 设置SSH
RUN mkdir /var/run/sshd \
    && echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config \
    && echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# 设置不安全的权限（预设漏洞）
RUN chmod 777 /var/backup/data \
    && chmod 755 /var/backup/scripts/backup_script.sh \
    && chmod 644 /etc/samba/smb.conf

# 创建启动脚本
COPY start-backup.sh /start-backup.sh
RUN chmod +x /start-backup.sh

# 暴露端口
EXPOSE 80 445 139 22

# 启动服务
CMD ["/start-backup.sh"]
