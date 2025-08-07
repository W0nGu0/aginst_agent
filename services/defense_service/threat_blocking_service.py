"""
威胁阻断服务 - MCP服务
提供实时威胁检测和阻断功能的模拟工具
"""

import asyncio
import json
import random
from datetime import datetime
from fastmcp import FastMCP
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# 创建MCP服务实例
mcp = FastMCP("Threat_Blocking_Service")

# 模拟的威胁数据库
THREAT_SIGNATURES = {
    "port_scan": {
        "name": "端口扫描攻击",
        "severity": "medium",
        "block_duration": 300,  # 5分钟
        "description": "检测到来源IP进行大量端口扫描"
    },
    "brute_force": {
        "name": "暴力破解攻击", 
        "severity": "high",
        "block_duration": 3600,  # 1小时
        "description": "检测到针对SSH/RDP的暴力破解尝试"
    },
    "malware_c2": {
        "name": "恶意软件C2通信",
        "severity": "critical", 
        "block_duration": 86400,  # 24小时
        "description": "检测到与已知C2服务器的通信"
    },
    "phishing_domain": {
        "name": "钓鱼域名访问",
        "severity": "high",
        "block_duration": 7200,  # 2小时
        "description": "检测到访问已知钓鱼域名"
    },
    "data_exfiltration": {
        "name": "数据外泄",
        "severity": "critical",
        "block_duration": 86400,  # 24小时
        "description": "检测到大量敏感数据向外传输"
    }
}

# 模拟的网络设备状态
NETWORK_DEVICES = {
    "firewall": {
        "name": "主防火墙",
        "status": "active",
        "rules_count": 1247,
        "blocked_ips": [],
        "last_update": datetime.now()
    },
    "ids": {
        "name": "入侵检测系统", 
        "status": "active",
        "alerts_count": 0,
        "last_scan": datetime.now()
    },
    "switch": {
        "name": "核心交换机",
        "status": "active", 
        "ports_blocked": [],
        "vlan_isolation": []
    }
}

# 模拟的防火墙状态（合并自防火墙控制服务）
FIREWALL_STATE = {
    "whitelist": [
        "192.168.100.50",    # 用户PC
        "192.168.200.10",    # 内网数据库
        "192.168.200.20",    # 内网文件服务器
        "172.16.100.10",     # DMZ Web服务器
        "172.16.100.20",     # DMZ DNS服务器
        "192.168.1.1",       # 网关
        "8.8.8.8",           # 公共DNS
        "114.114.114.114"    # 公共DNS
    ],
    "blacklist": [],
    "rules": [],
    "last_updated": datetime.now().isoformat(),
    "status": "active"
}

@mcp.tool()
async def detect_network_threats(target_network: str, scan_duration: int = 30) -> str:
    """
    检测网络中的威胁活动
    
    Args:
        target_network: 目标网络段 (如: 192.168.1.0/24)
        scan_duration: 扫描持续时间(秒)
    
    Returns:
        检测到的威胁列表
    """
    await asyncio.sleep(2)  # 模拟扫描时间
    
    # 模拟检测结果
    threats_detected = []
    
    # 随机生成一些威胁
    if random.random() > 0.3:  # 70%概率检测到威胁
        threat_types = random.sample(list(THREAT_SIGNATURES.keys()), 
                                   random.randint(1, 3))
        
        for threat_type in threat_types:
            threat = THREAT_SIGNATURES[threat_type]
            threats_detected.append({
                "type": threat_type,
                "name": threat["name"],
                "severity": threat["severity"],
                "source_ip": f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
                "target_ip": f"192.168.200.{random.randint(1,254)}",
                "timestamp": datetime.now().isoformat(),
                "description": threat["description"],
                "confidence": random.randint(85, 99)
            })
    
    result = {
        "scan_network": target_network,
        "scan_duration": scan_duration,
        "threats_found": len(threats_detected),
        "threats": threats_detected,
        "scan_completed": datetime.now().isoformat()
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
async def block_malicious_ip(ip_address: str, threat_type: str, duration: int = None) -> str:
    """
    阻断恶意IP地址
    
    Args:
        ip_address: 要阻断的IP地址
        threat_type: 威胁类型
        duration: 阻断持续时间(秒)，如果不指定则使用默认值
    
    Returns:
        阻断操作结果
    """
    await asyncio.sleep(1)  # 模拟配置时间
    
    if not duration and threat_type in THREAT_SIGNATURES:
        duration = THREAT_SIGNATURES[threat_type]["block_duration"]
    elif not duration:
        duration = 3600  # 默认1小时
    
    # 更新防火墙状态
    NETWORK_DEVICES["firewall"]["blocked_ips"].append({
        "ip": ip_address,
        "threat_type": threat_type,
        "blocked_at": datetime.now().isoformat(),
        "duration": duration,
        "rule_id": f"BLOCK_{random.randint(10000, 99999)}"
    })
    
    NETWORK_DEVICES["firewall"]["rules_count"] += 1
    
    result = {
        "action": "ip_blocked",
        "ip_address": ip_address,
        "threat_type": threat_type,
        "duration_seconds": duration,
        "firewall_rule_added": True,
        "blocked_at": datetime.now().isoformat(),
        "status": "success"
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
async def isolate_infected_host(host_ip: str, isolation_type: str = "vlan") -> str:
    """
    隔离被感染的主机
    
    Args:
        host_ip: 被感染主机的IP地址
        isolation_type: 隔离类型 (vlan/port/quarantine)
    
    Returns:
        隔离操作结果
    """
    await asyncio.sleep(2)  # 模拟隔离配置时间
    
    isolation_methods = {
        "vlan": "VLAN隔离 - 将主机移至隔离VLAN",
        "port": "端口隔离 - 关闭交换机端口",
        "quarantine": "检疫隔离 - 限制网络访问权限"
    }
    
    # 更新交换机状态
    if isolation_type == "vlan":
        NETWORK_DEVICES["switch"]["vlan_isolation"].append({
            "host_ip": host_ip,
            "original_vlan": f"VLAN_{random.randint(10, 99)}",
            "quarantine_vlan": "VLAN_999",
            "isolated_at": datetime.now().isoformat()
        })
    elif isolation_type == "port":
        NETWORK_DEVICES["switch"]["ports_blocked"].append({
            "host_ip": host_ip,
            "port": f"Gi0/{random.randint(1, 48)}",
            "blocked_at": datetime.now().isoformat()
        })
    
    result = {
        "action": "host_isolated",
        "host_ip": host_ip,
        "isolation_type": isolation_type,
        "method": isolation_methods.get(isolation_type, "未知隔离方式"),
        "isolated_at": datetime.now().isoformat(),
        "status": "success",
        "recovery_instructions": f"主机 {host_ip} 已被隔离，需要清理恶意软件后才能恢复网络访问"
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
async def block_malicious_domain(domain: str, category: str = "malware") -> str:
    """
    阻断恶意域名访问
    
    Args:
        domain: 要阻断的域名
        category: 域名类别 (malware/phishing/c2/botnet)
    
    Returns:
        域名阻断结果
    """
    await asyncio.sleep(1)  # 模拟DNS配置时间
    
    categories = {
        "malware": "恶意软件分发",
        "phishing": "钓鱼网站",
        "c2": "命令控制服务器",
        "botnet": "僵尸网络"
    }
    
    result = {
        "action": "domain_blocked",
        "domain": domain,
        "category": category,
        "category_description": categories.get(category, "未知类别"),
        "dns_sinkhole": f"127.0.0.1",  # 重定向到本地
        "blocked_at": datetime.now().isoformat(),
        "status": "success",
        "affected_users": random.randint(1, 50)
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
async def get_threat_intelligence() -> str:
    """
    获取最新威胁情报
    
    Returns:
        威胁情报摘要
    """
    await asyncio.sleep(1)  # 模拟情报获取时间
    
    # 模拟威胁情报
    intelligence = {
        "update_time": datetime.now().isoformat(),
        "new_threats": [
            {
                "name": "APT-2024-001",
                "type": "targeted_attack",
                "severity": "critical",
                "description": "针对医疗行业的定向攻击活动",
                "iocs": [
                    "evil-medical-corp.com",
                    "192.168.100.200",
                    "medical-update.exe"
                ]
            },
            {
                "name": "Phishing-Campaign-2024",
                "type": "phishing",
                "severity": "high", 
                "description": "大规模钓鱼邮件活动",
                "iocs": [
                    "secure-login-update.com",
                    "account-verification.net"
                ]
            }
        ],
        "blocked_indicators": len(NETWORK_DEVICES["firewall"]["blocked_ips"]),
        "threat_level": "elevated"
    }
    
    return json.dumps(intelligence, indent=2, ensure_ascii=False)

@mcp.tool()
async def get_firewall_status() -> str:
    """
    获取防火墙当前状态
    
    Returns:
        防火墙状态信息
    """
    await asyncio.sleep(0.5)  # 模拟查询时间
    
    result = {
        "firewall_status": "active",
        "whitelist_count": len(FIREWALL_STATE["whitelist"]),
        "blacklist_count": len(FIREWALL_STATE["blacklist"]),
        "whitelist": FIREWALL_STATE["whitelist"],
        "blacklist": FIREWALL_STATE["blacklist"],
        "total_rules": len(FIREWALL_STATE["rules"]),
        "last_updated": FIREWALL_STATE["last_updated"],
        "policy": "default_deny"
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
async def add_to_firewall_blacklist(ip_address: str, reason: str = "恶意活动") -> str:
    """
    将IP地址添加到防火墙黑名单
    
    Args:
        ip_address: 要阻断的IP地址
        reason: 阻断原因
    
    Returns:
        操作结果
    """
    await asyncio.sleep(1)  # 模拟配置时间
    
    if ip_address in FIREWALL_STATE["blacklist"]:
        return json.dumps({
            "status": "already_exists",
            "message": f"IP {ip_address} 已在黑名单中",
            "ip_address": ip_address
        }, ensure_ascii=False)
    
    # 从白名单中移除（如果存在）
    if ip_address in FIREWALL_STATE["whitelist"]:
        FIREWALL_STATE["whitelist"].remove(ip_address)
    
    # 添加到黑名单
    FIREWALL_STATE["blacklist"].append(ip_address)
    
    # 添加防火墙规则
    rule = {
        "id": f"DENY_{random.randint(10000, 99999)}",
        "action": "DENY",
        "source_ip": ip_address,
        "destination": "ANY",
        "protocol": "ANY",
        "port": "ANY",
        "reason": reason,
        "created_at": datetime.now().isoformat()
    }
    FIREWALL_STATE["rules"].append(rule)
    FIREWALL_STATE["last_updated"] = datetime.now().isoformat()
    
    result = {
        "status": "success",
        "action": "ip_blocked",
        "ip_address": ip_address,
        "reason": reason,
        "rule_id": rule["id"],
        "blocked_at": rule["created_at"],
        "current_blacklist_count": len(FIREWALL_STATE["blacklist"])
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
async def remove_from_firewall_blacklist(ip_address: str) -> str:
    """
    从防火墙黑名单中移除IP地址
    
    Args:
        ip_address: 要移除的IP地址
    
    Returns:
        操作结果
    """
    await asyncio.sleep(1)  # 模拟配置时间
    
    if ip_address not in FIREWALL_STATE["blacklist"]:
        return json.dumps({
            "status": "not_found",
            "message": f"IP {ip_address} 不在黑名单中",
            "ip_address": ip_address
        }, ensure_ascii=False)
    
    # 从黑名单中移除
    FIREWALL_STATE["blacklist"].remove(ip_address)
    
    # 移除相关防火墙规则
    FIREWALL_STATE["rules"] = [
        rule for rule in FIREWALL_STATE["rules"] 
        if rule["source_ip"] != ip_address
    ]
    
    # 添加回白名单（如果是内网IP）
    if ip_address.startswith(("192.168.", "172.16.", "10.")):
        FIREWALL_STATE["whitelist"].append(ip_address)
    
    FIREWALL_STATE["last_updated"] = datetime.now().isoformat()
    
    result = {
        "status": "success",
        "action": "ip_unblocked",
        "ip_address": ip_address,
        "unblocked_at": datetime.now().isoformat(),
        "current_blacklist_count": len(FIREWALL_STATE["blacklist"]),
        "added_to_whitelist": ip_address.startswith(("192.168.", "172.16.", "10."))
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
async def add_to_firewall_whitelist(ip_address: str, description: str = "可信IP") -> str:
    """
    将IP地址添加到防火墙白名单
    
    Args:
        ip_address: 要允许的IP地址
        description: 描述信息
    
    Returns:
        操作结果
    """
    await asyncio.sleep(0.5)  # 模拟配置时间
    
    if ip_address in FIREWALL_STATE["whitelist"]:
        return json.dumps({
            "status": "already_exists",
            "message": f"IP {ip_address} 已在白名单中",
            "ip_address": ip_address
        }, ensure_ascii=False)
    
    # 从黑名单中移除（如果存在）
    if ip_address in FIREWALL_STATE["blacklist"]:
        FIREWALL_STATE["blacklist"].remove(ip_address)
        # 移除相关阻断规则
        FIREWALL_STATE["rules"] = [
            rule for rule in FIREWALL_STATE["rules"] 
            if rule["source_ip"] != ip_address
        ]
    
    # 添加到白名单
    FIREWALL_STATE["whitelist"].append(ip_address)
    FIREWALL_STATE["last_updated"] = datetime.now().isoformat()
    
    result = {
        "status": "success",
        "action": "ip_whitelisted",
        "ip_address": ip_address,
        "description": description,
        "whitelisted_at": datetime.now().isoformat(),
        "current_whitelist_count": len(FIREWALL_STATE["whitelist"])
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
async def bulk_block_ips(ip_list: List[str], reason: str = "批量威胁阻断") -> str:
    """
    批量阻断IP地址
    
    Args:
        ip_list: IP地址列表
        reason: 阻断原因
    
    Returns:
        批量操作结果
    """
    await asyncio.sleep(2)  # 模拟批量配置时间
    
    results = []
    blocked_count = 0
    
    for ip in ip_list:
        if ip not in FIREWALL_STATE["blacklist"]:
            # 从白名单中移除
            if ip in FIREWALL_STATE["whitelist"]:
                FIREWALL_STATE["whitelist"].remove(ip)
            
            # 添加到黑名单
            FIREWALL_STATE["blacklist"].append(ip)
            
            # 添加规则
            rule = {
                "id": f"BULK_DENY_{random.randint(10000, 99999)}",
                "action": "DENY",
                "source_ip": ip,
                "destination": "ANY",
                "protocol": "ANY",
                "port": "ANY",
                "reason": reason,
                "created_at": datetime.now().isoformat()
            }
            FIREWALL_STATE["rules"].append(rule)
            
            results.append({
                "ip": ip,
                "status": "blocked",
                "rule_id": rule["id"]
            })
            blocked_count += 1
        else:
            results.append({
                "ip": ip,
                "status": "already_blocked"
            })
    
    FIREWALL_STATE["last_updated"] = datetime.now().isoformat()
    
    result = {
        "status": "success",
        "action": "bulk_block",
        "total_ips": len(ip_list),
        "blocked_count": blocked_count,
        "already_blocked": len(ip_list) - blocked_count,
        "reason": reason,
        "results": results,
        "completed_at": datetime.now().isoformat()
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)

@mcp.tool()
async def emergency_network_lockdown(reason: str, duration: int = 1800) -> str:
    """
    紧急网络封锁
    
    Args:
        reason: 封锁原因
        duration: 封锁持续时间(秒)
    
    Returns:
        封锁操作结果
    """
    await asyncio.sleep(3)  # 模拟紧急配置时间
    
    result = {
        "action": "emergency_lockdown",
        "reason": reason,
        "duration_seconds": duration,
        "measures_applied": [
            "阻断所有外网访问",
            "隔离内网关键服务器",
            "启用严格访问控制",
            "激活事件响应团队"
        ],
        "lockdown_at": datetime.now().isoformat(),
        "status": "active",
        "contact": "安全运营中心 SOC",
        "estimated_impact": "高 - 业务中断"
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    print("\n--- 威胁阻断服务 (Threat Blocking Service) is starting... ---\n")
    mcp.run(transport="http", port=8008)