#!/bin/bash

echo "==================================="
echo "启动PACS医学影像系统"
echo "==================================="

# 启动SSH服务
service ssh start

# 启动Apache服务
service apache2 start

# 启动PACS Python服务器
cd /var/pacs
python3 pacs_server.py &

# 创建示例DICOM文件
echo "创建示例DICOM文件..."
mkdir -p /var/pacs/images/samples

# 创建示例配置文件（包含敏感信息）
cat > /var/pacs/config/pacs_config.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<pacs_config>
    <database>
        <host>medical-database</host>
        <port>5432</port>
        <username>pacs_user</username>
        <password>pacs_pass123</password>
        <database>pacs_db</database>
    </database>
    <dicom_server>
        <ae_title>HOSPITAL_PACS</ae_title>
        <port>11112</port>
        <storage_path>/var/pacs/images</storage_path>
    </dicom_server>
    <security>
        <encryption_key>pacs_secret_key_2024</encryption_key>
        <admin_token>admin_token_12345</admin_token>
    </security>
</pacs_config>
EOF

# 创建示例患者数据
cat > /var/pacs/images/patient_list.txt << EOF
患者001,张三,110101199001011234,CT头部扫描
患者002,李四,110101199002021235,MRI脑部扫描
患者003,王五,110101199003031236,X光胸部
患者004,赵六,110101199004041237,超声腹部
EOF

# 设置不安全的权限（预设漏洞）
chmod 644 /var/pacs/config/pacs_config.xml
chmod 644 /var/pacs/images/patient_list.txt
chmod 777 /var/pacs/temp

# 输出服务器信息
echo "==================================="
echo "PACS医学影像系统已启动"
echo "Web界面: http://localhost"
echo "DICOM端口: 11112"
echo "SSH访问: ssh pacsadmin@localhost"
echo ""
echo "预设漏洞:"
echo "  - 弱密码: pacsadmin/pacs123"
echo "  - 目录遍历: ?image=../config/pacs_config.xml"
echo "  - SQL注入: patient_id参数"
echo "  - 文件权限: 配置文件可读"
echo "  - 未授权访问: DICOM服务器"
echo "==================================="

# 保持容器运行
tail -f /var/log/apache2/access.log
