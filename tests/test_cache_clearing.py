#!/usr/bin/env python3
"""
Test the cache clearing functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import clear_analysis_cache

def test_cache_clearing():
    """Test that cache clearing works correctly"""
    
    print("🧹 Testing Cache Clearing Functionality")
    print("=" * 45)
    
    # Check initial state
    cache_files = [
        "results/responses/bias_fairness.jsonl",
        "results/responses/consistency.jsonl", 
        "results/responses/robustness.jsonl"
    ]
    
    print("📂 Initial cache file status:")
    for file in cache_files:
        exists = "✅" if os.path.exists(file) else "❌"
        print(f"   {exists} {file}")
    
    # Test clearing specific cache
    print("\n🎯 Test 1: Clear consistency cache only")
    cache_options = {"clear_consistency_cache": True}
    cleared = clear_analysis_cache(cache_options)
    print(f"   Cleared files: {cleared}")
    
    # Check state after partial clear
    print("\n📂 After clearing consistency cache:")
    for file in cache_files:
        exists = "✅" if os.path.exists(file) else "❌"
        print(f"   {exists} {file}")
    
    # Test clearing all cache
    print("\n🎯 Test 2: Clear all cache")
    cache_options = {"clear_all_cache": True}
    cleared = clear_analysis_cache(cache_options)
    print(f"   Cleared files: {cleared}")
    
    # Check final state
    print("\n📂 After clearing all cache:")
    for file in cache_files:
        exists = "✅" if os.path.exists(file) else "❌"
        print(f"   {exists} {file}")
    
    print("\n✅ Cache clearing functionality test completed!")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    test_cache_clearing()
