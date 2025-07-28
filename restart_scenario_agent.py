#!/usr/bin/env python3
"""
重启场景智能体
"""

import subprocess
import time
import os
import signal
import psutil

def kill_process_on_port(port):
    """杀死占用指定端口的进程"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.info['connections']:
                    if conn.laddr.port == port:
                        print(f"🔪 杀死进程 {proc.info['pid']} ({proc.info['name']}) 占用端口 {port}")
                        proc.kill()
                        time.sleep(2)
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        print(f"❌ 杀死进程失败: {e}")
    return False

def start_scenario_agent():
    """启动场景智能体"""
    print("🚀 启动场景智能体...")
    
    # 切换到场景智能体目录
    agent_dir = os.path.join(os.getcwd(), "agents", "scenario_agent")
    
    # 启动场景智能体
    process = subprocess.Popen(
        ["python", "main.py"],
        cwd=agent_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    print(f"✅ 场景智能体已启动 (PID: {process.pid})")
    
    # 实时显示输出
    try:
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"[场景智能体] {output.strip()}")
    except KeyboardInterrupt:
        print("\n🛑 用户中断，停止场景智能体...")
        process.terminate()
        process.wait()

def main():
    """主函数"""
    print("🔧 重启场景智能体服务")
    print("=" * 50)
    
    # 1. 杀死占用8007端口的进程
    print("🔍 检查端口8007...")
    if kill_process_on_port(8007):
        print("✅ 已清理端口8007")
        time.sleep(3)
    else:
        print("ℹ️  端口8007未被占用")
    
    # 2. 启动场景智能体
    try:
        start_scenario_agent()
    except Exception as e:
        print(f"❌ 启动场景智能体失败: {e}")

if __name__ == "__main__":
    main()
