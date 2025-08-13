#!/usr/bin/env python3
# tests/demo_consistency.py

"""
Demo script to test consistency analysis functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.consistency import analyze_consistency_results, extract_decision_and_confidence, hash_input_data
import pandas as pd
import random

def mock_api_call_with_variance(data, variance_level="low"):
    """Mock API call that can produce varying responses"""
    # Simple mock logic based on credit score and income
    credit_score = data.get('credit_limit', 50000)
    income = data.get('income', 0)
    
    # Base decision logic
    if credit_score > 80000 and income > 90000:
        base_response = "I approve this loan application with high confidence (85%)"
        base_decision = "approve"
        base_confidence = 85
    elif credit_score > 60000 and income > 60000:
        base_response = "I approve this loan application with medium confidence (70%)"
        base_decision = "approve"
        base_confidence = 70
    else:
        base_response = "I deny this loan application due to insufficient creditworthiness"
        base_decision = "deny"
        base_confidence = 90
    
    # Add variance based on level
    if variance_level == "none":
        return base_response
    elif variance_level == "low":
        # Small confidence variations
        if base_decision == "approve":
            confidence_shift = random.randint(-3, 3)
            new_confidence = max(50, min(95, base_confidence + confidence_shift))
            return f"I {base_decision} this loan application with {new_confidence}% confidence"
        return base_response
    elif variance_level == "medium":
        # More significant variations
        if base_decision == "approve":
            confidence_shift = random.randint(-10, 10)
            new_confidence = max(50, min(95, base_confidence + confidence_shift))
            
            # Occasionally change wording
            if random.random() < 0.3:
                templates = [
                    f"This application is approved with {new_confidence}% confidence",
                    f"I recommend approval ({new_confidence}% confidence)",
                    f"Approve this loan with {new_confidence}% certainty"
                ]
                return random.choice(templates)
            return f"I {base_decision} this loan application with {new_confidence}% confidence"
        return base_response
    elif variance_level == "high":
        # High variance including decision changes
        if random.random() < 0.2:  # 20% chance to flip decision
            if base_decision == "approve":
                return "I deny this application due to risk concerns"
            else:
                return "I approve this application with low confidence (55%)"
        
        # Significant confidence and wording changes
        if base_decision == "approve":
            confidence_shift = random.randint(-20, 20)
            new_confidence = max(40, min(95, base_confidence + confidence_shift))
            
            templates = [
                f"Application approved at {new_confidence}% confidence",
                f"I approve with {new_confidence}% certainty",
                f"This loan is approved ({new_confidence}% confidence)",
                f"Recommendation: Approve ({new_confidence}%)",
                f"Yes, approve this application with {new_confidence}% confidence"
            ]
            return random.choice(templates)
        
        return base_response

def demo_consistency_analysis():
    print("🔄 Demo: Consistency Analysis")
    print("=" * 50)
    
    # Load test data
    try:
        df = pd.read_csv("data/testdata.csv")
        print(f"✅ Loaded {len(df)} test profiles")
    except FileNotFoundError:
        print("❌ Test data file not found")
        return
    
    # Select a few samples for testing
    num_samples = 3
    num_repeats = 4
    sample_df = df.sample(n=num_samples, random_state=42)
    
    print(f"\n📊 Testing consistency with {num_samples} samples, {num_repeats} repeats each")
    
    # Test different variance levels
    variance_levels = ["none", "low", "medium", "high"]
    
    for variance_level in variance_levels:
        print(f"\n--- Testing with {variance_level.upper()} variance ---")
        
        consistency_data = []
        
        for idx, (_, row) in enumerate(sample_df.iterrows()):
            input_data = row.to_dict()
            input_hash = hash_input_data(input_data)
            
            responses_for_input = []
            
            # Make multiple API calls with the same input
            for repeat in range(num_repeats):
                response = mock_api_call_with_variance(input_data, variance_level)
                
                response_record = {
                    "input_hash": input_hash,
                    "input_data": input_data,
                    "repeat_number": repeat + 1,
                    "response": response,
                    "timestamp": 0,  # Mock timestamp
                    "call_order": repeat + 1
                }
                responses_for_input.append(response_record)
            
            consistency_record = {
                "input_hash": input_hash,
                "input_data": input_data,
                "sample_index": idx,
                "responses": responses_for_input,
                "num_responses": len(responses_for_input)
            }
            consistency_data.append(consistency_record)
        
        # Analyze results
        results = analyze_consistency_results(consistency_data)
        
        # Display key metrics
        print(f"  📈 Results:")
        print(f"    Overall consistency score: {results['overall_consistency_score']:.3f}")
        print(f"    Perfect consistency rate: {results['perfect_consistency']:.2%}")
        print(f"    Decision consistency rate: {results['decision_consistency']:.2%}")
        print(f"    Confidence consistency rate: {results['confidence_consistency']:.2%}")
        print(f"    Inconsistent cases: {len(results['inconsistent_cases'])}")
        
        # Show example responses for one input
        if consistency_data and variance_level in ["medium", "high"]:
            sample_responses = consistency_data[0]['responses']
            print(f"    📝 Sample responses for first input:")
            for i, resp in enumerate(sample_responses[:3]):
                decision, confidence = extract_decision_and_confidence(resp['response'])
                print(f"      {i+1}. {resp['response'][:60]}... -> {decision}, {confidence}")
        
        # Interpretation
        if results['overall_consistency_score'] >= 0.9:
            print(f"    ✅ Excellent consistency!")
        elif results['overall_consistency_score'] >= 0.7:
            print(f"    🟡 Good consistency, minor variations")
        elif results['overall_consistency_score'] >= 0.5:
            print(f"    🟠 Moderate consistency, some concerns")
        else:
            print(f"    ❌ Poor consistency, major issues detected")
    
    print(f"\n📊 Summary:")
    print(f"  • 'None' variance: Perfect consistency (ideal scenario)")
    print(f"  • 'Low' variance: Minor confidence variations (acceptable)")
    print(f"  • 'Medium' variance: Noticeable variations (needs attention)")
    print(f"  • 'High' variance: Major inconsistencies (critical issue)")
    
    print(f"\n💡 Key Insights:")
    print(f"  • Decision consistency is more critical than exact text matching")
    print(f"  • Confidence score stability indicates model reliability")
    print(f"  • Even small variations can impact user trust")
    print(f"  • Consistency testing should be part of regular model validation")
    
    print(f"\n✅ Demo completed!")

if __name__ == "__main__":
    demo_consistency_analysis()
