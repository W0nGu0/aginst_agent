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
    print("🔧 启动AI Agent攻防推演平台所有服务...")
    print("=" * 60)

    processes = []

    # === 第一阶段：启动MCP微服务层 ===
    print("\n🔧 第一阶段：启动MCP微服务层")

    # 1. 启动场景服务 (端口 8002)
    scenario_service_process = start_service(
        "场景服务 (Scenario Service)",
        [sys.executable, "main.py"],
        cwd="services/scenario_service",
        port=8002
    )
    if scenario_service_process:
        processes.append(("场景服务", scenario_service_process))

    # 2. 启动攻击服务 (端口 8001)
    attack_service_process = start_service(
        "攻击服务 (Attack Service)",
        [sys.executable, "main.py"],
        cwd="services/attack_service",
        port=8001
    )
    if attack_service_process:
        processes.append(("攻击服务", attack_service_process))

    # 3. 启动评估服务 (端口 8005)
    evaluate_service_process = start_service(
        "评估服务 (Evaluate Service)",
        [sys.executable, "main.py"],
        cwd="services/evaluate_service",
        port=8005
    )
    if evaluate_service_process:
        processes.append(("评估服务", evaluate_service_process))

    # 4. 启动防御服务群组 (端口 8008-8010)
    defense_services_process = start_service(
        "防御服务群组 (Defense Services)",
        [sys.executable, "start_defense_services.py"],
        cwd="services/defense_service"
    )
    if defense_services_process:
        processes.append(("防御服务群组", defense_services_process))

    # === 第二阶段：启动AI智能代理层 ===
    print("\n🤖 第二阶段：启动AI智能代理层")

    # 5. 启动场景智能体 (端口 8007)
    scenario_agent_process = start_service(
        "场景智能体 (Scenario Agent)",
        [sys.executable, "main.py"],
        cwd="agents/scenario_agent",
        port=8007
    )
    if scenario_agent_process:
        processes.append(("场景智能体", scenario_agent_process))

    # 6. 启动攻击智能体 (端口 8004)
    attack_agent_process = start_service(
        "攻击智能体 (Attack Agent)",
        [sys.executable, "main.py"],
        cwd="agents/attack_agent",
        port=8004
    )
    if attack_agent_process:
        processes.append(("攻击智能体", attack_agent_process))

    # 7. 启动评估智能体 (端口 8014)
    evaluate_agent_process = start_service(
        "评估智能体 (Evaluate Agent)",
        [sys.executable, "main.py"],
        cwd="agents/evaluate_agent",
        port=8014
    )
    if evaluate_agent_process:
        processes.append(("评估智能体", evaluate_agent_process))

    # 8. 启动防御智能体群组 (端口 8011-8013)
    defense_agents_process = start_service(
        "防御智能体群组 (Defense Agents)",
        [sys.executable, "start_defense_agents.py"],
        cwd="agents/defense_agent"
    )
    if defense_agents_process:
        processes.append(("防御智能体群组", defense_agents_process))

    # 9. 启动受害主机智能体 (端口 8015)
    victim_agent_process = start_service(
        "受害主机智能体 (Victim Host Agent)",
        [sys.executable, "main.py"],
        cwd="agents/victim_host_agent",
        port=8015
    )
    if victim_agent_process:
        processes.append(("受害主机智能体", victim_agent_process))

    # === 第三阶段：启动控制和界面层 ===
    print("\n🎮 第三阶段：启动控制和界面层")

    # 10. 启动中央控制智能体 (端口 8006)
    central_agent_process = start_service(
        "中央控制智能体 (Central Agent)",
        [sys.executable, "main.py"],
        cwd="agents/central_agent",
        port=8006
    )
    if central_agent_process:
        processes.append(("中央控制智能体", central_agent_process))

    # 11. 启动后端API (端口 8080)
    backend_process = start_service(
        "后端API (Backend)",
        [sys.executable, "main.py"],
        cwd="backend",
        port=8080
    )
    if backend_process:
        processes.append(("后端API", backend_process))

    if not processes:
        print("❌ 没有服务成功启动")
        sys.exit(1)

    print(f"\n✅ 成功启动 {len(processes)} 个服务")
    print("\n🌐 服务访问地址:")
    print("=" * 60)
    print("📱 前端界面:")
    print("  - 主界面: http://localhost:5173 (需要单独启动: npm run dev)")
    print("\n🔗 后端服务:")
    print("  - API网关: http://localhost:8080")
    print("  - API文档: http://localhost:8080/docs")
    print("\n🤖 AI智能代理:")
    print("  - 场景智能体: http://localhost:8007")
    print("  - 攻击智能体: http://localhost:8004")
    print("  - 中央控制智能体: http://localhost:8006")
    print("  - 评估智能体: http://localhost:8014")
    print("  - 受害主机智能体: http://localhost:8015")
    print("  - 防御智能体群组: http://localhost:8011-8013")
    print("\n🔧 MCP微服务:")
    print("  - 场景服务: http://localhost:8002/mcp/")
    print("  - 攻击服务: http://localhost:8001/mcp/")
    print("  - 评估服务: http://localhost:8005/mcp/")
    print("  - 防御服务群组: http://localhost:8008-8010/mcp/")

    print("\n🧪 验证命令:")
    print("  python test_battle_system.py")
    print("  python test_phase2_frontend.py")
    print("  python test_scenario_agent_health.py")

    print("\n⚠️  重要提示:")
    print("1. 确保在agents/scenario_agent/.env中配置了DEEPSEEK_API_KEY")
    print("2. 确保Docker已安装并运行")
    print("3. 前端需要单独启动: npm run dev")
    print("4. 按Ctrl+C停止所有服务")

    try:
        print("\n⏳ 所有服务运行中... (按Ctrl+C停止)")
        while True:
            time.sleep(1)
            # 检查进程是否还在运行
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️  {name} 已停止")

    except KeyboardInterrupt:
        print("\n🛑 正在停止所有服务...")
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
