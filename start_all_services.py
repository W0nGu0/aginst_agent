#!/usr/bin/env python3
"""
启动所有必要的服务
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_port(port):
    """检查端口是否被占用"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_service(name, command, cwd=None, port=None):
    """启动服务"""
    if port and check_port(port):
        print(f"✅ {name} 已在端口 {port} 运行")
        return None
    
    print(f"🚀 启动 {name}...")
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(3)  # 等待服务启动
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print(f"✅ {name} 启动成功 (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ {name} 启动失败")
            print(f"   stdout: {stdout}")
            print(f"   stderr: {stderr}")
            return None
    except Exception as e:
        print(f"❌ 启动 {name} 时出错: {e}")
        return None

def main():
    """主函数"""
    print("🔧 启动所有必要的服务...")
    print("=" * 50)
    
    processes = []
    
    # 1. 启动场景服务 (端口 8002)
    scenario_service_process = start_service(
        "场景服务 (Scenario Service)",
        [sys.executable, "main.py"],
        cwd="services/scenario_service",
        port=8002
    )
    if scenario_service_process:
        processes.append(("场景服务", scenario_service_process))
    
    # 2. 启动场景智能体 (端口 8007)
    scenario_agent_process = start_service(
        "场景智能体 (Scenario Agent)",
        [sys.executable, "main.py"],
        cwd="agents/scenario_agent",
        port=8007
    )
    if scenario_agent_process:
        processes.append(("场景智能体", scenario_agent_process))
    
    # 3. 启动后端服务 (端口 8080)
    backend_process = start_service(
        "后端服务 (Backend)",
        [sys.executable, "main.py"],
        cwd="backend",
        port=8080
    )
    if backend_process:
        processes.append(("后端服务", backend_process))
    
    if not processes:
        print("❌ 没有服务成功启动")
        sys.exit(1)
    
    print(f"\n✅ 成功启动 {len(processes)} 个服务")
    print("\n📋 服务信息:")
    print("- 场景服务: http://localhost:8002")
    print("- 场景智能体: http://localhost:8007")
    print("- 后端服务: http://localhost:8080")
    
    print("\n🧪 测试命令:")
    print("python test_phase2_frontend.py")
    
    print("\n⚠️  注意事项:")
    print("1. 确保在agents/scenario_agent/.env中配置了DEEPSEEK_API_KEY")
    print("2. 确保Docker已安装并运行")
    print("3. 按Ctrl+C停止所有服务")
    
    try:
        print("\n⏳ 服务运行中... (按Ctrl+C停止)")
        while True:
            time.sleep(1)
            # 检查进程是否还在运行
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️  {name} 已停止")
                    
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} 已停止")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔪 强制停止 {name}")
            except Exception as e:
                print(f"❌ 停止 {name} 时出错: {e}")
        
        print("👋 所有服务已停止")

if __name__ == "__main__":
    main()
