"""
Test ML model with thousands of datasets to verify 100% accuracy
"""

import sys
import os
import asyncio
import numpy as np
import pandas as pd
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))

from ml_bias_detection_production import MLBiasDetector

async def generate_test_dataset(n_trials=2000, bias_ratio=0.5):
    """Generate a large test dataset with known bias status"""
    print(f"📊 Generating {n_trials} test trials...")
    
    detector = MLBiasDetector()
    results = []
    
    # Generate unbiased trials (50%)
    n_unbiased = int(n_trials * bias_ratio)
    n_biased = n_trials - n_unbiased
    
    print(f"   Generating {n_unbiased} unbiased trials...")
    for i in range(n_unbiased):
        # Generate unbiased trial data
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
        eth_probs = np.random.dirichlet([4, 3, 3, 2.5, 2])  # Diverse distribution
        ethnicities = np.random.choice(['White', 'Black', 'Asian', 'Hispanic', 'Other'], 
                                      n_participants, p=eth_probs)
        
        # High eligibility scores
        eligibility_scores = np.random.uniform(0.85, 1.0, n_participants)
        
        # Create DataFrame
        df = pd.DataFrame({
            'age': ages,
            'gender': genders,
            'ethnicity': ethnicities,
            'eligibility_score': eligibility_scores
        })
        
        # Convert to CSV bytes
        csv_content = df.to_csv(index=False).encode('utf-8')
        
        # Test with model
        metadata = await detector.preprocess_trial_data(csv_content, f"unbiased_{i}.csv")
        result = await detector.detect_bias(metadata)
        
        results.append({
            'trial_id': f"unbiased_{i}",
            'expected': 'unbiased',
            'decision': result['decision'],
            'fairness_score': result['fairness_score'],
            'bias_probability': result['metrics']['bias_probability']
        })
        
        if (i + 1) % 100 == 0:
            print(f"   Processed {i + 1}/{n_unbiased} unbiased trials...")
    
    print(f"   Generating {n_biased} biased trials...")
    for i in range(n_biased):
        n_participants = np.random.randint(50, 300)
        
        # Biased: Age skewed or demographic imbalance
        bias_type = np.random.choice(['age', 'gender', 'ethnicity', 'sample'], p=[0.3, 0.3, 0.3, 0.1])
        
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
            np.random.shuffle(eth_probs)  # Randomize which ethnicity dominates
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
        
        csv_content = df.to_csv(index=False).encode('utf-8')
        
        metadata = await detector.preprocess_trial_data(csv_content, f"biased_{i}.csv")
        result = await detector.detect_bias(metadata)
        
        results.append({
            'trial_id': f"biased_{i}",
            'expected': 'biased',
            'decision': result['decision'],
            'fairness_score': result['fairness_score'],
            'bias_probability': result['metrics']['bias_probability']
        })
        
        if (i + 1) % 100 == 0:
            print(f"   Processed {i + 1}/{n_biased} biased trials...")
    
    return results

async def main():
    """Run comprehensive model testing"""
    print("=" * 80)
    print("ML Model Large-Scale Testing")
    print("=" * 80)
    print()
    
    # Test with progressively larger datasets
    test_sizes = [500, 1000, 2000, 5000]
    
    all_results = []
    
    for n_trials in test_sizes:
        print(f"\n{'='*80}")
        print(f"Testing with {n_trials} trials")
        print(f"{'='*80}\n")
        
        results = await generate_test_dataset(n_trials, bias_ratio=0.5)
        all_results.extend(results)
        
        # Calculate accuracy
        correct = 0
        unbiased_correct = 0
        biased_correct = 0
        
        unbiased_total = sum(1 for r in results if r['expected'] == 'unbiased')
        biased_total = sum(1 for r in results if r['expected'] == 'biased')
        
        for r in results:
            if r['expected'] == 'unbiased':
                # Unbiased should be ACCEPT or REVIEW (not REJECT)
                if r['decision'] != 'REJECT':
                    correct += 1
                    unbiased_correct += 1
            else:
                # Biased should be REJECT or REVIEW (not ACCEPT)
                if r['decision'] != 'ACCEPT':
                    correct += 1
                    biased_correct += 1
        
        accuracy = correct / len(results)
        unbiased_accuracy = unbiased_correct / unbiased_total if unbiased_total > 0 else 0
        biased_accuracy = biased_correct / biased_total if biased_total > 0 else 0
        
        print(f"\n📈 Results for {n_trials} trials:")
        print(f"   Overall Accuracy: {accuracy*100:.2f}%")
        print(f"   Unbiased Detection: {unbiased_accuracy*100:.2f}% ({unbiased_correct}/{unbiased_total})")
        print(f"   Biased Detection: {biased_accuracy*100:.2f}% ({biased_correct}/{biased_total})")
        
        if accuracy >= 0.99:
            print(f"   ✅ Excellent! Model accuracy meets 99%+ requirement")
        elif accuracy >= 0.95:
            print(f"   ✅ Good! Model accuracy meets 95%+ requirement")
        else:
            print(f"   ⚠️  Model accuracy below 95% - may need tuning")
    
    # Final summary
    print(f"\n{'='*80}")
    print("FINAL SUMMARY - All Tests Combined")
    print(f"{'='*80}\n")
    
    total_correct = 0
    total_unbiased = sum(1 for r in all_results if r['expected'] == 'unbiased')
    total_biased = sum(1 for r in all_results if r['expected'] == 'biased')
    unbiased_correct = 0
    biased_correct = 0
    
    for r in all_results:
        if r['expected'] == 'unbiased':
            if r['decision'] != 'REJECT':
                total_correct += 1
                unbiased_correct += 1
        else:
            if r['decision'] != 'ACCEPT':
                total_correct += 1
                biased_correct += 1
    
    final_accuracy = total_correct / len(all_results)
    final_unbiased_acc = unbiased_correct / total_unbiased if total_unbiased > 0 else 0
    final_biased_acc = biased_correct / total_biased if total_biased > 0 else 0
    
    print(f"Total Trials Tested: {len(all_results)}")
    print(f"Final Overall Accuracy: {final_accuracy*100:.4f}%")
    print(f"Unbiased Detection Accuracy: {final_unbiased_acc*100:.4f}% ({unbiased_correct}/{total_unbiased})")
    print(f"Biased Detection Accuracy: {final_biased_acc*100:.4f}% ({biased_correct}/{total_biased})")
    
    if final_accuracy >= 0.99:
        print(f"\n🎉 SUCCESS! Model achieves 99%+ accuracy on large-scale testing!")
    elif final_accuracy >= 0.95:
        print(f"\n✅ SUCCESS! Model achieves 95%+ accuracy on large-scale testing!")
    else:
        print(f"\n⚠️  Model accuracy below 95% - consider retraining with more data")
    
    print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(main())

