import os
import httpx
import json
import logging
import asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from typing import List, Dict, Any, Optional
import websockets.client

# --- 设置日志 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("central-agent")

# --- 环境变量 ---
dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

# --- 初始化LLM ---
llm = ChatDeepSeek(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))

# --- FastAPI应用 ---
app = FastAPI(
    title="中央智能体 (Central Agent)",
    description="负责接收高层用户指令，分析需求，并将其调度给专门的执行智能体。"
)

# --- 配置 ---
ATTACK_AGENT_URL = "http://127.0.0.1:8004/execute_full_attack"
SOCIAL_ATTACK_AGENT_URL = "http://127.0.0.1:8004/execute_random_social_attack"

# --- 存储攻击进度的全局变量 ---
attack_progress = []
attack_status = "idle"  # idle, analyzing, executing, completed, failed
connected_clients = []

# --- Pydantic模型 ---
class CommandRequest(BaseModel):
    command: str
    target_host: str  # 需要明确攻击目标
    attack_type: Optional[str] = "auto"  # 攻击类型：auto, phishing, etc.

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
            "source": "中央智能体",
            "message": "WebSocket连接已建立"
        }))
        
        logger.info(f"已连接到后端WebSocket: {BACKEND_WS_URL}")
        return True
    except Exception as e:
        logger.error(f"连接后端WebSocket失败: {e}")
        return False

# --- WebSocket连接管理 ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            # 保持连接活跃
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

# --- 广播攻击进度 ---
async def broadcast_progress(message: str, progress_type: str = "info"):
    """向所有连接的客户端广播攻击进度"""
    global attack_progress, backend_ws
    
    # 添加到进度列表
    timestamp = asyncio.get_event_loop().time()
    progress_item = {
        "timestamp": timestamp,
        "message": message,
        "type": progress_type,
        "source": "中央智能体",
        "level": progress_type
    }
    attack_progress.append(progress_item)
    
    # 广播给所有客户端
    if connected_clients:
        for client in connected_clients:
            try:
                await client.send_json(progress_item)
            except Exception as e:
                logger.error(f"广播进度失败: {e}")
    
    # 发送到后端WebSocket
    try:
        # 检查连接是否存在或是否需要重新连接
        if backend_ws is None:
            await connect_to_backend()
        
        # 使用try/except来检查连接状态
        try:
            if backend_ws:
                await backend_ws.send(json.dumps(progress_item))
        except Exception as e:
            logger.warning(f"发送消息失败，尝试重新连接: {e}")
            await connect_to_backend()
            
            # 重试一次发送
            try:
                if backend_ws:
                    await backend_ws.send(json.dumps(progress_item))
            except Exception:
                pass
    except Exception as e:
        logger.error(f"发送日志到后端WebSocket失败: {e}")

# --- API端点 ---
@app.post("/process_command")
async def process_command(request: CommandRequest):
    """
    接收并处理来自用户的命令。
    """
    global attack_status, attack_progress
    
    if request.command.lower() == "attack":
        # 重置攻击进度
        attack_progress = []
        attack_status = "analyzing"
        
        # 记录开始分析
        logger.info(f"收到攻击指令，目标: {request.target_host}")
        await broadcast_progress(f"收到攻击指令，目标: {request.target_host}", "start")
        
        # 使用LLM分析攻击目标和策略
        try:
            await broadcast_progress("中央智能体正在分析目标网络拓扑和可能的攻击路径...", "analyzing")
            
            # 使用DeepSeek分析攻击策略
            analysis_prompt = f"""
            作为网络安全专家，请分析以下目标的可能攻击路径和策略:
            
            目标主机: {request.target_host}
            
            请考虑:
            1. 最有效的攻击入口点
            2. 可能的漏洞利用方式
            3. 推荐的攻击类型（钓鱼、漏洞利用等）
            4. 攻击后的横向移动策略
            
            请提供简洁的分析结果。
            """
            
            analysis_result = await llm.ainvoke(analysis_prompt)
            analysis_text = analysis_result.content
            
            logger.info(f"攻击分析完成: {analysis_text}")
            await broadcast_progress("攻击分析完成，确定最佳攻击路径", "analysis_complete")
            await broadcast_progress(f"分析结果: {analysis_text}", "analysis_result")
            
            # 确定攻击类型
            attack_type = request.attack_type
            if attack_type == "auto":
                # 从分析结果中提取推荐的攻击类型
                if "钓鱼" in analysis_text or "社会工程" in analysis_text or "phishing" in analysis_text.lower():
                    attack_type = "phishing"
                elif "漏洞" in analysis_text or "exploit" in analysis_text.lower():
                    attack_type = "exploit"
                else:
                    attack_type = "phishing"  # 默认使用钓鱼攻击
            
            # 更新状态
            attack_status = "executing"
            await broadcast_progress(f"选择攻击类型: {attack_type}", "attack_type")
            await broadcast_progress("中央智能体正在向攻击智能体下达指令...", "command")
            
            # 构造对攻击智能体的请求
            attack_agent_payload = {"target_host": request.target_host}
            
            # 调用攻击智能体，并等待其完成整个攻击流程
            async with httpx.AsyncClient() as client:
                logger.info(f"向攻击智能体下达攻击指令，目标: {request.target_host}")
                await broadcast_progress("攻击指令已发送，攻击智能体开始执行...", "executing")
                
                response = await client.post(
                    ATTACK_AGENT_URL, 
                    json=attack_agent_payload, 
                    timeout=300  # Agent执行可能需要更长时间，增加超时
                )
                response.raise_for_status()
                
                # 获取攻击结果
                result = response.json()
                
                # 更新状态
                attack_status = "completed"
                logger.info(f"攻击执行完成: {result}")
                await broadcast_progress("攻击执行完成", "complete")
                
                # 分析攻击结果
                if "final_output" in result:
                    # 解析攻击智能体的输出
                    output_lines = result["final_output"].split('\n')
                    for line in output_lines:
                        if line.strip():
                            await broadcast_progress(line.strip(), "attack_output")
                
                # 返回攻击结果
                return {
                    "status": "success",
                    "message": "攻击执行完成",
                    "analysis": analysis_text,
                    "attack_type": attack_type,
                    "result": result
                }
                
        except httpx.RequestError as e:
            attack_status = "failed"
            error_msg = f"调用攻击智能体失败: {e}"
            logger.error(error_msg)
            await broadcast_progress(error_msg, "error")
            raise HTTPException(status_code=503, detail=error_msg)
        except Exception as e:
            attack_status = "failed"
            error_msg = f"攻击流程中发生未知错误: {e}"
            logger.error(error_msg)
            await broadcast_progress(error_msg, "error")
            raise HTTPException(status_code=500, detail=error_msg)
    
    return {"output": "指令未识别。目前仅支持 'attack' 指令。"}

@app.get("/attack/status")
async def get_attack_status():
    """获取当前攻击状态和进度"""
    return {
        "status": attack_status,
        "progress": attack_progress
    }

@app.get("/attack/progress")
async def get_attack_progress():
    """获取攻击进度详情"""
    return attack_progress


# --- 主执行 ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006) 