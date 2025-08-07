# app.py

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
import threading
import time
import json
from analysis.bias_fairness import run_bias_analysis
from reports.report_builder import build_bias_fairness_report
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
        analysis_status["progress"] = 10
        analysis_status["message"] = "Starting bias analysis..."
        
        # Update config with form values
        config.API_URL = form_data["api_url"]
        config.USERNAME = form_data["username"] 
        config.PASSWORD = form_data["password"]
        
        analysis_status["progress"] = 20
        analysis_status["message"] = "Configuration updated, running analysis..."
        
        # Pass status reference to bias analysis
        from analysis.bias_fairness import set_status_reference
        set_status_reference(analysis_status)
        
        # Run the actual analysis
        results = run_bias_analysis()
        
        analysis_status["progress"] = 80
        analysis_status["message"] = "Analysis complete, generating report..."
        
        # Build the report
        build_bias_fairness_report(results)
        
        analysis_status["progress"] = 100
        analysis_status["message"] = "Report generated successfully!"
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
    return render_template("index.html")


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
        "run_bias": request.form.get("run_bias") == "on"
    }
    
    # Validate required fields
    if form_data["run_bias"] and not all([form_data["api_url"], form_data["username"], form_data["password"]]):
        return jsonify({"error": "Please fill in all API configuration fields."}), 400
    
    if form_data["run_bias"]:
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


@app.route("/", methods=["POST"])
def index_post():
    # Keep the old endpoint for compatibility, but redirect to new async approach
    form_data = {
        "api_url": request.form.get("api_url", ""),
        "username": request.form.get("username", ""),
        "password": request.form.get("password", ""),
        "run_bias": request.form.get("run_bias") == "on"
    }

    if request.method == "POST":
        form_data["api_url"] = request.form.get("api_url", "")
        form_data["username"] = request.form.get("username", "")
        form_data["password"] = request.form.get("password", "")
        form_data["run_bias"] = request.form.get("run_bias") == "on"

        # Validate required fields
        if form_data["run_bias"] and not all([form_data["api_url"], form_data["username"], form_data["password"]]):
            result = "❌ Error: Please fill in all API configuration fields."
            return render_template("index.html", show_button=False, report_path=None, 
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
