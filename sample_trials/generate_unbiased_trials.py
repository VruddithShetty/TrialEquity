"""
Generate 25 Unbiased Clinical Trial CSV Files
These trials are designed to pass 100% validation and ML bias checks
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

# Create output directory
output_dir = Path("sample_trials")
output_dir.mkdir(exist_ok=True)

# Define trial conditions for variety
trial_conditions = [
    "Diabetes Type 2",
    "Hypertension",
    "Cardiovascular Disease",
    "Asthma",
    "Chronic Pain",
    "Depression",
    "Anxiety",
    "Arthritis",
    "Osteoporosis",
    "Migraine",
    "Epilepsy",
    "Parkinson's Disease",
    "Alzheimer's Disease",
    "COPD",
    "Kidney Disease",
    "Liver Disease",
    "Inflammatory Bowel Disease",
    "Psoriasis",
    "Multiple Sclerosis",
    "Lupus",
    "Rheumatoid Arthritis",
    "Obesity",
    "High Cholesterol",
    "Sleep Disorders",
    "Gastroesophageal Reflux Disease"
]

# Ethnicity options
ethnicities = ["White", "Black", "Asian", "Hispanic", "Other"]
genders = ["Male", "Female"]

def generate_unbiased_trial(trial_num: int, condition: str, n_participants: int = None):
    """
    Generate an unbiased trial that will pass all validations
    
    Characteristics of unbiased trials:
    - Balanced gender distribution (48-52% each)
    - Diverse ethnicity (no single group > 45%)
    - Reasonable age distribution (mean 45-65, std 8-15)
    - Sample size >= 100
    - High eligibility scores (0.75-0.95)
    - No outliers
    """
    if n_participants is None:
        n_participants = np.random.randint(120, 500)  # Minimum 120 for good sample size
    
    # Generate balanced gender distribution (48-52% each)
    gender_ratio_male = np.random.uniform(0.48, 0.52)
    n_male = int(n_participants * gender_ratio_male)
    n_female = n_participants - n_male
    
    # Generate diverse ethnicity distribution
    # Ensure no single group dominates (>45%)
    white_ratio = np.random.uniform(0.25, 0.42)
    black_ratio = np.random.uniform(0.15, 0.25)
    asian_ratio = np.random.uniform(0.15, 0.25)
    hispanic_ratio = np.random.uniform(0.10, 0.20)
    other_ratio = 1.0 - (white_ratio + black_ratio + asian_ratio + hispanic_ratio)
    
    # Normalize to ensure sum = 1.0
    total = white_ratio + black_ratio + asian_ratio + hispanic_ratio + other_ratio
    white_ratio /= total
    black_ratio /= total
    asian_ratio /= total
    hispanic_ratio /= total
    other_ratio /= total
    
    # Calculate counts ensuring they sum to exactly n_participants
    n_white = int(n_participants * white_ratio)
    n_black = int(n_participants * black_ratio)
    n_asian = int(n_participants * asian_ratio)
    n_hispanic = int(n_participants * hispanic_ratio)
    n_other = n_participants - (n_white + n_black + n_asian + n_hispanic)
    
    # Ensure n_other is non-negative (adjust if needed due to rounding)
    if n_other < 0:
        # Redistribute the deficit
        deficit = -n_other
        n_other = 0
        # Subtract from largest group
        counts = [n_white, n_black, n_asian, n_hispanic]
        max_idx = np.argmax(counts)
        counts[max_idx] -= deficit
        n_white, n_black, n_asian, n_hispanic = counts
    
    # Generate reasonable age distribution (mean 45-65, std 8-15)
    age_mean = np.random.uniform(45, 65)
    age_std = np.random.uniform(8, 15)
    ages = np.random.normal(age_mean, age_std, n_participants)
    ages = np.clip(ages, 18, 90)  # Ensure valid age range
    
    # Generate high eligibility scores (0.75-0.95) - centered around 0.85
    eligibility_scores = np.random.normal(0.85, 0.08, n_participants)
    eligibility_scores = np.clip(eligibility_scores, 0.70, 1.0)  # Ensure >= 0.7 threshold
    
    # Create participants
    participants = []
    
    # Assign genders
    participant_genders = ["Male"] * n_male + ["Female"] * n_female
    np.random.shuffle(participant_genders)
    
    # Assign ethnicities
    participant_ethnicities = (
        ["White"] * n_white +
        ["Black"] * n_black +
        ["Asian"] * n_asian +
        ["Hispanic"] * n_hispanic +
        ["Other"] * n_other
    )
    np.random.shuffle(participant_ethnicities)
    
    # Create participant records
    for i in range(n_participants):
        participants.append({
            "participant_id": i + 1,
            "age": round(ages[i], 1),
            "gender": participant_genders[i],
            "ethnicity": participant_ethnicities[i],
            "eligibility_score": round(eligibility_scores[i], 3)
        })
    
    # Create DataFrame
    df = pd.DataFrame(participants)
    
    # Shuffle rows
    df = df.sample(frac=1).reset_index(drop=True)
    
    # Save to CSV
    filename = f"trial_{trial_num:02d}_{condition.replace(' ', '_').replace("'", '')}_unbiased.csv"
    filepath = output_dir / filename
    df.to_csv(filepath, index=False)
    
    # Print summary
    print(f"✅ Trial {trial_num:02d}: {condition}")
    print(f"   Participants: {n_participants}")
    print(f"   Gender: {n_male}M / {n_female}F ({gender_ratio_male*100:.1f}% male)")
    print(f"   Ethnicity: W:{n_white} B:{n_black} A:{n_asian} H:{n_hispanic} O:{n_other}")
    print(f"   Age: {ages.mean():.1f} ± {ages.std():.1f} (range: {ages.min():.1f}-{ages.max():.1f})")
    print(f"   Eligibility: {eligibility_scores.mean():.3f} ± {eligibility_scores.std():.3f}")
    print(f"   Saved: {filepath}\n")
    
    return filepath

def main():
    """Generate 25 unbiased trials"""
    print("=" * 70)
    print("Generating 25 Unbiased Clinical Trial CSV Files")
    print("These trials are designed to pass 100% validation and ML checks")
    print("=" * 70)
    print()
    
    # Generate 25 trials
    for i, condition in enumerate(trial_conditions, start=1):
        generate_unbiased_trial(i, condition)
    
    print("=" * 70)
    print(f"✅ Successfully generated 25 unbiased trial CSV files in '{output_dir}/'")
    print()
    print("Expected Results:")
    print("  ✓ All trials will pass validation (sample_size >= 100)")
    print("  ✓ All trials will have balanced demographics (gender 48-52%)")
    print("  ✓ All trials will have diverse ethnicity (no group > 45%)")
    print("  ✓ All trials will pass ML bias check (ACCEPT status expected)")
    print("  ✓ All trials will have high fairness scores (>0.80 expected)")
    print()
    print("You can upload these files at: http://localhost:3000/upload")
    print("=" * 70)

if __name__ == "__main__":
    main()

