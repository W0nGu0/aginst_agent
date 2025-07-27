FROM postgres:13

# 设置环境变量
ENV POSTGRES_DB=medical_db
ENV POSTGRES_USER=med_admin
ENV POSTGRES_PASSWORD=MedDB2024!

# 安装额外工具
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    nano \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# 复制初始化脚本
COPY init-medical-db.sql /docker-entrypoint-initdb.d/
COPY medical-data.sql /docker-entrypoint-initdb.d/
COPY vulnerable-config.sql /docker-entrypoint-initdb.d/

# 复制配置文件
COPY postgresql.conf /etc/postgresql/postgresql.conf
COPY pg_hba.conf /etc/postgresql/pg_hba.conf

# 创建数据目录
RUN mkdir -p /var/lib/postgresql/backup \
    && mkdir -p /var/log/postgresql \
    && chown -R postgres:postgres /var/lib/postgresql/backup \
    && chown -R postgres:postgres /var/log/postgresql

# 设置不安全的权限（预设漏洞）
RUN chmod 644 /etc/postgresql/postgresql.conf \
    && chmod 644 /etc/postgresql/pg_hba.conf

# 暴露端口
EXPOSE 5432

# 启动脚本
COPY start-medical-db.sh /start-medical-db.sh
RUN chmod +x /start-medical-db.sh

CMD ["/start-medical-db.sh"]
