# Accuracy Analysis - Implementation Guide

## Overview

The accuracy analysis feature evaluates how well the credit scoring model's predictions align with expected ground truth values. This analysis helps assess the overall performance and reliability of the model's scoring mechanism by comparing predicted scores against calculated ground truth benchmarks.

## What is Accuracy Analysis?

Accuracy analysis measures how close the model's predictions are to expected or "true" values. For credit scoring models, this is essential because:

- **Performance Validation**: Ensures the model produces reasonable and expected results
- **Quality Assurance**: Identifies systematic errors or biases in model predictions
- **Business Impact**: Inaccurate scoring can lead to poor lending decisions and financial losses
- **Regulatory Compliance**: Financial institutions must demonstrate model accuracy for regulatory approval

## Ground Truth: The Foundation of Accuracy Testing

### What is Ground Truth?

Ground truth refers to the "correct" or "expected" credit scores that we compare against the model's predictions. In this project, **ground truth is synthetically generated using a deterministic rule-based algorithm** rather than using historical data or expert judgments.

### Why Synthetic Ground Truth?

1. **Consistency**: Every test produces the same ground truth for identical inputs
2. **Transparency**: The scoring logic is fully observable and auditable
3. **Controllability**: We can create test cases targeting specific scenarios
4. **No Data Dependencies**: Works without requiring historical credit data
5. **Regulatory Safety**: No real customer data is used in testing

### How Ground Truth is Generated

The ground truth calculation happens in the `calculate_ground_truth()` function in `analysis/accuracy.py`. Here's the detailed process:

#### 1. Base Score Foundation
```python
score = 50  # Every profile starts with a base score of 50/100
```

#### 2. Income Assessment (0-20 points)
```python
income = input_data.get("income", 0)
if income > 100000:      score += 20  # Excellent income
elif income > 70000:     score += 15  # Very good income  
elif income > 50000:     score += 10  # Good income
elif income > 30000:     score += 5   # Moderate income
# Below $30k gets no bonus points
```

#### 3. Employment Stability (0-15 points)
```python
emp_duration = input_data.get("employment_duration_years", 0)
if emp_duration > 10:    score += 15  # Very stable employment
elif emp_duration > 5:   score += 10  # Stable employment
elif emp_duration > 2:   score += 5   # Moderate stability
# Less than 2 years gets no bonus
```

#### 4. Payment Defaults (Heavy Penalty)
```python
defaults = input_data.get("payment_defaults", 0)
score -= defaults * 15  # Each default costs 15 points
```

#### 5. Credit Utilization (±10 points)
```python
credit_limit = input_data.get("credit_limit", 1)
used_credit = input_data.get("used_credit", 0)
utilization = used_credit / max(credit_limit, 1)

if utilization < 0.3:    score += 10  # Excellent utilization
elif utilization < 0.7:  score += 5   # Good utilization  
else:                    score -= 10  # Poor utilization (>70%)
```

#### 6. Credit Inquiries Impact
```python
inquiries = input_data.get("credit_inquiries_last_6_months", 0)
score -= inquiries * 2  # Each inquiry costs 2 points
```

#### 7. Housing Stability Bonus
```python
if input_data.get("housing_status") == "owner":
    score += 5  # Homeownership adds stability
```

#### 8. Address Stability
```python
address_years = input_data.get("address_stability_years", 0)
if address_years > 10:   score += 5   # Long-term residence
elif address_years > 5:  score += 3   # Moderate residence stability
```

#### 9. Loan Portfolio Impact
```python
existing_loans = input_data.get("existing_loans", 0)
if existing_loans > 3:   score -= 5   # Too many existing loans
```

#### 10. Final Normalization and Classification
```python
# Ensure score stays within valid range
score = max(0, min(100, score))

# Determine risk classification
if score >= 70:         classification = "Good"
elif score >= 50:       classification = "Average"  
else:                   classification = "Poor"

return float(score), classification
```

### Ground Truth Examples

**High-Quality Profile:**
- Income: $120,000 → +20 points
- Employment: 12 years → +15 points
- No defaults → +0 points
- 25% credit utilization → +10 points
- Homeowner → +5 points
- **Total: 50 + 20 + 15 + 0 + 10 + 5 = 100 points → "Good"**

**Poor-Quality Profile:**
- Income: $25,000 → +0 points
- Employment: 6 months → +0 points
- 2 defaults → -30 points
- 85% credit utilization → -10 points
- Renter → +0 points
- **Total: 50 + 0 + 0 - 30 - 10 + 0 = 10 points → "Poor"**

### Validation and Testing

The ground truth algorithm is extensively tested:

```python
# From tests/test_accuracy.py
def test_calculate_ground_truth_high_score(self):
    input_data = {
        "income": 120000,
        "employment_duration_years": 12,
        "payment_defaults": 0,
        "credit_limit": 10000,
        "used_credit": 2500,  # 25% utilization
        "housing_status": "owner"
    }
    score, classification = calculate_ground_truth(input_data)
    assert score >= 85, f"Expected high score, got {score}"
    assert classification == "Good"
```

### Integration with the Analysis Workflow

1. **Data Loading**: Test profiles are loaded from `data/testdata.csv`
2. **API Prediction**: Each profile is sent to the LLM for credit scoring
3. **Ground Truth Calculation**: The same profile data generates ground truth scores
4. **Comparison**: Predicted vs. ground truth scores are compared using statistical metrics
5. **Report Generation**: Results are compiled into comprehensive accuracy reports

### Advantages of This Approach

**Pros:**
- ✅ Consistent and reproducible results
- ✅ No dependency on external data sources
- ✅ Transparent and auditable scoring logic
- ✅ Can test edge cases and specific scenarios
- ✅ No privacy concerns with real customer data

**Limitations:**
- ⚠️ May not reflect real-world credit scoring complexity
- ⚠️ Rule-based approach may miss nuanced relationships
- ⚠️ Ground truth is only as good as the algorithm design
- ⚠️ May not capture industry-specific scoring practices

### Future Enhancements

**Potential Improvements:**
1. **Weighted Scoring**: Different weights for different demographics
2. **Industry Benchmarks**: Incorporate external scoring standards
3. **Machine Learning Ground Truth**: Train on historical data for more realistic scores
4. **Regional Variations**: Adjust scoring based on geographic factors
5. **Time-based Factors**: Include economic conditions and trends

## How It Works

### 1. Ground Truth Calculation

The system establishes ground truth scores based on a comprehensive scoring algorithm:

- **Income Factor**: Higher income increases creditworthiness (+5 to +20 points)
- **Employment Stability**: Longer employment history improves score (+0 to +15 points)
- **Payment History**: Defaults significantly reduce score (-15 to -45 points)
- **Credit Utilization**: Lower utilization ratio improves score (-10 to +10 points)
- **Credit Inquiries**: Fewer recent inquiries are better (-10 to 0 points)
- **Housing Status**: Homeownership provides stability bonus (+0 to +5 points)
- **Address Stability**: Longer residence history improves score (+0 to +5 points)
- **Existing Loans**: Fewer existing loans are preferred (-5 to 0 points)

### 2. Prediction Extraction

For each test case, the system:
- Makes API calls with test profiles
- Extracts predicted credit scores from model responses
- Handles various response formats and error conditions
- Normalizes scores to a consistent scale (0-100)

### 3. Accuracy Metrics

The system calculates comprehensive accuracy metrics:

- **Mean Absolute Error (MAE)**: Average absolute difference between predicted and ground truth
- **Root Mean Square Error (RMSE)**: Square root of average squared differences
- **Mean Absolute Percentage Error (MAPE)**: Percentage-based error metric
- **R² Score**: Coefficient of determination measuring variance explained
- **Classification Accuracy**: Percentage of correctly classified risk categories

## Files Overview

### Core Implementation

1. **`analysis/accuracy.py`** - Main accuracy analysis module
   - Ground truth calculation algorithms
   - Prediction extraction and normalization
   - Statistical metrics computation
   - Score distribution analysis

2. **`tests/test_accuracy.py`** - Comprehensive unit tests
   - Ground truth calculation validation
   - Metric computation verification
   - Edge case handling
   - Error condition testing

3. **`tests/demo_accuracy.py`** - Demonstration script
   - Shows real-world usage examples
   - Provides sample analysis workflow

## Key Functions

### `calculate_ground_truth(input_data)`
Calculates expected credit score based on financial profile characteristics.

**Parameters:**
- `input_data`: Dictionary containing financial profile data

**Returns:**
- `score`: Calculated ground truth score (0-100)
- `classification`: Risk category ("Poor", "Average", "Good")

### `extract_predictions_and_ground_truth(responses)`
Extracts model predictions and calculates corresponding ground truth values.

**Parameters:**
- `responses`: List of API response dictionaries

**Returns:**
- `predictions`: Array of predicted scores
- `ground_truth`: Array of calculated ground truth scores
- `valid_count`: Number of successful extractions

### `calculate_regression_metrics(predictions, ground_truth)`
Computes regression-based accuracy metrics.

**Returns:**
- MAE, RMSE, MAPE, R² score

### `calculate_classification_metrics(predictions, ground_truth)`
Computes classification-based accuracy metrics.

**Returns:**
- Overall accuracy, confusion matrix, classification report

## Usage

### Through Web Interface

1. Open the Credit Scoring Validator web application
2. Configure API settings (URL, credentials)
3. Check the "Accuracy Analysis" checkbox
4. Click "Run Selected Analyses"
5. Review the generated accuracy report

### Programmatically

```python
from analysis.accuracy import run_accuracy_analysis

# Run complete accuracy analysis
results = run_accuracy_analysis()

# Access key metrics
mae = results['regression_metrics']['mae']
rmse = results['regression_metrics']['rmse']
r2_score = results['regression_metrics']['r2']
classification_accuracy = results['classification_metrics']['accuracy']

# View score distribution
distribution = results['score_distribution']
```

### Demo Script

```bash
cd /workspaces/credit_scoring_validator
python tests/demo_accuracy.py
```

## Report Features

The accuracy analysis report includes:

### Executive Summary
- Overall accuracy score and interpretation
- Mean Absolute Error and Root Mean Square Error
- Classification accuracy percentage
- Total profiles analyzed

### Regression Metrics
- **MAE**: Average absolute prediction error
- **RMSE**: Root mean square error (penalizes large errors)
- **MAPE**: Mean absolute percentage error
- **R² Score**: Proportion of variance explained by the model

### Classification Analysis
- **Accuracy**: Percentage of correctly classified risk categories
- **Confusion Matrix**: Detailed breakdown of classification results
- **Precision/Recall**: Per-class performance metrics

### Score Distribution Analysis
- Distribution of predicted vs. ground truth scores
- Systematic bias identification
- Outlier analysis and extreme cases

### Visualizations
- Scatter plots of predicted vs. actual scores
- Error distribution histograms
- Classification confusion matrix heatmap
- Score range distribution charts

## Interpretation Guidelines

### Regression Metrics
- **MAE < 10**: Excellent accuracy
- **MAE 10-20**: Good accuracy
- **MAE 20-30**: Acceptable accuracy
- **MAE > 30**: Poor accuracy, requires investigation

- **RMSE**: Should be close to MAE; large differences indicate outliers
- **MAPE < 15%**: Good percentage accuracy
- **R² > 0.8**: Strong correlation with ground truth

### Classification Accuracy
- **> 90%**: Excellent classification performance
- **80-90%**: Good classification performance
- **70-80%**: Acceptable performance
- **< 70%**: Poor performance, model improvements needed

### Common Issues
- **Systematic Bias**: Consistent over/under-prediction across score ranges
- **Variance Issues**: High RMSE relative to MAE indicates outlier problems
- **Classification Boundary Problems**: Confusion between adjacent risk categories

## Ground Truth Algorithm Details

### Scoring Components

**Income Assessment:**
```
- < $30k: +5 points
- $30k-50k: +10 points  
- $50k-80k: +15 points
- > $80k: +20 points
```

**Employment Duration:**
```
- < 1 year: +0 points
- 1-3 years: +5 points
- 3-7 years: +10 points
- > 7 years: +15 points
```

**Payment Defaults:**
```
- 0 defaults: +0 points
- 1 default: -15 points
- 2 defaults: -30 points
- 3+ defaults: -45 points
```

**Credit Utilization:**
```
- < 30%: +10 points
- 30-60%: +5 points
- 60-80%: +0 points
- > 80%: -10 points
```

### Base Score and Adjustments

- **Base Score**: 50 points
- **Final Range**: 0-100 points (clamped)
- **Risk Categories**: 
  - Poor: 0-49
  - Average: 50-69
  - Good: 70-100

## Best Practices

### For Model Developers
1. **Regular Validation**: Run accuracy analysis with each model update
2. **Ground Truth Review**: Periodically validate ground truth calculation logic
3. **Threshold Tuning**: Adjust classification thresholds based on accuracy results
4. **Feature Impact**: Analyze which features contribute most to accuracy gaps

### For Stakeholders
1. **Accuracy Targets**: Set minimum acceptable accuracy thresholds
2. **Trend Monitoring**: Track accuracy metrics over time
3. **Business Impact**: Correlate accuracy with business outcomes
4. **Model Governance**: Include accuracy analysis in model approval processes

## Testing

The implementation includes extensive test coverage:

- **Ground Truth Tests**: Validate scoring algorithm with known profiles
- **Metric Calculation Tests**: Verify statistical computations
- **Edge Case Tests**: Handle missing data and extreme values
- **Integration Tests**: Test complete workflow end-to-end

Run tests with:
```bash
python -m pytest tests/test_accuracy.py -v
```

## Troubleshooting

### Common Issues

**Low Accuracy Scores:**
- Check ground truth calculation logic
- Verify model prediction extraction
- Review data quality and completeness

**High Variance (RMSE >> MAE):**
- Identify and analyze outlier cases
- Check for data quality issues
- Review extreme value handling

**Classification Confusion:**
- Examine boundary cases near thresholds
- Consider adjusting classification cutoffs
- Review ground truth categorization logic

## Future Enhancements

Potential improvements to consider:

1. **Advanced Ground Truth**:
   - Machine learning-based ground truth
   - Industry benchmark integration
   - Historical performance correlation

2. **Additional Metrics**:
   - Area Under ROC Curve (AUC)
   - Precision-Recall curves
   - Calibration analysis

3. **Segmented Analysis**:
   - Accuracy by demographic groups
   - Performance by score ranges
   - Time-based accuracy trends

4. **Automated Insights**:
   - Root cause analysis of poor accuracy
   - Automated improvement recommendations
   - Predictive accuracy forecasting

## Conclusion

The accuracy analysis feature provides comprehensive evaluation of model prediction quality through multiple complementary metrics. It helps identify systematic issues, validates model performance, and ensures reliable credit scoring decisions. The implementation follows statistical best practices and provides actionable insights for continuous model improvement.
