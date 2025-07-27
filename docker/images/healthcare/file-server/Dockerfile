# Medical File Server - Simplified for APT Testing
FROM ubuntu:20.04

# 避免交互式安装
ENV DEBIAN_FRONTEND=noninteractive

# 安装基础软件包（简化版）
RUN apt-get update && apt-get install -y \
    apache2 \
    php \
    openssh-server \
    wget \
    curl \
    nano \
    && rm -rf /var/lib/apt/lists/*

# 创建医疗文件目录结构
RUN mkdir -p /var/medical-files/documents \
    && mkdir -p /var/medical-files/temp

# 复制Web界面文件
COPY index.php /var/www/html/
COPY upload.php /var/www/html/

# 复制示例医疗文件
COPY sample_files/ /var/medical-files/

# 复制启动脚本
COPY start-file-server.sh /start-file-server.sh
RUN chmod +x /start-file-server.sh

# 设置文件权限（故意设置为不安全）
RUN chmod -R 777 /var/medical-files/ \
    && chown -R www-data:www-data /var/www/html/

# 创建用户账户（弱密码）
RUN useradd -m -s /bin/bash fileadmin \
    && echo 'fileadmin:files123' | chpasswd

# 配置SSH（不安全配置）
RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config \
    && echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# 暴露端口
EXPOSE 80 22

# 启动脚本
CMD ["/start-file-server.sh"]
