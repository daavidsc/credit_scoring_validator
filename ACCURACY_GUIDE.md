# Accuracy Analysis - Implementation Guide

## Overview

The accuracy analysis feature evaluates how well the credit scoring model's predictions align with expected ground truth values. This analysis helps assess the overall performance and reliability of the model's scoring mechanism by comparing predicted scores against calculated ground truth benchmarks.

## What is Accuracy Analysis?

Accuracy analysis measures how close the model's predictions are to expected or "true" values. For credit scoring models, this is essential because:

- **Performance Validation**: Ensures the model produces reasonable and expected results
- **Quality Assurance**: Identifies systematic errors or biases in model predictions
- **Business Impact**: Inaccurate scoring can lead to poor lending decisions and financial losses
- **Regulatory Compliance**: Financial institutions must demonstrate model accuracy for regulatory approval

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
