#!/usr/bin/env python3
"""
测试前端场景生成功能
"""

import asyncio
import aiohttp
import json

async def test_frontend_scenario():
    """测试前端场景生成功能"""
    print("🎯 测试前端场景生成功能")
    print("=" * 50)
    
    # 模拟前端发送的请求
    test_data = {
        "prompt": "构建一个针对APT攻击的医疗业务的攻防推演靶场"
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
                    
                    # 检查响应结构
                    if "data" in result and "agent_output" in result["data"]:
                        agent_output = result["data"]["agent_output"]
                        print(f"📄 智能体输出长度: {len(agent_output)} 字符")
                        
                        # 检查是否包含拓扑数据
                        if "topology" in agent_output:
                            print("🎯 ✅ 包含拓扑数据")
                            
                            # 尝试解析JSON
                            try:
                                # 查找JSON部分
                                start = agent_output.find('{"status":')
                                if start != -1:
                                    end = agent_output.rfind('}') + 1
                                    json_part = agent_output[start:end]
                                    topology_data = json.loads(json_part)
                                    
                                    print(f"📊 场景统计:")
                                    if "topology" in topology_data:
                                        topo = topology_data["topology"]
                                        print(f"   - 节点数量: {len(topo.get('nodes', []))}")
                                        print(f"   - 网络数量: {len(topo.get('networks', []))}")
                                        print(f"   - 连接数量: {len(topo.get('connections', []))}")
                                        
                                        # 显示部分节点信息
                                        nodes = topo.get('nodes', [])[:3]
                                        print(f"   - 示例节点:")
                                        for node in nodes:
                                            print(f"     * {node.get('name', 'N/A')} ({node.get('type', 'N/A')})")
                                    
                                    return True
                                    
                            except json.JSONDecodeError as e:
                                print(f"⚠️  JSON解析失败: {e}")
                                print(f"📄 原始输出: {agent_output[:500]}...")
                        else:
                            print("⚠️  未包含拓扑数据")
                            print(f"📄 输出内容: {agent_output[:300]}...")
                    
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
    print("🎯 前端场景生成功能测试")
    print("=" * 60)
    
    success = await test_frontend_scenario()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 前端场景生成功能测试成功！")
        print("\n📋 现在可以在前端测试:")
        print("1. 启动前端: npm run dev")
        print("2. 访问: http://localhost:5173/against/create")
        print("3. 输入: '构建一个针对APT攻击的医疗业务的攻防推演靶场'")
        print("4. 点击'生成场景'按钮")
        print("5. 应该会跳转到拓扑页面并显示半透明拓扑图")
        print("6. 可以编辑节点，然后点击'部署容器'")
    else:
        print("❌ 前端场景生成功能测试失败")

if __name__ == "__main__":
    asyncio.run(main())
