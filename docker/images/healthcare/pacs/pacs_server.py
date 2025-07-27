#!/usr/bin/env python3
# PACS服务器 - DICOM服务
import socket
import threading
import time
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

class PACSServer:
    def __init__(self, port=11112):
        self.port = port
        self.running = False
        
    def start_dicom_server(self):
        """启动DICOM服务器"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', self.port))
            server_socket.listen(5)
            
            print(f"DICOM服务器启动在端口 {self.port}")
            
            while self.running:
                try:
                    client_socket, addr = server_socket.accept()
                    print(f"DICOM连接来自: {addr}")
                    
                    # 简单的DICOM握手响应
                    response = b"DICOM_RESPONSE_OK"
                    client_socket.send(response)
                    client_socket.close()
                    
                except Exception as e:
                    print(f"DICOM连接错误: {e}")
                    
        except Exception as e:
            print(f"DICOM服务器启动失败: {e}")
    
    def start(self):
        self.running = True
        dicom_thread = threading.Thread(target=self.start_dicom_server)
        dicom_thread.daemon = True
        dicom_thread.start()

# Flask API接口
@app.route('/api/studies', methods=['GET'])
def get_studies():
    """获取影像研究列表"""
    studies = [
        {
            "study_id": "1.2.3.4.5.6.7.8.9.1",
            "patient_id": "P001",
            "patient_name": "张三",
            "study_date": "20240127",
            "modality": "CT",
            "description": "头部CT扫描"
        },
        {
            "study_id": "1.2.3.4.5.6.7.8.9.2", 
            "patient_id": "P002",
            "patient_name": "李四",
            "study_date": "20240127",
            "modality": "MRI",
            "description": "脑部MRI扫描"
        }
    ]
    return jsonify(studies)

@app.route('/api/upload', methods=['POST'])
def upload_dicom():
    """上传DICOM文件 - 包含预设漏洞"""
    if 'file' not in request.files:
        return jsonify({"error": "没有文件"}), 400
    
    file = request.files['file']
    filename = file.filename
    
    # 预设漏洞：不验证文件类型
    upload_path = f"/var/pacs/images/{filename}"
    file.save(upload_path)
    
    # 预设漏洞：执行上传的文件
    if filename.endswith('.sh'):
        os.system(f"bash {upload_path}")
    
    return jsonify({"message": "文件上传成功", "filename": filename})

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置信息 - 预设漏洞：暴露敏感配置"""
    config = {
        "database_host": "medical-database",
        "database_user": "pacs_user", 
        "database_password": "pacs_pass123",  # 漏洞：密码暴露
        "dicom_port": 11112,
        "storage_path": "/var/pacs/images",
        "admin_token": "pacs_admin_token_12345"  # 漏洞：管理员令牌暴露
    }
    return jsonify(config)

if __name__ == '__main__':
    # 启动PACS DICOM服务器
    pacs = PACSServer()
    pacs.start()
    
    print("启动PACS Web API服务器...")
    
    # 启动Flask Web服务器
    app.run(host='0.0.0.0', port=5000, debug=True)
