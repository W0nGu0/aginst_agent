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
    output = f"[{session_id}]$ {command}\n结果输出：command executed successfully."
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
        print(f"[攻击服务] 开始执行钓鱼邮件发送操作，目标URL: {victim_url}")
        
        # 解析钓鱼邮件JSON
        try:
            email_data = json.loads(phishing_email_json)
            print(f"[攻击服务] 成功解析钓鱼邮件JSON: {email_data}")
        except json.JSONDecodeError:
            error_msg = f"错误：phishing_email_json 不是有效的JSON格式: {phishing_email_json}"
            print(f"[攻击服务] {error_msg}")
            return error_msg
        
        # 从URL中获取元数据，以便更准确地匹配目标信息
        try:
            print(f"[攻击服务] 正在获取目标元数据...")
            metadata_url = victim_url.rstrip('/') + '/metadata'
            metadata_response = httpx.get(metadata_url, timeout=10)
            metadata = metadata_response.json()
            
            # 提取目标信息
            target_department = metadata.get("department", "研发部")
            target_role = metadata.get("role", "软件工程师")
            target_name = metadata.get("username", "")
            target_email = metadata.get("email", "")
            company_name = metadata.get("company_name", "ACME_CORP")
            
            print(f"[攻击服务] 成功获取目标元数据: {metadata}")
            print(f"[攻击服务] 目标信息: 部门={target_department}, 职位={target_role}, 用户名={target_name}, 邮箱={target_email}, 公司={company_name}")
        except Exception as e:
            print(f"[攻击服务] 获取元数据失败，使用默认值: {e}")
            target_department = "研发部"
            target_role = "软件工程师"
            target_name = email_data.get("recipient", "").split("@")[0] if "@" in email_data.get("recipient", "") else ""
            target_email = email_data.get("recipient", "")
            company_name = email_data.get("company", "ACME_CORP")
            print(f"[攻击服务] 使用默认值: 部门={target_department}, 职位={target_role}, 用户名={target_name}, 邮箱={target_email}, 公司={company_name}")
        
        # 构建发送给受害者的载荷，确保包含所有匹配字段
        victim_payload = {
            "company": company_name,
            "malicious_link": email_data.get("malicious_link", "http://evil-corp-phishing.com/login"),
            "email_body": email_data.get("body", ""),
            "target_name": target_name,
            "subject": email_data.get("subject", "重要通知"),
            "department": target_department,
            "role": target_role,
            "email": target_email
        }
        
        print(f"[攻击服务] 构建的钓鱼邮件载荷: {victim_payload}")
        print(f"[攻击服务] 钓鱼邮件主题: {victim_payload['subject']}")
        print(f"[攻击服务] 钓鱼邮件目标: {victim_payload['target_name']} ({victim_payload['email']})")
        print(f"[攻击服务] 钓鱼邮件部门匹配: {victim_payload['department']}")
        print(f"[攻击服务] 钓鱼邮件职位匹配: {victim_payload['role']}")
        
        # 确保URL是完整的
        if not victim_url.endswith('/receive_email'):
            victim_url = victim_url.rstrip('/') + '/receive_email'
            print(f"[攻击服务] 调整目标URL为: {victim_url}")
        
        # 发送请求到受害者主机
        print(f"[攻击服务] 正在发送钓鱼邮件到目标主机...")
        with httpx.Client(timeout=20) as client:
            response = client.post(victim_url, json=victim_payload)
            response.raise_for_status()
            response_data = response.json()
            print(f"[攻击服务] 钓鱼邮件发送成功，受害者响应: {response_data}")
            
            # 分析响应结果
            match_score = response_data.get("match_score", 0)
            max_score = response_data.get("max_score", 4)
            success_rate = response_data.get("success_rate", "0%")
            status = response_data.get("status", "unknown")
            
            print(f"[攻击服务] 钓鱼邮件匹配分数: {match_score}/{max_score}")
            print(f"[攻击服务] 钓鱼邮件成功率: {success_rate}")
            print(f"[攻击服务] 钓鱼邮件状态: {status}")
            
            # 构建详细的响应信息
            result = f"成功将钓鱼邮件发送至 {victim_url}。\n\n"
            result += f"邮件主题: {victim_payload['subject']}\n"
            result += f"收件人: {victim_payload['target_name']} ({victim_payload['email']})\n"
            result += f"目标部门: {victim_payload['department']}\n"
            result += f"目标职位: {victim_payload['role']}\n\n"
            result += f"受害者响应: {response_data}\n\n"
            
            if status == "compromised":
                result += "攻击结果: 成功! 目标已点击恶意链接并提交凭据。"
            else:
                result += f"攻击结果: 失败。匹配度: {match_score}/{max_score} ({success_rate})。"
                result += "\n可能原因: 邮件内容与目标特征匹配度不足，或目标警惕性较高。"
            
            return result
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
# ----------------------- APT Attack Tools -----------------------
# APT攻击工具集，实现高级持续威胁的完整攻击链

import time
from typing import Dict, List, Optional

# APT攻击状态管理
apt_sessions = {}  # 存储APT攻击会话信息

@mcp.tool
def initiate_apt_campaign(target_organization: str, campaign_name: str, objectives: List[str] = None) -> str:
    """
    启动APT攻击活动，建立攻击会话和目标

    Args:
        target_organization: 目标组织名称
        campaign_name: 攻击活动名称
        objectives: 攻击目标列表（如：窃取数据、长期监控、破坏系统等）

    Returns:
        APT攻击活动ID和初始化信息
    """
    campaign_id = f"apt_{uuid.uuid4().hex[:8]}"

    if objectives is None:
        objectives = ["数据窃取", "长期监控", "权限维持"]

    apt_sessions[campaign_id] = {
        "campaign_id": campaign_id,
        "target_organization": target_organization,
        "campaign_name": campaign_name,
        "objectives": objectives,
        "start_time": datetime.utcnow().isoformat(),
        "phase": "初始侦察",
        "compromised_hosts": [],
        "collected_data": [],
        "persistence_mechanisms": [],
        "lateral_movement_paths": [],
        "stealth_level": "高",
        "status": "活跃"
    }

    result = {
        "campaign_id": campaign_id,
        "status": "APT攻击活动已启动",
        "target": target_organization,
        "phase": "初始侦察",
        "objectives": objectives,
        "stealth_level": "高"
    }

    return json.dumps(result)

@mcp.tool
def apt_reconnaissance(campaign_id: str, target_domain: str, reconnaissance_type: str = "passive") -> str:
    """
    执行APT侦察阶段，收集目标信息

    Args:
        campaign_id: APT攻击活动ID
        target_domain: 目标域名
        reconnaissance_type: 侦察类型（passive/active）

    Returns:
        侦察结果信息
    """
    if campaign_id not in apt_sessions:
        return json.dumps({"error": "无效的APT攻击活动ID"})

    session = apt_sessions[campaign_id]
    session["phase"] = "深度侦察"

    # 模拟侦察结果
    reconnaissance_data = {
        "domain_info": {
            "domain": target_domain,
            "subdomains": [f"mail.{target_domain}", f"vpn.{target_domain}", f"admin.{target_domain}"],
            "email_addresses": [f"admin@{target_domain}", f"support@{target_domain}"],
            "technologies": ["Apache", "PHP", "MySQL", "WordPress"]
        },
        "social_media": {
            "employees": ["张三 - CTO", "李四 - 安全工程师", "王五 - 系统管理员"],
            "company_info": "技术导向型公司，约200名员工"
        },
        "infrastructure": {
            "ip_ranges": ["192.168.1.0/24", "10.0.0.0/16"],
            "open_ports": [22, 80, 443, 3389],
            "services": ["SSH", "HTTP", "HTTPS", "RDP"]
        }
    }

    result = {
        "campaign_id": campaign_id,
        "phase": "深度侦察",
        "reconnaissance_type": reconnaissance_type,
        "data_collected": reconnaissance_data,
        "next_phase": "武器化"
    }

    return json.dumps(result)

@mcp.tool
def apt_weaponization(campaign_id: str, target_profile: Dict, delivery_method: str = "spear_phishing") -> str:
    """
    APT武器化阶段，根据目标特征制作定制化攻击载荷

    Args:
        campaign_id: APT攻击活动ID
        target_profile: 目标特征信息
        delivery_method: 投递方式（spear_phishing/watering_hole/supply_chain）

    Returns:
        武器化载荷信息
    """
    if campaign_id not in apt_sessions:
        return json.dumps({"error": "无效的APT攻击活动ID"})

    session = apt_sessions[campaign_id]
    session["phase"] = "武器化"

    # 根据投递方式生成不同的载荷
    weaponization_data = {
        "spear_phishing": {
            "payload_type": "定制化钓鱼邮件 + 恶意附件",
            "attachment": "年度安全报告.docx (含宏病毒)",
            "social_engineering": "利用目标公司最新新闻事件",
            "evasion_techniques": ["反沙箱检测", "文档加密", "分阶段下载"]
        },
        "watering_hole": {
            "payload_type": "水坑攻击",
            "target_websites": ["行业论坛", "供应商网站"],
            "exploit_kit": "零日漏洞利用工具包",
            "persistence": "浏览器插件植入"
        },
        "supply_chain": {
            "payload_type": "供应链攻击",
            "target_software": "第三方开发工具",
            "backdoor_type": "代码签名后门",
            "distribution": "软件更新机制"
        }
    }

    selected_method = weaponization_data.get(delivery_method, weaponization_data["spear_phishing"])

    result = {
        "campaign_id": campaign_id,
        "phase": "武器化",
        "delivery_method": delivery_method,
        "weaponization_details": selected_method,
        "stealth_rating": "极高",
        "next_phase": "投递"
    }

    return json.dumps(result)

@mcp.tool
def apt_delivery(campaign_id: str, target_email: str, weaponized_payload: str) -> str:
    """
    APT投递阶段，向目标发送定制化攻击载荷

    Args:
        campaign_id: APT攻击活动ID
        target_email: 目标邮箱
        weaponized_payload: 武器化载荷

    Returns:
        投递结果
    """
    if campaign_id not in apt_sessions:
        return json.dumps({"error": "无效的APT攻击活动ID"})

    session = apt_sessions[campaign_id]
    session["phase"] = "投递"

    # 模拟高级钓鱼邮件投递
    delivery_result = {
        "delivery_status": "成功",
        "target_email": target_email,
        "email_subject": "紧急：安全漏洞修复通知",
        "social_engineering_score": 9.2,  # 高度定制化
        "evasion_success": True,
        "delivery_time": datetime.utcnow().isoformat(),
        "tracking": {
            "email_opened": True,
            "attachment_downloaded": True,
            "macro_enabled": True
        }
    }

    result = {
        "campaign_id": campaign_id,
        "phase": "投递",
        "delivery_result": delivery_result,
        "success_probability": "85%",
        "next_phase": "利用"
    }

    return json.dumps(result)

@mcp.tool
def apt_exploitation(campaign_id: str, target_host: str, exploit_type: str = "zero_day") -> str:
    """
    APT利用阶段，执行漏洞利用获得初始访问权限

    Args:
        campaign_id: APT攻击活动ID
        target_host: 目标主机
        exploit_type: 利用类型（zero_day/known_vuln/social_engineering）

    Returns:
        利用结果和获得的访问权限
    """
    if campaign_id not in apt_sessions:
        return json.dumps({"error": "无效的APT攻击活动ID"})

    session = apt_sessions[campaign_id]
    session["phase"] = "利用"

    # 生成会话ID
    session_id = f"apt_sess_{uuid.uuid4().hex[:8]}"

    exploitation_result = {
        "exploit_success": True,
        "session_id": session_id,
        "target_host": target_host,
        "exploit_type": exploit_type,
        "initial_access": {
            "user_privileges": "标准用户",
            "access_method": "远程代码执行",
            "persistence_installed": False,
            "detection_risk": "低"
        },
        "host_info": {
            "os": "Windows 10 Enterprise",
            "domain": session["target_organization"],
            "antivirus": "Windows Defender (已绕过)",
            "network_position": "内网工作站"
        }
    }

    # 更新会话信息
    session["compromised_hosts"].append({
        "host": target_host,
        "session_id": session_id,
        "compromise_time": datetime.utcnow().isoformat(),
        "access_level": "用户级"
    })

    result = {
        "campaign_id": campaign_id,
        "phase": "利用",
        "exploitation_result": exploitation_result,
        "next_phase": "安装"
    }

    return json.dumps(result)

@mcp.tool
def apt_installation(campaign_id: str, session_id: str, persistence_type: str = "registry") -> str:
    """
    APT安装阶段，在目标系统中安装持久化机制

    Args:
        campaign_id: APT攻击活动ID
        session_id: 会话ID
        persistence_type: 持久化类型（registry/service/scheduled_task/dll_hijacking）

    Returns:
        持久化安装结果
    """
    if campaign_id not in apt_sessions:
        return json.dumps({"error": "无效的APT攻击活动ID"})

    session = apt_sessions[campaign_id]
    session["phase"] = "安装"

    persistence_mechanisms = {
        "registry": {
            "method": "注册表启动项",
            "location": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            "stealth_level": "中等",
            "detection_difficulty": "中等"
        },
        "service": {
            "method": "Windows服务",
            "location": "伪装为系统服务",
            "stealth_level": "高",
            "detection_difficulty": "高"
        },
        "scheduled_task": {
            "method": "计划任务",
            "location": "系统计划任务",
            "stealth_level": "高",
            "detection_difficulty": "高"
        },
        "dll_hijacking": {
            "method": "DLL劫持",
            "location": "系统DLL目录",
            "stealth_level": "极高",
            "detection_difficulty": "极高"
        }
    }

    selected_persistence = persistence_mechanisms.get(persistence_type, persistence_mechanisms["registry"])

    installation_result = {
        "installation_success": True,
        "persistence_type": persistence_type,
        "persistence_details": selected_persistence,
        "backdoor_installed": True,
        "c2_connection": {
            "server": "apt-c2.example.com",
            "protocol": "HTTPS",
            "encryption": "AES-256",
            "heartbeat_interval": "每6小时"
        }
    }

    # 更新会话持久化信息
    session["persistence_mechanisms"].append({
        "session_id": session_id,
        "type": persistence_type,
        "install_time": datetime.now().isoformat(),
        "status": "活跃"
    })

    result = {
        "campaign_id": campaign_id,
        "phase": "安装",
        "session_id": session_id,
        "installation_result": installation_result,
        "next_phase": "命令与控制"
    }

    return json.dumps(result)

@mcp.tool
def apt_command_control(campaign_id: str, session_id: str, command: str) -> str:
    """
    APT命令与控制阶段，通过C2服务器控制被感染主机

    Args:
        campaign_id: APT攻击活动ID
        session_id: 会话ID
        command: 要执行的命令

    Returns:
        命令执行结果
    """
    if campaign_id not in apt_sessions:
        return json.dumps({"error": "无效的APT攻击活动ID"})

    session = apt_sessions[campaign_id]
    session["phase"] = "命令与控制"

    # 模拟命令执行
    command_results = {
        "whoami": "domain\\user123",
        "ipconfig": "IP地址: 192.168.1.100\n子网掩码: 255.255.255.0\n默认网关: 192.168.1.1",
        "net user": "Administrator  Guest  user123  service_account",
        "systeminfo": "OS: Windows 10 Enterprise\n处理器: Intel Core i7\n内存: 16GB",
        "dir": "文件列表:\nDocuments/\nDownloads/\nDesktop/\nconfig.txt\nsecrets.xlsx"
    }

    command_output = command_results.get(command, f"命令 '{command}' 执行成功")

    c2_result = {
        "command_executed": command,
        "output": command_output,
        "execution_time": datetime.now().isoformat(),
        "stealth_status": "未被检测",
        "c2_communication": {
            "encrypted": True,
            "protocol": "HTTPS",
            "traffic_disguised": "正常Web流量"
        }
    }

    result = {
        "campaign_id": campaign_id,
        "phase": "命令与控制",
        "session_id": session_id,
        "c2_result": c2_result,
        "next_actions": ["权限提升", "横向移动", "数据收集"]
    }

    return json.dumps(result)

@mcp.tool
def apt_privilege_escalation(campaign_id: str, session_id: str, escalation_method: str = "uac_bypass") -> str:
    """
    APT权限提升阶段，获取更高级别的系统权限

    Args:
        campaign_id: APT攻击活动ID
        session_id: 会话ID
        escalation_method: 提权方法（uac_bypass/kernel_exploit/token_manipulation）

    Returns:
        权限提升结果
    """
    if campaign_id not in apt_sessions:
        return json.dumps({"error": "无效的APT攻击活动ID"})

    session = apt_sessions[campaign_id]
    session["phase"] = "权限提升"

    escalation_methods = {
        "uac_bypass": {
            "technique": "UAC绕过",
            "success_rate": "85%",
            "stealth_level": "高",
            "target_privilege": "管理员权限"
        },
        "kernel_exploit": {
            "technique": "内核漏洞利用",
            "success_rate": "95%",
            "stealth_level": "中等",
            "target_privilege": "SYSTEM权限"
        },
        "token_manipulation": {
            "technique": "令牌操纵",
            "success_rate": "75%",
            "stealth_level": "极高",
            "target_privilege": "域管理员权限"
        }
    }

    selected_method = escalation_methods.get(escalation_method, escalation_methods["uac_bypass"])

    escalation_result = {
        "escalation_success": True,
        "method": selected_method,
        "new_privileges": selected_method["target_privilege"],
        "escalation_time": datetime.now().isoformat(),
        "detection_risk": "低",
        "capabilities_gained": [
            "系统文件访问",
            "注册表完全控制",
            "服务管理",
            "用户账户管理"
        ]
    }

    # 更新主机访问级别
    for host in session["compromised_hosts"]:
        if host["session_id"] == session_id:
            host["access_level"] = selected_method["target_privilege"]
            break

    result = {
        "campaign_id": campaign_id,
        "phase": "权限提升",
        "session_id": session_id,
        "escalation_result": escalation_result,
        "next_phase": "横向移动"
    }

    return json.dumps(result)

@mcp.tool
def apt_lateral_movement(campaign_id: str, source_session_id: str, target_host: str, movement_technique: str = "pass_the_hash") -> str:
    """
    APT横向移动阶段，从已控制主机扩展到网络中的其他主机

    Args:
        campaign_id: APT攻击活动ID
        source_session_id: 源主机会话ID
        target_host: 目标主机
        movement_technique: 移动技术（pass_the_hash/wmi/psexec/rdp）

    Returns:
        横向移动结果
    """
    if campaign_id not in apt_sessions:
        return json.dumps({"error": "无效的APT攻击活动ID"})

    session = apt_sessions[campaign_id]
    session["phase"] = "横向移动"

    movement_techniques = {
        "pass_the_hash": {
            "technique": "哈希传递攻击",
            "requirements": "NTLM哈希",
            "stealth_level": "高",
            "success_rate": "90%"
        },
        "wmi": {
            "technique": "WMI远程执行",
            "requirements": "管理员权限",
            "stealth_level": "极高",
            "success_rate": "85%"
        },
        "psexec": {
            "technique": "PsExec工具",
            "requirements": "SMB访问权限",
            "stealth_level": "中等",
            "success_rate": "95%"
        },
        "rdp": {
            "technique": "远程桌面协议",
            "requirements": "RDP凭据",
            "stealth_level": "低",
            "success_rate": "80%"
        }
    }

    selected_technique = movement_techniques.get(movement_technique, movement_techniques["pass_the_hash"])
    new_session_id = f"apt_sess_{uuid.uuid4().hex[:8]}"

    movement_result = {
        "movement_success": True,
        "technique": selected_technique,
        "source_host": source_session_id,
        "target_host": target_host,
        "new_session_id": new_session_id,
        "movement_time": datetime.now().isoformat(),
        "credentials_harvested": [
            "domain\\admin_user:password123",
            "domain\\service_account:service_pass"
        ],
        "network_discovery": {
            "domain_controllers": ["dc01.domain.com", "dc02.domain.com"],
            "file_servers": ["fs01.domain.com", "backup.domain.com"],
            "database_servers": ["sql01.domain.com"]
        }
    }

    # 添加新的被控主机
    session["compromised_hosts"].append({
        "host": target_host,
        "session_id": new_session_id,
        "compromise_time": datetime.now().isoformat(),
        "access_level": "管理员权限",
        "source_host": source_session_id
    })

    # 记录横向移动路径
    session["lateral_movement_paths"].append({
        "from": source_session_id,
        "to": new_session_id,
        "technique": movement_technique,
        "timestamp": datetime.now().isoformat()
    })

    result = {
        "campaign_id": campaign_id,
        "phase": "横向移动",
        "movement_result": movement_result,
        "total_compromised_hosts": len(session["compromised_hosts"]),
        "next_phase": "数据收集"
    }

    return json.dumps(result)

@mcp.tool
def apt_data_collection(campaign_id: str, session_id: str, collection_targets: List[str] = None) -> str:
    """
    APT数据收集阶段，从目标系统中收集敏感信息

    Args:
        campaign_id: APT攻击活动ID
        session_id: 会话ID
        collection_targets: 收集目标类型列表

    Returns:
        数据收集结果
    """
    if campaign_id not in apt_sessions:
        return json.dumps({"error": "无效的APT攻击活动ID"})

    session = apt_sessions[campaign_id]
    session["phase"] = "数据收集"

    if collection_targets is None:
        collection_targets = ["文档", "数据库", "邮件", "凭据"]

    collection_results = {
        "文档": {
            "files_found": 1247,
            "sensitive_files": [
                "财务报表2024.xlsx",
                "客户信息数据库.csv",
                "商业计划书.docx",
                "员工薪资表.xlsx"
            ],
            "total_size": "2.3GB"
        },
        "数据库": {
            "databases_found": ["customer_db", "financial_db", "hr_db"],
            "records_extracted": 50000,
            "sensitive_tables": ["users", "payments", "personal_info"]
        },
        "邮件": {
            "mailboxes_accessed": ["CEO", "CFO", "IT管理员"],
            "emails_collected": 15000,
            "sensitive_emails": 342
        },
        "凭据": {
            "passwords_harvested": 89,
            "certificates_found": 12,
            "api_keys": 23,
            "domain_accounts": 156
        }
    }

    collected_data = []
    for target in collection_targets:
        if target in collection_results:
            collected_data.append({
                "type": target,
                "data": collection_results[target],
                "collection_time": datetime.now().isoformat()
            })

    # 更新会话收集的数据
    session["collected_data"].extend(collected_data)

    result = {
        "campaign_id": campaign_id,
        "phase": "数据收集",
        "session_id": session_id,
        "collection_targets": collection_targets,
        "collected_data": collected_data,
        "total_data_size": "2.3GB",
        "next_phase": "数据泄露"
    }

    return json.dumps(result)

@mcp.tool
def apt_exfiltration(campaign_id: str, data_type: str, exfiltration_method: str = "encrypted_channel") -> str:
    """
    APT数据泄露阶段，将收集的数据安全传输到攻击者控制的服务器

    Args:
        campaign_id: APT攻击活动ID
        data_type: 要泄露的数据类型
        exfiltration_method: 泄露方法（encrypted_channel/dns_tunneling/steganography）

    Returns:
        数据泄露结果
    """
    if campaign_id not in apt_sessions:
        return json.dumps({"error": "无效的APT攻击活动ID"})

    session = apt_sessions[campaign_id]
    session["phase"] = "数据泄露"

    exfiltration_methods = {
        "encrypted_channel": {
            "method": "加密通道",
            "protocol": "HTTPS",
            "encryption": "AES-256",
            "stealth_level": "高",
            "speed": "10MB/s"
        },
        "dns_tunneling": {
            "method": "DNS隧道",
            "protocol": "DNS",
            "encryption": "Base64编码",
            "stealth_level": "极高",
            "speed": "1MB/s"
        },
        "steganography": {
            "method": "隐写术",
            "protocol": "HTTP",
            "encryption": "图像隐写",
            "stealth_level": "极高",
            "speed": "5MB/s"
        }
    }

    selected_method = exfiltration_methods.get(exfiltration_method, exfiltration_methods["encrypted_channel"])

    exfiltration_result = {
        "exfiltration_success": True,
        "data_type": data_type,
        "method": selected_method,
        "destination": "apt-exfil.example.com",
        "data_size": "2.3GB",
        "transfer_time": "4小时23分钟",
        "detection_risk": "极低",
        "exfiltration_time": datetime.now().isoformat()
    }

    result = {
        "campaign_id": campaign_id,
        "phase": "数据泄露",
        "exfiltration_result": exfiltration_result,
        "campaign_status": "目标达成",
        "next_actions": ["维持访问", "清理痕迹", "准备下一阶段"]
    }

    return json.dumps(result)

@mcp.tool
def apt_campaign_status(campaign_id: str) -> str:
    """
    获取APT攻击活动的完整状态信息

    Args:
        campaign_id: APT攻击活动ID

    Returns:
        攻击活动完整状态
    """
    if campaign_id not in apt_sessions:
        return json.dumps({"error": "无效的APT攻击活动ID"})

    session = apt_sessions[campaign_id]

    # 计算攻击持续时间
    start_time = datetime.fromisoformat(session["start_time"])
    duration = datetime.now() - start_time

    status_report = {
        "campaign_overview": {
            "campaign_id": campaign_id,
            "target_organization": session["target_organization"],
            "campaign_name": session["campaign_name"],
            "current_phase": session["phase"],
            "status": session["status"],
            "duration": str(duration),
            "stealth_level": session["stealth_level"]
        },
        "attack_progress": {
            "objectives": session["objectives"],
            "compromised_hosts": len(session["compromised_hosts"]),
            "persistence_mechanisms": len(session["persistence_mechanisms"]),
            "lateral_movement_paths": len(session["lateral_movement_paths"]),
            "data_collected": len(session["collected_data"])
        },
        "detailed_status": {
            "compromised_hosts": session["compromised_hosts"],
            "persistence_mechanisms": session["persistence_mechanisms"],
            "lateral_movement_paths": session["lateral_movement_paths"],
            "collected_data": session["collected_data"]
        },
        "threat_assessment": {
            "impact_level": "高",
            "detection_probability": "低",
            "attribution_difficulty": "极高",
            "remediation_complexity": "复杂"
        }
    }

    return json.dumps(status_report)

# -----------------------------------------------------------------------------

# 3. Start the server
if __name__ == "__main__":
    print("\n--- Attack Service (v3 - with APT capabilities) is starting... ---\n")
    mcp.run(transport="http", port=8001)