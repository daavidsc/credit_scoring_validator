# app.py

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
import threading
import time
import json
from analysis.bias_fairness import run_bias_analysis
from analysis.accuracy import run_accuracy_analysis
from analysis.robustness import run_robustness_analysis
from analysis.consistency import run_consistency_analysis
from reports.report_builder import build_bias_fairness_report, build_accuracy_report, build_robustness_report, build_consistency_report
import config

app = Flask(__name__)

# Global variables to track analysis progress
analysis_status = {
    "running": False,
    "completed": False,
    "error": None,
    "progress": 0,
    "message": "Ready to start analysis"
}

def run_analysis_background(form_data):
    """Run the analysis in the background and update status"""
    global analysis_status
    
    try:
        analysis_status["running"] = True
        analysis_status["completed"] = False
        analysis_status["error"] = None
        analysis_status["progress"] = 5
        analysis_status["message"] = "Starting analysis..."
        
        # Update config with form values
        config.API_URL = form_data["api_url"]
        config.USERNAME = form_data["username"] 
        config.PASSWORD = form_data["password"]
        config.MODEL = form_data.get("model", "gpt-3.5-turbo-0125")
        
        results = {}
        total_analyses = sum([form_data["run_bias"], form_data["run_accuracy"], form_data["run_robustness"], form_data["run_consistency"]])
        current_analysis = 0
        
        # Run bias analysis if selected
        if form_data["run_bias"]:
            current_analysis += 1
            analysis_status["progress"] = 10 + (current_analysis - 1) * 22
            analysis_status["message"] = f"Running bias analysis ({current_analysis}/{total_analyses})..."
            
            # Pass status reference to bias analysis
            from analysis.bias_fairness import set_status_reference
            set_status_reference(analysis_status)
            
            bias_results = run_bias_analysis()
            results["bias_fairness"] = bias_results
            
            # Build bias report
            build_bias_fairness_report(bias_results)
        
        # Run accuracy analysis if selected
        if form_data["run_accuracy"]:
            current_analysis += 1
            analysis_status["progress"] = 10 + (current_analysis - 1) * 22
            analysis_status["message"] = f"Running accuracy analysis ({current_analysis}/{total_analyses})..."
            
            # Pass status reference to accuracy analysis
            from analysis.accuracy import set_status_reference
            set_status_reference(analysis_status)
            
            accuracy_results = run_accuracy_analysis()
            results["accuracy"] = accuracy_results
            
            # Build accuracy report
            build_accuracy_report(accuracy_results)
        
        # Run robustness analysis if selected
        if form_data["run_robustness"]:
            current_analysis += 1
            analysis_status["progress"] = 10 + (current_analysis - 1) * 22
            analysis_status["message"] = f"Running robustness analysis ({current_analysis}/{total_analyses})..."
            
            # Pass status reference to robustness analysis
            from analysis.robustness import set_status_reference
            set_status_reference(analysis_status)
            
            robustness_results = run_robustness_analysis()
            results["robustness"] = robustness_results
            
            # Build robustness report
            build_robustness_report(robustness_results)
        
        # Run consistency analysis if selected
        if form_data["run_consistency"]:
            current_analysis += 1
            analysis_status["progress"] = 10 + (current_analysis - 1) * 22
            analysis_status["message"] = f"Running consistency analysis ({current_analysis}/{total_analyses})..."
            
            # Pass status reference to consistency analysis
            from analysis.consistency import set_status_reference
            set_status_reference(analysis_status)
            
            consistency_results = run_consistency_analysis()
            results["consistency"] = consistency_results
            
            # Build consistency report
            build_consistency_report(consistency_results)
        
        analysis_status["progress"] = 95
        analysis_status["message"] = "Analysis complete, finalizing reports..."
        
        analysis_status["progress"] = 100
        analysis_status["message"] = "All analyses completed successfully!"
        analysis_status["completed"] = True
        analysis_status["running"] = False
        
    except Exception as e:
        analysis_status["running"] = False
        analysis_status["error"] = str(e)
        analysis_status["message"] = f"Error: {str(e)}"
        app.logger.error(f"Background analysis failed: {str(e)}")
        import traceback
        app.logger.error(f"Full traceback: {traceback.format_exc()}")


@app.route("/")
def index():
    # Provide default form data for template
    form_data = {
        "api_url": "",
        "username": "",
        "password": "",
        "run_bias": False,
        "run_accuracy": False,
        "run_robustness": False,
        "run_consistency": False,
        "model": "gpt-3.5-turbo-0125"
    }
    return render_template("index.html", form_data=form_data)


@app.route("/start_analysis", methods=["POST"])
def start_analysis():
    """Start the analysis in the background"""
    global analysis_status
    
    if analysis_status["running"]:
        return jsonify({"error": "Analysis already running"}), 400
    
    form_data = {
        "api_url": request.form.get("api_url", ""),
        "username": request.form.get("username", ""),
        "password": request.form.get("password", ""),
        "run_bias": request.form.get("run_bias") == "on",
        "run_accuracy": request.form.get("run_accuracy") == "on",
        "run_robustness": request.form.get("run_robustness") == "on",
        "run_consistency": request.form.get("run_consistency") == "on",
        "model": request.form.get("model", "gpt-3.5-turbo-0125")
    }
    
    # Validate that at least one analysis is selected
    if not (form_data["run_bias"] or form_data["run_accuracy"] or form_data["run_robustness"] or form_data["run_consistency"]):
        return jsonify({"error": "Please select at least one analysis to run."}), 400
    
    # Validate required fields for analyses that need API calls
    if (form_data["run_bias"] or form_data["run_robustness"] or form_data["run_consistency"]) and not all([form_data["api_url"], form_data["username"], form_data["password"]]):
        return jsonify({"error": "Please fill in all API configuration fields for bias/robustness/consistency analysis."}), 400
    
    # For accuracy analysis, we can run it on existing data even without API credentials
    if form_data["run_bias"] or form_data["run_accuracy"] or form_data["run_robustness"] or form_data["run_consistency"]:
        # Start analysis in background thread
        thread = threading.Thread(target=run_analysis_background, args=(form_data,))
        thread.daemon = True
        thread.start()
        
        return jsonify({"message": "Analysis started successfully"})
    
    return jsonify({"error": "No analysis selected"}), 400


@app.route("/status")
def get_status():
    """Get the current analysis status"""
    return jsonify(analysis_status)


@app.route("/report")
def view_report():
    report_file = "reports/generated/bias_report.html"
    if not os.path.exists(report_file):
        return "Report not found. Please run the bias analysis first.", 404
    return send_from_directory("reports/generated", "bias_report.html")


@app.route("/accuracy_report")
def view_accuracy_report():
    report_file = "reports/generated/accuracy_report.html"
    if not os.path.exists(report_file):
        return "Accuracy report not found. Please run the accuracy analysis first.", 404
    return send_from_directory("reports/generated", "accuracy_report.html")


@app.route("/robustness_report")
def view_robustness_report():
    report_file = "reports/generated/robustness_report.html"
    if not os.path.exists(report_file):
        return "Robustness report not found. Please run the robustness analysis first.", 404
    return send_from_directory("reports/generated", "robustness_report.html")


@app.route("/consistency_report")
def view_consistency_report():
    report_file = "reports/generated/consistency_report.html"
    if not os.path.exists(report_file):
        return "Consistency report not found. Please run the consistency analysis first.", 404
    return send_from_directory("reports/generated", "consistency_report.html")


if __name__ == "__main__":
    app.run(debug=True)
