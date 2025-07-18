# 改为基于 Debian9 安装旧版 OpenVPN 2.4.0（含 CVE-2020-15078）
FROM debian:11-slim

RUN apt-get update \
    && apt-get install -y openvpn python3 openssl \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /dev/net \
    && mknod /dev/net/tun c 10 200 || true \
    && chmod 600 /dev/net/tun \
    && mkdir -p /etc/openvpn/easy-rsa /opt/share

# 创建必要的证书和密钥
RUN cd /etc/openvpn/easy-rsa \
    && openssl dhparam -out /etc/openvpn/dh2048.pem 2048 \
    && openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout ca.key -out ca.crt -subj '/CN=OpenVPN-CA' \
    && openssl req -new -newkey rsa:2048 -nodes -keyout server.key -out server.csr -subj '/CN=OpenVPN-Server' \
    && openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 3650

# 创建凭证文件
RUN printf "%s\n" "${VPN_USER:-vpnuser} ${VPN_PASS:-vpnpass}" > /etc/openvpn/psw-file \
    && chmod 600 /etc/openvpn/psw-file

ENV COMPANY=ACME_CORP \
    ROLE=vpn \
    HOST_TYPE=VPN \
    VPN_USER=vpnuser \
    VPN_PASS=vpnpass

WORKDIR /opt/vpn
COPY server.conf ./
# 修改服务器配置，添加证书和密钥路径
RUN sed -i 's|/usr/lib/openvpn/openvpn-plugin-auth-pam.so|/usr/lib/x86_64-linux-gnu/openvpn/plugins/openvpn-plugin-auth-pam.so|g' /opt/vpn/server.conf \
    && echo "dh /etc/openvpn/dh2048.pem" >> /opt/vpn/server.conf \
    && echo "ca /etc/openvpn/easy-rsa/ca.crt" >> /opt/vpn/server.conf \
    && echo "cert /etc/openvpn/easy-rsa/server.crt" >> /opt/vpn/server.conf \
    && echo "key /etc/openvpn/easy-rsa/server.key" >> /opt/vpn/server.conf

COPY start.sh ./
RUN chmod +x start.sh

# 管理接口 7505 / HTTP 8000 / 数据通道 1194
EXPOSE 1194/udp 7505/tcp 8000

CMD ["./start.sh"]