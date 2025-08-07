# app.py

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from analysis.bias_fairness import run_bias_analysis
from reports.report_builder import build_bias_fairness_report
import config

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    show_button = False
    report_path = None
    result = None

    form_data = {
        "api_url": "",
        "username": "",
        "password": "",
        "run_bias": False
    }

    if request.method == "POST":
        form_data["api_url"] = request.form.get("api_url", "")
        form_data["username"] = request.form.get("username", "")
        form_data["password"] = request.form.get("password", "")
        form_data["run_bias"] = request.form.get("run_bias") == "on"

        # Validate required fields
        if form_data["run_bias"] and not all([form_data["api_url"], form_data["username"], form_data["password"]]):
            result = "❌ Error: Please fill in all API configuration fields."
            return render_template("index.html", show_button=show_button, report_path=report_path, 
                                   form_data=form_data, result=result)

        if form_data["run_bias"]:
            try:
                # Update config with form values
                config.API_URL = form_data["api_url"]
                config.USERNAME = form_data["username"] 
                config.PASSWORD = form_data["password"]
                
                results = run_bias_analysis()
                build_bias_fairness_report(results)
                report_path = "reports/generated/bias_report.html"
                show_button = True
                result = "✅ Bias analysis completed successfully!"
                
            except Exception as e:
                result = f"❌ Error running analysis: {str(e)}"
                app.logger.error(f"Analysis failed: {str(e)}")

    return render_template("index.html", show_button=show_button, report_path=report_path, 
                          form_data=form_data, result=result)


@app.route("/report")
def view_report():
    report_file = "reports/generated/bias_report.html"
    if not os.path.exists(report_file):
        return "Report not found. Please run the bias analysis first.", 404
    return send_from_directory("reports/generated", "bias_report.html")


if __name__ == "__main__":
    app.run(debug=True)
