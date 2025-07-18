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
def craft_phishing_email(target_name: str, company: str, malicious_link: str) -> str:
    """生成一封针对特定目标的钓鱼邮件"""
    templates = [
        ("薪资信息更新通知", "您好 {name}，\n\n您的{company}薪资信息需要更新。点击此处立即更新：\n{link}\n\n谢谢，\n{company}人力资源部"),
        ("账号异常登录活动", "亲爱的{name}，\n\n我们检测到您的{company}账号有异常登录活动。请点击以下链接验证您的身份：\n{link}\n\n此致,\n{company}安全团队"),
        ("年度安全审计确认", "{name}您好，\n\n作为年度安全审计的一部分，我们需要您确认您的凭据。请点击以下安全链接：\n{link}\n\n祝好，\n{company}IT技术支持")
    ]
    
    subject, body = random.choice(templates)
    email_body = body.format(name=target_name, company=company, link=malicious_link)
    return f"已为{target_name}创建了一封钓鱼邮件，内容如下：\n\n---\n\n**主题**: {subject}\n\n**正文**:\n{email_body}\n\n---"

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
# -----------------------------------------------------------------------------

# 3. Start the server
if __name__ == "__main__":
    print("\n--- Attack Service (v2 - with JSON string fix) is starting... ---\n")
    mcp.run(transport="http", port=8001)