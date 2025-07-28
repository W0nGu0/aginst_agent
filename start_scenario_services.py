#!/usr/bin/env python3
"""
启动场景相关服务的脚本
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_python_packages():
    """检查必要的Python包"""
    required_packages = [
        "fastapi", "uvicorn", "httpx", "pydantic", 
        "websockets", "python-dotenv", "langchain-deepseek",
        "fastmcp", "pyyaml"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少以下Python包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有必要的Python包已安装")
    return True

def check_files():
    """检查必要的文件"""
    required_files = [
        "agents/scenario_agent/main.py",
        "services/scenario_service/main.py",
        "docker/compose-templates/generated/apt-ready.yml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 缺少以下文件: {', '.join(missing_files)}")
        return False
    
    print("✅ 所有必要的文件已存在")
    return True

def start_service(name, command, cwd=None):
    """启动服务"""
    print(f"🚀 启动 {name}...")
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(2)  # 等待服务启动
        
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
    print("🔧 场景智能体服务启动器")
    print("=" * 40)
    
    # 检查环境
    if not check_python_packages():
        sys.exit(1)
    
    if not check_files():
        sys.exit(1)
    
    print("\n🚀 开始启动服务...")
    
    processes = []
    
    # 启动场景服务
    scenario_service_process = start_service(
        "场景服务 (Scenario Service)",
        [sys.executable, "main.py"],
        cwd="services/scenario_service"
    )
    if scenario_service_process:
        processes.append(("场景服务", scenario_service_process))
    
    # 启动场景智能体
    scenario_agent_process = start_service(
        "场景智能体 (Scenario Agent)",
        [sys.executable, "main.py"],
        cwd="agents/scenario_agent"
    )
    if scenario_agent_process:
        processes.append(("场景智能体", scenario_agent_process))
    
    if not processes:
        print("❌ 没有服务成功启动")
        sys.exit(1)
    
    print(f"\n✅ 成功启动 {len(processes)} 个服务")
    print("\n📋 服务信息:")
    print("- 场景服务: http://localhost:8002")
    print("- 场景智能体: http://localhost:8007")
    
    print("\n🧪 运行测试:")
    print("python test_scenario_agent.py")
    
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
