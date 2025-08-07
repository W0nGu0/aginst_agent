#!/usr/bin/env python3
"""
攻防演练系统改进验证脚本
验证主机恢复、胜负判定和日志去重的修复
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
    
    # 2. 攻击阶段 - 侦察
    {
        "level": "info", 
        "source": "攻击智能体",
        "message": "开始目标侦察，扫描网络拓扑结构",
        "timestamp": time.time()
    },
    
    # 3. 攻击阶段 - 利用漏洞攻陷主机
    {
        "level": "warning",
        "source": "攻击智能体", 
        "message": "利用阶段完成，获得目标主机 web-server 访问权限",
        "timestamp": time.time()
    },
    
    # 4. 防御响应 - 威胁检测
    {
        "level": "warning",
        "source": "威胁阻断智能体", 
        "message": "检测到端口扫描行为，发现恶意IP 192.168.100.11",
        "timestamp": time.time()
    },
    
    # 5. 防御响应 - IP阻断
    {
        "level": "success",
        "source": "威胁阻断智能体",
        "message": "成功阻断恶意IP 192.168.100.11，防火墙规则已更新",
        "timestamp": time.time()
    },
    
    # 6. 防御响应 - 漏洞修复（应该恢复主机状态）
    {
        "level": "success",
        "source": "漏洞修复智能体",
        "message": "漏洞修复完成，主机 web-server 已加固和恢复",
        "timestamp": time.time()
    },
    
    # 7. 防御响应 - 攻击溯源
    {
        "level": "success",
        "source": "攻击溯源智能体",
        "message": "攻击溯源完成，已收集攻击证据并生成报告",
        "timestamp": time.time()
    },
    
    # 8. 攻击继续 - 数据窃取（等待防御工作完成后再判定）
    {
        "level": "critical",
        "source": "攻击智能体",
        "message": "数据窃取完成，成功获取数据库核心数据",
        "timestamp": time.time()
    },
    
    # 9. 重复消息测试（应该被去重）
    {
        "level": "warning",
        "source": "威胁阻断智能体", 
        "message": "检测到端口扫描行为，发现恶意IP 192.168.100.11",
        "timestamp": time.time()
    },
    
    # 10. 重复消息测试（应该被去重）
    {
        "level": "warning",
        "source": "威胁阻断智能体", 
        "message": "检测到端口扫描行为，发现恶意IP 192.168.100.11",
        "timestamp": time.time()
    }
]

# 测试场景2：防御方胜利
DEFENSE_VICTORY_MESSAGES = [
    # 1. 演练开始
    {
        "level": "info",
        "source": "攻防演练裁判",
        "message": "🚀 攻防演练开始！",
        "timestamp": time.time()
    },
    
    # 2. 攻击开始
    {
        "level": "info", 
        "source": "攻击智能体",
        "message": "开始目标侦察，扫描网络拓扑结构",
        "timestamp": time.time()
    },
    
    # 3. 防御快速响应 - 威胁检测
    {
        "level": "warning",
        "source": "威胁阻断智能体", 
        "message": "检测到端口扫描行为，发现恶意IP 192.168.100.11",
        "timestamp": time.time()
    },
    
    # 4. 防御快速响应 - IP阻断
    {
        "level": "success",
        "source": "威胁阻断智能体",
        "message": "成功阻断恶意IP 192.168.100.11，防火墙规则已更新",
        "timestamp": time.time()
    },
    
    # 5. 防御快速响应 - 漏洞修复
    {
        "level": "success",
        "source": "漏洞修复智能体",
        "message": "发现并修复CVE-2023-1234漏洞，系统已加固",
        "timestamp": time.time()
    },
    
    # 6. 防御快速响应 - 攻击溯源
    {
        "level": "success",
        "source": "攻击溯源智能体",
        "message": "攻击溯源完成，已收集攻击证据并生成报告",
        "timestamp": time.time()
    }
]

async def test_attack_victory_scenario():
    """测试攻击方胜利场景"""
    print("🔴 测试攻击方胜利场景")
    print("=" * 50)
    
    try:
        uri = "ws://localhost:8080/ws/logs"
        async with websockets.connect(uri) as websocket:
            print("✅ 已连接到WebSocket服务器")
            
            for i, message in enumerate(TEST_MESSAGES, 1):
                print(f"\n📤 发送消息 {i}/{len(TEST_MESSAGES)}")
                print(f"   来源: {message['source']}")
                print(f"   内容: {message['message'][:60]}...")
                
                # 发送消息
                await websocket.send(json.dumps(message, ensure_ascii=False))
                
                # 特殊等待时间
                if "数据窃取完成" in message['message']:
                    print("   ⚠️ 数据窃取完成，等待防御工作完成后判定胜负")
                    await asyncio.sleep(3)
                elif "重复消息" in message.get('note', ''):
                    print("   🔄 重复消息，应该被去重")
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(3)
            
            print("\n✅ 攻击方胜利场景测试完成")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

async def test_defense_victory_scenario():
    """测试防御方胜利场景"""
    print("\n🟢 测试防御方胜利场景")
    print("=" * 50)
    
    try:
        uri = "ws://localhost:8080/ws/logs"
        async with websockets.connect(uri) as websocket:
            print("✅ 已连接到WebSocket服务器")
            
            for i, message in enumerate(DEFENSE_VICTORY_MESSAGES, 1):
                print(f"\n📤 发送消息 {i}/{len(DEFENSE_VICTORY_MESSAGES)}")
                print(f"   来源: {message['source']}")
                print(f"   内容: {message['message'][:60]}...")
                
                # 发送消息
                await websocket.send(json.dumps(message, ensure_ascii=False))
                
                if "攻击溯源完成" in message['message']:
                    print("   ⚠️ 所有防御工作完成，应该判定防御方胜利")
                    await asyncio.sleep(5)  # 等待裁判判定
                else:
                    await asyncio.sleep(3)
            
            print("\n✅ 防御方胜利场景测试完成")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def print_test_expectations():
    """打印测试期望结果"""
    print("\n📋 测试期望结果")
    print("=" * 50)
    print("请在前端界面验证以下改进:")
    
    print("\n1. 🔄 主机状态恢复:")
    print("   - 当漏洞修复智能体完成修复时")
    print("   - 被攻陷的主机应该从红色脉冲变为正常状态")
    print("   - 应该显示绿色恢复脉冲效果")
    
    print("\n2. ⚡ 胜负判定优化:")
    print("   - 等待防御工作（威胁阻断、漏洞修复、攻击溯源）全部完成")
    print("   - 防御工作完成后，根据数据是否被窃取判定胜负")
    print("   - 数据被窃取且防御完成 → 攻击方胜利")
    print("   - 数据未被窃取且防御完成 → 防御方胜利")
    
    print("\n3. 🚫 日志去重:")
    print("   - 相同的防御智能体日志不会重复触发")
    print("   - 重复消息会被自动过滤")
    print("   - 避免同一条日志触发多次防御响应")
    
    print("\n4. 🏁 演练结束:")
    print("   - 胜负判定后所有智能体停止工作")
    print("   - 显示详细战报")
    print("   - 防御协调器停止监听")

async def main():
    """主函数"""
    print("🧪 攻防演练系统改进验证")
    print("=" * 60)
    
    # 打印测试期望
    print_test_expectations()
    
    # 询问测试场景
    print("\n" + "=" * 60)
    print("选择测试场景:")
    print("1. 攻击方胜利场景（数据窃取成功）")
    print("2. 防御方胜利场景（防御工作完成）")
    print("3. 两个场景都测试")
    
    choice = input("请选择 (1/2/3): ")
    
    if choice == "1":
        await test_attack_victory_scenario()
    elif choice == "2":
        await test_defense_victory_scenario()
    elif choice == "3":
        await test_attack_victory_scenario()
        await asyncio.sleep(10)  # 等待系统重置
        await test_defense_victory_scenario()
    else:
        print("无效选择")
        return
    
    print("\n🎉 测试完成！")
    print("请检查前端界面和控制台日志验证改进效果")

if __name__ == "__main__":
    asyncio.run(main())