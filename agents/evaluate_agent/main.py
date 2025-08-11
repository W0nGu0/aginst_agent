#!/usr/bin/env python3
"""
评估智能体 - AI Agent
基于LangChain和DeepSeek API实现智能化演练评估
"""

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

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/evaluate_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("evaluate_agent")

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(title="评估智能体", description="AI驱动的演练评估和技能分析")

# 初始化AI模型
llm = None
agent_executor = None

try:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        llm = ChatDeepSeek(
            model="deepseek-chat",
            api_key=api_key,
            max_tokens=4000,
            temperature=0.3  # 评估需要更准确的结果
        )
        logger.info("✅ DeepSeek API 初始化成功")
    else:
        logger.warning("⚠️ 未找到DEEPSEEK_API_KEY，评估智能体将以模拟模式运行")
except Exception as e:
    logger.error(f"❌ DeepSeek API 初始化失败: {e}")

# 连接评估服务
evaluate_service = FastMCP.as_proxy("http://127.0.0.1:8005/mcp/")

# 请求模型
class EvaluationRequest(BaseModel):
    exercise_id: str = Field(..., description="演练ID")
    participants: List[str] = Field(..., description="参与人员列表")
    evaluation_type: str = Field(default="comprehensive", description="评估类型")
    focus_areas: Optional[List[str]] = Field(default=None, description="重点评估领域")

class SkillProfileRequest(BaseModel):
    participant: str = Field(..., description="参与者")
    session_id: str = Field(..., description="评估会话ID")
    analysis_depth: str = Field(default="detailed", description="分析深度")

class ReportRequest(BaseModel):
    session_id: str = Field(..., description="评估会话ID")
    report_type: str = Field(default="comprehensive", description="报告类型")
    target_audience: str = Field(default="management", description="目标受众")

# 后端日志发送
async def send_log_to_backend(level: str, source: str, message: str):
    """向后端发送日志"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://localhost:8080/api/logs",
                json={
                    "level": level,
                    "source": source,
                    "message": message,
                    "timestamp": asyncio.get_event_loop().time()
                },
                timeout=5.0
            )
    except Exception as e:
        logger.error(f"发送日志到后端失败: {e}")

# AI Agent工具定义
@tool
async def create_evaluation_session(exercise_id: str, participants: List[str], evaluation_type: str = "comprehensive") -> str:
    """创建评估会话"""
    try:
        await send_log_to_backend("info", "评估智能体", f"创建评估会话: {exercise_id}")
        
        async with evaluate_service.client as client:
            response = await client.call_tool(
                "create_evaluation_session",
                arguments={
                    'exercise_id': exercise_id,
                    'participants': participants,
                    'evaluation_type': evaluation_type
                }
            )
        
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        await send_log_to_backend("info", "评估智能体", f"评估会话创建成功")
        return result
        
    except Exception as e:
        error_msg = f"创建评估会话失败: {str(e)}"
        await send_log_to_backend("error", "评估智能体", error_msg)
        return f"错误: {error_msg}"

@tool
async def analyze_participant_performance(participant: str, session_id: str) -> str:
    """分析参与者表现"""
    try:
        await send_log_to_backend("info", "评估智能体", f"分析参与者表现: {participant}")
        
        async with evaluate_service.client as client:
            response = await client.call_tool(
                "generate_skill_profile",
                arguments={
                    'participant': participant,
                    'session_id': session_id
                }
            )
        
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        await send_log_to_backend("info", "评估智能体", f"参与者表现分析完成")
        return result
        
    except Exception as e:
        error_msg = f"分析参与者表现失败: {str(e)}"
        await send_log_to_backend("error", "评估智能体", error_msg)
        return f"错误: {error_msg}"

@tool
async def generate_comprehensive_report(session_id: str, report_type: str = "comprehensive") -> str:
    """生成综合评估报告"""
    try:
        await send_log_to_backend("info", "评估智能体", f"生成评估报告: {session_id}")
        
        async with evaluate_service.client as client:
            response = await client.call_tool(
                "generate_evaluation_report",
                arguments={
                    'session_id': session_id,
                    'report_type': report_type
                }
            )
        
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        await send_log_to_backend("info", "评估智能体", f"评估报告生成完成")
        return result
        
    except Exception as e:
        error_msg = f"生成评估报告失败: {str(e)}"
        await send_log_to_backend("error", "评估智能体", error_msg)
        return f"错误: {error_msg}"

@tool
async def record_evaluation_event(session_id: str, event_type: str, participant: str, event_data: str) -> str:
    """记录评估事件"""
    try:
        # 解析事件数据
        try:
            parsed_data = json.loads(event_data)
        except:
            parsed_data = {"description": event_data}
        
        async with evaluate_service.client as client:
            response = await client.call_tool(
                "record_evaluation_event",
                arguments={
                    'session_id': session_id,
                    'event_type': event_type,
                    'participant': participant,
                    'event_data': parsed_data
                }
            )
        
        result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
        return result
        
    except Exception as e:
        error_msg = f"记录评估事件失败: {str(e)}"
        await send_log_to_backend("error", "评估智能体", error_msg)
        return f"错误: {error_msg}"

# 初始化AI Agent
if llm:
    tools = [
        create_evaluation_session,
        analyze_participant_performance,
        generate_comprehensive_report,
        record_evaluation_event
    ]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个专业的网络安全演练评估专家，具备以下能力：

1. 演练评估分析：
   - 分析演练过程中的关键事件和决策点
   - 评估参与者的技能水平和表现
   - 识别团队协作效果和沟通质量

2. 技能画像生成：
   - 基于行为数据生成个人技能画像
   - 识别优势技能和改进领域
   - 提供个性化发展建议

3. 报告生成：
   - 生成详细的评估报告
   - 提供数据驱动的洞察分析
   - 制定改进计划和培训建议

4. 评估标准：
   - 基于NIST网络安全框架
   - 结合行业最佳实践
   - 考虑组织特定需求

请根据用户请求，使用可用工具进行专业的评估分析。"""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# API端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "评估智能体",
        "ai_enabled": llm is not None,
        "timestamp": asyncio.get_event_loop().time()
    }

@app.post("/create_evaluation")
async def create_evaluation(request: EvaluationRequest):
    """创建演练评估"""
    try:
        await send_log_to_backend("info", "评估智能体", 
                                f"收到评估创建请求: {request.exercise_id}")
        
        # 构建输入
        input_text = f"""
        演练ID: {request.exercise_id}
        参与人员: {', '.join(request.participants)}
        评估类型: {request.evaluation_type}
        重点领域: {', '.join(request.focus_areas) if request.focus_areas else '全面评估'}
        
        请执行以下评估任务：
        1. 创建评估会话，设置评估框架
        2. 初始化评估指标和基准
        3. 准备实时数据收集机制
        4. 设置参与者技能评估模板
        
        确保评估过程科学、客观、全面。
        """
        
        # 执行Agent
        if agent_executor is not None:
            result = await agent_executor.ainvoke({"input": input_text})
        else:
            # 如果智能体未初始化，返回模拟结果
            result = {
                "output": "评估智能体当前处于模拟模式，请配置DEEPSEEK_API_KEY以启用完整功能。"
            }
        
        return {"status": "success", "result": result.get("output", "评估创建完成")}
        
    except Exception as e:
        logger.error(f"创建评估失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_skill_profile")
async def generate_skill_profile(request: SkillProfileRequest):
    """生成技能画像"""
    try:
        await send_log_to_backend("info", "评估智能体", 
                                f"生成技能画像: {request.participant}")
        
        # 构建输入
        input_text = f"""
        参与者: {request.participant}
        评估会话: {request.session_id}
        分析深度: {request.analysis_depth}
        
        请为该参与者生成详细的技能画像：
        1. 分析其在演练中的表现数据
        2. 评估各项安全技能水平
        3. 识别优势技能和改进领域
        4. 生成个性化发展建议
        5. 提供职业发展路径建议
        
        确保分析客观、准确、有建设性。
        """
        
        # 执行Agent
        if agent_executor is not None:
            result = await agent_executor.ainvoke({"input": input_text})
        else:
            result = {
                "output": "评估智能体当前处于模拟模式，请配置DEEPSEEK_API_KEY以启用完整功能。"
            }
        
        return {"status": "success", "result": result.get("output", "技能画像生成完成")}
        
    except Exception as e:
        logger.error(f"生成技能画像失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_evaluation_report")
async def generate_evaluation_report(request: ReportRequest):
    """生成评估报告"""
    try:
        await send_log_to_backend("info", "评估智能体", 
                                f"生成评估报告: {request.session_id}")
        
        # 构建输入
        input_text = f"""
        评估会话: {request.session_id}
        报告类型: {request.report_type}
        目标受众: {request.target_audience}
        
        请生成专业的演练评估报告：
        1. 分析整体演练效果和团队表现
        2. 提供详细的数据分析和洞察
        3. 识别关键成功因素和改进机会
        4. 制定具体的改进计划和建议
        5. 生成符合目标受众需求的报告格式
        
        确保报告专业、全面、具有指导价值。
        """
        
        # 执行Agent
        if agent_executor is not None:
            result = await agent_executor.ainvoke({"input": input_text})
        else:
            result = {
                "output": "评估智能体当前处于模拟模式，请配置DEEPSEEK_API_KEY以启用完整功能。"
            }
        
        return {"status": "success", "result": result.get("output", "评估报告生成完成")}
        
    except Exception as e:
        logger.error(f"生成评估报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8014)
