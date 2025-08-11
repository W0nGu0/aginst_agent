#!/usr/bin/env python3
"""
AI Agent攻防推演平台 - 一键部署脚本
支持Windows、Linux、macOS跨平台部署
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import time

class Colors:
    """终端颜色定义"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
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

def print_step(step_num, text):
    """打印步骤"""
    print_colored(f"\n{step_num}. {text}", Colors.BLUE + Colors.BOLD)

def print_success(text):
    """打印成功信息"""
    print_colored(f"✅ {text}", Colors.GREEN)

def print_warning(text):
    """打印警告信息"""
    print_colored(f"⚠️  {text}", Colors.YELLOW)

def print_error(text):
    """打印错误信息"""
    print_colored(f"❌ {text}", Colors.RED)

def check_command(command):
    """检查命令是否存在"""
    return shutil.which(command) is not None

def run_command(command, cwd=None, check=True):
    """运行命令"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_dependencies():
    """检查系统依赖"""
    print_step(1, "检查系统依赖")
    
    dependencies = {
        'docker': 'Docker',
        'node': 'Node.js',
        'npm': 'NPM',
        'python3' if platform.system() != 'Windows' else 'python': 'Python 3.9+',
        'pip3' if platform.system() != 'Windows' else 'pip': 'pip'
    }
    
    missing_deps = []
    for cmd, name in dependencies.items():
        if check_command(cmd):
            print_success(f"{name} 已安装")
        else:
            print_error(f"{name} 未安装")
            missing_deps.append(name)
    
    if missing_deps:
        print_error(f"缺少依赖: {', '.join(missing_deps)}")
        print_colored("\n请安装缺少的依赖后重新运行部署脚本", Colors.YELLOW)
        return False
    
    return True

def install_frontend_dependencies():
    """安装前端依赖"""
    print_step(2, "安装前端依赖")
    
    if not os.path.exists('../package.json'):
        print_error("未找到package.json文件，请确保在项目根目录运行")
        return False
    
    print_colored("正在安装前端依赖...", Colors.CYAN)
    success, stdout, stderr = run_command('npm install', cwd='..')
    
    if success:
        print_success("前端依赖安装成功")
        return True
    else:
        print_error("前端依赖安装失败")
        print_colored(f"错误信息: {stderr}", Colors.RED)
        return False

def install_python_dependencies():
    """安装Python依赖"""
    print_step(3, "安装Python依赖")
    
    python_cmd = 'python3' if platform.system() != 'Windows' else 'python'
    pip_cmd = 'pip3' if platform.system() != 'Windows' else 'pip'
    
    # 安装全局依赖
    if os.path.exists('../requirements.txt'):
        print_colored("正在安装全局Python依赖...", Colors.CYAN)
        success, stdout, stderr = run_command(f'{pip_cmd} install -r requirements.txt', cwd='..')
        if not success:
            print_error("全局Python依赖安装失败")
            print_colored(f"错误信息: {stderr}", Colors.RED)
            return False
        print_success("全局Python依赖安装成功")
    
    # 安装后端依赖
    backend_requirements = Path('../backend/requirements.txt')
    if backend_requirements.exists():
        print_colored("正在安装后端Python依赖...", Colors.CYAN)
        success, stdout, stderr = run_command(f'{pip_cmd} install -r requirements.txt', cwd='../backend')
        if not success:
            print_error("后端Python依赖安装失败")
            print_colored(f"错误信息: {stderr}", Colors.RED)
            return False
        print_success("后端Python依赖安装成功")
    
    return True

def check_environment_config():
    """检查环境配置"""
    print_step(4, "检查环境配置")
    
    env_file = Path('../agents/scenario_agent/.env')
    if not env_file.exists():
        print_warning("未找到agents/scenario_agent/.env文件")
        print_colored("请创建该文件并配置以下内容:", Colors.YELLOW)
        print_colored("""
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-chat
        """, Colors.CYAN)
        
        create_env = input("是否现在创建环境配置文件? (y/n): ").lower().strip()
        if create_env == 'y':
            api_key = input("请输入您的DeepSeek API密钥: ").strip()
            if api_key:
                env_content = f"""DEEPSEEK_API_KEY={api_key}
DEEPSEEK_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-chat
MAX_TOKENS=4000
TEMPERATURE=0.7
TIMEOUT=30
"""
                env_file.parent.mkdir(parents=True, exist_ok=True)
                env_file.write_text(env_content)
                print_success("环境配置文件创建成功")
            else:
                print_warning("未输入API密钥，请稍后手动配置")
        else:
            print_warning("请稍后手动创建环境配置文件")
    else:
        print_success("环境配置文件已存在")
    
    return True

def start_services():
    """启动服务"""
    print_step(5, "启动服务")
    
    if not os.path.exists('../start_all_services.py'):
        print_error("未找到start_all_services.py文件")
        return False
    
    python_cmd = 'python3' if platform.system() != 'Windows' else 'python'
    print_colored("正在启动所有服务...", Colors.CYAN)
    
    try:
        # 在新进程中启动服务
        process = subprocess.Popen([python_cmd, 'start_all_services.py'], cwd='..')
        time.sleep(5)  # 等待服务启动
        
        if process.poll() is None:
            print_success("服务启动成功")
            print_colored("\n🌐 访问地址:", Colors.BOLD + Colors.GREEN)
            print_colored("  前端界面: http://localhost:5173", Colors.GREEN)
            print_colored("  后端API: http://localhost:8080", Colors.GREEN)
            print_colored("  场景服务: http://localhost:8002", Colors.GREEN)
            print_colored("  场景智能体: http://localhost:8007", Colors.GREEN)
            
            print_colored("\n⚠️  注意事项:", Colors.YELLOW)
            print_colored("  1. 确保已配置DeepSeek API密钥", Colors.YELLOW)
            print_colored("  2. 确保Docker已安装并运行", Colors.YELLOW)
            print_colored("  3. 按Ctrl+C停止所有服务", Colors.YELLOW)
            
            return True
        else:
            print_error("服务启动失败")
            return False
            
    except Exception as e:
        print_error(f"启动服务时出错: {e}")
        return False

def main():
    """主函数"""
    print_header("AI Agent攻防推演平台 - 一键部署脚本")
    print_colored(f"操作系统: {platform.system()} {platform.release()}", Colors.CYAN)
    print_colored(f"Python版本: {sys.version}", Colors.CYAN)
    
    # 检查是否在正确目录
    if not os.path.exists('../package.json') or not os.path.exists('../backend'):
        print_error("请将此脚本放在项目根目录的部署手册文件夹中运行")
        sys.exit(1)
    
    # 执行部署步骤
    steps = [
        check_dependencies,
        install_frontend_dependencies,
        install_python_dependencies,
        check_environment_config,
        start_services
    ]
    
    for step in steps:
        if not step():
            print_error("部署失败，请检查错误信息")
            sys.exit(1)
    
    print_header("部署完成")
    print_success("AI Agent攻防推演平台部署成功!")
    print_colored("\n🎉 您现在可以开始使用系统了!", Colors.BOLD + Colors.GREEN)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n部署被用户中断", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        print_error(f"部署过程中发生未知错误: {e}")
        sys.exit(1)
