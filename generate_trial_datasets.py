"""
Generate 50 biased, 50 unbiased, and 25 mixed trial datasets
"""
import pandas as pd
import numpy as np
from pathlib import Path

def generate_unbiased_trial(trial_id, condition):
    """Generate an unbiased clinical trial"""
    n_participants = np.random.randint(120, 500)
    
    # Balanced demographics
    age_mean = np.random.uniform(45, 65)
    age_std = np.random.uniform(8, 15)
    ages = np.clip(np.random.normal(age_mean, age_std, n_participants), 18, 90)
    
    # Balanced gender (48-52%)
    gender_ratio = np.random.uniform(0.48, 0.52)
    genders = np.random.choice(['Male', 'Female'], n_participants, 
                              p=[gender_ratio, 1-gender_ratio])
    
    # Diverse ethnicity
    eth_probs = np.random.dirichlet([4, 3, 3, 2.5, 2])
    ethnicities = np.random.choice(['White', 'Black', 'Asian', 'Hispanic', 'Other'], 
                                  n_participants, p=eth_probs)
    
    # High eligibility scores
    eligibility_scores = np.random.uniform(0.85, 1.0, n_participants)
    
    df = pd.DataFrame({
        'age': ages,
        'gender': genders,
        'ethnicity': ethnicities,
        'eligibility_score': eligibility_scores
    })
    
    return df

def generate_biased_trial(trial_id, condition, bias_type=None):
    """Generate a biased clinical trial"""
    n_participants = np.random.randint(50, 300)
    
    if bias_type is None:
        bias_type = np.random.choice(['age', 'gender', 'ethnicity', 'sample'])
    
    if bias_type == 'age':
        # Very old or very young
        age_mean = np.random.choice([np.random.uniform(70, 85), np.random.uniform(18, 25)])
        age_std = np.random.uniform(3, 6)
        ages = np.clip(np.random.normal(age_mean, age_std, n_participants), 18, 90)
    else:
        ages = np.clip(np.random.normal(np.random.uniform(45, 65), np.random.uniform(8, 15), n_participants), 18, 90)
    
    if bias_type == 'gender':
        # Gender imbalance (70%+ one gender)
        gender_ratio = np.random.choice([0.75, 0.25])
        genders = np.random.choice(['Male', 'Female'], n_participants, 
                                  p=[gender_ratio, 1-gender_ratio])
    else:
        gender_ratio = np.random.uniform(0.48, 0.52)
        genders = np.random.choice(['Male', 'Female'], n_participants, 
                                  p=[gender_ratio, 1-gender_ratio])
    
    if bias_type == 'ethnicity':
        # Ethnicity imbalance (80%+ one ethnicity)
        eth_probs = np.array([0.85, 0.05, 0.05, 0.03, 0.02])
        np.random.shuffle(eth_probs)
        ethnicities = np.random.choice(['White', 'Black', 'Asian', 'Hispanic', 'Other'], 
                                      n_participants, p=eth_probs)
    else:
        eth_probs = np.random.dirichlet([4, 3, 3, 2.5, 2])
        ethnicities = np.random.choice(['White', 'Black', 'Asian', 'Hispanic', 'Other'], 
                                      n_participants, p=eth_probs)
    
    # Lower eligibility scores for biased trials
    eligibility_scores = np.random.uniform(0.4, 0.75, n_participants)
    
    # Very small sample for underpowered bias
    if bias_type == 'sample':
        n_participants = np.random.randint(15, 30)
        ages = np.clip(np.random.normal(np.random.uniform(45, 65), np.random.uniform(8, 15), n_participants), 18, 90)
        genders = np.random.choice(['Male', 'Female'], n_participants, p=[0.5, 0.5])
        ethnicities = np.random.choice(['White', 'Black', 'Asian', 'Hispanic', 'Other'], 
                                      n_participants, p=[0.4, 0.2, 0.2, 0.15, 0.05])
        eligibility_scores = np.random.uniform(0.5, 0.8, n_participants)
    
    df = pd.DataFrame({
        'age': ages,
        'gender': genders,
        'ethnicity': ethnicities,
        'eligibility_score': eligibility_scores
    })
    
    return df

def generate_mixed_trial(trial_id, condition):
    """Generate a mixed trial (some bias but not severe)"""
    n_participants = np.random.randint(100, 400)
    
    # Mild age skew or slight demographic imbalance
    age_mean = np.random.uniform(50, 70)
    age_std = np.random.uniform(6, 12)
    ages = np.clip(np.random.normal(age_mean, age_std, n_participants), 18, 90)
    
    # Slight gender imbalance (55-65% one gender)
    gender_ratio = np.random.choice([0.6, 0.4])
    genders = np.random.choice(['Male', 'Female'], n_participants, 
                              p=[gender_ratio, 1-gender_ratio])
    
    # Moderate ethnicity diversity (some imbalance but not extreme)
    eth_probs = np.array([0.6, 0.15, 0.12, 0.08, 0.05])
    np.random.shuffle(eth_probs)
    ethnicities = np.random.choice(['White', 'Black', 'Asian', 'Hispanic', 'Other'], 
                                  n_participants, p=eth_probs)
    
    # Moderate eligibility scores
    eligibility_scores = np.random.uniform(0.65, 0.85, n_participants)
    
    df = pd.DataFrame({
        'age': ages,
        'gender': genders,
        'ethnicity': ethnicities,
        'eligibility_score': eligibility_scores
    })
    
    return df

def main():
    np.random.seed(42)
    
    conditions = [
        'Diabetes', 'Hypertension', 'Cardiovascular_Disease', 'Asthma', 'Chronic_Pain',
        'Depression', 'Anxiety', 'Arthritis', 'Osteoporosis', 'Migraine',
        'Epilepsy', 'Parkinsons_Disease', 'Alzheimers_Disease', 'COPD', 'Kidney_Disease',
        'Liver_Disease', 'Inflammatory_Bowel_Disease', 'Psoriasis', 'Multiple_Sclerosis',
        'Lupus', 'Rheumatoid_Arthritis', 'Obesity', 'High_Cholesterol', 'Sleep_Disorders',
        'Gastroesophageal_Reflux_Disease', 'Cancer', 'Stroke', 'Heart_Failure',
        'Chronic_Kidney_Disease', 'Atrial_Fibrillation', 'Osteoarthritis', 'Fibromyalgia',
        'Crohns_Disease', 'Ulcerative_Colitis', 'Irritable_Bowel_Syndrome', 'Gout',
        'Rheumatoid_Arthritis', 'Sjogrens_Syndrome', 'Polymyalgia_Rheumatica', 'Osteopenia',
        'Hypertension_Stage_1', 'Hypertension_Stage_2', 'Pre_Diabetes', 'Metabolic_Syndrome',
        'Chronic_Fatigue_Syndrome', 'Restless_Legs_Syndrome', 'Insomnia', 'Sleep_Apnea',
        'Chronic_Back_Pain', 'Neuropathy', 'Fibromyalgia'
    ]
    
    # Create directories
    unbiased_dir = Path('trials/unbiased_trials')
    biased_dir = Path('trials/biased_trials')
    mixed_dir = Path('trials/mixed_trials')
    
    unbiased_dir.mkdir(parents=True, exist_ok=True)
    biased_dir.mkdir(parents=True, exist_ok=True)
    mixed_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate 50 unbiased trials
    print("Generating 50 unbiased trials...")
    for i in range(50):
        condition = conditions[i % len(conditions)]
        df = generate_unbiased_trial(i+1, condition)
        filename = f"trial_{i+1:02d}_{condition}_unbiased.csv"
        df.to_csv(unbiased_dir / filename, index=False)
    
    # Generate 50 biased trials
    print("Generating 50 biased trials...")
    bias_types = ['age', 'gender', 'ethnicity', 'sample']
    for i in range(50):
        condition = conditions[i % len(conditions)]
        bias_type = bias_types[i % len(bias_types)]
        df = generate_biased_trial(i+1, condition, bias_type)
        filename = f"trial_{i+1:02d}_{condition}_biased.csv"
        df.to_csv(biased_dir / filename, index=False)
    
    # Generate 25 mixed trials
    print("Generating 25 mixed trials...")
    for i in range(25):
        condition = conditions[i % len(conditions)]
        df = generate_mixed_trial(i+1, condition)
        filename = f"trial_{i+1:02d}_{condition}_mixed.csv"
        df.to_csv(mixed_dir / filename, index=False)
    
    print("\n✅ All trial datasets generated successfully!")
    print(f"   - 50 unbiased trials in: {unbiased_dir}")
    print(f"   - 50 biased trials in: {biased_dir}")
    print(f"   - 25 mixed trials in: {mixed_dir}")

if __name__ == "__main__":
    main()

