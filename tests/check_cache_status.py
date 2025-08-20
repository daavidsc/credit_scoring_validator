#!/usr/bin/env python3
"""
Analysis Cache Management Guide
Shows which analysis modules use cached data and how to clear them
"""

import os
import glob

def check_cached_files():
    """Check which analysis modules use cached response files"""
    
    print("🗂️  ANALYSIS CACHE MANAGEMENT GUIDE")
    print("=" * 50)
    print()
    
    # Define cache files and their corresponding analyses
    cache_info = {
        "bias_fairness.jsonl": {
            "analysis": "Bias & Fairness Analysis",
            "description": "API responses for demographic parity and disparate impact",
            "behavior": "Reuses cached responses if file exists",
            "sample_size_impact": "High - old cache might have fewer records"
        },
        "consistency.jsonl": {
            "analysis": "Consistency Analysis", 
            "description": "Multiple API responses for same inputs",
            "behavior": "Reuses cached responses if file exists",
            "sample_size_impact": "Medium - uses sample of input data"
        },
        "robustness.jsonl": {
            "analysis": "Robustness Analysis",
            "description": "API responses for adversarial/perturbed inputs", 
            "behavior": "Reuses cached responses if file exists",
            "sample_size_impact": "Medium - uses adversarial examples"
        },
        "accuracy_analysis.jsonl": {
            "analysis": "Accuracy Analysis",
            "description": "API responses saved after analysis (not reused)",
            "behavior": "Always generates fresh data, saves results",
            "sample_size_impact": "None - always uses current data"
        }
    }
    
    # Check which files actually exist
    response_dir = "results/responses"
    existing_files = []
    if os.path.exists(response_dir):
        existing_files = [f for f in os.listdir(response_dir) if f.endswith('.jsonl')]
    
    print("📋 CACHE STATUS:")
    print("-" * 30)
    
    for cache_file, info in cache_info.items():
        exists = cache_file in existing_files
        status = "✅ EXISTS" if exists else "❌ NOT FOUND"
        
        print(f"\n🎯 {info['analysis']}")
        print(f"   File: {cache_file}")
        print(f"   Status: {status}")
        print(f"   Behavior: {info['behavior']}")
        print(f"   Sample Impact: {info['sample_size_impact']}")
        
        if exists:
            file_path = os.path.join(response_dir, cache_file)
            try:
                with open(file_path, 'r') as f:
                    lines = len(f.readlines())
                print(f"   📊 Cached Records: {lines}")
            except:
                print(f"   📊 Cached Records: Unable to count")
    
    print(f"\n📁 OTHER FILES IN {response_dir}:")
    print("-" * 30)
    other_files = [f for f in existing_files if f not in cache_info.keys()]
    if other_files:
        for file in other_files:
            print(f"   • {file}")
    else:
        print("   (none)")
    
    print(f"\n🧹 TO CLEAR CACHE AND FORCE FRESH DATA:")
    print("=" * 45)
    print("# Clear specific analysis caches:")
    print("rm results/responses/bias_fairness.jsonl      # Bias analysis")
    print("rm results/responses/consistency.jsonl        # Consistency analysis") 
    print("rm results/responses/robustness.jsonl         # Robustness analysis")
    print()
    print("# Clear all cached responses:")
    print("rm results/responses/*.jsonl")
    print()
    print("# Keep only logs, clear all responses:")
    print("rm -rf results/responses && mkdir -p results/responses")
    
    print(f"\n⚠️  IMPORTANT NOTES:")
    print("=" * 20)
    print("• Accuracy Analysis: Always generates fresh data (no cache reuse)")
    print("• Data Quality Analysis: Uses existing response files from other analyses")
    print("• Clearing cache forces new API calls (costs time/money)")
    print("• Old cached files may have different sample sizes than current code")

if __name__ == "__main__":
    # Set up environment
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    check_cached_files()
