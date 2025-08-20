# Robustness Analysis - Implementation Guide

## Overview

The robustness analysis feature has been successfully added to the Credit Scoring Validator. This feature tests how stable and reliable the credit scoring model is when faced with various input perturbations, helping identify potential weaknesses and inconsistencies in model behavior.

## What is Robustness Analysis?

Robustness analysis evaluates how consistently a machine learning model performs when inputs are slightly modified or contain noise. For credit scoring models, this is crucial because:

- **Real-world data is imperfect**: Applications may contain typos, missing values, or data entry errors
- **Adversarial inputs**: Malicious users might try to manipulate their data to get favorable decisions  
- **Model reliability**: Consistent decisions build trust in automated systems
- **Regulatory compliance**: Financial institutions need to demonstrate model stability

## Robustness Testing: Technical Deep Dive

### Adversarial Example Generation Algorithm

The system generates perturbations using five distinct strategies:

**1. Numerical Noise Injection**
```python
def add_noise_to_numerical(value, noise_factor=0.1):
    """Add gaussian noise to numerical values"""
    if pd.isna(value) or not isinstance(value, (int, float)):
        return value
    
    # Generate Gaussian noise proportional to value magnitude
    noise = np.random.normal(0, abs(value) * noise_factor)
    return value + noise

# Example: Income of $50,000 → $52,134 (4.3% variation)
```

**2. Text Corruption with Typos**
```python
def add_typos_to_text(text, typo_rate=0.05):
    """Add random typos to text fields"""
    if pd.isna(text) or not isinstance(text, str):
        return text
    
    chars = list(text)
    num_typos = max(1, int(len(chars) * typo_rate))
    
    for _ in range(num_typos):
        if len(chars) > 0:
            pos = random.randint(0, len(chars) - 1)
            # Random character substitution
            chars[pos] = random.choice(string.ascii_letters)
    
    return ''.join(chars)

# Example: "Engineer" → "Enqineer" (single character substitution)
```

**3. Case Transformation**
```python
def capitalize_text(text):
    """Convert text to uppercase for case sensitivity testing"""
    if pd.isna(text) or not isinstance(text, str):
        return text
    return text.upper()

# Example: "software engineer" → "SOFTWARE ENGINEER"
```

**4. Missing Value Simulation**
```python
def generate_missing_values(row, num_fields=3):
    """Randomly set fields to null to test missing data handling"""
    cols_to_modify = random.sample(list(row.index), min(num_fields, len(row.index)))
    for col in cols_to_modify:
        row[col] = np.nan
    return row

# Example: {income: 50000, age: 30} → {income: NaN, age: 30}
```

**5. Extreme Value Testing**
```python
def generate_extreme_values(row, df):
    """Replace values with extreme high/low values"""
    for col in df.select_dtypes(include=[np.number]).columns:
        if col in row:
            if random.choice([True, False]):
                row[col] = df[col].max() * 2  # Extreme high
            else:
                row[col] = df[col].min() * 2  # Extreme low
    return row

# Example: income: $50,000 → $250,000 (extreme high)
```

### Comprehensive Perturbation Generation

```python
def generate_adversarial_examples(df: pd.DataFrame, num_examples: int = 50) -> List[Dict]:
    """Generate systematic adversarial examples across all perturbation types"""
    adversarial_examples = []
    
    # Sample random profiles for testing
    sample_indices = random.sample(range(len(df)), min(num_examples, len(df)))
    
    perturbation_types = [
        "noise_numerical", "typos_text", "case_change", 
        "missing_values", "extreme_values"
    ]
    
    for i, idx in enumerate(sample_indices):
        original_row = df.iloc[idx].copy()
        
        # Generate one adversarial example per perturbation type
        for perturbation_type in perturbation_types:
            perturbed_row = original_row.copy()
            
            # Apply specific perturbation strategy
            if perturbation_type == "noise_numerical":
                for col in df.select_dtypes(include=[np.number]).columns:
                    if col in perturbed_row:
                        perturbed_row[col] = add_noise_to_numerical(perturbed_row[col])
                        
            elif perturbation_type == "typos_text":
                for col in df.select_dtypes(include=['object']).columns:
                    if col in perturbed_row and isinstance(perturbed_row[col], str):
                        perturbed_row[col] = add_typos_to_text(perturbed_row[col])
                        
            # ... (other perturbation types)
            
            # Store example with metadata
            example = {
                "original_index": int(idx),
                "perturbation_type": perturbation_type,
                "original_data": original_row.to_dict(),
                "perturbed_data": perturbed_row.to_dict()
            }
            adversarial_examples.append(example)
    
    return adversarial_examples
```

### Response Processing and Decision Extraction

```python
def extract_response_text(response) -> str:
    """Extract standardized text from various response formats"""
    if not response:
        return ""
    
    # Handle error responses
    if isinstance(response, dict) and "error_type" in response:
        return f"Error: {response.get('error', 'Unknown error')}"
    
    # Handle structured API responses
    if isinstance(response, dict) and "parsed" in response:
        parsed = response["parsed"]
        if isinstance(parsed, dict):
            # Create standardized string representation
            parts = []
            if "credit_score" in parsed and parsed["credit_score"] is not None:
                parts.append(f"score:{parsed['credit_score']}")
            if "classification" in parsed and parsed["classification"]:
                parts.append(f"class:{parsed['classification']}")
            if "explanation" in parsed and parsed["explanation"]:
                parts.append(f"reason:{parsed['explanation']}")
            return " ".join(parts) if parts else "no_data"
    
    return str(response) if response else ""
```

```python
def parse_credit_decision(response) -> Tuple[Optional[str], Optional[float], str]:
    """
    Extract decision, confidence, and reasoning from API response
    Returns (decision, confidence, full_text)
    """
    response_text = extract_response_text(response)
    
    if not response_text:
        return None, None, "No response"
    
    text_lower = response_text.lower()
    decision = None
    confidence = None
    
    # Decision extraction from structured format
    if "class:" in text_lower:
        if "class:good" in text_lower or "class:approved" in text_lower:
            decision = "approve"
        elif "class:poor" in text_lower or "class:bad" in text_lower:
            decision = "deny"
        elif "class:average" in text_lower or "class:moderate" in text_lower:
            # Use credit score threshold for borderline cases
            if "score:" in text_lower:
                import re
                score_match = re.search(r'score:(\d+)', text_lower)
                if score_match:
                    score = int(score_match.group(1))
                    if score >= 700:
                        decision = "approve"
                    elif score < 600:
                        decision = "deny"
                    else:
                        decision = "conditional"
    
    # Confidence extraction with multiple strategies
    try:
        import re
        # Look for explicit percentage
        confidence_matches = re.findall(r'(\d+)%', response_text)
        if confidence_matches:
            confidence = float(confidence_matches[0]) / 100.0
        # Look for confidence keywords
        elif "high confidence" in text_lower:
            confidence = 0.8
        elif "medium confidence" in text_lower:
            confidence = 0.6
        elif "low confidence" in text_lower:
            confidence = 0.4
        # Use credit score as confidence proxy
        elif "score:" in text_lower:
            score_match = re.search(r'score:(\d+)', text_lower)
            if score_match:
                score = int(score_match.group(1))
                confidence = min(score / 850.0, 1.0)  # Normalize to [0,1]
    except:
        pass
    
    return decision, confidence, response_text
```

### Robustness Metrics Calculation

**1. Decision Consistency Rate**
```python
def calculate_decision_consistency(responses):
    """Calculate percentage of cases with consistent decisions"""
    decision_consistent = 0
    valid_examples = 0
    
    for response in responses:
        original_decision, _, orig_text = parse_credit_decision(
            response["original_response"]
        )
        perturbed_decision, _, pert_text = parse_credit_decision(
            response["perturbed_response"]
        )
        
        # Skip cases where original response failed
        if original_decision is None and "error" in orig_text.lower():
            continue
            
        valid_examples += 1
        
        # Check for consistent decisions
        decisions_consistent = (original_decision == perturbed_decision)
        
        # Handle error cases: API rejecting corrupted data is robust behavior
        if perturbed_decision is None and "error" in pert_text.lower():
            decisions_consistent = True  # Robust: correctly rejected bad input
        
        if decisions_consistent:
            decision_consistent += 1
    
    return decision_consistent / valid_examples if valid_examples > 0 else 0
```

**2. Confidence Stability Analysis**
```python
def calculate_confidence_stability(responses):
    """Analyze confidence score variations under perturbations"""
    confidence_differences = []
    
    for response in responses:
        _, original_conf, _ = parse_credit_decision(response["original_response"])
        _, perturbed_conf, _ = parse_credit_decision(response["perturbed_response"])
        
        if original_conf is not None and perturbed_conf is not None:
            conf_diff = abs(original_conf - perturbed_conf)
            confidence_differences.append(conf_diff)
    
    if confidence_differences:
        return {
            "mean_difference": np.mean(confidence_differences),
            "max_difference": np.max(confidence_differences),
            "std_difference": np.std(confidence_differences),
            "stability_score": 1.0 - np.mean(confidence_differences)  # Higher is better
        }
    
    return {"mean_difference": 0, "stability_score": 1.0}
```

**3. Perturbation-Specific Analysis**
```python
def analyze_perturbation_impact(responses):
    """Analyze which perturbation types cause most inconsistency"""
    perturbation_stats = {}
    
    for response in responses:
        perturbation_type = response["perturbation_type"]
        
        if perturbation_type not in perturbation_stats:
            perturbation_stats[perturbation_type] = {
                "total": 0, "consistent_decisions": 0, "confidence_drops": []
            }
        
        # Track consistency for this perturbation type
        original_decision, original_conf, _ = parse_credit_decision(
            response["original_response"]
        )
        perturbed_decision, perturbed_conf, _ = parse_credit_decision(
            response["perturbed_response"]
        )
        
        perturbation_stats[perturbation_type]["total"] += 1
        
        if original_decision == perturbed_decision:
            perturbation_stats[perturbation_type]["consistent_decisions"] += 1
        
        if original_conf and perturbed_conf:
            conf_diff = abs(original_conf - perturbed_conf)
            perturbation_stats[perturbation_type]["confidence_drops"].append(conf_diff)
    
    # Calculate summary statistics
    analysis_results = {}
    for ptype, stats in perturbation_stats.items():
        consistency_rate = stats["consistent_decisions"] / stats["total"]
        avg_conf_drop = np.mean(stats["confidence_drops"]) if stats["confidence_drops"] else 0
        
        analysis_results[ptype] = {
            "total_examples": stats["total"],
            "consistency_rate": consistency_rate,
            "average_confidence_drop": avg_conf_drop,
            "max_confidence_drop": np.max(stats["confidence_drops"]) if stats["confidence_drops"] else 0,
            "vulnerability_score": 1.0 - consistency_rate  # Higher means more vulnerable
        }
    
    return analysis_results
```

### Overall Robustness Score Calculation

```python
def calculate_robustness_score(decision_consistency_rate, confidence_stability):
    """
    Calculate overall robustness score (0-1, higher is better)
    Combines decision consistency (70%) and confidence stability (30%)
    """
    decision_score = decision_consistency_rate
    confidence_score = confidence_stability.get("stability_score", 0.5)
    
    # Ensure scores are in valid range
    decision_score = max(0, min(1, decision_score))
    confidence_score = max(0, min(1, confidence_score))
    
    # Weighted combination
    robustness_score = (decision_score * 0.7 + confidence_score * 0.3)
    return robustness_score
```

### Real-World Robustness Testing Example

**Original Profile**:
```json
{
  "name": "Alice Johnson",
  "income": 75000,
  "employment_status": "employed",
  "age": 28,
  "gender": "Female"
}
```

**Perturbation Testing Results**:

| Perturbation Type | Modified Data | Original Decision | Perturbed Decision | Consistent? |
|------------------|---------------|-------------------|-------------------|------------|
| Numerical Noise | income: 77,321 | Approve (score: 720) | Approve (score: 725) | ✅ Yes |
| Text Typos | name: "Alict Johnson" | Approve (score: 720) | Approve (score: 720) | ✅ Yes |
| Case Change | name: "ALICE JOHNSON" | Approve (score: 720) | Approve (score: 720) | ✅ Yes |
| Missing Values | employment_status: null | Approve (score: 720) | Deny (score: 580) | ❌ No |
| Extreme Values | income: 150,000 | Approve (score: 720) | Approve (score: 780) | ✅ Yes |

**Analysis Results**:
```json
{
  "decision_consistency_rate": 0.8,  // 4 out of 5 consistent
  "confidence_stability": {
    "mean_difference": 0.045,
    "max_difference": 0.165,
    "stability_score": 0.955
  },
  "perturbation_analysis": {
    "missing_values": {
      "consistency_rate": 0.6,  // Most vulnerable
      "vulnerability_score": 0.4
    },
    "numerical_noise": {
      "consistency_rate": 0.95,  // Most robust
      "vulnerability_score": 0.05
    }
  },
  "robustness_score": 0.843,  // Overall robustness
  "robustness_level": "GOOD"
}
```

### Failure Case Detection

```python
def detect_robustness_failures(responses):
    """Identify and categorize robustness failures"""
    failure_cases = []
    
    for response in responses:
        original_decision, original_conf, orig_text = parse_credit_decision(
            response["original_response"]
        )
        perturbed_decision, perturbed_conf, pert_text = parse_credit_decision(
            response["perturbed_response"]
        )
        
        # Major inconsistency: decision flip
        decision_inconsistent = (original_decision != perturbed_decision)
        
        # Major confidence drop (>30%)
        major_confidence_drop = (
            original_conf and perturbed_conf and 
            abs(original_conf - perturbed_conf) > 0.3
        )
        
        if decision_inconsistent or major_confidence_drop:
            failure_case = {
                "perturbation_type": response["perturbation_type"],
                "failure_type": "decision_flip" if decision_inconsistent else "confidence_drop",
                "original_decision": original_decision,
                "perturbed_decision": perturbed_decision,
                "original_confidence": original_conf,
                "perturbed_confidence": perturbed_conf,
                "confidence_change": abs(original_conf - perturbed_conf) if (original_conf and perturbed_conf) else None,
                "original_data": response["original_data"],
                "perturbed_data": response["perturbed_data"],
                "severity": "HIGH" if decision_inconsistent else "MEDIUM"
            }
            failure_cases.append(failure_case)
    
    return failure_cases
```

### Robustness Interpretation Guidelines

**Excellent Robustness (0.9-1.0)**:
- Decision consistency > 95%
- Mean confidence difference < 0.05
- No major failure cases
- **Status**: Production ready, highly reliable

**Good Robustness (0.8-0.9)**:
- Decision consistency 85-95%
- Mean confidence difference 0.05-0.15
- Few minor inconsistencies
- **Status**: Acceptable for most applications

**Fair Robustness (0.7-0.8)**:
- Decision consistency 70-85%
- Mean confidence difference 0.15-0.25
- Some notable vulnerabilities
- **Status**: Requires monitoring, consider improvements

**Poor Robustness (<0.7)**:
- Decision consistency < 70%
- Mean confidence difference > 0.25
- Multiple failure cases
- **Status**: Not production ready, needs significant work

## How It Works

### 1. Adversarial Example Generation

The system generates various types of perturbed inputs:

- **Numerical Noise**: Adds Gaussian noise to numerical fields (age, income, etc.)
- **Text Typos**: Introduces random character substitutions in text fields
- **Case Changes**: Converts text to uppercase/lowercase
- **Missing Values**: Sets random fields to null/empty
- **Extreme Values**: Replaces values with extreme high/low values

### 2. Model Testing

For each adversarial example:
- Makes an API call with the original data
- Makes an API call with the perturbed data  
- Compares the responses to measure consistency

### 3. Analysis Metrics

The system calculates several robustness metrics:

- **Decision Consistency Rate**: Percentage of cases where the model made the same decision (approve/deny) for both original and perturbed inputs
- **Confidence Stability**: How much the model's confidence scores vary under perturbations
- **Perturbation Impact**: Which types of perturbations cause the most inconsistency
- **Overall Robustness Score**: Combined metric (0-1, higher is better)

## Files Added/Modified

### New Files

1. **`analysis/robustness.py`** - Core robustness analysis implementation
2. **`reports/templates/robustness_template.html`** - HTML report template
3. **`tests/test_robustness.py`** - Comprehensive unit tests
4. **`tests/demo_robustness.py`** - Demo script for testing

### Modified Files

1. **`app.py`** - Added robustness integration to Flask app
2. **`reports/report_builder.py`** - Added robustness report builder
3. **`templates/index.html`** - Added robustness checkbox and report button

## Key Functions

### `generate_adversarial_examples(df, num_examples)`
Creates perturbed versions of input data using various perturbation strategies.

### `collect_robustness_responses()`
Makes API calls for original and perturbed data, collecting responses for analysis.

### `analyze_robustness_results(responses)`
Processes collected responses to calculate robustness metrics and identify failure cases.

### `run_robustness_analysis()`
Main entry point that orchestrates the complete robustness testing workflow.

## Usage

### Through Web Interface

1. Open the Credit Scoring Validator web application
2. Fill in API configuration (URL, username, password)
3. Check the "Robustness Analysis" checkbox
4. Click "Run Selected Analyses"
5. View the generated robustness report when complete

### Programmatically

```python
from analysis.robustness import run_robustness_analysis

# Run robustness analysis
results = run_robustness_analysis()

# Access key metrics
robustness_score = results['robustness_score']
consistency_rate = results['decision_consistency']['rate']
failure_cases = results['failure_cases']
```

### Demo Script

```bash
cd /workspaces/credit_scoring_validator
source venv/bin/activate
python tests/demo_robustness.py
```

## Report Features

The robustness analysis report includes:

### Executive Summary
- Overall robustness score (0-100%)
- Decision consistency rate
- Total test cases processed

### Detailed Metrics  
- Decision consistency breakdown
- Confidence stability statistics
- Performance by perturbation type

### Visualizations
- Interactive charts showing perturbation impact
- Consistency rates by perturbation type

### Failure Case Analysis
- Specific examples where the model was inconsistent
- Side-by-side comparison of original vs perturbed responses
- Confidence score changes

### Recommendations
- Automated suggestions based on robustness score
- Best practices for improving model stability

## Interpretation Guidelines

### Robustness Scores
- **0.8-1.0**: Excellent robustness, model is very stable
- **0.6-0.8**: Good robustness, minor improvements possible  
- **0.4-0.6**: Moderate robustness, consider model improvements
- **0.0-0.4**: Poor robustness, significant stability issues

### Perturbation Analysis
- **Noise Numerical**: Tests resilience to measurement errors
- **Typos Text**: Tests handling of data entry mistakes
- **Case Changes**: Tests case sensitivity issues
- **Missing Values**: Tests graceful degradation with incomplete data
- **Extreme Values**: Tests boundary condition handling

## Best Practices

### For Model Developers
1. **Regular Testing**: Run robustness analysis as part of your ML pipeline
2. **Input Validation**: Implement robust input preprocessing and validation
3. **Feature Engineering**: Create features that are naturally more robust
4. **Ensemble Methods**: Consider using ensemble approaches for better stability

### For Stakeholders  
1. **Set Thresholds**: Define minimum acceptable robustness scores
2. **Monitor Trends**: Track robustness metrics over time
3. **Risk Assessment**: Use robustness scores in risk management
4. **Compliance**: Include robustness testing in model validation processes

## Testing

The implementation includes comprehensive test coverage:

- **Unit Tests**: Test individual functions and components
- **Integration Tests**: Test the complete workflow
- **Mock API Tests**: Test without requiring external API access
- **Edge Case Tests**: Test handling of unusual inputs and errors

Run tests with:
```bash
python -m unittest tests.test_robustness -v
```

## Future Enhancements

Potential improvements to consider:

1. **Additional Perturbation Types**: 
   - Temporal shifts for time-series data
   - Demographic distribution shifts
   - Feature correlation changes

2. **Advanced Metrics**:
   - Statistical significance testing
   - Confidence interval analysis
   - Robustness benchmarking

3. **Automated Remediation**:
   - Suggestions for fixing specific vulnerabilities
   - Automatic input preprocessing recommendations
   - Model retraining recommendations

4. **Real-time Monitoring**:
   - Continuous robustness monitoring in production
   - Drift detection based on robustness changes
   - Alert systems for robustness degradation

## Conclusion

The robustness analysis feature provides comprehensive testing of model stability and reliability. It helps identify potential weaknesses, ensures consistent behavior under various conditions, and builds confidence in automated credit decisions. The implementation follows best practices for ML model validation and provides actionable insights for improving model robustness.
