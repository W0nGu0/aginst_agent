#!/bin/bash

# Medical Workstation Startup Script

echo "Starting Medical Workstation..."

# Start VNC server
vncserver :1 -geometry 1024x768 -depth 24

# Start medical client application
cd /opt/workstation
python3 medical_client.py &

# Keep container running
tail -f /dev/null
