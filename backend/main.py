from fastapi import FastAPI, HTTPException, APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
import subprocess
import os
import json
import logging
import httpx
import asyncio
from typing import List, Dict, Optional, Any, Set

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("topology-api")

# 模板目录
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "docker", "compose-templates")
DEFAULT_TEMPLATE = "company-topology.yml"

app = FastAPI(title="Topology Orchestrator API")

class TopologyAction(BaseModel):
    action: str  # start | stop | status
    template: Optional[str] = Field(None, description="Docker compose template name (without .yml extension)")
    config: Optional[Dict[str, Any]] = Field(None, description="Additional configuration parameters")

@app.post("/topology")
async def manage_topology(req: TopologyAction):
    """
    管理拓扑结构的主要端点
    
    - action=start: 启动指定模板的容器
    - action=stop: 停止当前运行的容器
    - action=status: 获取当前运行容器的状态
    """
    logger.info(f"Received topology action: {req.action}, template: {req.template}")
    
    # 确定使用的模板文件
    template = req.template or "company-topology"
    compose_file = os.path.join(TEMPLATES_DIR, f"{template}.yml")
    
    # 检查模板文件是否存在
    if not os.path.exists(compose_file):
        available_templates = [f.replace(".yml", "") for f in os.listdir(TEMPLATES_DIR) if f.endswith(".yml")]
        logger.error(f"Template {template} not found. Available templates: {available_templates}")
        raise HTTPException(
            status_code=404, 
            detail=f"Template '{template}' not found. Available templates: {available_templates}"
        )
    
    if req.action == "start":
        return _compose_up(compose_file)
    if req.action == "stop":
        return _compose_down(compose_file)
    if req.action == "status":
        return _compose_ps(compose_file)
    
    logger.error(f"Invalid action: {req.action}")
    raise HTTPException(status_code=400, detail=f"Invalid action: {req.action}")

def _compose_up(compose_file: str):
    """启动容器并返回详细信息"""
    try:
        logger.info(f"Starting containers using template: {compose_file}")
        subprocess.check_call(["docker-compose", "-f", compose_file, "up", "-d"])
        
        # 返回当前运行的服务信息，以便前端立即渲染容器
        services_info = _compose_ps(compose_file)
        return {"status": "started", **services_info}
    except subprocess.CalledProcessError as e:
        logger.error(f"Error starting containers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start containers: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def _compose_down(compose_file: str):
    """停止并移除容器"""
    try:
        logger.info(f"Stopping containers from template: {compose_file}")
        subprocess.check_call(["docker-compose", "-f", compose_file, "down", "--remove-orphans"])
        return {"status": "stopped"}
    except subprocess.CalledProcessError as e:
        logger.error(f"Error stopping containers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop containers: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def _compose_ps(compose_file: str):
    """获取所有容器的详细信息（包括运行中和已停止的）"""
    try:
        logger.info(f"Getting container status for template: {compose_file}")
        
        # 获取所有服务名称（不过滤状态）
        output = subprocess.check_output(["docker-compose", "-f", compose_file, "ps", "--services"])
        services: List[str] = output.decode().strip().split("\n") if output and output.decode().strip() else []
        
        if not services:
            logger.info("No services found")
            return {"running_services": [], "all_services": [], "failed_services": []}
        
        # 获取详细的容器信息
        all_services = []
        running_services = []
        failed_services = []
        
        for service in services:
            try:
                # 获取容器ID（可能为空，如果容器未创建）
                container_id_output = subprocess.check_output(
                    ["docker-compose", "-f", compose_file, "ps", "-q", service]
                ).decode().strip()
                
                if not container_id_output:
                    # 容器未创建，记录为失败
                    failed_services.append({
                        "name": service,
                        "status": "not_created",
                        "error": "Container not created"
                    })
                    continue
                    
                # 获取容器详细信息
                container_info = json.loads(subprocess.check_output(
                    ["docker", "inspect", container_id_output]
                ).decode())[0]
                
                # 提取关键信息
                networks = container_info.get("NetworkSettings", {}).get("Networks", {})
                ip_addresses = {}
                for network_name, network_config in networks.items():
                    ip_addresses[network_name] = network_config.get("IPAddress", "")
                
                # 检查容器状态
                state = container_info.get("State", {})
                status = "running" if state.get("Running", False) else "stopped"
                error_msg = state.get("Error", "") if status == "stopped" else ""
                
                # 构建服务信息
                service_info = {
                    "name": service,
                    "id": container_id_output,
                    "ip": next(iter(ip_addresses.values()), ""),  # 取第一个IP地址作为主IP
                    "networks": ip_addresses,
                    "status": status,
                    "image": container_info.get("Config", {}).get("Image", ""),
                    "created": container_info.get("Created", ""),
                    "ports": container_info.get("NetworkSettings", {}).get("Ports", {}),
                    "error": error_msg
                }
                
                all_services.append(service_info)
                
                if status == "running":
                    running_services.append(service_info)
                else:
                    failed_services.append(service_info)
                    
            except subprocess.CalledProcessError as e:
                # 处理命令执行错误
                failed_services.append({
                    "name": service,
                    "status": "error",
                    "error": str(e)
                })
            except Exception as e:
                # 处理其他错误
                failed_services.append({
                    "name": service,
                    "status": "error",
                    "error": str(e)
                })
        
        logger.info(f"Found {len(running_services)} running services, {len(failed_services)} failed services")
        return {
            "running_services": running_services,
            "all_services": all_services,
            "failed_services": failed_services
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting container status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get container status: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# WebSocket连接管理
connected_clients: Set[WebSocket] = set()

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket端点，用于实时推送日志"""
    await websocket.accept()
    connected_clients.add(websocket)
    logger.info(f"WebSocket客户端已连接，当前连接数: {len(connected_clients)}")
    
    # 发送一条欢迎消息
    welcome_message = {
        "timestamp": asyncio.get_event_loop().time(),
        "level": "info",
        "source": "系统",
        "message": "WebSocket连接已建立，可以接收实时日志"
    }
    await websocket.send_json(welcome_message)
    
    try:
        while True:
            # 保持连接活跃，等待客户端消息
            data = await websocket.receive_text()
            
            # 处理心跳消息
            if data == "ping":
                await websocket.send_text("pong")
                continue
                
            # 如果客户端发送了其他消息，可以在这里处理
            logger.debug(f"收到WebSocket消息: {data}")
            
            # 尝试解析JSON消息
            try:
                message = json.loads(data)
                # 如果是日志消息，广播给所有客户端
                if "level" in message and "source" in message and "message" in message:
                    await broadcast_log(message)
            except json.JSONDecodeError:
                logger.warning(f"收到非JSON格式的WebSocket消息: {data}")
            
    except WebSocketDisconnect:
        # 客户端断开连接
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        logger.info(f"WebSocket客户端已断开，当前连接数: {len(connected_clients)}")
    except Exception as e:
        # 其他异常
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        logger.error(f"WebSocket连接异常: {str(e)}")

async def broadcast_log(log_data: dict):
    """向所有连接的WebSocket客户端广播日志"""
    if not connected_clients:
        return
    
    # 添加时间戳
    if "timestamp" not in log_data:
        log_data["timestamp"] = asyncio.get_event_loop().time()
    
    # 广播消息
    disconnected_clients = set()
    for client in connected_clients:
        try:
            await client.send_json(log_data)
        except Exception as e:
            logger.error(f"向WebSocket客户端发送消息失败: {str(e)}")
            disconnected_clients.add(client)
    
    # 移除断开连接的客户端
    for client in disconnected_clients:
        if client in connected_clients:
            connected_clients.remove(client)

# -----------------------------
# Expose the same functionality under the /api prefix so that the
# frontend proxy (see vite.config.js) can reach it at /api/topology
# -----------------------------
api_router = APIRouter(prefix="/api")

@api_router.post("/topology")
async def manage_topology_api(req: TopologyAction):
    """Proxy endpoint matching the frontend expectation (POST /api/topology)."""
    return await manage_topology(req)

# 添加攻击智能体相关的API
class AttackRequest(BaseModel):
    target_host: str = Field(description="攻击目标的主机地址，例如 http://127.0.0.1:8005")

@api_router.post("/attack/execute_full_attack")
async def execute_full_attack(req: AttackRequest):
    """
    接收来自前端的攻击请求，并转发给中控智能体
    """
    logger.info(f"Received attack request for target: {req.target_host}")
    
    try:
        # 中控智能体的URL
        central_agent_url = "http://localhost:8006/process_command"
        
        # 记录请求开始
        logger.info(f"Forwarding attack request to central agent at {central_agent_url}")
        
        # 构造发送给中控智能体的请求
        central_agent_payload = {
            "command": "attack",
            "target_host": req.target_host
        }
        
        # 添加攻击类型（如果有）
        if hasattr(req, 'attack_type'):
            central_agent_payload["attack_type"] = req.attack_type
        
        logger.info(f"Payload to central agent: {central_agent_payload}")
        
        # 使用httpx发送请求到中控智能体
        async with httpx.AsyncClient() as client:
            try:
                # 尝试连接中控智能体
                try:
                    # 先检查中控智能体是否可用
                    logger.info("正在检查中控智能体连接状态...")
                    check_response = await client.get(
                        "http://localhost:8006/docs",
                        timeout=2.0
                    )
                    logger.info(f"中控智能体连接检查成功，状态码: {check_response.status_code}")
                except httpx.TimeoutException as e:
                    logger.error(f"中控智能体连接超时: {str(e)}")
                    raise httpx.RequestError(f"Central agent timeout: {str(e)}", request=None)
                except httpx.ConnectError as e:
                    logger.error(f"中控智能体连接被拒绝: {str(e)}")
                    raise httpx.RequestError(f"Central agent connection refused: {str(e)}", request=None)
                except Exception as e:
                    logger.error(f"中控智能体连接检查失败: {type(e).__name__}: {str(e)}")
                    raise httpx.RequestError(f"Central agent unavailable: {str(e)}", request=None)
                
                # 发送请求到中控智能体
                logger.info(f"正在向中控智能体发送攻击请求: {central_agent_url}")
                logger.info(f"请求载荷: {central_agent_payload}")
                response = await client.post(
                    central_agent_url,
                    json=central_agent_payload,
                    timeout=400.0  # 增加超时时间，因为中控智能体需要调用LLM分析+攻击智能体执行(300s)
                )
                logger.info(f"中控智能体响应状态码: {response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"中控智能体请求错误: {type(e).__name__}: {str(e)}")
                # 如果中控智能体不可用，直接调用攻击智能体
                logger.warning("中控智能体不可用，尝试直接调用攻击智能体")

                # 尝试连接攻击智能体
                try:
                    # 先检查攻击智能体是否可用
                    logger.info("正在检查攻击智能体连接状态...")
                    check_response = await client.get(
                        "http://localhost:8004/docs",
                        timeout=2.0
                    )
                    logger.info(f"攻击智能体连接检查成功，状态码: {check_response.status_code}")
                except httpx.TimeoutException as e:
                    logger.error(f"攻击智能体连接超时: {str(e)}")
                    return {
                        "status": "error",
                        "message": "Both central agent and attack agent are unavailable (timeout).",
                        "error_details": f"Central agent error: {str(e)}, Attack agent timeout"
                    }
                except httpx.ConnectError as e:
                    logger.error(f"攻击智能体连接被拒绝: {str(e)}")
                    return {
                        "status": "error",
                        "message": "Both central agent and attack agent are unavailable (connection refused).",
                        "error_details": f"Central agent error: {str(e)}, Attack agent connection refused"
                    }
                except Exception as e:
                    logger.error(f"攻击智能体连接检查失败: {type(e).__name__}: {str(e)}")
                    # 如果攻击智能体也不可用，返回模拟数据
                    return {
                        "status": "simulated",
                        "message": "Both central agent and attack agent are unavailable. Using simulated data.",
                        "final_output": "模拟攻击过程：\n1. 扫描目标主机\n2. 发现开放端口\n3. 生成钓鱼邮件\n4. 发送钓鱼邮件\n5. 攻击成功，获取到目标凭据",
                        "error_details": f"Central agent error: {str(e)}, Attack agent error: {str(e)}"
                    }
                
                # 发送请求到攻击智能体
                attack_agent_url = "http://localhost:8004/execute_full_attack"
                attack_payload = {"target_host": req.target_host}
                logger.info(f"正在向攻击智能体发送请求: {attack_agent_url}")
                logger.info(f"攻击智能体请求载荷: {attack_payload}")
                response = await client.post(
                    attack_agent_url,
                    json=attack_payload,
                    timeout=60.0
                )
                logger.info(f"攻击智能体响应状态码: {response.status_code}")
            
            # 检查响应状态
            response.raise_for_status()
            
            # 获取响应数据
            result = response.json()
            
            # 记录成功响应
            logger.info(f"Central agent responded successfully: {result}")
            
            # 返回中控智能体的响应
            return result
            
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error occurred when contacting attack agent: {e.response.status_code} {e.response.text}"
        logger.error(f"HTTP状态错误: {error_msg}")
        logger.error(f"响应头: {dict(e.response.headers)}")
        raise HTTPException(status_code=e.response.status_code, detail=error_msg)
    except httpx.TimeoutException as e:
        error_msg = f"Timeout error occurred when contacting attack agent: {str(e)}"
        logger.error(f"超时错误: {error_msg}")
        raise HTTPException(status_code=504, detail=error_msg)
    except httpx.ConnectError as e:
        error_msg = f"Connection error occurred when contacting attack agent: {str(e)}"
        logger.error(f"连接错误: {error_msg}")
        raise HTTPException(status_code=503, detail=error_msg)
    except httpx.RequestError as e:
        error_msg = f"Request error occurred when contacting attack agent: {type(e).__name__}: {str(e)}"
        logger.error(f"请求错误: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Unexpected error when executing attack: {type(e).__name__}: {str(e)}"
        logger.error(f"未预期错误: {error_msg}")
        logger.error(f"错误堆栈: ", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)

@api_router.post("/attack/execute_random_social_attack")
async def execute_random_social_attack(req: dict):
    """
    接收来自前端的社会工程学攻击请求，并转发给攻击智能体
    """
    logger.info(f"Received social engineering attack request: {req}")
    
    try:
        # 攻击智能体的URL
        attack_agent_url = "http://localhost:8004/execute_random_social_attack"
        
        # 记录请求开始
        logger.info(f"Forwarding social engineering attack request to attack agent at {attack_agent_url}")
        
        # 使用httpx发送请求到攻击智能体
        async with httpx.AsyncClient() as client:
            response = await client.post(
                attack_agent_url,
                json=req,
                timeout=30.0
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 获取响应数据
            result = response.json()
            
            # 记录成功响应
            logger.info(f"Attack agent responded successfully: {result}")
            
            # 返回攻击智能体的响应
            return result
            
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error occurred when contacting attack agent: {e.response.status_code} {e.response.text}"
        logger.error(error_msg)
        raise HTTPException(status_code=e.response.status_code, detail=error_msg)
    except httpx.RequestError as e:
        error_msg = f"Request error occurred when contacting attack agent: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Unexpected error when executing social engineering attack: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# 场景智能体相关API
@api_router.get("/scenario/parse_apt_scenario")
async def parse_apt_scenario():
    """
    解析APT场景，返回拓扑结构信息
    """
    logger.info("收到APT场景解析请求")

    try:
        # 场景智能体的URL
        scenario_agent_url = "http://localhost:8007/parse_apt_scenario"

        async with httpx.AsyncClient() as client:
            response = await client.get(scenario_agent_url, timeout=30.0)
            response.raise_for_status()

            result = response.json()
            logger.info("APT场景解析成功")

            return result

    except httpx.HTTPStatusError as e:
        error_msg = f"场景智能体HTTP错误: {e.response.status_code} {e.response.text}"
        logger.error(error_msg)
        raise HTTPException(status_code=e.response.status_code, detail=error_msg)
    except httpx.RequestError as e:
        error_msg = f"场景智能体连接错误: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=503, detail=error_msg)
    except Exception as e:
        error_msg = f"APT场景解析失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

class ScenarioAnalysisRequest(BaseModel):
    prompt: str = Field(description="用户输入的场景描述")

@api_router.post("/scenario/analyze_prompt")
async def analyze_scenario_prompt(req: ScenarioAnalysisRequest):
    """
    分析用户输入的场景提示词
    """
    logger.info(f"收到场景提示词分析请求: {req.prompt[:100]}...")

    try:
        # 场景智能体的URL
        scenario_agent_url = "http://localhost:8007/analyze_prompt"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                scenario_agent_url,
                json={"prompt": req.prompt},
                timeout=30.0
            )
            response.raise_for_status()

            result = response.json()
            logger.info("场景提示词分析成功")

            return result

    except httpx.HTTPStatusError as e:
        error_msg = f"场景智能体HTTP错误: {e.response.status_code} {e.response.text}"
        logger.error(error_msg)
        raise HTTPException(status_code=e.response.status_code, detail=error_msg)
    except httpx.RequestError as e:
        error_msg = f"场景智能体连接错误: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=503, detail=error_msg)
    except Exception as e:
        error_msg = f"场景提示词分析失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@api_router.post("/scenario/process_request")
async def process_scenario_request(req: ScenarioAnalysisRequest):
    """
    综合处理场景请求：分析提示词 -> 生成场景 -> 返回拓扑数据
    """
    logger.info(f"收到综合场景处理请求: {req.prompt[:100]}...")

    try:
        # 场景智能体的URL
        scenario_agent_url = "http://localhost:8007/process_scenario_request"

        logger.info(f"开始调用场景智能体: {scenario_agent_url}")
        logger.info(f"请求内容: {req.prompt}")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                scenario_agent_url,
                json={"prompt": req.prompt},
                timeout=300.0  # 增加超时时间到5分钟
            )

            logger.info(f"场景智能体响应状态码: {response.status_code}")
            response.raise_for_status()

            result = response.json()
            logger.info("综合场景处理成功")
            logger.info(f"响应数据长度: {len(str(result))} 字符")

            return result

    except httpx.HTTPStatusError as e:
        error_msg = f"场景智能体HTTP错误: {e.response.status_code} {e.response.text}"
        logger.error(error_msg)
        raise HTTPException(status_code=e.response.status_code, detail=error_msg)
    except httpx.RequestError as e:
        error_msg = f"场景智能体连接错误: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=503, detail=error_msg)
    except httpx.TimeoutException as e:
        error_msg = f"场景智能体请求超时: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=504, detail=error_msg)
    except Exception as e:
        error_msg = f"综合场景处理失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# Register router
app.include_router(api_router)

# 启动命令示例：uvicorn backend.main:app --reload --port 8080 