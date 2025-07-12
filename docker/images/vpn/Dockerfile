# 改为基于 Debian9 安装旧版 OpenVPN 2.4.0（含 CVE-2020-15078）
FROM debian:11-slim

RUN apt-get update \
    && apt-get install -y openvpn python3 \
    && rm -rf /var/lib/apt/lists/*

ENV COMPANY=ACME_CORP \
    ROLE=vpn \
    HOST_TYPE=VPN \
    VPN_USER=vpnuser \
    VPN_PASS=vpnpass

WORKDIR /opt/vpn
COPY server.conf ./
COPY start.sh ./
RUN chmod +x start.sh

# 管理接口 7505 / HTTP 8000 / 数据通道 1194
EXPOSE 1194/udp 7505/tcp 8000

CMD ["./start.sh"] 