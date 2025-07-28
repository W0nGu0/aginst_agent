#!/usr/bin/env python3
"""
直接测试场景智能体功能
"""

import asyncio
import aiohttp
import json

async def test_scenario_agent():
    """测试场景智能体"""
    print("🧪 直接测试场景智能体")
    print("=" * 40)
    
    test_data = {
        "prompt": "生成APT攻击推演的医疗业务场景"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            print("📡 发送请求到场景智能体...")
            async with session.post(
                "http://localhost:8007/process_scenario_request",
                json=test_data,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                print(f"状态码: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ 场景智能体响应成功")
                    
                    # 美化输出
                    print("\n📄 响应内容:")
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                    
                    # 检查关键字段
                    result_str = json.dumps(result)
                    if "topology" in result_str:
                        print("\n🎯 ✅ 包含拓扑数据")
                    if "nodes" in result_str:
                        print("🎯 ✅ 包含节点数据")
                    if "connections" in result_str:
                        print("🎯 ✅ 包含连接数据")
                    if "error" in result_str:
                        print("⚠️  包含错误信息")
                    
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ 场景智能体响应失败: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return False

async def test_backend_proxy():
    """测试后端代理功能"""
    print("\n🧪 测试后端代理功能")
    print("=" * 40)
    
    test_data = {
        "prompt": "生成APT攻击推演的医疗业务场景"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            print("📡 发送请求到后端代理...")
            async with session.post(
                "http://localhost:8080/api/scenario/process_request",
                json=test_data,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                print(f"状态码: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ 后端代理响应成功")
                    
                    # 美化输出
                    print("\n📄 响应内容:")
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                    
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ 后端代理响应失败: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            return False

async def main():
    """主函数"""
    print("🎯 场景智能体功能测试")
    print("=" * 60)
    
    # 检查服务状态
    services = [
        ("场景智能体", "http://localhost:8007"),
        ("后端服务", "http://localhost:8080"),
        ("场景服务", "http://localhost:8002")
    ]
    
    print("📋 检查服务状态:")
    all_ok = True
    async with aiohttp.ClientSession() as session:
        for name, url in services:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    if response.status in [200, 404]:
                        print(f"  ✅ {name}: 运行中")
                    else:
                        print(f"  ⚠️  {name}: 状态码 {response.status}")
                        all_ok = False
            except Exception:
                print(f"  ❌ {name}: 未运行")
                all_ok = False
    
    if not all_ok:
        print("\n❌ 部分服务未运行，测试可能失败")
    
    print("\n" + "=" * 60)
    
    # 测试场景智能体
    agent_ok = await test_scenario_agent()
    
    # 测试后端代理
    backend_ok = await test_backend_proxy()
    
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    print(f"  场景智能体: {'✅ 正常' if agent_ok else '❌ 异常'}")
    print(f"  后端代理: {'✅ 正常' if backend_ok else '❌ 异常'}")
    
    if agent_ok or backend_ok:
        print("\n🎉 至少一个接口工作正常！")
        print("可以在前端测试场景创建功能了:")
        print("1. 访问 http://localhost:5173/against/create")
        print("2. 输入: '生成APT攻击推演的医疗业务场景'")
        print("3. 点击'生成场景'按钮")
    else:
        print("\n❌ 所有接口都有问题，需要进一步排查")

if __name__ == "__main__":
    asyncio.run(main())
