#!/usr/bin/env python3
"""
测试场景智能体健康状态
"""

import asyncio
import aiohttp
import json

async def test_scenario_agent_health():
    """测试场景智能体健康状态"""
    print("🔍 测试场景智能体健康状态")
    print("=" * 50)
    
    endpoints = [
        ("根路径", "http://localhost:8007/"),
        ("处理请求", "http://localhost:8007/process_scenario_request"),
        ("解析场景", "http://localhost:8007/parse_apt_scenario"),
    ]
    
    async with aiohttp.ClientSession() as session:
        for name, url in endpoints:
            try:
                if "process_scenario_request" in url:
                    # POST请求
                    async with session.post(
                        url,
                        json={"prompt": "测试"},
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        print(f"📡 {name} (POST): {response.status}")
                        if response.status == 200:
                            result = await response.json()
                            print(f"   ✅ 响应正常: {str(result)[:100]}...")
                        else:
                            text = await response.text()
                            print(f"   ❌ 错误: {text[:100]}...")
                else:
                    # GET请求
                    async with session.get(
                        url,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        print(f"📡 {name} (GET): {response.status}")
                        if response.status in [200, 404]:
                            print(f"   ✅ 服务运行中")
                        else:
                            text = await response.text()
                            print(f"   ❌ 错误: {text[:100]}...")
                            
            except Exception as e:
                print(f"📡 {name}: ❌ 连接失败 - {str(e)[:100]}...")

async def test_backend_to_scenario_agent():
    """测试后端到场景智能体的连接"""
    print("\n🔍 测试后端到场景智能体的连接")
    print("=" * 50)
    
    # 模拟后端发送的请求
    test_data = {
        "prompt": "构建一个针对APT攻击的医疗业务的攻防推演靶场"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            print("📡 发送请求到场景智能体...")
            async with session.post(
                "http://localhost:8007/process_scenario_request",
                json=test_data,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                print(f"状态码: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ 场景智能体响应成功")
                    print(f"📄 响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ 场景智能体响应失败: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            return False

async def main():
    """主函数"""
    print("🎯 场景智能体健康检查")
    print("=" * 60)
    
    # 基础健康检查
    await test_scenario_agent_health()
    
    # 连接测试
    success = await test_backend_to_scenario_agent()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 场景智能体工作正常！")
        print("问题可能在于:")
        print("1. 前端请求的URL路径不正确")
        print("2. 前端请求的数据格式不正确")
        print("3. 网络超时设置太短")
    else:
        print("❌ 场景智能体有问题，需要检查:")
        print("1. 场景智能体服务是否正常启动")
        print("2. 依赖的场景服务是否运行")
        print("3. API密钥是否配置正确")

if __name__ == "__main__":
    asyncio.run(main())
