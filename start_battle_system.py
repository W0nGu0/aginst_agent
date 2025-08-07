#!/usr/bin/env python3
"""
攻防演练系统一键启动脚本
自动启动所有必要的服务组件
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path
import threading
import queue

class BattleSystemManager:
    def __init__(self):
        self.processes = []
        self.process_info = []
        
    def start_service(self, name, command, cwd=None, wait_time=3):
        """启动单个服务"""
        print(f"🚀 启动 {name}...")
        
        try:
            # 设置环境变量
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path(__file__).parent)
            
            # 启动进程
            process = subprocess.Popen(
                command,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes.append(process)
            self.process_info.append({
                "name": name,
                "process": process,
                "command": " ".join(command),
                "cwd": cwd
            })
            
            # 等待服务启动
            time.sleep(wait_time)
            
            # 检查进程是否还在运行
            if process.poll() is None:
                print(f"✅ {name} 启动成功 (PID: {process.pid})")
                return True
            else:
                print(f"❌ {name} 启动失败")
                # 读取错误输出
                try:
                    output, _ = process.communicate(timeout=1)
                    if output:
                        print(f"   错误信息: {output[-500:]}")  # 显示最后500个字符
                except:
                    pass
                return False
                
        except Exception as e:
            print(f"❌ 启动 {name} 时出错: {e}")
            return False
    
    def start_all_services(self):
        """启动所有服务"""
        print("🎯 攻防演练系统启动器")
        print("=" * 50)
        
        services = [
            {
                "name": "后端服务",
                "command": [sys.executable, "main.py"],
                "cwd": Path(__file__).parent / "backend",
                "wait_time": 5
            },
            {
                "name": "防御智能体组",
                "command": [sys.executable, "start_defense_agents.py"],
                "cwd": Path(__file__).parent / "agents" / "defense_agent",
                "wait_time": 8
            },
            {
                "name": "攻击智能体",
                "command": [sys.executable, "main.py"],
                "cwd": Path(__file__).parent / "agents" / "attack_agent",
                "wait_time": 3
            },
            {
                "name": "中央智能体",
                "command": [sys.executable, "main.py"],
                "cwd": Path(__file__).parent / "agents" / "central_agent",
                "wait_time": 3
            }
        ]
        
        success_count = 0
        for service in services:
            if self.start_service(**service):
                success_count += 1
            time.sleep(2)  # 服务间启动间隔
        
        print("\n" + "=" * 50)
        print(f"🎉 成功启动 {success_count}/{len(services)} 个服务")
        
        if success_count > 0:
            self.show_system_status()
            self.monitor_services()
        else:
            print("❌ 没有服务成功启动")
            return False
        
        return True
    
    def show_system_status(self):
        """显示系统状态"""
        print("\n📊 系统状态:")
        for info in self.process_info:
            if info["process"].poll() is None:
                print(f"  ✅ {info['name']}: 运行中 (PID: {info['process'].pid})")
            else:
                print(f"  ❌ {info['name']}: 已停止")
        
        print("\n🌐 服务端点:")
        print("  • 后端API: http://localhost:8080")
        print("  • WebSocket: ws://localhost:8080/ws/logs")
        print("  • 威胁阻断智能体: http://localhost:8011")
        print("  • 漏洞修复智能体: http://localhost:8012")
        print("  • 攻击溯源智能体: http://localhost:8013")
        
        print("\n📋 使用说明:")
        print("  1. 打开前端界面 (通常是 http://localhost:3000 或 http://localhost:5173)")
        print("  2. 进入 '对抗演练' -> '拓扑图' 页面")
        print("  3. 生成或加载攻防场景")
        print("  4. 启动攻击智能体开始演练")
        print("  5. 观察实时的攻防对抗和可视化效果")
        
        print("\n🧪 测试工具:")
        print("  • 运行测试脚本: python test_battle_system.py")
        print("  • 查看日志: 各服务的控制台输出")
        
        print("\n⚠️ 停止系统: 按 Ctrl+C")
    
    def monitor_services(self):
        """监控服务状态"""
        print("\n🔍 开始监控服务状态...")
        print("按 Ctrl+C 停止所有服务")
        
        try:
            while True:
                time.sleep(30)  # 每30秒检查一次
                
                # 检查服务状态
                for info in self.process_info:
                    if info["process"].poll() is not None:
                        print(f"⚠️ {info['name']} 意外停止，尝试重启...")
                        # 这里可以添加自动重启逻辑
                        
        except KeyboardInterrupt:
            print("\n🛑 收到停止信号，正在关闭所有服务...")
            self.stop_all_services()
    
    def stop_all_services(self):
        """停止所有服务"""
        print("正在停止所有服务...")
        
        for info in self.process_info:
            if info["process"].poll() is None:
                print(f"停止 {info['name']}...")
                try:
                    info["process"].terminate()
                    info["process"].wait(timeout=5)
                    print(f"✅ {info['name']} 已停止")
                except subprocess.TimeoutExpired:
                    print(f"⚠️ 强制终止 {info['name']}")
                    info["process"].kill()
                except Exception as e:
                    print(f"❌ 停止 {info['name']} 时出错: {e}")
        
        print("✅ 所有服务已停止")
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n收到信号 {signum}")
        self.stop_all_services()
        sys.exit(0)

def check_dependencies():
    """检查依赖项"""
    print("🔍 检查系统依赖...")
    
    required_dirs = [
        "backend",
        "agents/defense_agent", 
        "agents/attack_agent",
        "agents/central_agent"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("❌ 缺少必要的目录:")
        for dir_path in missing_dirs:
            print(f"   - {dir_path}")
        return False
    
    print("✅ 目录结构检查通过")
    return True

def main():
    """主函数"""
    # 检查依赖
    if not check_dependencies():
        print("请确保在正确的项目根目录下运行此脚本")
        return 1
    
    # 创建系统管理器
    manager = BattleSystemManager()
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, manager.signal_handler)
    signal.signal(signal.SIGTERM, manager.signal_handler)
    
    # 启动所有服务
    success = manager.start_all_services()
    
    if not success:
        print("系统启动失败")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())