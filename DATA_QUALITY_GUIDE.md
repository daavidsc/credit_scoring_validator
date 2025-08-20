# Data Quality Analysis - Implementation Guide

## Overview

The data quality analysis feature evaluates the reliability, completeness, and validity of data used in the credit scoring process. This analysis helps identify data-related issues that could impact model performance, compliance, and decision accuracy.

## What is Data Quality Analysis?

Data quality analysis assesses various dimensions of data integrity and reliability in machine learning systems. For credit scoring models, this is essential because:

- **Decision Accuracy**: Poor data quality leads to incorrect credit decisions
- **Regulatory Compliance**: Financial regulations require high data quality standards
- **Risk Management**: Data quality issues can introduce hidden risks
- **Model Performance**: Clean, accurate data is fundamental to model effectiveness
- **Customer Experience**: Data errors can result in unfair treatment of applicants

## Data Quality Analysis: Technical Deep Dive

### Data Quality Dimensions Framework

The system evaluates six critical dimensions of data quality:

**1. Completeness**: Percentage of missing or null values
**2. Accuracy**: Correctness of data values and formats
**3. Consistency**: Uniformity of data representation and encoding
**4. Validity**: Adherence to expected data types and ranges
**5. Timeliness**: Freshness and relevance of data
**6. Uniqueness**: Absence of duplicate records

### Error Rate Analysis Algorithm

```python
def calculate_error_rates(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate comprehensive error rates and quality metrics"""
    total_requests = len(responses)
    
    if total_requests == 0:
        return {"total_requests": 0, "error_rate": 0.0, "data_quality_score": 0.0}
    
    # Define error taxonomy
    error_counts = {
        "http_error": 0,      # HTTP 4xx/5xx status codes
        "timeout": 0,         # Request timeout errors
        "connection_error": 0, # Network connectivity issues
        "request_error": 0,   # Malformed request errors
        "unknown_error": 0,   # Unclassified errors
        "parsing_error": 0,   # Response parsing failures
        "missing_score": 0    # Missing credit score in response
    }
    
    successful_requests = 0
    valid_scores = 0
    
    for response in responses:
        # Classify response type
        has_error = "error" in response or "error_type" in response
        
        if not has_error and "output" in response:
            successful_requests += 1
            
            # Validate parsed response structure
            parsed = response["output"].get("parsed", {})
            if parsed and parsed.get("credit_score") is not None:
                valid_scores += 1
            else:
                error_counts["missing_score"] += 1
            
            # Check for parsing completeness
            if not parsed:
                error_counts["parsing_error"] += 1
                
        else:
            # Categorize error type
            error_type = response.get("error_type", "unknown_error")
            if error_type in error_counts:
                error_counts[error_type] += 1
            else:
                error_counts["unknown_error"] += 1
    
    # Calculate quality metrics
    error_rate = ((total_requests - successful_requests) / total_requests) * 100
    success_rate = (successful_requests / total_requests) * 100
    valid_score_rate = (valid_scores / total_requests) * 100
    data_quality_score = (valid_scores / total_requests) * 100
    
    return {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "valid_scores": valid_scores,
        "error_rate": error_rate,
        "success_rate": success_rate,
        "valid_score_rate": valid_score_rate,
        "data_quality_score": data_quality_score,
        "error_breakdown": {
            error_type: {"count": count, "percentage": (count / total_requests) * 100}
            for error_type, count in error_counts.items() if count > 0
        }
    }
```

### Response Completeness Analysis

```python
def analyze_response_completeness(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze structural completeness of API responses"""
    total_responses = len(responses)
    
    if total_responses == 0:
        return {"completeness_score": 0.0, "issues": {}}
    
    # Define completeness criteria
    completeness_issues = {
        "missing_credit_score": 0,    # No credit score in response
        "missing_classification": 0,  # No classification (approve/deny)
        "missing_explanation": 0,     # No reasoning/explanation
        "empty_response": 0,          # Completely empty parsed response
        "malformed_response": 0       # Structurally invalid response
    }
    
    complete_responses = 0
    
    for response in responses:
        has_error = "error" in response or "error_type" in response
        
        if not has_error and "output" in response:
            parsed = response["output"].get("parsed", {})
            
            if not parsed:
                completeness_issues["empty_response"] += 1
                continue
            
            # Check each required field
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
            
            # Count as complete only if no issues found
            if not issues_found:
                complete_responses += 1
        else:
            completeness_issues["malformed_response"] += 1
    
    completeness_score = (complete_responses / total_responses) * 100
    
    # Create issues summary with percentages
    issues_summary = {
        issue_type: {
            "count": count,
            "percentage": (count / total_responses) * 100
        }
        for issue_type, count in completeness_issues.items() if count > 0
    }
    
    return {
        "completeness_score": completeness_score,
        "complete_responses": complete_responses,
        "total_responses": total_responses,
        "issues": issues_summary
    }
```

### Multi-Module Quality Assessment

```python
def analyze_module_breakdown(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze quality metrics by analysis module for targeted improvements"""
    module_stats = {}
    
    for response in responses:
        module = response.get("module", "unknown")
        
        # Initialize module statistics
        if module not in module_stats:
            module_stats[module] = {
                "total_requests": 0,
                "successful_requests": 0,
                "error_count": 0,
                "valid_scores": 0
            }
        
        module_stats[module]["total_requests"] += 1
        
        # Classify response outcome
        has_error = "error" in response or "error_type" in response
        
        if not has_error and "output" in response:
            module_stats[module]["successful_requests"] += 1
            
            # Validate response data quality
            parsed = response["output"].get("parsed", {})
            if parsed and parsed.get("credit_score") is not None:
                module_stats[module]["valid_scores"] += 1
        else:
            module_stats[module]["error_count"] += 1
    
    # Calculate quality rates per module
    for module, stats in module_stats.items():
        total = stats["total_requests"]
        if total > 0:
            stats["success_rate"] = (stats["successful_requests"] / total) * 100
            stats["error_rate"] = (stats["error_count"] / total) * 100
            stats["valid_score_rate"] = (stats["valid_scores"] / total) * 100
            stats["quality_score"] = stats["valid_score_rate"]  # Alias for consistency
        else:
            stats.update({
                "success_rate": 0.0, "error_rate": 0.0, 
                "valid_score_rate": 0.0, "quality_score": 0.0
            })
    
    return module_stats
```

### Comprehensive Quality Summary Generation

```python
def generate_data_quality_summary(responses: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generate comprehensive quality assessment across all system components"""
    
    if responses is None:
        # Aggregate responses from global collector
        from utils.response_collector import get_collector
        collector = get_collector()
        all_responses = collector.get_all_responses()
        
        # Convert collector format to analysis format
        responses = []
        for response in all_responses:
            converted_response = {
                "input": response.get("input", {}),
                "output": response.get("output", {}),
                "module": response.get("module", "unknown")
            }
            
            # Preserve error information for compatibility
            output = response.get("output", {})
            if "error_type" in output:
                converted_response["error_type"] = output["error_type"]
                converted_response["error"] = output.get("error")
            
            responses.append(converted_response)
    
    # Calculate all quality metrics
    error_metrics = calculate_error_rates(responses)
    completeness_metrics = analyze_response_completeness(responses)
    response_time_metrics = calculate_response_time_metrics(responses)
    module_breakdown = analyze_module_breakdown(responses)
    
    # Determine overall quality classification
    quality_score = error_metrics["data_quality_score"]
    quality_level, quality_color = classify_quality_level(quality_score)
    
    return {
        "overall_quality": {
            "score": quality_score,
            "level": quality_level,
            "color": quality_color
        },
        "error_metrics": error_metrics,
        "completeness_metrics": completeness_metrics,
        "response_time_metrics": response_time_metrics,
        "module_breakdown": module_breakdown,
        "recommendations": generate_quality_recommendations(error_metrics, completeness_metrics)
    }

def classify_quality_level(quality_score: float) -> Tuple[str, str]:
    """Classify quality score into level and display color"""
    if quality_score >= 95:
        return "Excellent", "#27ae60"  # Green
    elif quality_score >= 90:
        return "Good", "#f39c12"       # Orange
    elif quality_score >= 80:
        return "Fair", "#e67e22"       # Dark Orange
    else:
        return "Poor", "#e74c3c"       # Red
```

### Intelligent Quality Recommendations

```python
def generate_quality_recommendations(error_metrics: Dict, completeness_metrics: Dict) -> List[str]:
    """Generate actionable recommendations based on quality analysis"""
    recommendations = []
    
    # Error rate analysis
    if error_metrics["error_rate"] > 10:
        recommendations.append(
            "High error rate detected (>10%). Review API endpoint stability, "
            "network connectivity, and authentication mechanisms."
        )
    
    # Timeout analysis
    timeout_errors = error_metrics["error_breakdown"].get("timeout", {}).get("count", 0)
    if timeout_errors > 0:
        recommendations.append(
            f"Timeout errors detected ({timeout_errors} instances). "
            "Consider increasing request timeout or optimizing API response time."
        )
    
    # HTTP error analysis
    http_errors = error_metrics["error_breakdown"].get("http_error", {}).get("count", 0)
    if http_errors > 0:
        recommendations.append(
            f"HTTP errors detected ({http_errors} instances). "
            "Review API authentication, request formatting, and endpoint availability."
        )
    
    # Completeness analysis
    if completeness_metrics["completeness_score"] < 90:
        recommendations.append(
            f"Response completeness below optimal ({completeness_metrics['completeness_score']:.1f}%). "
            "Review API response format and parsing logic for consistency."
        )
    
    # Missing score analysis
    issues = completeness_metrics.get("issues", {})
    missing_scores = issues.get("missing_credit_score", {}).get("count", 0)
    if missing_scores > 0:
        recommendations.append(
            f"Missing credit scores detected ({missing_scores} instances). "
            "This may indicate model processing issues or incomplete API responses."
        )
    
    # Success case
    if len(recommendations) == 0:
        recommendations.append(
            "Data quality is excellent. No immediate action required. "
            "Continue monitoring for quality degradation."
        )
    
    return recommendations
```

### Real-World Quality Analysis Example

**Sample Data Quality Report**:

```json
{
  "overall_quality": {
    "score": 87.5,
    "level": "Good",
    "color": "#f39c12"
  },
  "error_metrics": {
    "total_requests": 200,
    "successful_requests": 185,
    "valid_scores": 175,
    "error_rate": 7.5,
    "success_rate": 92.5,
    "data_quality_score": 87.5,
    "error_breakdown": {
      "timeout": {"count": 8, "percentage": 4.0},
      "http_error": {"count": 5, "percentage": 2.5},
      "missing_score": {"count": 10, "percentage": 5.0}
    }
  },
  "completeness_metrics": {
    "completeness_score": 94.6,
    "complete_responses": 175,
    "total_responses": 185,
    "issues": {
      "missing_explanation": {"count": 8, "percentage": 4.3},
      "missing_classification": {"count": 2, "percentage": 1.1}
    }
  },
  "module_breakdown": {
    "accuracy": {
      "total_requests": 50,
      "success_rate": 96.0,
      "quality_score": 94.0
    },
    "bias_fairness": {
      "total_requests": 75,
      "success_rate": 89.3,
      "quality_score": 85.3
    },
    "consistency": {
      "total_requests": 45,
      "success_rate": 95.6,
      "quality_score": 91.1
    },
    "robustness": {
      "total_requests": 30,
      "success_rate": 90.0,
      "quality_score": 83.3
    }
  },
  "recommendations": [
    "Timeout errors detected (8 instances). Consider increasing request timeout or optimizing API response time.",
    "HTTP errors detected (5 instances). Review API authentication and request formatting.",
    "Missing explanations in 4.3% of responses. Review explanation generation logic."
  ]
}
```

### Quality Monitoring Integration

```python
def calculate_response_time_metrics(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate response time and performance metrics"""
    # Extract timing information if available
    response_times = []
    timeout_count = 0
    
    for response in responses:
        # Check for timeout errors
        if response.get("error_type") == "timeout":
            timeout_count += 1
        
        # Extract response time if tracked
        if "response_time" in response:
            response_times.append(response["response_time"])
    
    if response_times:
        import numpy as np
        return {
            "average_response_time": np.mean(response_times),
            "min_response_time": np.min(response_times),
            "max_response_time": np.max(response_times),
            "median_response_time": np.median(response_times),
            "p95_response_time": np.percentile(response_times, 95),
            "timeout_count": timeout_count,
            "response_time_samples": len(response_times)
        }
    else:
        return {
            "average_response_time": None,
            "min_response_time": None,
            "max_response_time": None,
            "timeout_count": timeout_count,
            "message": "Response timing data not available"
        }
```

### Data Quality Thresholds and Alerts

**Quality Score Interpretation**:

- **Excellent (95-100%)**: Production ready, no immediate concerns
- **Good (90-95%)**: Acceptable quality, minor monitoring recommended  
- **Fair (80-90%)**: Moderate quality issues, investigation recommended
- **Poor (<80%)**: Significant quality problems, immediate action required

**Alert Thresholds**:
- Error rate > 15%: Critical alert
- Completeness score < 85%: Warning alert
- Missing scores > 10%: Investigation alert
- Timeout rate > 5%: Performance alert

## How It Works

## Files Overview

### Core Implementation

1. **`analysis/data_quality.py`** - Main data quality analysis module
   - Error rate calculation algorithms
   - Data completeness assessment
   - Quality scoring mechanisms
   - Statistical validation methods

2. **`tests/test_data_quality.py`** - Comprehensive unit tests
   - Quality metric validation
   - Edge case handling
   - Statistical computation verification

### Integration Points

1. Used by other analysis modules (bias_fairness.py, accuracy.py)
2. Integrated into report generation system
3. Provides data quality scores for overall assessment

## Key Functions

### `calculate_error_rates(responses)`
Calculates comprehensive error rates and data quality metrics from API responses.

**Parameters:**
- `responses`: List of API response dictionaries

**Returns:**
```python
{
    "total_requests": int,
    "error_rate": float,
    "error_breakdown": dict,
    "success_rate": float,
    "data_quality_score": float
}
```

**Error Categories Tracked:**
- `http_error`: HTTP status code errors (4xx, 5xx)
- `timeout`: Request timeout failures
- `connection_error`: Network connectivity issues
- `request_error`: Malformed request problems
- `unknown_error`: Unclassified errors
- `parsing_error`: Response parsing failures
- `missing_score`: Missing or invalid credit scores

### `validate_response_structure(response)`
Validates the structure and content of individual API responses.

**Validation Checks:**
- Presence of required fields
- Data type validation
- Score range validation
- Response format consistency

### `assess_data_completeness(data)`
Analyzes completeness across data fields and records.

**Metrics:**
- Field population rates
- Critical field missing rates
- Overall completeness score
- Pattern analysis of missing data

### `generate_data_quality_summary(responses)`
Creates a comprehensive data quality assessment summary.

**Summary Components:**
- Overall quality score (0-100%)
- Error distribution breakdown
- Completeness statistics
- Validity assessment
- Recommendations for improvement

## Usage

### As Part of Other Analyses

Data quality analysis is automatically integrated into other analysis modules:

```python
from analysis.data_quality import generate_data_quality_summary

# Used within other analysis functions
def run_accuracy_analysis():
    # ... collect responses ...
    quality_summary = generate_data_quality_summary(responses)
    # Use quality insights to interpret accuracy results
```

### Standalone Quality Assessment

```python
from analysis.data_quality import calculate_error_rates, assess_data_completeness

# Analyze API response quality
responses = load_api_responses()
error_metrics = calculate_error_rates(responses)
completeness_metrics = assess_data_completeness(responses)

# Check quality thresholds
if error_metrics['error_rate'] > 0.05:  # More than 5% errors
    print("High error rate detected - investigate API issues")

if completeness_metrics['completeness_score'] < 0.90:  # Less than 90% complete
    print("Data completeness issues detected")
```

## Quality Metrics and Thresholds

### Error Rate Analysis

**Excellent Quality (< 1% error rate):**
- System operating smoothly
- High reliability and availability
- Suitable for production use

**Good Quality (1-3% error rate):**
- Minor technical issues
- Acceptable for most scenarios
- Monitor for trend changes

**Moderate Quality (3-10% error rate):**
- Noticeable reliability issues
- Investigate root causes
- May impact analysis accuracy

**Poor Quality (> 10% error rate):**
- Significant system problems
- Analysis results unreliable
- Immediate remediation required

### Completeness Scoring

**Data Completeness Score:**
```
Score = (Populated Fields / Total Expected Fields) * 100%
```

**Critical Field Completeness:**
- Credit score: Must be present and valid
- Decision field: Required for classification analysis
- Key demographics: Important for fairness analysis

### Success Rate Calculation

**Success Rate Components:**
- API call completion rate
- Response parsing success rate
- Data validation pass rate
- Overall system reliability score

## Data Quality Dimensions

### 1. Completeness

**Assessment Criteria:**
- Missing value percentages
- Critical field availability
- Optional field population rates
- Data coverage across profiles

**Impact on Analysis:**
- Incomplete data reduces sample sizes
- Missing critical fields invalidate records
- Systematic missingness introduces bias

### 2. Accuracy

**Validation Methods:**
- Data type checking
- Range validation
- Format compliance
- Cross-field consistency

**Common Issues:**
- Scores outside valid ranges (0-850 or 0-100)
- Invalid data types (strings where numbers expected)
- Inconsistent formatting

### 3. Consistency

**Consistency Checks:**
- Uniform data representation
- Consistent field naming
- Standardized value encodings
- Temporal consistency

**Examples:**
- Date formats: "2023-01-01" vs "01/01/2023"
- Boolean values: true/false vs 1/0 vs Yes/No
- Case sensitivity: "Male" vs "male" vs "MALE"

### 4. Validity

**Validation Rules:**
- Credit scores: 300-850 (FICO) or 0-100 (custom)
- Age ranges: 18-100 years
- Income values: > 0 and reasonable maximum
- Percentage fields: 0-100%

### 5. Timeliness

**Time-related Quality:**
- Response time consistency
- Data freshness indicators
- Temporal data validity
- Processing time patterns

## Quality Issue Classification

### Technical Errors

**HTTP Errors:**
- 400 Bad Request: Invalid input data
- 401 Unauthorized: Authentication issues
- 403 Forbidden: Access permission problems
- 404 Not Found: Endpoint or resource issues
- 500 Internal Server Error: Server-side problems
- 502 Bad Gateway: Proxy or load balancer issues
- 503 Service Unavailable: System overload
- 504 Gateway Timeout: Processing time limits exceeded

**Connection Issues:**
- Network connectivity problems
- DNS resolution failures
- SSL/TLS certificate issues
- Connection timeout problems

### Data-Related Errors

**Parsing Failures:**
- Invalid JSON/XML format
- Unexpected response structure
- Character encoding issues
- Truncated responses

**Validation Failures:**
- Missing required fields
- Invalid data types
- Out-of-range values
- Inconsistent formats

## Best Practices

### For Data Engineers

1. **Proactive Monitoring**: Set up automated data quality checks
2. **Error Handling**: Implement robust error detection and logging
3. **Data Validation**: Create comprehensive validation rules
4. **Quality Metrics**: Track quality trends over time
5. **Alerting Systems**: Set up notifications for quality degradation

### For Model Developers

1. **Quality-Aware Analysis**: Consider data quality in model interpretation
2. **Robust Features**: Design features that handle missing data gracefully
3. **Quality Thresholds**: Set minimum quality requirements for model training
4. **Documentation**: Document data quality assumptions and requirements

### for Operations Teams

1. **System Health**: Monitor API performance and availability
2. **Capacity Planning**: Ensure adequate system resources
3. **Maintenance Windows**: Schedule updates to minimize disruption
4. **Incident Response**: Develop procedures for quality issues

## Integration with Other Analyses

### Accuracy Analysis Integration

```python
def run_accuracy_analysis():
    # ... collect responses ...
    
    # Assess data quality first
    quality_summary = generate_data_quality_summary(responses)
    
    # Filter out low-quality responses for accuracy calculation
    high_quality_responses = filter_by_quality(responses, quality_summary)
    
    # Calculate accuracy metrics on clean data
    accuracy_metrics = calculate_accuracy_metrics(high_quality_responses)
    
    # Include quality context in results
    results = {
        'accuracy_metrics': accuracy_metrics,
        'data_quality': quality_summary,
        'data_filtering_applied': len(responses) != len(high_quality_responses)
    }
```

### Bias Analysis Integration

Data quality issues can introduce or mask bias:

- **Systematic Missingness**: Missing data patterns correlated with demographics
- **Quality Disparities**: Different error rates across demographic groups
- **Representation Issues**: Uneven data quality affecting fairness analysis

## Reporting and Visualization

### Quality Dashboard Components

1. **Overall Quality Score**: Single metric summary (0-100%)
2. **Error Rate Trends**: Time-series visualization of error rates
3. **Completeness Heatmap**: Field-by-field completeness visualization
4. **Error Distribution**: Pie chart of error types
5. **Quality Alerts**: List of current quality issues

### Detailed Quality Reports

```python
quality_report = {
    "summary": {
        "overall_score": 87.5,
        "total_records": 1000,
        "quality_grade": "Good"
    },
    "completeness": {
        "critical_fields": 98.2,
        "optional_fields": 76.3,
        "overall": 89.1
    },
    "accuracy": {
        "format_compliance": 94.7,
        "range_validation": 91.2,
        "type_validation": 97.8
    },
    "system_reliability": {
        "api_success_rate": 96.8,
        "response_time_avg": 245.7,
        "error_rate": 3.2
    }
}
```

## Testing

The implementation includes comprehensive test coverage:

### Unit Tests

- Error rate calculation verification
- Quality metric computation validation
- Edge case handling (empty datasets, all errors)
- Statistical computation accuracy

### Integration Tests

- End-to-end quality assessment workflow
- Integration with other analysis modules
- Report generation validation

Run tests with:
```bash
python -m pytest tests/test_data_quality.py -v
```

## Troubleshooting

### High Error Rates

**Investigation Steps:**
1. Check API endpoint availability
2. Verify authentication credentials
3. Review request format and parameters
4. Analyze error patterns and timing
5. Check network connectivity and firewalls

**Common Solutions:**
- Update API endpoints or credentials
- Adjust request timeout settings
- Implement retry logic with exponential backoff
- Address network configuration issues

### Poor Data Completeness

**Root Cause Analysis:**
1. Identify which fields are frequently missing
2. Determine if missing data is systematic or random
3. Check if missing data correlates with other variables
4. Review data collection and preprocessing steps

**Improvement Strategies:**
- Enhance data collection processes
- Implement data imputation techniques
- Update validation rules
- Improve error handling in data pipelines

### Quality Score Degradation

**Monitoring Approach:**
1. Set up automated quality monitoring
2. Track quality trends over time
3. Create alerts for threshold violations
4. Implement quality dashboards

## Future Enhancements

Potential improvements to consider:

1. **Advanced Quality Metrics**:
   - Statistical outlier detection
   - Data drift identification
   - Quality prediction modeling
   - Cross-validation quality assessment

2. **Real-time Quality Monitoring**:
   - Streaming quality assessment
   - Real-time alerting systems
   - Dynamic quality thresholds
   - Automated quality remediation

3. **Enhanced Data Validation**:
   - Machine learning-based validation
   - Business rule validation engine
   - Cross-field dependency checking
   - Historical comparison validation

4. **Quality Improvement Automation**:
   - Automated data cleaning pipelines
   - Quality-driven data collection
   - Self-healing data systems
   - Intelligent error recovery

## Conclusion

The data quality analysis feature provides essential validation of data integrity and reliability in credit scoring systems. It helps identify and address data-related issues that could impact model performance, compliance, and decision accuracy. The implementation follows data quality best practices and provides comprehensive insights for maintaining high-quality data pipelines.
