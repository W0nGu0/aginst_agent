from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel, Field
import subprocess
import os
import json
import logging
from typing import List, Dict, Optional, Any

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

# -----------------------------
# Expose the same functionality under the /api prefix so that the
# frontend proxy (see vite.config.js) can reach it at /api/topology
# -----------------------------
api_router = APIRouter(prefix="/api")

@api_router.post("/topology")
async def manage_topology_api(req: TopologyAction):
    """Proxy endpoint matching the frontend expectation (POST /api/topology)."""
    return await manage_topology(req)

# Register router
app.include_router(api_router)

# 启动命令示例：uvicorn backend.main:app --reload --port 8080 