#!/usr/bin/env python3
# API网关服务器 - 包含预设漏洞
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import requests
import json
import jwt
import time
import os

app = Flask(__name__)
CORS(app)  # 预设漏洞：允许所有跨域请求

# 预设漏洞：硬编码密钥
JWT_SECRET = "api_gateway_secret_key_12345"
API_KEYS = {
    "internal_api": "med_api_key_12345_secret",
    "external_service": "ext_service_token_abcdef",
    "admin_api": "admin_api_super_secret_key"
}

# 预设漏洞：弱认证
VALID_USERS = {
    "apiadmin": "api@2024",
    "developer": "dev123",
    "service": "service123"
}

@app.route('/')
def index():
    return jsonify({
        "service": "API Gateway",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/auth/login",
            "/api/proxy/<service>",
            "/admin/config",
            "/health"
        ]
    })

@app.route('/auth/login', methods=['POST'])
def login():
    """用户认证 - 包含预设漏洞"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # 预设漏洞：弱密码验证
    if username in VALID_USERS and VALID_USERS[username] == password:
        # 预设漏洞：JWT密钥硬编码
        token = jwt.encode({
            'username': username,
            'exp': time.time() + 3600,
            'role': 'admin' if username == 'apiadmin' else 'user'
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            "token": token,
            "username": username,
            "message": "登录成功"
        })
    else:
        return jsonify({"error": "用户名或密码错误"}), 401

@app.route('/api/proxy/<service>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy_request(service):
    """API代理 - 包含预设漏洞"""
    
    # 预设漏洞：不验证API密钥
    api_key = request.headers.get('X-API-Key', '')
    
    # 预设漏洞：SQL注入风险
    if 'sql' in request.args:
        query = request.args.get('sql')
        # 漏洞：直接执行SQL查询
        return jsonify({"query": query, "warning": "SQL注入风险"})
    
    # 预设漏洞：SSRF风险
    target_url = request.args.get('url')
    if target_url:
        try:
            # 漏洞：没有URL验证，可能导致SSRF
            response = requests.get(target_url, timeout=5)
            return jsonify({
                "url": target_url,
                "status": response.status_code,
                "content": response.text[:1000]
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # 服务路由配置
    service_routes = {
        "his": "http://his-server:80",
        "pacs": "http://pacs-server:80", 
        "lis": "http://lis-server:80",
        "medical-db": "http://medical-database:5432"
    }
    
    if service not in service_routes:
        return jsonify({"error": "服务不存在"}), 404
    
    # 转发请求
    target_url = service_routes[service] + request.path.replace(f'/api/proxy/{service}', '')
    
    try:
        if request.method == 'GET':
            response = requests.get(target_url, params=request.args, timeout=10)
        elif request.method == 'POST':
            response = requests.post(target_url, json=request.get_json(), timeout=10)
        else:
            return jsonify({"error": "不支持的HTTP方法"}), 405
            
        return jsonify(response.json()) if response.headers.get('content-type', '').startswith('application/json') else response.text
        
    except Exception as e:
        return jsonify({"error": f"代理请求失败: {str(e)}"}), 500

@app.route('/admin/config', methods=['GET'])
def get_config():
    """获取配置信息 - 预设漏洞：暴露敏感配置"""
    
    # 预设漏洞：不验证管理员权限
    config = {
        "database": {
            "host": "medical-database",
            "username": "api_gateway_user",
            "password": "gateway_db_pass_123"  # 漏洞：密码暴露
        },
        "api_keys": API_KEYS,  # 漏洞：API密钥暴露
        "jwt_secret": JWT_SECRET,  # 漏洞：JWT密钥暴露
        "services": {
            "his_endpoint": "http://his-server:80",
            "pacs_endpoint": "http://pacs-server:80",
            "lis_endpoint": "http://lis-server:80"
        },
        "security": {
            "cors_enabled": True,
            "rate_limiting": False,  # 漏洞：未启用速率限制
            "input_validation": False,  # 漏洞：未启用输入验证
            "ssl_verification": False  # 漏洞：未启用SSL验证
        }
    }
    
    return jsonify(config)

@app.route('/admin/users', methods=['GET'])
def get_users():
    """获取用户列表 - 预设漏洞：暴露用户信息"""
    users = []
    for username, password in VALID_USERS.items():
        users.append({
            "username": username,
            "password": password,  # 漏洞：密码暴露
            "role": "admin" if username == "apiadmin" else "user",
            "last_login": "2024-01-27 12:00:00"
        })
    
    return jsonify({"users": users})

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "uptime": "24h",
        "memory_usage": "256MB",
        "cpu_usage": "15%"
    })

@app.route('/debug', methods=['GET'])
def debug_info():
    """调试信息 - 预设漏洞：暴露系统信息"""
    import platform
    import psutil
    
    debug_data = {
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "hostname": platform.node()
        },
        "environment": dict(os.environ),  # 漏洞：暴露环境变量
        "process": {
            "pid": os.getpid(),
            "memory": psutil.Process().memory_info()._asdict() if 'psutil' in globals() else "N/A"
        },
        "request_headers": dict(request.headers),
        "flask_config": {
            "DEBUG": app.debug,
            "SECRET_KEY": app.secret_key
        }
    }
    
    return jsonify(debug_data)

if __name__ == '__main__':
    print("启动API网关服务器...")
    print("预设漏洞:")
    print("  - 弱密码: apiadmin/api@2024")
    print("  - 硬编码密钥: JWT和API密钥")
    print("  - CORS漏洞: 允许所有跨域请求")
    print("  - SSRF漏洞: URL参数未验证")
    print("  - 信息泄露: 配置和调试接口")
    print("  - SQL注入: sql参数未过滤")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
