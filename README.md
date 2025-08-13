# 🤖 Credit Scoring LLM Validator

A comprehensive web application for **evaluating and auditing LLM-based credit scoring systems** with advanced bias detection, real-time progress tracking, and professional reporting capabilities.

Built for rigorous testing of AI decision systems in regulated financial contexts with **asynchronous processing** to handle long-running API calls without browser timeouts.

---

## ✨ Key Features

* 🌐 **Modern Web UI**: Real-time progress tracking with dynamic status updates
* ⚡ **Asynchronous Processing**: Background analysis prevents browser timeouts
* 📊 **Advanced Bias Analysis**: Dual methodology combining observational and counterfactual fairness
* 🛡️ **Robustness Testing**: Comprehensive adversarial testing for model stability and reliability
* 🎯 **Realistic Test Data**: German-specific demographics with proper distributions
* 📈 **Professional Reports**: Auto-generated HTML reports with visualizations
* 🔒 **Secure API Integration**: Basic Auth support with enhanced error handling
* 📂 **Comprehensive Logging**: Detailed API call tracking and error diagnostics

---

## 🆕 Latest Enhancements

### **Robustness Analysis System** 🛡️
- **Adversarial Testing**: 5 types of input perturbations (noise, typos, missing values, etc.)
- **Stability Metrics**: Decision consistency and confidence stability analysis
- **Failure Case Detection**: Identifies specific scenarios where models fail
- **Professional Reporting**: Interactive visualizations and actionable insights

### **Asynchronous Analysis System**
- Background processing with real-time progress updates
- No more browser timeouts during long API processing
- Dynamic status polling with user-friendly progress indicators

### **Enhanced Bias Detection**
- **Demographic Parity**: Statistical analysis of outcome distributions
- **Counterfactual Fairness**: Tests for disparate treatment by modifying protected attributes
- **Bias Level Classification**: Automatic severity assessment (Low/Medium/High/Critical)

### **Improved Data Generation**
- German demographic distributions (employment, education, gender)
- Non-binary gender support (1.5% representation)
- German education system levels (vocational training, degrees)
- Age-appropriate employment status distributions

### **Professional Web Interface**
- Animated loading indicators with progress bars
- Real-time status messages during processing
- Enhanced error handling and user feedback
- Modern responsive design with TailwindCSS

---

## 📁 Project Architecture

```
credit_scoring_validator/
├── app.py                          # Flask web app with async analysis
├── config.py                       # API configuration and paths
├── requirements.txt                # Python dependencies
├── data/
│   └── testdata.csv               # Generated test dataset (German demographics)
├── generator/
│   └── testdata_generator.py      # Realistic demographic data generation
├── api/
│   └── client.py                  # Enhanced API client with error handling
├── analysis/
│   └── bias_fairness.py           # Advanced bias detection algorithms
├── reports/
│   ├── report_builder.py          # Professional HTML report generation
│   ├── templates/
│   │   └── report_template.html   # Jinja2 template for bias reports
│   └── generated/
│       └── bias_report.html       # Generated analysis reports
├── templates/
│   └── index.html                 # Modern web UI with progress tracking
├── results/
│   ├── logs/                      # Detailed logging for debugging
│   │   ├── api_client.log        # API call logs
│   │   └── bias_fairness.log     # Analysis process logs
│   └── responses/
│       └── bias_fairness.jsonl    # Collected API responses
├── tests/
│   ├── test_api_client.py         # API integration tests
│   ├── test_bias_fairness.py      # Bias analysis tests
│   └── test_app.py                # Web application tests
└── utils/
    ├── logger.py                   # Centralized logging setup
    └── file_io.py                 # File handling utilities
```

---

## 🚀 Quick Start Guide

### 1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

Key dependencies: Flask, pandas, requests, Jinja2, Faker

### 2. **Generate Test Data** (Optional)

```bash
cd generator/
python testdata_generator.py
```

This creates realistic German demographic test data in `data/testdata.csv` with:
- Proper age-employment distributions
- German education system levels
- Realistic income and credit patterns
- Non-binary gender representation (1.5%)

### 3. **Start the Application**

```bash
python app.py
```

The app runs on `http://localhost:5000` by default.

### 4. **Configure and Run Analysis**

1. **Open your browser** and navigate to the web interface
2. **Enter API credentials**:
   - API URL (your credit scoring endpoint)
   - Username and Password for Basic Auth
3. **Select "Bias & Fairness" analysis**
4. **Click "Run Selected Analyses"**
5. **Monitor real-time progress** with the animated progress bar
6. **View the generated report** once analysis completes

### 5. **Access Reports**

Generated reports are saved to:
```
reports/generated/bias_report.html
```

---

## 🔧 Advanced Usage

### **Custom Test Data**

To use your own dataset, replace `data/testdata.csv` with your data. Required columns:
- `name`, `gender`, `nationality`, `ethnicity`, `age`, `income`
- `employment_status`, `existing_loans`, `loan_amount`, `credit_limit`
- `used_credit`, `payment_defaults`, `credit_inquiries_last_6_months`
- `housing_status`, `address_stability_years`, `household_size`
- `employment_duration_years`, `disability_status`, `education_level`
- `marital_status`, `postal_code`, `language_preference`

### **API Endpoint Requirements**

Your credit scoring API should:
- Accept POST requests to `/score` endpoint
- Support Basic Authentication
- Accept JSON payload with applicant data
- Return structured response with credit score/classification

---

## 🧪 Analysis Modules

### ✅ **Bias & Fairness Analysis**

Our comprehensive bias detection system uses a **dual methodology approach**:

#### **📊 Observational Analysis (Demographic Parity)**
- Measures outcome distribution equality across demographic groups
- Calculates acceptance rates for each protected attribute
- Identifies statistical disparities in credit approvals
- Provides fairness metrics and disparity ratios

#### **🔄 Counterfactual Analysis (Disparate Treatment)**
- Tests individual records with modified protected attributes
- Detects direct discrimination by comparing decision changes
- Evaluates model consistency across demographic variations
- Identifies specific cases of unfair treatment

#### **🎯 Advanced Features**
- **Bias Severity Classification**: Automatic categorization (Low/Medium/High/Critical)
- **Statistical Significance Testing**: Robust analysis of group differences
- **Interactive Visualizations**: Charts and tables in generated reports
- **Detailed Logging**: Complete audit trail for compliance documentation

#### **📈 Metrics Calculated**
- Group acceptance rates and disparities
- Disparate impact ratios
- Counterfactual violation rates
- Statistical significance tests
- Bias level assessments

### 🔮 **Coming Soon**
- **Accuracy Analysis**: Performance metrics and error analysis
- **Robustness Testing**: Adversarial input and edge case handling
- **Transparency Evaluation**: Model explainability assessment
- **Drift Detection**: Temporal stability monitoring

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

## 📊 Generated Reports

### **Professional HTML Reports**
Located in: `reports/generated/bias_report.html`

#### **Report Contents**
- **Executive Summary**: Key findings and bias levels
- **Demographic Analysis**: Group-by-group breakdowns
- **Fairness Metrics**: Statistical measures with thresholds
- **Counterfactual Results**: Individual violation cases
- **Visual Charts**: Interactive data visualizations
- **Compliance Notes**: Regulatory considerations

#### **Report Features**
- Professional styling with modern CSS
- Mobile-responsive design
- Print-friendly formatting
- Detailed methodology explanations
- Actionable recommendations

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
pytest

# Run specific test modules
pytest tests/test_api_client.py      # API integration tests
pytest tests/test_bias_fairness.py   # Bias analysis tests
pytest tests/test_app.py             # Web application tests
```

### **Test Coverage**
- API client functionality and error handling
- Bias analysis algorithms and edge cases
- Flask application routes and responses
- Data generation and validation
- Report building and formatting

### **Quality Checks**
- Code linting and formatting standards
- Comprehensive error handling
- Security best practices
- Performance optimization
- Documentation completeness

---

## 🎯 Use Cases & Applications

This tool was specifically designed for **regulated financial AI systems**:

### **Primary Use Cases**
- 🏦 **Credit Scoring Systems**: Loan approval bias detection
- 💳 **Credit Card Applications**: Fair lending compliance
- 🏠 **Mortgage Underwriting**: Housing discrimination prevention
- 🏢 **Commercial Lending**: Business loan fairness evaluation

### **Compliance Frameworks**
- 📋 **Fair Credit Reporting Act (FCRA)**
- ⚖️ **Equal Credit Opportunity Act (ECOA)**
- 🇪🇺 **EU AI Act compliance**
- 📊 **ISO 42001 AI Management Systems**
- 🛡️ **GDPR algorithmic decision-making**

### **Benefits for Organizations**
- **Risk Mitigation**: Early bias detection before deployment
- **Regulatory Compliance**: Documentation for audits
- **Operational Efficiency**: Automated testing workflows
- **Stakeholder Confidence**: Transparent AI validation
- **Continuous Monitoring**: Regular bias assessment capabilities

---

## 🛠️ Development & Customization

### **Extending the System**
- **New Analysis Modules**: Add custom evaluation algorithms
- **Custom Metrics**: Implement domain-specific fairness measures
- **Report Templates**: Customize HTML output formatting
- **Data Sources**: Integrate additional demographic datasets
- **API Integrations**: Support for different authentication methods

### **Configuration Options**
- Bias threshold customization
- Protected attribute selection
- Report styling and branding
- Logging levels and formats
- Performance tuning parameters

---

## 📈 Roadmap

### **Upcoming Features**
- 🤖 **GPT-powered Analysis**: AI-generated insights and recommendations
- 🌍 **Multi-language Support**: International compliance frameworks

### **Long-term Vision**
- Comprehensive AI governance platform
- Industry-specific bias detection templates
- Automated remediation recommendations
- Integration with MLOps pipelines
- Real-time production monitoring

---

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for:
- Code style and standards
- Testing requirements
- Documentation expectations
- Pull request process

### **Areas for Contribution**
- Additional fairness metrics implementation
- New demographic data sources
- Enhanced visualization capabilities
- Performance optimizations
- Translation and localization

---

## 📄 License & Legal

This project is developed for educational and research purposes in responsible AI development. 

**Important**: This tool provides analysis capabilities but does not constitute legal advice. Organizations should consult with legal and compliance experts when implementing AI fairness systems in production environments.

---

## 📬 Support & Contact

- 🐛 **Issues**: Report bugs and feature requests via GitHub Issues
- 💬 **Discussions**: Join our community discussions
- 📧 **Contact**: Reach out for collaboration opportunities
- 📚 **Documentation**: Complete technical documentation available

---

**Built with ❤️ for responsible AI and fair algorithmic decision-making**

*© 2025 — Credit Scoring LLM Validator. Advancing fairness in financial AI systems.*
