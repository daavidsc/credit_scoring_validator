# analysis/data_quality.py

import pandas as pd
import json
from typing import Dict, List, Any
from utils.logger import setup_logger

logger = setup_logger("data_quality", "results/logs/data_quality.log")

def calculate_error_rates(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate various error rates and data quality metrics from API responses"""
    total_requests = len(responses)
    
    if total_requests == 0:
        return {
            "total_requests": 0,
            "error_rate": 0.0,
            "error_breakdown": {},
            "success_rate": 0.0,
            "data_quality_score": 0.0
        }
    
    error_counts = {
        "http_error": 0,
        "timeout": 0, 
        "connection_error": 0,
        "request_error": 0,
        "unknown_error": 0,
        "parsing_error": 0,
        "missing_score": 0
    }
    
    successful_requests = 0
    valid_scores = 0
    incomplete_responses = 0
    
    for response in responses:
        # Check if this was a successful API call (no 'error' key means success)
        has_error = "error" in response or "error_type" in response
        
        if not has_error and "output" in response:
            successful_requests += 1
            
            # Check if we got a valid parsed response
            parsed = response["output"].get("parsed", {})
            if parsed and parsed.get("credit_score") is not None:
                valid_scores += 1
            elif not parsed or not parsed.get("credit_score"):
                error_counts["missing_score"] += 1
                incomplete_responses += 1
            
            # Check for parsing issues
            if not parsed:
                error_counts["parsing_error"] += 1
                
        else:
            # This was an error response
            error_type = response.get("error_type", "unknown_error")
            if error_type in error_counts:
                error_counts[error_type] += 1
            else:
                error_counts["unknown_error"] += 1
    
    # Calculate rates
    total_errors = total_requests - successful_requests
    error_rate = (total_errors / total_requests) * 100
    success_rate = (successful_requests / total_requests) * 100
    valid_score_rate = (valid_scores / total_requests) * 100
    
    # Calculate data quality score (combination of success rate and completeness)
    data_quality_score = (valid_scores / total_requests) * 100
    
    # Create error breakdown with percentages
    error_breakdown = {}
    for error_type, count in error_counts.items():
        if count > 0:
            error_breakdown[error_type] = {
                "count": count,
                "percentage": (count / total_requests) * 100
            }
    
    logger.info(f"Data Quality Analysis: {total_requests} requests, "
                f"{error_rate:.1f}% error rate, {data_quality_score:.1f}% quality score")
    
    return {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "valid_scores": valid_scores,
        "error_rate": error_rate,
        "success_rate": success_rate,
        "valid_score_rate": valid_score_rate,
        "data_quality_score": data_quality_score,
        "error_breakdown": error_breakdown,
        "incomplete_responses": incomplete_responses
    }

def analyze_response_completeness(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze the completeness of API responses"""
    total_responses = len(responses)
    
    if total_responses == 0:
        return {"completeness_score": 0.0, "issues": []}
    
    completeness_issues = {
        "missing_credit_score": 0,
        "missing_classification": 0,
        "missing_explanation": 0,
        "empty_response": 0,
        "malformed_response": 0
    }
    
    complete_responses = 0
    
    for response in responses:
        # Check if this is an error response
        has_error = "error" in response or "error_type" in response
        
        if not has_error and "output" in response:
            parsed = response["output"].get("parsed", {})
            
            if not parsed:
                completeness_issues["empty_response"] += 1
                continue
                
            issues_found = False
            
            if not parsed.get("credit_score"):
                completeness_issues["missing_credit_score"] += 1
                issues_found = True
                
            if not parsed.get("classification"):
                completeness_issues["missing_classification"] += 1
                issues_found = True
                
            if not parsed.get("explanation"):
                completeness_issues["missing_explanation"] += 1
                issues_found = True
                
            if not issues_found:
                complete_responses += 1
        else:
            # Error responses are considered incomplete
            completeness_issues["malformed_response"] += 1
    
    completeness_score = (complete_responses / total_responses) * 100
    
    # Convert to percentages and filter out zero counts
    issues_summary = {}
    for issue_type, count in completeness_issues.items():
        if count > 0:
            issues_summary[issue_type] = {
                "count": count,
                "percentage": (count / total_responses) * 100
            }
    
    return {
        "completeness_score": completeness_score,
        "complete_responses": complete_responses,
        "total_responses": total_responses,
        "issues": issues_summary
    }

def calculate_response_time_metrics(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate response time metrics if available"""
    # Note: This would require modifying the API client to track response times
    # For now, we'll return a placeholder structure
    return {
        "average_response_time": None,
        "min_response_time": None,
        "max_response_time": None,
        "timeout_count": sum(1 for r in responses if r.get("error_type") == "timeout")
    }

def generate_data_quality_summary(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a comprehensive data quality summary"""
    error_metrics = calculate_error_rates(responses)
    completeness_metrics = analyze_response_completeness(responses)
    response_time_metrics = calculate_response_time_metrics(responses)
    
    # Determine overall quality level
    quality_score = error_metrics["data_quality_score"]
    if quality_score >= 95:
        quality_level = "Excellent"
        quality_color = "#27ae60"  # Green
    elif quality_score >= 90:
        quality_level = "Good"
        quality_color = "#f39c12"  # Orange
    elif quality_score >= 80:
        quality_level = "Fair"
        quality_color = "#e67e22"  # Dark Orange
    else:
        quality_level = "Poor"
        quality_color = "#e74c3c"  # Red
    
    return {
        "overall_quality": {
            "score": quality_score,
            "level": quality_level,
            "color": quality_color
        },
        "error_metrics": error_metrics,
        "completeness_metrics": completeness_metrics,
        "response_time_metrics": response_time_metrics,
        "recommendations": generate_quality_recommendations(error_metrics, completeness_metrics)
    }

def generate_quality_recommendations(error_metrics: Dict, completeness_metrics: Dict) -> List[str]:
    """Generate recommendations based on quality metrics"""
    recommendations = []
    
    if error_metrics["error_rate"] > 10:
        recommendations.append("High error rate detected. Consider reviewing API endpoint stability and network connectivity.")
    
    if error_metrics["error_breakdown"].get("timeout", {}).get("count", 0) > 0:
        recommendations.append("Timeout errors detected. Consider increasing request timeout or optimizing API response time.")
    
    if error_metrics["error_breakdown"].get("http_error", {}).get("count", 0) > 0:
        recommendations.append("HTTP errors detected. Review API authentication and request formatting.")
    
    if completeness_metrics["completeness_score"] < 90:
        recommendations.append("Response completeness is below optimal. Review API response format and parsing logic.")
    
    if completeness_metrics["issues"].get("missing_credit_score", {}).get("count", 0) > 0:
        recommendations.append("Missing credit scores detected. This may indicate model processing issues.")
    
    if len(recommendations) == 0:
        recommendations.append("Data quality is good. No immediate action required.")
    
    return recommendations
