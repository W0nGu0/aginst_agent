#!/bin/bash

# Medical File Server Startup Script

echo "Starting Medical File Server..."

# Start SSH service
service ssh start

# Start Apache
service apache2 start

# Set proper ownership and permissions
chown -R www-data:www-data /var/www/html/
chmod -R 755 /var/www/html/

# Keep container running
echo "Medical File Server started successfully!"
echo "Web Interface: http://localhost"
echo "SSH Access: ssh fileadmin@localhost (password: files123)"

# Keep the container running
while true; do
    sleep 30
    # Check if services are running
    if ! pgrep apache2 > /dev/null; then
        echo "Apache2 stopped, restarting..."
        service apache2 start
    fi
    if ! pgrep sshd > /dev/null; then
        echo "SSH stopped, restarting..."
        service ssh start
    fi
done
