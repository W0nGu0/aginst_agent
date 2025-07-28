# Added comment for test
import os
import json
import tempfile
from fastapi import FastAPI
from fastmcp import FastMCP
from pydantic import BaseModel, Field
import subprocess
import yaml
from typing import Dict, List, Optional
from pathlib import Path

# Define the path to the scenario library relative to this script
SCENARIO_LIBRARY_PATH = os.path.join(os.path.dirname(__file__), "scenario_library")
COMPOSE_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "docker", "compose-templates")

mcp = FastMCP(
    name="Scenario Service"
)

class ScenarioTemplate(BaseModel):
    name: str
    description: str
    version: str
    ports: list[str] = Field(default_factory=list)
    docker_compose_content: str | None = None

@mcp.tool
def list_scenario_templates() -> List[str]:
    """
    Lists all available scenario templates from the library.
    """
    if not os.path.exists(SCENARIO_LIBRARY_PATH):
        os.makedirs(SCENARIO_LIBRARY_PATH)
        return []
    
    try:
        # List directories in the scenario library path
        return [
            d for d in os.listdir(SCENARIO_LIBRARY_PATH)
            if os.path.isdir(os.path.join(SCENARIO_LIBRARY_PATH, d))
        ]
    except Exception as e:
        return [f"Error listing templates: {str(e)}"]

@mcp.tool
def get_scenario_template(name: str) -> ScenarioTemplate | str:
    """
    Retrieves the details of a specific scenario template, including its manifest and docker-compose content.
    """
    template_dir = os.path.join(SCENARIO_LIBRARY_PATH, name)
    if not os.path.isdir(template_dir):
        return f"Error: Scenario template '{name}' not found."

    try:
        manifest_path = os.path.join(template_dir, "manifest.yml")
        compose_path = os.path.join(template_dir, "docker-compose.yml")

        manifest_data = {}
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                manifest_data = yaml.safe_load(f).get("info", {})

        compose_content = None
        if os.path.exists(compose_path):
            with open(compose_path, 'r') as f:
                compose_content = f.read()

        return ScenarioTemplate(
            name=manifest_data.get("name", name),
            description=manifest_data.get("description", "No description provided."),
            version=manifest_data.get("version", "N/A"),
            ports=manifest_data.get("ports", []),
            docker_compose_content=compose_content
        )

    except Exception as e:
        return f"Error reading template '{name}': {str(e)}"

class ScenarioRequest(BaseModel):
    attack_type: str = Field(..., description="攻击类型：apt, phishing, ransomware, insider_threat")
    business_scenario: str = Field(..., description="业务场景：healthcare, finance, education, manufacturing")
    custom_config: Optional[Dict] = Field(None, description="自定义配置参数")

@mcp.tool
def generate_dynamic_scenario(attack_type: str, business_scenario: str, custom_config: dict = None) -> str:
    """
    根据攻击类型和业务场景动态生成Docker Compose文件

    Args:
        attack_type: 攻击类型 (apt, phishing, ransomware, insider_threat)
        business_scenario: 业务场景 (healthcare, finance, education, manufacturing)
        custom_config: 自定义配置参数

    Returns:
        生成的场景信息和Docker Compose文件路径
    """
    try:
        # 验证输入参数
        valid_attacks = ["apt", "phishing", "ransomware", "insider_threat"]
        valid_scenarios = ["healthcare", "finance", "education", "manufacturing"]

        if attack_type not in valid_attacks:
            return f"Error: Invalid attack type. Valid options: {valid_attacks}"

        if business_scenario not in valid_scenarios:
            return f"Error: Invalid business scenario. Valid options: {valid_scenarios}"

        # 构建模板文件路径
        base_template = os.path.join(COMPOSE_TEMPLATES_PATH, "base-infrastructure.yml")
        attack_template = os.path.join(COMPOSE_TEMPLATES_PATH, "attack-modules", f"{attack_type}-attack.yml")
        business_template = os.path.join(COMPOSE_TEMPLATES_PATH, "business-scenarios", f"{business_scenario}.yml")

        # 检查模板文件是否存在
        templates_to_merge = []

        if os.path.exists(base_template):
            templates_to_merge.append(base_template)
        else:
            # 如果没有基础模板，使用现有的company-topology作为基础
            fallback_template = os.path.join(COMPOSE_TEMPLATES_PATH, "company-topology.yml")
            if os.path.exists(fallback_template):
                templates_to_merge.append(fallback_template)

        if os.path.exists(attack_template):
            templates_to_merge.append(attack_template)

        if os.path.exists(business_template):
            templates_to_merge.append(business_template)

        if not templates_to_merge:
            return f"Error: No valid templates found for {attack_type} + {business_scenario}"

        # 合并Docker Compose文件
        merged_compose = merge_compose_files(templates_to_merge, custom_config)

        # 生成唯一的文件名
        scenario_name = f"{attack_type}-{business_scenario}-{hash(str(custom_config)) % 10000}"
        output_file = os.path.join(COMPOSE_TEMPLATES_PATH, f"generated-{scenario_name}.yml")

        # 写入合并后的文件
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(merged_compose, f, default_flow_style=False, allow_unicode=True)

        return json.dumps({
            "status": "success",
            "scenario_name": scenario_name,
            "attack_type": attack_type,
            "business_scenario": business_scenario,
            "compose_file": output_file,
            "services_count": len(merged_compose.get("services", {})),
            "networks_count": len(merged_compose.get("networks", {})),
            "message": f"成功生成 {attack_type} 攻击的 {business_scenario} 业务场景"
        })

    except Exception as e:
        return f"Error generating scenario: {str(e)}"

def merge_compose_files(template_files: List[str], custom_config: dict = None) -> dict:
    """
    合并多个Docker Compose文件

    Args:
        template_files: 要合并的模板文件列表
        custom_config: 自定义配置参数

    Returns:
        合并后的Docker Compose配置字典
    """
    merged = {
        "version": "3.8",
        "services": {},
        "networks": {},
        "volumes": {}
    }

    for template_file in template_files:
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = yaml.safe_load(f)

            # 合并services
            if "services" in template_data:
                merged["services"].update(template_data["services"])

            # 合并networks
            if "networks" in template_data:
                merged["networks"].update(template_data["networks"])

            # 合并volumes
            if "volumes" in template_data:
                merged["volumes"].update(template_data["volumes"])

        except Exception as e:
            print(f"Warning: Failed to merge template {template_file}: {e}")

    # 应用自定义配置
    if custom_config:
        apply_custom_config(merged, custom_config)

    # 清理空的sections
    merged = {k: v for k, v in merged.items() if v}

    return merged

def apply_custom_config(compose_data: dict, custom_config: dict):
    """
    应用自定义配置到Docker Compose数据

    Args:
        compose_data: Docker Compose配置字典
        custom_config: 自定义配置参数
    """
    # 示例：修改服务的环境变量
    if "environment_overrides" in custom_config:
        for service_name, env_vars in custom_config["environment_overrides"].items():
            if service_name in compose_data["services"]:
                if "environment" not in compose_data["services"][service_name]:
                    compose_data["services"][service_name]["environment"] = []

                # 添加或更新环境变量
                for key, value in env_vars.items():
                    compose_data["services"][service_name]["environment"].append(f"{key}={value}")

    # 示例：修改端口映射
    if "port_overrides" in custom_config:
        for service_name, ports in custom_config["port_overrides"].items():
            if service_name in compose_data["services"]:
                compose_data["services"][service_name]["ports"] = ports

@mcp.tool
def parse_apt_ready_scenario() -> str:
    """
    解析apt-ready.yml场景文件，提取拓扑结构信息

    Returns:
        包含拓扑结构的JSON字符串，包括节点、网络和连接信息
    """
    try:
        # apt-ready.yml文件路径
        apt_ready_path = os.path.join(COMPOSE_TEMPLATES_PATH, "generated", "apt-ready.yml")

        if not os.path.exists(apt_ready_path):
            return json.dumps({
                "error": f"apt-ready.yml文件不存在: {apt_ready_path}"
            })

        # 读取并解析YAML文件
        with open(apt_ready_path, 'r', encoding='utf-8') as f:
            compose_data = yaml.safe_load(f)

        # 提取拓扑结构信息
        topology_data = extract_topology_from_compose(compose_data)

        return json.dumps({
            "status": "success",
            "scenario_name": "apt-ready",
            "description": "APT医疗场景 - 高级持续威胁攻击医疗机构",
            "topology": topology_data,
            "compose_file": apt_ready_path
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "error": f"解析apt-ready.yml失败: {str(e)}"
        })

def extract_topology_from_compose(compose_data: dict) -> dict:
    """
    从Docker Compose数据中提取拓扑结构信息

    Args:
        compose_data: Docker Compose配置字典

    Returns:
        拓扑结构字典，包含节点和网络信息
    """
    topology = {
        "nodes": [],
        "networks": [],
        "connections": []
    }

    services = compose_data.get("services", {})
    networks = compose_data.get("networks", {})

    # 提取网络信息
    for network_name, network_config in networks.items():
        subnet = ""
        if "ipam" in network_config and "config" in network_config["ipam"]:
            subnet = network_config["ipam"]["config"][0].get("subnet", "")

        topology["networks"].append({
            "id": network_name,
            "name": network_name,
            "subnet": subnet,
            "type": "network_segment"
        })

    # 提取服务节点信息
    for service_name, service_config in services.items():
        node = {
            "id": service_name,
            "name": service_name,
            "type": determine_node_type(service_name, service_config),
            "networks": [],
            "ip_addresses": {},
            "ports": service_config.get("ports", []),
            "environment": service_config.get("environment", []),
            "labels": service_config.get("labels", []),
            "status": "virtual"  # 初始状态为虚拟
        }

        # 提取网络连接信息
        service_networks = service_config.get("networks", {})
        for network_name, network_config in service_networks.items():
            node["networks"].append(network_name)
            if isinstance(network_config, dict) and "ipv4_address" in network_config:
                node["ip_addresses"][network_name] = network_config["ipv4_address"]

        topology["nodes"].append(node)

    # 生成连接关系（基于网络共享）
    topology["connections"] = generate_network_connections(topology["nodes"])

    return topology

def determine_node_type(service_name: str, service_config: dict) -> str:
    """
    根据服务名称和配置确定节点类型
    """
    name_lower = service_name.lower()

    # 根据服务名称判断类型
    if "firewall" in name_lower or "fw" in name_lower:
        return "firewall"
    elif "database" in name_lower or "db" in name_lower or "sql" in name_lower:
        return "database"
    elif "web" in name_lower or "apache" in name_lower or "wordpress" in name_lower:
        return "web_server"
    elif "dns" in name_lower:
        return "dns_server"
    elif "ws-" in name_lower or "workstation" in name_lower:
        return "workstation"
    elif "attacker" in name_lower:
        return "attacker"
    elif "vpn" in name_lower:
        return "vpn_server"
    elif "file" in name_lower:
        return "file_server"
    elif "syslog" in name_lower or "log" in name_lower:
        return "log_server"
    elif "update" in name_lower:
        return "update_server"
    elif "medical" in name_lower:
        return "medical_server"
    else:
        return "server"

def generate_network_connections(nodes: list) -> list:
    """
    基于网络共享生成节点间的连接关系
    """
    connections = []

    # 按网络分组节点
    network_groups = {}
    for node in nodes:
        for network in node["networks"]:
            if network not in network_groups:
                network_groups[network] = []
            network_groups[network].append(node["id"])

    # 在同一网络内的节点之间创建连接
    for network_name, node_ids in network_groups.items():
        for i, node1 in enumerate(node_ids):
            for node2 in node_ids[i+1:]:
                connections.append({
                    "id": f"{node1}-{node2}",
                    "source": node1,
                    "target": node2,
                    "network": network_name,
                    "type": "ethernet"
                })

    return connections

@mcp.tool
def get_scenario_topology_data(scenario_name: str = "apt-ready") -> str:
    """
    获取指定场景的拓扑数据，用于前端渲染

    Args:
        scenario_name: 场景名称，默认为apt-ready

    Returns:
        包含拓扑渲染数据的JSON字符串
    """
    try:
        if scenario_name == "apt-ready":
            return parse_apt_ready_scenario()
        else:
            return json.dumps({
                "error": f"不支持的场景: {scenario_name}"
            })

    except Exception as e:
        return json.dumps({
            "error": f"获取场景拓扑数据失败: {str(e)}"
        })

@mcp.tool
def generate_apt_medical_scenario(custom_config: dict = None) -> str:
    """
    生成APT医疗场景，基于apt-ready.yml模板

    Args:
        custom_config: 自定义配置参数

    Returns:
        生成的场景信息JSON字符串
    """
    try:
        # 使用现有的apt-ready.yml作为基础
        apt_ready_path = os.path.join(COMPOSE_TEMPLATES_PATH, "generated", "apt-ready.yml")

        if not os.path.exists(apt_ready_path):
            return json.dumps({
                "error": f"apt-ready.yml模板不存在: {apt_ready_path}"
            })

        # 读取模板
        with open(apt_ready_path, 'r', encoding='utf-8') as f:
            template_data = yaml.safe_load(f)

        # 应用自定义配置
        if custom_config:
            apply_custom_config(template_data, custom_config)

        # 生成新的场景文件
        scenario_name = f"apt-medical-{hash(str(custom_config)) % 10000}"
        output_file = os.path.join(COMPOSE_TEMPLATES_PATH, f"generated-{scenario_name}.yml")

        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(template_data, f, default_flow_style=False, allow_unicode=True)

        # 提取拓扑信息
        topology_data = extract_topology_from_compose(template_data)

        return json.dumps({
            "status": "success",
            "scenario_name": scenario_name,
            "attack_type": "apt",
            "business_scenario": "healthcare",
            "compose_file": output_file,
            "topology": topology_data,
            "services_count": len(template_data.get("services", {})),
            "networks_count": len(template_data.get("networks", {})),
            "message": "成功生成APT医疗攻击场景"
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "error": f"生成APT医疗场景失败: {str(e)}"
        })

@mcp.tool
def deploy_scenario_containers(scenario_file: str) -> str:
    """
    部署场景容器

    Args:
        scenario_file: Docker Compose文件路径

    Returns:
        部署结果JSON字符串
    """
    try:
        if not os.path.exists(scenario_file):
            return json.dumps({
                "error": f"场景文件不存在: {scenario_file}"
            })

        # 使用docker-compose启动容器
        result = subprocess.run(
            ["docker-compose", "-f", scenario_file, "up", "-d"],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            return json.dumps({
                "status": "success",
                "message": "容器部署成功",
                "stdout": result.stdout,
                "scenario_file": scenario_file
            })
        else:
            return json.dumps({
                "error": f"容器部署失败: {result.stderr}",
                "stdout": result.stdout
            })

    except subprocess.TimeoutExpired:
        return json.dumps({
            "error": "容器部署超时"
        })
    except Exception as e:
        return json.dumps({
            "error": f"部署容器时发生错误: {str(e)}"
        })


if __name__ == "__main__":
    mcp.run(transport="http", port=8002) 