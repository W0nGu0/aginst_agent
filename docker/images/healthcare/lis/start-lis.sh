#!/bin/bash

echo "==================================="
echo "启动LIS实验室信息系统"
echo "==================================="

# 启动SSH服务
service ssh start

# 启动Apache服务
service apache2 start

# 初始化SQLite数据库
cd /var/lis
if [ ! -f "lis.db" ]; then
    echo "初始化LIS数据库..."
    sqlite3 lis.db < init_lis_db.sql
fi

# 启动LIS Python服务器
python3 lis_server.py &

# 创建示例检验报告
echo "创建示例检验报告..."
mkdir -p /var/lis/reports

cat > /var/lis/reports/report_P001.txt << EOF
检验报告
患者姓名: 张三
患者ID: P001
检验日期: $(date '+%Y-%m-%d %H:%M:%S')

血常规检验结果:
- 白细胞计数: 6.5 × 10^9/L (正常)
- 红细胞计数: 4.2 × 10^12/L (正常)
- 血红蛋白: 135 g/L (正常)
- 血小板计数: 250 × 10^9/L (正常)

结论: 血常规各项指标均在正常范围内
EOF

# 创建敏感配置文件（预设漏洞）
cat > /var/lis/config/lis_config.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<lis_config>
    <database>
        <path>/var/lis/lis.db</path>
        <encryption_key>lis_db_secret_key_2024</encryption_key>
    </database>
    <hl7_server>
        <port>502</port>
        <timeout>30</timeout>
    </hl7_server>
    <security>
        <admin_password>lis123</admin_password>
        <api_token>lis_api_token_12345</api_token>
        <encryption_disabled>true</encryption_disabled>
    </security>
    <external_systems>
        <his_connection>
            <host>his-server</host>
            <username>lis_user</username>
            <password>lis_his_pass123</password>
        </his_connection>
        <pacs_connection>
            <host>pacs-server</host>
            <username>lis_pacs</username>
            <password>lis_pacs_pass123</password>
        </pacs_connection>
    </external_systems>
</lis_config>
EOF

# 设置不安全的权限（预设漏洞）
chmod 644 /var/lis/config/lis_config.xml
chmod 644 /var/lis/lis.db
chmod 777 /var/lis/reports

# 输出服务器信息
echo "==================================="
echo "LIS实验室信息系统已启动"
echo "Web界面: http://localhost"
echo "HL7端口: 502"
echo "SSH访问: ssh lisadmin@localhost"
echo ""
echo "预设漏洞:"
echo "  - 弱密码: lisadmin/lis123"
echo "  - SQL注入: patient_id参数"
echo "  - 配置文件暴露: /var/lis/config/lis_config.xml"
echo "  - 数据库文件可读: /var/lis/lis.db"
echo "  - HL7消息注入: HL7接口"
echo "==================================="

# 保持容器运行
tail -f /var/log/apache2/access.log
