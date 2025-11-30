"""
Synthetic Clinical Trial Data Generator
Generates biased and unbiased datasets for ML model training
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json

class SyntheticTrialGenerator:
    """Generate synthetic clinical trial datasets with configurable bias"""
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
    
    def generate_unbiased_trial(
        self, n_participants: int = 200, trial_id: Optional[str] = None
    ) -> Dict:
        """Generate an unbiased, fair clinical trial dataset"""
        trial_id = trial_id or f"TRIAL_{np.random.randint(10000, 99999)}"
        
        # Age distribution (normal, balanced)
        ages = np.random.normal(55, 15, n_participants)
        ages = np.clip(ages, 18, 90)
        
        # Gender distribution (balanced)
        genders = np.random.choice(['Male', 'Female'], n_participants, p=[0.5, 0.5])
        
        # Ethnicity distribution (diverse)
        ethnicities = np.random.choice(
            ['White', 'Black', 'Asian', 'Hispanic', 'Other'],
            n_participants,
            p=[0.4, 0.2, 0.2, 0.15, 0.05]
        )
        
        # Eligibility scores (high, indicating good eligibility)
        eligibility_scores = np.random.uniform(0.75, 1.0, n_participants)
        
        # Create DataFrame
        df = pd.DataFrame({
            'participant_id': range(1, n_participants + 1),
            'age': ages,
            'gender': genders,
            'ethnicity': ethnicities,
            'eligibility_score': eligibility_scores,
        })
        
        return {
            'trial_id': trial_id,
            'participant_count': n_participants,
            'bias_type': 'unbiased',
            'age_distribution': {
                'mean': float(np.mean(ages)),
                'std': float(np.std(ages)),
                'min': float(np.min(ages)),
                'max': float(np.max(ages)),
            },
            'gender_distribution': {
                'male': float(np.sum(genders == 'Male') / n_participants),
                'female': float(np.sum(genders == 'Female') / n_participants),
            },
            'ethnicity_distribution': {
                'white': float(np.sum(ethnicities == 'White') / n_participants),
                'black': float(np.sum(ethnicities == 'Black') / n_participants),
                'asian': float(np.sum(ethnicities == 'Asian') / n_participants),
                'hispanic': float(np.sum(ethnicities == 'Hispanic') / n_participants),
                'other': float(np.sum(ethnicities == 'Other') / n_participants),
            },
            'sample_size': n_participants,
            'eligibility_score': float(np.mean(eligibility_scores)),
            'data': df.to_dict('records'),
        }
    
    def generate_age_skewed_trial(
        self, n_participants: int = 200, trial_id: Optional[str] = None
    ) -> Dict:
        """Generate a trial with age group bias (skewed toward elderly)"""
        trial_id = trial_id or f"TRIAL_AGE_BIAS_{np.random.randint(10000, 99999)}"
        
        # Age distribution (skewed toward elderly)
        ages = np.random.normal(70, 8, n_participants)
        ages = np.clip(ages, 18, 90)
        
        # Gender distribution (slightly imbalanced)
        genders = np.random.choice(['Male', 'Female'], n_participants, p=[0.6, 0.4])
        
        # Ethnicity distribution (less diverse)
        ethnicities = np.random.choice(
            ['White', 'Black', 'Asian', 'Hispanic', 'Other'],
            n_participants,
            p=[0.7, 0.15, 0.1, 0.04, 0.01]
        )
        
        eligibility_scores = np.random.uniform(0.6, 0.9, n_participants)
        
        df = pd.DataFrame({
            'participant_id': range(1, n_participants + 1),
            'age': ages,
            'gender': genders,
            'ethnicity': ethnicities,
            'eligibility_score': eligibility_scores,
        })
        
        return {
            'trial_id': trial_id,
            'participant_count': n_participants,
            'bias_type': 'age_skewed',
            'age_distribution': {
                'mean': float(np.mean(ages)),
                'std': float(np.std(ages)),
                'min': float(np.min(ages)),
                'max': float(np.max(ages)),
            },
            'gender_distribution': {
                'male': float(np.sum(genders == 'Male') / n_participants),
                'female': float(np.sum(genders == 'Female') / n_participants),
            },
            'ethnicity_distribution': {
                'white': float(np.sum(ethnicities == 'White') / n_participants),
                'black': float(np.sum(ethnicities == 'Black') / n_participants),
                'asian': float(np.sum(ethnicities == 'Asian') / n_participants),
                'hispanic': float(np.sum(ethnicities == 'Hispanic') / n_participants),
                'other': float(np.sum(ethnicities == 'Other') / n_participants),
            },
            'sample_size': n_participants,
            'eligibility_score': float(np.mean(eligibility_scores)),
            'data': df.to_dict('records'),
        }
    
    def generate_demographic_imbalanced_trial(
        self, n_participants: int = 200, trial_id: Optional[str] = None
    ) -> Dict:
        """Generate a trial with demographic imbalance"""
        trial_id = trial_id or f"TRIAL_DEMO_BIAS_{np.random.randint(10000, 99999)}"
        
        ages = np.random.normal(55, 15, n_participants)
        ages = np.clip(ages, 18, 90)
        
        # Highly imbalanced gender
        genders = np.random.choice(['Male', 'Female'], n_participants, p=[0.85, 0.15])
        
        # Highly imbalanced ethnicity
        ethnicities = np.random.choice(
            ['White', 'Black', 'Asian', 'Hispanic', 'Other'],
            n_participants,
            p=[0.9, 0.05, 0.03, 0.01, 0.01]
        )
        
        eligibility_scores = np.random.uniform(0.5, 0.8, n_participants)
        
        df = pd.DataFrame({
            'participant_id': range(1, n_participants + 1),
            'age': ages,
            'gender': genders,
            'ethnicity': ethnicities,
            'eligibility_score': eligibility_scores,
        })
        
        return {
            'trial_id': trial_id,
            'participant_count': n_participants,
            'bias_type': 'demographic_imbalanced',
            'age_distribution': {
                'mean': float(np.mean(ages)),
                'std': float(np.std(ages)),
                'min': float(np.min(ages)),
                'max': float(np.max(ages)),
            },
            'gender_distribution': {
                'male': float(np.sum(genders == 'Male') / n_participants),
                'female': float(np.sum(genders == 'Female') / n_participants),
            },
            'ethnicity_distribution': {
                'white': float(np.sum(ethnicities == 'White') / n_participants),
                'black': float(np.sum(ethnicities == 'Black') / n_participants),
                'asian': float(np.sum(ethnicities == 'Asian') / n_participants),
                'hispanic': float(np.sum(ethnicities == 'Hispanic') / n_participants),
                'other': float(np.sum(ethnicities == 'Other') / n_participants),
            },
            'sample_size': n_participants,
            'eligibility_score': float(np.mean(eligibility_scores)),
            'data': df.to_dict('records'),
        }
    
    def generate_underpowered_trial(
        self, n_participants: int = 20, trial_id: Optional[str] = None
    ) -> Dict:
        """Generate an underpowered trial (too few participants)"""
        return self.generate_unbiased_trial(n_participants, trial_id or f"TRIAL_UNDERPOWERED_{np.random.randint(10000, 99999)}")
    
    def save_to_csv(self, trial_data: Dict, filepath: str):
        """Save trial data to CSV file"""
        df = pd.DataFrame(trial_data['data'])
        df.to_csv(filepath, index=False)
        print(f"Saved trial {trial_data['trial_id']} to {filepath}")
    
    def save_to_json(self, trial_data: Dict, filepath: str):
        """Save trial metadata to JSON file"""
        metadata = {k: v for k, v in trial_data.items() if k != 'data'}
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"Saved metadata to {filepath}")

if __name__ == "__main__":
    generator = SyntheticTrialGenerator()
    
    # Generate various trial types
    print("Generating synthetic clinical trial datasets...")
    
    # Unbiased trial
    unbiased = generator.generate_unbiased_trial(200)
    generator.save_to_csv(unbiased, "unbiased_trial.csv")
    generator.save_to_json(unbiased, "unbiased_trial_metadata.json")
    
    # Age-skewed trial
    age_skewed = generator.generate_age_skewed_trial(200)
    generator.save_to_csv(age_skewed, "age_skewed_trial.csv")
    generator.save_to_json(age_skewed, "age_skewed_trial_metadata.json")
    
    # Demographically imbalanced trial
    demo_imbalanced = generator.generate_demographic_imbalanced_trial(200)
    generator.save_to_csv(demo_imbalanced, "demo_imbalanced_trial.csv")
    generator.save_to_json(demo_imbalanced, "demo_imbalanced_trial_metadata.json")
    
    # Underpowered trial
    underpowered = generator.generate_underpowered_trial(20)
    generator.save_to_csv(underpowered, "underpowered_trial.csv")
    generator.save_to_json(underpowered, "underpowered_trial_metadata.json")
    
    print("\nAll synthetic datasets generated successfully!")

