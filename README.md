# 🤖 Credit Scoring LLM Validator

A comprehensive Application for **evaluating and auditing LLM-based credit scoring systems** with advanced bias detection, robustness testing, accuracy analysis, and professional reporting capabilities.

Built for rigorous testing of AI decision systems in regulated financial contexts with **asynchronous processing** to handle long-running analyses without browser timeouts.

---

## 📚 Analysis Guides

Detailed guides for each analysis metric:

* 📊 **[Accuracy Analysis Guide](ACCURACY_GUIDE.md)** - Model prediction accuracy assessment and ground truth validation
* ⚖️ **[Bias & Fairness Guide](BIAS_FAIRNESS_GUIDE.md)** - Fair lending compliance and demographic parity analysis
* 🔄 **[Consistency Analysis Guide](CONSISTENCY_GUIDE.md)** - Deterministic behavior and repeatability validation
* 🔍 **[Data Quality Guide](DATA_QUALITY_GUIDE.md)** - Data integrity, completeness, and error rate analysis
* 🛡️ **[Robustness Analysis Guide](ROBUSTNESS_GUIDE.md)** - Adversarial testing and model stability assessment
* � **[Report Archiving Guide](ARCHIVING_GUIDE.md)** - Automatic report preservation during cache clearing
* �🔬 **[Transparency Guide](TRANSPARENCY_GUIDE.md)** - Model explainability and interpretability *(planned)*

Each guide provides detailed implementation information, usage examples, interpretation guidelines, and best practices.

---

## ✨ Key Features

### 🔬 **Comprehensive Analysis Suite**
* **Accuracy Analysis**: Model prediction quality assessment with ground truth validation
* **Bias & Fairness**: Advanced fairness testing across demographic groups
* **Consistency Analysis**: Deterministic behavior and repeatability validation
* **Data Quality**: API response integrity and completeness monitoring
* **Robustness Testing**: Adversarial input and stability assessment

### 🌐 **Modern Web Interface**
* **Integrated Test Data Generation**: Create custom test datasets directly from the web UI
* Real-time progress tracking with dynamic status updates
* Professional HTML reports with interactive visualizations
* Asynchronous processing prevents browser timeouts
* Mobile-responsive design with modern UI components
* **Integrated Cache Management**: Clear cached data directly from the web interface with automatic report archiving

### 🎯 **Realistic Test Data Generation**
* **Web Interface Generation**: Generate test data directly from the web UI with custom record counts
* **Command Line Support**: Traditional script-based generation for automation
* German-specific demographic distributions
* Age-appropriate employment status patterns
* Educational system modeling (vocational training, degrees)
* Non-binary gender representation and diversity
* **Customizable Sample Sizes**: Generate anywhere from 10 to 1000+ records

### 🔒 **Enterprise-Ready Security**
* Basic Auth support with secure credential handling
* Comprehensive error handling and diagnostics
* Detailed audit trails and logging
* API timeout and retry mechanisms

---

## 🆕 Latest Enhancements

### **Integrated Test Data Generation** 🎯
- **Web UI Integration**: Generate test data directly from the web interface
- **Custom Record Counts**: Specify exact number of records (10-1000+)
- **Real-time Progress**: Live status updates during generation
- **Instant Availability**: Generated data immediately ready for analysis
- **German Demographics**: Realistic population distributions and patterns

### **Multi-Metric Analysis System** �
- **Five Analysis Types**: Accuracy, bias/fairness, consistency, data quality, and robustness
- **Professional Reports**: Individual HTML reports for each analysis with visualizations
- **Statistical Rigor**: Comprehensive metrics and significance testing
- **Actionable Insights**: Clear interpretation guidelines and recommendations

### **Robustness Analysis** 🛡️
- **5 Perturbation Types**: Numerical noise, text typos, case changes, missing values, extreme values
- **Decision Consistency**: Tracks model stability under input variations
- **Confidence Analysis**: Measures prediction confidence stability
- **Failure Case Detection**: Identifies specific scenarios where models fail

### **Accuracy Assessment** 📊
- **Ground Truth Calculation**: Financial profile-based expected scores
- **Regression Metrics**: MAE, RMSE, MAPE, R² coefficient
- **Classification Metrics**: Accuracy, precision, recall, F1-score
- **Score Distribution Analysis**: Statistical analysis of prediction patterns

### **Enhanced Bias Detection** ⚖️
- **Demographic Parity**: Statistical analysis of outcome distributions across groups
- **Protected Attributes**: Gender, ethnicity, nationality, disability, marital status
- **Statistical Tests**: Chi-square, Fisher's exact, and significance testing
- **Compliance Reporting**: Documentation for regulatory requirements

### **Consistency Validation** 🔄
- **Deterministic Testing**: Ensures identical inputs produce identical outputs
- **Temporal Analysis**: Consistency across different time periods
- **Hash-based Tracking**: Precise duplicate input identification
- **Variance Analysis**: Statistical measurement of response variations

---

## 📁 Project Architecture

```
credit_scoring_validator/
├── app.py                          # Flask web app with async analysis
├── config.py                       # API configuration and paths
├── requirements.txt                # Python dependencies
├── *.md                           # Comprehensive analysis guides
│   ├── ACCURACY_GUIDE.md          # Model prediction accuracy assessment
│   ├── BIAS_FAIRNESS_GUIDE.md     # Fair lending compliance analysis
│   ├── CONSISTENCY_GUIDE.md       # Deterministic behavior validation
│   ├── DATA_QUALITY_GUIDE.md      # Data integrity and error analysis
│   ├── ROBUSTNESS_GUIDE.md        # Adversarial testing and stability
│   └── TRANSPARENCY_GUIDE.md      # LIME explainability and quality assessment
├── data/
│   └── testdata.csv               # Generated test dataset (German demographics)
├── generator/
│   └── testdata_generator.py      # Realistic demographic data generation
├── api/
│   └── client.py                  # Enhanced API client with error handling
├── analysis/                      # Complete analysis module suite
│   ├── accuracy.py                # Ground truth validation and regression metrics
│   ├── bias_fairness.py           # Advanced bias detection algorithms
│   ├── consistency.py             # Deterministic behavior and repeatability
│   ├── data_quality.py            # API response integrity monitoring
│   ├── data_quality_analyzer.py   # Comprehensive data quality assessment
│   ├── drift.py                   # Model performance drift detection
│   ├── robustness.py              # Adversarial testing and perturbation analysis
│   └── transparency.py            # LIME explanations and interpretability
├── reports/
│   ├── report_builder.py          # Professional HTML report generation
│   ├── templates/                 # Jinja2 templates for all analysis types
│   │   ├── accuracy_template.html          # Accuracy analysis reports
│   │   ├── consistency_template.html       # Consistency validation reports
│   │   ├── robustness_template.html        # Robustness testing reports
│   │   ├── comprehensive_data_quality_template.html  # Data quality reports
│   │   └── report_template.html            # General bias/fairness reports
│   └── generated/                 # Auto-generated analysis reports
│       ├── accuracy_report.html           # Model prediction accuracy
│       ├── bias_report.html               # Fairness and demographic analysis
│       ├── consistency_report.html        # Deterministic behavior
│       ├── comprehensive_data_quality_report.html  # Data integrity
│       └── robustness_report.html         # Adversarial testing results
├── templates/
│   └── index.html                 # Modern web UI with progress tracking
├── results/
│   ├── logs/                      # Detailed logging for all analysis types
│   │   ├── accuracy.log           # Accuracy analysis logs
│   │   ├── api_client.log         # API call logs
│   │   ├── bias_fairness.log      # Bias analysis logs
│   │   ├── consistency.log        # Consistency testing logs
│   │   ├── data_quality.log       # Data quality logs
│   │   └── robustness.log         # Robustness testing logs
│   └── responses/                 # Collected API responses by analysis type
│       ├── accuracy.jsonl         # Accuracy test responses
│       ├── bias_fairness.jsonl    # Bias analysis responses
│       ├── consistency.jsonl      # Consistency test responses
│       ├── data_quality.jsonl     # Data quality responses
│       └── robustness.jsonl       # Robustness test responses
├── tests/                         # Comprehensive testing suite
│   ├── test_accuracy.py           # Accuracy analysis tests
│   ├── test_api_client.py         # API integration tests
│   ├── test_bias_fairness.py      # Bias detection tests
│   ├── test_consistency.py        # Consistency validation tests
│   ├── test_data_quality.py       # Data quality tests
│   ├── test_robustness.py         # Robustness testing tests
│   ├── demo_*.py                  # Interactive demonstration scripts
│   └── test_app.py                # Web application tests
└── utils/
    ├── file_io.py                 # File handling utilities
    ├── logger.py                  # Centralized logging setup
    ├── progress.py                # Real-time progress tracking
    └── response_collector.py      # API response collection and caching
```

---

## 🚀 Quick Start Guide

### 1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

**Key dependencies**: Flask, pandas, requests, Jinja2, numpy, scipy, matplotlib

### 2. **Generate Test Data**

You can generate test data in two ways:

#### **Option A: Web Interface (Recommended)**
1. Start the application: `python app.py`
2. Open `http://localhost:5000` in your browser
3. Click **"Generate Test Data"** button
4. **Custom Record Count**: Enter desired number of records (10-1000+)
5. **Real-time Feedback**: Watch progress with live status updates
6. **Instant Availability**: Generated data is immediately available for analysis

#### **Option B: Command Line**
```bash
python generator/testdata_generator.py
```

**Generated Data Features**:
- Proper age-employment distributions
- German education system levels
- Realistic income and credit patterns
- Diverse demographic representation
- **Customizable Volume**: Generate the exact number of test records you need

### 3. **Start the Application**

```bash
python app.py
```

The web interface runs on `http://localhost:5000`

### 4. **Run Analysis**

1. **Configure API Settings**:
   - Enter your credit scoring API URL
   - Provide authentication credentials
   - Test connection before analysis

2. **Select Analysis Types**:
   - ✅ Accuracy Analysis
   - ✅ Bias & Fairness Analysis  
   - ✅ Consistency Analysis
   - ✅ Data Quality Analysis
   - ✅ Robustness Analysis

3. **Manage Cache (Optional)**:
   - Clear specific analysis caches to force fresh data
   - Use "Clear ALL caches" after sample size updates
   - Balance between speed (cached) and freshness (cleared)
   - **Auto-Archive Reports**: Existing reports are automatically archived before cache clearing
   - **Archived Reports**: Saved in `reports/archive/archive_YYYYMMDD_HHMMSS/` with timestamps

4. **Monitor Progress**: Real-time status updates with progress bars

5. **Review Reports**: Professional HTML reports with visualizations

### 5. **Access Generated Reports**

Reports are saved to `reports/generated/`:
- `accuracy_report.html` - Model prediction accuracy
- `bias_report.html` - Fairness and demographic analysis
- `consistency_report.html` - Deterministic behavior
- `data_quality_report.html` - Data integrity assessment
- `robustness_report.html` - Adversarial testing results

---

## �️ API Requirements & Configuration

### **Credit Scoring API Specification**
Your credit scoring API should support:

#### **Endpoint Requirements**
- **URL**: POST endpoint (e.g. `/score`)
- **Authentication**: Basic Auth (username/password)
- **Content-Type**: `application/json`
- **Request Format**: JSON payload with applicant data

#### **Required Input Fields**
```json
{
  "name": "string",
  "age": "integer",
  "income": "number",
  "employment_status": "string",
  "employment_duration_years": "number",
  "credit_limit": "number",
  "used_credit": "number", 
  "payment_defaults": "integer",
  "credit_inquiries_last_6_months": "integer",
  "housing_status": "string",
  "address_stability_years": "number",
  "existing_loans": "integer",
  "loan_amount": "number",
  "household_size": "integer",
  "gender": "string",
  "nationality": "string", 
  "ethnicity": "string",
  "marital_status": "string",
  "disability_status": "string",
  "education_level": "string",
  "postal_code": "string",
  "language_preference": "string"
}
```

#### **Expected Response Format**
The API should return structured JSON with credit information:

```json
{
  "credit_score": 75,
  "classification": "Good",
  "explanation": "Strong employment history and low credit utilization"
}
```

### **Configuration Options**
- **Request Timeout**: Configurable timeout for API calls
- **Retry Logic**: Automatic retry on temporary failures
- **Error Handling**: Graceful degradation on API issues
- **Batch Processing**: Efficient handling of multiple requests

---

## 🧪 Analysis Modules

### ✅ **Accuracy Analysis** 📊
**Model prediction quality assessment with comprehensive statistical validation**

- **Full Dataset Processing**: Uses all available test data for comprehensive accuracy assessment
- **Ground Truth Calculation**: Financial profile-based expected credit scores
- **Regression Metrics**: MAE, RMSE, MAPE, R² coefficient for score accuracy
- **Classification Metrics**: Accuracy, precision, recall for approval decisions
- **Score Distribution**: Statistical analysis of prediction patterns
- **Performance Validation**: Model reliability assessment across entire dataset

### ✅ **Bias & Fairness Analysis** ⚖️
**Comprehensive fairness testing across demographic groups**

- **Protected Attributes**: Gender, ethnicity, nationality, disability status, marital status
- **Statistical Parity**: Equal treatment rates across demographic groups
- **Demographic Analysis**: Group-specific outcome distributions
- **Significance Testing**: Chi-square and Fisher's exact tests
- **Compliance Documentation**: Regulatory audit trail generation

### ✅ **Consistency Analysis** 🔄
**Deterministic behavior and repeatability validation with enhanced statistical power**

- **Exact Match Testing**: Identical inputs produce identical outputs
- **Temporal Consistency**: Stability across different time periods
- **Hash-based Tracking**: Precise duplicate input identification
- **Variance Analysis**: Statistical measurement of response variations
- **System Reliability**: Infrastructure stability assessment
- **Configurable Testing**: Customizable sample sizes and repeat counts

### ✅ **Data Quality Analysis** �
**API response integrity and completeness monitoring**

- **Error Rate Tracking**: HTTP errors, timeouts, connection failures
- **Response Completeness**: Missing fields and data validation
- **Parsing Success**: Structured data extraction reliability
- **Score Validity**: Credit scores within expected ranges
- **Quality Scoring**: Overall data integrity assessment

### ✅ **Robustness Analysis** 🛡️
**Adversarial testing and model stability assessment with comprehensive coverage**

- **5 Perturbation Types**: 
  - Numerical noise injection
  - Text typo introduction
  - Case sensitivity testing
  - Missing value handling
  - Extreme value resilience
- **Decision Consistency**: Model stability under input variations
- **Confidence Analysis**: Prediction confidence stability
- **Failure Case Detection**: Identifies problematic scenarios
- **Comprehensive Coverage**: More test cases for better reliability assessment

---

## 🔐 Security & Authentication

### **API Authentication Support**
- **Basic Auth**: Username/password authentication
- **Dynamic Configuration**: Runtime API credential updates
- **Secure Handling**: Credentials not stored persistently
- **Connection Testing**: Pre-analysis API validation

### **Error Handling & Debugging**
- **Enhanced Logging**: Detailed API call tracking
- **Error Diagnostics**: Comprehensive error messages
- **Timeout Management**: Configurable request timeouts
- **Status Monitoring**: Real-time processing updates

---

## 📊 Professional Reports

### **Comprehensive HTML Reports**
Each analysis generates a professional HTML report with:

#### **Accuracy Report** (`accuracy_report.html`)
- **Statistical Metrics**: MAE, RMSE, MAPE, R² scores
- **Classification Performance**: Accuracy, precision, recall
- **Score Distribution**: Predicted vs. ground truth analysis
- **Performance Insights**: Model reliability assessment

#### **Bias & Fairness Report** (`bias_report.html`)
- **Demographic Breakdown**: Group-by-group fairness analysis
- **Statistical Tests**: Significance testing results
- **Compliance Metrics**: Regulatory requirement assessment
- **Visual Charts**: Interactive demographic comparisons

#### **Consistency Report** (`consistency_report.html`)
- **Deterministic Analysis**: Exact match rate assessment
- **Variance Metrics**: Response stability statistics
- **Temporal Patterns**: Time-based consistency trends
- **Reliability Scores**: System stability evaluation

#### **Data Quality Report** (`data_quality_report.html`)
- **Error Analysis**: API failure rates and categorization
- **Completeness Metrics**: Missing data assessment
- **Validation Results**: Data integrity checks
- **Quality Scores**: Overall data reliability rating

#### **Robustness Report** (`robustness_report.html`)
- **Perturbation Analysis**: Stability under different input variations
- **Decision Consistency**: Model behavior under adversarial conditions
- **Failure Cases**: Specific scenarios where model fails
- **Stability Metrics**: Confidence and decision reliability


---

## ⚡ Technical Architecture

### **Asynchronous Processing**
- **Background Threads**: Non-blocking analysis execution
- **Status Polling**: Real-time progress updates via AJAX
- **Progress Tracking**: Granular status reporting
- **Error Recovery**: Graceful handling of API failures

### **Performance Optimizations**
- **Efficient API Batching**: Optimized request handling
- **Memory Management**: Streaming data processing
- **Logging Optimization**: Structured logging with rotation
- **Resource Cleanup**: Proper thread and connection management
- **Smart Caching System**: API response caching with selective clearing
- **Cache Management**: Web interface for clearing stale cached data with automatic report archiving

### **Web Interface**
- **Modern UI**: TailwindCSS with animated components
- **Real-time Updates**: Dynamic progress indicators
- **Error Feedback**: User-friendly error messages
- **Responsive Design**: Works on desktop and mobile

---

## 🧪 Testing & Quality Assurance

### **Automated Testing Suite**

```bash
# Run all tests
python -m pytest tests/

# Run specific test modules
python -m pytest tests/test_accuracy.py          # Accuracy analysis tests
python -m pytest tests/test_bias_fairness.py     # Bias detection tests
python -m pytest tests/test_consistency.py       # Consistency validation tests
python -m pytest tests/test_robustness.py        # Robustness testing tests
python -m pytest tests/test_api_client.py        # API integration tests
python -m pytest tests/test_app.py               # Web application tests
```

### **Demo Scripts**
Interactive demonstration scripts for each analysis:

```bash
python tests/demo_accuracy.py      # Accuracy analysis demonstration
python tests/demo_consistency.py   # Consistency testing demo
python tests/demo_robustness.py    # Robustness analysis demo
```

### **Test Coverage Areas**
- **Algorithm Validation**: Statistical calculations and metrics
- **API Integration**: Error handling and response processing  
- **Report Generation**: Template rendering and visualization
- **Data Processing**: Input validation and transformation
- **Edge Cases**: Boundary conditions and error scenarios

### **Quality Standards**
- Comprehensive unit and integration testing
- Code documentation and type hints
- Error handling and graceful degradation
- Performance optimization and memory management
- Security best practices and input validation

---

## 🎯 Use Cases & Applications

### **Financial Services Applications**
- 🏦 **Credit Scoring Systems**: Loan approval fairness and accuracy assessment
- 💳 **Credit Card Underwriting**: Application processing bias detection  
- 🏠 **Mortgage Lending**: Housing discrimination prevention and compliance
- 🏢 **Commercial Lending**: Business loan fairness and model validation
- 📈 **Risk Assessment**: Model reliability and stability evaluation

### **Regulatory Compliance Frameworks**
- 📋 **Fair Credit Reporting Act (FCRA)**: Adverse action requirements
- ⚖️ **Equal Credit Opportunity Act (ECOA)**: Discrimination prevention
- 🇪🇺 **EU AI Act**: AI system risk assessment and documentation
- 📊 **ISO 42001**: AI management systems compliance
- 🛡️ **GDPR Article 22**: Automated decision-making transparency

### **Organizational Benefits**
- **Risk Mitigation**: Early detection of bias and performance issues
- **Regulatory Readiness**: Comprehensive documentation for audits
- **Model Validation**: Statistical validation before deployment
- **Continuous Monitoring**: Regular assessment capabilities
- **Stakeholder Confidence**: Transparent AI validation process
- **Operational Efficiency**: Automated testing workflows

### **Industry Applications**
- **Banking**: Consumer and commercial lending validation
- **Insurance**: Underwriting fairness assessment
- **Fintech**: Digital lending platform validation
- **Consulting**: AI audit and compliance services

---

## 🛠️ Development & Customization

### **Extending the System**
- **New Analysis Modules**: Add custom evaluation algorithms
- **Custom Metrics**: Implement domain-specific fairness measures
- **Data Sources**: Integrate additional demographic datasets
- **API Integrations**: Support for different authentication methods and JSON structures

### **Configuration Options**
- Bias threshold customization
- Protected attribute selection
- Report styling and branding
- Logging levels and formats
- Performance tuning parameters

---

## 📈 Development Roadmap

### **Current Status** ✅
- ✅ **Core Analysis Suite**: Accuracy, bias, consistency, data quality, robustness
- ✅ **Professional Reporting**: HTML reports with visualizations
- ✅ **Web Interface**: Modern UI with real-time progress tracking
- ✅ **Integrated Test Data Generation**: Web UI and command-line generation with custom record counts
- ✅ **German Demographics**: Realistic population distributions and demographic modeling
- ✅ **Comprehensive Testing**: Unit and integration test coverage

### **Next Phase** 🚧
- 🔬 **Transparency Analysis**: SHAP and LIME integration for model explainability
- 📈 **Drift Detection**: Temporal model performance monitoring
- 🌍 **Multi-Language**: Extended demographic datasets and localization
- 📊 **Advanced Visualizations**: Enhanced charts and interactive dashboards

### **Future Enhancements** 🔮
- 🤖 **AI-Powered Insights**: GPT-assisted analysis and recommendations
- 🔄 **CI/CD Integration**: Automated testing in pipelines
- 🌐 **Cloud Deployment**: Scalable cloud infrastructure options

---

## 📄 License & Legal Notice

### **License**
This project is developed for educational and research purposes in responsible AI development. 

### **Important Legal Disclaimer**
⚠️ **This tool provides analysis capabilities but does not constitute legal advice.** 

Organizations should:
- Consult with legal and compliance experts when implementing AI fairness systems
- Validate results with domain expertise before making business decisions  
- Ensure compliance with applicable regulations in their jurisdiction
- Conduct additional validation beyond this tool's capabilities

### **Regulatory Compliance**
While this tool helps assess AI fairness and performance, it is the organization's responsibility to:
- Understand applicable laws and regulations
- Implement appropriate governance frameworks
- Maintain audit trails and documentation
- Regularly validate and monitor AI systems in production

### **Data Privacy**
- This tool processes test data locally and does not store personal information
- API calls are made directly to your specified endpoints
- No data is transmitted to third parties
- Users are responsible for ensuring data privacy compliance

---

### **Development Guidelines**
- Follow existing code style and conventions
- Add unit tests for new functionality
- Update documentation for changes
- Ensure backward compatibility when possible
- Include clear commit messages and PR descriptions


---

## 📬 Support & Contact

- 🐛 **Issues**: Report bugs and feature requests via GitHub Issues
- 📚 **Documentation**: Complete technical documentation available

---


*© 2025 — FS MDAM Experential Learning Group 4. Credit Scoring LLM Validator. Advancing fairness in financial AI systems.*
