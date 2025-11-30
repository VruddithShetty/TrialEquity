#!/bin/bash

# Start production Hyperledger Fabric network

set -e

echo "Starting production Hyperledger Fabric network..."

# Generate genesis block
if [ ! -f "channel-artifacts/genesis.block" ]; then
    echo "Generating genesis block..."
    ./fabric-samples/bin/configtxgen \
        -profile ClinicalTrialsOrdererGenesis \
        -channelID system-channel \
        -outputBlock ./channel-artifacts/genesis.block \
        -configPath .
fi

# Generate channel configuration
if [ ! -f "channel-artifacts/channel.tx" ]; then
    echo "Generating channel configuration..."
    ./fabric-samples/bin/configtxgen \
        -profile ClinicalTrialsChannel \
        -outputCreateChannelTx ./channel-artifacts/channel.tx \
        -channelID clinicaltrials \
        -configPath .
fi

# Start network using docker-compose
echo "Starting network containers..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for network to be ready
echo "Waiting for network to be ready..."
sleep 30

# Create channel
echo "Creating channel..."
docker exec cli peer channel create \
    -o orderer0.example.com:7050 \
    -c clinicaltrials \
    -f ./channel-artifacts/channel.tx \
    --tls \
    --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer0.example.com/msp/tlscacerts/tlsca.example.com-cert.pem

# Join peers to channel
echo "Joining peers to channel..."
for org in sponsor investigator regulator auditor; do
    for peer in 0 1; do
        docker exec cli peer channel join \
            -b clinicaltrials.block \
            --tls \
            --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer0.example.com/msp/tlscacerts/tlsca.example.com-cert.pem
    done
done

echo "✅ Production network started successfully!"
echo "Network status:"
docker-compose -f docker-compose.prod.yml ps

