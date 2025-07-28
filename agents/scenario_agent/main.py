import os
import httpx
import json
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any
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
logger = logging.getLogger("scenario-agent")

# --- 环境变量 ---
dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

# --- 初始化LLM ---
llm = ChatDeepSeek(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))

# --- 配置 ---
SCENARIO_SERVICE_URL = os.getenv("SCENARIO_SERVICE_URL", "http://127.0.0.1:8002/mcp/")

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
            "source": "场景智能体",
            "message": "WebSocket连接已建立"
        }))
        
        logger.info(f"已连接到后端WebSocket: {BACKEND_WS_URL}")
        return True
    except Exception as e:
        logger.error(f"连接后端WebSocket失败: {e}")
        return False

async def send_log_to_backend(level: str, source: str, message: str):
    """发送日志到后端WebSocket"""
    global backend_ws
    
    log_data = {
        "timestamp": asyncio.get_event_loop().time(),
        "level": level,
        "source": source,
        "message": message
    }
    
    try:
        if backend_ws is None:
            await connect_to_backend()
        
        try:
            if backend_ws:
                await backend_ws.send(json.dumps(log_data, ensure_ascii=False))
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

# --- 业务场景和攻击方式关键词定义 ---
BUSINESS_KEYWORDS = {
    "healthcare": [
        "医疗", "医院", "病人", "病历", "诊断", "治疗", "药物", "手术",
        "护士", "医生", "患者", "医疗设备", "医疗系统", "健康", "诊所",
        "医疗机构", "医疗数据", "病历系统", "医疗网络"
    ],
    "finance": [
        "银行", "金融", "支付", "交易", "资金", "贷款", "信贷", "投资",
        "证券", "保险", "财务", "账户", "转账", "金融机构", "金融系统",
        "银行卡", "信用卡", "金融数据", "金融网络", "资产"
    ],
    "education": [
        "学校", "教育", "学生", "课程", "考试", "教师", "大学", "学院",
        "教学", "学习", "成绩", "学籍", "教育系统", "校园", "教育机构",
        "学术", "研究", "图书馆", "教育网络", "学生信息"
    ],
    "manufacturing": [
        "制造", "工厂", "生产", "设备", "供应链", "制造业", "生产线",
        "工业", "机械", "自动化", "质量控制", "生产管理", "制造系统",
        "工业控制", "生产数据", "制造网络", "工业设备", "生产流程"
    ]
}

ATTACK_KEYWORDS = {
    "apt": [
        "APT", "高级持续威胁", "长期潜伏", "定向攻击", "持续攻击",
        "高级威胁", "复杂攻击", "多阶段攻击", "隐蔽攻击", "国家级攻击"
    ],
    "phishing": [
        "钓鱼", "邮件攻击", "社会工程", "欺骗邮件", "虚假邮件",
        "钓鱼网站", "邮件钓鱼", "社工攻击", "诱骗", "伪造邮件"
    ],
    "ransomware": [
        "勒索", "加密", "赎金", "勒索软件", "文件加密", "勒索病毒",
        "加密勒索", "赎金软件", "文件锁定", "勒索攻击"
    ],
    "insider_threat": [
        "内部威胁", "员工", "权限滥用", "内鬼", "内部人员", "恶意员工",
        "权限误用", "内部攻击", "员工威胁", "内部风险"
    ]
}

# --- 使用FastMCP客户端连接到场景服务 ---
scenario_service_client = FastMCP.as_proxy(SCENARIO_SERVICE_URL)

# --- 将所有工具放入列表 ---
tools = []

# --- 为Agent定义工具 ---
@tool
async def generate_dynamic_scenario(business_scenario: str, attack_type: str, custom_config: dict = None) -> str:
    """
    调用场景服务生成动态场景

    Args:
        business_scenario: 业务场景类型
        attack_type: 攻击方式类型
        custom_config: 自定义配置参数

    Returns:
        生成的场景信息JSON字符串
    """
    try:
        await send_log_to_backend("info", "场景智能体",
                                f"开始生成动态场景: {business_scenario} + {attack_type}")

        async with scenario_service_client.client as client:
            response = await client.call_tool(
                "generate_dynamic_scenario",
                arguments={
                    'attack_type': attack_type,
                    'business_scenario': business_scenario,
                    'custom_config': custom_config or {}
                }
            )

        # 从CallToolResult对象中提取文本
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])

        await send_log_to_backend("success", "场景智能体", "动态场景生成完成")

        return result

    except Exception as e:
        error_msg = f"生成动态场景失败: {str(e)}"
        logger.error(error_msg)
        await send_log_to_backend("error", "场景智能体", error_msg)
        return json.dumps({"error": error_msg})

@tool
async def parse_apt_ready_scenario() -> str:
    """
    解析apt-ready.yml场景文件，提取拓扑结构信息

    Returns:
        包含拓扑结构的JSON字符串
    """
    try:
        await send_log_to_backend("info", "场景智能体", "开始解析apt-ready.yml场景")

        # 调用场景服务解析apt-ready.yml
        async with scenario_service_client.client as client:
            response = await client.call_tool(
                "parse_apt_ready_scenario",
                arguments={}
            )

        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])

        await send_log_to_backend("success", "场景智能体", "apt-ready.yml场景解析完成")

        return result

    except Exception as e:
        error_msg = f"解析apt-ready.yml场景失败: {str(e)}"
        logger.error(error_msg)
        await send_log_to_backend("error", "场景智能体", error_msg)
        return json.dumps({"error": error_msg})

@tool
async def analyze_user_prompt(prompt: str) -> str:
    """
    分析用户输入的提示词，提取业务场景和攻击方式关键信息
    
    Args:
        prompt: 用户输入的场景描述
        
    Returns:
        包含解析结果的JSON字符串
    """
    try:
        await send_log_to_backend("info", "场景智能体", f"开始分析用户提示词: {prompt[:50]}...")
        
        # 使用DeepSeek进行智能分析
        analysis_prompt = f"""
        作为网络安全场景分析专家，请分析以下用户输入的攻防场景描述，提取关键信息：

        用户输入: "{prompt}"

        请从以下维度进行分析：

        1. 业务场景类型（必选其一）：
           - healthcare: 医疗机构相关
           - finance: 金融机构相关  
           - education: 教育机构相关
           - manufacturing: 制造企业相关

        2. 攻击方式类型（必选其一）：
           - apt: APT高级持续威胁
           - phishing: 钓鱼攻击
           - ransomware: 勒索软件攻击
           - insider_threat: 内部威胁

        3. 场景特征：
           - 攻击目标
           - 攻击路径
           - 关键资产

        请以JSON格式返回分析结果：
        {{
            "business_scenario": "healthcare|finance|education|manufacturing",
            "attack_type": "apt|phishing|ransomware|insider_threat", 
            "confidence": 0.0-1.0,
            "reasoning": "分析推理过程",
            "scenario_features": {{
                "target": "攻击目标",
                "attack_path": "攻击路径",
                "key_assets": ["关键资产1", "关键资产2"]
            }}
        }}
        """
        
        analysis_result = await llm.ainvoke(analysis_prompt)
        analysis_text = analysis_result.content
        
        # 尝试解析JSON结果
        try:
            # 提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_result = json.loads(json_str)
            else:
                # 如果没有找到JSON，使用关键词匹配作为备选
                parsed_result = keyword_based_analysis(prompt)
        except Exception as e:
            logger.warning(f"JSON解析失败，使用关键词匹配: {e}")
            parsed_result = keyword_based_analysis(prompt)
        
        await send_log_to_backend("success", "场景智能体", 
                                f"提示词分析完成: {parsed_result['business_scenario']} + {parsed_result['attack_type']}")
        
        return json.dumps(parsed_result, ensure_ascii=False)
        
    except Exception as e:
        error_msg = f"分析用户提示词失败: {str(e)}"
        logger.error(error_msg)
        await send_log_to_backend("error", "场景智能体", error_msg)
        return json.dumps({"error": error_msg})

def keyword_based_analysis(prompt: str) -> dict:
    """
    基于关键词的备选分析方法
    """
    prompt_lower = prompt.lower()
    
    # 分析业务场景
    business_scores = {}
    for business, keywords in BUSINESS_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in prompt_lower)
        if score > 0:
            business_scores[business] = score
    
    # 分析攻击方式
    attack_scores = {}
    for attack, keywords in ATTACK_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in prompt_lower)
        if score > 0:
            attack_scores[attack] = score
    
    # 选择得分最高的
    business_scenario = max(business_scores, key=business_scores.get) if business_scores else "healthcare"
    attack_type = max(attack_scores, key=attack_scores.get) if attack_scores else "apt"
    
    confidence = min((business_scores.get(business_scenario, 0) + attack_scores.get(attack_type, 0)) / 10, 1.0)
    
    return {
        "business_scenario": business_scenario,
        "attack_type": attack_type,
        "confidence": confidence,
        "reasoning": f"基于关键词匹配分析，业务场景匹配度: {business_scores.get(business_scenario, 0)}, 攻击方式匹配度: {attack_scores.get(attack_type, 0)}",
        "scenario_features": {
            "target": "待确定",
            "attack_path": "待确定",
            "key_assets": ["待确定"]
        }
    }

# 将工具添加到工具列表
tools.extend([
    analyze_user_prompt,
    generate_dynamic_scenario,
    parse_apt_ready_scenario
])

# --- 定义Agent ---
prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一个专业的网络安全场景生成智能体。
你的任务是：
1. 分析用户输入的攻防场景描述
2. 提取业务场景类型（healthcare/finance/education/manufacturing）
3. 提取攻击方式类型（apt/phishing/ransomware/insider_threat）
4. 调用相应的工具生成动态场景
5. 返回包含拓扑结构的场景数据

你必须严格按照工具的定义来使用它们，确保返回结构化的JSON数据。"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- FastAPI应用 ---
app = FastAPI(
    title="场景智能体 (Scenario Agent)",
    description="负责分析用户输入，生成动态攻防场景，并协调场景部署。"
)

class PromptAnalysisRequest(BaseModel):
    prompt: str = Field(description="用户输入的场景描述")

class ScenarioGenerationRequest(BaseModel):
    business_scenario: str = Field(description="业务场景类型")
    attack_type: str = Field(description="攻击方式类型")
    description: Optional[str] = Field(None, description="详细描述")
    custom_config: Optional[Dict] = Field(None, description="自定义配置")

@app.post("/analyze_prompt")
async def analyze_prompt_endpoint(request: PromptAnalysisRequest):
    """
    分析用户输入的提示词，提取业务场景和攻击方式
    """
    try:
        logger.info(f"收到提示词分析请求: {request.prompt[:100]}...")

        # 调用分析工具 - 使用正确的调用方式
        result = await analyze_user_prompt.ainvoke({"prompt": request.prompt})
        parsed_result = json.loads(result)

        if "error" in parsed_result:
            raise HTTPException(status_code=500, detail=parsed_result["error"])

        return {
            "status": "success",
            "data": parsed_result
        }

    except Exception as e:
        error_msg = f"提示词分析失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/generate_scenario")
async def generate_scenario_endpoint(request: ScenarioGenerationRequest):
    """
    根据业务场景和攻击类型生成动态场景
    """
    try:
        logger.info(f"收到场景生成请求: {request.business_scenario} + {request.attack_type}")

        # 调用场景生成工具 - 使用正确的调用方式
        result = await generate_dynamic_scenario.ainvoke({
            "business_scenario": request.business_scenario,
            "attack_type": request.attack_type,
            "custom_config": request.custom_config or {}
        })

        # 尝试解析结果
        try:
            parsed_result = json.loads(result)
            if "error" in parsed_result:
                raise HTTPException(status_code=500, detail=parsed_result["error"])
        except json.JSONDecodeError:
            # 如果不是JSON格式，直接返回
            parsed_result = {"raw_result": result}

        return {
            "status": "success",
            "data": parsed_result
        }

    except Exception as e:
        error_msg = f"场景生成失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/parse_apt_scenario")
async def parse_apt_scenario_endpoint():
    """
    解析apt-ready.yml场景，返回拓扑结构信息
    """
    try:
        logger.info("收到apt-ready.yml场景解析请求")

        # 调用解析工具 - 使用正确的调用方式
        result = await parse_apt_ready_scenario.ainvoke({})

        try:
            parsed_result = json.loads(result)
            if "error" in parsed_result:
                raise HTTPException(status_code=500, detail=parsed_result["error"])
        except json.JSONDecodeError:
            parsed_result = {"raw_result": result}

        return {
            "status": "success",
            "data": parsed_result
        }

    except Exception as e:
        error_msg = f"apt场景解析失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/process_scenario_request")
async def process_scenario_request(request: PromptAnalysisRequest):
    """
    综合处理场景请求：分析提示词 -> 生成场景 -> 返回拓扑数据
    """
    try:
        logger.info(f"收到综合场景处理请求: {request.prompt[:100]}...")

        # 使用Agent执行器处理完整流程
        input_prompt = f"""
        用户输入了以下场景描述："{request.prompt}"

        请执行以下步骤：
        1. 分析这个提示词，提取业务场景和攻击类型
        2. 如果识别出是医疗+APT场景，调用parse_apt_ready_scenario获取拓扑数据
        3. 否则调用generate_dynamic_scenario生成对应场景
        4. 返回包含拓扑结构的完整场景数据
        """

        result = await agent_executor.ainvoke({"input": input_prompt})

        return {
            "status": "success",
            "data": {
                "agent_output": result.get("output"),
                "prompt": request.prompt
            }
        }

    except Exception as e:
        error_msg = f"综合场景处理失败: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
