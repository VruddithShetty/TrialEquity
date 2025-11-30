/*
SPDX-License-Identifier: Apache-2.0
*/

package main

import (
	"encoding/json"
	"fmt"
	"strconv"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// TrialChain contract for managing clinical trials
type TrialChain struct {
	contractapi.Contract
}

// Trial represents a clinical trial record on the blockchain
type Trial struct {
	TrialID        string    `json:"trial_id"`
	Hash           string    `json:"hash"`
	ParticipantCount int     `json:"participant_count"`
	MLStatus       string    `json:"ml_status"`
	FairnessScore  float64   `json:"fairness_score"`
	Timestamp      time.Time `json:"timestamp"`
	UploadedBy     string    `json:"uploaded_by"`
	Metadata       string    `json:"metadata"`
}

// CreateTrial creates a new trial record on the blockchain
func (tc *TrialChain) CreateTrial(ctx contractapi.TransactionContextInterface, trialID string, hash string, participantCount int, mlStatus string, fairnessScore float64, uploadedBy string, metadata string) error {
	// Check if trial already exists
	trialJSON, err := ctx.GetStub().GetState(trialID)
	if err != nil {
		return fmt.Errorf("failed to read from world state: %v", err)
	}
	if trialJSON != nil {
		return fmt.Errorf("trial %s already exists", trialID)
	}

	// Create new trial
	trial := Trial{
		TrialID:         trialID,
		Hash:            hash,
		ParticipantCount: participantCount,
		MLStatus:        mlStatus,
		FairnessScore:   fairnessScore,
		Timestamp:       time.Now(),
		UploadedBy:      uploadedBy,
		Metadata:        metadata,
	}

	trialJSON, err = json.Marshal(trial)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(trialID, trialJSON)
}

// GetTrial retrieves a trial from the blockchain
func (tc *TrialChain) GetTrial(ctx contractapi.TransactionContextInterface, trialID string) (*Trial, error) {
	trialJSON, err := ctx.GetStub().GetState(trialID)
	if err != nil {
		return nil, fmt.Errorf("failed to read from world state: %v", err)
	}
	if trialJSON == nil {
		return nil, fmt.Errorf("trial %s does not exist", trialID)
	}

	var trial Trial
	err = json.Unmarshal(trialJSON, &trial)
	if err != nil {
		return nil, err
	}

	return &trial, nil
}

// VerifyTrial verifies the integrity of a trial by checking its hash
func (tc *TrialChain) VerifyTrial(ctx contractapi.TransactionContextInterface, trialID string, providedHash string) (bool, error) {
	trial, err := tc.GetTrial(ctx, trialID)
	if err != nil {
		return false, err
	}

	return trial.Hash == providedHash, nil
}

// GetAllTrials returns all trials in the world state
func (tc *TrialChain) GetAllTrials(ctx contractapi.TransactionContextInterface) ([]*Trial, error) {
	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var trials []*Trial
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		var trial Trial
		err = json.Unmarshal(queryResponse.Value, &trial)
		if err != nil {
			return nil, err
		}
		trials = append(trials, &trial)
	}

	return trials, nil
}

// UpdateTrialStatus updates the ML status of a trial
func (tc *TrialChain) UpdateTrialStatus(ctx contractapi.TransactionContextInterface, trialID string, mlStatus string) error {
	trial, err := tc.GetTrial(ctx, trialID)
	if err != nil {
		return err
	}

	trial.MLStatus = mlStatus
	trialJSON, err := json.Marshal(trial)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(trialID, trialJSON)
}

func main() {
	trialChain, err := contractapi.NewChaincode(&TrialChain{})
	if err != nil {
		fmt.Printf("Error creating trialchain chaincode: %v", err)
		return
	}

	if err := trialChain.Start(); err != nil {
		fmt.Printf("Error starting trialchain chaincode: %v", err)
	}
}

