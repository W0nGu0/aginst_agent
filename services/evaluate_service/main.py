#!/usr/bin/env python3
"""
评估服务 - MCP服务
提供演练评估、技能画像、报告生成等功能
"""

import json
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP

# 创建MCP服务实例
mcp = FastMCP(name="Evaluate Service")

# 评估数据存储
evaluation_sessions = {}
skill_profiles = {}
evaluation_metrics = {}

@mcp.tool()
async def create_evaluation_session(exercise_id: str, participants: List[str], evaluation_type: str = "comprehensive") -> str:
    """
    创建评估会话
    
    Args:
        exercise_id: 演练ID
        participants: 参与人员列表
        evaluation_type: 评估类型 (comprehensive/quick/custom)
    
    Returns:
        评估会话信息
    """
    session_id = f"eval_{uuid.uuid4().hex[:8]}"
    
    session_data = {
        "session_id": session_id,
        "exercise_id": exercise_id,
        "participants": participants,
        "evaluation_type": evaluation_type,
        "start_time": datetime.now().isoformat(),
        "status": "active",
        "metrics": {
            "response_time": [],
            "detection_rate": [],
            "mitigation_effectiveness": [],
            "collaboration_score": [],
            "decision_quality": []
        },
        "events": [],
        "skill_assessments": {}
    }
    
    evaluation_sessions[session_id] = session_data
    
    result = {
        "session_id": session_id,
        "status": "created",
        "participants_count": len(participants),
        "evaluation_framework": "NIST Cybersecurity Framework",
        "assessment_areas": [
            "威胁检测能力",
            "事件响应速度", 
            "决策质量评估",
            "团队协作效果",
            "技术技能水平"
        ]
    }
    
    return json.dumps(result, ensure_ascii=False)

@mcp.tool()
async def record_evaluation_event(session_id: str, event_type: str, participant: str, event_data: Dict[str, Any]) -> str:
    """
    记录评估事件
    
    Args:
        session_id: 评估会话ID
        event_type: 事件类型 (detection/response/decision/collaboration)
        participant: 参与者
        event_data: 事件数据
    
    Returns:
        事件记录结果
    """
    if session_id not in evaluation_sessions:
        return json.dumps({"error": "无效的评估会话ID"})
    
    session = evaluation_sessions[session_id]
    
    event = {
        "event_id": f"evt_{uuid.uuid4().hex[:6]}",
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "participant": participant,
        "data": event_data,
        "score": calculate_event_score(event_type, event_data)
    }
    
    session["events"].append(event)
    
    # 更新实时指标
    update_session_metrics(session, event)
    
    result = {
        "event_recorded": True,
        "event_id": event["event_id"],
        "participant_score": event["score"],
        "session_events_count": len(session["events"])
    }
    
    return json.dumps(result, ensure_ascii=False)

def calculate_event_score(event_type: str, event_data: Dict[str, Any]) -> float:
    """计算事件得分"""
    base_scores = {
        "detection": 8.0,
        "response": 7.5,
        "decision": 8.5,
        "collaboration": 7.0
    }
    
    base_score = base_scores.get(event_type, 6.0)
    
    # 根据事件数据调整分数
    if "response_time" in event_data:
        response_time = event_data["response_time"]
        if response_time < 60:  # 1分钟内响应
            base_score += 1.0
        elif response_time < 300:  # 5分钟内响应
            base_score += 0.5
        elif response_time > 600:  # 超过10分钟
            base_score -= 1.0
    
    if "accuracy" in event_data:
        accuracy = event_data["accuracy"]
        base_score += (accuracy - 0.7) * 5  # 基准70%准确率
    
    return min(max(base_score, 0.0), 10.0)

def update_session_metrics(session: Dict, event: Dict):
    """更新会话指标"""
    event_type = event["event_type"]
    score = event["score"]
    
    if event_type == "detection":
        session["metrics"]["detection_rate"].append(score)
    elif event_type == "response":
        session["metrics"]["response_time"].append(score)
        session["metrics"]["mitigation_effectiveness"].append(score)
    elif event_type == "decision":
        session["metrics"]["decision_quality"].append(score)
    elif event_type == "collaboration":
        session["metrics"]["collaboration_score"].append(score)

@mcp.tool()
async def generate_skill_profile(participant: str, session_id: str) -> str:
    """
    生成个人技能画像
    
    Args:
        participant: 参与者
        session_id: 评估会话ID
    
    Returns:
        技能画像分析结果
    """
    if session_id not in evaluation_sessions:
        return json.dumps({"error": "无效的评估会话ID"})
    
    session = evaluation_sessions[session_id]
    participant_events = [e for e in session["events"] if e["participant"] == participant]
    
    if not participant_events:
        return json.dumps({"error": "该参与者无评估数据"})
    
    # 计算各项技能得分
    skill_scores = {
        "威胁检测": calculate_skill_score(participant_events, "detection"),
        "事件响应": calculate_skill_score(participant_events, "response"),
        "决策分析": calculate_skill_score(participant_events, "decision"),
        "团队协作": calculate_skill_score(participant_events, "collaboration"),
        "技术操作": calculate_technical_score(participant_events)
    }
    
    # 生成技能画像
    skill_profile = {
        "participant": participant,
        "evaluation_date": datetime.now().isoformat(),
        "overall_score": sum(skill_scores.values()) / len(skill_scores),
        "skill_breakdown": skill_scores,
        "strengths": identify_strengths(skill_scores),
        "improvement_areas": identify_weaknesses(skill_scores),
        "recommendations": generate_recommendations(skill_scores),
        "competency_level": determine_competency_level(skill_scores),
        "career_path_suggestions": suggest_career_paths(skill_scores)
    }
    
    # 存储技能画像
    skill_profiles[f"{participant}_{session_id}"] = skill_profile
    
    return json.dumps(skill_profile, ensure_ascii=False, indent=2)

def calculate_skill_score(events: List[Dict], skill_type: str) -> float:
    """计算特定技能得分"""
    relevant_events = [e for e in events if e["event_type"] == skill_type]
    if not relevant_events:
        return 6.0  # 默认分数
    
    scores = [e["score"] for e in relevant_events]
    return sum(scores) / len(scores)

def calculate_technical_score(events: List[Dict]) -> float:
    """计算技术操作得分"""
    technical_events = [e for e in events if "technical" in e.get("data", {})]
    if not technical_events:
        return 6.5
    
    scores = [e["score"] for e in technical_events]
    return sum(scores) / len(scores)

def identify_strengths(skill_scores: Dict[str, float]) -> List[str]:
    """识别优势技能"""
    strengths = []
    for skill, score in skill_scores.items():
        if score >= 8.0:
            strengths.append(skill)
    return strengths

def identify_weaknesses(skill_scores: Dict[str, float]) -> List[str]:
    """识别需要改进的技能"""
    weaknesses = []
    for skill, score in skill_scores.items():
        if score < 6.0:
            weaknesses.append(skill)
    return weaknesses

def generate_recommendations(skill_scores: Dict[str, float]) -> List[str]:
    """生成改进建议"""
    recommendations = []
    
    if skill_scores.get("威胁检测", 0) < 7.0:
        recommendations.append("建议加强威胁情报分析和异常行为识别训练")
    
    if skill_scores.get("事件响应", 0) < 7.0:
        recommendations.append("建议参加应急响应流程培训和实战演练")
    
    if skill_scores.get("决策分析", 0) < 7.0:
        recommendations.append("建议提升风险评估和决策分析能力")
    
    if skill_scores.get("团队协作", 0) < 7.0:
        recommendations.append("建议加强跨部门沟通协作技能")
    
    if skill_scores.get("技术操作", 0) < 7.0:
        recommendations.append("建议深入学习安全工具和技术操作")
    
    return recommendations

def determine_competency_level(skill_scores: Dict[str, float]) -> str:
    """确定能力等级"""
    avg_score = sum(skill_scores.values()) / len(skill_scores)
    
    if avg_score >= 9.0:
        return "专家级"
    elif avg_score >= 8.0:
        return "高级"
    elif avg_score >= 7.0:
        return "中级"
    elif avg_score >= 6.0:
        return "初级"
    else:
        return "入门级"

def suggest_career_paths(skill_scores: Dict[str, float]) -> List[str]:
    """建议职业发展路径"""
    paths = []
    
    if skill_scores.get("威胁检测", 0) >= 8.0:
        paths.append("威胁情报分析师")
    
    if skill_scores.get("事件响应", 0) >= 8.0:
        paths.append("安全事件响应专家")
    
    if skill_scores.get("决策分析", 0) >= 8.0:
        paths.append("安全架构师")
    
    if skill_scores.get("技术操作", 0) >= 8.0:
        paths.append("渗透测试工程师")
    
    if not paths:
        paths.append("网络安全工程师")
    
    return paths

@mcp.tool()
async def generate_evaluation_report(session_id: str, report_type: str = "comprehensive") -> str:
    """
    生成评估报告
    
    Args:
        session_id: 评估会话ID
        report_type: 报告类型 (comprehensive/summary/executive)
    
    Returns:
        评估报告
    """
    if session_id not in evaluation_sessions:
        return json.dumps({"error": "无效的评估会话ID"})
    
    session = evaluation_sessions[session_id]
    
    # 计算整体指标
    overall_metrics = calculate_overall_metrics(session)
    
    # 生成团队分析
    team_analysis = generate_team_analysis(session)
    
    # 生成改进建议
    improvement_recommendations = generate_improvement_recommendations(session)
    
    report = {
        "report_id": f"rpt_{uuid.uuid4().hex[:8]}",
        "session_id": session_id,
        "exercise_id": session["exercise_id"],
        "generation_time": datetime.now().isoformat(),
        "report_type": report_type,
        "executive_summary": {
            "overall_score": overall_metrics["overall_score"],
            "participants_count": len(session["participants"]),
            "events_analyzed": len(session["events"]),
            "key_findings": overall_metrics["key_findings"]
        },
        "detailed_metrics": overall_metrics,
        "team_performance": team_analysis,
        "individual_assessments": generate_individual_assessments(session),
        "improvement_recommendations": improvement_recommendations,
        "compliance_assessment": generate_compliance_assessment(session),
        "next_steps": generate_next_steps(overall_metrics)
    }
    
    return json.dumps(report, ensure_ascii=False, indent=2)

def calculate_overall_metrics(session: Dict) -> Dict:
    """计算整体指标"""
    metrics = session["metrics"]
    
    overall_score = 0
    metric_scores = {}
    
    for metric_name, values in metrics.items():
        if values:
            avg_score = sum(values) / len(values)
            metric_scores[metric_name] = avg_score
            overall_score += avg_score
    
    if metric_scores:
        overall_score = overall_score / len(metric_scores)
    
    key_findings = []
    if overall_score >= 8.0:
        key_findings.append("团队整体表现优秀，具备较强的安全防护能力")
    elif overall_score >= 7.0:
        key_findings.append("团队表现良好，在某些方面仍有提升空间")
    else:
        key_findings.append("团队需要加强安全技能培训和实战演练")
    
    return {
        "overall_score": overall_score,
        "metric_scores": metric_scores,
        "key_findings": key_findings
    }

def generate_team_analysis(session: Dict) -> Dict:
    """生成团队分析"""
    participants = session["participants"]
    events = session["events"]
    
    team_stats = {
        "collaboration_effectiveness": 7.5,
        "communication_quality": 8.0,
        "role_distribution": "均衡",
        "decision_consensus": 85,
        "knowledge_sharing": 7.8
    }
    
    return team_stats

def generate_individual_assessments(session: Dict) -> Dict:
    """生成个人评估摘要"""
    assessments = {}
    
    for participant in session["participants"]:
        participant_events = [e for e in session["events"] if e["participant"] == participant]
        if participant_events:
            avg_score = sum(e["score"] for e in participant_events) / len(participant_events)
            assessments[participant] = {
                "average_score": avg_score,
                "events_count": len(participant_events),
                "performance_level": determine_performance_level(avg_score)
            }
    
    return assessments

def determine_performance_level(score: float) -> str:
    """确定表现等级"""
    if score >= 9.0:
        return "卓越"
    elif score >= 8.0:
        return "优秀"
    elif score >= 7.0:
        return "良好"
    elif score >= 6.0:
        return "合格"
    else:
        return "需要改进"

def generate_improvement_recommendations(session: Dict) -> List[str]:
    """生成改进建议"""
    recommendations = [
        "建议定期开展安全意识培训，提升全员安全素养",
        "加强威胁情报收集和分析能力建设",
        "完善应急响应流程，缩短事件处置时间",
        "建立跨部门协作机制，提升整体防护效果",
        "引入自动化安全工具，提高检测和响应效率"
    ]
    
    return recommendations

def generate_compliance_assessment(session: Dict) -> Dict:
    """生成合规评估"""
    return {
        "framework": "NIST Cybersecurity Framework",
        "compliance_score": 82,
        "areas_assessed": [
            "识别(Identify)",
            "保护(Protect)", 
            "检测(Detect)",
            "响应(Respond)",
            "恢复(Recover)"
        ],
        "compliance_gaps": [
            "威胁建模流程需要完善",
            "事件响应计划需要更新"
        ]
    }

def generate_next_steps(metrics: Dict) -> List[str]:
    """生成后续步骤建议"""
    return [
        "制定个性化培训计划",
        "安排进阶安全技能培训",
        "组织定期安全演练",
        "建立技能评估跟踪机制",
        "完善安全管理制度"
    ]

if __name__ == "__main__":
    print("🔍 评估服务 (Evaluate Service) 正在启动...")
    mcp.run(transport="http", port=8005)
