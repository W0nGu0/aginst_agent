#!/usr/bin/env python3
"""
测试场景生成功能
"""

import asyncio
import aiohttp
import json

async def test_scenario_generation():
    """测试场景生成功能"""
    print("🧪 测试场景生成功能")
    print("=" * 50)
    
    # 测试数据
    test_prompt = "生成APT攻击推演的医疗业务场景"
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. 测试场景智能体的综合处理接口
            print("📡 调用场景智能体...")
            async with session.post(
                "http://localhost:8007/process_scenario_request",
                json={"prompt": test_prompt},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                print(f"状态码: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ 场景智能体响应成功")
                    print(f"📄 响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    
                    # 检查是否包含拓扑数据
                    if "topology" in str(result):
                        print("🎯 包含拓扑数据 - 场景生成成功！")
                        return True
                    else:
                        print("⚠️  响应中未包含拓扑数据")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ 场景智能体响应失败: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False

async def test_mcp_tools_directly():
    """直接测试MCP工具"""
    print("\n🔧 直接测试MCP工具...")
    
    from fastmcp import FastMCP
    
    try:
        # 测试场景服务MCP工具
        client = FastMCP.as_proxy("http://127.0.0.1:8002/mcp/")
        
        print("📡 测试parse_apt_ready_scenario工具...")
        async with client.client as mcp_client:
            response = await mcp_client.call_tool("parse_apt_ready_scenario", arguments={})
            result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
            print(f"✅ parse_apt_ready_scenario 成功: {result[:200]}...")
        
        print("📡 测试generate_dynamic_scenario工具...")
        async with client.client as mcp_client:
            response = await mcp_client.call_tool(
                "generate_dynamic_scenario",
                arguments={
                    "business_scenario": "healthcare",
                    "attack_type": "apt",
                    "custom_config": {}
                }
            )
            result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
            print(f"✅ generate_dynamic_scenario 成功: {result[:200]}...")
            
        return True
        
    except Exception as e:
        print(f"❌ MCP工具测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🎯 场景生成功能完整测试")
    print("=" * 60)
    
    # 检查服务状态
    services = [
        ("场景服务", "http://127.0.0.1:8002"),
        ("场景智能体", "http://127.0.0.1:8007"),
        ("后端服务", "http://127.0.0.1:8080")
    ]
    
    print("📋 检查必要服务状态:")
    all_services_ok = True
    async with aiohttp.ClientSession() as session:
        for name, url in services:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    if response.status in [200, 404]:
                        print(f"  ✅ {name}: 运行中")
                    else:
                        print(f"  ⚠️  {name}: 状态码 {response.status}")
                        all_services_ok = False
            except Exception as e:
                print(f"  ❌ {name}: 未运行")
                all_services_ok = False
    
    if not all_services_ok:
        print("\n❌ 部分服务未运行，请先启动所有必要服务")
        return
    
    print("\n" + "=" * 60)
    
    # 测试MCP工具
    mcp_ok = await test_mcp_tools_directly()
    
    if not mcp_ok:
        print("\n❌ MCP工具测试失败，跳过综合测试")
        return
    
    print("\n" + "=" * 60)
    
    # 测试完整场景生成流程
    scenario_ok = await test_scenario_generation()
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"  MCP工具连接: {'✅ 正常' if mcp_ok else '❌ 异常'}")
    print(f"  场景生成流程: {'✅ 正常' if scenario_ok else '❌ 异常'}")
    
    if mcp_ok and scenario_ok:
        print("\n🎉 所有测试通过！场景生成功能正常工作")
        print("现在可以在前端测试场景创建功能了:")
        print("1. 访问 http://localhost:5173/against/create")
        print("2. 输入: '生成APT攻击推演的医疗业务场景'")
        print("3. 点击'生成场景'按钮")
        print("4. 应该会跳转到拓扑页面并显示半透明拓扑图")
    else:
        print("\n❌ 测试失败，需要进一步排查问题")

if __name__ == "__main__":
    asyncio.run(main())
