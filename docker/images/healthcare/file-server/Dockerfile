# Medical File Server - Vulnerable for APT Testing
FROM ubuntu:20.04

# 避免交互式安装
ENV DEBIAN_FRONTEND=noninteractive

# 安装基础软件包
RUN apt-get update && apt-get install -y \
    apache2 \
    php \
    php-mysql \
    samba \
    samba-common-bin \
    openssh-server \
    wget \
    curl \
    nano \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# 创建医疗文件目录结构
RUN mkdir -p /var/medical-files/documents \
    && mkdir -p /var/medical-files/images \
    && mkdir -p /var/medical-files/reports \
    && mkdir -p /var/medical-files/policies \
    && mkdir -p /var/medical-files/backups \
    && mkdir -p /var/medical-files/temp

# 复制Web界面文件
COPY index.php /var/www/html/
COPY file_manager.php /var/www/html/
COPY upload.php /var/www/html/
COPY download.php /var/www/html/

# 复制示例医疗文件
COPY sample_files/ /var/medical-files/

# 复制Samba配置
COPY smb.conf /etc/samba/smb.conf

# 复制启动脚本
COPY start-file-server.sh /start-file-server.sh
RUN chmod +x /start-file-server.sh

# 设置文件权限（故意设置为不安全）
RUN chmod -R 777 /var/medical-files/ \
    && chmod 666 /etc/samba/smb.conf \
    && chown -R www-data:www-data /var/www/html/

# 创建用户账户（弱密码）
RUN useradd -m -s /bin/bash fileadmin \
    && echo 'fileadmin:files123' | chpasswd \
    && useradd -m -s /bin/bash meduser \
    && echo 'meduser:medical2024' | chpasswd

# 添加Samba用户
RUN echo -e 'files123\nfiles123' | smbpasswd -a fileadmin \
    && echo -e 'medical2024\nmedical2024' | smbpasswd -a meduser

# 配置SSH（不安全配置）
RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config \
    && echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config \
    && echo 'PermitEmptyPasswords yes' >> /etc/ssh/sshd_config

# 暴露端口
EXPOSE 80 139 445 22

# 启动脚本
CMD ["/start-file-server.sh"]
