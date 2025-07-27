#!/usr/bin/env python3
"""
Docker Compose模板合并工具
用于将基础设施模板与攻击模块和业务场景模块合并
"""

import yaml
import os
import sys
from pathlib import Path

def load_yaml_file(file_path):
    """加载YAML文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def merge_compose_files(base_file, attack_module=None, business_scenario=None, output_file=None):
    """
    合并Docker Compose文件
    
    Args:
        base_file: 基础设施文件路径
        attack_module: 攻击模块文件路径
        business_scenario: 业务场景文件路径
        output_file: 输出文件路径
    """
    
    # 加载基础文件
    base_data = load_yaml_file(base_file)
    if not base_data:
        return False
    
    merged_data = base_data.copy()
    
    # 合并攻击模块
    if attack_module and os.path.exists(attack_module):
        attack_data = load_yaml_file(attack_module)
        if attack_data:
            print(f"Merging attack module: {attack_module}")
            
            # 合并services
            if 'services' in attack_data:
                if 'services' not in merged_data:
                    merged_data['services'] = {}
                merged_data['services'].update(attack_data['services'])
            
            # 合并networks
            if 'networks' in attack_data:
                if 'networks' not in merged_data:
                    merged_data['networks'] = {}
                merged_data['networks'].update(attack_data['networks'])
            
            # 合并volumes
            if 'volumes' in attack_data:
                if 'volumes' not in merged_data:
                    merged_data['volumes'] = {}
                merged_data['volumes'].update(attack_data['volumes'])
    
    # 合并业务场景
    if business_scenario and os.path.exists(business_scenario):
        business_data = load_yaml_file(business_scenario)
        if business_data:
            print(f"Merging business scenario: {business_scenario}")
            
            # 合并services
            if 'services' in business_data:
                if 'services' not in merged_data:
                    merged_data['services'] = {}
                merged_data['services'].update(business_data['services'])
            
            # 合并networks
            if 'networks' in business_data:
                if 'networks' not in merged_data:
                    merged_data['networks'] = {}
                merged_data['networks'].update(business_data['networks'])
            
            # 合并volumes
            if 'volumes' in business_data:
                if 'volumes' not in merged_data:
                    merged_data['volumes'] = {}
                merged_data['volumes'].update(business_data['volumes'])
    
    # 输出合并结果
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(merged_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            print(f"Merged compose file saved to: {output_file}")
            return True
        except Exception as e:
            print(f"Error saving merged file: {e}")
            return False
    else:
        # 输出到控制台
        print(yaml.dump(merged_data, default_flow_style=False, allow_unicode=True, sort_keys=False))
        return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python merge_templates.py <scenario_type>")
        print("Available scenarios:")
        print("  apt-healthcare    - APT攻击 + 医疗场景")
        print("  phishing-finance  - 钓鱼攻击 + 金融场景")
        print("  ransomware-healthcare - 勒索软件 + 医疗场景")
        return
    
    scenario_type = sys.argv[1]
    
    # 定义文件路径
    base_dir = Path(__file__).parent
    base_file = base_dir / "base-infrastructure.yml"
    generated_dir = base_dir / "generated"
    
    # 确保生成目录存在
    generated_dir.mkdir(exist_ok=True)
    
    # 根据场景类型选择模块
    scenarios = {
        "apt-healthcare": {
            "attack": base_dir / "modules/attack-modules/apt-attack.yml",
            "business": base_dir / "modules/business-scenarios/healthcare.yml",
            "output": generated_dir / "apt-healthcare-scenario.yml"
        },
        "phishing-finance": {
            "attack": base_dir / "modules/attack-modules/phishing-attack.yml",
            "business": base_dir / "modules/business-scenarios/finance.yml",
            "output": generated_dir / "phishing-finance-scenario.yml"
        },
        "ransomware-healthcare": {
            "attack": base_dir / "modules/attack-modules/ransomware-attack.yml",
            "business": base_dir / "modules/business-scenarios/healthcare.yml",
            "output": generated_dir / "ransomware-healthcare-scenario.yml"
        }
    }
    
    if scenario_type not in scenarios:
        print(f"Unknown scenario type: {scenario_type}")
        return
    
    config = scenarios[scenario_type]
    
    # 执行合并
    success = merge_compose_files(
        base_file=base_file,
        attack_module=config["attack"],
        business_scenario=config["business"],
        output_file=config["output"]
    )
    
    if success:
        print(f"\n✅ Successfully created scenario: {scenario_type}")
        print(f"📁 Output file: {config['output']}")
        print(f"\n🚀 To start the scenario, run:")
        print(f"   docker-compose -f {config['output']} up -d")
    else:
        print(f"\n❌ Failed to create scenario: {scenario_type}")

if __name__ == "__main__":
    main()
