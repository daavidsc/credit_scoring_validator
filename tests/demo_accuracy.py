#!/usr/bin/env python3
"""
Demonstration script for the accuracy analysis functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.accuracy import run_accuracy_analysis
import json

def main():
    """Run accuracy analysis and display results"""
    print("🎯 Credit Scoring Accuracy Analysis")
    print("=" * 50)
    
    # Run the analysis
    results = run_accuracy_analysis()
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Display summary
    summary = results.get("summary", {})
    print(f"\n📊 Summary:")
    print(f"   Total responses: {summary.get('total_responses', 0)}")
    print(f"   Valid predictions: {summary.get('total_predictions', 0)}")
    print(f"   Success rate: {summary.get('valid_prediction_rate', 0):.1%}")
    
    # Display regression metrics
    reg_metrics = results.get("regression_metrics", {})
    if reg_metrics:
        print(f"\n📈 Regression Metrics (Credit Scores):")
        print(f"   Mean Absolute Error: {reg_metrics.get('mae', 0):.2f}")
        print(f"   Root Mean Square Error: {reg_metrics.get('rmse', 0):.2f}")
        print(f"   R² Score: {reg_metrics.get('r2', 0):.3f}")
        print(f"   Correlation: {reg_metrics.get('correlation', 0):.3f}")
    
    # Display classification metrics
    class_metrics = results.get("classification_metrics", {})
    if class_metrics:
        print(f"\n🎯 Classification Metrics:")
        print(f"   Overall Accuracy: {class_metrics.get('accuracy', 0):.3f}")
        
        macro_avg = class_metrics.get('macro_avg', {})
        print(f"   Macro F1-Score: {macro_avg.get('f1_score', 0):.3f}")
        
        print(f"\n   Class-specific metrics:")
        class_details = class_metrics.get('class_metrics', {})
        for class_name, metrics in class_details.items():
            print(f"     {class_name}:")
            print(f"       Precision: {metrics.get('precision', 0):.3f}")
            print(f"       Recall: {metrics.get('recall', 0):.3f}")
            print(f"       F1-Score: {metrics.get('f1_score', 0):.3f}")
            print(f"       Support: {metrics.get('support', 0)}")
    
    # Display distribution analysis
    distribution = results.get("distribution_analysis", {})
    if distribution:
        print(f"\n📊 Score Distribution Analysis:")
        pred_stats = distribution.get("predicted_stats", {})
        true_stats = distribution.get("true_stats", {})
        
        print(f"   Predicted scores: Mean={pred_stats.get('mean', 0):.1f}, Std={pred_stats.get('std', 0):.1f}")
        print(f"   Ground truth: Mean={true_stats.get('mean', 0):.1f}, Std={true_stats.get('std', 0):.1f}")
        
        print(f"\n   Range distribution:")
        range_analysis = distribution.get("range_analysis", {})
        for range_name, data in range_analysis.items():
            pred_pct = data.get("predicted_percentage", 0)
            true_pct = data.get("true_percentage", 0)
            print(f"     {range_name}: Predicted={pred_pct:.1f}%, Ground Truth={true_pct:.1f}%")
    
    print(f"\n✅ Accuracy analysis completed successfully!")

if __name__ == "__main__":
    main()
