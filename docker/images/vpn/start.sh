#!/bin/bash
set -e

echo "Starting VPN container..."

# 确保 TUN 设备存在
if [ ! -c /dev/net/tun ]; then
    mkdir -p /dev/net
    mknod /dev/net/tun c 10 200
    chmod 600 /dev/net/tun
fi
echo "TUN device ready"

# 确保凭证文件存在
mkdir -p /etc/openvpn
printf "%s\n" "${VPN_USER:-vpnuser} ${VPN_PASS:-vpnpass}" > /etc/openvpn/psw-file
chmod 600 /etc/openvpn/psw-file
echo "Credentials file ready"

# 生成易泄漏客户端配置并放到共享目录
mkdir -p /opt/share
cat > /opt/share/acme_vpn.ovpn <<EOF
client
dev tun
proto udp
remote 127.0.0.1 1194
resolv-retry infinite
nobind
cipher DES-CBC
verb 3
auth-user-pass
EOF
echo "Client config ready"

# 启动 OpenVPN 服务器
echo "Starting OpenVPN server..."
openvpn --config /opt/vpn/server.conf --auth-user-pass-verify "/bin/cat /etc/openvpn/psw-file" via-env &
OPENVPN_PID=$!
echo "OpenVPN server started with PID: $OPENVPN_PID"

# 用 Python 暴露 /opt/share 目录，方便攻击者下载 ovpn
echo "Starting HTTP server..."
cd /opt/share && python3 -m http.server 8000 &
HTTP_PID=$!
echo "HTTP server started with PID: $HTTP_PID"

# 创建日志文件
touch /var/log/openvpn.log
touch /var/log/openvpn-status.log

echo "VPN container startup complete"

# 阻塞，保持容器活跃
wait -n $OPENVPN_PID $HTTP_PID
# 如果任何一个进程退出，重新启动它
while true; do
    if ! kill -0 $OPENVPN_PID 2>/dev/null; then
        echo "OpenVPN process died, restarting..."
        openvpn --config /opt/vpn/server.conf --auth-user-pass-verify "/bin/cat /etc/openvpn/psw-file" via-env &
        OPENVPN_PID=$!
    fi
    
    if ! kill -0 $HTTP_PID 2>/dev/null; then
        echo "HTTP server died, restarting..."
        cd /opt/share && python3 -m http.server 8000 &
        HTTP_PID=$!
    fi
    
    sleep 10
done