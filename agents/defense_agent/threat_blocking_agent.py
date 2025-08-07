"""
威胁阻断智能体 (Threat Blocking Agent)
负责实时检测和阻断正在进行的攻击
"""

import os
import httpx
import json
import asyncio
import logging
import websockets.client
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

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
logger = logging.getLogger("threat-blocking-agent")

# --- 后端WebSocket连接 ---
BACKEND_WS_URL = "ws://localhost:8080/ws/logs"
backend_ws = None

async def connect_to_backend():
    """连接到后端WebSocket"""
    global backend_ws
    try:
        if backend_ws:
            try:
                await backend_ws.close()
            except Exception:
                pass
            backend_ws = None
            
        backend_ws = await websockets.client.connect(BACKEND_WS_URL)
        
        await backend_ws.send(json.dumps({
            "level": "info",
            "source": "威胁阻断智能体",
            "message": "WebSocket连接已建立"
        }))
        
        logger.info(f"已连接到后端WebSocket: {BACKEND_WS_URL}")
        return True
    except Exception as e:
        logger.error(f"连接后端WebSocket失败: {e}")
        return False

# 日志去重缓存
_log_cache = {}
_log_cache_timeout = 5.0  # 5秒内的相同日志不重复发送

async def send_log_to_backend(level: str, source: str, message: str, defense_info: dict = None):
    """发送防御日志到后端WebSocket（带去重功能）"""
    global backend_ws, _log_cache
    
    # 日志去重检查
    import hashlib
    current_time = asyncio.get_event_loop().time()
    log_key = hashlib.md5(f"{source}:{message}".encode('utf-8')).hexdigest()
    
    # 检查是否是重复日志
    if log_key in _log_cache:
        last_time = _log_cache[log_key]
        if current_time - last_time < _log_cache_timeout:
            logger.debug(f"跳过重复日志: {message[:50]}...")
            return
    
    # 记录日志时间
    _log_cache[log_key] = current_time
    
    # 清理过期的缓存条目
    expired_keys = [k for k, t in _log_cache.items() if current_time - t > _log_cache_timeout * 2]
    for k in expired_keys:
        del _log_cache[k]
    
    log_data = {
        "timestamp": current_time,
        "level": level,
        "source": source,
        "message": message,
        "defense_info": defense_info or {}
    }
    
    try:
        if backend_ws is None:
            await connect_to_backend()
        
        try:
            if backend_ws:
                await backend_ws.send(json.dumps(log_data, ensure_ascii=False))
                logger.debug(f"已发送防御日志到后端: {message}")
        except Exception as e:
            logger.warning(f"发送消息失败，尝试重新连接: {e}")
            await connect_to_backend()
            
            try:
                if backend_ws:
                    await backend_ws.send(json.dumps(log_data, ensure_ascii=False))
            except Exception:
                pass
    except Exception as e:
        logger.error(f"发送日志到后端WebSocket失败: {e}")

# --- 环境变量和配置 ---
dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

THREAT_BLOCKING_SERVICE_URL = os.getenv("THREAT_BLOCKING_SERVICE_URL", "http://127.0.0.1:8008/mcp/")

# --- 初始化LLM和工具 ---
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    logger.warning("DEEPSEEK_API_KEY未设置，使用默认密钥")
    api_key = "sk-default-key"

try:
    llm = ChatDeepSeek(model="deepseek-chat", api_key=api_key)
    logger.info("ChatDeepSeek初始化成功")
except Exception as e:
    logger.error(f"ChatDeepSeek初始化失败: {e}")
    # 使用一个简单的模拟LLM
    llm = None

# 使用FastMCP客户端连接到威胁阻断服务
try:
    threat_blocking_service = FastMCP.as_proxy(THREAT_BLOCKING_SERVICE_URL)
    logger.info(f"FastMCP代理连接成功: {THREAT_BLOCKING_SERVICE_URL}")
except Exception as e:
    logger.error(f"FastMCP代理连接失败: {e}")
    threat_blocking_service = None

# --- 为Agent定义工具 ---
@tool
async def detect_network_threats(target_network: str, scan_duration: int = 30) -> str:
    """检测网络中的威胁活动"""
    try:
        await send_log_to_backend("info", "威胁阻断智能体", f"开始检测网络威胁: {target_network}")
        
        async with threat_blocking_service.client as client:
            response = await client.call_tool(
                "detect_network_threats",
                arguments={'target_network': target_network, 'scan_duration': scan_duration}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        # 解析结果并发送详细日志
        try:
            threat_data = json.loads(result)
            threats_found = threat_data.get("threats_found", 0)
            if threats_found > 0:
                await send_log_to_backend("warning", "威胁阻断智能体", 
                                        f"检测到 {threats_found} 个威胁，准备执行阻断措施")
            else:
                await send_log_to_backend("info", "威胁阻断智能体", "网络扫描完成，未发现威胁")
        except:
            pass
        
        return result
    except Exception as e:
        await send_log_to_backend("error", "威胁阻断智能体", f"威胁检测失败: {e}")
        return f"执行威胁检测时出错: {e}"

@tool
async def block_malicious_ip(ip_address: str, threat_type: str, duration: int = None) -> str:
    """阻断恶意IP地址"""
    try:
        await send_log_to_backend("info", "威胁阻断智能体", f"正在阻断恶意IP: {ip_address}")
        
        async with threat_blocking_service.client as client:
            response = await client.call_tool(
                "block_malicious_ip",
                arguments={'ip_address': ip_address, 'threat_type': threat_type, 'duration': duration}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        await send_log_to_backend("success", "威胁阻断智能体", f"成功阻断恶意IP {ip_address}")
        return result
    except Exception as e:
        await send_log_to_backend("error", "威胁阻断智能体", f"IP阻断失败: {e}")
        return f"执行IP阻断时出错: {e}"

@tool
async def isolate_infected_host(host_ip: str, isolation_type: str = "vlan") -> str:
    """隔离被感染的主机"""
    try:
        await send_log_to_backend("info", "威胁阻断智能体", f"正在隔离被感染主机: {host_ip}")
        
        async with threat_blocking_service.client as client:
            response = await client.call_tool(
                "isolate_infected_host",
                arguments={'host_ip': host_ip, 'isolation_type': isolation_type}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        await send_log_to_backend("success", "威胁阻断智能体", f"成功隔离被感染主机 {host_ip}")
        return result
    except Exception as e:
        await send_log_to_backend("error", "威胁阻断智能体", f"主机隔离失败: {e}")
        return f"执行主机隔离时出错: {e}"

@tool
async def block_malicious_domain(domain: str, category: str = "malware") -> str:
    """阻断恶意域名访问"""
    try:
        await send_log_to_backend("info", "威胁阻断智能体", f"正在阻断恶意域名: {domain}")
        
        async with threat_blocking_service.client as client:
            response = await client.call_tool(
                "block_malicious_domain",
                arguments={'domain': domain, 'category': category}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        await send_log_to_backend("success", "威胁阻断智能体", f"成功阻断恶意域名 {domain}")
        return result
    except Exception as e:
        await send_log_to_backend("error", "威胁阻断智能体", f"域名阻断失败: {e}")
        return f"执行域名阻断时出错: {e}"

@tool
async def get_threat_intelligence() -> str:
    """获取最新威胁情报"""
    try:
        await send_log_to_backend("info", "威胁阻断智能体", "正在获取最新威胁情报")
        
        async with threat_blocking_service.client as client:
            response = await client.call_tool(
                "get_threat_intelligence",
                arguments={}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        await send_log_to_backend("info", "威胁阻断智能体", "威胁情报更新完成")
        return result
    except Exception as e:
        await send_log_to_backend("error", "威胁阻断智能体", f"威胁情报获取失败: {e}")
        return f"执行威胁情报获取时出错: {e}"

@tool
async def get_firewall_status() -> str:
    """获取防火墙当前状态"""
    try:
        await send_log_to_backend("info", "威胁阻断智能体", "正在查询防火墙状态")
        
        async with threat_blocking_service.client as client:
            response = await client.call_tool(
                "get_firewall_status",
                arguments={}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        await send_log_to_backend("info", "威胁阻断智能体", "防火墙状态查询完成")
        return result
    except Exception as e:
        await send_log_to_backend("error", "威胁阻断智能体", f"防火墙状态查询失败: {e}")
        return f"执行防火墙状态查询时出错: {e}"

@tool
async def add_to_firewall_blacklist(ip_address: str, reason: str = "恶意活动") -> str:
    """将IP地址添加到防火墙黑名单"""
    try:
        await send_log_to_backend("warning", "威胁阻断智能体", f"正在将恶意IP {ip_address} 添加到黑名单")
        
        async with threat_blocking_service.client as client:
            response = await client.call_tool(
                "add_to_firewall_blacklist",
                arguments={'ip_address': ip_address, 'reason': reason}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        await send_log_to_backend("success", "威胁阻断智能体", f"成功阻断恶意IP {ip_address}")
        return result
    except Exception as e:
        await send_log_to_backend("error", "威胁阻断智能体", f"IP黑名单添加失败: {e}")
        return f"执行IP黑名单添加时出错: {e}"

@tool
async def remove_from_firewall_blacklist(ip_address: str) -> str:
    """从防火墙黑名单中移除IP地址"""
    try:
        await send_log_to_backend("info", "威胁阻断智能体", f"正在从黑名单中移除IP {ip_address}")
        
        async with threat_blocking_service.client as client:
            response = await client.call_tool(
                "remove_from_firewall_blacklist",
                arguments={'ip_address': ip_address}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        await send_log_to_backend("success", "威胁阻断智能体", f"成功从黑名单移除IP {ip_address}")
        return result
    except Exception as e:
        await send_log_to_backend("error", "威胁阻断智能体", f"IP黑名单移除失败: {e}")
        return f"执行IP黑名单移除时出错: {e}"

@tool
async def add_to_firewall_whitelist(ip_address: str, description: str = "可信IP") -> str:
    """将IP地址添加到防火墙白名单"""
    try:
        await send_log_to_backend("info", "威胁阻断智能体", f"正在将可信IP {ip_address} 添加到白名单")
        
        async with threat_blocking_service.client as client:
            response = await client.call_tool(
                "add_to_firewall_whitelist",
                arguments={'ip_address': ip_address, 'description': description}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        await send_log_to_backend("success", "威胁阻断智能体", f"成功将IP {ip_address} 添加到白名单")
        return result
    except Exception as e:
        await send_log_to_backend("error", "威胁阻断智能体", f"IP白名单添加失败: {e}")
        return f"执行IP白名单添加时出错: {e}"

@tool
async def bulk_block_ips(ip_list: List[str], reason: str = "批量威胁阻断") -> str:
    """批量阻断IP地址"""
    try:
        await send_log_to_backend("warning", "威胁阻断智能体", f"正在批量阻断 {len(ip_list)} 个恶意IP")
        
        async with threat_blocking_service.client as client:
            response = await client.call_tool(
                "bulk_block_ips",
                arguments={'ip_list': ip_list, 'reason': reason}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        await send_log_to_backend("success", "威胁阻断智能体", f"成功批量阻断 {len(ip_list)} 个恶意IP")
        return result
    except Exception as e:
        await send_log_to_backend("error", "威胁阻断智能体", f"批量IP阻断失败: {e}")
        return f"执行批量IP阻断时出错: {e}"

@tool
async def emergency_network_lockdown(reason: str, duration: int = 1800) -> str:
    """紧急网络封锁"""
    try:
        await send_log_to_backend("warning", "威胁阻断智能体", f"启动紧急网络封锁: {reason}")
        
        async with threat_blocking_service.client as client:
            response = await client.call_tool(
                "emergency_network_lockdown",
                arguments={'reason': reason, 'duration': duration}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        await send_log_to_backend("critical", "威胁阻断智能体", "紧急网络封锁已激活")
        return result
    except Exception as e:
        await send_log_to_backend("error", "威胁阻断智能体", f"紧急封锁失败: {e}")
        return f"执行紧急网络封锁时出错: {e}"

# 工具列表
tools = [
    detect_network_threats,
    block_malicious_ip,
    isolate_infected_host,
    block_malicious_domain,
    get_threat_intelligence,
    get_firewall_status,
    add_to_firewall_blacklist,
    remove_from_firewall_blacklist,
    add_to_firewall_whitelist,
    bulk_block_ips,
    emergency_network_lockdown
]

# --- 定义Agent ---
prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的威胁阻断智能体，负责实时检测和阻断网络安全威胁。

你的主要职责：
1. **实时监控**: 持续监控网络流量和系统活动，识别潜在威胁
2. **快速响应**: 一旦检测到威胁，立即采取阻断措施
3. **威胁分析**: 分析威胁类型和严重程度，选择合适的应对策略
4. **防火墙管理**: 动态管理防火墙黑白名单，实现精准阻断
5. **防护加固**: 根据威胁情报更新防护策略

工作流程：
1. 首先使用 detect_network_threats 检测当前网络威胁
2. 使用 get_firewall_status 查看当前防火墙状态
3. 根据检测结果分析威胁类型和严重程度
4. 选择合适的阻断措施：
   - 对恶意IP使用 add_to_firewall_blacklist 添加到黑名单
   - 对可信IP使用 add_to_firewall_whitelist 添加到白名单
   - 批量威胁使用 bulk_block_ips 进行批量阻断
   - 对被感染主机使用 isolate_infected_host
   - 对恶意域名使用 block_malicious_domain
   - 紧急情况下使用 emergency_network_lockdown
5. 获取最新威胁情报以更新防护策略

响应原则：
- 优先保护关键资产和数据
- 快速响应，最小化业务影响
- 记录所有防护行动以供后续分析
- 与其他防御组件协调配合

请根据接收到的威胁信息，制定并执行相应的阻断策略。"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# 创建Agent
try:
    if llm is not None:
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        logger.info("威胁阻断智能体创建成功")
    else:
        agent_executor = None
        logger.warning("LLM未初始化，智能体功能受限")
except Exception as e:
    logger.error(f"智能体创建失败: {e}")
    agent_executor = None

# --- FastAPI应用 ---
app = FastAPI(
    title="威胁阻断智能体",
    description="负责实时检测和阻断网络安全威胁"
)

class ThreatBlockingRequest(BaseModel):
    target_network: str = Field(description="目标网络段")
    threat_level: str = Field(default="medium", description="威胁级别")
    auto_block: bool = Field(default=True, description="是否自动阻断")

@app.post("/execute_threat_blocking")
async def execute_threat_blocking(request: ThreatBlockingRequest):
    """执行威胁阻断任务"""
    try:
        await send_log_to_backend("info", "威胁阻断智能体", 
                                f"收到威胁阻断任务: {request.target_network}")
        
        # 构建输入
        input_text = f"""
        目标网络: {request.target_network}
        威胁级别: {request.threat_level}
        自动阻断: {'是' if request.auto_block else '否'}
        
        请执行以下任务：
        1. 检测目标网络中的威胁活动
        2. 分析威胁类型和严重程度
        3. 根据威胁级别采取相应的阻断措施
        4. 更新威胁情报和防护策略
        
        如果检测到高危威胁且启用自动阻断，请立即执行阻断操作。
        """
        
        # 执行Agent
        if agent_executor is not None:
            result = await agent_executor.ainvoke({"input": input_text})
        else:
            # 如果智能体未初始化，返回模拟结果
            result = {
                "output": "威胁阻断智能体当前处于模拟模式，请配置DEEPSEEK_API_KEY以启用完整功能。"
            }
        
        await send_log_to_backend("success", "威胁阻断智能体", "威胁阻断任务执行完成")
        
        return {
            "status": "success",
            "message": "威胁阻断任务执行完成",
            "result": result["output"],
            "target_network": request.target_network
        }
        
    except Exception as e:
        error_msg = f"威胁阻断任务执行失败: {e}"
        logger.error(error_msg)
        await send_log_to_backend("error", "威胁阻断智能体", error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/status")
async def get_status():
    """获取智能体状态"""
    return {
        "agent": "威胁阻断智能体",
        "status": "active",
        "service_url": THREAT_BLOCKING_SERVICE_URL,
        "capabilities": [
            "网络威胁检测",
            "恶意IP阻断", 
            "主机隔离",
            "域名阻断",
            "威胁情报获取",
            "紧急网络封锁"
        ]
    }

# --- 主执行 ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)