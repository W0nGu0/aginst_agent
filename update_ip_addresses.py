#!/usr/bin/env python3
"""
批量更新IP地址脚本
将199.203.100网段改为172.203.100网段
"""

import os
import re
from pathlib import Path

def update_ip_in_file(file_path, old_pattern, new_pattern):
    """更新文件中的IP地址"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换IP地址
        updated_content = re.sub(old_pattern, new_pattern, content)
        
        if content != updated_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✅ 已更新: {file_path}")
            return True
        else:
            print(f"⏸️ 无需更新: {file_path}")
            return False
    except Exception as e:
        print(f"❌ 更新失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    print("🔄 批量更新IP地址：199.203.100 -> 172.203.100")
    print("=" * 60)
    
    # 需要更新的文件列表
    files_to_update = [
        "docker/compose-templates/company-topology.yml",
        "docker/compose-templates/base-infrastructure.yml", 
        "docker/compose-templates/generated-phishing-education-8456.yml",
        "docker/compose-templates/modules/attack-modules/phishing-attack.yml",
        "docker/compose-templates/modules/attack-modules/ransomware-attack.yml",
        "services/scenario_service/main.py",
        "test_fixes.py"
    ]
    
    # IP地址替换规则
    replacements = [
        (r'199\.203\.100\.(\d+)', r'172.203.100.\1'),  # 替换具体IP
        (r'199\.203\.100\.0/24', r'172.203.100.0/24'),  # 替换子网
        (r'gateway: 199\.203\.100\.1', r'gateway: 172.203.100.1'),  # 替换网关
    ]
    
    updated_count = 0
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            print(f"\n📁 处理文件: {file_path}")
            file_updated = False
            
            for old_pattern, new_pattern in replacements:
                if update_ip_in_file(file_path, old_pattern, new_pattern):
                    file_updated = True
            
            if file_updated:
                updated_count += 1
        else:
            print(f"⚠️ 文件不存在: {file_path}")
    
    print(f"\n🎉 更新完成！共更新了 {updated_count} 个文件")
    
    # 验证更新结果
    print("\n🔍 验证更新结果...")
    remaining_files = []
    
    for root, dirs, files in os.walk("."):
        # 跳过一些目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
        
        for file in files:
            if file.endswith(('.yml', '.yaml', '.py', '.js', '.vue', '.html')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if '199.203.100.' in content:
                        remaining_files.append(file_path)
                except:
                    pass
    
    if remaining_files:
        print("⚠️ 以下文件仍包含旧IP地址:")
        for file_path in remaining_files:
            print(f"   - {file_path}")
    else:
        print("✅ 所有文件已成功更新！")

if __name__ == "__main__":
    main()