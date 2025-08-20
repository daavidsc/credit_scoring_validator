# tests/demo_comprehensive_data_quality.py

"""
Demo: Comprehensive Data Quality Analysis

This demo shows how the new comprehensive data quality analysis works
by simulating API responses from multiple analysis modules.
"""

import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.response_collector import reset_collector, get_collector
from analysis.data_quality_analyzer import run_comprehensive_data_quality_analysis
from reports.report_builder import build_comprehensive_data_quality_report

def simulate_real_world_analysis():
    """Simulate a real-world analysis session with multiple modules"""
    print("🚀 Starting Comprehensive Data Quality Analysis Demo")
    print("=" * 60)
    
    # Reset collector to start fresh
    reset_collector()
    collector = get_collector()
    
    # Simulate bias fairness analysis (10 requests)
    print("📊 Simulating Bias Fairness Analysis...")
    for i in range(10):
        collector.add_response(
            "bias_fairness",
            {"name": f"User {i+1}", "income": 30000 + i*5000},
            {
                "status": "success",
                "parsed": {
                    "credit_score": 650 + i*10,
                    "classification": "Good" if i > 5 else "Average",
                    "explanation": f"Analysis for user {i+1}"
                }
            }
        )
    
    # Simulate robustness analysis (100+ requests with some errors)
    print("🛡️  Simulating Robustness Analysis...")
    for i in range(120):
        if i % 15 == 0:  # 1 in 15 has timeout error
            collector.add_response(
                "robustness",
                {"name": f"Robust Test {i+1}", "perturbed": True},
                {
                    "error_type": "timeout",
                    "error": "Request timed out after 30 seconds"
                }
            )
        elif i % 20 == 0:  # 1 in 20 has connection error
            collector.add_response(
                "robustness",
                {"name": f"Robust Test {i+1}", "perturbed": True},
                {
                    "error_type": "connection_error", 
                    "error": "Connection refused"
                }
            )
        else:  # Success
            collector.add_response(
                "robustness",
                {"name": f"Robust Test {i+1}", "perturbed": True},
                {
                    "status": "success",
                    "parsed": {
                        "credit_score": 60 + (i % 40),  # Generate scores 60-99 for 0-100 scale
                        "classification": ["Poor", "Average", "Good"][i % 3],
                        "explanation": f"Robustness test result {i+1}"
                    }
                }
            )
    
    # Simulate consistency analysis (30 requests)
    print("🔄 Simulating Consistency Analysis...")
    for i in range(30):
        collector.add_response(
            "consistency",
            {"name": f"Consistency Test {i+1}", "repeat": i % 3},
            {
                "status": "success",
                "parsed": {
                    "credit_score": 70 + (i % 30),  # Generate scores 70-99 for 0-100 scale
                    "classification": "Good",
                    "explanation": f"Consistency analysis {i+1}"
                }
            }
        )
    
    # Simulate accuracy analysis (50 requests with some parsing errors)
    print("🎯 Simulating Accuracy Analysis...")
    for i in range(50):
        if i % 10 == 0:  # 1 in 10 has parsing error
            collector.add_response(
                "accuracy",
                {"name": f"Accuracy Test {i+1}"},
                {
                    "status": "success",
                    "parsed": {}  # Empty parsing - missing score
                }
            )
        else:
            collector.add_response(
                "accuracy",
                {"name": f"Accuracy Test {i+1}"},
                {
                    "status": "success",
                    "parsed": {
                        "credit_score": 550 + i*5,
                        "classification": ["Poor", "Average", "Good"][i % 3],
                        "explanation": f"Accuracy test result {i+1}"
                    }
                }
            )
    
    print(f"\n📋 Collection Summary:")
    module_counts = collector.get_module_counts()
    total_responses = collector.get_response_count()
    
    print(f"  Total Responses: {total_responses}")
    for module, count in module_counts.items():
        print(f"  • {module}: {count} responses")
    
    print(f"\n🔍 Running Comprehensive Data Quality Analysis...")
    
    # Run the comprehensive analysis
    results = run_comprehensive_data_quality_analysis()
    
    print(f"\n✅ Analysis Complete!")
    print(f"📊 Quality Score: {results['data_quality']['overall_quality']['score']:.1f}%")
    print(f"🎯 Quality Level: {results['data_quality']['overall_quality']['level']}")
    
    # Show module breakdown
    print(f"\n📈 Module Performance:")
    for module, stats in results['data_quality']['module_breakdown'].items():
        print(f"  • {module}:")
        print(f"    - {stats['total_requests']} total requests")
        print(f"    - {stats['success_rate']:.1f}% success rate")
        print(f"    - {stats['valid_score_rate']:.1f}% valid score rate")
    
    # Show error breakdown
    if results['data_quality']['error_metrics']['error_breakdown']:
        print(f"\n⚠️  Error Breakdown:")
        for error_type, error_data in results['data_quality']['error_metrics']['error_breakdown'].items():
            print(f"  • {error_type}: {error_data['count']} occurrences ({error_data['percentage']:.1f}%)")
    
    # Build HTML report
    print(f"\n📄 Building HTML Report...")
    report_path = build_comprehensive_data_quality_report(results)
    
    print(f"\n🎉 Demo Complete!")
    print(f"📊 Comprehensive Data Quality Analysis processed {total_responses} API responses")
    print(f"📋 Report saved to: {report_path}")
    
    return results

if __name__ == "__main__":
    results = simulate_real_world_analysis()
    
    print(f"\n" + "="*60)
    print(f"COMPREHENSIVE DATA QUALITY ANALYSIS DEMO")
    print(f"="*60)
    print(f"✅ Successfully analyzed {results['total_responses_analyzed']} API responses")
    print(f"📊 Overall Quality: {results['data_quality']['overall_quality']['score']:.1f}% ({results['data_quality']['overall_quality']['level']})")
    print(f"🎯 Success Rate: {results['data_quality']['error_metrics']['success_rate']:.1f}%")
    print(f"📈 Valid Score Rate: {results['data_quality']['error_metrics']['valid_score_rate']:.1f}%")
    print(f"📋 Modules Analyzed: {len(results['data_quality']['module_breakdown'])}")
    
    print(f"\n💡 This solves the original problem:")
    print(f"   Before: Data quality only looked at ~10 bias analysis responses")
    print(f"   Now: Data quality analyzes ALL {results['total_responses_analyzed']} API responses from all modules!")
