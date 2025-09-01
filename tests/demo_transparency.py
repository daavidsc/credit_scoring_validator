#!/usr/bin/env python3
"""
Demonstration script for the transparency analysis functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.transparency import run_transparency_analysis
from reports.report_builder import build_transparency_report
import json

def main():
    """Run transparency analysis and display results"""
    print("🔍 Credit Scoring Transparency Analysis")
    print("=" * 50)
    
    # Run the analysis
    print("Running transparency analysis...")
    results = run_transparency_analysis(sample_size=10)  # Small sample for demo
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Display summary
    summary = results.get("summary", {})
    print(f"\n📊 Summary:")
    print(f"   Total analyzed: {summary.get('total_analyzed', 0)}")
    print(f"   Average quality score: {summary.get('average_quality_score', 0):.1f}")
    print(f"   Compliance rate: {summary.get('compliance_rate', 0):.1%}")
    
    # Display category distribution
    category_dist = summary.get("category_distribution", {})
    if category_dist:
        print(f"\n🏆 Quality Distribution:")
        for category, count in category_dist.items():
            if count > 0:
                print(f"   {category.title()}: {count}")
    
    # Display dimension analysis
    dimension_analysis = summary.get("dimension_analysis", {})
    if dimension_analysis:
        print(f"\n📈 Dimension Analysis (Averages):")
        for dimension, stats in dimension_analysis.items():
            avg_score = stats.get('average', 0)
            dimension_name = dimension.replace('_', ' ').title()
            print(f"   {dimension_name}: {avg_score:.2f}")
    
    # Display LIME quality
    lime_quality = summary.get("lime_quality", {})
    if lime_quality:
        print(f"\n🔍 LIME Analysis Quality:")
        print(f"   Average R² Score: {lime_quality.get('average_r2', 0):.3f}")
        print(f"   Median R² Score: {lime_quality.get('median_r2', 0):.3f}")
    
    # Display recommendations
    recommendations = summary.get("recommendations", [])
    if recommendations:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    
    # Show some detailed examples
    detailed_results = results.get("detailed_results", [])
    if detailed_results:
        print(f"\n🔍 Example Analysis (First 3):")
        for i, result in enumerate(detailed_results[:3], 1):
            print(f"\n   Example {i}:")
            print(f"     Quality Score: {result.get('quality_score', 0):.1f} ({result.get('quality_category', 'unknown')})")
            print(f"     Compliant: {'Yes' if result.get('is_compliant', False) else 'No'}")
            
            # Show profile summary
            profile = result.get('profile', {})
            print(f"     Profile: Age {profile.get('age', '?')}, Income ${profile.get('income', '?'):,}, Credit Score {profile.get('credit_score', '?')}")
            
            # Show explanation excerpt
            explanation = result.get('explanation_text', '')
            if explanation:
                excerpt = explanation[:100] + "..." if len(explanation) > 100 else explanation
                print(f"     Explanation: {excerpt}")
            
            # Show top LIME features
            lime_results = result.get('lime_results', {})
            if lime_results and not lime_results.get('error'):
                top_features = lime_results.get('top_positive_features', [])[:2]
                if top_features:
                    print(f"     Top LIME Features: {', '.join([f'{name} (+{imp:.3f})' for name, imp in top_features])}")
    
    # Build report
    print(f"\n📄 Building HTML report...")
    try:
        build_transparency_report(results)
        print(f"✅ Transparency analysis complete!")
        print(f"📁 Report saved to: reports/generated/transparency_report.html")
    except Exception as e:
        print(f"❌ Error building report: {str(e)}")
    
    print(f"\n🎯 Analysis Details:")
    print(f"   Total responses processed: {results.get('total_responses', 0)}")
    if summary.get('average_quality_score', 0) >= 80:
        print(f"   🟢 Overall quality is GOOD - explanations are production-ready")
    elif summary.get('average_quality_score', 0) >= 70:
        print(f"   🟡 Overall quality is FAIR - some improvements recommended")
    else:
        print(f"   🔴 Overall quality is POOR - significant improvements needed")

if __name__ == "__main__":
    main()
