#!/usr/bin/env python3
"""
修正后的攻防演练逻辑测试脚本
验证：1. 等待防御工作完成后再判定胜负  2. 简化的日志去重
"""

import asyncio
import json
import websockets
import time

# 测试消息 - 完整的攻防流程
COMPLETE_BATTLE_MESSAGES = [
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
    
    # 3. 防御响应阶段 - 按顺序完成三个核心工作
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
    
    {
        "level": "success",
        "source": "漏洞修复智能体",
        "message": "漏洞修复完成，主机 web-server 已加固和恢复",
        "timestamp": time.time()
    },
    
    {
        "level": "success",
        "source": "攻击溯源智能体",
        "message": "攻击溯源完成，已收集攻击证据并生成报告",
        "timestamp": time.time()
    },
    
    # 4. 重复消息测试（应该被去重）
    {
        "level": "warning",
        "source": "威胁阻断智能体", 
        "message": "检测到端口扫描行为，发现恶意IP 192.168.100.11",
        "timestamp": time.time()
    }
]

async def test_corrected_battle_logic():
    """测试修正后的攻防演练逻辑"""
    print("🔄 测试修正后的攻防演练逻辑")
    print("=" * 60)
    
    try:
        uri = "ws://localhost:8080/ws/logs"
        async with websockets.connect(uri) as websocket:
            print("✅ 已连接到WebSocket服务器")
            
            for i, message in enumerate(COMPLETE_BATTLE_MESSAGES, 1):
                print(f"\n📤 发送消息 {i}/{len(COMPLETE_BATTLE_MESSAGES)}")
                print(f"   来源: {message['source']}")
                print(f"   内容: {message['message'][:60]}...")
                
                # 发送消息
                await websocket.send(json.dumps(message, ensure_ascii=False))
                
                # 特殊处理
                if "数据窃取完成" in message['message']:
                    print("   📊 数据已被窃取，但需等待防御工作完成")
                    await asyncio.sleep(3)
                elif "攻击溯源完成" in message['message']:
                    print("   🏁 防御工作全部完成，裁判应该开始最终判定")
                    await asyncio.sleep(5)  # 等待裁判判定
                elif "重复消息" in str(i):
                    print("   🔄 重复消息，应该被去重")
                    await asyncio.sleep(1)
                else:
                    await asyncio.sleep(3)
            
            print("\n✅ 测试完成")
            print("\n📋 预期结果:")
            print("   1. 数据窃取后不会立即判定胜负")
            print("   2. 等待威胁阻断、漏洞修复、攻击溯源全部完成")
            print("   3. 防御工作完成后判定攻击方胜利（因为数据已被窃取）")
            print("   4. 重复的威胁阻断消息被去重，不会重复触发")
            print("   5. 胜负判定日志应该在最后显示，不会被其他日志顶上去")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def print_key_changes():
    """打印关键修改点"""
    print("🔧 关键修改点")
    print("=" * 60)
    print("1. 胜负判定逻辑修正:")
    print("   - 攻击方胜利：数据被窃取 AND 防御工作完成")
    print("   - 防御方胜利：数据未被窃取 AND 防御工作完成")
    print("   - 防御工作包括：威胁检测、IP阻断、漏洞修复、攻击溯源")
    
    print("\n2. 日志去重简化:")
    print("   - 只保留基本的消息去重功能")
    print("   - 移除了触发频率限制")
    print("   - 移除了自动清理过期消息")
    
    print("\n3. 防御完成通知:")
    print("   - 防御智能体完成工作后通知裁判")
    print("   - 裁判收到通知后进行最终胜负判定")
    print("   - 确保胜负判定日志在最后显示")

async def main():
    """主函数"""
    print("🧪 修正后的攻防演练逻辑验证")
    print("=" * 70)
    
    # 打印关键修改点
    print_key_changes()
    
    # 询问是否开始测试
    print("\n" + "=" * 70)
    response = input("是否开始测试修正后的逻辑? (y/n): ")
    
    if response.lower() in ['y', 'yes', '是']:
        await test_corrected_battle_logic()
    else:
        print("测试结束")

if __name__ == "__main__":
    asyncio.run(main())