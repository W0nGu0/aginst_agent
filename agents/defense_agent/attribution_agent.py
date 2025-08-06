"""
攻击溯源智能体 (Attack Attribution Agent)
负责分析攻击路径，追踪攻击来源，提供取证支持
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
logger = logging.getLogger("attribution-agent")

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
            "source": "攻击溯源智能体",
            "message": "WebSocket连接已建立"
        }))
        
        logger.info(f"已连接到后端WebSocket: {BACKEND_WS_URL}")
        return True
    except Exception as e:
        logger.error(f"连接后端WebSocket失败: {e}")
        return False

async def send_log_to_backend(level: str, source: str, message: str, defense_info: dict = None):
    """发送防御日志到后端WebSocket"""
    global backend_ws
    
    log_data = {
        "timestamp": asyncio.get_event_loop().time(),
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

ATTRIBUTION_SERVICE_URL = os.getenv("ATTRIBUTION_SERVICE_URL", "http://127.0.0.1:8010/mcp/")

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

# 使用FastMCP客户端连接到攻击溯源服务
try:
    attribution_service = FastMCP.as_proxy(ATTRIBUTION_SERVICE_URL)
    logger.info(f"FastMCP代理连接成功: {ATTRIBUTION_SERVICE_URL}")
except Exception as e:
    logger.error(f"FastMCP代理连接失败: {e}")
    attribution_service = None

# --- 为Agent定义工具 ---
@tool
async def analyze_attack_timeline(start_time: str = None, end_time: str = None) -> str:
    """分析攻击时间线"""
    try:
        await send_log_to_backend("info", "攻击溯源智能体", "开始分析攻击时间线")
        
        async with attribution_service.client as client:
            response = await client.call_tool(
                "analyze_attack_timeline",
                arguments={'start_time': start_time, 'end_time': end_time}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        await send_log_to_backend("info", "攻击溯源智能体", "攻击时间线分析完成")
        return result
    except Exception as e:
        await send_log_to_backend("error", "攻击溯源智能体", f"时间线分析失败: {e}")
        return f"执行攻击时间线分析时出错: {e}"

@tool
async def trace_attack_path(source_node: str, target_node: str) -> str:
    """追踪攻击路径"""
    try:
        await send_log_to_backend("info", "攻击溯源智能体", f"正在追踪攻击路径: {source_node} -> {target_node}")
        
        async with attribution_service.client as client:
            response = await client.call_tool(
                "trace_attack_path",
                arguments={'source_node': source_node, 'target_node': target_node}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        await send_log_to_backend("success", "攻击溯源智能体", "攻击路径追踪完成")
        return result
    except Exception as e:
        await send_log_to_backend("error", "攻击溯源智能体", f"攻击路径追踪失败: {e}")
        return f"执行攻击路径追踪时出错: {e}"

@tool
async def generate_threat_actor_profile(indicators: List[str]) -> str:
    """生成威胁行为者画像"""
    try:
        await send_log_to_backend("info", "攻击溯源智能体", "正在生成威胁行为者画像")
        
        async with attribution_service.client as client:
            response = await client.call_tool(
                "generate_threat_actor_profile",
                arguments={'indicators': indicators}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        await send_log_to_backend("success", "攻击溯源智能体", "威胁行为者画像生成完成")
        return result
    except Exception as e:
        await send_log_to_backend("error", "攻击溯源智能体", f"威胁画像生成失败: {e}")
        return f"执行威胁行为者画像生成时出错: {e}"

@tool
async def collect_digital_evidence(evidence_type: str, target_system: str) -> str:
    """收集数字证据"""
    try:
        await send_log_to_backend("info", "攻击溯源智能体", f"正在收集数字证据: {evidence_type} from {target_system}")
        
        async with attribution_service.client as client:
            response = await client.call_tool(
                "collect_digital_evidence",
                arguments={'evidence_type': evidence_type, 'target_system': target_system}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        await send_log_to_backend("success", "攻击溯源智能体", f"数字证据收集完成: {evidence_type}")
        return result
    except Exception as e:
        await send_log_to_backend("error", "攻击溯源智能体", f"数字证据收集失败: {e}")
        return f"执行数字证据收集时出错: {e}"

@tool
async def analyze_malware_sample(sample_hash: str, analysis_type: str = "dynamic") -> str:
    """分析恶意软件样本"""
    try:
        await send_log_to_backend("info", "攻击溯源智能体", f"正在分析恶意软件样本: {sample_hash}")
        
        async with attribution_service.client as client:
            response = await client.call_tool(
                "analyze_malware_sample",
                arguments={'sample_hash': sample_hash, 'analysis_type': analysis_type}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        await send_log_to_backend("success", "攻击溯源智能体", "恶意软件样本分析完成")
        return result
    except Exception as e:
        await send_log_to_backend("error", "攻击溯源智能体", f"恶意软件分析失败: {e}")
        return f"执行恶意软件分析时出错: {e}"

@tool
async def generate_incident_report(incident_id: str, incident_type: str = "apt_attack") -> str:
    """生成事件报告"""
    try:
        await send_log_to_backend("info", "攻击溯源智能体", f"正在生成事件报告: {incident_id}")
        
        async with attribution_service.client as client:
            response = await client.call_tool(
                "generate_incident_report",
                arguments={'incident_id': incident_id, 'incident_type': incident_type}
            )
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        
        await send_log_to_backend("success", "攻击溯源智能体", "事件报告生成完成")
        return result
    except Exception as e:
        await send_log_to_backend("error", "攻击溯源智能体", f"事件报告生成失败: {e}")
        return f"执行事件报告生成时出错: {e}"

# 工具列表
tools = [
    analyze_attack_timeline,
    trace_attack_path,
    generate_threat_actor_profile,
    collect_digital_evidence,
    analyze_malware_sample,
    generate_incident_report
]

# --- 定义Agent ---
prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的攻击溯源智能体，负责分析攻击路径，追踪攻击来源，提供取证支持。

你的主要职责：
1. **攻击分析**: 分析攻击时间线和攻击路径，重构攻击过程
2. **威胁归因**: 识别攻击者身份和动机，生成威胁行为者画像
3. **证据收集**: 收集和保全数字证据，支持后续调查
4. **报告生成**: 生成详细的事件分析报告和建议

工作流程：
1. 使用 analyze_attack_timeline 分析攻击时间线
2. 使用 trace_attack_path 追踪具体的攻击路径
3. 收集威胁指标，使用 generate_threat_actor_profile 生成攻击者画像
4. 使用 collect_digital_evidence 收集关键证据
5. 如有恶意软件样本，使用 analyze_malware_sample 进行分析
6. 使用 generate_incident_report 生成综合事件报告

分析原则：
- 基于事实和证据进行分析，避免主观推测
- 保持证据链的完整性和可信度
- 关注攻击者的TTP（战术、技术、程序）
- 提供可操作的防护建议

请根据提供的攻击信息，进行全面的溯源分析和取证工作。"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# 创建Agent
try:
    if llm is not None:
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        logger.info("攻击溯源智能体创建成功")
    else:
        agent_executor = None
        logger.warning("LLM未初始化，智能体功能受限")
except Exception as e:
    logger.error(f"智能体创建失败: {e}")
    agent_executor = None

# --- FastAPI应用 ---
app = FastAPI(
    title="攻击溯源智能体",
    description="负责分析攻击路径，追踪攻击来源，提供取证支持"
)

class AttributionRequest(BaseModel):
    incident_id: str = Field(description="事件ID")
    attack_indicators: List[str] = Field(default=[], description="攻击指标列表")
    source_node: str = Field(default="internet", description="攻击源节点")
    target_node: str = Field(default="internal_db", description="攻击目标节点")
    evidence_types: List[str] = Field(default=["logs", "network"], description="需要收集的证据类型")

@app.post("/execute_attack_attribution")
async def execute_attack_attribution(request: AttributionRequest):
    """执行攻击溯源任务"""
    try:
        await send_log_to_backend("info", "攻击溯源智能体", 
                                f"收到攻击溯源任务: {request.incident_id}")
        
        # 构建输入
        input_text = f"""
        事件ID: {request.incident_id}
        攻击指标: {', '.join(request.attack_indicators) if request.attack_indicators else '待分析'}
        攻击源: {request.source_node}
        攻击目标: {request.target_node}
        证据类型: {', '.join(request.evidence_types)}
        
        请执行以下溯源分析任务：
        1. 分析攻击时间线，重构攻击过程
        2. 追踪从 {request.source_node} 到 {request.target_node} 的攻击路径
        3. 基于攻击指标生成威胁行为者画像
        4. 收集指定类型的数字证据
        5. 如发现恶意软件，进行深度分析
        6. 生成综合的事件分析报告
        
        重点关注攻击者的战术、技术和程序，为防护改进提供建议。
        """
        
        # 执行Agent
        if agent_executor is not None:
            result = await agent_executor.ainvoke({"input": input_text})
        else:
            # 如果智能体未初始化，返回模拟结果
            result = {
                "output": "攻击溯源智能体当前处于模拟模式，请配置DEEPSEEK_API_KEY以启用完整功能。"
            }
        
        await send_log_to_backend("success", "攻击溯源智能体", "攻击溯源任务执行完成")
        
        return {
            "status": "success",
            "message": "攻击溯源任务执行完成",
            "result": result["output"],
            "incident_id": request.incident_id
        }
        
    except Exception as e:
        error_msg = f"攻击溯源任务执行失败: {e}"
        logger.error(error_msg)
        await send_log_to_backend("error", "攻击溯源智能体", error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/status")
async def get_status():
    """获取智能体状态"""
    return {
        "agent": "攻击溯源智能体",
        "status": "active",
        "service_url": ATTRIBUTION_SERVICE_URL,
        "capabilities": [
            "攻击时间线分析",
            "攻击路径追踪",
            "威胁行为者画像",
            "数字证据收集",
            "恶意软件分析",
            "事件报告生成"
        ]
    }

# --- 主执行 ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8013)