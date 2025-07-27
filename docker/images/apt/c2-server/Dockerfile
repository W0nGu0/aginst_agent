# APT C2 Server - 模拟APT攻击的命令控制服务器
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# 安装必要的软件包
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nginx \
    openssl \
    dnsutils \
    net-tools \
    curl \
    wget \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
RUN pip3 install flask requests cryptography

# 创建工作目录
WORKDIR /opt/c2

# 复制C2服务器文件
COPY c2_server.py ./
COPY nginx.conf /etc/nginx/nginx.conf
COPY start.sh ./

# 设置权限
RUN chmod +x start.sh

# 环境变量
ENV ATTACK_TYPE=apt \
    C2_DOMAIN=medical-updates.com \
    C2_PORT=443 \
    PERSISTENCE_METHOD=service \
    EXFILTRATION_METHOD=dns_tunneling \
    TARGET_SECTOR=healthcare \
    CAMPAIGN_NAME=MedicalShadow

# 暴露端口
EXPOSE 80 443 53

# 创建数据目录
RUN mkdir -p /var/c2/data /var/c2/logs

# 启动脚本
CMD ["./start.sh"]
