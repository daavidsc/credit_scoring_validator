# tests/test_report_generator.py

import os
from analysis.bias_fairness import run_bias_analysis
from reports.report_builder import build_bias_fairness_report

REPORT_PATH = "results/reports/bias_fairness_report.html"

def test_bias_fairness_report_generation():
    # Run analysis
    results = run_bias_analysis()

    # Generate report
    build_bias_fairness_report(results)

    # Check file exists
    assert os.path.exists(REPORT_PATH), "Report file was not created."

    # Check it’s not empty
    with open(REPORT_PATH, "r") as f:
        content = f.read()
        assert len(content) > 100, "Report file is unexpectedly small or empty."

    print("✅ Bias fairness report generated and verified successfully.")
