from flask import Flask, request, jsonify
import os
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("victim-host")

app = Flask(__name__)

# 从环境变量获取配置
COMPANY = os.getenv("COMPANY", "ACME_CORP")
USERNAME = os.getenv("USERNAME", "john.doe")
PASSWORD = os.getenv("PASSWORD", "User@123")
ROLE = os.getenv("ROLE", "developer")
DEPARTMENT = os.getenv("DEPARTMENT", "研发部")
EMAIL = os.getenv("EMAIL", f"{USERNAME}@{COMPANY.lower().replace(' ', '')}.com")
POSITION = os.getenv("POSITION", "工程师")
OS_INFO = os.getenv("OS", "Ubuntu 20.04 LTS")
KERNEL = os.getenv("KERNEL", "5.4.0-42-generic")
HOST_TYPE = os.getenv("HOST_TYPE", "WS-UBUNTU")

@app.route("/metadata", methods=["GET"])
def get_metadata():
    """
    暴露一些可供侦察的元数据，模拟一个配置不当或信息泄露的端点。
    """
    metadata = {
        "company_name": COMPANY,
        "username": USERNAME,
        "department": DEPARTMENT,
        "role": ROLE,
        "email": EMAIL,
        "position": POSITION,
        "system_info": OS_INFO,
        "kernel": KERNEL,
        "host_type": HOST_TYPE,
        "server": "Apache/2.4.41 (Ubuntu)",
        "open_ports": [22, 80, 443]
    }
    
    logger.info(f"元数据请求: 返回 {metadata}")
    return jsonify(metadata)

@app.route("/email", methods=["POST"])
def email():
    """
    原始的邮件接收端点，保留向后兼容性。
    """
    data = request.get_json(silent=True) or {}
    sender_company = data.get("company")
    # 模拟用户查看邮件：若公司名匹配，则"上当"提交凭证
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

@app.route("/receive_email", methods=["POST"])
def receive_email():
    """
    接收钓鱼邮件，根据邮件内容与用户信息的匹配程度决定是否点击恶意链接。
    """
    try:
        email = request.get_json(silent=True) or {}
        logger.info(f"收到钓鱼邮件: {email}")
        
        # 计算匹配分数
        match_score = 0
        max_score = 4  # 最大可能分数
        
        # 检查公司名称匹配
        if email.get("company", "").lower() == COMPANY.lower():
            match_score += 1
            logger.info("公司名称匹配 (+1)")
        
        # 检查目标用户名匹配
        if email.get("target_name", "").lower() == USERNAME.lower():
            match_score += 1
            logger.info("用户名匹配 (+1)")
        
        # 检查部门匹配
        if email.get("department", "").lower() == DEPARTMENT.lower():
            match_score += 1
            logger.info("部门匹配 (+1)")
        
        # 检查职位匹配
        if email.get("role", "").lower() == ROLE.lower():
            match_score += 1
            logger.info("职位匹配 (+1)")
        
        # 计算成功率
        success_rate = match_score / max_score
        
        # 根据匹配分数决定是否点击恶意链接
        if success_rate >= 0.75:  # 如果匹配度超过75%，则点击链接
            logger.warning(
                f"钓鱼攻击成功！匹配分数: {match_score}/{max_score} ({success_rate*100:.0f}%). "
                f"模拟用户点击恶意链接: {email.get('malicious_link')}"
            )
            
            # 返回凭据信息
            return jsonify({
                "status": "compromised", 
                "detail": "凭据已发送给攻击者。", 
                "match_score": match_score,
                "max_score": max_score,
                "success_rate": f"{success_rate*100:.0f}%",
                "credentials": {
                    "username": USERNAME,
                    "password": PASSWORD,
                    "role": ROLE,
                    "department": DEPARTMENT
                }
            })
        else:
            logger.info(f"钓鱼攻击失败。匹配分数: {match_score}/{max_score} ({success_rate*100:.0f}%)。邮件被忽略。")
            return jsonify({
                "status": "ignored", 
                "detail": "邮件与受害者信息匹配度不足。", 
                "match_score": match_score,
                "max_score": max_score,
                "success_rate": f"{success_rate*100:.0f}%"
            })
    except Exception as e:
        logger.error(f"处理钓鱼邮件时出错: {e}")
        return jsonify({"status": "error", "detail": str(e)}), 500

@app.route("/receive_social", methods=["POST"])
def receive_social():
    """
    接收社会工程学攻击载荷。
    """
    try:
        payload = request.get_json(silent=True) or {}
        logger.warning(f"收到社会工程学攻击载荷: {payload}")
        
        # 简单返回确认信息
        return jsonify({"status": "received", "tactic": payload.get("tactic")})
    except Exception as e:
        logger.error(f"处理社会工程学攻击载荷时出错: {e}")
        return jsonify({"status": "error", "detail": str(e)}), 500

if __name__ == "__main__":
    # Debug=true 故意开启 RCE 风险
    app.run(host="0.0.0.0", port=5000, debug=True)