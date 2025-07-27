FROM ubuntu:20.04

# 设置非交互模式
ENV DEBIAN_FRONTEND=noninteractive

# 安装基础软件和DICOM工具
RUN apt-get update && apt-get install -y \
    apache2 \
    php \
    php-mysql \
    php-gd \
    python3 \
    python3-pip \
    dcmtk \
    wget \
    curl \
    nano \
    net-tools \
    openssh-server \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# 安装Python DICOM库
RUN pip3 install pydicom flask pillow

# 创建PACS目录结构
RUN mkdir -p /var/pacs/images \
    && mkdir -p /var/pacs/backup \
    && mkdir -p /var/pacs/temp \
    && mkdir -p /var/pacs/config \
    && mkdir -p /var/www/html/pacs

# 复制PACS应用文件
COPY pacs_server.py /var/pacs/pacs_server.py
COPY pacs_web.php /var/www/html/index.php
COPY dicom_viewer.php /var/www/html/viewer.php
COPY vulnerable_upload.php /var/www/html/upload.php
COPY sample_images/ /var/pacs/images/

# 设置Apache配置
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
RUN a2enmod rewrite

# 创建PACS用户（预设漏洞：弱密码）
RUN useradd -m -s /bin/bash pacsadmin \
    && echo "pacsadmin:pacs123" | chpasswd \
    && usermod -aG sudo pacsadmin

# 设置SSH
RUN mkdir /var/run/sshd \
    && echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config \
    && echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

# 设置不安全的权限（预设漏洞）
RUN chmod 777 /var/pacs/images \
    && chmod 777 /var/pacs/temp \
    && chmod 644 /var/pacs/config

# 创建启动脚本
COPY start-pacs.sh /start-pacs.sh
RUN chmod +x /start-pacs.sh

# 暴露端口
EXPOSE 80 11112 104 22

# 启动服务
CMD ["/start-pacs.sh"]
