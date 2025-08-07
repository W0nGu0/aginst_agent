#!/usr/bin/env python3
"""
防御协调器启动脚本
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def start_coordinator():
    """启动防御协调器"""
    script_path = Path(__file__).parent / "defense_coordinator.py"
    
    print("🛡️ 启动防御协调器...")
    print("=" * 50)
    
    try:
        # 设置环境变量
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent)
        
        # 启动防御协调器
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print(f"✅ 防御协调器已启动 (PID: {process.pid})")
        print("\n📋 功能说明:")
        print("  • 监听WebSocket日志流")
        print("  • 自动识别攻击活动")
        print("  • 触发相应防御智能体响应")
        print("  • 协调多个防御智能体协作")
        print("\n🔍 监控模式:")
        print("  • 威胁阻断: 检测到扫描、恶意IP、C2通信时触发")
        print("  • 漏洞修复: 检测到漏洞利用、系统被攻陷时触发")
        print("  • 攻击溯源: 检测到攻击完成、数据窃取时触发")
        print("\n按 Ctrl+C 停止防御协调器")
        
        # 实时显示输出
        try:
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
        except KeyboardInterrupt:
            print("\n🛑 正在停止防御协调器...")
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✅ 防御协调器已停止")
            except subprocess.TimeoutExpired:
                print("⚠️ 强制终止防御协调器")
                process.kill()
        
        return process.returncode or 0
        
    except Exception as e:
        print(f"❌ 启动防御协调器失败: {e}")
        return 1

def main():
    """主函数"""
    return start_coordinator()

if __name__ == "__main__":
    sys.exit(main())