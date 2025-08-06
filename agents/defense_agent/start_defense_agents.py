#!/usr/bin/env python3
"""
防御智能体启动脚本
同时启动三个防御智能体
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

# 智能体配置
AGENTS = [
    {
        "name": "威胁阻断智能体",
        "script": "threat_blocking_agent.py",
        "port": 8011,
        "process": None
    },
    {
        "name": "漏洞修复智能体", 
        "script": "vulnerability_agent.py",
        "port": 8012,
        "process": None
    },
    {
        "name": "攻击溯源智能体",
        "script": "attribution_agent.py", 
        "port": 8013,
        "process": None
    }
]

def start_agent(agent):
    """启动单个智能体"""
    script_path = Path(__file__).parent / agent["script"]
    
    print(f"🚀 启动 {agent['name']} (端口 {agent['port']})...")
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent)
        
        # 创建日志文件
        log_file = Path(__file__).parent / f"{agent['name'].replace(' ', '_')}.log"
        
        with open(log_file, 'w') as log:
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True
            )
        
        agent["process"] = process
        agent["log_file"] = log_file
        
        # 等待一下检查进程是否立即退出
        time.sleep(3)
        if process.poll() is not None:
            # 进程已退出，读取日志
            with open(log_file, 'r', encoding='utf-8') as f:
                error_log = f.read()
            print(f"❌ {agent['name']} 启动失败，错误日志:")
            print(error_log[-1000:])  # 只显示最后1000个字符
            return False
        
        print(f"✅ {agent['name']} 已启动 (PID: {process.pid})")
        print(f"   日志文件: {log_file}")
        return True
        
    except Exception as e:
        print(f"❌ 启动 {agent['name']} 失败: {e}")
        return False

def stop_agents():
    """停止所有智能体"""
    print("\n🛑 正在停止所有防御智能体...")
    
    for agent in AGENTS:
        if agent["process"] and agent["process"].poll() is None:
            print(f"停止 {agent['name']}...")
            agent["process"].terminate()
            
            # 等待进程结束
            try:
                agent["process"].wait(timeout=5)
                print(f"✅ {agent['name']} 已停止")
            except subprocess.TimeoutExpired:
                print(f"⚠️ 强制终止 {agent['name']}")
                agent["process"].kill()

def signal_handler(signum, frame):
    """信号处理器"""
    print(f"\n收到信号 {signum}，正在关闭智能体...")
    stop_agents()
    sys.exit(0)

def check_agents():
    """检查智能体状态"""
    print("\n📊 智能体状态检查:")
    for agent in AGENTS:
        if agent["process"] and agent["process"].poll() is None:
            print(f"✅ {agent['name']}: 运行中 (PID: {agent['process'].pid})")
        else:
            print(f"❌ {agent['name']}: 已停止")

def main():
    """主函数"""
    print("🛡️ 防御智能体管理器")
    print("=" * 50)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动所有智能体
    success_count = 0
    for agent in AGENTS:
        if start_agent(agent):
            success_count += 1
        time.sleep(2)  # 避免端口冲突
    
    if success_count == 0:
        print("❌ 没有智能体成功启动")
        return 1
    
    print(f"\n🎉 成功启动 {success_count}/{len(AGENTS)} 个智能体")
    print("\n智能体端点:")
    for agent in AGENTS:
        if agent["process"] and agent["process"].poll() is None:
            print(f"  • {agent['name']}: http://localhost:{agent['port']}")
    
    print("\n📋 智能体功能:")
    print("  • 威胁阻断智能体: 实时检测和阻断网络威胁")
    print("  • 漏洞修复智能体: 扫描漏洞并应用安全补丁")
    print("  • 攻击溯源智能体: 分析攻击路径和威胁归因")
    
    print("\n按 Ctrl+C 停止所有智能体")
    
    try:
        # 主循环 - 监控智能体状态
        while True:
            time.sleep(30)  # 每30秒检查一次
            
            # 检查是否有智能体意外停止
            for agent in AGENTS:
                if agent["process"] and agent["process"].poll() is not None:
                    print(f"⚠️ {agent['name']} 意外停止，尝试重启...")
                    start_agent(agent)
                    
    except KeyboardInterrupt:
        pass
    finally:
        stop_agents()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())