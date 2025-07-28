#!/usr/bin/env python3
"""
测试后端到场景智能体的连接
"""

import asyncio
import httpx
import json

async def test_direct_connection():
    """直接测试连接"""
    print("🔍 直接测试后端到场景智能体的连接")
    print("=" * 50)
    
    test_data = {"prompt": "构建一个针对APT攻击的医疗业务的攻防推演靶场"}
    
    async with httpx.AsyncClient() as client:
        try:
            print("📡 直接调用场景智能体...")
            response = await client.post(
                "http://localhost:8007/process_scenario_request",
                json=test_data,
                timeout=60.0
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 直接连接成功")
                print(f"📄 响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
                return True
            else:
                print(f"❌ 直接连接失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 连接异常: {e}")
            return False

async def test_backend_proxy():
    """测试后端代理"""
    print("\n🔍 测试后端代理")
    print("=" * 50)
    
    test_data = {"prompt": "构建一个针对APT攻击的医疗业务的攻防推演靶场"}
    
    async with httpx.AsyncClient() as client:
        try:
            print("📡 调用后端代理...")
            response = await client.post(
                "http://localhost:8080/api/scenario/process_request",
                json=test_data,
                timeout=120.0
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 后端代理成功")
                print(f"📄 响应: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
                return True
            else:
                print(f"❌ 后端代理失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 代理异常: {e}")
            return False

async def main():
    """主函数"""
    print("🎯 后端连接测试")
    print("=" * 60)
    
    # 测试直接连接
    direct_ok = await test_direct_connection()
    
    # 测试后端代理
    proxy_ok = await test_backend_proxy()
    
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    print(f"  直接连接: {'✅ 正常' if direct_ok else '❌ 异常'}")
    print(f"  后端代理: {'✅ 正常' if proxy_ok else '❌ 异常'}")
    
    if direct_ok and not proxy_ok:
        print("\n🔍 分析: 场景智能体正常，但后端代理有问题")
        print("可能原因:")
        print("1. 后端代理的超时设置太短")
        print("2. 后端代理的错误处理有问题")
        print("3. 后端代理的URL配置错误")
    elif not direct_ok:
        print("\n🔍 分析: 场景智能体本身有问题")
        print("需要检查场景智能体的日志")
    else:
        print("\n🎉 所有连接都正常！")

if __name__ == "__main__":
    asyncio.run(main())
