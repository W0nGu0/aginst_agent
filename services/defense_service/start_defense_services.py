#!/usr/bin/env python3
"""
防御服务启动脚本
同时启动三个防御相关的MCP服务
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

# 服务配置
SERVICES = [
    {
        "name": "威胁阻断服务",
        "script": "threat_blocking_service.py",
        "port": 8008,
        "process": None
    },
    {
        "name": "漏洞修复服务", 
        "script": "vulnerability_service.py",
        "port": 8009,
        "process": None
    },
    {
        "name": "攻击溯源服务",
        "script": "attribution_service.py", 
        "port": 8010,
        "process": None
    }
]

def start_service(service):
    """启动单个服务"""
    script_path = Path(__file__).parent / service["script"]
    
    print(f"🚀 启动 {service['name']} (端口 {service['port']})...")
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent)
        
        # 创建日志文件
        log_file = Path(__file__).parent / f"{service['name']}.log"
        
        with open(log_file, 'w') as log:
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True
            )
        
        service["process"] = process
        service["log_file"] = log_file
        
        # 等待一下检查进程是否立即退出
        time.sleep(2)
        if process.poll() is not None:
            # 进程已退出，读取日志
            with open(log_file, 'r') as f:
                error_log = f.read()
            print(f"❌ {service['name']} 启动失败，错误日志:")
            print(error_log)
            return False
        
        print(f"✅ {service['name']} 已启动 (PID: {process.pid})")
        return True
        
    except Exception as e:
        print(f"❌ 启动 {service['name']} 失败: {e}")
        return False

def stop_services():
    """停止所有服务"""
    print("\n🛑 正在停止所有防御服务...")
    
    for service in SERVICES:
        if service["process"] and service["process"].poll() is None:
            print(f"停止 {service['name']}...")
            service["process"].terminate()
            
            # 等待进程结束
            try:
                service["process"].wait(timeout=5)
                print(f"✅ {service['name']} 已停止")
            except subprocess.TimeoutExpired:
                print(f"⚠️ 强制终止 {service['name']}")
                service["process"].kill()

def signal_handler(signum, frame):
    """信号处理器"""
    print(f"\n收到信号 {signum}，正在关闭服务...")
    stop_services()
    sys.exit(0)

def check_services():
    """检查服务状态"""
    print("\n📊 服务状态检查:")
    for service in SERVICES:
        if service["process"] and service["process"].poll() is None:
            print(f"✅ {service['name']}: 运行中 (PID: {service['process'].pid})")
        else:
            print(f"❌ {service['name']}: 已停止")

def main():
    """主函数"""
    print("🛡️ 防御Agent MCP服务管理器")
    print("=" * 50)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动所有服务
    success_count = 0
    for service in SERVICES:
        if start_service(service):
            success_count += 1
        time.sleep(1)  # 避免端口冲突
    
    if success_count == 0:
        print("❌ 没有服务成功启动")
        return 1
    
    print(f"\n🎉 成功启动 {success_count}/{len(SERVICES)} 个服务")
    print("\n服务端点:")
    for service in SERVICES:
        if service["process"] and service["process"].poll() is None:
            print(f"  • {service['name']}: http://localhost:{service['port']}/mcp/")
    
    print("\n按 Ctrl+C 停止所有服务")
    
    try:
        # 主循环 - 监控服务状态
        while True:
            time.sleep(30)  # 每30秒检查一次
            
            # 检查是否有服务意外停止
            for service in SERVICES:
                if service["process"] and service["process"].poll() is not None:
                    print(f"⚠️ {service['name']} 意外停止，尝试重启...")
                    start_service(service)
                    
    except KeyboardInterrupt:
        pass
    finally:
        stop_services()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())