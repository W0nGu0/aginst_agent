#!/usr/bin/env python3
"""
HIS (Hospital Information System) - 医院信息系统
包含预设漏洞用于APT攻击演示
"""

from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
import psycopg2
import json
import datetime
import os
import hashlib
import random

app = Flask(__name__)
app.secret_key = 'his_secret_key_123'  # 预设漏洞：弱密钥

# 数据库连接配置
DB_CONFIG = {
    'host': 'medical-database',
    'port': 5432,
    'database': 'medical_db',
    'user': 'med_admin',
    'password': 'MedDB2024!'
}

# 预设用户账户（包含弱密码）
USERS = {
    'admin': {'password': 'admin123', 'role': 'admin', 'department': 'IT'},
    'dr_zhang': {'password': 'Doctor123!', 'role': 'doctor', 'department': '内科'},
    'nurse_wang': {'password': 'Nurse2024', 'role': 'nurse', 'department': '急诊科'},
    'pharmacist': {'password': 'pharmacy123', 'role': 'pharmacist', 'department': '药房'}
}

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def index():
    """HIS系统主页"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ hospital_name }} - HIS系统</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { background: #2c5aa0; color: white; padding: 15px; margin: -20px -20px 20px -20px; }
            .nav { background: #34495e; padding: 10px; margin: 0 -20px 20px -20px; }
            .nav a { color: white; text-decoration: none; margin-right: 20px; }
            .module { background: white; padding: 20px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .user-info { float: right; color: white; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{{ hospital_name }} - 医院信息系统</h1>
            <div class="user-info">
                欢迎，{{ user.role }} {{ user.username }} ({{ user.department }})
                <a href="/logout" style="color: #fff; margin-left: 20px;">退出</a>
            </div>
        </div>
        
        <div class="nav">
            <a href="/patients">患者管理</a>
            <a href="/medical_records">病历管理</a>
            <a href="/billing">费用管理</a>
            <a href="/pharmacy">药房管理</a>
            <a href="/reports">报表统计</a>
            {% if user.role == 'admin' %}
            <a href="/admin">系统管理</a>
            {% endif %}
        </div>
        
        <div class="module">
            <h3>系统概览</h3>
            <p>当前在线用户：{{ online_users }}</p>
            <p>今日门诊量：{{ daily_patients }}</p>
            <p>系统版本：HIS v2.4.1</p>
            <p>数据库状态：{{ db_status }}</p>
        </div>
        
        <div class="module">
            <h3>快速操作</h3>
            <button onclick="location.href='/patients/new'">新增患者</button>
            <button onclick="location.href='/medical_records/new'">创建病历</button>
            <button onclick="location.href='/billing/new'">费用录入</button>
        </div>
    </body>
    </html>
    """, 
    hospital_name=os.getenv('HOSPITAL_NAME', '中心医院'),
    user=session['user'],
    online_users=random.randint(15, 30),
    daily_patients=random.randint(200, 500),
    db_status="正常" if get_db_connection() else "连接异常"
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 预设漏洞：简单的用户验证，容易被绕过
        if username in USERS and USERS[username]['password'] == password:
            session['user'] = {
                'username': username,
                'role': USERS[username]['role'],
                'department': USERS[username]['department']
            }
            return redirect(url_for('index'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error="用户名或密码错误")
    
    return render_template_string(LOGIN_TEMPLATE)

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>HIS系统登录</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f0f0f0; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 300px; }
        .form-group { margin: 15px 0; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { width: 100%; padding: 12px; background: #2c5aa0; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .error { color: red; margin: 10px 0; }
        .demo-accounts { margin-top: 20px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>HIS系统登录</h2>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="post">
            <div class="form-group">
                <input type="text" name="username" placeholder="用户名" required>
            </div>
            <div class="form-group">
                <input type="password" name="password" placeholder="密码" required>
            </div>
            <button type="submit">登录</button>
        </form>
        
        <div class="demo-accounts">
            <strong>演示账户：</strong><br>
            管理员: admin / admin123<br>
            医生: dr_zhang / Doctor123!<br>
            护士: nurse_wang / Nurse2024
        </div>
    </div>
</body>
</html>
"""

@app.route('/patients')
def patients():
    """患者管理页面"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # 预设漏洞：SQL注入
    search = request.args.get('search', '')
    if search:
        # 危险的SQL查询构造
        query = f"SELECT * FROM patients WHERE name LIKE '%{search}%' OR id_card LIKE '%{search}%'"
        # 这里应该使用参数化查询，但故意留下SQL注入漏洞
    
    return render_template_string("""
    <h1>患者管理</h1>
    <form method="get">
        <input type="text" name="search" placeholder="搜索患者姓名或身份证" value="{{ search }}">
        <button type="submit">搜索</button>
    </form>
    
    {% if search %}
    <p>搜索SQL: {{ query }}</p>
    <div style="color: red;">注意：此处存在SQL注入漏洞用于演示</div>
    {% endif %}
    
    <table border="1">
        <tr><th>患者ID</th><th>姓名</th><th>身份证</th><th>电话</th><th>科室</th></tr>
        {% for patient in patients %}
        <tr>
            <td>{{ patient.id }}</td>
            <td>{{ patient.name }}</td>
            <td>{{ patient.id_card }}</td>
            <td>{{ patient.phone }}</td>
            <td>{{ patient.department }}</td>
        </tr>
        {% endfor %}
    </table>
    
    <a href="/">返回主页</a>
    """, 
    search=search, 
    query=query if search else '',
    patients=[
        {'id': 'P001', 'name': '张三', 'id_card': '110101199001011234', 'phone': '13800138001', 'department': '内科'},
        {'id': 'P002', 'name': '李四', 'id_card': '110101199002022345', 'phone': '13800138002', 'department': '外科'},
        {'id': 'P003', 'name': '王五', 'id_card': '110101199003033456', 'phone': '13800138003', 'department': '儿科'}
    ]
    )

@app.route('/admin')
def admin():
    """系统管理页面"""
    if 'user' not in session or session['user']['role'] != 'admin':
        return "权限不足", 403
    
    return render_template_string("""
    <h1>系统管理</h1>
    <h3>数据库配置</h3>
    <p>主机: {{ db_host }}</p>
    <p>端口: {{ db_port }}</p>
    <p>数据库: {{ db_name }}</p>
    <p>用户: {{ db_user }}</p>
    <p>密码: {{ db_password }}</p>
    
    <h3>系统用户</h3>
    {% for username, info in users.items() %}
    <p>{{ username }} - {{ info.role }} - 密码: {{ info.password }}</p>
    {% endfor %}
    
    <a href="/">返回主页</a>
    """,
    db_host=DB_CONFIG['host'],
    db_port=DB_CONFIG['port'],
    db_name=DB_CONFIG['database'],
    db_user=DB_CONFIG['user'],
    db_password=DB_CONFIG['password'],  # 预设漏洞：密码明文显示
    users=USERS
    )

@app.route('/logout')
def logout():
    """退出登录"""
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)  # 预设漏洞：debug模式开启
