#!/usr/bin/env python3
"""
完整的前端功能测试
"""

import asyncio
import aiohttp
import json

async def test_complete_frontend_flow():
    """测试完整的前端流程"""
    print("🎯 测试完整的前端场景生成流程")
    print("=" * 60)
    
    # 模拟前端发送的请求
    test_data = {
        "prompt": "构建一个针对APT攻击的医疗业务的攻防推演靶场"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            print("📡 发送请求到后端...")
            print(f"   URL: http://localhost:8080/api/scenario/process_request")
            print(f"   数据: {test_data}")
            
            async with session.post(
                "http://localhost:8080/api/scenario/process_request",
                json=test_data,
                timeout=aiohttp.ClientTimeout(total=200)  # 3分钟超时
            ) as response:
                print(f"📊 响应状态码: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ 后端响应成功")
                    
                    # 检查响应结构
                    print("\n📋 响应结构分析:")
                    print(f"   - 响应类型: {type(result)}")
                    print(f"   - 响应键: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
                    
                    # 检查是否包含拓扑数据
                    result_str = json.dumps(result, ensure_ascii=False)
                    
                    checks = [
                        ("拓扑数据", "topology" in result_str),
                        ("节点数据", "nodes" in result_str),
                        ("网络数据", "networks" in result_str),
                        ("连接数据", "connections" in result_str),
                        ("医疗场景", "medical" in result_str or "healthcare" in result_str),
                        ("APT攻击", "apt" in result_str.lower()),
                        ("场景名称", "scenario_name" in result_str),
                        ("Docker文件", "compose_file" in result_str)
                    ]
                    
                    print("\n🔍 内容检查:")
                    for name, passed in checks:
                        status = "✅" if passed else "❌"
                        print(f"   {status} {name}")
                    
                    # 尝试解析拓扑数据
                    if "topology" in result_str:
                        try:
                            # 查找JSON部分
                            if "data" in result and "agent_output" in result["data"]:
                                agent_output = result["data"]["agent_output"]
                                
                                # 查找拓扑JSON
                                start = agent_output.find('{"status":')
                                if start != -1:
                                    end = agent_output.rfind('}') + 1
                                    json_part = agent_output[start:end]
                                    topology_data = json.loads(json_part)
                                    
                                    if "topology" in topology_data:
                                        topo = topology_data["topology"]
                                        print(f"\n📊 拓扑统计:")
                                        print(f"   - 节点数量: {len(topo.get('nodes', []))}")
                                        print(f"   - 网络数量: {len(topo.get('networks', []))}")
                                        print(f"   - 连接数量: {len(topo.get('connections', []))}")
                                        
                                        # 显示部分节点
                                        nodes = topo.get('nodes', [])[:5]
                                        print(f"   - 示例节点:")
                                        for node in nodes:
                                            node_type = node.get('type', 'unknown')
                                            node_name = node.get('name', 'unnamed')
                                            print(f"     * {node_name} ({node_type})")
                                        
                                        print("\n🎉 拓扑数据解析成功！")
                                        return True
                                        
                        except json.JSONDecodeError as e:
                            print(f"⚠️  JSON解析失败: {e}")
                    
                    print("\n📄 原始响应预览:")
                    preview = str(result)[:500] + "..." if len(str(result)) > 500 else str(result)
                    print(f"   {preview}")
                    
                    return True
                    
                else:
                    error_text = await response.text()
                    print(f"❌ 后端响应失败: {error_text}")
                    return False
                    
        except asyncio.TimeoutError:
            print("❌ 请求超时")
            return False
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False

async def test_services_health():
    """测试服务健康状态"""
    print("🔍 检查服务健康状态")
    print("=" * 40)
    
    services = [
        ("后端服务", "http://localhost:8080"),
        ("场景智能体", "http://localhost:8007"),
        ("场景服务", "http://localhost:8002"),
        ("前端服务", "http://localhost:5173")
    ]
    
    all_healthy = True
    async with aiohttp.ClientSession() as session:
        for name, url in services:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status in [200, 404]:
                        print(f"   ✅ {name}: 运行中")
                    else:
                        print(f"   ⚠️  {name}: 状态码 {response.status}")
                        all_healthy = False
            except Exception as e:
                print(f"   ❌ {name}: 未运行 ({str(e)[:30]}...)")
                all_healthy = False
    
    return all_healthy

async def main():
    """主函数"""
    print("🎯 完整前端功能测试")
    print("=" * 70)
    
    # 检查服务健康状态
    services_ok = await test_services_health()
    
    if not services_ok:
        print("\n❌ 部分服务未运行，测试可能失败")
        print("请确保以下服务正在运行:")
        print("1. 后端服务: uvicorn backend.main:app --reload --port 8080")
        print("2. 场景智能体: cd agents/scenario_agent && python main.py")
        print("3. 场景服务: cd services/scenario_service && python main.py")
        print("4. 前端服务: npm run dev")
        return
    
    print("\n" + "=" * 70)
    
    # 测试完整流程
    success = await test_complete_frontend_flow()
    
    print("\n" + "=" * 70)
    print("📊 测试结果:")
    print(f"   服务健康: {'✅ 正常' if services_ok else '❌ 异常'}")
    print(f"   场景生成: {'✅ 正常' if success else '❌ 异常'}")
    
    if services_ok and success:
        print("\n🎉 所有测试通过！")
        print("\n📋 现在可以在前端测试:")
        print("1. 访问: http://localhost:5173/against/create")
        print("2. 输入: '构建一个针对APT攻击的医疗业务的攻防推演靶场'")
        print("3. 点击'场景生成'按钮")
        print("4. 应该会跳转到: http://localhost:5173/#/topology?mode=scenario")
        print("5. 显示半透明拓扑图，可以编辑节点")
        print("6. 点击'🚀 部署容器'启动实际容器")
    else:
        print("\n❌ 测试失败，需要进一步排查")

if __name__ == "__main__":
    asyncio.run(main())
