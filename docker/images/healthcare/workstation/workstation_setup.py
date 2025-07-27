#!/usr/bin/env python3
"""
Medical Workstation Setup Script
"""

import os
import subprocess

def setup_workstation():
    """Setup medical workstation environment"""
    print("Setting up medical workstation...")
    
    # Create desktop shortcuts
    desktop_dir = "/home/doctor/Desktop"
    os.makedirs(desktop_dir, exist_ok=True)
    
    # Create HIS shortcut
    his_shortcut = f"{desktop_dir}/HIS.desktop"
    with open(his_shortcut, 'w') as f:
        f.write("""[Desktop Entry]
Version=1.0
Type=Application
Name=Hospital Information System
Comment=Access HIS
Exec=firefox http://his.hospital.local
Icon=applications-internet
Terminal=false
""")
    
    # Create PACS shortcut
    pacs_shortcut = f"{desktop_dir}/PACS.desktop"
    with open(pacs_shortcut, 'w') as f:
        f.write("""[Desktop Entry]
Version=1.0
Type=Application
Name=PACS System
Comment=Medical Imaging
Exec=firefox http://pacs.hospital.local
Icon=applications-graphics
Terminal=false
""")
    
    print("Workstation setup complete!")

if __name__ == "__main__":
    setup_workstation()
