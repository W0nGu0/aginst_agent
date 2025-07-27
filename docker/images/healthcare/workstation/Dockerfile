# Healthcare Workstation - 医疗工作站
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# 安装桌面环境和必要软件
RUN apt-get update && apt-get install -y \
    xfce4 \
    xfce4-goodies \
    tightvncserver \
    firefox \
    libreoffice \
    python3 \
    python3-pip \
    curl \
    wget \
    openssh-server \
    samba \
    cifs-utils \
    rdesktop \
    net-tools \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
RUN pip3 install requests

# 创建用户目录
RUN mkdir -p /home/doctor /home/nurse /home/admin

# 设置VNC
RUN mkdir -p /root/.vnc
COPY vncpasswd /root/.vnc/passwd
RUN chmod 600 /root/.vnc/passwd

# 复制工作站配置文件
COPY xstartup /root/.vnc/xstartup
COPY workstation_setup.py ./
COPY medical_client.py ./
COPY start.sh ./

# 设置权限
RUN chmod +x /root/.vnc/xstartup
RUN chmod +x start.sh

# 创建共享文件夹（预设漏洞：权限过于宽松）
RUN mkdir -p /shared/patient_data
RUN chmod 777 /shared/patient_data

# 环境变量
ENV USER_ROLE=doctor \
    DEPARTMENT=internal_medicine \
    USERNAME=dr_zhang \
    PASSWORD=Doctor123! \
    EMAIL=zhang.doctor@hospital.com \
    ACCESS_LEVEL=high \
    PATIENT_ACCESS=full \
    SYSTEM_ACCESS=his,pacs,lis

# 暴露端口
EXPOSE 5900 3389 22 445

# 启动脚本
CMD ["./start.sh"]
