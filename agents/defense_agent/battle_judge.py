"""
攻防演练裁判系统 (Battle Judge)
负责判定攻防演练的胜负结果
"""

import asyncio
import json
import logging
import websockets.client
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
from dotenv import load_dotenv

# --- 设置日志 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("battle-judge")

# --- 环境变量 ---
dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

BACKEND_WS_URL = "ws://localhost:8080/ws/logs"

class BattleJudge:
    def __init__(self):
        self.ws_connection = None
        self.battle_state = {
            "status": "ongoing",  # ongoing, attack_victory, defense_victory
            "start_time": None,
            "end_time": None,
            "attack_progress": {
                "reconnaissance": False,
                "weaponization": False,
                "delivery": False,
                "exploitation": False,
                "installation": False,
                "command_and_control": False,
                "actions_on_objectives": False,
                "data_exfiltrated": False
            },
            "defense_actions": {
                "threat_detected": False,
                "ip_blocked": False,
                "vulnerability_patched": False,
                "system_recovered": False,
                "attack_traced": False,
                "evidence_collected": False
            },
            "compromised_assets": set(),
            "recovered_assets": set(),
            "blocked_ips": set(),
            "patched_vulnerabilities": set()
        }
        
        # 胜负判定规则 - 必须等待防御工作完成后再判定
        self.victory_conditions = {
            "attack_victory": [
                # 攻击方胜利：数据被窃取且防御工作已完成
                lambda state: (
                    state["attack_progress"]["data_exfiltrated"] and
                    self.is_defense_work_completed(state)
                )
            ],
            "defense_victory": [
                # 防御方胜利：防御工作全部完成且数据未被窃取
                lambda state: (
                    not state["attack_progress"]["data_exfiltrated"] and
                    self.is_defense_work_completed(state)
                )
            ]
        }
    
    async def connect_to_backend(self):
        """连接到后端WebSocket"""
        try:
            self.ws_connection = await websockets.client.connect(BACKEND_WS_URL)
            logger.info("攻防演练裁判系统已连接到WebSocket")
            return True
        except Exception as e:
            logger.error(f"连接WebSocket失败: {e}")
            return False
    
    async def send_log(self, level: str, message: str):
        """发送裁判日志"""
        if self.ws_connection:
            try:
                log_data = {
                    "level": level,
                    "source": "攻防演练裁判",
                    "message": message,
                    "timestamp": asyncio.get_event_loop().time(),
                    "battle_state": self.battle_state
                }
                await self.ws_connection.send(json.dumps(log_data, ensure_ascii=False))
            except Exception as e:
                logger.error(f"发送裁判日志失败: {e}")
    
    def update_attack_progress(self, log_message: str):
        """更新攻击进度"""
        message = log_message.lower()
        
        if "完成目标侦察" in log_message or "侦察阶段完成" in log_message:
            self.battle_state["attack_progress"]["reconnaissance"] = True
            logger.info("攻击进度更新: 侦察阶段完成")
        elif "完成恶意载荷制作" in log_message or "武器化完成" in log_message:
            self.battle_state["attack_progress"]["weaponization"] = True
            logger.info("攻击进度更新: 武器化阶段完成")
        elif "钓鱼邮件成功投递" in log_message or "投递阶段完成" in log_message:
            self.battle_state["attack_progress"]["delivery"] = True
            logger.info("攻击进度更新: 投递阶段完成")
        elif "获得目标主机访问权限" in log_message or "漏洞被利用" in log_message or "利用阶段完成" in log_message:
            self.battle_state["attack_progress"]["exploitation"] = True
            logger.info("攻击进度更新: 利用阶段完成")
            # 提取被攻陷的资产
            if "主机" in log_message:
                import re
                hosts = re.findall(r'主机\s+([^\s]+)', log_message)
                for host in hosts:
                    self.battle_state["compromised_assets"].add(host)
                    logger.info(f"资产被攻陷: {host}")
        elif "安装后门" in log_message or "持久化访问" in log_message or "安装阶段完成" in log_message:
            self.battle_state["attack_progress"]["installation"] = True
            logger.info("攻击进度更新: 安装阶段完成")
        elif "建立c2通信" in message or "命令控制" in log_message or "c2阶段完成" in log_message:
            self.battle_state["attack_progress"]["command_and_control"] = True
            logger.info("攻击进度更新: C2阶段完成")
        elif "数据窃取" in log_message or "数据被窃取" in log_message or "目标行动完成" in log_message or "攻击链完成" in log_message:
            self.battle_state["attack_progress"]["actions_on_objectives"] = True
            self.battle_state["attack_progress"]["data_exfiltrated"] = True
            logger.info("攻击进度更新: 数据窃取完成 - 这可能触发攻击方胜利")
    
    async def update_defense_actions(self, log_message: str, log_source: str):
        """更新防御行动"""
        message = log_message.lower()
        
        if "威胁阻断" in log_source:
            if "检测到" in log_message or "发现" in log_message:
                self.battle_state["defense_actions"]["threat_detected"] = True
                logger.info("防御进度更新: 威胁检测完成")
            elif "阻断" in log_message or "黑名单" in log_message:
                self.battle_state["defense_actions"]["ip_blocked"] = True
                logger.info("防御进度更新: IP阻断完成")
                # 提取被阻断的IP
                import re
                ips = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', log_message)
                for ip in ips:
                    self.battle_state["blocked_ips"].add(ip)
                    logger.info(f"IP已阻断: {ip}")
        
        elif "漏洞修复" in log_source:
            if "修复" in log_message or "补丁" in log_message:
                self.battle_state["defense_actions"]["vulnerability_patched"] = True
                logger.info("防御进度更新: 漏洞修复完成")
                # 提取修复的漏洞
                import re
                cves = re.findall(r'CVE-\d{4}-\d+', log_message)
                for cve in cves:
                    self.battle_state["patched_vulnerabilities"].add(cve)
                    logger.info(f"漏洞已修复: {cve}")
            elif "恢复" in log_message or "加固" in log_message:
                self.battle_state["defense_actions"]["system_recovered"] = True
                logger.info("防御进度更新: 系统恢复完成")
                # 提取恢复的资产
                import re
                hosts = re.findall(r'主机\s+([^\s]+)', log_message)
                for host in hosts:
                    self.battle_state["recovered_assets"].add(host)
                    logger.info(f"资产已恢复: {host}")
        
        elif "攻击溯源" in log_source:
            if "溯源" in log_message or "分析" in log_message:
                self.battle_state["defense_actions"]["attack_traced"] = True
                logger.info("防御进度更新: 攻击溯源完成")
            elif "证据" in log_message or "报告" in log_message:
                self.battle_state["defense_actions"]["evidence_collected"] = True
                logger.info("防御进度更新: 证据收集完成")
                # 攻击溯源完成报告生成后，立即触发最终判定
                logger.info("攻击溯源报告已生成，准备进行最终胜负判定")
                await self.check_defense_completion()
        
        # 检查防御工作是否全部完成
        await self.check_defense_completion()
    
    def check_victory_conditions(self):
        """检查胜负条件"""
        # 如果演练已经结束，不再检查
        if self.battle_state["status"] != "ongoing":
            return self.battle_state["status"]
        
        # 检查攻击方胜利条件
        for condition in self.victory_conditions["attack_victory"]:
            if condition(self.battle_state):
                logger.info("攻击方胜利条件满足")
                return "attack_victory"
        
        # 检查防御方胜利条件  
        for condition in self.victory_conditions["defense_victory"]:
            if condition(self.battle_state):
                logger.info("防御方胜利条件满足")
                return "defense_victory"
        
        # 检查超时条件（演练时间过长自动判定）
        if self.battle_state["start_time"]:
            from datetime import datetime, timedelta
            start_time = datetime.fromisoformat(self.battle_state["start_time"])
            if datetime.now() - start_time > timedelta(minutes=15):  # 15分钟超时
                # 根据当前状态判定胜负
                if self.battle_state["attack_progress"]["data_exfiltrated"]:
                    logger.info("演练超时，攻击方已窃取数据，判定攻击方胜利")
                    return "attack_victory"
                elif self.battle_state["defense_actions"]["vulnerability_patched"]:
                    logger.info("演练超时，防御方已修复漏洞，判定防御方胜利")
                    return "defense_victory"
        
        return "ongoing"
    
    async def declare_victory(self, winner: str):
        """宣布胜负结果"""
        self.battle_state["status"] = winner
        self.battle_state["end_time"] = datetime.now().isoformat()
        
        if winner == "attack_victory":
            await self.send_log("critical", "🔴 攻防演练结束 - 攻击方胜利！")
            await self.send_log("info", "攻击方成功完成攻击目标，防御方响应不及时")
            
            # 详细战果统计
            compromised_count = len(self.battle_state["compromised_assets"])
            recovered_count = len(self.battle_state["recovered_assets"])
            
            await self.send_log("info", f"战果统计 - 被攻陷资产: {compromised_count}, 已恢复资产: {recovered_count}")
            
            if self.battle_state["attack_progress"]["data_exfiltrated"]:
                await self.send_log("critical", "关键数据已被窃取，造成重大安全损失")
            
        elif winner == "defense_victory":
            await self.send_log("success", "🟢 攻防演练结束 - 防御方胜利！")
            await self.send_log("info", "防御方成功阻断攻击并恢复系统安全")
            
            # 详细防御统计
            blocked_ips_count = len(self.battle_state["blocked_ips"])
            patched_vulns_count = len(self.battle_state["patched_vulnerabilities"])
            
            await self.send_log("info", f"防御统计 - 阻断IP: {blocked_ips_count}, 修复漏洞: {patched_vulns_count}")
            
            if not self.battle_state["attack_progress"]["data_exfiltrated"]:
                await self.send_log("success", "成功保护关键数据，未发生数据泄露")
        
        # 生成详细战报
        await self.generate_battle_report()
    
    def is_defense_work_completed(self, state):
        """检查防御工作是否全部完成"""
        defense_actions = state["defense_actions"]
        
        # 核心防御工作：威胁阻断、漏洞修复、攻击溯源
        core_actions_completed = (
            defense_actions["threat_detected"] and
            defense_actions["ip_blocked"] and
            defense_actions["vulnerability_patched"] and
            defense_actions["attack_traced"]
        )
        
        return core_actions_completed
    
    async def check_defense_completion(self):
        """检查防御工作完成并通知裁判进行最终判定"""
        if self.is_defense_work_completed(self.battle_state):
            logger.info("🛡️ 所有防御工作已完成，通知裁判进行最终胜负判定")
            await self.send_log("info", "防御智能体工作完成，请求最终胜负判定")
            
            # 立即检查胜负条件
            result = self.check_victory_conditions()
            if result != "ongoing":
                await self.declare_victory(result)

    async def generate_battle_report(self):
        """生成详细战报"""
        start_time = self.battle_state.get("start_time")
        end_time = self.battle_state.get("end_time")
        
        duration = "未知"
        if start_time and end_time:
            from datetime import datetime
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            duration_seconds = (end_dt - start_dt).total_seconds()
            duration = f"{int(duration_seconds // 60)}分{int(duration_seconds % 60)}秒"
        
        report = {
            "battle_duration": duration,
            "attack_stages_completed": sum(1 for completed in self.battle_state["attack_progress"].values() if completed),
            "defense_actions_taken": sum(1 for completed in self.battle_state["defense_actions"].values() if completed),
            "compromised_assets": list(self.battle_state["compromised_assets"]),
            "recovered_assets": list(self.battle_state["recovered_assets"]),
            "blocked_ips": list(self.battle_state["blocked_ips"]),
            "patched_vulnerabilities": list(self.battle_state["patched_vulnerabilities"]),
            "final_result": self.battle_state["status"]
        }
        
        await self.send_log("info", f"📊 攻防演练战报: {json.dumps(report, ensure_ascii=False, indent=2)}")
    
    async def process_log_message(self, message_data: Dict[str, Any]):
        """处理日志消息并更新战况"""
        try:
            log_message = message_data.get("message", "")
            log_source = message_data.get("source", "")
            
            # 跳过裁判自己的日志
            if "攻防演练裁判" in log_source:
                return
            
            # 初始化战斗状态
            if not self.battle_state["start_time"] and "攻击智能体" in log_source:
                self.battle_state["start_time"] = datetime.now().isoformat()
                await self.send_log("info", "🚀 攻防演练开始！")
            
            # 更新攻击进度
            if "攻击智能体" in log_source:
                self.update_attack_progress(log_message)
            
            # 更新防御行动
            elif any(defense_agent in log_source for defense_agent in ["威胁阻断", "漏洞修复", "攻击溯源"]):
                await self.update_defense_actions(log_message, log_source)
            
            # 检查胜负条件
            if self.battle_state["status"] == "ongoing":
                result = self.check_victory_conditions()
                if result != "ongoing":
                    await self.declare_victory(result)
                    
        except Exception as e:
            logger.error(f"处理战况更新失败: {e}")
    
    async def monitor_battle(self):
        """监控攻防演练"""
        while True:
            try:
                if not self.ws_connection:
                    await self.connect_to_backend()
                    if not self.ws_connection:
                        await asyncio.sleep(5)
                        continue
                
                message = await self.ws_connection.recv()
                message_data = json.loads(message)
                await self.process_log_message(message_data)
                
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket连接断开，尝试重连...")
                self.ws_connection = None
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"监控战况时出错: {e}")
                await asyncio.sleep(1)
    
    async def start(self):
        """启动裁判系统"""
        await self.send_log("info", "攻防演练裁判系统已启动")
        logger.info("攻防演练裁判系统已启动")
        
        try:
            await self.monitor_battle()
        except KeyboardInterrupt:
            logger.info("收到停止信号")
        finally:
            if self.ws_connection:
                await self.ws_connection.close()

async def main():
    judge = BattleJudge()
    await judge.start()

if __name__ == "__main__":
    asyncio.run(main())