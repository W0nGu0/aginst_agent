import os
import httpx
import json
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pathlib import Path
from dotenv import load_dotenv
import random
import websockets.client

from fastmcp import FastMCP
from langchain_deepseek import ChatDeepSeek
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool

# --- 设置日志 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("attack-agent")

# --- 后端WebSocket连接 ---
BACKEND_WS_URL = "ws://localhost:8080/ws/logs"
backend_ws = None

async def connect_to_backend():
    """连接到后端WebSocket"""
    global backend_ws
    try:
        # 如果已有连接，先关闭
        if backend_ws:
            try:
                await backend_ws.close()
            except Exception:
                pass
            backend_ws = None
            
        # 创建新连接
        backend_ws = await websockets.client.connect(BACKEND_WS_URL)
        
        # 发送一条测试消息
        await backend_ws.send(json.dumps({
            "level": "info",
            "source": "攻击智能体",
            "message": "WebSocket连接已建立"
        }))
        
        logger.info(f"已连接到后端WebSocket: {BACKEND_WS_URL}")
        return True
    except Exception as e:
        logger.error(f"连接后端WebSocket失败: {e}")
        return False

async def send_log_to_backend(level: str, source: str, message: str, attack_step_info: dict = None):
    """发送精确的结构化日志到后端WebSocket"""
    global backend_ws
    
    # 分析消息内容，提取攻击步骤信息
    step_info = analyze_attack_step(message, attack_step_info)
    
    # 构建结构化日志数据
    log_data = {
        "timestamp": asyncio.get_event_loop().time(),
        "level": level,
        "source": source,
        "message": message,  # 使用简化的消息，不再添加阶段前缀
        # 攻击步骤详细信息
        "attack_info": {
            "stage": step_info["stage"],           # 攻击阶段
            "technique": step_info["technique"],   # 攻击技术
            "source_node": step_info["source_node"],  # 源节点
            "target_node": step_info["target_node"],  # 目标节点
            "progress": step_info["progress"],     # 进度百分比
            "status": step_info["status"]          # 状态：starting/in_progress/completed/failed
        }
    }
    
    # 增强的连接稳定性和重试机制
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # 检查连接是否存在或是否需要重新连接
            if backend_ws is None:
                await connect_to_backend()
                await asyncio.sleep(0.1)  # 给连接一点时间稳定
            
            # 检查连接状态
            if backend_ws and not backend_ws.closed:
                await backend_ws.send(json.dumps(log_data, ensure_ascii=False))
                logger.debug(f"已发送结构化日志到后端: {step_info['stage']} - {message}")
                return  # 成功发送，退出重试循环
            else:
                # 连接已关闭，重新连接
                await connect_to_backend()
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.warning(f"发送消息失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)  # 等待后重试
                await connect_to_backend()
            else:
                logger.error(f"发送日志到后端WebSocket最终失败: {e}")

async def send_standardized_log(level: str, source: str, standard_message: str, **kwargs):
    """发送标准化的简化日志消息"""
    # 构建攻击信息
    attack_info = None
    if kwargs:
        attack_info = kwargs

    await send_log_to_backend(level, source, standard_message, attack_info)

class AttackLogHandler:
    """攻击日志处理器，根据工具调用自动生成标准化日志"""

    def __init__(self):
        self.current_stage = "reconnaissance"
        self.stage_progress = {
            "reconnaissance": 0,
            "weaponization": 0,
            "delivery": 0,
            "exploitation": 0,
            "installation": 0,
            "command_and_control": 0,
            "actions_on_objectives": 0
        }
        self.stage_order = [
            "reconnaissance", "weaponization", "delivery",
            "exploitation", "installation", "command_and_control",
            "actions_on_objectives"
        ]

    def get_overall_progress(self) -> int:
        """计算整体攻击进度"""
        total_stages = len(self.stage_order)
        total_progress = 0

        for stage in self.stage_order:
            total_progress += self.stage_progress[stage]

        return int(total_progress / total_stages)

    def advance_stage(self, stage: str, progress: int = 100):
        """推进特定阶段的进度"""
        if stage in self.stage_progress:
            self.stage_progress[stage] = progress
            self.current_stage = stage

    async def log_tool_start(self, tool_name: str, tool_input: dict):
        """工具开始执行时的日志"""
        if tool_name == "run_nmap":
            self.advance_stage("reconnaissance", 10)
            await send_standardized_log("info", "攻击智能体", "攻击者使用Nmap工具扫描防火墙")
        elif tool_name == "fetch_url_content":
            if "/metadata" in str(tool_input):
                self.advance_stage("reconnaissance", 30)
                await send_standardized_log("info", "攻击智能体", "攻击者发现防火墙开放端口")
        elif tool_name == "craft_phishing_email":
            self.advance_stage("weaponization", 45)
            await send_standardized_log("info", "攻击智能体", "攻击者生成钓鱼邮件")
        elif tool_name == "send_payload_to_victim":
            self.advance_stage("delivery", 55)
            await send_standardized_log("info", "攻击智能体", "攻击者向目标发送钓鱼邮件")

    async def log_tool_end(self, tool_name: str, tool_output: str):
        """工具执行完成时的日志"""
        if tool_name == "run_nmap":
            if "open" in tool_output.lower():
                self.advance_stage("reconnaissance", 30)
                await send_standardized_log("warning", "攻击智能体", "攻击者使用Nmap扫描防火墙发现开放端口 22,80,443 - 目标设备: border_firewall (192.168.1.1)")
        elif tool_name == "fetch_url_content":
            if "/metadata" in tool_output or "company" in tool_output.lower():
                self.advance_stage("reconnaissance", 100)
                await send_standardized_log("success", "攻击智能体", "攻击者完成目标侦察 - 获取公司信息和员工数据 - 目标: Acme Corp")
        elif tool_name == "craft_phishing_email":
            self.advance_stage("weaponization", 100)
            await send_standardized_log("success", "攻击智能体", "攻击者完成恶意载荷制作 - 生成针对性钓鱼邮件 - 目标用户: victim_user")
        elif tool_name == "send_payload_to_victim":
            if "成功" in tool_output or "success" in tool_output.lower():
                self.advance_stage("delivery", 100)
                await send_standardized_log("success", "攻击智能体", "钓鱼邮件成功投递到目标 - 邮件已发送至 victim_user@acmecorp.com")

                # === 阶段3：利用阶段 - 攻击DMZ Web服务器 ===
                await asyncio.sleep(2)
                self.advance_stage("exploitation", 50)
                await send_standardized_log("critical", "攻击智能体", "攻击者利用钓鱼邮件攻击DMZ Web服务器 - 目标：172.16.100.10 (dmz-web-01)")

                await asyncio.sleep(1)
                self.advance_stage("exploitation", 100)
                await send_standardized_log("critical", "攻击智能体", "攻击者成功攻陷DMZ Web服务器 - dmz-web-01因Web应用漏洞被攻陷")

                # === 阶段4：安装阶段 - 在DMZ服务器建立后门 ===
                await asyncio.sleep(1)
                self.advance_stage("installation", 50)
                await send_standardized_log("critical", "攻击智能体", "攻击者在DMZ Web服务器安装后门 - dmz-web-01植入持久化木马")

                await asyncio.sleep(1)
                self.advance_stage("installation", 100)
                await send_standardized_log("critical", "攻击智能体", "攻击者建立DMZ服务器持久化访问 - 检测到来自203.0.113.100的恶意IP连接")

                # === 阶段5：命令控制阶段 - 从DMZ开始横向移动 ===
                await asyncio.sleep(1)
                self.advance_stage("command_and_control", 15)
                await send_standardized_log("critical", "攻击智能体", "攻击者与DMZ服务器建立C2通信 - 恶意IP 203.0.113.100开始远程控制dmz-web-01")

                await asyncio.sleep(1)
                self.advance_stage("command_and_control", 25)
                await send_standardized_log("critical", "攻击智能体", "攻击者从DMZ扫描内网 - 发现内网网段192.168.200.0/24")

                await asyncio.sleep(1)
                self.advance_stage("command_and_control", 35)
                await send_standardized_log("critical", "攻击智能体", "攻击者发现内网应用服务器 - 目标：192.168.200.10 (app-server-01)")

                await asyncio.sleep(1)
                self.advance_stage("command_and_control", 45)
                await send_standardized_log("critical", "攻击智能体", "攻击者尝试突破内网防火墙 - 利用DMZ服务器权限测试防火墙规则")

                await asyncio.sleep(1)
                self.advance_stage("command_and_control", 55)
                await send_standardized_log("critical", "攻击智能体", "攻击者成功绕过内网防火墙 - 发现内网应用服务器开放端口")

                await asyncio.sleep(1)
                self.advance_stage("command_and_control", 65)
                await send_standardized_log("critical", "攻击智能体", "攻击者攻陷内网应用服务器 - 获得app-server-01控制权限")

                await asyncio.sleep(1)
                self.advance_stage("command_and_control", 75)
                await send_standardized_log("critical", "攻击智能体", "攻击者从内网服务器探测数据库网段 - 扫描数据库网段192.168.214.0/24")

                await asyncio.sleep(1)
                self.advance_stage("command_and_control", 85)
                await send_standardized_log("critical", "攻击智能体", "攻击者发现数据库服务器 - 目标：192.168.214.10 (internal-db-01)")

                await asyncio.sleep(1)
                self.advance_stage("command_and_control", 95)
                await send_standardized_log("critical", "攻击智能体", "攻击者尝试突破数据库防火墙 - 利用内网服务器身份访问数据库")

                await asyncio.sleep(1)
                self.advance_stage("command_and_control", 100)
                await send_standardized_log("critical", "攻击智能体", "攻击者建立完整攻击路径 - DMZ→内网→数据库的横向移动通道建立")

                # === 阶段6：行动目标阶段 - 攻击核心数据库并窃取数据 ===
                await asyncio.sleep(1)
                self.advance_stage("actions_on_objectives", 25)
                await send_standardized_log("critical", "攻击智能体", "攻击者成功访问数据库服务器 - 绕过数据库防火墙，获得数据库连接")

                await asyncio.sleep(1)
                self.advance_stage("actions_on_objectives", 50)
                await send_standardized_log("critical", "攻击智能体", "攻击者攻陷数据库服务器 - internal-db-01数据库权限被获取")

                await asyncio.sleep(1)
                self.advance_stage("actions_on_objectives", 75)
                await send_standardized_log("critical", "攻击智能体", "攻击者开始窃取敏感数据 - 从internal-db-01数据库导出客户信息和财务数据")

                await asyncio.sleep(1)
                self.advance_stage("actions_on_objectives", 100)
                await send_standardized_log("critical", "攻击智能体", "攻击者完成数据窃取 - 成功窃取10GB敏感数据，APT攻击目标达成")
                

# 创建全局日志处理器
attack_log_handler = AttackLogHandler()

def analyze_attack_step_fallback(message: str) -> dict:
    """备选的智能匹配逻辑，用于处理非标准化消息"""

    # 默认值
    result = {
        "stage": "未知阶段",
        "technique": "未知技术",
        "source_node": "internet",
        "target_node": "unknown",
        "progress": 0,
        "status": "in_progress"
    }

    msg_lower = message.lower()

    # 阶段识别
    if any(keyword in msg_lower for keyword in ["扫描", "侦察", "nmap", "端口", "服务发现", "元数据"]):
        result["stage"] = "reconnaissance"
        result["technique"] = "port_scan" if "扫描" in msg_lower else "info_gathering"
        result["target_node"] = "firewall" if "防火墙" in message else "target_host"

    elif any(keyword in msg_lower for keyword in ["武器化", "生成", "定制", "钓鱼邮件", "载荷"]):
        result["stage"] = "weaponization"
        result["technique"] = "phishing_email"
        result["target_node"] = "target_host"

    elif any(keyword in msg_lower for keyword in ["投递", "发送", "邮件", "传输"]):
        result["stage"] = "delivery"
        result["technique"] = "email_delivery"
        result["source_node"] = "internet"
        result["target_node"] = "target_host"

    elif any(keyword in msg_lower for keyword in ["利用", "点击", "漏洞", "exploit", "凭据"]):
        result["stage"] = "exploitation"
        result["technique"] = "credential_theft"
        result["target_node"] = "target_host"

    elif any(keyword in msg_lower for keyword in ["安装", "持久", "后门", "权限"]):
        result["stage"] = "installation"
        result["technique"] = "backdoor_install"
        result["target_node"] = "target_host"

    elif any(keyword in msg_lower for keyword in ["命令", "控制", "远程", "c2", "通信"]):
        result["stage"] = "command_and_control"
        result["technique"] = "c2_communication"
        result["source_node"] = "internet"
        result["target_node"] = "target_host"

    elif any(keyword in msg_lower for keyword in ["目标", "数据", "窃取", "攻陷", "横向", "移动"]):
        result["stage"] = "actions_on_objectives"
        result["technique"] = "data_theft" if "数据" in msg_lower else "lateral_movement"
        result["source_node"] = "target_host"
        result["target_node"] = "internal-db"

    # 状态识别
    if any(keyword in msg_lower for keyword in ["开始", "启动", "初始化"]):
        result["status"] = "starting"
        result["progress"] = 0
    elif any(keyword in msg_lower for keyword in ["完成", "成功", "获取", "建立"]):
        result["status"] = "completed"
        result["progress"] = 100
    elif any(keyword in msg_lower for keyword in ["失败", "错误", "无法"]):
        result["status"] = "failed"
        result["progress"] = 0
    else:
        result["status"] = "in_progress"
        result["progress"] = 50

    return result

def analyze_attack_step(message: str, step_info: dict = None) -> dict:
    """简化的攻击步骤分析 - 基于标准化消息映射"""

    # 如果提供了明确的步骤信息，优先使用
    if step_info:
        return step_info

    # 标准化消息映射表 - 包含动作+发起方+承受方的基本语义要素
    message_mapping = {
        # 侦察阶段
        "攻击者扫描防火墙": {
            "stage": "reconnaissance",
            "technique": "port_scan",
            "source_node": "internet",
            "target_node": "firewall",
            "status": "starting",
            "progress": 10
        },
        "攻击者发现防火墙开放端口": {
            "stage": "reconnaissance",
            "technique": "port_scan",
            "source_node": "internet",
            "target_node": "firewall",
            "status": "in_progress",
            "progress": 30
        },
        "攻击者完成目标侦察": {
            "stage": "reconnaissance",
            "technique": "info_gathering",
            "source_node": "internet",
            "target_node": "firewall",
            "status": "completed",
            "progress": 40
        },

        # 武器化阶段
        "攻击者生成钓鱼邮件": {
            "stage": "weaponization",
            "technique": "phishing_email",
            "source_node": "internet",
            "target_node": "target_host",
            "status": "starting",
            "progress": 45
        },
        "攻击者完成恶意载荷制作": {
            "stage": "weaponization",
            "technique": "phishing_email",
            "source_node": "internet",
            "target_node": "target_host",
            "status": "completed",
            "progress": 50
        },

        # 投递阶段
        "攻击者向目标发送钓鱼邮件": {
            "stage": "delivery",
            "technique": "email_delivery",
            "source_node": "internet",
            "target_node": "target_host",
            "status": "starting",
            "progress": 55
        },
        "钓鱼邮件成功投递到目标": {
            "stage": "delivery",
            "technique": "email_delivery",
            "source_node": "internet",
            "target_node": "target_host",
            "status": "completed",
            "progress": 60
        },

        # 利用阶段
        "目标用户点击恶意链接": {
            "stage": "exploitation",
            "technique": "credential_theft",
            "source_node": "target_host",
            "target_node": "target_host",
            "status": "starting",
            "progress": 65
        },
        "攻击者获得目标主机访问权限": {
            "stage": "exploitation",
            "technique": "credential_theft",
            "source_node": "internet",
            "target_node": "target_host",
            "status": "completed",
            "progress": 70
        },

        # 安装阶段
        "攻击者在目标主机安装后门": {
            "stage": "installation",
            "technique": "backdoor_install",
            "source_node": "internet",
            "target_node": "target_host",
            "status": "starting",
            "progress": 75
        },
        "攻击者建立目标主机持久化访问": {
            "stage": "installation",
            "technique": "persistence_mechanism",
            "source_node": "internet",
            "target_node": "target_host",
            "status": "completed",
            "progress": 80
        },

        # 命令控制阶段
        "攻击者与目标主机建立C2通信": {
            "stage": "command_and_control",
            "technique": "c2_communication",
            "source_node": "internet",
            "target_node": "target_host",
            "status": "starting",
            "progress": 85
        },
        "攻击者从目标主机向内网横向移动": {
            "stage": "command_and_control",
            "technique": "lateral_movement",
            "source_node": "target_host",
            "target_node": "internal-db",
            "status": "in_progress",
            "progress": 90
        },

        # 行动目标阶段
        "攻击者从内网数据库窃取数据": {
            "stage": "actions_on_objectives",
            "technique": "data_theft",
            "source_node": "internal-db",
            "target_node": "internet",
            "status": "starting",
            "progress": 95
        },
        "攻击者完全攻陷目标系统": {
            "stage": "actions_on_objectives",
            "technique": "system_compromise",
            "source_node": "internet",
            "target_node": "internal-db",
            "status": "completed",
            "progress": 100
        }
    }

    # 查找标准化消息
    if message in message_mapping:
        return message_mapping[message].copy()

    # 如果没有找到标准化消息，使用智能匹配作为备选
    return analyze_attack_step_fallback(message)

# --- 环境变量和配置 ---
dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

ATTACK_SERVICE_URL = os.getenv("ATTACK_SERVICE_URL", "http://127.0.0.1:8001/mcp/")
# 受害者主机的基础URL，指向Docker容器的IP地址和端口
# 由于我们现在使用Docker容器而不是本地进程，所以只能使用这些URL
VICTIM_HOST_URLS = {
    "alice": "http://localhost:5001",      # ws-ubuntu-cnt1 (宿主机端口映射)
    "bob": "http://localhost:5002",        # ws-ubuntu-cnt2 (宿主机端口映射)
    "default": "http://localhost:5001"     # 默认使用alice容器
}

# --- 初始化LLM和工具 ---
llm = ChatDeepSeek(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))

# 使用FastMCP客户端连接到攻击服务
attack_service_client = FastMCP.as_proxy(ATTACK_SERVICE_URL)

# --- 为Agent手动定义可用的工具 ---
# LangChain Agent需要一个明确的工具列表来了解其能力。
# 这些工具函数是对 `attack_service` 中真实工具的异步RPC调用封装。

@tool
async def run_nmap(target_ip: str, options: str = "-T4 --top-ports 20") -> str:
    """对目标IP地址执行Nmap扫描。对于Web服务器，通常目标IP是URL中的域名或IP。"""
    try:
        # 记录工具开始执行
        await attack_log_handler.log_tool_start("run_nmap", {"target_ip": target_ip, "options": options})

        async with attack_service_client.client as client:
            response = await client.call_tool(
                "run_nmap",
                arguments={'target_ip': target_ip, 'options': options}
            )
        # 从CallToolResult对象中安全地提取文本
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])

        # 记录工具执行完成
        await attack_log_handler.log_tool_end("run_nmap", result)

        return result
    except Exception as e:
        return f"执行nmap工具时出错: {e}"

@tool
async def fetch_url_content(url: str) -> str:
    """获取给定URL的内容。这对于发现目标网站上的信息（如公司名称）至关重要。"""
    try:
        # 记录工具开始执行
        await attack_log_handler.log_tool_start("fetch_url_content", {"url": url})

        async with attack_service_client.client as client:
            response = await client.call_tool(
                "fetch_url_content",
                arguments={'url': url}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])

        # 记录工具执行完成
        await attack_log_handler.log_tool_end("fetch_url_content", result)

        return result
    except Exception as e:
        return f"执行fetch_url_content工具时出错: {e}"

@tool
async def craft_phishing_email(target_name: str, company: str, malicious_link: str, 
                              department: str = None, role: str = None, email: str = None) -> str:
    """
    根据侦察到的公司名称和目标用户信息，制作一封高度定制化的钓鱼邮件。
    
    参数:
    - target_name: 目标人物姓名
    - company: 目标公司名称
    - malicious_link: 恶意链接
    - department: 目标部门（可选）
    - role: 目标职位（可选）
    - email: 目标邮箱（可选）
    
    返回:
    - 包含钓鱼邮件详细信息的JSON字符串
    """
    try:
        # 构建参数字典，仅包含非空参数
        args = {
            'target_name': target_name,
            'company': company,
            'malicious_link': malicious_link
        }
        
        # 添加可选参数（如果提供）
        if department:
            args['department'] = department
        if role:
            args['role'] = role
        if email:
            args['email'] = email
            
        async with attack_service_client.client as client:
            response = await client.call_tool(
                "craft_phishing_email",
                arguments=args
            )
        
        # 记录工具开始执行
        await attack_log_handler.log_tool_start("craft_phishing_email", args)

        # 获取响应内容
        response_text = "\n".join([b.text for b in response.content if hasattr(b, "text")])

        # 记录工具执行完成
        await attack_log_handler.log_tool_end("craft_phishing_email", response_text)

        # 尝试解析JSON响应
        try:
            # 如果响应已经是JSON格式，直接返回
            return response_text
        except Exception:
            # 如果不是JSON格式，构造一个基本的JSON响应
            return json.dumps({
                "subject": "钓鱼邮件",
                "body": response_text,
                "sender": f"{company} <noreply@{company.lower().replace(' ', '')}.com>",
                "recipient": email or f"{target_name}@{company.lower().replace(' ', '')}.com",
                "malicious_link": malicious_link
            })
    except Exception as e:
        return f"执行craft_phishing_email工具时出错: {e}"

@tool
async def send_payload_to_victim(victim_url: str, phishing_email_json: str) -> str:
    """
    将最终制作好的钓鱼邮件载荷，通过API发送给受害者。
    这是攻击流程的最后一步。
    
    参数:
    - victim_url: 受害者URL
    - phishing_email_json: 由craft_phishing_email工具生成的JSON格式钓鱼邮件内容
    """
    try:
        # 确定目标URL
        target_url = victim_url
        
        # 如果URL是旧的本地测试URL或为空，使用Docker容器URL
        if victim_url == "http://127.0.0.1:8005" or not victim_url:
            # 尝试从phishing_email_json中解析目标信息
            try:
                email_data = json.loads(phishing_email_json)
                target_name = email_data.get("recipient", "").split("<")[0].strip() or email_data.get("target_name", "")
                
                # 根据目标用户名选择不同的容器
                if "alice" in target_name.lower():
                    target_url = VICTIM_HOST_URLS["alice"]
                elif "bob" in target_name.lower():
                    target_url = VICTIM_HOST_URLS["bob"]
                else:
                    # 默认使用alice容器
                    target_url = VICTIM_HOST_URLS["default"]
            except Exception as e:
                print(f"解析phishing_email_json失败: {e}，使用默认URL")
                target_url = VICTIM_HOST_URLS["default"]
        
        print(f"选择目标URL: {target_url}")

        # 记录工具开始执行
        await attack_log_handler.log_tool_start("send_payload_to_victim", {"victim_url": target_url})

        # 调用攻击服务中的send_payload_to_victim工具
        # 注意：我们需要确保攻击服务中有这个工具
        async with attack_service_client.client as client:
            # 构建参数
            args = {
                'victim_url': target_url,
                'phishing_email_json': phishing_email_json
            }

            # 调用工具
            response = await client.call_tool(
                "send_payload_to_victim",
                arguments=args
            )

            # 从CallToolResult对象中安全地提取文本
            result = "\n".join([b.text for b in response.content if hasattr(b, "text")])

            # 记录工具执行完成
            await attack_log_handler.log_tool_end("send_payload_to_victim", result)

            return result
    except Exception as e:
        return f"执行send_payload_to_victim工具时出错: {e}"
    except Exception as e:
        return f"执行send_payload_to_victim工具时出错: {e}"

@tool
async def get_network_info(session_id: str) -> str:
    """获取当前会话可达的内网主机信息。"""
    try:
        async with attack_service_client.client as client:
            response = await client.call_tool(
                "get_network_info",
                arguments={"session_id": session_id}
            )
        return "\n".join([b.text for b in response.content if hasattr(b, "text")])
    except Exception as e:
        return f"执行get_network_info工具时出错: {e}"

@tool
async def search_exploit(service: str, version: str) -> str:
    """搜索可利用漏洞模块。"""
    try:
        async with attack_service_client.client as client:
            response = await client.call_tool(
                "search_exploit",
                arguments={"service": service, "version": version}
            )
        return "\n".join([b.text for b in response.content if hasattr(b, "text")])
    except Exception as e:
        return f"执行search_exploit工具时出错: {e}"

@tool
async def execute_exploit_module(module: str, target: str) -> str:
    """执行指定漏洞利用模块，返回 session_id"""
    try:
        async with attack_service_client.client as client:
            response = await client.call_tool(
                "execute_exploit_module",
                arguments={"module": module, "target": target}
            )
        return "\n".join([b.text for b in response.content if hasattr(b, "text")])
    except Exception as e:
        return f"执行execute_exploit_module工具时出错: {e}"

@tool
async def execute_shell_command(session_id: str, command: str) -> str:
    """在已控目标上执行命令。"""
    try:
        async with attack_service_client.client as client:
            response = await client.call_tool(
                "execute_shell_command",
                arguments={"session_id": session_id, "command": command}
            )
        return "\n".join([b.text for b in response.content if hasattr(b, "text")])
    except Exception as e:
        return f"执行execute_shell_command工具时出错: {e}"

# 将所有定义好的工具放入一个列表
tools = [
    run_nmap,
    fetch_url_content,
    craft_phishing_email,
    send_payload_to_victim,
    search_exploit,
    execute_exploit_module,
    execute_shell_command,
    get_network_info,
]

# --- 新增：社会工程学工具封装 -------------------------------------------
@tool
async def craft_doc_with_enable_macro(victim_name: str) -> str:
    """生成诱导启用宏的文档下载链接。"""
    async with attack_service_client.client as client:
        res = await client.call_tool("craft_doc_with_enable_macro", arguments={"victim_name": victim_name})
    return "\n".join([b.text for b in res.content if hasattr(b, "text")])

@tool
async def simulate_sextortion_email(victim_name: str, position: str) -> str:
    """生成性勒索邮件内容。"""
    async with attack_service_client.client as client:
        res = await client.call_tool("simulate_sextortion_email", arguments={"victim_name": victim_name, "position": position})
    return "\n".join([b.text for b in res.content if hasattr(b, "text")])

@tool
async def craft_affinity_chat(common_interest: str, first_question: str = "能加个微信聊细节吗？") -> str:
    """基于共同爱好生成亲和聊天脚本并返回对话开场白。"""
    async with attack_service_client.client as client:
        res = await client.call_tool("craft_affinity_chat", arguments={"common_interest": common_interest, "first_question": first_question})
    return "\n".join([b.text for b in res.content if hasattr(b, "text")])

@tool
async def craft_fake_job_offer(target_name: str, desired_role: str, salary_range: str, form_link: str) -> str:
    """生成虚假的招聘信息，诱导受害者填写个人信息。"""
    async with attack_service_client.client as client:
        res = await client.call_tool(
            "craft_fake_job_offer",
            arguments={
                "target_name": target_name,
                "desired_role": desired_role,
                "salary_range": salary_range,
                "form_link": form_link,
            },
        )
    return "\n".join([b.text for b in res.content if hasattr(b, "text")])
# --------------------------------------------------------------------------

# Append new tools to tools list
tools.extend([
    craft_doc_with_enable_macro,
    simulate_sextortion_email,
    craft_affinity_chat,
    craft_fake_job_offer,
])

# ------------------ Helper: 生成随机社会工程学载荷 ------------------

async def _generate_random_social_payload(victim_name: str, company_name: str):
    tactics = [
        ("phishing_email", craft_phishing_email),
        ("enable_macro", craft_doc_with_enable_macro),
        ("sextortion", simulate_sextortion_email),
        ("affinity_chat", craft_affinity_chat),
        ("fake_job_offer", craft_fake_job_offer),
    ]
    tactic_name, tool_fn = random.choice(tactics)

    if tactic_name == "phishing_email":
        result = await tool_fn(target_name=victim_name, company=company_name, malicious_link="http://evil.example.com/login")
        payload = {
            "tactic": tactic_name,
            "subject": "钓鱼邮件",
            "body": result,
            "malicious_link": "http://evil.example.com/login",
        }
    elif tactic_name == "enable_macro":
        link = await tool_fn(victim_name=victim_name)
        payload = {"tactic": tactic_name, "subject": "启用宏文档", "body": link, "malicious_link": None}
    elif tactic_name == "sextortion":
        body = await tool_fn(victim_name=victim_name, position="Manager")
        payload = {"tactic": tactic_name, "subject": "紧急！", "body": body, "malicious_link": None}
    elif tactic_name == "affinity_chat":
        body = await tool_fn(common_interest="摄影")
        payload = {"tactic": tactic_name, "subject": "你好！", "body": body, "malicious_link": None}
    else:  # fake_job_offer
        body = await tool_fn(target_name=victim_name, desired_role="DevOps", salary_range="60W-80W", form_link="https://tinyurl.com/apply")
        payload = {"tactic": tactic_name, "subject": "高薪职位", "body": body, "malicious_link": None}

    return payload

# -------------------- 发送社会工程学载荷 -----------------------------

@tool
async def send_payload_to_victim_social(victim_url: str, payload: dict) -> str:
    """将社会工程学载荷 POST 至 /receive_social。"""
    try:
        # 确定目标URL
        target_url = victim_url
        
        # 如果URL是旧的本地测试URL或为空，使用Docker容器URL
        if victim_url == "http://127.0.0.1:8005" or not victim_url:
            # 尝试从payload中解析目标信息
            target_name = payload.get("target_name", "").lower()
            
            # 根据目标用户名选择不同的容器
            if "alice" in target_name:
                target_url = VICTIM_HOST_URLS["alice"]
            elif "bob" in target_name:
                target_url = VICTIM_HOST_URLS["bob"]
            else:
                # 默认使用alice容器
                target_url = VICTIM_HOST_URLS["default"]
        
        print(f"选择社会工程学攻击目标URL: {target_url}")
        
        # 调用攻击服务中的send_payload_to_victim_social工具
        async with attack_service_client.client as client:
            # 构建参数
            args = {
                'victim_url': target_url,
                'payload': payload
            }
            
            # 调用工具
            response = await client.call_tool(
                "send_payload_to_victim_social",
                arguments=args
            )
            
            # 从CallToolResult对象中安全地提取文本
            return "\n".join([b.text for b in response.content if hasattr(b, "text")])
    except Exception as e:
        return f"执行send_payload_to_victim_social工具时出错: {e}"

tools.append(send_payload_to_victim_social)
# --------------------------------------------------------------------

# --- 定义Agent ---
# 这是给Agent的指令，告诉它它的角色、能力和目标
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """你是一个专业的、自动化的网络攻击代理。
你的任务是接收一个目标（target_host），然后自主执行一个完整的钓鱼攻击流程。
攻击流程包括：
1.  **侦察**: 使用工具扫描目标，发现开放的服务，并抓取信息（例如，从web端点获取元数据）来识别目标的详细信息，包括公司名称、用户名、部门、职位等。如果nmap工具不可用或失败，请继续尝试使用fetch_url_content工具。

2.  **规划**: 根据你侦察到的信息，准备进行钓鱼邮件攻击。分析目标的部门和职位，选择最合适的钓鱼邮件类型。

3.  **执行**: 调用 `craft_phishing_email` 工具来生成一封针对性的邮件。确保传入所有可用的目标信息，包括：
    - target_name: 目标用户名
    - company: 目标公司名称
    - malicious_link: 恶意链接（使用 'http://evil-corp-phishing.com/login'）
    - department: 目标部门（如果有）
    - role: 目标职位（如果有）
    - email: 目标邮箱（如果有）
    
    该工具会返回一个JSON字符串，包含钓鱼邮件的详细信息。

4.  **交付**: 调用 `send_payload_to_victim` 工具，将生成的钓鱼邮件发送给受害者。注意，该工具现在需要两个参数：
    - victim_url: 受害者URL
    - phishing_email_json: 由craft_phishing_email工具生成的JSON字符串
    
    不要尝试分解JSON字符串，直接将craft_phishing_email的完整输出传递给send_payload_to_victim。

5.  **权限提升**: 一旦获取到受害者凭据，调用 `search_exploit` → `execute_exploit_module` 获取 `session_id`。

6.  **横向移动**: 使用 `get_network_info` 枚举内网，再对其中一台主机执行 `execute_shell_command` (例如 `cat /etc/passwd`)。

7.  **报告**: 把横向移动的最终命令输出作为最终答案。

你必须严格按照工具的定义来使用它们，并自主完成整个流程。特别注意工具参数的变化，确保正确传递参数。"""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- FastAPI应用 ---
app = FastAPI(
    title="攻击智能体 (Attack Agent)",
    description="接收高层指令，自主执行侦察、规划和攻击的完整流程。"
)

class AttackRequest(BaseModel):
    target_host: str = Field(description="攻击目标的主机地址，例如 http://127.0.0.1:8005")

@app.post("/execute_full_attack")
async def execute_full_attack(request: AttackRequest):
    """
    接收来自中央智能体的指令，启动一次完整的、自主的攻击。
    现在会获取更多目标信息，生成更具针对性的钓鱼邮件。
    """
    # 确定目标主机URL
    target_host = request.target_host
    
    # 如果目标主机是Docker容器，使用对应的URL
    if "alice" in target_host.lower() or "192.168.100.9" in target_host:
        target_host = VICTIM_HOST_URLS["alice"]
    elif "bob" in target_host.lower() or "192.168.100.34" in target_host:
        target_host = VICTIM_HOST_URLS["bob"]
    else:
        # 默认使用本地测试URL
        target_host = VICTIM_HOST_URLS["default"]
    
    logger.info(f"选择目标主机URL: {target_host}")
    await send_standardized_log("info", "攻击智能体", "攻击者扫描防火墙")
    
    # 构造一个清晰的指令，让Agent开始工作
    input_prompt = f"""
    开始对目标 {target_host} 执行一次完整的钓鱼攻击。
    
    首先，你需要通过目标的 /metadata 端点进行侦察，获取尽可能多的信息，包括：
    - 公司名称
    - 用户名
    - 部门
    - 职位
    - 邮箱
    - 系统信息
    - 内核版本
    - 主机类型
    
    然后，利用这些信息为目标制作一封高度定制化的钓鱼邮件。邮件内容应该：
    1. 针对目标的部门和职位定制
    2. 引用目标可能使用的系统或软件
    3. 使用与目标公司相关的术语
    4. 包含恶意链接 'http://evil-corp-phishing.com/login'
    
    最后，你必须调用 `send_payload_to_victim` 工具将邮件发送给目标，并报告最终结果。
    
    记住，越是针对性强的钓鱼邮件，成功率越高。利用所有可用的信息使攻击更加精准。
    """
    try:
        # 发送侦察开始日志
        await send_standardized_log("info", "攻击智能体", "攻击者扫描防火墙")

        # 运行Agent，它现在会自主完成所有步骤，包括最后的交付
        attack_result = await agent_executor.ainvoke({"input": input_prompt})

        # 发送攻击完成日志
        attack_log_handler.advance_stage("actions_on_objectives", 100)
        await send_standardized_log("success", "攻击智能体", "攻击者完全攻陷目标系统")
        
        # 解析输出并发送详细日志
        output_lines = attack_result.get("output", "").split("\n")
        for line in output_lines:
            if line.strip():
                await send_log_to_backend("info", "攻击结果", line.strip())

        # 直接返回Agent的最终输出
        return {"status": "success", "detail": "Agent finished execution.", "final_output": attack_result.get("output")}

    except Exception as e:
        error_msg = f"攻击流程执行失败: {str(e)}"
        logger.error(error_msg)
        await send_log_to_backend("error", "攻击智能体", error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# --- 新增 API: 随机社会工程学攻击 -----------------------------------------
class SocialEngRequest(BaseModel):
    victim_name: str = "Alice"
    company: str = "ACME_CORP"

@app.post("/execute_social_engineering")
async def execute_social_engineering(req: SocialEngRequest):
    """随机选择一种社会工程学技巧并生成相应 payload 返回。"""
    tactics = [
        ("phishing_email", craft_phishing_email),
        ("enable_macro", craft_doc_with_enable_macro),
        ("sextortion", simulate_sextortion_email),
        ("affinity_chat", craft_affinity_chat),
        ("fake_job_offer", craft_fake_job_offer),
    ]
    tactic_name, tool_fn = random.choice(tactics)

    if tactic_name == "phishing_email":
        result = await tool_fn(target_name=req.victim_name, company=req.company, malicious_link="http://evil.example.com/login")
    elif tactic_name == "enable_macro":
        result = await tool_fn(victim_name=req.victim_name)
    elif tactic_name == "sextortion":
        result = await tool_fn(victim_name=req.victim_name, position="CTO")
    elif tactic_name == "affinity_chat":
        result = await tool_fn(common_interest="摇滚音乐")
    else:  # fake_job_offer
        result = await tool_fn(
            target_name=req.victim_name,
            desired_role="Senior DevOps Engineer",
            salary_range="¥70万-90万",
            form_link="https://tinyurl.com/apply-now",
        )

    return {"tactic": tactic_name, "payload": result}
# --------------------------------------------------------------------------

# 新增端点：完整随机社会工程学攻击（无需 LangChain 规划）
class RandomAttackReq(BaseModel):
    victim_url: str = VICTIM_HOST_URLS["alice"]  # 默认使用alice容器
    victim_name: str = "Alice"
    company: str = "ACME_CORP"


@app.post("/execute_random_social_attack")
async def execute_random_social_attack(req: RandomAttackReq):
    payload = await _generate_random_social_payload(req.victim_name, req.company)
    result = await send_payload_to_victim_social(req.victim_url, payload)
    return {"tactic": payload["tactic"], "send_result": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004) 