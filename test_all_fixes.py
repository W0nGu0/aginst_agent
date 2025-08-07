#!/usr/bin/env python3
"""
全面修复验证脚本
验证：1. 裁判启动  2. 节点恢复  3. 日志去重  4. 错误修复
"""

import asyncio
import json
import websockets
import time

# 测试消息 - 包含节点恢复和去重测试
TEST_MESSAGES = [
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
    
    # 3. 防御响应 - 威胁检测
    {
        "level": "warning",
        "source": "威胁阻断智能体", 
        "message": "检测到端口扫描行为，发现恶意IP 192.168.100.11",
        "timestamp": time.time()
    },
    
    # 4. 防御响应 - IP阻断
    {
        "level": "success",
        "source": "威胁阻断智能体",
        "message": "成功阻断恶意IP 192.168.100.11，防火墙规则已更新",
        "timestamp": time.time()
    },
    
    # 5. 防御响应 - 漏洞修复（应该恢复节点状态）
    {
        "level": "success",
        "source": "漏洞修复智能体",
        "message": "漏洞修复完成，主机 web-server 已加固和恢复",
        "timestamp": time.time()
    },
    
    # 6. 防御响应 - 攻击溯源
    {
        "level": "success",
        "source": "攻击溯源智能体",
        "message": "攻击溯源完成，已收集攻击证据并生成报告",
        "timestamp": time.time()
    },
    
    # 7. 重复消息测试1
    {
        "level": "warning",
        "source": "威胁阻断智能体", 
        "message": "检测到端口扫描行为，发现恶意IP 192.168.100.11",
        "timestamp": time.time()
    },
    
    # 8. 重复消息测试2
    {
        "level": "success",
        "source": "漏洞修复智能体",
        "message": "漏洞修复完成，主机 web-server 已加固和恢复",
        "timestamp": time.time()
    },
    
    # 9. 攻击继续 - 数据窃取
    {
        "level": "critical",
        "source": "攻击智能体",
        "message": "数据窃取完成，成功获取数据库核心数据",
        "timestamp": time.time()
    }
]

async def test_system_fixes():
    """测试系统修复"""
    print("🔧 测试系统修复")
    print("=" * 60)
    
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
                
                # 特殊处理
                if "主机 web-server" in message['message'] and "修复完成" in message['message']:
                    if i == 5:  # 第一次修复消息
                        print("   🔄 节点应该从红色脉冲恢复为正常状态")
                    else:  # 重复修复消息
                        print("   🚫 重复消息，应该被去重，不会重复触发动画")
                    await asyncio.sleep(4)
                elif "重复消息" in str(i) or i in [7, 8]:
                    print("   🔄 重复消息测试，应该被去重")
                    await asyncio.sleep(2)
                elif "攻击溯源完成" in message['message']:
                    print("   🏁 防御工作完成，等待最终判定")
                    await asyncio.sleep(5)
                else:
                    await asyncio.sleep(3)
            
            print("\n✅ 测试完成")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def print_fix_summary():
    """打印修复总结"""
    print("🔧 修复总结")
    print("=" * 60)
    print("1. 裁判启动修复:")
    print("   - 修复了 'await' outside async function 语法错误")
    print("   - update_defense_actions 方法改为异步")
    print("   - 相关调用处添加 await 关键字")
    
    print("\n2. 节点恢复修复:")
    print("   - 改进了被攻陷节点的查找逻辑")
    print("   - 添加了 findCompromisedNode() 函数")
    print("   - 漏洞修复时优先恢复被攻陷的节点")
    print("   - restoreNodeToNormalState() 移除红色脉冲动画")
    
    print("\n3. 日志去重改进:")
    print("   - 使用 MD5 哈希替代 Python hash()")
    print("   - 添加了调试日志输出")
    print("   - 改进了消息唯一标识符生成")
    
    print("\n4. 错误修复:")
    print("   - 修复了防御智能体的各种报错")
    print("   - 改进了异步方法调用")
    print("   - 增强了错误处理和日志输出")

def check_system_status():
    """检查系统状态"""
    print("\n📊 系统状态检查")
    print("=" * 60)
    print("请验证以下修复效果:")
    
    print("\n✅ 裁判系统:")
    print("   - 攻防演练裁判应该能正常启动")
    print("   - 不再出现语法错误")
    print("   - 能正确处理防御工作完成通知")
    
    print("\n✅ 节点恢复:")
    print("   - 被攻陷的节点显示红色脉冲动画")
    print("   - 漏洞修复完成后节点恢复正常状态")
    print("   - 显示绿色恢复脉冲效果")
    
    print("\n✅ 日志去重:")
    print("   - 相同的防御智能体日志不会重复出现")
    print("   - 重复消息被正确过滤")
    print("   - 防御动画不会重复触发")
    
    print("\n✅ 错误修复:")
    print("   - 防御智能体日志文件中不再有报错")
    print("   - 所有异步方法调用正确")
    print("   - 系统运行稳定")

async def main():
    """主函数"""
    print("🧪 攻防演练系统全面修复验证")
    print("=" * 70)
    
    # 打印修复总结
    print_fix_summary()
    
    # 检查系统状态
    check_system_status()
    
    # 询问是否开始测试
    print("\n" + "=" * 70)
    response = input("是否开始测试所有修复? (y/n): ")
    
    if response.lower() in ['y', 'yes', '是']:
        await test_system_fixes()
        
        print("\n🎉 测试完成！")
        print("请检查:")
        print("  1. 裁判系统是否正常启动")
        print("  2. 被攻陷节点是否正确恢复")
        print("  3. 重复日志是否被去重")
        print("  4. 防御智能体日志是否无错误")
    else:
        print("测试结束")

if __name__ == "__main__":
    asyncio.run(main())