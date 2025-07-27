# HIS (Hospital Information System) - 医院信息系统
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# 安装必要的软件包
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    postgresql-client \
    nginx \
    curl \
    wget \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
RUN pip3 install flask psycopg2-binary requests sqlalchemy flask-sqlalchemy

# 创建工作目录
WORKDIR /opt/his

# 复制HIS系统文件
COPY his_app.py ./
COPY templates/ ./templates/
COPY static/ ./static/
COPY nginx.conf /etc/nginx/nginx.conf
COPY start.sh ./

# 设置权限
RUN chmod +x start.sh

# 环境变量
ENV HOSPITAL_NAME="中心医院" \
    PATIENT_DB=patients_database \
    MEDICAL_RECORDS=enabled \
    BILLING_SYSTEM=enabled \
    DEPARTMENT_SYSTEM=enabled \
    USER_ROLES=doctor,nurse,admin,pharmacist,technician \
    ENCRYPTION_ENABLED=false

# 暴露端口
EXPOSE 80 443

# 创建数据目录
RUN mkdir -p /var/his/data /var/his/records /var/his/logs

# 启动脚本
CMD ["./start.sh"]
