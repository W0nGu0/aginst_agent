#!/usr/bin/env python3
"""
防御智能体诊断工具
用于诊断智能体启动问题
"""

import sys
import traceback
import os
from pathlib import Path

def test_imports():
    """测试所有必要的导入"""
    print("🔍 测试导入...")
    
    imports_to_test = [
        ("os", "os"),
        ("httpx", "httpx"),
        ("json", "json"),
        ("asyncio", "asyncio"),
        ("logging", "logging"),
        ("websockets.client", "websockets"),
        ("fastapi", "fastapi"),
        ("pydantic", "pydantic"),
        ("pathlib", "pathlib"),
        ("dotenv", "python-dotenv"),
        ("typing", "typing"),
        ("fastmcp", "fastmcp"),
        ("langchain_deepseek", "langchain-deepseek"),
        ("langchain.agents", "langchain"),
        ("langchain_core.prompts", "langchain-core"),
        ("langchain.tools", "langchain")
    ]
    
    failed_imports = []
    
    for module_name, package_name in imports_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            failed_imports.append(package_name)
    
    if failed_imports:
        print(f"\n❌ 缺失的包，请安装:")
        for package in set(failed_imports):
            print(f"   pip install {package}")
        return False
    
    return True

def test_env_config():
    """测试环境配置"""
    print("\n🔍 测试环境配置...")
    
    # 检查.env文件
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        print("⚠️ .env文件不存在，将使用默认配置")
        print("   建议复制 .env.example 为 .env 并配置API密钥")
    else:
        print("✅ .env文件存在")
    
    # 检查环境变量
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_key:
        print("⚠️ DEEPSEEK_API_KEY 未设置")
        print("   智能体可能无法正常工作，请在.env文件中设置API密钥")
    else:
        print("✅ DEEPSEEK_API_KEY 已设置")
    
    return True

def test_mcp_connection():
    """测试MCP服务连接"""
    print("\n🔍 测试MCP服务连接...")
    
    import httpx
    
    services = [
        ("威胁阻断服务", "http://127.0.0.1:8008/mcp/"),
        ("漏洞修复服务", "http://127.0.0.1:8009/mcp/"),
        ("攻击溯源服务", "http://127.0.0.1:8010/mcp/")
    ]
    
    for service_name, url in services:
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(url)
                if response.status_code == 200:
                    print(f"✅ {service_name}: 连接成功")
                else:
                    print(f"⚠️ {service_name}: HTTP {response.status_code}")
        except httpx.ConnectError:
            print(f"❌ {service_name}: 连接失败 - 服务可能未启动")
        except Exception as e:
            print(f"❌ {service_name}: {e}")
    
    return True

def test_fastmcp_proxy():
    """测试FastMCP代理连接"""
    print("\n🔍 测试FastMCP代理...")
    
    try:
        from fastmcp import FastMCP
        
        # 测试创建代理
        threat_service = FastMCP.as_proxy("http://127.0.0.1:8008/mcp/")
        print("✅ FastMCP代理创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ FastMCP代理测试失败: {e}")
        traceback.print_exc()
        return False

def test_langchain_components():
    """测试LangChain组件"""
    print("\n🔍 测试LangChain组件...")
    
    try:
        from langchain_deepseek import ChatDeepSeek
        from langchain.agents import AgentExecutor, create_tool_calling_agent
        from langchain_core.prompts import ChatPromptTemplate
        from langchain.tools import tool
        
        print("✅ LangChain组件导入成功")
        
        # 测试创建LLM（不需要真实API密钥）
        try:
            llm = ChatDeepSeek(model="deepseek-chat", api_key="test-key")
            print("✅ ChatDeepSeek实例创建成功")
        except Exception as e:
            print(f"⚠️ ChatDeepSeek创建警告: {e}")
        
        # 测试工具装饰器
        @tool
        async def test_tool() -> str:
            """测试工具"""
            return "测试成功"
        
        print("✅ 工具装饰器测试成功")
        
        return True
        
    except Exception as e:
        print(f"❌ LangChain组件测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🧪 防御智能体诊断工具")
    print("=" * 50)
    
    all_tests_passed = True
    
    # 测试导入
    if not test_imports():
        all_tests_passed = False
    
    # 测试环境配置
    if not test_env_config():
        all_tests_passed = False
    
    # 测试MCP连接
    if not test_mcp_connection():
        all_tests_passed = False
    
    # 测试FastMCP代理
    if not test_fastmcp_proxy():
        all_tests_passed = False
    
    # 测试LangChain组件
    if not test_langchain_components():
        all_tests_passed = False
    
    if all_tests_passed:
        print("\n🎉 所有测试通过！")
        print("防御智能体应该可以正常启动了。")
        return 0
    else:
        print("\n❌ 部分测试失败，请根据上述提示解决问题。")
        return 1

if __name__ == "__main__":
    sys.exit(main())