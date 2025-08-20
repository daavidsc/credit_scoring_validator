#!/usr/bin/env python3
"""
Quick test to verify bias analysis processes all available test data
"""

import os
import sys
import pandas as pd

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_bias_data_processing():
    """Test that bias analysis will process all test data"""
    
    print("🔍 Testing Bias Analysis Data Processing")
    print("=" * 45)
    
    # Check test data availability
    test_data_path = "data/testdata.csv"
    try:
        df = pd.read_csv(test_data_path)
        print(f"📊 Available test data: {len(df)} records")
    except FileNotFoundError:
        print("❌ Test data file not found")
        return False
    
    # Check if cached responses exist
    response_path = "results/responses/bias_fairness.jsonl"
    if os.path.exists(response_path):
        print(f"❌ Cached responses found at {response_path}")
        print("   This will prevent new data generation!")
        print("   Run: rm results/responses/bias_fairness.jsonl")
        return False
    else:
        print("✅ No cached responses - will generate fresh data")
    
    # Simulate what collect_responses() will do
    print(f"\n📋 Bias analysis will process:")
    print(f"   - Dataset: {test_data_path}")
    print(f"   - Total rows: {len(df)}")
    print(f"   - Response file: {response_path}")
    
    print(f"\n🎯 Expected demographic parity analysis:")
    print(f"   - Should process ALL {len(df)} records (not just 10)")
    print(f"   - Each protected attribute analyzed across full dataset")
    
    return True

if __name__ == "__main__":
    # Set up environment
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    test_bias_data_processing()
