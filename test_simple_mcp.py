#!/usr/bin/env python3
"""
简单的MCP连接测试
"""

import asyncio
import json
from fastmcp import FastMCP

async def test_simple_mcp():
    """简单测试MCP连接"""
    print("🔧 简单MCP连接测试")
    print("=" * 40)
    
    try:
        # 创建客户端
        client = FastMCP.as_proxy("http://127.0.0.1:8002/mcp/")
        print("✅ FastMCP客户端创建成功")
        
        # 测试连接
        async with client.client as mcp_client:
            print("✅ MCP客户端连接成功")
            
            # 列出可用工具
            tools_response = await mcp_client.list_tools()
            print(f"📋 可用工具数量: {len(tools_response.tools)}")
            
            for tool in tools_response.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # 测试一个简单的工具
            print("\n🧪 测试 list_scenario_templates 工具...")
            response = await mcp_client.call_tool("list_scenario_templates", arguments={})
            result = "\n".join([b.text for b in response.content if hasattr(b, "text")])
            print(f"✅ 工具调用成功: {result}")
            
        return True
        
    except Exception as e:
        print(f"❌ MCP连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    success = await test_simple_mcp()
    
    if success:
        print("\n🎉 MCP连接测试成功！")
        print("现在可以测试场景智能体了")
    else:
        print("\n❌ MCP连接测试失败")
        print("请检查场景服务是否正常运行")

if __name__ == "__main__":
    asyncio.run(main())
