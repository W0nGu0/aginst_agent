#!/usr/bin/env python3
# LIS服务器 - HL7接口和实验室数据处理
import socket
import threading
import sqlite3
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

class LISServer:
    def __init__(self, port=502):
        self.port = port
        self.running = False
        self.db_path = '/var/lis/lis.db'
        
    def start_hl7_server(self):
        """启动HL7接口服务器"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', self.port))
            server_socket.listen(5)
            
            print(f"HL7服务器启动在端口 {self.port}")
            
            while self.running:
                try:
                    client_socket, addr = server_socket.accept()
                    print(f"HL7连接来自: {addr}")
                    
                    # 接收HL7消息
                    data = client_socket.recv(1024).decode('utf-8')
                    if data:
                        self.process_hl7_message(data)
                    
                    # 发送ACK响应
                    ack = "MSH|^~\\&|LIS|HOSPITAL|SENDER|HOSPITAL|" + time.strftime("%Y%m%d%H%M%S") + "||ACK|" + str(int(time.time())) + "|P|2.5\rMSA|AA|12345"
                    client_socket.send(ack.encode('utf-8'))
                    client_socket.close()
                    
                except Exception as e:
                    print(f"HL7连接错误: {e}")
                    
        except Exception as e:
            print(f"HL7服务器启动失败: {e}")
    
    def process_hl7_message(self, message):
        """处理HL7消息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 简单的HL7消息解析
            lines = message.split('\r')
            message_type = "UNKNOWN"
            patient_id = "UNKNOWN"
            
            for line in lines:
                if line.startswith('MSH'):
                    parts = line.split('|')
                    if len(parts) > 8:
                        message_type = parts[8]
                elif line.startswith('PID'):
                    parts = line.split('|')
                    if len(parts) > 3:
                        patient_id = parts[3]
            
            # 存储HL7消息
            cursor.execute("""
                INSERT INTO hl7_messages (message_type, message_content, patient_id, status)
                VALUES (?, ?, ?, 'processed')
            """, (message_type, message, patient_id))
            
            conn.commit()
            conn.close()
            
            print(f"处理HL7消息: {message_type} for patient {patient_id}")
            
        except Exception as e:
            print(f"HL7消息处理错误: {e}")
    
    def start(self):
        self.running = True
        hl7_thread = threading.Thread(target=self.start_hl7_server)
        hl7_thread.daemon = True
        hl7_thread.start()

# Flask API接口
@app.route('/api/results', methods=['GET'])
def get_results():
    """获取检验结果"""
    patient_id = request.args.get('patient_id', '')
    
    conn = sqlite3.connect('/var/lis/lis.db')
    cursor = conn.cursor()
    
    if patient_id:
        # 预设漏洞：SQL注入
        query = f"SELECT * FROM lab_results WHERE patient_id = '{patient_id}'"
    else:
        query = "SELECT * FROM lab_results LIMIT 10"
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    return jsonify({"results": results})

@app.route('/api/upload_result', methods=['POST'])
def upload_result():
    """上传检验结果 - 包含预设漏洞"""
    data = request.json
    
    # 预设漏洞：不验证输入数据
    patient_id = data.get('patient_id')
    test_name = data.get('test_name')
    result_value = data.get('result_value')
    
    conn = sqlite3.connect('/var/lis/lis.db')
    cursor = conn.cursor()
    
    # 预设漏洞：SQL注入
    query = f"""
        INSERT INTO lab_results (patient_id, test_name, result_value, test_date)
        VALUES ('{patient_id}', '{test_name}', '{result_value}', datetime('now'))
    """
    
    try:
        cursor.execute(query)
        conn.commit()
        conn.close()
        return jsonify({"message": "结果上传成功"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置信息 - 预设漏洞：暴露敏感配置"""
    config = {
        "database_path": "/var/lis/lis.db",
        "hl7_port": 502,
        "admin_password": "lis123",  # 漏洞：密码暴露
        "database_key": "lis_db_secret_key",  # 漏洞：数据库密钥暴露
        "api_token": "lis_api_token_12345"  # 漏洞：API令牌暴露
    }
    return jsonify(config)

if __name__ == '__main__':
    # 启动LIS HL7服务器
    lis = LISServer()
    lis.start()
    
    print("启动LIS Web API服务器...")
    
    # 启动Flask Web服务器
    app.run(host='0.0.0.0', port=5001, debug=True)
