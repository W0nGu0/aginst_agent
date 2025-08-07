"""
防御协调器 (Defense Coordinator)
监听WebSocket日志，自动触发相应的防御智能体响应
"""

import os
import json
import asyncio
import logging
import websockets.client
import httpx
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Any
import re

# --- 设置日志 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("defense-coordinator")

# --- 环境变量 ---
dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

# --- 配置 ---
BACKEND_WS_URL = "ws://localhost:8080/ws/logs"
DEFENSE_AGENTS = {
    "threat_blocking": "http://127.0.0.1:8011/execute_threat_blocking",
    "vulnerability_remediation": "http://127.0.0.1:8012/execute_vulnerability_remediation",
    "attack_attribution": "http://127.0.0.1:8013/execute_attack_attribution"
}

class DefenseCoordinator:
    def __init__(self):
        self.ws_connection = None
        self.running = True  # 初始化为True
        self.processed_messages = set()  # 用于去重
        
        # 日志模式匹配规则
        self.defense_patterns = {
            # 威胁阻断触发模式
            "threat_blocking": [
                r"攻击者.*扫描.*防火墙",
                r"检测到.*端口扫描",
                r"发现.*开放端口",
                r"攻击者.*发送.*钓鱼邮件",
                r"恶意.*IP.*访问",
                r"检测到.*暴力破解",
                r"发现.*恶意域名",
                r"攻击者.*建立.*C2通信",
                r"检测到.*数据外泄"
            ],
            
            # 漏洞修复触发模式
            "vulnerability_remediation": [
                r".*漏洞.*被利用",
                r"攻击者.*获得.*访问权限",
                r".*系统.*被攻陷",
                r"发现.*安全漏洞",
                r".*补丁.*需要更新",
                r"攻击者.*安装.*后门",
                r".*配置.*存在缺陷",
                r"系统.*需要加固"
            ],
            
            # 攻击溯源触发模式
            "attack_attribution": [
                r"攻击.*完成",
                r"攻击者.*完全.*攻陷",
                r"数据.*被窃取",
                r"攻击.*成功",
                r"需要.*溯源.*分析",
                r"攻击.*路径.*分析",
                r"威胁.*归因.*分析",
                r"收集.*数字证据"
            ]
        }
    
    async def connect_to_backend(self):
        """连接到后端WebSocket"""
        try:
            self.ws_connection = await websockets.client.connect(BACKEND_WS_URL)
            logger.info(f"防御协调器已连接到WebSocket: {BACKEND_WS_URL}")
            return True
        except Exception as e:
            logger.error(f"连接WebSocket失败: {e}")
            return False
    
    async def send_log(self, level: str, message: str):
        """发送日志到后端"""
        if self.ws_connection:
            try:
                log_data = {
                    "level": level,
                    "source": "防御协调器",
                    "message": message,
                    "timestamp": asyncio.get_event_loop().time()
                }
                await self.ws_connection.send(json.dumps(log_data, ensure_ascii=False))
            except Exception as e:
                logger.error(f"发送日志失败: {e}")
    
    def analyze_log_for_defense_triggers(self, log_message: str, log_source: str) -> List[str]:
        """分析日志消息，确定需要触发的防御智能体"""
        triggered_agents = []
        
        # 跳过防御智能体自己的日志，避免循环触发
        if any(agent in log_source for agent in ["威胁阻断", "漏洞修复", "攻击溯源", "防御协调器"]):
            return triggered_agents
        
        # 检查每种防御智能体的触发模式
        for agent_type, patterns in self.defense_patterns.items():
            for pattern in patterns:
                if re.search(pattern, log_message, re.IGNORECASE):
                    if agent_type not in triggered_agents:
                        triggered_agents.append(agent_type)
                    break
        
        return triggered_agents
    
    def extract_context_from_log(self, log_message: str, log_source: str) -> Dict[str, Any]:
        """从日志中提取上下文信息"""
        context = {
            "source_message": log_message,
            "log_source": log_source,
            "extracted_info": {}
        }
        
        # 提取IP地址
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ips = re.findall(ip_pattern, log_message)
        if ips:
            context["extracted_info"]["ip_addresses"] = ips
        
        # 提取主机名或设备名
        host_patterns = [
            r'主机\s*([^\s]+)',
            r'设备\s*([^\s]+)',
            r'服务器\s*([^\s]+)',
            r'节点\s*([^\s]+)'
        ]
        for pattern in host_patterns:
            matches = re.findall(pattern, log_message)
            if matches:
                context["extracted_info"]["hosts"] = matches
                break
        
        # 提取漏洞信息
        vuln_patterns = [
            r'CVE-\d{4}-\d+',
            r'漏洞\s*([^\s]+)',
            r'补丁\s*([^\s]+)'
        ]
        for pattern in vuln_patterns:
            matches = re.findall(pattern, log_message)
            if matches:
                context["extracted_info"]["vulnerabilities"] = matches
                break
        
        # 提取攻击类型
        attack_patterns = [
            r'(钓鱼|phishing)',
            r'(暴力破解|brute.?force)',
            r'(端口扫描|port.?scan)',
            r'(SQL注入|sql.?injection)',
            r'(远程代码执行|remote.?code.?execution)'
        ]
        for pattern in attack_patterns:
            matches = re.findall(pattern, log_message, re.IGNORECASE)
            if matches:
                context["extracted_info"]["attack_types"] = matches
                break
        
        return context
    
    async def trigger_defense_agent(self, agent_type: str, context: Dict[str, Any]):
        """触发特定的防御智能体"""
        if agent_type not in DEFENSE_AGENTS:
            logger.warning(f"未知的防御智能体类型: {agent_type}")
            return
        
        agent_url = DEFENSE_AGENTS[agent_type]
        
        try:
            # 根据智能体类型构建请求参数
            if agent_type == "threat_blocking":
                payload = {
                    "target_network": "192.168.0.0/16",
                    "threat_level": "high",
                    "auto_block": True,
                    "context": context
                }
            elif agent_type == "vulnerability_remediation":
                # 提取目标主机信息，使用更通用的名称
                target_hosts = context["extracted_info"].get("hosts", [])
                if not target_hosts:
                    # 如果没有提取到主机名，使用默认的系统名称
                    target_hosts = ["web-server", "database-server", "file-server"]
                
                payload = {
                    "target_systems": target_hosts[0] if target_hosts else "web-server",
                    "scan_type": "comprehensive", 
                    "auto_patch": True,
                    "hardening_profile": "standard",
                    "context": context
                }
            elif agent_type == "attack_attribution":
                payload = {
                    "incident_id": f"INC_{asyncio.get_event_loop().time():.0f}",
                    "attack_indicators": context["extracted_info"].get("ip_addresses", []),
                    "source_node": "internet",
                    "target_node": context["extracted_info"].get("hosts", ["internal_db"])[0] if context["extracted_info"].get("hosts") else "internal_db",
                    "evidence_types": ["logs", "network"],
                    "context": context
                }
            
            # 发送请求到防御智能体
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(agent_url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    await self.send_log("success", f"成功触发{agent_type}防御智能体响应")
                    logger.info(f"防御智能体 {agent_type} 响应成功: {result.get('message', 'OK')}")
                else:
                    await self.send_log("error", f"触发{agent_type}防御智能体失败: HTTP {response.status_code}")
                    logger.error(f"防御智能体 {agent_type} 响应失败: {response.status_code}")
                    
        except Exception as e:
            await self.send_log("error", f"调用{agent_type}防御智能体时出错: {e}")
            logger.error(f"调用防御智能体 {agent_type} 失败: {e}")
    
    async def process_log_message(self, message_data: Dict[str, Any]):
        """处理接收到的日志消息"""
        try:
            log_message = message_data.get("message", "")
            log_source = message_data.get("source", "")
            log_level = message_data.get("level", "info")
            
            # 创建消息唯一标识符用于去重 - 使用更稳定的哈希方法
            import hashlib
            message_content = f"{log_source}:{log_message}".encode('utf-8')
            message_id = hashlib.md5(message_content).hexdigest()
            
            # 检查是否是重复消息
            if message_id in self.processed_messages:
                logger.debug(f"跳过重复消息: {log_source} - {log_message[:50]}...")
                return
            
            # 记录已处理的消息
            self.processed_messages.add(message_id)
            logger.debug(f"处理新消息: {log_source} - {log_message[:50]}...")
            
            # 检查是否是演练结束消息
            if log_source == "攻防演练裁判" and ("胜利" in log_message or "演练结束" in log_message):
                await self.send_log("info", "🏁 检测到演练结束信号，停止防御协调器")
                logger.info("演练已结束，防御协调器停止工作")
                self.running = False
                return
            
            # 如果演练已结束，不再触发防御响应
            if not self.running:
                return
            
            # 分析日志，确定需要触发的防御智能体
            triggered_agents = self.analyze_log_for_defense_triggers(log_message, log_source)
            
            if triggered_agents:
                # 提取上下文信息
                context = self.extract_context_from_log(log_message, log_source)
                
                await self.send_log("info", f"检测到攻击活动，准备触发防御响应: {', '.join(triggered_agents)}")
                logger.info(f"日志触发防御响应: {log_message[:100]}... -> {triggered_agents}")
                
                # 并行触发所有相关的防御智能体
                tasks = []
                for agent_type in triggered_agents:
                    task = self.trigger_defense_agent(agent_type, context)
                    tasks.append(task)
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    
        except Exception as e:
            logger.error(f"处理日志消息失败: {e}")
    
    async def listen_to_logs(self):
        """监听WebSocket日志"""
        while self.running:
            try:
                if not self.ws_connection:
                    await self.connect_to_backend()
                    if not self.ws_connection:
                        await asyncio.sleep(5)
                        continue
                
                # 接收消息
                message = await self.ws_connection.recv()
                message_data = json.loads(message)
                
                # 处理日志消息
                await self.process_log_message(message_data)
                
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket连接已断开，尝试重新连接...")
                self.ws_connection = None
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"监听日志时出错: {e}")
                await asyncio.sleep(1)
    
    async def start(self):
        """启动防御协调器"""
        self.running = True
        await self.send_log("info", "防御协调器已启动，开始监听攻击日志")
        logger.info("防御协调器已启动")
        
        try:
            await self.listen_to_logs()
        except KeyboardInterrupt:
            logger.info("收到停止信号")
        finally:
            await self.stop()
    
    async def stop(self):
        """停止防御协调器"""
        self.running = False
        if self.ws_connection:
            await self.ws_connection.close()
        await self.send_log("info", "防御协调器已停止")
        logger.info("防御协调器已停止")

async def main():
    """主函数"""
    coordinator = DefenseCoordinator()
    await coordinator.start()

if __name__ == "__main__":
    asyncio.run(main())