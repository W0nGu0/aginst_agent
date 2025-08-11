#!/usr/bin/env python3
"""
部署验证脚本 - 验证所有服务是否正常运行
"""

import requests
import time
import sys
from typing import Dict, List, Tuple

class Colors:
    """终端颜色定义"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(text, color=Colors.WHITE):
    """打印彩色文本"""
    print(f"{color}{text}{Colors.END}")

def print_header(text):
    """打印标题"""
    print_colored("=" * 60, Colors.CYAN)
    print_colored(f"  {text}", Colors.BOLD + Colors.CYAN)
    print_colored("=" * 60, Colors.CYAN)

def check_service(name: str, url: str, timeout: int = 5) -> Tuple[bool, str]:
    """检查单个服务状态"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return True, f"HTTP {response.status_code}"
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "连接被拒绝"
    except requests.exceptions.Timeout:
        return False, "连接超时"
    except Exception as e:
        return False, f"错误: {str(e)}"

def verify_all_services():
    """验证所有服务"""
    print_header("AI Agent攻防推演平台 - 部署验证")
    
    # 定义所有服务
    services = {
        "前端和后端服务": [
            ("前端开发服务器", "http://localhost:5173"),
            ("后端API网关", "http://localhost:8080/health"),
            ("后端API文档", "http://localhost:8080/docs"),
        ],
        
        "AI智能代理": [
            ("场景智能体", "http://localhost:8007/health"),
            ("攻击智能体", "http://localhost:8004/health"),
            ("中央控制智能体", "http://localhost:8006/health"),
            ("评估智能体", "http://localhost:8014/health"),
            ("受害主机智能体", "http://localhost:8015/health"),
        ],
        
        "防御智能体群组": [
            ("威胁阻断智能体", "http://localhost:8011/health"),
            ("漏洞修复智能体", "http://localhost:8012/health"),
            ("攻击溯源智能体", "http://localhost:8013/health"),
        ],
        
        "MCP微服务": [
            ("场景服务", "http://localhost:8002/mcp/"),
            ("攻击服务", "http://localhost:8001/mcp/"),
            ("评估服务", "http://localhost:8005/mcp/"),
            ("威胁阻断服务", "http://localhost:8008/mcp/"),
            ("漏洞修复服务", "http://localhost:8009/mcp/"),
            ("攻击溯源服务", "http://localhost:8010/mcp/"),
        ]
    }
    
    total_services = 0
    healthy_services = 0
    failed_services = []
    
    for category, service_list in services.items():
        print_colored(f"\n🔍 检查 {category}:", Colors.BLUE + Colors.BOLD)
        
        for service_name, service_url in service_list:
            total_services += 1
            print(f"  检查 {service_name}...", end=" ")
            
            is_healthy, status = check_service(service_name, service_url)
            
            if is_healthy:
                print_colored(f"✅ 正常 ({status})", Colors.GREEN)
                healthy_services += 1
            else:
                print_colored(f"❌ 异常 ({status})", Colors.RED)
                failed_services.append((service_name, service_url, status))
    
    # 显示总结
    print_colored(f"\n📊 验证结果总结:", Colors.BOLD + Colors.CYAN)
    print_colored(f"  总服务数: {total_services}", Colors.WHITE)
    print_colored(f"  正常服务: {healthy_services}", Colors.GREEN)
    print_colored(f"  异常服务: {len(failed_services)}", Colors.RED if failed_services else Colors.GREEN)
    
    if failed_services:
        print_colored(f"\n❌ 以下服务存在问题:", Colors.RED + Colors.BOLD)
        for service_name, service_url, status in failed_services:
            print_colored(f"  • {service_name}: {status}", Colors.RED)
            print_colored(f"    URL: {service_url}", Colors.YELLOW)
        
        print_colored(f"\n🔧 故障排除建议:", Colors.YELLOW + Colors.BOLD)
        print_colored("1. 检查服务是否已启动: python start_all_services.py", Colors.YELLOW)
        print_colored("2. 检查端口是否被占用: netstat -tulpn | grep :端口号", Colors.YELLOW)
        print_colored("3. 查看服务日志文件", Colors.YELLOW)
        print_colored("4. 确认环境配置正确", Colors.YELLOW)
        
        return False
    else:
        print_colored(f"\n🎉 所有服务运行正常!", Colors.GREEN + Colors.BOLD)
        return True

def test_core_functionality():
    """测试核心功能"""
    print_header("核心功能测试")
    
    tests = [
        ("场景生成功能", test_scenario_generation),
        ("攻击模拟功能", test_attack_simulation),
        ("防御响应功能", test_defense_response),
        ("评估分析功能", test_evaluation_analysis),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 测试 {test_name}...", end=" ")
        try:
            if test_func():
                print_colored("✅ 通过", Colors.GREEN)
                passed_tests += 1
            else:
                print_colored("❌ 失败", Colors.RED)
        except Exception as e:
            print_colored(f"❌ 错误: {str(e)}", Colors.RED)
    
    print_colored(f"\n📊 功能测试结果:", Colors.BOLD + Colors.CYAN)
    print_colored(f"  通过测试: {passed_tests}/{total_tests}", Colors.GREEN if passed_tests == total_tests else Colors.YELLOW)
    
    return passed_tests == total_tests

def test_scenario_generation():
    """测试场景生成功能"""
    try:
        response = requests.post(
            "http://localhost:8007/generate_scenario",
            json={
                "industry": "healthcare",
                "attack_type": "apt",
                "complexity": "medium"
            },
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

def test_attack_simulation():
    """测试攻击模拟功能"""
    try:
        response = requests.post(
            "http://localhost:8004/execute_attack",
            json={
                "target": "web-server",
                "attack_type": "phishing"
            },
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

def test_defense_response():
    """测试防御响应功能"""
    try:
        response = requests.post(
            "http://localhost:8011/execute_threat_blocking",
            json={
                "threat_indicators": ["suspicious_ip"],
                "auto_response": True
            },
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

def test_evaluation_analysis():
    """测试评估分析功能"""
    try:
        response = requests.post(
            "http://localhost:8014/create_evaluation",
            json={
                "exercise_id": "test-001",
                "participants": ["user1", "user2"],
                "evaluation_type": "quick"
            },
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

def check_environment():
    """检查环境配置"""
    print_header("环境配置检查")
    
    checks = [
        ("DeepSeek API配置", check_deepseek_config),
        ("Docker服务状态", check_docker_status),
        ("Python依赖", check_python_dependencies),
        ("Node.js依赖", check_nodejs_dependencies),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"🔍 检查 {check_name}...", end=" ")
        try:
            if check_func():
                print_colored("✅ 正常", Colors.GREEN)
            else:
                print_colored("❌ 异常", Colors.RED)
                all_passed = False
        except Exception as e:
            print_colored(f"❌ 错误: {str(e)}", Colors.RED)
            all_passed = False
    
    return all_passed

def check_deepseek_config():
    """检查DeepSeek API配置"""
    import os
    from pathlib import Path
    
    env_file = Path("../agents/scenario_agent/.env")
    if not env_file.exists():
        return False
    
    content = env_file.read_text()
    return "DEEPSEEK_API_KEY" in content and "sk-" in content

def check_docker_status():
    """检查Docker状态"""
    import subprocess
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def check_python_dependencies():
    """检查Python依赖"""
    try:
        import fastapi
        import uvicorn
        import langchain
        import fastmcp
        return True
    except ImportError:
        return False

def check_nodejs_dependencies():
    """检查Node.js依赖"""
    from pathlib import Path
    return Path("../node_modules").exists()

def main():
    """主函数"""
    print_colored("🚀 开始部署验证...\n", Colors.BOLD + Colors.CYAN)
    
    # 1. 检查环境配置
    env_ok = check_environment()
    
    # 2. 验证服务状态
    services_ok = verify_all_services()
    
    # 3. 测试核心功能
    if services_ok:
        print_colored("\n⏳ 等待服务完全启动...", Colors.YELLOW)
        time.sleep(5)
        functionality_ok = test_core_functionality()
    else:
        functionality_ok = False
    
    # 4. 生成最终报告
    print_header("最终验证报告")
    
    if env_ok and services_ok and functionality_ok:
        print_colored("🎉 部署验证完全通过!", Colors.GREEN + Colors.BOLD)
        print_colored("✅ 环境配置正确", Colors.GREEN)
        print_colored("✅ 所有服务运行正常", Colors.GREEN)
        print_colored("✅ 核心功能测试通过", Colors.GREEN)
        print_colored("\n🌐 您现在可以访问:", Colors.CYAN)
        print_colored("  前端界面: http://localhost:5173", Colors.CYAN)
        print_colored("  后端API: http://localhost:8080/docs", Colors.CYAN)
        return True
    else:
        print_colored("❌ 部署验证失败!", Colors.RED + Colors.BOLD)
        if not env_ok:
            print_colored("❌ 环境配置存在问题", Colors.RED)
        if not services_ok:
            print_colored("❌ 部分服务未正常运行", Colors.RED)
        if not functionality_ok:
            print_colored("❌ 功能测试未通过", Colors.RED)
        print_colored("\n🔧 请查看上述错误信息并进行修复", Colors.YELLOW)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
