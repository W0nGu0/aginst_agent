import subprocess
from fastmcp import FastMCP
import random
import httpx
import json

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
    """模拟在虚假登录页面捕获用户凭据"""
    if password.lower() in {"password", "password123", "123456"}:
        return "凭据收集成功！目标使用了弱密码。"
    return "凭据收集尝试已记录。密码看起来比常见弱密码更强。"


# 3. Start the server
if __name__ == "__main__":
    print("\n--- Attack Service (v2 - with JSON string fix) is starting... ---\n")
    mcp.run(transport="http", port=8001)