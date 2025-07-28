#!/usr/bin/env python3
"""
测试场景智能体功能
"""

import asyncio
import httpx
import json

# 测试配置
SCENARIO_AGENT_URL = "http://localhost:8007"
SCENARIO_SERVICE_URL = "http://localhost:8002"

async def test_scenario_service():
    """测试场景服务的MCP工具"""
    print("🔧 测试场景服务...")
    
    try:
        async with httpx.AsyncClient() as client:
            # 测试解析apt-ready场景
            response = await client.get(f"{SCENARIO_SERVICE_URL}parse_apt_ready_scenario")
            if response.status_code == 200:
                print("✅ 场景服务apt-ready解析功能正常")
                result = response.json()
                print(f"   - 解析结果: {result.get('status', 'unknown')}")
            else:
                print(f"❌ 场景服务测试失败: {response.status_code}")
                
    except Exception as e:
        print(f"❌ 场景服务连接失败: {e}")

async def test_scenario_agent():
    """测试场景智能体"""
    print("\n🤖 测试场景智能体...")
    
    try:
        async with httpx.AsyncClient() as client:
            # 测试提示词分析
            test_prompt = "医疗机构遭受APT攻击，攻击者通过钓鱼邮件获得初始访问权限，然后在内网中横向移动，最终窃取患者医疗数据"
            
            response = await client.post(
                f"{SCENARIO_AGENT_URL}/analyze_prompt",
                json={"prompt": test_prompt},
                timeout=30.0
            )
            
            if response.status_code == 200:
                print("✅ 场景智能体提示词分析功能正常")
                result = response.json()
                data = result.get("data", {})
                print(f"   - 业务场景: {data.get('business_scenario')}")
                print(f"   - 攻击类型: {data.get('attack_type')}")
                print(f"   - 置信度: {data.get('confidence')}")
            else:
                print(f"❌ 场景智能体测试失败: {response.status_code}")
                print(f"   - 错误信息: {response.text}")
                
    except Exception as e:
        print(f"❌ 场景智能体连接失败: {e}")

async def test_apt_scenario_parsing():
    """测试APT场景解析"""
    print("\n📋 测试APT场景解析...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SCENARIO_AGENT_URL}/parse_apt_scenario",
                timeout=30.0
            )
            
            if response.status_code == 200:
                print("✅ APT场景解析功能正常")
                result = response.json()
                data = result.get("data", {})
                if "topology" in data:
                    topology = data["topology"]
                    print(f"   - 节点数量: {len(topology.get('nodes', []))}")
                    print(f"   - 网络数量: {len(topology.get('networks', []))}")
                    print(f"   - 连接数量: {len(topology.get('connections', []))}")
                    
                    # 显示一些节点信息
                    nodes = topology.get('nodes', [])[:5]  # 显示前5个节点
                    for node in nodes:
                        print(f"   - 节点: {node.get('name')} ({node.get('type')})")
            else:
                print(f"❌ APT场景解析失败: {response.status_code}")
                print(f"   - 错误信息: {response.text}")
                
    except Exception as e:
        print(f"❌ APT场景解析连接失败: {e}")

async def test_comprehensive_scenario():
    """测试综合场景处理"""
    print("\n🎯 测试综合场景处理...")
    
    try:
        async with httpx.AsyncClient() as client:
            test_prompt = "创建一个医疗机构的APT攻击场景，包含多层网络防护"
            
            response = await client.post(
                f"{SCENARIO_AGENT_URL}/process_scenario_request",
                json={"prompt": test_prompt},
                timeout=60.0
            )
            
            if response.status_code == 200:
                print("✅ 综合场景处理功能正常")
                result = response.json()
                agent_output = result.get("data", {}).get("agent_output", "")
                print(f"   - Agent输出长度: {len(agent_output)} 字符")
                print(f"   - 输出预览: {agent_output[:200]}...")
            else:
                print(f"❌ 综合场景处理失败: {response.status_code}")
                print(f"   - 错误信息: {response.text}")
                
    except Exception as e:
        print(f"❌ 综合场景处理连接失败: {e}")

async def main():
    """主测试函数"""
    print("🚀 开始测试场景智能体系统...")
    print("=" * 50)
    
    # 按顺序执行测试
    await test_scenario_service()
    await test_scenario_agent()
    await test_apt_scenario_parsing()
    await test_comprehensive_scenario()
    
    print("\n" + "=" * 50)
    print("✨ 测试完成！")
    print("\n📝 使用说明:")
    print("1. 确保场景服务运行在端口8002")
    print("2. 确保场景智能体运行在端口8007")
    print("3. 确保DeepSeek API密钥已配置")
    print("4. 确保apt-ready.yml文件存在于docker/compose-templates/generated/目录")

if __name__ == "__main__":
    asyncio.run(main())
