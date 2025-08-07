#!/usr/bin/env python3
"""
攻防演练系统测试脚本
用于验证胜负判定和防御可视化系统是否正常工作
"""

import asyncio
import json
import websockets
import time
from datetime import datetime

# 测试消息模板
TEST_MESSAGES = [
    # 1. 演练开始
    {
        "level": "info",
        "source": "攻防演练裁判",
        "message": "🚀 攻防演练开始！",
        "timestamp": time.time()
    },
    
    # 2. 攻击阶段消息
    {
        "level": "info", 
        "source": "攻击智能体",
        "message": "开始目标侦察，扫描网络拓扑结构",
        "timestamp": time.time()
    },
    
    # 3. 防御响应消息
    {
        "level": "warning",
        "source": "威胁阻断智能体", 
        "message": "检测到端口扫描行为，正在阻断恶意IP 192.168.100.11",
        "timestamp": time.time()
    },
    
    # 4. 漏洞修复消息
    {
        "level": "info",
        "source": "漏洞修复智能体",
        "message": "发现Web服务器存在漏洞，正在应用安全补丁",
        "timestamp": time.time()
    },
    
    # 5. 攻击溯源消息
    {
        "level": "info",
        "source": "攻击溯源智能体",
        "message": "正在分析攻击路径，追踪攻击源头",
        "timestamp": time.time()
    },
    
    # 6. 胜负判定消息 - 防御方胜利
    {
        "level": "success",
        "source": "攻防演练裁判",
        "message": "🟢 攻防演练结束 - 防御方胜利！防御方成功阻断攻击并恢复系统安全",
        "timestamp": time.time()
    },
    
    # 7. 战报消息
    {
        "level": "info",
        "source": "攻防演练裁判", 
        "message": '📊 攻防演练战报: {"battle_duration": "5分32秒", "attack_stages_completed": 3, "defense_actions_taken": 5, "compromised_assets": ["web-server"], "recovered_assets": ["web-server"], "blocked_ips": ["192.168.100.11"], "patched_vulnerabilities": ["CVE-2023-1234"], "final_result": "defense_victory"}',
        "timestamp": time.time()
    }
]

async def send_test_messages():
    """发送测试消息到WebSocket"""
    try:
        # 连接到后端WebSocket
        uri = "ws://localhost:8080/ws/logs"
        async with websockets.connect(uri) as websocket:
            print("✅ 已连接到WebSocket服务器")
            
            for i, message in enumerate(TEST_MESSAGES, 1):
                print(f"\n📤 发送测试消息 {i}/{len(TEST_MESSAGES)}")
                print(f"   来源: {message['source']}")
                print(f"   内容: {message['message'][:50]}...")
                
                # 发送消息
                await websocket.send(json.dumps(message, ensure_ascii=False))
                
                # 等待一段时间再发送下一条消息
                await asyncio.sleep(3)
            
            print("\n✅ 所有测试消息发送完成")
            print("请检查前端界面是否正确显示了:")
            print("  1. 防御可视化动画 (威胁阻断、漏洞修复、攻击溯源)")
            print("  2. 胜负判定结果 (防御方胜利)")
            print("  3. 详细战报信息")
            
    except Exception as e:
        print(f"❌ 发送测试消息失败: {e}")

async def test_defense_agents():
    """测试防御智能体是否正常响应"""
    import httpx
    
    agents = {
        "威胁阻断智能体": "http://127.0.0.1:8011/execute_threat_blocking",
        "漏洞修复智能体": "http://127.0.0.1:8012/execute_vulnerability_remediation", 
        "攻击溯源智能体": "http://127.0.0.1:8013/execute_attack_attribution"
    }
    
    print("\n🧪 测试防御智能体连接状态...")
    
    async with httpx.AsyncClient() as client:
        for name, url in agents.items():
            try:
                response = await client.post(url, json={
                    "attack_log": "测试连接",
                    "target_info": "测试目标"
                }, timeout=5.0)
                
                if response.status_code == 200:
                    print(f"✅ {name}: 连接正常")
                else:
                    print(f"⚠️ {name}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {name}: 连接失败 - {e}")

def check_system_status():
    """检查系统组件状态"""
    print("🔍 检查攻防演练系统状态...")
    print("\n📋 系统组件清单:")
    print("  1. 后端服务 (backend/main.py) - 端口 8080")
    print("  2. 攻击智能体 (agents/attack_agent/main.py)")
    print("  3. 防御智能体组 (agents/defense_agent/start_defense_agents.py)")
    print("     - 威胁阻断智能体 (端口 8011)")
    print("     - 漏洞修复智能体 (端口 8012)")
    print("     - 攻击溯源智能体 (端口 8013)")
    print("     - 防御协调器 (WebSocket监听)")
    print("     - 攻防演练裁判 (WebSocket监听)")
    print("  4. 前端界面 (TopologyView.vue)")
    print("     - 防御可视化动画系统")
    print("     - 胜负判定显示系统")
    print("     - 战报展示系统")
    
    print("\n🚀 启动建议:")
    print("  1. cd backend && python main.py")
    print("  2. cd agents/defense_agent && python start_defense_agents.py")
    print("  3. cd agents/attack_agent && python main.py")
    print("  4. 打开前端界面，进入拓扑图页面")
    print("  5. 运行此测试脚本: python test_battle_system.py")

async def main():
    """主函数"""
    print("🎯 攻防演练系统测试工具")
    print("=" * 50)
    
    # 检查系统状态
    check_system_status()
    
    # 测试防御智能体连接
    await test_defense_agents()
    
    # 询问是否发送测试消息
    print("\n" + "=" * 50)
    response = input("是否发送测试消息到WebSocket? (y/n): ")
    
    if response.lower() in ['y', 'yes', '是']:
        await send_test_messages()
    else:
        print("测试结束")

if __name__ == "__main__":
    asyncio.run(main())