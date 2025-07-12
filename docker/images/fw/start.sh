#!/bin/bash
set -e

echo 1 > /proc/sys/net/ipv4/ip_forward

# 容器启动时可导入默认 iptables 规则，如需更严格可编辑 /etc/iptables/rules.v4
if [ -f /etc/iptables/rules.v4 ]; then
  iptables-restore < /etc/iptables/rules.v4
fi

# 进入 sleep 以保持容器运行
sleep infinity 