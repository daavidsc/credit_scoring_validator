# analysis/data_quality_analyzer.py

"""
Standalone Data Quality Analyzer

This module provides comprehensive data quality analysis across all analysis modules.
It can be run independently to analyze all collected API responses.
"""

from analysis.data_quality import generate_data_quality_summary
from utils.response_collector import get_collector, reset_collector
from utils.logger import setup_logger
import json

logger = setup_logger("data_quality_analyzer", "results/logs/data_quality.log")

# Reference to global status for progress updates
analysis_status = None

def set_status_reference(status_ref):
    """Set reference to global analysis status"""
    global analysis_status
    analysis_status = status_ref

def run_comprehensive_data_quality_analysis():
    """Run comprehensive data quality analysis on all collected responses"""
    logger.info("Starting comprehensive data quality analysis...")
    
    if analysis_status:
        analysis_status["progress"] = 95
        analysis_status["message"] = "Analyzing data quality across all modules..."
    
    # Get comprehensive data quality summary
    data_quality_summary = generate_data_quality_summary()
    
    collector = get_collector()
    total_responses = collector.get_response_count()
    module_counts = collector.get_module_counts()
    
    logger.info(f"Data quality analysis complete:")
    logger.info(f"  Total responses analyzed: {total_responses}")
    logger.info(f"  Overall quality score: {data_quality_summary['overall_quality']['score']:.1f}%")
    logger.info(f"  Quality level: {data_quality_summary['overall_quality']['level']}")
    
    for module, count in module_counts.items():
        logger.info(f"  {module}: {count} responses")
    
    # Save comprehensive responses to file
    if total_responses > 0:
        output_path = collector.save_all_responses()
        logger.info(f"Saved all {total_responses} responses to {output_path}")
    
    if analysis_status:
        analysis_status["progress"] = 98
        analysis_status["message"] = "Data quality analysis complete!"
    
    return {
        "data_quality": data_quality_summary,
        "total_responses_analyzed": total_responses,
        "module_breakdown": module_counts,
        "comprehensive_data_file": "results/responses/all_responses.jsonl" if total_responses > 0 else None
    }

def save_data_quality_report(results, output_path="results/data_quality_report.json"):
    """Save data quality analysis results to a JSON file"""
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Data quality report saved to {output_path}")

if __name__ == "__main__":
    # Run standalone data quality analysis
    results = run_comprehensive_data_quality_analysis()
    save_data_quality_report(results)
    
    print(f"\n✅ Comprehensive Data Quality Analysis Complete!")
    print(f"📊 Total API Responses Analyzed: {results['total_responses_analyzed']}")
    print(f"🎯 Overall Quality Score: {results['data_quality']['overall_quality']['score']:.1f}%")
    print(f"📈 Quality Level: {results['data_quality']['overall_quality']['level']}")
    print(f"\nModule Breakdown:")
    for module, count in results['module_breakdown'].items():
        print(f"  • {module}: {count} responses")
