# Bias and Fairness Analysis - Implementation Guide

## Overview

The bias and fairness analysis feature evaluates whether the credit scoring model makes fair and unbiased decisions across different demographic groups. This analysis is crucial for ensuring compliance with fair lending laws and promoting equitable access to financial services.

## What is Bias and Fairness Analysis?

Bias and fairness analysis examines whether a machine learning model treats different demographic groups fairly and consistently. For credit scoring models, this is essential because:

- **Legal Compliance**: Fair lending laws prohibit discrimination based on protected characteristics
- **Ethical AI**: Ensures responsible and equitable use of artificial intelligence
- **Business Risk**: Biased models can lead to legal liability and reputational damage
- **Social Impact**: Promotes equal access to credit and financial opportunities

## Bias Detection: Technical Deep Dive

### Protected Attributes Analyzed

The system examines five key protected characteristics:

```python
PROTECTED_ATTRIBUTES = [
    "gender",           # Male, Female, Non-binary
    "ethnicity",        # Various ethnic backgrounds
    "nationality",      # Different national origins  
    "disability_status", # Disabled vs. non-disabled
    "marital_status"    # Single, Married, Divorced, Widowed
]
```

### 1. Demographic Parity Analysis

**What it measures**: Whether approval rates are similar across different demographic groups.

**Technical Implementation**:
```python
def demographic_parity(responses, protected_attr, positive_class="Good"):
    groups = {}
    
    for entry in responses:
        group = entry["input"].get(protected_attr)
        classification = entry["output"]["parsed"].get("classification")
        
        if group not in groups:
            groups[group] = {"total": 0, "positive": 0}
        
        groups[group]["total"] += 1
        if classification == positive_class:
            groups[group]["positive"] += 1
    
    # Calculate approval rates for each group
    for group in groups:
        groups[group]["rate"] = groups[group]["positive"] / groups[group]["total"]
```

**Example Results**:
```json
{
  "gender": {
    "Male": {"total": 450, "positive": 315, "rate": 0.70},
    "Female": {"total": 430, "positive": 258, "rate": 0.60},
    "Non-binary": {"total": 120, "positive": 72, "rate": 0.60}
  }
}
```

**Interpretation**: 
- Male approval rate: 70%
- Female approval rate: 60%
- **Potential bias detected**: 10 percentage point difference

### 2. Disparate Impact Ratio

**What it measures**: The ratio between the lowest and highest group approval rates.

**Formula**: `Minimum Group Rate / Maximum Group Rate`

**Technical Implementation**:
```python
def disparate_impact_ratio(demographic_groups):
    rates = [group["rate"] for group in demographic_groups.values() if group["total"] > 0]
    if len(rates) < 2:
        return None
    
    min_rate = min(rates)
    max_rate = max(rates)
    ratio = min_rate / max_rate if max_rate > 0 else 0
    
    return {
        "ratio": ratio,
        "min_rate": min_rate,
        "max_rate": max_rate,
        "passes_80_percent_rule": ratio >= 0.8
    }
```

**80% Rule Compliance**:
- **Ratio ≥ 0.8**: Compliant (no significant disparate impact)
- **Ratio < 0.8**: Potential disparate impact violation
- **Ratio < 0.6**: Clear disparate impact concern

### 3. Counterfactual Fairness Testing

**What it measures**: Whether changing only a protected attribute affects the credit decision.

**The Test Process**:
1. **Original Prediction**: Send profile to LLM → Get credit score
2. **Counterfactual Prediction**: Change only protected attribute → Send modified profile
3. **Comparison**: Check if outcomes differ significantly

**Technical Implementation**:
```python
def counterfactual_fairness(df, protected_attr, values, sample_size=200):
    violations = 0
    total_tests = 0
    
    for _, row in df.sample(sample_size).iterrows():
        original_value = row[protected_attr]
        input_data = row.to_dict()
        
        # Get original prediction
        original_response = send_request(input_data)
        original_score = original_response["parsed"]["credit_score"]
        original_class = original_response["parsed"]["classification"]
        
        # Test counterfactuals
        for alt_value in values:
            if alt_value == original_value:
                continue
                
            # Create counterfactual (change ONLY protected attribute)
            cf_input = input_data.copy()
            cf_input[protected_attr] = alt_value
            
            cf_response = send_request(cf_input)
            cf_score = cf_response["parsed"]["credit_score"]
            cf_class = cf_response["parsed"]["classification"]
            
            # Check for differences
            classification_changed = (original_class != cf_class)
            score_diff = abs(float(original_score) - float(cf_score))
            significant_score_change = score_diff >= 10  # 10+ point difference
            
            if classification_changed or significant_score_change:
                violations += 1
                logger.warning(f"BIAS: {protected_attr} {original_value}→{alt_value}")
                logger.warning(f"  Score: {original_score}→{cf_score} (Δ{score_diff:.1f})")
                logger.warning(f"  Class: {original_class}→{cf_class}")
            
            total_tests += 1
    
    violation_ratio = violations / total_tests if total_tests > 0 else 0
    return {
        "violations": violations,
        "total_tests": total_tests,
        "violation_ratio": violation_ratio,
        "bias_level": "HIGH" if violation_ratio > 0.05 else "LOW"
    }
```

**Bias Detection Thresholds**:
- **Violation Ratio > 5%**: HIGH bias risk
- **Violation Ratio 1-5%**: LOW bias risk  
- **Violation Ratio < 1%**: MINIMAL bias risk

### Real-World Bias Detection Example

**Scenario**: Testing gender bias in credit scoring

**Test Profile**:
```json
{
  "name": "Alex Johnson",
  "income": 75000,
  "employment_status": "employed",
  "age": 35,
  "gender": "Male"  // Original value
}
```

**Test Results**:
1. **Male Profile** → Credit Score: 78, Classification: "Good"
2. **Female Profile** (same everything else) → Credit Score: 65, Classification: "Average"
3. **Score Difference**: 13 points (significant bias detected!)

**System Response**:
```
🚨 BIAS DETECTED: gender = Male → Female
  Profile: Income=75000, Age=35, Employment=employed
  Classification: Good → Average  
  Score: 78 → 65 (diff: 13.0)
  ⚠️ This suggests disparate treatment based on protected attribute!
```

### Integration Workflow

1. **Data Preparation**: Load test profiles with demographic information
2. **API Response Collection**: Send profiles to LLM for credit scoring
3. **Demographic Parity**: Calculate approval rates by protected groups
4. **Disparate Impact**: Check 80% rule compliance
5. **Counterfactual Testing**: Test for direct discrimination
6. **Report Generation**: Compile comprehensive bias analysis report

### Statistical Significance Testing

The system also performs statistical tests to validate findings:

**Chi-Square Test**: Tests independence between protected attributes and credit decisions
```python
from scipy.stats import chi2_contingency

def test_independence(responses, protected_attr):
    # Create contingency table
    contingency_table = create_contingency_table(responses, protected_attr)
    
    # Perform chi-square test
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
    
    return {
        "chi2_statistic": chi2,
        "p_value": p_value,
        "significant": p_value < 0.05,
        "interpretation": "Significant association detected" if p_value < 0.05 else "No significant association"
    }
```

### Bias Mitigation Strategies

**1. Pre-processing**:
- Remove or transform discriminatory features
- Ensure balanced representation in training data
- Apply fairness-aware sampling techniques

**2. In-processing**:
- Add fairness constraints to model training
- Use adversarial debiasing techniques
- Implement multi-objective optimization

**3. Post-processing**:
- Adjust decision thresholds by group
- Apply equalized odds post-processing
- Implement demographic parity corrections

## How It Works

### 1. Protected Attribute Analysis

The system evaluates fairness across key protected characteristics:

- **Gender**: Male, Female, Non-binary
- **Ethnicity**: Various ethnic backgrounds
- **Nationality**: Different national origins
- **Disability Status**: Disabled vs. non-disabled individuals
- **Marital Status**: Single, Married, Divorced, Widowed

### 2. Fairness Metrics Calculation

For each protected attribute, the system computes:

- **Statistical Parity**: Equal positive prediction rates across groups
- **Equalized Odds**: Equal true positive and false positive rates
- **Equalized Opportunity**: Equal true positive rates across groups
- **Demographic Parity**: Proportional representation in positive outcomes
- **Individual Fairness**: Similar individuals receive similar predictions

### 3. Bias Detection

The analysis identifies various types of bias:

- **Direct Discrimination**: Explicit use of protected attributes
- **Indirect Discrimination**: Proxy discrimination through correlated features
- **Systematic Bias**: Consistent unfair treatment of certain groups
- **Intersectional Bias**: Bias affecting individuals with multiple protected characteristics

## Files Overview

### Core Implementation

1. **`analysis/bias_fairness.py`** - Main bias analysis module
   - Protected attribute extraction and analysis
   - Fairness metrics calculation
   - Statistical significance testing
   - Bias detection algorithms

2. **`tests/test_bias_fairness.py`** - Comprehensive unit tests
   - Fairness metric validation
   - Edge case handling
   - Statistical test verification

### Integration Points

1. **`app.py`** - Flask integration for web interface
2. **`reports/report_builder.py`** - Bias report generation
3. **`templates/index.html`** - Web UI controls

## Key Functions

### `collect_responses(input_path, output_path)`
Collects API responses for bias analysis with progress tracking.

**Parameters:**
- `input_path`: Path to test data CSV file
- `output_path`: Path to save response data

**Process:**
- Loads test profiles with demographic data
- Makes API calls for each profile
- Saves responses for analysis

### `calculate_fairness_metrics(responses)`
Computes comprehensive fairness metrics across protected groups.

**Returns:**
- Statistical parity ratios
- Equalized odds metrics
- Demographic parity analysis
- Group-wise performance statistics

### `detect_bias_patterns(responses, protected_attributes)`
Identifies potential bias patterns in model predictions.

**Parameters:**
- `responses`: List of API response data
- `protected_attributes`: List of attributes to analyze

**Returns:**
- Bias severity scores
- Affected group identification
- Statistical significance results

### `run_bias_fairness_analysis()`
Main orchestration function for complete bias analysis workflow.

**Process:**
1. Generates/loads test data with demographic information
2. Collects API responses for analysis
3. Calculates fairness metrics
4. Detects bias patterns
5. Generates comprehensive bias report

## Usage

### Through Web Interface

1. Open the Credit Scoring Validator web application
2. Configure API settings (URL, authentication credentials)
3. Check the "Bias and Fairness Analysis" checkbox
4. Click "Run Selected Analyses"
5. Review the generated bias and fairness report

### Programmatically

```python
from analysis.bias_fairness import run_bias_fairness_analysis

# Run complete bias analysis
results = run_bias_fairness_analysis()

# Access fairness metrics
statistical_parity = results['statistical_parity']
equalized_odds = results['equalized_odds']
demographic_parity = results['demographic_parity']

# Check for bias detection
bias_detected = results['bias_detected']
affected_groups = results['affected_groups']
```

## Report Features

The bias and fairness analysis report includes:

### Executive Summary
- Overall fairness assessment score
- Number of protected groups analyzed
- Bias detection status and severity
- Key findings and recommendations

### Statistical Parity Analysis
- Approval rates by demographic group
- Parity ratios and deviations
- Statistical significance tests
- Visual comparisons across groups

### Equalized Odds Assessment
- True positive rates by group
- False positive rates by group
- ROC curve comparisons
- Performance parity evaluation

### Demographic Analysis
- Population representation in dataset
- Score distribution by protected attribute
- Intersectional bias analysis
- Group-specific performance metrics

### Visualizations
- Approval rate comparison charts
- Score distribution histograms by group
- Fairness metric heatmaps
- ROC curves for different demographics

### Detailed Findings
- Specific bias instances identified
- Statistical significance of disparities
- Affected individual profiles
- Recommended remediation actions

## Interpretation Guidelines

### Fairness Thresholds

**Statistical Parity Ratio:**
- **0.8-1.2**: Acceptable range (80-120% rule)
- **0.6-0.8 or 1.2-1.4**: Concerning disparity
- **< 0.6 or > 1.4**: Significant bias concern

**Equalized Odds Difference:**
- **< 0.05**: Excellent fairness
- **0.05-0.10**: Acceptable fairness
- **0.10-0.15**: Concerning disparity
- **> 0.15**: Significant bias issue

### Bias Severity Levels

**Low Bias (Score: 0.0-0.3):**
- Minor statistical differences
- Within acceptable variance ranges
- No immediate action required

**Moderate Bias (Score: 0.3-0.6):**
- Noticeable disparities across groups
- Requires monitoring and investigation
- Consider model adjustments

**High Bias (Score: 0.6-1.0):**
- Significant unfair treatment detected
- Immediate remediation required
- Legal and ethical concerns

## Protected Attributes Details

### Gender Analysis
- Examines approval rates across gender categories
- Identifies salary/income bias correlations
- Detects proxy discrimination through related features

### Ethnicity and Nationality
- Analyzes cultural and geographic bias
- Examines language and name-based discrimination
- Assesses intersectional impacts

### Disability Status
- Evaluates accessibility and accommodation fairness
- Analyzes income-related bias impacts
- Ensures compliance with ADA requirements

### Marital Status
- Examines household income assumptions
- Identifies family structure bias
- Analyzes stability perception impacts

## Best Practices

### For Model Developers

1. **Proactive Design**: Build fairness constraints into model training
2. **Regular Testing**: Conduct bias analysis throughout development lifecycle
3. **Diverse Data**: Ensure training data represents all demographic groups
4. **Feature Engineering**: Remove or transform potentially discriminatory features
5. **Ensemble Fairness**: Use multiple models to balance accuracy and fairness

### For Compliance Officers

1. **Documentation**: Maintain detailed records of fairness analysis
2. **Threshold Setting**: Establish clear fairness acceptance criteria
3. **Regular Monitoring**: Schedule periodic bias assessments
4. **Legal Review**: Coordinate with legal team on compliance requirements
5. **Stakeholder Communication**: Report findings to relevant stakeholders

### For Business Leaders

1. **Policy Development**: Create fair lending policies and procedures
2. **Training**: Educate staff on bias detection and mitigation
3. **Customer Impact**: Consider fairness in customer communication
4. **Reputation Management**: Address bias issues proactively
5. **Competitive Advantage**: Use fairness as a market differentiator

## Statistical Methods

### Fairness Metrics Formulas

**Statistical Parity:**
```
P(Ŷ = 1 | A = a) = P(Ŷ = 1 | A = b) for all groups a, b
```

**Equalized Odds:**
```
P(Ŷ = 1 | Y = y, A = a) = P(Ŷ = 1 | Y = y, A = b) for y ∈ {0,1}
```

**Demographic Parity:**
```
|P(Ŷ = 1 | A = a) - P(Ŷ = 1)| ≤ ε for all groups a
```

### Statistical Tests

- **Chi-Square Test**: Independence of predictions and protected attributes
- **Fisher's Exact Test**: Precise p-values for small sample sizes
- **Welch's t-test**: Mean score differences between groups
- **Kolmogorov-Smirnov**: Distribution similarity testing

## Testing

The implementation includes comprehensive test coverage:

- **Metric Calculation Tests**: Verify fairness computation accuracy
- **Edge Case Tests**: Handle small groups and missing data
- **Statistical Tests**: Validate significance testing methods
- **Integration Tests**: Test complete analysis workflow

Run tests with:
```bash
python -m pytest tests/test_bias_fairness.py -v
```

## Troubleshooting

### Common Issues

**Insufficient Data for Groups:**
- Increase sample size for underrepresented groups
- Use statistical techniques for small sample analysis
- Consider data augmentation or synthetic data generation

**High Variance in Results:**
- Check for data quality issues
- Verify protected attribute encoding
- Review statistical significance levels

**Conflicting Fairness Metrics:**
- Understand trade-offs between different fairness definitions
- Prioritize metrics based on use case and legal requirements
- Document decision rationale

## Regulatory Compliance

### Fair Credit Reporting Act (FCRA)
- Ensures accurate and fair credit reporting
- Requires disclosure of automated decision-making
- Mandates dispute resolution processes

### Equal Credit Opportunity Act (ECOA)
- Prohibits discrimination in credit transactions
- Defines protected characteristics
- Requires adverse action notifications

### Fair Housing Act (FHA)
- Applies to mortgage and housing-related credit
- Prohibits discriminatory practices
- Requires equal treatment regardless of protected status

## Future Enhancements

Potential improvements to consider:

1. **Advanced Fairness Metrics**:
   - Counterfactual fairness analysis
   - Individual fairness measurements
   - Multi-objective fairness optimization

2. **Intersectional Analysis**:
   - Multiple protected attribute combinations
   - Compound bias detection
   - Hierarchical bias analysis

3. **Temporal Fairness**:
   - Bias evolution over time
   - Seasonal fairness variations
   - Longitudinal fairness tracking

4. **Remediation Tools**:
   - Automated bias correction algorithms
   - Fair representation learning
   - Post-processing fairness adjustments

5. **Explainable Bias**:
   - Feature-level bias attribution
   - Decision pathway analysis
   - Counterfactual explanations

## Conclusion

The bias and fairness analysis feature provides comprehensive evaluation of model equity across demographic groups. It helps ensure compliance with fair lending regulations, promotes ethical AI practices, and protects against discrimination. The implementation follows established fairness research and provides actionable insights for creating more equitable credit scoring systems.
