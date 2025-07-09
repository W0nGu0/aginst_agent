import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from dotenv import load_dotenv

# --- 环境变量 ---
dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

# --- FastAPI应用 ---
app = FastAPI(
    title="中央智能体 (Central Agent)",
    description="负责接收高层用户指令，并将其调度给专门的执行智能体。"
)

# --- 配置 ---
# 现在指向新的、智能化的攻击代理
ATTACK_AGENT_URL = "http://127.0.0.1:8004/execute_full_attack" 

# --- Pydantic模型 ---
class CommandRequest(BaseModel):
    command: str
    target_host: str # 新增：需要明确攻击目标

# --- API端点 ---
@app.post("/process_command")
async def process_command(request: CommandRequest):
    """
    接收并处理来自用户的命令。
    """
    if request.command.lower() == "attack":
        # 1. 构造对攻击智能体的请求
        attack_agent_payload = {"target_host": request.target_host}

        # 2. 调用攻击智能体，并等待其完成整个攻击流程
        try:
            async with httpx.AsyncClient() as client:
                print(f"向攻击智能体 ({ATTACK_AGENT_URL}) 下达攻击指令，目标: {request.target_host}")
                response = await client.post(
                    ATTACK_AGENT_URL, 
                    json=attack_agent_payload, 
                    timeout=300 # Agent执行可能需要更长时间，增加超时
                )
                response.raise_for_status()
                
                # 3. 将攻击智能体返回的最终结果，原样返回给调用者
                return response.json()
            
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503, 
                detail=f"调用攻击智能体失败: {e}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"攻击流程中发生未知错误: {e}"
            )
    
    return {"output": "指令未识别。目前仅支持 'attack' 指令。"}


# --- 主执行 ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006) 