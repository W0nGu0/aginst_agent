# Added comment for test
import os
from fastapi import FastAPI
from fastmcp import FastMCP
from pydantic import BaseModel, Field
import subprocess
import yaml

# Define the path to the scenario library relative to this script
SCENARIO_LIBRARY_PATH = os.path.join(os.path.dirname(__file__), "scenario_library")

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

# To be implemented based on the plan
# @mcp.tool
# def deploy_environment(docker_compose_yaml: str) -> dict:
#     ...


if __name__ == "__main__":
    mcp.run(transport="http", port=8002) 