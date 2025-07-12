# WS-UBUNTU: User workstation with Flask phishing endpoint (vulnerable)
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# ===== 安装 Python3 & Flask =====
RUN apt-get update \
    && apt-get install -y python3 python3-pip \
    && pip3 install flask requests \
    && rm -rf /var/lib/apt/lists/*

# ===== 环境变量：用户身份 & 公司名 =====
ENV COMPANY=ACME_CORP \
    USERNAME=john.doe \
    PASSWORD=User@123 \
    ROLE=developer \
    HOST_TYPE=WS-UBUNTU

WORKDIR /opt/app
COPY app.py ./

EXPOSE 5000

CMD ["python3", "app.py"]

 