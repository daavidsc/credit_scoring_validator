# 🤖 LLM Evaluation Dashboard

A modular web application to **evaluate and audit GenAI / LLM-based decision systems** for key compliance attributes, starting with **Bias & Fairness**.

Built for rapid testing, validation, and documentation of AI systems – especially in regulated contexts like **credit scoring**, **HR**, or **insurance**.

---

## ✨ Features

* ✅ Web-based UI to enter API credentials and select evaluation modules
* 📦 Modular backend supporting multiple analysis types
* 📊 **Bias & Fairness Analysis**: Demographic parity, disparate impact, counterfactual fairness
* 📝 Auto-generated, human-readable HTML report
* 📂 Clear folder structure for results, logs, and configs
* 🔒 Supports **Basic Auth**-protected APIs

---

## 📁 Project Structure

```
credit_scoring_validator/
├── app.py                     # Flask web app
├── config.py                  # Config paths for logs, reports, etc.
├── data/                      # Input test dataset (e.g. testdata.csv)
├── api/
│   └── client.py              # Sends API requests
├── analysis/
│   └── bias_fairness.py       # Bias evaluation logic
├── reports/
│   ├── report_builder.py      # Generates HTML reports
│   └── templates/
│       └── report_template.html  # Report HTML template (Jinja2)
├── results/
│   └── bias_fairness.jsonl    # Collected API responses
├── tests/
│   └── ...                    # Pytest test cases
└── README.md
```

---

## 🚀 Getting Started

### 1. Install Requirements

```bash
pip install -r requirements.txt
```

(Requirements include Flask, pandas, requests, Jinja2, etc.)

### 2. Prepare Data

Add your test dataset to:

```
/data/testdata.csv
```

Ensure the format matches the expected input schema for your scoring API.

### 3. Run the Web App

```bash
python app.py
```

Open your browser and go to:

```
http://localhost:5000
```

---

## 🧪 Modules

### ✅ Bias & Fairness

* **Demographic Parity** – How equally are outcomes distributed across groups?
* **Disparate Impact Ratio** – Ratio between most and least favored groups
* **Counterfactual Fairness** – Would the decision change if only a protected attribute were altered?

### Coming Soon

* Accuracy
* Robustness
* Transparency
* Stability & Drift

---

## 🔐 API Authentication

We support **Basic Auth** for protected endpoints.

You can enter:

* ✅ API URL
* 👤 Username
* 🔑 Password

These are used to call your LLM scoring API in real time.

---

## 📊 Reports

After each run, the tool generates an HTML report in:

```
results/report_bias_fairness.html
```

The report includes:

* 📈 Decision rates per group
* ⚖️ Fairness metrics
* 🚨 Counterfactual violations
* 🧠 (Planned) GPT-based summaries & checklist evaluations

---

## 🧪 Testing

To run unit tests:

```bash
pytest
```

Make sure all modules and the API client work as expected before deployment.

---

## 🧠 Why This Tool?

This project was developed to explore **responsible GenAI validation** for use cases like:

* 📉 Credit Scoring
* 🢑 HR Screening
* 📋 Insurance Risk Assessment
* ⚖️ AI compliance with EU AI Act / ISO 42001

---

## 📬 Feedback & Contributions

Have ideas, issues, or want to collaborate? Feel free to open an issue or reach out.

---

© 2025 — GenAI Validator Project. Built with ❤️ for responsible AI.
