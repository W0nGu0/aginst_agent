#!/usr/bin/env python3
"""
最终修复验证脚本
验证：1. 日志去重  2. 漏洞修复  3. 裁判判决时机
"""

import asyncio
import json
import websockets
import time

# 测试消息 - 完整的攻防流程
FINAL_TEST_MESSAGES = [
    # 1. 演练开始
    {
        "level": "info",
        "source": "攻防演练裁判",
        "message": "🚀 攻防演练开始！",
        "timestamp": time.time()
    },
    
    # 2. 攻击阶段 - 攻陷节点
    {
        "level": "warning",
        "source": "攻击智能体", 
        "message": "利用阶段完成，获得目标主机 web-server 访问权限",
        "timestamp": time.time()
    },
    
    {
        "level": "critical",
        "source": "攻击智能体",
        "message": "数据窃取完成，成功获取数据库核心数据",
        "timestamp": time.time()
    },
    
    # 3. 防御响应 - 威胁检测和阻断
    {
        "level": "warning",
        "source": "威胁阻断智能体", 
        "message": "检测到端口扫描行为，发现恶意IP 192.168.100.11",
        "timestamp": time.time()
    },
    
    {
        "level": "success",
        "source": "威胁阻断智能体",
        "message": "成功阻断恶意IP 192.168.100.11，防火墙规则已更新",
        "timestamp": time.time()
    },
    
    # 4. 防御响应 - 漏洞修复（应该成功修复并恢复节点）
    {
        "level": "info",
        "source": "漏洞修复智能体",
        "message": "发现系统漏洞CVE-2023-1234，开始应用安全补丁",
        "timestamp": time.time()
    },
    
    {
        "level": "success",
        "source": "漏洞修复智能体",
        "message": "漏洞修复完成，主机 web-server 已加固和恢复",
        "timestamp": time.time()
    },
    
    # 5. 防御响应 - 攻击溯源（完成后应该立即判决）
    {
        "level": "info",
        "source": "攻击溯源智能体",
        "message": "开始分析攻击路径，追踪攻击源头",
        "timestamp": time.time()
    },
    
    {
        "level": "success",
        "source": "攻击溯源智能体",
        "message": "攻击溯源完成，已收集攻击证据并生成事件报告",
        "timestamp": time.time()
    },
    
    # 6. 重复消息测试（应该被去重）
    {
        "level": "success",
        "source": "威胁阻断智能体",
        "message": "成功阻断恶意IP 192.168.100.11，防火墙规则已更新",
        "timestamp": time.time()
    },
    
    {
        "level": "success",
        "source": "漏洞修复智能体",
        "message": "漏洞修复完成，主机 web-server 已加固和恢复",
        "timestamp": time.time()
    }
]

async def test_final_fixes():
    """测试最终修复"""
    print("🔧 测试最终修复效果")
    print("=" * 60)
    
    try:
        uri = "ws://localhost:8080/ws/logs"
        async with websockets.connect(uri) as websocket:
            print("✅ 已连接到WebSocket服务器")
            
            for i, message in enumerate(FINAL_TEST_MESSAGES, 1):
                print(f"\n📤 发送消息 {i}/{len(FINAL_TEST_MESSAGES)}")
                print(f"   来源: {message['source']}")
                print(f"   内容: {message['message'][:60]}...")
                
                # 发送消息
                await websocket.send(json.dumps(message, ensure_ascii=False))
                
                # 特殊处理
                if "生成事件报告" in message['message']:
                    print("   🏁 攻击溯源报告生成，裁判应该立即进行最终判决")
                    await asyncio.sleep(6)  # 等待裁判判决
                elif "漏洞修复完成" in message['message']:
                    if i == 7:  # 第一次修复消息
                        print("   🔄 节点应该从红色脉冲恢复为正常状态")
                        await asyncio.sleep(4)
                    else:  # 重复修复消息
                        print("   🚫 重复消息，应该被去重")
                        await asyncio.sleep(2)
                elif i in [11, 12]:  # 重复消息
                    print("   🔄 重复消息测试，应该被去重")
                    await asyncio.sleep(2)
                else:
                    await asyncio.sleep(3)
            
            print("\n✅ 测试完成")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def print_expected_results():
    """打印预期结果"""
    print("📋 预期测试结果")
    print("=" * 60)
    
    print("1. 🚫 日志去重:")
    print("   - 后端WebSocket应用MD5哈希去重")
    print("   - 重复的防御智能体日志不会重复显示")
    print("   - 防御协调器也会过滤重复消息")
    
    print("\n2. 🔧 漏洞修复:")
    print("   - 漏洞修复智能体能正确识别目标系统")
    print("   - 系统名称映射：web-server -> ws-web-01")
    print("   - 修复完成后节点从红色脉冲变为正常状态")
    print("   - 显示绿色恢复脉冲效果")
    
    print("\n3. ⚖️ 裁判判决时机:")
    print("   - 攻击溯源完成并生成事件报告后")
    print("   - 裁判立即进行最终胜负判定")
    print("   - 不再等待其他防御工作")
    print("   - 判决结果应该在溯源报告后立即显示")
    
    print("\n4. 🎯 整体流程:")
    print("   - 攻击方窃取数据")
    print("   - 防御方完成威胁阻断、漏洞修复、攻击溯源")
    print("   - 溯源报告生成后立即判定攻击方胜利")
    print("   - 所有重复日志被正确过滤")

def print_fix_summary():
    """打印修复总结"""
    print("🔧 修复总结")
    print("=" * 60)
    
    print("1. 后端日志去重 (backend/main.py):")
    print("   - 添加了log_cache缓存机制")
    print("   - 使用MD5哈希创建唯一标识符")
    print("   - 限制缓存大小避免内存泄漏")
    
    print("\n2. 防御协调器去重 (defense_coordinator.py):")
    print("   - 改进了消息哈希算法")
    print("   - 添加了调试日志输出")
    print("   - 修复了目标系统名称映射")
    
    print("\n3. 漏洞修复智能体 (vulnerability_agent.py):")
    print("   - 添加了系统名称映射机制")
    print("   - web-server -> ws-web-01")
    print("   - 支持通用系统名称")
    
    print("\n4. 裁判系统 (battle_judge.py):")
    print("   - 攻击溯源报告生成后立即判决")
    print("   - 不再等待所有防御工作完成")
    print("   - 优化了判决时机")

async def main():
    """主函数"""
    print("🧪 攻防演练系统最终修复验证")
    print("=" * 70)
    
    # 打印修复总结
    print_fix_summary()
    
    # 打印预期结果
    print("\n" + "=" * 70)
    print_expected_results()
    
    # 询问是否开始测试
    print("\n" + "=" * 70)
    response = input("是否开始测试最终修复效果? (y/n): ")
    
    if response.lower() in ['y', 'yes', '是']:
        await test_final_fixes()
        
        print("\n🎉 测试完成！")
        print("请验证:")
        print("  1. 重复日志是否被正确去重")
        print("  2. 被攻陷节点是否正确恢复")
        print("  3. 裁判是否在溯源报告后立即判决")
        print("  4. 漏洞修复智能体是否正常工作")
    else:
        print("测试结束")

if __name__ == "__main__":
    asyncio.run(main())