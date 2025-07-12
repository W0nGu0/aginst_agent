from flask import Flask, request, jsonify
import os

app = Flask(__name__)

COMPANY = os.getenv("COMPANY", "ACME_CORP")
USERNAME = os.getenv("USERNAME", "john.doe")
PASSWORD = os.getenv("PASSWORD", "User@123")
ROLE = os.getenv("ROLE", "developer")

@app.route("/email", methods=["POST"])
def receive_email():
    """接收钓鱼邮件 JSON 数据，字段示例：{"company": "ACME_CORP", "link": "http://evil/phish"}"""
    data = request.get_json(silent=True) or {}
    sender_company = data.get("company")
    # 模拟用户查看邮件：若公司名匹配，则“上当”提交凭证
    if sender_company and sender_company.lower() == COMPANY.lower():
        response = {
            "username": USERNAME,
            "password": PASSWORD,
            "role": ROLE,
            "host": os.getenv("HOST_TYPE", "WS-UBUNTU")
        }
        return jsonify(response), 200
    # 否则忽略
    return jsonify({"status": "ignored"}), 202

if __name__ == "__main__":
    # Debug=true 故意开启 RCE 风险
    app.run(host="0.0.0.0", port=5000, debug=True) 