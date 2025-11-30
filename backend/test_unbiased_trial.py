"""
Test script to verify ML model works correctly with unbiased trials
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ml_bias_detection_production import MLBiasDetector
from pathlib import Path

async def test_trial(csv_path: str):
    """Test a single trial CSV file"""
    print(f"\n{'='*70}")
    print(f"Testing: {csv_path}")
    print(f"{'='*70}")
    
    detector = MLBiasDetector()
    
    # Read CSV file
    with open(csv_path, 'rb') as f:
        content = f.read()
    
    # Preprocess
    print("\n📊 Preprocessing trial data...")
    trial_metadata = await detector.preprocess_trial_data(content, Path(csv_path).name)
    
    print(f"   Participants: {trial_metadata['participant_count']}")
    print(f"   Age: {trial_metadata['age_distribution']['mean']:.1f} ± {trial_metadata['age_distribution']['std']:.1f}")
    print(f"   Gender: M:{trial_metadata['gender_distribution']['male']:.1%} F:{trial_metadata['gender_distribution']['female']:.1%}")
    print(f"   Ethnicity: W:{trial_metadata['ethnicity_distribution'].get('white', 0):.1%} "
          f"B:{trial_metadata['ethnicity_distribution'].get('black', 0):.1%} "
          f"A:{trial_metadata['ethnicity_distribution'].get('asian', 0):.1%} "
          f"H:{trial_metadata['ethnicity_distribution'].get('hispanic', 0):.1%}")
    
    # Validate rules
    print("\n✓ Validating rules...")
    validation = await detector.validate_eligibility_rules(trial_metadata)
    print(f"   Status: {validation['status'].upper()}")
    print(f"   Passed: {len(validation['rules_passed'])}/{validation['total_rules']}")
    
    # Detect bias
    print("\n🤖 Running ML bias detection...")
    result = await detector.detect_bias(trial_metadata)
    
    print(f"\n📈 Results:")
    print(f"   Decision: {result['decision']}")
    print(f"   Fairness Score: {result['fairness_score']*100:.1f}%")
    print(f"   Bias Probability: {result['metrics']['bias_probability']*100:.1f}%")
    print(f"   Is Outlier: {result['metrics']['is_outlier']}")
    print(f"   Demographic Parity: {result['metrics']['fairness_metrics']['demographic_parity']*100:.1f}%")
    print(f"   Disparate Impact: {result['metrics']['fairness_metrics']['disparate_impact_ratio']*100:.1f}%")
    print(f"   Equality of Opportunity: {result['metrics']['fairness_metrics']['equality_of_opportunity']*100:.1f}%")
    
    if result['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in result['recommendations']:
            print(f"   • {rec}")
    
    return result

async def main():
    """Test multiple unbiased trials"""
    import asyncio
    
    sample_trials_dir = Path("../sample_trials")
    
    if not sample_trials_dir.exists():
        print("❌ Sample trials directory not found!")
        return
    
    # Test first 3 trials
    csv_files = sorted(list(sample_trials_dir.glob("trial_*.csv")))[:3]
    
    if not csv_files:
        print("❌ No trial CSV files found!")
        return
    
    print("=" * 70)
    print("Testing Unbiased Trials with ML Model")
    print("=" * 70)
    
    results = []
    for csv_file in csv_files:
        result = await test_trial(str(csv_file))
        results.append(result)
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    
    for i, result in enumerate(results, 1):
        status = "✅" if result['decision'] == "ACCEPT" else "⚠️" if result['decision'] == "REVIEW" else "❌"
        print(f"{status} Trial {i}: {result['decision']} - Fairness: {result['fairness_score']*100:.1f}%")
    
    all_accepted = all(r['decision'] == "ACCEPT" for r in results)
    if all_accepted:
        print("\n✅ All unbiased trials correctly accepted!")
    else:
        print("\n⚠️ Some trials were not accepted - may need further tuning")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

