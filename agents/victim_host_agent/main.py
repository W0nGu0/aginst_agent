import os
import httpx
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import logging
from fastmcp import FastMCP

# --- Configuration for the Victim ---
# In a real scenario, this would be loaded from env vars or a config file
# specific to the container instance.
VICTIM_CONFIG = {
    "company_name": "Acme Corp",
    "username": "victim_user",
    "password": "Password123!",
    "attack_service_credential_harvest_url": os.getenv(
        "ATTACK_SERVICE_URL", "http://127.0.0.1:8001/mcp/"
    ) + "simulate_credential_harvest"
}

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App ---
app = FastAPI(
    title="Victim Host Agent (VHA)",
    description="Simulates a programmable victim host that can be targeted by attacks."
)

class PhishingEmail(BaseModel):
    company: str
    malicious_link: str # In this simulation, this link points back to the attack service
    email_body: str # The crafted content from the attack agent
    target_name: str = None # 目标用户名
    department: str = None # 目标部门
    role: str = None # 目标职位
    subject: str = None # 邮件主题

@app.get("/metadata")
async def get_metadata():
    """
    暴露一些可供侦察的元数据，模拟一个配置不当或信息泄露的端点。
    从环境变量中获取更多信息。
    """
    # 从环境变量中获取信息，这些环境变量在docker-compose中配置
    # 如果环境变量不存在，则使用默认值
    company = os.getenv("COMPANY", VICTIM_CONFIG["company_name"])
    username = os.getenv("USERNAME", VICTIM_CONFIG["username"])
    department = os.getenv("DEPARTMENT", "研发部")
    role = os.getenv("ROLE", "软件工程师")
    email = os.getenv("EMAIL", f"{username}@{company.lower().replace(' ', '')}.com")
    position = os.getenv("POSITION", "工程师")
    os_info = os.getenv("OS", "Ubuntu 20.04 LTS")
    kernel = os.getenv("KERNEL", "5.4.0-42-generic")
    host_type = os.getenv("HOST_TYPE", "工作站")
    
    # 打印环境变量，便于调试
    logger.info(f"获取到的环境变量: COMPANY={company}, USERNAME={username}, DEPARTMENT={department}, ROLE={role}")
    
    # 构建返回的元数据
    metadata = {
        "company_name": company,
        "username": username,
        "department": department,
        "role": role,
        "email": email,
        "position": position,
        "system_info": os_info,
        "kernel": kernel,
        "host_type": host_type,
        "server": "Apache/2.4.41 (Ubuntu)",
        "open_ports": [22, 80, 443]
    }
    
    logger.info(f"返回元数据: {metadata}")
    return metadata

@app.post("/receive_email")
async def receive_email(email: PhishingEmail):
    """
    模拟接收钓鱼邮件。根据邮件内容与受害者信息的匹配程度，计算攻击成功的可能性。
    匹配度越高，攻击成功率越高。
    """
    # 获取当前环境变量中的信息
    company = os.getenv("COMPANY", VICTIM_CONFIG["company_name"])
    username = os.getenv("USERNAME", VICTIM_CONFIG["username"])
    department = os.getenv("DEPARTMENT", "未知部门")
    role = os.getenv("ROLE", "未知职位")
    
    # 记录接收到的钓鱼邮件
    logger.info(f"收到钓鱼邮件，目标公司: {email.company}")
    logger.info(f"主题: {email.subject or '无主题'}")
    logger.info(f"目标用户: {email.target_name}, 部门: {email.department}, 职位: {email.role}")
    logger.info(f"邮件内容:\n{email.email_body}")
    
    # 计算匹配分数，用于确定攻击成功率
    match_score = 0
    max_score = 4  # 最大可能分数
    
    # 检查公司名称匹配
    if email.company.lower() == company.lower():
        match_score += 1
        logger.info("公司名称匹配 (+1)")
    
    # 检查目标用户名匹配
    if email.target_name and email.target_name.lower() == username.lower():
        match_score += 1
        logger.info("用户名匹配 (+1)")
    
    # 检查部门匹配
    if email.department and email.department.lower() == department.lower():
        match_score += 1
        logger.info("部门匹配 (+1)")
    
    # 检查职位匹配
    if email.role and email.role.lower() == role.lower():
        match_score += 1
        logger.info("职位匹配 (+1)")
    
    # 计算成功率
    success_rate = match_score / max_score
    
    # 提高匹配度要求，更符合真实场景
    # 根据匹配分数决定是否点击恶意链接
    if success_rate >= 0.75:  # 如果匹配度超过75%，则点击链接
        logger.warning(
            f"钓鱼攻击成功！匹配分数: {match_score}/{max_score} ({success_rate*100:.0f}%). "
            f"模拟用户点击恶意链接: {email.malicious_link}"
        )
        try:
            # 向攻击服务发送凭据
            attack_service = FastMCP.as_proxy("http://127.0.0.1:8001/mcp/")
            async with attack_service.client as client:
                await client.call_tool(
                    "simulate_credential_harvest",
                    arguments={
                        "username": username,
                        "password": VICTIM_CONFIG["password"],
                        "match_score": match_score,
                        "max_score": max_score
                    }
                )
            return {
                "status": "compromised", 
                "detail": "凭据已发送给攻击者。", 
                "match_score": match_score,
                "max_score": max_score,
                "success_rate": f"{success_rate*100:.0f}%"
            }

        except Exception as e:
            error_message = f"凭据提交过程中发生意外错误: {e}"
            logger.error(error_message)
            raise HTTPException(status_code=500, detail=error_message)

    else:
        logger.info(f"钓鱼攻击失败。匹配分数: {match_score}/{max_score} ({success_rate*100:.0f}%)。邮件被忽略。")
        return {
            "status": "ignored", 
            "detail": "邮件与受害者信息匹配度不足。", 
            "match_score": match_score,
            "max_score": max_score,
            "success_rate": f"{success_rate*100:.0f}%"
        }

# -------------------- 新增：统一接收社会工程学载荷 --------------------
from typing import Optional


class SocialPayload(BaseModel):
    tactic: str
    subject: Optional[str] = None
    body: Optional[str] = None
    malicious_link: Optional[str] = None


@app.post("/receive_social")
async def receive_social(payload: SocialPayload):
    """统一接收社会工程学攻击载荷，仅记录并返回确认。未来可根据 tactic 触发不同行为。"""
    logger.warning(
        "[SOCIAL-ENG] 收到载荷 -> tactic=%s subject=%s link=%s",
        payload.tactic,
        payload.subject,
        payload.malicious_link,
    )
    # 此处仅打印，后续可根据 tactic 执行不同模拟动作
    return {"status": "received", "tactic": payload.tactic}

if __name__ == "__main__":
    import uvicorn
    # This agent would run on a different port
    uvicorn.run(app, host="0.0.0.0", port=8005) 