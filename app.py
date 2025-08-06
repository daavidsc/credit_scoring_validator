# app.py

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from analysis.bias_fairness import run_bias_analysis
from reports.report_builder import build_bias_fairness_report

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    show_button = False
    report_path = None

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

        if form_data["run_bias"]:
            results = run_bias_analysis()
            build_bias_fairness_report(results)
            report_path = "reports/generated/bias_report.html"
            show_button = True

    return render_template("index.html", show_button=show_button, report_path=report_path, form_data=form_data)


@app.route("/report")
def view_report():
    return send_from_directory("reports/generated", "bias_report.html")


if __name__ == "__main__":
    app.run(debug=True)
