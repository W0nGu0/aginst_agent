# CNT-SQL: MySQL 5.7.20 with intentional vulnerabilities
FROM mysql:5.7.20

# ====== Insecure default credentials (弱口令) ======
ENV MYSQL_ROOT_PASSWORD=rootpass \
    MYSQL_DATABASE=testdb \
    MYSQL_USER=testuser \
    MYSQL_PASSWORD=testpass \
    COMPANY=ACME_CORP \
    ROLE=server \
    HOST_TYPE=CNT-SQL

# ====== Remote root login & bind to all interfaces ======
COPY my.cnf /etc/mysql/conf.d/my.cnf

EXPOSE 3306 