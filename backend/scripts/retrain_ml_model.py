"""
Script to force retrain the ML model with improved parameters
Run this to ensure the model is properly trained and saved
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ml_bias_detection_production import MLBiasDetector
import shutil
from pathlib import Path

def main():
    print("=" * 70)
    print("ML Model Retraining Script")
    print("This will delete existing models and train new ones")
    print("=" * 70)
    print()
    
    # Remove existing models to force retraining
    model_dir = Path("models")
    if model_dir.exists():
        print("🗑️  Removing existing models...")
        for file in model_dir.glob("*.pkl"):
            file.unlink()
            print(f"   Deleted: {file.name}")
        for file in model_dir.glob("*.json"):
            file.unlink()
            print(f"   Deleted: {file.name}")
    
    print()
    print("🔄 Starting model training with improved parameters...")
    print()
    
    # Initialize detector - this will train new models
    detector = MLBiasDetector()
    
    print()
    print("=" * 70)
    print("✅ Model training completed!")
    print(f"   Model Accuracy: {detector.model_accuracy:.2%}")
    print(f"   Models saved to: {model_dir.absolute()}")
    print()
    print("The model is now ready to use and should provide accurate results")
    print("for unbiased trials (expecting ACCEPT status with 80-90% fairness scores)")
    print("=" * 70)

if __name__ == "__main__":
    main()

