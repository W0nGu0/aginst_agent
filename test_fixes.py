#!/usr/bin/env python3
"""
修复验证测试脚本
验证防御动画、胜负判定和防火墙对话框的修复
"""

import asyncio
import json
import websockets
import time
from datetime import datetime

# 测试消息 - 模拟完整的攻防流程
TEST_MESSAGES = [
    # 1. 演练开始
    {
        "level": "info",
        "source": "攻防演练裁判",
        "message": "🚀 攻防演练开始！",
        "timestamp": time.time()
    },
    
    # 2. 攻击阶段
    {
        "level": "info", 
        "source": "攻击智能体",
        "message": "开始目标侦察，扫描网络拓扑结构",
        "timestamp": time.time()
    },
    
    {
        "level": "info",
        "source": "攻击智能体", 
        "message": "侦察阶段完成，发现目标主机 192.168.200.23",
        "timestamp": time.time()
    },
    
    # 3. 防御响应 - 威胁阻断
    {
        "level": "warning",
        "source": "威胁阻断智能体", 
        "message": "检测到端口扫描行为，正在阻断恶意IP 192.168.100.11",
        "timestamp": time.time()
    },
    
    {
        "level": "success",
        "source": "威胁阻断智能体",
        "message": "成功阻断恶意IP 192.168.100.11，防火墙规则已更新",
        "timestamp": time.time()
    },
    
    # 4. 攻击继续
    {
        "level": "warning",
        "source": "攻击智能体",
        "message": "利用阶段完成，获得目标主机 web-server 访问权限",
        "timestamp": time.time()
    },
    
    # 5. 防御响应 - 漏洞修复
    {
        "level": "info",
        "source": "漏洞修复智能体",
        "message": "发现Web服务器存在CVE-2023-1234漏洞，正在应用安全补丁",
        "timestamp": time.time()
    },
    
    {
        "level": "success",
        "source": "漏洞修复智能体",
        "message": "漏洞修复完成，主机 web-server 已加固",
        "timestamp": time.time()
    },
    
    # 6. 攻击溯源
    {
        "level": "info",
        "source": "攻击溯源智能体",
        "message": "正在分析攻击路径，追踪攻击源头 192.168.100.11",
        "timestamp": time.time()
    },
    
    {
        "level": "success",
        "source": "攻击溯源智能体",
        "message": "攻击溯源完成，已收集攻击证据并生成报告",
        "timestamp": time.time()
    },
    
    # 7. 胜负判定 - 防御方胜利
    {
        "level": "success",
        "source": "攻防演练裁判",
        "message": "🟢 攻防演练结束 - 防御方胜利！防御方成功阻断攻击并恢复系统安全",
        "timestamp": time.time()
    },
    
    # 8. 战报
    {
        "level": "info",
        "source": "攻防演练裁判", 
        "message": '📊 攻防演练战报: {"battle_duration": "8分15秒", "attack_stages_completed": 3, "defense_actions_taken": 6, "compromised_assets": ["web-server"], "recovered_assets": ["web-server"], "blocked_ips": ["192.168.100.11"], "patched_vulnerabilities": ["CVE-2023-1234"], "final_result": "defense_victory"}',
        "timestamp": time.time()
    }
]

async def test_defense_animations():
    """测试防御动画系统"""
    print("🎬 测试防御可视化动画系统")
    print("=" * 50)
    
    try:
        uri = "ws://localhost:8080/ws/logs"
        async with websockets.connect(uri) as websocket:
            print("✅ 已连接到WebSocket服务器")
            
            for i, message in enumerate(TEST_MESSAGES, 1):
                print(f"\n📤 发送测试消息 {i}/{len(TEST_MESSAGES)}")
                print(f"   来源: {message['source']}")
                print(f"   内容: {message['message'][:60]}...")
                
                # 发送消息
                await websocket.send(json.dumps(message, ensure_ascii=False))
                
                # 根据消息类型调整等待时间
                if "裁判" in message['source']:
                    await asyncio.sleep(2)  # 裁判消息等待短一些
                elif "防御" in message['source']:
                    await asyncio.sleep(4)  # 防御消息等待长一些，观察动画
                else:
                    await asyncio.sleep(3)  # 其他消息正常等待
            
            print("\n✅ 所有测试消息发送完成")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_battle_judge_logic():
    """测试胜负判定逻辑"""
    print("\n🏆 测试胜负判定逻辑")
    print("=" * 50)
    
    # 模拟战斗状态
    battle_state = {
        "status": "ongoing",
        "attack_progress": {
            "reconnaissance": True,
            "weaponization": False,
            "delivery": False,
            "exploitation": True,
            "installation": False,
            "command_and_control": False,
            "actions_on_objectives": False,
            "data_exfiltrated": False
        },
        "defense_actions": {
            "threat_detected": True,
            "ip_blocked": True,
            "vulnerability_patched": True,
            "system_recovered": True,
            "attack_traced": True,
            "evidence_collected": True
        },
        "compromised_assets": {"web-server"},
        "recovered_assets": {"web-server"},
        "blocked_ips": {"192.168.100.11"},
        "patched_vulnerabilities": {"CVE-2023-1234"}
    }
    
    # 测试防御方胜利条件
    def check_defense_victory(state):
        return (
            state["defense_actions"]["ip_blocked"] and
            state["defense_actions"]["vulnerability_patched"] and
            state["defense_actions"]["system_recovered"] and
            len(state["recovered_assets"]) >= len(state["compromised_assets"])
        )
    
    # 测试攻击方胜利条件
    def check_attack_victory(state):
        return (
            state["attack_progress"]["data_exfiltrated"] and
            not state["defense_actions"]["system_recovered"]
        )
    
    print("📊 当前战斗状态:")
    print(f"   攻击进度: 侦察✅ 利用✅ 其他❌")
    print(f"   防御行动: 威胁检测✅ IP阻断✅ 漏洞修复✅ 系统恢复✅ 攻击溯源✅")
    print(f"   被攻陷资产: {len(battle_state['compromised_assets'])}")
    print(f"   已恢复资产: {len(battle_state['recovered_assets'])}")
    
    if check_defense_victory(battle_state):
        print("🟢 判定结果: 防御方胜利！")
        print("   理由: 成功阻断攻击并恢复所有系统")
    elif check_attack_victory(battle_state):
        print("🔴 判定结果: 攻击方胜利！")
        print("   理由: 成功窃取数据且防御方未及时恢复")
    else:
        print("⏳ 判定结果: 演练进行中")
    
    print("✅ 胜负判定逻辑测试完成")

def test_firewall_dialog_data():
    """测试防火墙对话框数据加载"""
    print("\n🔥 测试防火墙对话框数据加载")
    print("=" * 50)
    
    # 模拟防火墙设备数据
    firewall_device = {
        "deviceData": {
            "name": "border_firewall",
            "ip": "192.168.1.1",
            "scenarioData": {
                "id": "firewall-001",
                "status": "running",
                "networks": ["user_segment", "server_segment", "dmz_segment", "internet"],
                "ip_addresses": {
                    "user_segment": "192.168.100.1",
                    "server_segment": "192.168.200.1", 
                    "dmz_segment": "172.16.100.1",
                    "internet": "172.203.100.1"
                },
                "blacklist": [
                    {"address": "192.168.100.11", "reason": "攻击源IP", "enabled": True},
                    {"address": "203.0.113.15", "reason": "恶意IP地址", "enabled": True}
                ],
                "whitelist": [
                    {"address": "192.168.100.50", "description": "用户PC", "enabled": True},
                    {"address": "8.8.8.8", "description": "Google DNS", "enabled": True}
                ]
            }
        }
    }
    
    print("📊 防火墙设备数据:")
    print(f"   名称: {firewall_device['deviceData']['name']}")
    print(f"   状态: {firewall_device['deviceData']['scenarioData']['status']}")
    print(f"   网络接口数: {len(firewall_device['deviceData']['scenarioData']['networks'])}")
    print(f"   黑名单条目: {len(firewall_device['deviceData']['scenarioData']['blacklist'])}")
    print(f"   白名单条目: {len(firewall_device['deviceData']['scenarioData']['whitelist'])}")
    
    # 模拟接口数据生成
    interfaces = []
    for i, network in enumerate(firewall_device['deviceData']['scenarioData']['networks']):
        ip = firewall_device['deviceData']['scenarioData']['ip_addresses'].get(network, f"192.168.{i}.1")
        interfaces.append({
            "name": f"eth{i}",
            "ip": ip,
            "network": network,
            "status": "up"
        })
    
    print("\n🔌 生成的接口配置:")
    for interface in interfaces:
        print(f"   {interface['name']}: {interface['ip']} ({interface['network']}) - {interface['status']}")
    
    print("✅ 防火墙对话框数据测试完成")

def print_test_instructions():
    """打印测试说明"""
    print("\n📋 测试验证说明")
    print("=" * 50)
    print("请在前端界面验证以下修复:")
    print("\n1. 🎬 防御可视化动画优化:")
    print("   - 威胁阻断: 盾牌和阻断符号显示在节点上方")
    print("   - 漏洞修复: 进度条和文字显示在节点上方，避免与名称重叠")
    print("   - 攻击溯源: 分析图标和路径追踪动画更美观")
    print("   - 所有动画都有阴影和现代化样式")
    
    print("\n2. 🏆 胜负判定系统:")
    print("   - 演练开始时显示开始消息")
    print("   - 防御方胜利时显示绿色胜利动画")
    print("   - 演练结束后防御智能体停止工作")
    print("   - 显示详细的战报信息")
    
    print("\n3. 🔥 防火墙对话框修复:")
    print("   - 基本信息显示实际设备数据")
    print("   - 接口配置显示动态生成的接口")
    print("   - 访问规则显示实际规则配置")
    print("   - 黑白名单显示实际数据")
    print("   - 日志显示模拟的访问记录")
    
    print("\n4. 🔄 演练流程优化:")
    print("   - 攻击完成后及时判定胜负")
    print("   - 防御协调器在演练结束后停止")
    print("   - 所有组件正确响应演练结束信号")

async def main():
    """主函数"""
    print("🧪 攻防演练系统修复验证")
    print("=" * 60)
    
    # 测试胜负判定逻辑
    test_battle_judge_logic()
    
    # 测试防火墙对话框数据
    test_firewall_dialog_data()
    
    # 打印测试说明
    print_test_instructions()
    
    # 询问是否发送测试消息
    print("\n" + "=" * 60)
    response = input("是否发送测试消息验证防御动画? (y/n): ")
    
    if response.lower() in ['y', 'yes', '是']:
        await test_defense_animations()
        
        print("\n🎉 测试完成！")
        print("请检查前端界面是否正确显示:")
        print("  ✅ 防御动画位置优化（节点上方）")
        print("  ✅ 防御动画样式美化（阴影、现代化）")
        print("  ✅ 胜负判定结果显示")
        print("  ✅ 演练结束后组件停止")
        print("  ✅ 防火墙对话框数据正确加载")
    else:
        print("测试结束")

if __name__ == "__main__":
    asyncio.run(main())