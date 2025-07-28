#!/usr/bin/env python3
"""
测试MCP服务连接
"""

import asyncio
import aiohttp
import json
from fastmcp import FastMCP

async def test_scenario_service_connection():
    """测试场景服务MCP连接"""
    print("🔧 测试场景服务MCP连接...")
    
    # 测试基础HTTP连接
    async with aiohttp.ClientSession() as session:
        try:
            # 测试服务是否运行
            async with session.get("http://127.0.0.1:8002/") as response:
                print(f"📡 场景服务基础连接: {response.status}")
        except Exception as e:
            print(f"❌ 场景服务基础连接失败: {e}")
            return False
        
        try:
            # 测试MCP端点
            async with session.post("http://127.0.0.1:8002/mcp/") as response:
                print(f"📡 场景服务MCP端点: {response.status}")
                if response.status == 200:
                    text = await response.text()
                    print(f"📄 响应内容: {text[:200]}...")
        except Exception as e:
            print(f"❌ 场景服务MCP端点连接失败: {e}")
    
    # 测试FastMCP客户端连接
    try:
        print("🔌 测试FastMCP客户端连接...")
        client = FastMCP.as_proxy("http://127.0.0.1:8002/mcp/")
        
        # 尝试调用一个简单的方法
        result = await client.list_scenario_templates()
        print(f"✅ FastMCP连接成功，获取到模板: {len(result) if isinstance(result, list) else 'N/A'}")
        return True
        
    except Exception as e:
        print(f"❌ FastMCP客户端连接失败: {e}")
        return False

async def test_attack_service_connection():
    """测试攻击服务MCP连接（作为对比）"""
    print("\n🔧 测试攻击服务MCP连接（对比）...")
    
    try:
        client = FastMCP.as_proxy("http://127.0.0.1:8001/mcp/")
        result = await client.scan_network("127.0.0.1")
        print(f"✅ 攻击服务MCP连接成功")
        return True
    except Exception as e:
        print(f"❌ 攻击服务MCP连接失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🧪 MCP服务连接测试")
    print("=" * 50)
    
    # 检查服务状态
    services = [
        ("场景服务", "http://127.0.0.1:8002"),
        ("攻击服务", "http://127.0.0.1:8001"),
        ("场景智能体", "http://127.0.0.1:8007"),
        ("后端服务", "http://127.0.0.1:8080")
    ]
    
    print("📋 检查服务状态:")
    async with aiohttp.ClientSession() as session:
        for name, url in services:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    status = "🟢 运行中" if response.status in [200, 404] else f"⚠️  状态码: {response.status}"
                    print(f"  {name}: {status}")
            except Exception as e:
                print(f"  {name}: 🔴 未运行 ({str(e)[:50]}...)")
    
    print("\n" + "=" * 50)
    
    # 测试MCP连接
    scenario_ok = await test_scenario_service_connection()
    attack_ok = await test_attack_service_connection()
    
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    print(f"  场景服务MCP: {'✅ 正常' if scenario_ok else '❌ 异常'}")
    print(f"  攻击服务MCP: {'✅ 正常' if attack_ok else '❌ 异常'}")
    
    if not scenario_ok:
        print("\n🔧 场景服务MCP连接问题排查:")
        print("1. 确保场景服务已启动: cd services/scenario_service && python main.py")
        print("2. 检查端口8002是否被占用")
        print("3. 检查FastMCP版本兼容性")
        print("4. 查看场景服务日志输出")
    
    if scenario_ok and attack_ok:
        print("\n🎉 所有MCP服务连接正常！")
        print("现在可以测试前端场景生成功能了。")

if __name__ == "__main__":
    asyncio.run(main())
