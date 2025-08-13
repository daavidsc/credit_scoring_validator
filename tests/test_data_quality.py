# tests/test_data_quality.py

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.data_quality import generate_data_quality_summary

def test_data_quality_analysis():
    """Test the data quality analysis with various response types"""
    
    test_responses = [
        # Successful responses
        {
            'input': {'name': 'Alice', 'gender': 'Female'},
            'output': {
                'parsed': {
                    'credit_score': '750',
                    'classification': 'Good',
                    'explanation': 'High income, excellent payment history'
                }
            }
        },
        {
            'input': {'name': 'Bob', 'gender': 'Male'},
            'output': {
                'parsed': {
                    'credit_score': '620',
                    'classification': 'Average',
                    'explanation': 'Moderate income, some payment delays'
                }
            }
        },
        # HTTP 500 error
        {
            'input': {'name': 'Charlie', 'gender': 'Male'},
            'error_type': 'http_error',
            'error': 'Internal server error',
            'status_code': 500
        },
        # Timeout error
        {
            'input': {'name': 'Diana', 'gender': 'Female'},
            'error_type': 'timeout',
            'error': 'Request timeout after 30 seconds'
        },
        # Incomplete response (missing classification)
        {
            'input': {'name': 'Eve', 'gender': 'Female'},
            'output': {
                'parsed': {
                    'credit_score': '680',
                    'explanation': 'Good income, average credit history'
                    # Missing classification
                }
            }
        },
        # Empty parsed response
        {
            'input': {'name': 'Frank', 'gender': 'Male'},
            'output': {
                'parsed': {}
            }
        }
    ]
    
    print("🧪 Testing Data Quality Analysis")
    print("=" * 50)
    
    result = generate_data_quality_summary(test_responses)
    
    print(f"📊 Overall Quality Score: {result['overall_quality']['score']:.1f}% ({result['overall_quality']['level']})")
    print(f"📈 Success Rate: {result['error_metrics']['success_rate']:.1f}%")
    print(f"❌ Error Rate: {result['error_metrics']['error_rate']:.1f}%")
    print(f"✅ Valid Scores: {result['error_metrics']['valid_scores']}/{result['error_metrics']['total_requests']}")
    
    print("\n🔍 Error Breakdown:")
    for error_type, details in result['error_metrics']['error_breakdown'].items():
        print(f"  • {error_type.replace('_', ' ').title()}: {details['count']} ({details['percentage']:.1f}%)")
    
    print("\n📋 Completeness Issues:")
    for issue_type, details in result['completeness_metrics']['issues'].items():
        print(f"  • {issue_type.replace('_', ' ').title()}: {details['count']} ({details['percentage']:.1f}%)")
    
    print("\n💡 Recommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print("\n" + "=" * 50)
    print("✅ Data Quality Analysis Test Complete!")
    
    return result

if __name__ == "__main__":
    test_data_quality_analysis()
