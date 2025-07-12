#!/bin/bash
set -e

# 创建弱凭证文件
printf "%s\n" "${VPN_USER} ${VPN_PASS}" > /etc/openvpn/psw-file
chmod 600 /etc/openvpn/psw-file

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

# 启动 OpenVPN 服务器
openvpn --config /opt/vpn/server.conf --auth-user-pass-verify "/bin/cat /etc/openvpn/psw-file" via-env &

# 用 Python 暴露 /opt/share 目录，方便攻击者下载 ovpn
cd /opt/share && python3 -m http.server 8000 &

# 阻塞，保持容器活跃
wait -n 