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
    name="Scenario Service",
    description="Manages the lifecycle of attack-defense scenarios."
)

class ScenarioTemplate(BaseModel):
    name: str
    description: str
    version: str
    ports: list[str] = Field(default_factory=list)
    docker_compose_content: str | None = None

@mcp.tool
def list_scenario_templates() -> list[str]:
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

# To be implemented based on the plan
# @mcp.tool
# def deploy_environment(docker_compose_yaml: str) -> dict:
#     ...


if __name__ == "__main__":
    mcp.run(transport="http", port=8002) 