import subprocess
from fastmcp import FastMCP
import random
import httpx
import json
import uuid

# 1. Create a FastMCP server instance
mcp = FastMCP(
    name="Attack Service"
)

# 2. Define a tool using the @mcp.tool decorator
@mcp.tool
def run_nmap(target_ip: str, options: str = "-T4 --top-ports 20") -> str:
    """
    Executes an Nmap scan against a target IP address.

    Args:
        target_ip: The IP address of the target to scan.
        options: The command-line options to pass to Nmap.

    Returns:
        The stdout from the Nmap command if successful.
    """
    command = ["nmap"] + options.split() + [target_ip]
    
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
            check=True
        )
        return process.stdout
    except FileNotFoundError:
        return "Error: nmap command not found. Make sure it's installed and in the system's PATH."
    except subprocess.CalledProcessError as e:
        return f"Error: Nmap scan failed with exit code {e.returncode}:\n{e.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Nmap scan timed out after 120 seconds."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

# ----------------------- Social Engineering Tools -----------------------
@mcp.tool
def fetch_url_content(url: str) -> str:
    """
    Fetches the content from a given URL.

    Args:
        url: The URL to fetch content from.

    Returns:
        The content of the URL if successful, otherwise an error message.
    """
    try:
        response = httpx.get(url, follow_redirects=True, timeout=10)
        response.raise_for_status()
        # 尝试解析为JSON，如果失败则返回原始文本
        try:
            # 修复：将json字典转换为字符串，以匹配工具的返回类型定义
            return json.dumps(response.json())
        except Exception:
            return response.text
    except httpx.RequestError as e:
        return f"Error: Failed to fetch URL {e.request.url}. Reason: {e}"
    except Exception as e:
        return f"An unexpected error occurred while fetching the URL: {str(e)}"

@mcp.tool
def craft_phishing_email(target_name: str, company: str, malicious_link: str, department: str = None, role: str = None, email: str = None) -> str:
    """
    生成一封针对特定目标的钓鱼邮件，根据目标的部门和角色定制内容
    
    Args:
        target_name: 目标人物姓名
        company: 目标公司名称
        malicious_link: 恶意链接
        department: 目标部门（可选）
        role: 目标职位（可选）
        email: 目标邮箱（可选）
    
    Returns:
        生成的钓鱼邮件内容
    """
    # 基本模板
    basic_templates = [
        ("薪资信息更新通知", "您好 {name}，\n\n您的{company}薪资信息需要更新。点击此处立即更新：\n{link}\n\n谢谢，\n{company}人力资源部"),
        ("账号异常登录活动", "亲爱的{name}，\n\n我们检测到您的{company}账号有异常登录活动。请点击以下链接验证您的身份：\n{link}\n\n此致,\n{company}安全团队"),
        ("年度安全审计确认", "{name}您好，\n\n作为年度安全审计的一部分，我们需要您确认您的凭据。请点击以下安全链接：\n{link}\n\n祝好，\n{company}IT技术支持")
    ]
    
    # 根据部门定制的模板
    department_templates = {
        "研发部": [
            ("代码审查邀请", "Hi {name}，\n\n您被邀请参与一个新项目的代码审查。请通过以下链接访问代码库：\n{link}\n\n感谢您的参与，\n{company}技术团队"),
            ("新开发工具许可证", "{name}，\n\n我们已为{department}购买了新的开发工具许可证。请点击以下链接激活您的账号：\n{link}\n\n祝编码愉快，\n{company}IT部门")
        ],
        "IT运维": [
            ("服务器异常警报", "紧急：{name}，\n\n我们检测到服务器异常。请立即查看监控报告：\n{link}\n\n请尽快处理，\n{company}监控系统"),
            ("系统更新通知", "管理员{name}，\n\n需要您批准系统更新。请登录管理控制台：\n{link}\n\n谢谢，\n{company}系统管理")
        ],
        "数据库管理": [
            ("数据库性能报告", "DBA {name}，\n\n请查看最新的数据库性能分析报告：\n{link}\n\n如有问题请及时处理，\n{company}监控团队"),
            ("数据库安全审计", "{name}，\n\n我们需要您确认最近的数据库安全审计结果。请点击查看详情：\n{link}\n\n谢谢，\n{company}安全团队")
        ],
        "网络安全": [
            ("安全漏洞通报", "{name}，\n\n我们发现了一个紧急安全漏洞。请查看详细报告并采取行动：\n{link}\n\n此致，\n{company}安全响应团队"),
            ("安全工具更新", "安全专家{name}，\n\n您使用的安全工具需要更新。请点击以下链接进行更新：\n{link}\n\n谢谢，\n{company}IT支持")
        ],
        "市场部": [
            ("营销活动数据", "{name}，\n\n最新的营销活动数据已经可以查看。请点击以下链接访问报告：\n{link}\n\n祝好，\n{company}数据分析团队"),
            ("品牌资产更新", "亲爱的{name}，\n\n我们更新了公司的品牌资产。请通过以下链接下载最新版本：\n{link}\n\n谢谢，\n{company}品牌团队")
        ]
    }
    
    # 根据角色定制的模板
    role_templates = {
        "管理员": [
            ("管理员权限确认", "{name}管理员，\n\n请确认您的管理员权限。点击以下链接验证：\n{link}\n\n谢谢，\n{company}系统管理"),
            ("管理控制台更新", "尊敬的{name}，\n\n管理控制台已更新。请使用以下链接登录新版本：\n{link}\n\n此致，\n{company}IT部门")
        ],
        "工程师": [
            ("技术文档更新", "{name}工程师，\n\n我们更新了技术文档。请通过以下链接访问：\n{link}\n\n祝工作顺利，\n{company}文档团队"),
            ("代码库访问", "Hi {name}，\n\n您已被授予新项目代码库的访问权限。请点击以下链接设置访问凭证：\n{link}\n\n谢谢，\n{company}开发团队")
        ],
        "开发": [
            ("API文档更新", "开发者{name}，\n\n我们更新了API文档。请查看最新版本：\n{link}\n\n祝编码愉快，\n{company}API团队"),
            ("开发环境配置", "{name}，\n\n请更新您的开发环境配置。详情请点击：\n{link}\n\n谢谢，\n{company}DevOps团队")
        ]
    }
    
    # 选择合适的模板
    selected_templates = basic_templates
    
    # 如果有部门信息，尝试使用部门特定模板
    if department and department in department_templates:
        selected_templates = department_templates[department]
    # 如果有角色信息，尝试使用角色特定模板
    elif role:
        for role_key in role_templates:
            if role_key.lower() in role.lower():
                selected_templates = role_templates[role_key]
                break
    
    # 随机选择一个模板
    subject, body = random.choice(selected_templates)
    
    # 格式化邮件内容
    email_body = body.format(
        name=target_name,
        company=company,
        department=department or "您的部门",
        role=role or "您的职位",
        link=malicious_link
    )
    
    # 构建更丰富的响应
    response = {
        "subject": subject,
        "body": email_body,
        "sender": f"{company} IT部门 <it@{company.lower().replace(' ', '')}.com>",
        "recipient": email or f"{target_name}@{company.lower().replace(' ', '')}.com",
        "malicious_link": malicious_link
    }
    
    # 返回格式化的响应
    return json.dumps(response)

@mcp.tool
def lookup_email_breach(domain: str) -> str:
    """模拟在公开泄露数据库中搜索指定域名"""
    breaches = [
        "LinkedIn 2012年泄露",
        "Adobe 2013年泄露",
        "Dropbox 2016年泄露",
    ]
    return f"发现{domain}域名在{len(breaches)}个公开泄露数据库中出现：" + "，".join(breaches)

@mcp.tool
def simulate_credential_harvest(username: str, password: str) -> str:
    # 防御性处理输入类型
    username = str(username or "").strip()
    password = str(password or "").strip()
    
    # 确保返回值为纯字符串（FastMCP会自动包装为JSON响应）
    if not username or not password:
        return "错误：用户名或密码为空"
    
    weak_passwords = {"password", "password123", "123456"}
    if password.lower() in weak_passwords:
        return "凭据收集成功！目标使用了弱密码。"
    return "凭据收集尝试已记录。密码强度较高。"

# ----------------------- Privilege Escalation & Lateral Movement (Simulated) -----------------------

# 为后续权限提升与横向移动增加一组简化工具，当前仅返回模拟数据，后续可接入真实 exploit 框架与 session 管理。

@mcp.tool
def search_exploit(service: str, version: str) -> str:
    """模拟搜索漏洞利用模块，返回一个 JSON 字符串，其中包含是否匹配以及 module_id。"""
    module_id = f"exploit_{service}_{version}".replace(" ", "_")
    return json.dumps({"matched": True, "module": module_id})


@mcp.tool
def execute_exploit_module(module: str, target: str) -> str:
    """模拟执行漏洞利用，成功后生成并返回 session_id。"""
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    return json.dumps({"status": "success", "session_id": session_id, "target": target})


@mcp.tool
def execute_shell_command(session_id: str, command: str) -> str:
    """模拟在受控主机上执行命令并返回输出结果。"""
    output = f"[{session_id}]$ {command}\n模拟输出：command executed successfully."
    return output


@mcp.tool
def get_network_info(session_id: str) -> str:
    """模拟收集当前主机可达的内网 IP，用于横向移动规划。"""
    hosts = ["10.0.0.5", "10.0.0.6"]
    return json.dumps({"session": session_id, "reachable_hosts": hosts})

# ----------------------- Social Engineering – New Tools -----------------------
# 说明：为了演示社会工程学攻击，这里实现 4 个轻量级工具，返回字符串即可被前端渲染。

import base64
from datetime import datetime

@mcp.tool
def send_payload_to_victim(victim_url: str, phishing_email_json: str) -> str:
    """
    将最终制作好的钓鱼邮件载荷，通过API发送给受害者。
    这是攻击流程的最后一步。
    
    参数:
    - victim_url: 受害者URL
    - phishing_email_json: 由craft_phishing_email工具生成的JSON格式钓鱼邮件内容
    """
    try:
        # 解析钓鱼邮件JSON
        try:
            email_data = json.loads(phishing_email_json)
        except json.JSONDecodeError:
            return f"错误：phishing_email_json 不是有效的JSON格式: {phishing_email_json}"
        
        # 构建发送给受害者的载荷
        victim_payload = {
            "company": email_data.get("sender", "").split("<")[0].strip() or email_data.get("company", "Unknown Company"),
            "malicious_link": email_data.get("malicious_link", "http://evil-corp-phishing.com/login"),
            "email_body": email_data.get("body", ""),
            "target_name": email_data.get("recipient", "").split("<")[0].strip() or email_data.get("target_name", ""),
            "subject": email_data.get("subject", "重要通知"),
            "department": email_data.get("department", "研发部"),  # 默认使用"研发部"
            "role": email_data.get("role", "软件工程师")  # 默认使用"软件工程师"
        }
        
        # 确保URL是完整的
        if not victim_url.endswith('/receive_email'):
            victim_url = victim_url.rstrip('/') + '/receive_email'
        
        # 发送请求到受害者主机
        with httpx.Client(timeout=20) as client:
            response = client.post(victim_url, json=victim_payload)
            response.raise_for_status()
            return f"成功将钓鱼邮件发送至 {victim_url}。\n\n邮件主题: {victim_payload['subject']}\n收件人: {victim_payload['target_name']}\n\n受害者响应: {response.json()}"
    except httpx.RequestError as e:
        return f"请求错误: {e}"
    except httpx.HTTPStatusError as e:
        return f"HTTP错误: {e.response.status_code} {e.response.text}"
    except Exception as e:
        return f"发送钓鱼邮件时出错: {str(e)}"

@mcp.tool
def craft_doc_with_enable_macro(victim_name: str) -> str:
    """生成一个诱导受害者启用宏的伪 Word 文档下载链接（Base64 Data URL 占位）。"""
    fake_doc = f"Enable Macro Payload for {victim_name} @ {datetime.utcnow().isoformat()}".encode()
    data_url = "data:application/vnd.ms-word;base64," + base64.b64encode(fake_doc).decode()
    return (
        f"已生成诱导启用宏的文档，受害者启用宏后将执行 VBA 恶意代码。\n"
        f"下载链接（占位）：{data_url}"
    )

@mcp.tool
def simulate_sextortion_email(victim_name: str, position: str) -> str:
    """生成性勒索邮件内容，威胁公开隐私并索要比特币赎金。"""
    btc_address = "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    return (
        f"亲爱的 {victim_name} ({position})，\n\n"
        "我们掌握了你的隐私影像，如果48小时内未支付 0.5 BTC 到下列地址，视频将被公开：\n"
        f"{btc_address}\n\n切勿尝试报警！"
    )

@mcp.tool
def craft_affinity_chat(common_interest: str, first_question: str = "能加个微信聊细节吗？") -> str:
    """基于共同爱好创建亲和聊天脚本。"""
    return (
        f"【开场】嗨！我也超喜欢{common_interest}，上周还去了线下活动。\n\n"
        f"【下一步】{first_question}"
    )

@mcp.tool
def craft_fake_job_offer(target_name: str, desired_role: str, salary_range: str, form_link: str) -> str:
    """伪造高薪猎头邮件引导受害者填写钓鱼表单。"""
    return (
        f"主题: {desired_role} – 年薪 {salary_range}（保密）\n\n"
        f"{target_name} 您好！我们正在为独角兽企业招募 {desired_role}。\n"
        f"请在24小时内填写表单确认意向：{form_link}\n\n期待回复！"
    )

@mcp.tool
def send_payload_to_victim_social(victim_url: str, payload: dict) -> str:
    """将社会工程学载荷 POST 至 /receive_social。"""
    try:
        if not victim_url.endswith("/receive_social"):
            victim_url = victim_url.rstrip("/") + "/receive_social"
        with httpx.Client(timeout=20) as client:
            resp = client.post(victim_url, json=payload)
            resp.raise_for_status()
            return f"已发送 tactic={payload.get('tactic', 'unknown')} 至 {victim_url}，受害者响应: {resp.json()}"
    except httpx.RequestError as e:
        return f"请求错误: {e}"
    except httpx.HTTPStatusError as e:
        return f"HTTP错误: {e.response.status_code} {e.response.text}"
    except Exception as e:
        return f"发送社会工程学载荷失败: {str(e)}"
# -----------------------------------------------------------------------------

# 3. Start the server
if __name__ == "__main__":
    print("\n--- Attack Service (v2 - with JSON string fix) is starting... ---\n")
    mcp.run(transport="http", port=8001)