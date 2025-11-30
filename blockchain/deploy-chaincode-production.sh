#!/bin/bash

# Deploy chaincode to production network

set -e

CHAINCODE_NAME="trialchain"
CHAINCODE_VERSION="1.0"
CHAINCODE_PATH="./chaincode/trialchain"
CHANNEL_NAME="clinicaltrials"

echo "Deploying chaincode to production network..."

# Package chaincode
echo "Packaging chaincode..."
docker exec cli peer lifecycle chaincode package ${CHAINCODE_NAME}.tar.gz \
    --path ${CHAINCODE_PATH} \
    --lang golang \
    --label ${CHAINCODE_NAME}_${CHAINCODE_VERSION}

# Install on all organizations
echo "Installing chaincode on all peers..."
for org in sponsor investigator regulator auditor; do
    for peer in 0 1; do
        echo "Installing on peer${peer}.${org}.example.com..."
        docker exec cli peer lifecycle chaincode install ${CHAINCODE_NAME}.tar.gz \
            --peerAddresses peer${peer}.${org}.example.com:7051 \
            --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/${org}.example.com/peers/peer${peer}.${org}.example.com/tls/ca.crt
    done
done

# Get package ID
PACKAGE_ID=$(docker exec cli peer lifecycle chaincode queryinstalled | grep -oP 'Package ID: \K[^,]+' | head -1)
echo "Package ID: $PACKAGE_ID"

# Approve for each organization
echo "Approving chaincode for organizations..."
for org in sponsor investigator regulator auditor; do
    docker exec cli peer lifecycle chaincode approveformyorg \
        -o orderer0.example.com:7050 \
        --channelID ${CHANNEL_NAME} \
        --name ${CHAINCODE_NAME} \
        --version ${CHAINCODE_VERSION} \
        --package-id ${PACKAGE_ID} \
        --sequence 1 \
        --tls \
        --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer0.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
        --peerAddresses peer0.${org}.example.com:7051 \
        --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/${org}.example.com/peers/peer0.${org}.example.com/tls/ca.crt
done

# Commit chaincode
echo "Committing chaincode..."
docker exec cli peer lifecycle chaincode commit \
    -o orderer0.example.com:7050 \
    --channelID ${CHANNEL_NAME} \
    --name ${CHAINCODE_NAME} \
    --version ${CHAINCODE_VERSION} \
    --sequence 1 \
    --tls \
    --cafile /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/ordererOrganizations/example.com/orderers/orderer0.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
    --peerAddresses peer0.sponsor.example.com:7051 \
    --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/sponsor.example.com/peers/peer0.sponsor.example.com/tls/ca.crt \
    --peerAddresses peer0.regulator.example.com:7051 \
    --tlsRootCertFiles /opt/gopath/src/github.com/hyperledger/fabric/peer/crypto/peerOrganizations/regulator.example.com/peers/peer0.regulator.example.com/tls/ca.crt

echo "✅ Chaincode deployed successfully!"

# Query chaincode
echo "Querying chaincode..."
docker exec cli peer chaincode query \
    -C ${CHANNEL_NAME} \
    -n ${CHAINCODE_NAME} \
    -c '{"Args":["GetAllTrials"]}'

