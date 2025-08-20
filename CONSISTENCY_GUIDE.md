# Consistency Analysis - Implementation Guide

## Overview

The consistency analysis feature evaluates whether the credit scoring model produces identical responses when given the same input data. This analysis helps identify non-deterministic behavior, caching issues, and other sources of inconsistency that could undermine trust in the model's reliability.

## What is Consistency Analysis?

Consistency analysis tests whether a machine learning model produces repeatable, deterministic results when presented with identical inputs. For credit scoring models, this is crucial because:

- **Deterministic Decisions**: Same applicant should always receive the same evaluation
- **Regulatory Compliance**: Auditors expect consistent and reproducible model behavior
- **Customer Trust**: Inconsistent scoring erodes confidence in the system
- **System Reliability**: Identifies technical issues like caching problems or race conditions
- **Fair Treatment**: Ensures applicants are evaluated consistently regardless of timing

## Consistency Testing: Technical Deep Dive

### Core Testing Methodology

The system performs consistency testing through a rigorous process:

**1. Input Preparation and Hashing**
```python
def hash_input_data(data: dict) -> str:
    """Create consistent hash for duplicate detection"""
    # Sort keys to ensure consistent hashing regardless of input order
    sorted_data = {k: data[k] for k in sorted(data.keys())}
    data_str = json.dumps(sorted_data, sort_keys=True, default=str)
    return hashlib.md5(data_str.encode()).hexdigest()
```

**2. Multiple Request Strategy**
```python
def collect_consistency_responses(num_repeats=3, delay_seconds=1.0, sample_size=50):
    responses = []
    
    for profile in test_profiles:
        input_hash = hash_input_data(profile)
        
        # Make multiple identical requests with delays
        for repeat_num in range(num_repeats):
            timestamp = time.time()
            response = send_request(profile)
            
            responses.append({
                "input": profile,
                "input_hash": input_hash,
                "repeat_number": repeat_num,
                "timestamp": timestamp,
                "output": response
            })
            
            if repeat_num < num_repeats - 1:
                time.sleep(delay_seconds)  # Prevent rate limiting
```

**3. Response Normalization for Comparison**
```python
def normalize_response_text(response) -> str:
    """Normalize responses for accurate comparison"""
    if isinstance(response, dict) and "parsed" in response:
        parsed = response["parsed"]
        
        # Extract structured data
        parts = []
        if "credit_score" in parsed and parsed["credit_score"] is not None:
            parts.append(f"score:{parsed['credit_score']}")
        if "classification" in parsed:
            parts.append(f"class:{parsed['classification']}")
        if "explanation" in parsed:
            # Truncate explanations to first 100 chars for comparison
            parts.append(f"reason:{parsed['explanation'][:100]}")
        
        response_text = " ".join(parts)
    else:
        response_text = str(response)
    
    # Normalize whitespace and case
    normalized = response_text.lower().strip()
    normalized = ' '.join(normalized.split())
    
    return normalized
```

### Consistency Metrics Calculation

**1. Exact Match Rate**
```python
def calculate_exact_match_rate(responses):
    """Calculate percentage of perfectly identical responses"""
    grouped_by_input = {}
    
    for response in responses:
        input_hash = response["input_hash"]
        if input_hash not in grouped_by_input:
            grouped_by_input[input_hash] = []
        grouped_by_input[input_hash].append(response)
    
    exact_matches = 0
    total_groups = 0
    
    for input_hash, group_responses in grouped_by_input.items():
        if len(group_responses) < 2:
            continue
            
        total_groups += 1
        
        # Normalize all responses in the group
        normalized_responses = [
            normalize_response_text(r["output"]) 
            for r in group_responses
        ]
        
        # Check if all responses are identical
        if len(set(normalized_responses)) == 1:
            exact_matches += 1
    
    return exact_matches / total_groups if total_groups > 0 else 0
```

**2. Score Variance Analysis**
```python
def calculate_score_variance(responses):
    """Analyze variance in credit scores for identical inputs"""
    grouped_by_input = {}
    variance_stats = []
    
    for response in responses:
        input_hash = response["input_hash"]
        
        # Extract credit score
        score = None
        if "output" in response and "parsed" in response["output"]:
            score = response["output"]["parsed"].get("credit_score")
        
        if score is not None:
            try:
                score = float(score)
                if input_hash not in grouped_by_input:
                    grouped_by_input[input_hash] = []
                grouped_by_input[input_hash].append(score)
            except (ValueError, TypeError):
                continue
    
    for input_hash, scores in grouped_by_input.items():
        if len(scores) >= 2:
            variance = np.var(scores)
            std_dev = np.std(scores)
            mean_score = np.mean(scores)
            cv = std_dev / mean_score if mean_score > 0 else 0
            
            variance_stats.append({
                "input_hash": input_hash,
                "scores": scores,
                "variance": variance,
                "std_dev": std_dev,
                "mean": mean_score,
                "coefficient_of_variation": cv,
                "min_score": min(scores),
                "max_score": max(scores),
                "range": max(scores) - min(scores)
            })
    
    return variance_stats
```

**3. Decision Consistency Rate**
```python
def calculate_decision_consistency(responses):
    """Analyze consistency of approve/deny decisions"""
    grouped_by_input = {}
    
    for response in responses:
        input_hash = response["input_hash"]
        decision, confidence = extract_decision_and_confidence(response["output"])
        
        if decision:
            if input_hash not in grouped_by_input:
                grouped_by_input[input_hash] = []
            grouped_by_input[input_hash].append({
                "decision": decision,
                "confidence": confidence
            })
    
    consistent_decisions = 0
    total_groups = 0
    
    for input_hash, decisions in grouped_by_input.items():
        if len(decisions) < 2:
            continue
            
        total_groups += 1
        decision_set = set(d["decision"] for d in decisions)
        
        if len(decision_set) == 1:  # All decisions identical
            consistent_decisions += 1
    
    return consistent_decisions / total_groups if total_groups > 0 else 0
```

### Decision and Confidence Extraction

```python
def extract_decision_and_confidence(response) -> Tuple[Optional[str], Optional[float]]:
    """Extract decision and confidence from various response formats"""
    if not response:
        return None, None
    
    if isinstance(response, dict) and "parsed" in response:
        parsed = response["parsed"]
        
        # Extract classification and score
        classification = parsed.get("classification", "").lower()
        credit_score = parsed.get("credit_score")
        explanation = parsed.get("explanation", "").lower()
        
        # Map classification to standardized decision
        decision = None
        if classification in ["good", "approved", "approve"]:
            decision = "approve"
        elif classification in ["poor", "bad", "denied", "deny", "reject"]:
            decision = "deny"
        elif classification in ["average", "moderate"]:
            # Use credit score threshold for average cases (API returns 0-100)
        if credit_score is not None:
            if credit_score >= 70:
                decision = "approve"
            elif credit_score < 60:
                decision = "deny"
                else:
                    decision = "conditional"
        
        # Extract confidence from explanation or use score as proxy
        confidence = None
        if explanation:
            import re
            # Look for percentage confidence in explanation
            confidence_matches = re.findall(r'(\d+(?:\.\d+)?)%', explanation)
            if confidence_matches:
                confidence = float(confidence_matches[0]) / 100.0
            elif "high confidence" in explanation:
                confidence = 0.9
            elif "medium confidence" in explanation:
                confidence = 0.7
            elif "low confidence" in explanation:
                confidence = 0.5
        
        # Use credit score as confidence proxy if no explicit confidence
        if confidence is None and credit_score is not None:
            confidence = min(credit_score / 100.0, 1.0)  # Normalize 0-100 to 0-1
        
        return decision, confidence
    
    # Fallback to text-based extraction
    text = str(response).lower()
    decision = None
    if "approve" in text:
        decision = "approve"
    elif "deny" in text or "reject" in text:
        decision = "deny"
    
    return decision, None
```

### Real-World Consistency Testing Example

**Test Profile**:
```json
{
  "name": "John Smith",
  "income": 65000,
  "employment_status": "employed",
  "age": 32,
  "gender": "Male"
}
```

**Multiple API Calls (3 repeats)**:
1. **Call 1** → Score: 72, Classification: "Good"
2. **Call 2** → Score: 72, Classification: "Good"  
3. **Call 3** → Score: 74, Classification: "Good"

**Analysis Results**:
```json
{
  "exact_match_rate": 0.67,  // 2 out of 3 identical
  "score_variance": {
    "mean": 72.67,
    "std_dev": 1.15,
    "variance": 1.33,
    "range": 2,
    "coefficient_of_variation": 0.016
  },
  "decision_consistency": 1.0,  // All "Good" classifications
  "consistency_level": "HIGH"   // Low variance, consistent decisions
}
```

### Temporal Consistency Analysis

```python
def analyze_temporal_consistency(responses):
    """Analyze consistency over time periods"""
    # Group responses by time windows (e.g., 1-hour windows)
    time_windows = {}
    
    for response in responses:
        timestamp = response["timestamp"]
        hour_window = int(timestamp // 3600) * 3600  # Round to hour
        
        if hour_window not in time_windows:
            time_windows[hour_window] = []
        time_windows[hour_window].append(response)
    
    # Calculate consistency metrics for each time window
    window_consistency = {}
    for window, window_responses in time_windows.items():
        window_consistency[window] = {
            "exact_match_rate": calculate_exact_match_rate(window_responses),
            "score_variance": calculate_score_variance(window_responses),
            "response_count": len(window_responses)
        }
    
    return window_consistency
```

### Inconsistency Pattern Detection

```python
def detect_inconsistency_patterns(responses):
    """Identify specific patterns of inconsistency"""
    patterns = {
        "high_variance_inputs": [],
        "decision_flips": [],
        "temporal_inconsistencies": [],
        "systematic_bias": []
    }
    
    # Detect high variance inputs
    variance_stats = calculate_score_variance(responses)
    for stat in variance_stats:
        if stat["std_dev"] > 5:  # High variance threshold
            patterns["high_variance_inputs"].append({
                "input_hash": stat["input_hash"],
                "std_dev": stat["std_dev"],
                "range": stat["range"],
                "scores": stat["scores"]
            })
    
    # Detect decision flips (same input, different decisions)
    grouped_by_input = {}
    for response in responses:
        input_hash = response["input_hash"]
        decision, _ = extract_decision_and_confidence(response["output"])
        
        if decision and input_hash not in grouped_by_input:
            grouped_by_input[input_hash] = []
        if decision:
            grouped_by_input[input_hash].append(decision)
    
    for input_hash, decisions in grouped_by_input.items():
        unique_decisions = set(decisions)
        if len(unique_decisions) > 1:
            patterns["decision_flips"].append({
                "input_hash": input_hash,
                "decisions": decisions,
                "unique_count": len(unique_decisions)
            })
    
    return patterns
```

### Integration Workflow

1. **Test Data Preparation**: Load profiles and create input hashes
2. **Multiple API Calls**: Send 3+ identical requests per profile with delays
3. **Response Collection**: Store all responses with timestamps
4. **Normalization**: Standardize response formats for comparison
5. **Metric Calculation**: Compute exact match rates, variance, and decision consistency
6. **Pattern Detection**: Identify specific inconsistency patterns
7. **Report Generation**: Compile comprehensive consistency analysis

### Consistency Thresholds and Interpretation

**Excellent Consistency (95-100%)**:
- Exact match rate > 95%
- Score standard deviation < 1.0
- Decision consistency = 100%
- **Status**: Production ready

**Good Consistency (85-95%)**:
- Exact match rate 85-95%
- Score standard deviation 1.0-3.0
- Decision consistency > 95%
- **Status**: Acceptable for most use cases

**Poor Consistency (<85%)**:
- Exact match rate < 85%
- Score standard deviation > 5.0
- Decision consistency < 90%
- **Status**: Requires immediate investigation

## How It Works

### 1. Duplicate Input Testing

The system performs consistency testing by:

- **Creating Input Variations**: Same logical data in different formats
- **Multiple API Calls**: Sending identical requests multiple times
- **Response Comparison**: Analyzing differences in model outputs
- **Temporal Testing**: Testing consistency across different time periods
- **Hash-based Tracking**: Using input hashing to ensure exact duplicates

### 2. Consistency Metrics

The analysis evaluates several types of consistency:

- **Exact Match Rate**: Percentage of identical responses for identical inputs
- **Score Variance**: Statistical variation in credit scores for same inputs
- **Decision Consistency**: Whether approve/deny decisions remain stable
- **Confidence Stability**: How much prediction confidence varies
- **Response Time Consistency**: Whether processing time affects results

### 3. Inconsistency Detection

The system identifies various sources of inconsistency:

- **Non-deterministic Algorithms**: Random elements in model architecture
- **Caching Issues**: Stale or corrupted cached responses
- **Race Conditions**: Concurrent processing leading to different results
- **System State Dependencies**: Results varying based on system load or state
- **Data Processing Variations**: Inconsistent input preprocessing

## Files Overview

### Core Implementation

1. **`analysis/consistency.py`** - Main consistency analysis module
   - Input duplication and hashing algorithms
   - Response comparison and variance calculation
   - Consistency metrics computation
   - Temporal analysis functionality

2. **`tests/test_consistency.py`** - Comprehensive unit tests
   - Hash function validation
   - Consistency metric verification
   - Edge case handling

3. **`tests/demo_consistency.py`** - Demonstration script
   - Real-world usage examples
   - Interactive consistency testing

## Key Functions

### `hash_input_data(data)`
Creates a consistent hash of input data for duplicate detection.

**Parameters:**
- `data`: Dictionary containing input profile data

**Returns:**
- `hash_string`: MD5 hash of sorted and normalized input data

**Purpose:**
- Enables exact duplicate identification
- Handles slight formatting variations
- Provides consistent input tracking

### `collect_consistency_responses()`
Performs multiple API calls with identical and near-identical inputs.

**Process:**
1. Loads test data from CSV file
2. Creates exact duplicates of each input
3. Makes multiple API calls per input
4. Records timestamps and response variations
5. Saves results for analysis

### `analyze_consistency_results(responses)`
Calculates comprehensive consistency metrics from collected responses.

**Metrics Calculated:**
- Exact match percentage
- Score variance statistics
- Decision consistency rate
- Response time variance
- Temporal consistency analysis

### `detect_inconsistency_patterns(responses)`
Identifies specific patterns and sources of inconsistency.

**Detection Areas:**
- Systematic response variations
- Time-dependent inconsistencies
- Input-specific instability
- System load correlations

### `run_consistency_analysis()`
Main orchestration function for complete consistency testing workflow.

**Workflow:**
1. Prepares test data with duplicates
2. Collects multiple responses per input
3. Analyzes consistency metrics
4. Identifies inconsistency patterns
5. Generates detailed consistency report

## Usage

### Through Web Interface

1. Open the Credit Scoring Validator web application
2. Configure API settings (URL, credentials)
3. Check the "Consistency Analysis" checkbox
4. Click "Run Selected Analyses"
5. Review the generated consistency report

### Programmatically

```python
from analysis.consistency import run_consistency_analysis

# Run complete consistency analysis
results = run_consistency_analysis()

# Access consistency metrics
exact_match_rate = results['exact_match_rate']
score_variance = results['score_variance']
decision_consistency = results['decision_consistency']

# Check for inconsistency issues
has_issues = results['consistency_issues']
problematic_inputs = results['problematic_cases']
```

### Demo Script

```bash
cd /workspaces/credit_scoring_validator
python tests/demo_consistency.py
```

## Report Features

The consistency analysis report includes:

### Executive Summary
- Overall consistency score (0-100%)
- Exact match rate for identical inputs
- Decision consistency percentage
- Total duplicate tests performed

### Detailed Metrics
- **Exact Match Analysis**: Percentage of perfectly identical responses
- **Score Variance**: Statistical analysis of score variations
- **Decision Stability**: Approve/deny consistency across identical inputs
- **Confidence Consistency**: Variation in prediction confidence scores
- **Temporal Analysis**: Consistency over different time periods

### Inconsistency Detection
- **Problematic Cases**: Specific inputs showing high variance
- **Pattern Analysis**: Common sources of inconsistency
- **Statistical Significance**: Whether variations exceed random noise
- **System Correlation**: Links between inconsistency and system factors

### Visualizations
- Score variance distribution charts
- Consistency rate over time graphs
- Inconsistency pattern heatmaps
- Response time correlation plots

### Root Cause Analysis
- **Technical Issues**: Caching, race conditions, system state
- **Model Architecture**: Non-deterministic components
- **Data Processing**: Input preprocessing variations
- **Infrastructure**: Load balancing, server differences

## Interpretation Guidelines

### Consistency Score Thresholds

**Excellent Consistency (95-100%):**
- Model is highly deterministic
- Minimal technical issues
- Suitable for production deployment

**Good Consistency (85-95%):**
- Minor inconsistencies present
- Acceptable for most use cases
- Monitor for degradation

**Moderate Consistency (70-85%):**
- Noticeable inconsistency issues
- Investigate root causes
- Consider system improvements

**Poor Consistency (<70%):**
- Significant reliability concerns
- Not suitable for production
- Immediate remediation required

### Variance Analysis

**Score Variance:**
- **< 1.0**: Excellent stability
- **1.0-3.0**: Acceptable variation
- **3.0-5.0**: Concerning instability
- **> 5.0**: Unacceptable variation

**Decision Consistency:**
- **100%**: Perfect decision stability
- **95-99%**: Minor edge case variations
- **90-95%**: Concerning decision instability
- **< 90%**: Unacceptable decision variance

## Technical Implementation Details

### Input Hashing Strategy

```python
def hash_input_data(data: dict) -> str:
    # Sort keys for consistent hashing
    sorted_data = {k: data[k] for k in sorted(data.keys())}
    # Convert to JSON with sorted keys
    data_str = json.dumps(sorted_data, sort_keys=True, default=str)
    # Generate MD5 hash
    return hashlib.md5(data_str.encode()).hexdigest()
```

### Response Normalization

The system normalizes responses to enable accurate comparison:

- **Score Extraction**: Handles various response formats
- **Text Cleaning**: Removes formatting inconsistencies
- **Decision Mapping**: Standardizes approve/deny decisions
- **Confidence Parsing**: Normalizes confidence expressions

### Statistical Analysis Methods

**Variance Calculation:**
```python
# Calculate score variance for identical inputs
variance = np.var(scores_for_same_input)
std_deviation = np.std(scores_for_same_input)
coefficient_of_variation = std_deviation / np.mean(scores_for_same_input)
```

**Temporal Consistency:**
```python
# Analyze consistency over time windows
time_windows = group_by_time_period(responses)
consistency_trend = calculate_trend(time_windows)
```

## Best Practices

### For Model Developers

1. **Deterministic Design**: Avoid random elements without fixed seeds
2. **Input Validation**: Implement consistent input preprocessing
3. **State Management**: Ensure stateless model inference
4. **Testing Protocol**: Include consistency testing in CI/CD pipeline
5. **Documentation**: Document any expected sources of variation

### For System Engineers

1. **Caching Strategy**: Implement proper cache invalidation
2. **Load Balancing**: Ensure consistent routing and processing
3. **Environment Parity**: Maintain identical deployment environments
4. **Monitoring**: Set up alerts for consistency degradation
5. **Performance Tuning**: Balance speed with consistency requirements

### For Quality Assurance

1. **Regular Testing**: Schedule automated consistency checks
2. **Regression Testing**: Test consistency after system changes
3. **Edge Case Analysis**: Focus on boundary conditions and unusual inputs
4. **Documentation**: Track consistency issues and resolutions
5. **Threshold Management**: Maintain appropriate consistency thresholds

## Common Inconsistency Sources

### Model-Related Issues

**Non-deterministic Algorithms:**
- Neural networks with random dropout
- Ensemble methods with random sampling
- Algorithms with random initialization

**Preprocessing Variations:**
- Different data scaling approaches
- Inconsistent missing value handling
- Variable feature encoding methods

### System-Related Issues

**Caching Problems:**
- Stale cached responses
- Cache key collisions
- Inconsistent cache policies

**Infrastructure Variations:**
- Different server configurations
- Load balancer routing differences
- Database connection variations

**Concurrent Processing:**
- Race conditions in parallel processing
- Resource contention issues
- Timing-dependent calculations

## Testing Strategy

### Unit Tests

```python
def test_input_hashing_consistency():
    """Test that identical inputs produce identical hashes"""
    data1 = {"income": 50000, "age": 30}
    data2 = {"age": 30, "income": 50000}  # Different order
    assert hash_input_data(data1) == hash_input_data(data2)

def test_response_variance_calculation():
    """Test variance calculation for response analysis"""
    identical_responses = [750, 750, 750, 750]
    varied_responses = [750, 752, 748, 751]
    assert calculate_variance(identical_responses) == 0
    assert calculate_variance(varied_responses) > 0
```

### Integration Tests

- End-to-end consistency workflow testing
- API response comparison validation
- Report generation verification
- Error handling and edge case testing

Run tests with:
```bash
python -m pytest tests/test_consistency.py -v
```

## Troubleshooting

### High Inconsistency Rates

**Investigation Steps:**
1. Check for model randomness sources
2. Verify input preprocessing consistency
3. Analyze system load correlations
4. Review caching implementation
5. Examine server configuration differences

**Common Fixes:**
- Set random seeds for reproducibility
- Standardize preprocessing pipelines
- Implement proper cache management
- Ensure environment consistency

### Intermittent Consistency Issues

**Diagnostic Approach:**
1. Analyze temporal patterns
2. Check system resource utilization
3. Review deployment and scaling events
4. Monitor database connection patterns

## Performance Considerations

### Efficiency Optimizations

**Batch Processing:**
- Group similar inputs for efficient processing
- Minimize API call overhead
- Optimize response collection

**Smart Sampling:**
- Focus on representative input samples
- Prioritize high-risk inconsistency scenarios
- Balance thoroughness with execution time

### Resource Management

**Memory Usage:**
- Stream large response datasets
- Implement garbage collection for temporary data
- Optimize data structures for consistency analysis

**Network Optimization:**
- Minimize redundant API calls
- Implement connection pooling
- Use compression for large payloads

## Future Enhancements

Potential improvements to consider:

1. **Advanced Statistical Analysis**:
   - Bayesian consistency modeling
   - Time series consistency analysis
   - Multi-dimensional variance decomposition

2. **Real-time Monitoring**:
   - Continuous consistency tracking
   - Automated alert systems
   - Trend analysis and forecasting

3. **Root Cause Automation**:
   - Automated inconsistency diagnosis
   - System health correlation analysis
   - Self-healing consistency mechanisms

4. **Enhanced Reporting**:
   - Interactive consistency dashboards
   - Comparative consistency analysis
   - Predictive consistency modeling

## Conclusion

The consistency analysis feature provides essential validation of model reliability and deterministic behavior. It helps identify technical issues, ensures reproducible results, and builds confidence in automated credit scoring systems. The implementation follows software engineering best practices and provides comprehensive insights into model consistency across various dimensions.
