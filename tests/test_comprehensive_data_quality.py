# tests/test_comprehensive_data_quality.py

import os
import sys
import tempfile
import json
from unittest import mock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.data_quality_analyzer import run_comprehensive_data_quality_analysis
from utils.response_collector import get_collector, reset_collector

def test_comprehensive_data_quality():
    """Test comprehensive data quality analysis with multiple modules"""
    print("🧪 Testing Comprehensive Data Quality Analysis")
    
    # Reset collector
    reset_collector()
    collector = get_collector()
    
    # Mock some responses from different modules
    mock_responses = [
        # Bias fairness responses
        {
            "module": "bias_fairness",
            "input": {"name": "John Doe", "income": 50000},
            "output": {
                "status": "success",
                "parsed": {
                    "credit_score": 750,
                    "classification": "Good",
                    "explanation": "High income and stable employment"
                }
            }
        },
        # Robustness responses (with errors)
        {
            "module": "robustness", 
            "input": {"name": "Jane Smith", "income": 30000},
            "output": {
                "error_type": "timeout",
                "error": "Request timed out"
            }
        },
        # Consistency responses
        {
            "module": "consistency",
            "input": {"name": "Bob Johnson", "income": 60000},
            "output": {
                "status": "success", 
                "parsed": {
                    "credit_score": 680,
                    "classification": "Average",
                    "explanation": "Moderate risk profile"
                }
            }
        },
        # More robustness responses
        {
            "module": "robustness",
            "input": {"name": "Alice Brown", "income": 45000},
            "output": {
                "status": "success",
                "parsed": {
                    "credit_score": 720,
                    "classification": "Good", 
                    "explanation": "Solid financial profile"
                }
            }
        }
    ]
    
    # Add mock responses to collector
    for response in mock_responses:
        collector.add_response(
            response["module"],
            response["input"], 
            response["output"]
        )
    
    print(f"✅ Added {len(mock_responses)} mock responses")
    print(f"📊 Module breakdown: {collector.get_module_counts()}")
    
    # Run comprehensive analysis
    results = run_comprehensive_data_quality_analysis()
    
    # Verify results
    assert results["total_responses_analyzed"] == 4
    assert "comprehensive_data_quality" in results or "data_quality" in results
    
    data_quality = results.get("data_quality", {})
    overall_quality = data_quality.get("overall_quality", {})
    
    print(f"📈 Quality Score: {overall_quality.get('score', 0):.1f}%")
    print(f"🎯 Quality Level: {overall_quality.get('level', 'Unknown')}")
    
    # Check module breakdown
    module_breakdown = data_quality.get("module_breakdown", {})
    print(f"🔍 Module Analysis:")
    for module, stats in module_breakdown.items():
        print(f"  • {module}: {stats['total_requests']} requests, {stats['success_rate']:.1f}% success rate")
    
    print("✅ Comprehensive Data Quality Analysis Test Passed!")
    return results

if __name__ == "__main__":
    results = test_comprehensive_data_quality()
    
    # Save test results
    with open("test_comprehensive_dq_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n🎉 Test completed successfully!")
    print(f"📋 Results saved to test_comprehensive_dq_results.json")
