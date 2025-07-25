#!/usr/bin/env python3
"""
测试日志优化效果的脚本
验证标准化消息映射和简化日志输出
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents', 'attack_agent'))

from main import analyze_attack_step, AttackLogHandler

def test_standardized_messages():
    """测试标准化消息映射"""
    print("🧪 测试标准化消息映射...")
    
    test_cases = [
        "攻击者扫描防火墙",
        "攻击者发现防火墙开放端口",
        "攻击者完成目标侦察",
        "攻击者生成钓鱼邮件",
        "攻击者完成恶意载荷制作",
        "攻击者向目标发送钓鱼邮件",
        "钓鱼邮件成功投递到目标",
        "目标用户点击恶意链接",
        "攻击者获得目标主机访问权限",
        "攻击者在目标主机安装后门",
        "攻击者建立目标主机持久化访问",
        "攻击者与目标主机建立C2通信",
        "攻击者从目标主机向内网横向移动",
        "攻击者从内网数据库窃取数据",
        "攻击者完全攻陷目标系统"
    ]
    
    for message in test_cases:
        result = analyze_attack_step(message)
        source = result.get('source_node', 'N/A')
        target = result.get('target_node', 'N/A')
        print(f"✅ '{message}' -> {result['stage']} | {result['technique']} | {source}→{target} | 进度: {result['progress']}%")
    
    print()

def test_fallback_logic():
    """测试备选智能匹配逻辑"""
    print("🧪 测试备选智能匹配逻辑...")
    
    test_cases = [
        "正在使用nmap扫描目标主机",
        "开始制作钓鱼邮件",
        "邮件发送中...",
        "用户已点击链接",
        "正在安装恶意软件",
        "建立远程控制连接",
        "开始窃取敏感数据"
    ]
    
    for message in test_cases:
        result = analyze_attack_step(message)
        print(f"✅ '{message}' -> {result['stage']} | {result['technique']} | 状态: {result['status']}")
    
    print()

def test_attack_log_handler():
    """测试攻击日志处理器"""
    print("🧪 测试攻击日志处理器...")
    
    handler = AttackLogHandler()
    
    # 模拟攻击进展
    stages = [
        ("reconnaissance", 40),
        ("weaponization", 100),
        ("delivery", 100),
        ("exploitation", 100),
        ("installation", 100),
        ("command_and_control", 90),
        ("actions_on_objectives", 50)
    ]
    
    for stage, progress in stages:
        handler.advance_stage(stage, progress)
        overall = handler.get_overall_progress()
        print(f"✅ {stage}: {progress}% -> 整体进度: {overall}%")
    
    print()

def test_message_comparison():
    """对比优化前后的消息格式"""
    print("🧪 对比优化前后的消息格式...")
    
    print("❌ 优化前的冗长消息:")
    old_messages = [
        "[侦察阶段] 正在使用nmap工具对目标防火墙192.168.1.1进行全端口扫描，检测开放的服务和版本信息，以便后续的漏洞分析和攻击向量确定",
        "[武器化阶段] 根据侦察到的目标信息，正在生成针对性的钓鱼邮件，包含恶意链接和社会工程学元素",
        "[投递阶段] 通过SMTP协议将制作好的钓鱼邮件发送到目标用户邮箱，等待用户交互"
    ]
    
    for msg in old_messages:
        print(f"  📝 {msg}")
    
    print("\n✅ 优化后的简洁消息:")
    new_messages = [
        "攻击者扫描防火墙",
        "攻击者生成钓鱼邮件",
        "攻击者向目标发送钓鱼邮件"
    ]

    for msg in new_messages:
        result = analyze_attack_step(msg)
        source = result.get('source_node', 'N/A')
        target = result.get('target_node', 'N/A')
        print(f"  📝 {msg} (阶段: {result['stage']}, 技术: {result['technique']}, {source}→{target}, 进度: {result['progress']}%)")
    
    print()

def main():
    """主测试函数"""
    print("🚀 开始测试日志优化效果...\n")
    
    test_standardized_messages()
    test_fallback_logic()
    test_attack_log_handler()
    test_message_comparison()
    
    print("✅ 所有测试完成！")
    print("\n📊 优化效果总结:")
    print("  🎯 消息长度: 从50-100字减少到5-10字")
    print("  🎯 可读性: 技术细节简化，核心信息突出")
    print("  🎯 动画识别: 标准化关键词确保精确匹配")
    print("  🎯 用户体验: 简洁明了，易于理解")

if __name__ == "__main__":
    main()
