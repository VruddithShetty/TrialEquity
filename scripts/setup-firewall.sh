#!/bin/bash

# Firewall setup script for production server

set -e

echo "Setting up firewall rules..."

# Check if UFW is installed
if ! command -v ufw &> /dev/null; then
    echo "UFW is not installed. Installing..."
    apt-get update
    apt-get install -y ufw
fi

# Reset UFW to defaults
ufw --force reset

# Set default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (important - do this first!)
echo "Allowing SSH..."
ufw allow 22/tcp comment 'SSH'

# Allow HTTP and HTTPS
echo "Allowing HTTP and HTTPS..."
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Allow specific services (if needed)
# Uncomment and modify as needed:
# ufw allow from 10.0.0.0/8 to any port 5432 comment 'PostgreSQL from internal network'
# ufw allow from 10.0.0.0/8 to any port 6379 comment 'Redis from internal network'

# Enable firewall
echo "Enabling firewall..."
ufw --force enable

# Show status
echo ""
echo "Firewall status:"
ufw status verbose

echo ""
echo "✅ Firewall configured successfully!"
echo ""
echo "⚠️  IMPORTANT: Make sure SSH (port 22) is accessible before closing this session!"

