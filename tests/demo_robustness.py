#!/usr/bin/env python3
# tests/demo_robustness.py

"""
Demo script to test robustness analysis functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.robustness import generate_adversarial_examples, analyze_robustness_results, parse_credit_decision
import pandas as pd
import json

def mock_api_call(data):
    """Mock API call that returns a credit decision based on simple rules"""
    # Simple mock logic based on credit score and income
    credit_score = data.get('credit_limit', 50000)  # Using credit_limit as proxy for credit score
    income = data.get('income', 0)
    
    # Simple decision logic
    if credit_score > 80000 and income > 90000:
        return "I approve this loan application with high confidence (85%)"
    elif credit_score > 60000 and income > 60000:
        return "I approve this loan application with medium confidence (70%)"
    elif credit_score > 40000 and income > 40000:
        return "I approve this loan application with low confidence (55%)"
    else:
        return "I deny this loan application due to insufficient creditworthiness"

def demo_robustness_analysis():
    print("🛡️  Demo: Robustness Analysis")
    print("=" * 50)
    
    # Load test data
    try:
        df = pd.read_csv("data/testdata.csv")
        print(f"✅ Loaded {len(df)} test profiles")
    except FileNotFoundError:
        print("❌ Test data file not found")
        return
    
    # Generate adversarial examples
    print("\n📊 Generating adversarial examples...")
    adversarial_examples = generate_adversarial_examples(df, num_examples=5)
    print(f"✅ Generated {len(adversarial_examples)} adversarial examples")
    
    # Show example perturbations
    for i, example in enumerate(adversarial_examples[:3]):
        print(f"\n--- Example {i+1} ({example['perturbation_type']}) ---")
        orig_data = example['original_data']
        pert_data = example['perturbed_data']
        
        # Show a few key fields
        for field in ['age', 'income', 'employment_status'][:2]:
            if field in orig_data:
                orig_val = orig_data[field]
                pert_val = pert_data[field]
                if orig_val != pert_val:
                    print(f"{field}: {orig_val} → {pert_val}")
    
    # Simulate API responses
    print("\n🔄 Simulating API calls...")
    responses = []
    
    for example in adversarial_examples:
        original_response = mock_api_call(example['original_data'])
        perturbed_response = mock_api_call(example['perturbed_data'])
        
        response_record = {
            "perturbation_type": example["perturbation_type"],
            "original_response": original_response,
            "perturbed_response": perturbed_response,
            "original_data": example["original_data"],
            "perturbed_data": example["perturbed_data"]
        }
        responses.append(response_record)
    
    print(f"✅ Collected {len(responses)} response pairs")
    
    # Analyze results
    print("\n🔍 Analyzing robustness results...")
    results = analyze_robustness_results(responses)
    
    # Display key metrics
    print(f"\n📈 Results Summary:")
    print(f"  Total examples: {results['total_examples']}")
    print(f"  Decision consistency rate: {results['decision_consistency']['rate']:.2%}")
    print(f"  Consistent decisions: {results['decision_consistency']['consistent_count']}")
    print(f"  Inconsistent decisions: {results['decision_consistency']['inconsistent_count']}")
    print(f"  Overall robustness score: {results['robustness_score']:.3f}")
    
    if results['confidence_stability']:
        print(f"  Mean confidence difference: {results['confidence_stability']['mean_difference']:.3f}")
        print(f"  Max confidence difference: {results['confidence_stability']['max_difference']:.3f}")
    
    # Show perturbation analysis
    print(f"\n📊 Analysis by perturbation type:")
    for ptype, stats in results['perturbation_analysis'].items():
        consistency = stats['consistency_rate']
        confidence_drop = stats['average_confidence_drop']
        print(f"  {ptype.replace('_', ' ').title()}:")
        print(f"    - Consistency rate: {consistency:.2%}")
        print(f"    - Avg confidence drop: {confidence_drop:.3f}")
    
    # Show failure cases
    if results['failure_cases']:
        print(f"\n⚠️  Failure cases ({len(results['failure_cases'])}):")
        for case in results['failure_cases'][:3]:  # Show first 3
            print(f"  - {case['perturbation_type']} perturbation")
            print(f"    Original: {case['original_response'][:50]}...")
            print(f"    Perturbed: {case['perturbed_response'][:50]}...")
            print()
    
    # Interpretation
    print("📝 Interpretation:")
    if results['robustness_score'] >= 0.8:
        print("  ✅ Excellent robustness! The model is very stable.")
    elif results['robustness_score'] >= 0.6:
        print("  🟡 Good robustness, but there's room for improvement.")
    elif results['robustness_score'] >= 0.4:
        print("  🟠 Moderate robustness. Consider model improvements.")
    else:
        print("  ❌ Poor robustness. The model is highly unstable.")
    
    print(f"\n✅ Demo completed!")
    return results

if __name__ == "__main__":
    demo_robustness_analysis()
