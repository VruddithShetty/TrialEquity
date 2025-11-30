#!/bin/bash

# Generate cryptographic materials for Hyperledger Fabric network

set -e

echo "Generating cryptographic materials for production network..."

# Create crypto-config directory
mkdir -p crypto-config

# Generate crypto materials using cryptogen
if [ -f "fabric-samples/bin/cryptogen" ]; then
    ./fabric-samples/bin/cryptogen generate --config=./crypto-config.yaml
else
    echo "Error: cryptogen not found. Please install Fabric samples first."
    exit 1
fi

echo "✅ Cryptographic materials generated successfully!"
echo "Location: ./crypto-config/"

