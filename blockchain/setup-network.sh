#!/bin/bash

# Hyperledger Fabric Network Setup Script
# This script sets up a basic Fabric network for clinical trials

set -e

echo "Setting up Hyperledger Fabric network for Clinical Trials..."

# Check if Fabric binaries are installed
if [ ! -d "fabric-samples" ]; then
    echo "Downloading Fabric samples..."
    curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.5.0 1.5.0
fi

# Navigate to test network
cd fabric-samples/test-network

# Create network
echo "Creating network..."
./network.sh up createChannel -c clinicaltrials -ca

# Deploy chaincode
echo "Deploying chaincode..."
./network.sh deployCC -ccn trialchain -ccp ../../chaincode/trialchain -ccl go

echo "Network setup complete!"
echo "To interact with the network, use the peer CLI or SDK"

