#!/bin/bash

# 启动SSH服务
service ssh start

# 启动Apache服务
service apache2 start

# 创建一些示例文件
echo "<?php echo 'Database config: host=localhost, user=admin, pass=secret123'; ?>" > /var/updates/config/config.php
echo "Update package v1.0" > /var/updates/packages/update_v1.0.zip
echo "Critical security patch" > /var/updates/packages/security_patch.exe

# 设置权限（故意设置不安全的权限作为漏洞）
chmod 777 /var/updates/packages
chmod 644 /var/updates/config/config.php

# 输出服务器信息
echo "==================================="
echo "软件更新服务器已启动"
echo "Web界面: http://localhost"
echo "SSH访问: ssh updateadmin@localhost"
echo "预设漏洞:"
echo "  - 弱密码: updateadmin/update123"
echo "  - 目录遍历: ?file=../config/config.php"
echo "  - 代码注入: 更新脚本执行功能"
echo "  - 文件上传: upload.php"
echo "==================================="

# 保持容器运行
tail -f /var/log/apache2/access.log
