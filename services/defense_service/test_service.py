#!/usr/bin/env python3
"""
防御服务测试脚本
用于诊断服务启动问题
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """测试所有必要的导入"""
    print("🔍 测试导入...")
    
    try:
        import asyncio
        print("✅ asyncio")
    except ImportError as e:
        print(f"❌ asyncio: {e}")
        return False
    
    try:
        import json
        print("✅ json")
    except ImportError as e:
        print(f"❌ json: {e}")
        return False
    
    try:
        import random
        print("✅ random")
    except ImportError as e:
        print(f"❌ random: {e}")
        return False
    
    try:
        from datetime import datetime
        print("✅ datetime")
    except ImportError as e:
        print(f"❌ datetime: {e}")
        return False
    
    try:
        from fastmcp import FastMCP
        print("✅ fastmcp")
    except ImportError as e:
        print(f"❌ fastmcp: {e}")
        print("请安装: pip install fastmcp")
        return False
    
    try:
        from pydantic import BaseModel
        print("✅ pydantic")
    except ImportError as e:
        print(f"❌ pydantic: {e}")
        print("请安装: pip install pydantic")
        return False
    
    try:
        from typing import List, Dict, Any, Optional
        print("✅ typing")
    except ImportError as e:
        print(f"❌ typing: {e}")
        return False
    
    return True

def test_mcp_service():
    """测试MCP服务创建"""
    print("\n🔍 测试MCP服务创建...")
    
    try:
        from fastmcp import FastMCP
        
        # 创建测试服务
        mcp = FastMCP("Test Service")
        
        @mcp.tool()
        async def test_tool() -> str:
            """测试工具"""
            return "测试成功"
        
        print("✅ MCP服务创建成功")
        return True
        
    except Exception as e:
        print(f"❌ MCP服务创建失败: {e}")
        traceback.print_exc()
        return False

def test_uvicorn():
    """测试uvicorn"""
    print("\n🔍 测试uvicorn...")
    
    try:
        import uvicorn
        print("✅ uvicorn导入成功")
        return True
    except ImportError as e:
        print(f"❌ uvicorn导入失败: {e}")
        print("请安装: pip install uvicorn")
        return False

def main():
    """主函数"""
    print("🧪 防御服务诊断工具")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        print("\n❌ 导入测试失败，请安装缺失的依赖包")
        return 1
    
    # 测试uvicorn
    if not test_uvicorn():
        print("\n❌ uvicorn测试失败")
        return 1
    
    # 测试MCP服务
    if not test_mcp_service():
        print("\n❌ MCP服务测试失败")
        return 1
    
    print("\n🎉 所有测试通过！")
    print("现在可以尝试启动防御服务了。")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())