#!/usr/bin/env python3
"""
Script to train production ML model with >95% accuracy
Run this before deploying to production
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ml_bias_detection_production import MLBiasDetector

def main():
    print("=" * 60)
    print("PRODUCTION ML MODEL TRAINING")
    print("Target: >95% Accuracy")
    print("=" * 60)
    print()
    
    # Initialize detector (will train if models don't exist)
    detector = MLBiasDetector(model_dir="backend/models")
    
    # Verify accuracy
    if detector.model_accuracy >= 0.95:
        print("\n" + "=" * 60)
        print("✅ PRODUCTION READY!")
        print(f"   Model Accuracy: {detector.model_accuracy*100:.2f}%")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("⚠️  WARNING: Model accuracy below 95%")
        print(f"   Current Accuracy: {detector.model_accuracy*100:.2f}%")
        print("   Consider retraining with more data or tuning")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    exit(main())

