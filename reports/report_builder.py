# reports/report_builder.py

import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = "reports/templates"
OUTPUT_DIR = "reports/generated"

def load_analysis_results(path):
    with open(path, "r") as f:
        return json.load(f)

def build_bias_fairness_report(data, output_filename="bias_report.html"):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("report_template.html")

    rendered = template.render(results=data)

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, "w") as f:
        f.write(rendered)

    print(f"✅ Bias Report saved to {output_path}")


def build_accuracy_report(data, output_filename="accuracy_report.html"):
    """Build accuracy analysis report"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("accuracy_template.html")

    rendered = template.render(results=data)

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, "w") as f:
        f.write(rendered)

    print(f"✅ Accuracy Report saved to {output_path}")


def build_robustness_report(data, output_filename="robustness_report.html"):
    """Build robustness analysis report"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("robustness_template.html")
    
    # Determine score class for styling
    robustness_score = data.get("robustness_score", 0)
    if robustness_score >= 0.8:
        score_class = "score-excellent"
    elif robustness_score >= 0.6:
        score_class = "score-good"
    elif robustness_score >= 0.4:
        score_class = "score-fair"
    else:
        score_class = "score-poor"
    
    # Prepare template variables
    template_vars = {
        "robustness_score": robustness_score,
        "score_class": score_class,
        "total_examples": data.get("total_examples", 0),
        "decision_consistency_rate": data.get("decision_consistency", {}).get("rate", 0),
        "consistent_decisions": data.get("decision_consistency", {}).get("consistent_count", 0),
        "confidence_stats": data.get("confidence_stability"),
        "perturbation_analysis": data.get("perturbation_analysis", {}),
        "failure_cases": data.get("failure_cases", []),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    rendered = template.render(**template_vars)

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, "w") as f:
        f.write(rendered)

    print(f"✅ Robustness Report saved to {output_path}")


def build_consistency_report(data, output_filename="consistency_report.html"):
    """Build consistency analysis report"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("consistency_template.html")
    
    # Determine score class for styling
    consistency_score = data.get("overall_consistency_score", 0)
    if consistency_score >= 0.9:
        score_class = "score-excellent"
    elif consistency_score >= 0.7:
        score_class = "score-good"
    elif consistency_score >= 0.5:
        score_class = "score-fair"
    else:
        score_class = "score-poor"
    
    # Prepare template variables
    template_vars = {
        "overall_consistency_score": consistency_score,
        "score_class": score_class,
        "total_inputs": data.get("total_inputs", 0),
        "total_responses": data.get("total_responses", 0),
        "perfect_consistency": data.get("perfect_consistency", 0),
        "decision_consistency": data.get("decision_consistency", 0),
        "confidence_consistency": data.get("confidence_consistency", 0),
        "statistics": data.get("statistics", {}),
        "consistency_by_input": data.get("consistency_by_input", []),
        "inconsistent_cases": data.get("inconsistent_cases", []),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    rendered = template.render(**template_vars)

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, "w") as f:
        f.write(rendered)

    print(f"✅ Consistency Report saved to {output_path}")

def build_transparency_report(data, output_filename="transparency_report.html"):
    """Build transparency analysis report"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("transparency_template.html")
    
    # Extract summary data
    summary = data.get("summary", {})
    
    # Determine score class for styling
    avg_quality_score = summary.get("average_quality_score", 0)
    if avg_quality_score >= 90:
        score_class = "score-excellent"
    elif avg_quality_score >= 80:
        score_class = "score-good"
    elif avg_quality_score >= 70:
        score_class = "score-fair"
    else:
        score_class = "score-poor"
    
    # Prepare template variables
    template_vars = {
        "summary": summary,
        "average_quality_score": avg_quality_score,
        "score_class": score_class,
        "total_analyzed": summary.get("total_analyzed", 0),
        "compliance_rate": summary.get("compliance_rate", 0),
        "category_distribution": summary.get("category_distribution", {}),
        "dimension_analysis": summary.get("dimension_analysis", {}),
        "lime_quality": summary.get("lime_quality", {}),
        "recommendations": summary.get("recommendations", []),
        "detailed_results": data.get("detailed_results", [])[:10],  # Show first 10 detailed results
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    rendered = template.render(**template_vars)

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, "w") as f:
        f.write(rendered)

    print(f"✅ Transparency Report saved to {output_path}")

def build_comprehensive_data_quality_report(data, output_filename="comprehensive_data_quality_report.html"):
    """Build comprehensive data quality report from analysis results"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("comprehensive_data_quality_template.html")
    
    # Prepare template variables
    template_vars = {
        "data_quality": data.get("data_quality", {}),
        "total_responses_analyzed": data.get("total_responses_analyzed", 0),
        "module_breakdown": data.get("module_breakdown", {}),
        "comprehensive_data_file": data.get("comprehensive_data_file"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    rendered = template.render(**template_vars)
    
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, "w") as f:
        f.write(rendered)
    
    print(f"✅ Comprehensive Data Quality Report saved to {output_path}")
    return output_path
