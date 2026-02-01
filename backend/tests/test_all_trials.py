"""
Test all 25 unbiased trials to ensure they all pass
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(__file__))

from ml_bias_detection_production import MLBiasDetector
from pathlib import Path

async def test_trial(csv_path: str):
    """Test a single trial CSV file"""
    detector = MLBiasDetector()
    
    # Read CSV file
    with open(csv_path, 'rb') as f:
        content = f.read()
    
    # Preprocess
    trial_metadata = await detector.preprocess_trial_data(content, Path(csv_path).name)
    
    # Validate rules
    validation = await detector.validate_eligibility_rules(trial_metadata)
    
    # Detect bias
    result = await detector.detect_bias(trial_metadata)
    
    return {
        'file': Path(csv_path).name,
        'validation_status': validation['status'],
        'decision': result['decision'],
        'fairness_score': result['fairness_score'],
        'bias_probability': result['metrics']['bias_probability'],
        'demographic_parity': result['metrics']['fairness_metrics']['demographic_parity'],
        'disparate_impact': result['metrics']['fairness_metrics']['disparate_impact_ratio']
    }

async def main():
    """Test all unbiased trials"""
    sample_trials_dir = Path("../sample_trials")
    
    if not sample_trials_dir.exists():
        print("❌ Sample trials directory not found!")
        return
    
    csv_files = sorted(list(sample_trials_dir.glob("trial_*.csv")))
    
    if not csv_files:
        print("❌ No trial CSV files found!")
        return
    
    print("=" * 90)
    print("Testing All 25 Unbiased Trials")
    print("=" * 90)
    
    results = []
    for csv_file in csv_files:
        result = await test_trial(str(csv_file))
        results.append(result)
        status = "✅" if result['decision'] == "ACCEPT" else "⚠️" if result['decision'] == "REVIEW" else "❌"
        print(f"{status} {result['file'][:40]:40s} | {result['decision']:6s} | "
              f"Fairness: {result['fairness_score']*100:5.1f}% | "
              f"Bias: {result['bias_probability']*100:5.1f}%")
    
    print("=" * 90)
    print("Summary")
    print("=" * 90)
    
    accepted = sum(1 for r in results if r['decision'] == "ACCEPT")
    review = sum(1 for r in results if r['decision'] == "REVIEW")
    rejected = sum(1 for r in results if r['decision'] == "REJECT")
    
    validation_passed = sum(1 for r in results if r['validation_status'] == "PASSED")
    
    print(f"Total Trials: {len(results)}")
    print(f"✅ Validation Passed: {validation_passed}/{len(results)}")
    print(f"✅ Accepted: {accepted}/{len(results)}")
    print(f"⚠️  Review: {review}/{len(results)}")
    print(f"❌ Rejected: {rejected}/{len(results)}")
    
    avg_fairness = sum(r['fairness_score'] for r in results) / len(results)
    print(f"\nAverage Fairness Score: {avg_fairness*100:.1f}%")
    
    if accepted == len(results):
        print("\n🎉 SUCCESS! All 25 unbiased trials correctly accepted!")
    elif accepted + review == len(results):
        print("\n✅ SUCCESS! All trials passed (accepted or review) - no rejections!")
    else:
        print(f"\n⚠️  {rejected} trial(s) were rejected - may need further tuning")
    
    # Show any review/rejected trials
    if review > 0 or rejected > 0:
        print("\nTrials needing attention:")
        for r in results:
            if r['decision'] != "ACCEPT":
                print(f"  • {r['file']}: {r['decision']} (Fairness: {r['fairness_score']*100:.1f}%)")

if __name__ == "__main__":
    asyncio.run(main())

