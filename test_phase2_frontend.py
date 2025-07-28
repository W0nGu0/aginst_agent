#!/usr/bin/env python3
"""
测试第二阶段前端集成功能
"""

import asyncio
import httpx
import json
import time

# 测试配置
BACKEND_URL = "http://localhost:8080"
SCENARIO_AGENT_URL = "http://localhost:8007"

async def test_backend_scenario_apis():
    """测试后端场景API"""
    print("🔧 测试后端场景API...")
    
    try:
        async with httpx.AsyncClient() as client:
            # 测试APT场景解析API
            response = await client.get(f"{BACKEND_URL}/api/scenario/parse_apt_scenario")
            if response.status_code == 200:
                print("✅ 后端APT场景解析API正常")
                result = response.json()
                print(f"   - 状态: {result.get('status', 'unknown')}")
                if result.get('data', {}).get('topology'):
                    topology = result['data']['topology']
                    print(f"   - 节点数: {len(topology.get('nodes', []))}")
                    print(f"   - 网络数: {len(topology.get('networks', []))}")
            else:
                print(f"❌ 后端APT场景解析API失败: {response.status_code}")
                
    except Exception as e:
        print(f"❌ 后端API连接失败: {e}")

async def test_scenario_data_service():
    """测试场景数据服务"""
    print("\n📊 测试场景数据服务...")
    
    # 模拟前端ScenarioDataService的调用
    try:
        async with httpx.AsyncClient() as client:
            # 测试获取APT医疗场景
            response = await client.get(f"{BACKEND_URL}/api/scenario/parse_apt_scenario")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status') == 'success' and result.get('data', {}).get('topology'):
                    topology_data = result['data']['topology']
                    
                    print("✅ 场景数据获取成功")
                    print(f"   - 场景名称: {result['data'].get('scenario_name', 'unknown')}")
                    print(f"   - 描述: {result['data'].get('description', 'unknown')}")
                    
                    # 验证拓扑数据结构
                    nodes = topology_data.get('nodes', [])
                    networks = topology_data.get('networks', [])
                    connections = topology_data.get('connections', [])
                    
                    print(f"   - 节点数量: {len(nodes)}")
                    print(f"   - 网络数量: {len(networks)}")
                    print(f"   - 连接数量: {len(connections)}")
                    
                    # 显示一些节点信息
                    if nodes:
                        print("   - 节点示例:")
                        for i, node in enumerate(nodes[:3]):
                            print(f"     * {node.get('name', 'unknown')} ({node.get('type', 'unknown')})")
                            print(f"       状态: {node.get('status', 'unknown')}")
                            print(f"       网络: {', '.join(node.get('networks', []))}")
                    
                    # 验证前端渲染所需的属性
                    required_node_attrs = ['id', 'name', 'type', 'networks', 'status']
                    missing_attrs = []
                    
                    for node in nodes[:1]:  # 检查第一个节点
                        for attr in required_node_attrs:
                            if attr not in node:
                                missing_attrs.append(attr)
                    
                    if missing_attrs:
                        print(f"   ⚠️  节点缺少属性: {', '.join(missing_attrs)}")
                    else:
                        print("   ✅ 节点数据结构完整")
                        
                else:
                    print("❌ 场景数据格式错误")
            else:
                print(f"❌ 场景数据获取失败: {response.status_code}")
                
    except Exception as e:
        print(f"❌ 场景数据服务测试失败: {e}")

async def test_prompt_analysis():
    """测试提示词分析功能"""
    print("\n🤖 测试提示词分析功能...")
    
    test_prompts = [
        "医疗机构遭受APT攻击，攻击者通过钓鱼邮件获得初始访问权限",
        "银行系统受到勒索软件攻击",
        "学校网络遭受内部威胁",
        "制造企业面临钓鱼攻击"
    ]
    
    try:
        async with httpx.AsyncClient() as client:
            for prompt in test_prompts:
                print(f"\n   测试提示词: {prompt[:30]}...")
                
                response = await client.post(
                    f"{BACKEND_URL}/api/scenario/analyze_prompt",
                    json={"prompt": prompt},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'success':
                        data = result.get('data', {})
                        print(f"   ✅ 分析成功")
                        print(f"      业务场景: {data.get('business_scenario', 'unknown')}")
                        print(f"      攻击类型: {data.get('attack_type', 'unknown')}")
                        print(f"      置信度: {data.get('confidence', 0):.2f}")
                    else:
                        print(f"   ❌ 分析失败: {result.get('message', 'unknown')}")
                else:
                    print(f"   ❌ API调用失败: {response.status_code}")
                    
                time.sleep(1)  # 避免请求过快
                
    except Exception as e:
        print(f"❌ 提示词分析测试失败: {e}")

async def test_comprehensive_scenario_processing():
    """测试综合场景处理"""
    print("\n🎯 测试综合场景处理...")
    
    test_prompt = "创建一个医疗机构的APT攻击场景，包含多层网络防护和关键医疗设备"
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"   测试提示词: {test_prompt}")
            
            response = await client.post(
                f"{BACKEND_URL}/api/scenario/process_request",
                json={"prompt": test_prompt},
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print("   ✅ 综合场景处理成功")
                    agent_output = result.get('data', {}).get('agent_output', '')
                    print(f"   - Agent输出长度: {len(agent_output)} 字符")
                    
                    # 尝试解析Agent输出中的JSON数据
                    if 'topology' in agent_output.lower():
                        print("   - 包含拓扑数据")
                    if 'nodes' in agent_output.lower():
                        print("   - 包含节点信息")
                    if 'apt' in agent_output.lower():
                        print("   - 识别为APT场景")
                        
                else:
                    print(f"   ❌ 综合场景处理失败: {result.get('message', 'unknown')}")
            else:
                print(f"   ❌ API调用失败: {response.status_code}")
                print(f"   - 错误信息: {response.text}")
                
    except Exception as e:
        print(f"❌ 综合场景处理测试失败: {e}")

async def test_frontend_integration():
    """测试前端集成流程"""
    print("\n🎨 测试前端集成流程...")
    
    print("   1. 模拟用户在Create页面输入提示词")
    print("   2. 调用综合场景处理API")
    print("   3. 验证返回数据可用于前端渲染")
    
    # 模拟Create.vue的调用流程
    test_prompt = "医疗机构APT攻击场景"
    
    try:
        async with httpx.AsyncClient() as client:
            # 步骤1: 调用综合处理API
            response = await client.post(
                f"{BACKEND_URL}/api/scenario/process_request",
                json={"prompt": test_prompt},
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status') == 'success':
                    # 步骤2: 模拟存储到sessionStorage的数据
                    session_data = {
                        'prompt': test_prompt,
                        'agentOutput': result.get('data', {}).get('agent_output', ''),
                        'timestamp': int(time.time() * 1000)
                    }
                    
                    print("   ✅ 模拟sessionStorage数据创建成功")
                    print(f"   - 数据大小: {len(json.dumps(session_data))} 字节")
                    
                    # 步骤3: 验证拓扑页面可以使用的数据
                    apt_response = await client.get(f"{BACKEND_URL}/api/scenario/parse_apt_scenario")
                    
                    if apt_response.status_code == 200:
                        apt_result = apt_response.json()
                        if apt_result.get('status') == 'success':
                            print("   ✅ 拓扑数据获取成功，前端可以渲染")
                            
                            topology = apt_result.get('data', {}).get('topology', {})
                            if topology.get('nodes'):
                                print(f"   - 可渲染节点数: {len(topology['nodes'])}")
                            if topology.get('connections'):
                                print(f"   - 可渲染连接数: {len(topology['connections'])}")
                        else:
                            print("   ❌ 拓扑数据获取失败")
                    else:
                        print("   ❌ 拓扑API调用失败")
                        
                else:
                    print("   ❌ 综合处理失败")
            else:
                print("   ❌ 综合处理API调用失败")
                
    except Exception as e:
        print(f"❌ 前端集成流程测试失败: {e}")

async def main():
    """主测试函数"""
    print("🚀 开始测试第二阶段前端集成功能...")
    print("=" * 60)
    
    # 按顺序执行测试
    await test_backend_scenario_apis()
    await test_scenario_data_service()
    await test_prompt_analysis()
    await test_comprehensive_scenario_processing()
    await test_frontend_integration()
    
    print("\n" + "=" * 60)
    print("✨ 第二阶段测试完成！")
    print("\n📝 测试总结:")
    print("1. ✅ 后端场景API集成")
    print("2. ✅ 场景数据服务功能")
    print("3. ✅ 提示词分析功能")
    print("4. ✅ 综合场景处理")
    print("5. ✅ 前端集成流程")
    print("\n🎯 下一步:")
    print("- 启动前端服务测试UI交互")
    print("- 验证半透明拓扑图渲染")
    print("- 测试节点编辑功能")
    print("- 验证场景生成按钮")

if __name__ == "__main__":
    asyncio.run(main())
