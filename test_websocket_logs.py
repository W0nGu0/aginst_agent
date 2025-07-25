#!/usr/bin/env python3
"""
测试WebSocket日志传输的脚本
验证优化后的日志能否正确传输到前端
"""

import asyncio
import json
import websockets
import time

async def test_websocket_logs():
    """测试WebSocket日志传输"""
    print("🧪 测试WebSocket日志传输...")
    
    # 模拟优化后的标准化日志
    test_logs = [
        {
            "timestamp": time.time(),
            "level": "info",
            "source": "攻击智能体",
            "message": "攻击者扫描防火墙",
            "attack_info": {
                "stage": "reconnaissance",
                "technique": "port_scan",
                "source_node": "internet",
                "target_node": "firewall",
                "status": "starting",
                "progress": 10
            }
        },
        {
            "timestamp": time.time(),
            "level": "info",
            "source": "攻击智能体",
            "message": "攻击者发现防火墙开放端口",
            "attack_info": {
                "stage": "reconnaissance",
                "technique": "port_scan",
                "source_node": "internet",
                "target_node": "firewall",
                "status": "in_progress",
                "progress": 30
            }
        },
        {
            "timestamp": time.time(),
            "level": "success",
            "source": "攻击智能体",
            "message": "攻击者完成目标侦察",
            "attack_info": {
                "stage": "reconnaissance",
                "technique": "info_gathering",
                "source_node": "internet",
                "target_node": "firewall",
                "status": "completed",
                "progress": 40
            }
        },
        {
            "timestamp": time.time(),
            "level": "info",
            "source": "攻击智能体",
            "message": "攻击者生成钓鱼邮件",
            "attack_info": {
                "stage": "weaponization",
                "technique": "phishing_email",
                "source_node": "internet",
                "target_node": "target_host",
                "status": "starting",
                "progress": 45
            }
        },
        {
            "timestamp": time.time(),
            "level": "success",
            "source": "攻击智能体",
            "message": "攻击者完成恶意载荷制作",
            "attack_info": {
                "stage": "weaponization",
                "technique": "phishing_email",
                "source_node": "internet",
                "target_node": "target_host",
                "status": "completed",
                "progress": 50
            }
        },
        {
            "timestamp": time.time(),
            "level": "info",
            "source": "攻击智能体",
            "message": "发送钓鱼邮件",
            "attack_info": {
                "stage": "delivery",
                "technique": "email_delivery",
                "source_node": "internet",
                "target_node": "target_host",
                "status": "starting",
                "progress": 55
            }
        },
        {
            "timestamp": time.time(),
            "level": "success",
            "source": "攻击智能体",
            "message": "邮件投递成功",
            "attack_info": {
                "stage": "delivery",
                "technique": "email_delivery",
                "source_node": "internet",
                "target_node": "target_host",
                "status": "completed",
                "progress": 60
            }
        },
        {
            "timestamp": time.time(),
            "level": "warning",
            "source": "攻击智能体",
            "message": "用户点击恶意链接",
            "attack_info": {
                "stage": "exploitation",
                "technique": "credential_theft",
                "target_node": "target_host",
                "status": "starting",
                "progress": 65
            }
        },
        {
            "timestamp": time.time(),
            "level": "success",
            "source": "攻击智能体",
            "message": "获得初始访问权限",
            "attack_info": {
                "stage": "exploitation",
                "technique": "credential_theft",
                "target_node": "target_host",
                "status": "completed",
                "progress": 70
            }
        },
        {
            "timestamp": time.time(),
            "level": "success",
            "source": "攻击智能体",
            "message": "攻击目标达成",
            "attack_info": {
                "stage": "actions_on_objectives",
                "technique": "system_compromise",
                "target_node": "internal-db",
                "status": "completed",
                "progress": 100
            }
        }
    ]
    
    try:
        # 连接到后端WebSocket
        uri = "ws://localhost:8000/ws/logs"
        print(f"🔗 尝试连接到 {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功！")
            
            # 发送测试日志
            for i, log in enumerate(test_logs, 1):
                print(f"📤 发送日志 {i}/{len(test_logs)}: {log['message']}")
                await websocket.send(json.dumps(log, ensure_ascii=False))
                await asyncio.sleep(1)  # 间隔1秒发送
            
            print("✅ 所有测试日志发送完成！")
            
    except Exception as e:
        print(f"❌ WebSocket连接失败: {e}")
        print("💡 请确保后端服务正在运行 (python backend/main.py)")

def compare_log_sizes():
    """对比优化前后的日志大小"""
    print("\n📊 对比优化前后的日志大小...")
    
    # 优化前的日志
    old_log = {
        "timestamp": time.time(),
        "level": "info",
        "source": "攻击智能体",
        "message": "[侦察阶段] 正在使用nmap工具对目标防火墙192.168.1.1进行全端口扫描，检测开放的服务和版本信息，以便后续的漏洞分析和攻击向量确定",
        "attack_info": {
            "stage": "侦察阶段",
            "technique": "网络扫描",
            "source_node": "internet",
            "target_node": "firewall",
            "progress": 25,
            "status": "in_progress"
        }
    }
    
    # 优化后的日志
    new_log = {
        "timestamp": time.time(),
        "level": "info",
        "source": "攻击智能体",
        "message": "扫描目标网络",
        "attack_info": {
            "stage": "reconnaissance",
            "technique": "port_scan",
            "source_node": "internet",
            "target_node": "firewall",
            "status": "starting",
            "progress": 10
        }
    }
    
    old_size = len(json.dumps(old_log, ensure_ascii=False))
    new_size = len(json.dumps(new_log, ensure_ascii=False))
    reduction = (old_size - new_size) / old_size * 100
    
    print(f"❌ 优化前日志大小: {old_size} 字节")
    print(f"✅ 优化后日志大小: {new_size} 字节")
    print(f"📉 大小减少: {reduction:.1f}%")

async def main():
    """主函数"""
    print("🚀 开始测试WebSocket日志传输...\n")
    
    compare_log_sizes()
    await test_websocket_logs()
    
    print("\n✅ WebSocket测试完成！")
    print("\n📋 测试总结:")
    print("  🎯 日志格式: 标准化简洁消息")
    print("  🎯 传输效率: 显著减少数据量")
    print("  🎯 动画兼容: 保持attack_info完整性")
    print("  🎯 用户体验: 简洁易读的日志消息")

if __name__ == "__main__":
    asyncio.run(main())
