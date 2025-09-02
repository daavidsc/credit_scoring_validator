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
from analysis.transparency import run_transparency_analysis
from analysis.data_quality_analyzer import run_comprehensive_data_quality_analysis
from reports.report_builder import build_bias_fairness_report, build_accuracy_report, build_robustness_report, build_consistency_report, build_transparency_report, build_comprehensive_data_quality_report
from utils.response_collector import reset_collector
import config

app = Flask(__name__)

# Configure Flask app for production if deployed
if os.environ.get('FLASK_ENV') == 'production':
    app.config.from_object('config_prod.Config')
else:
    app.config['SECRET_KEY'] = 'dev-secret-key'

# Global variables to track analysis progress
analysis_status = {
    "running": False,
    "completed": False,
    "error": None,
    "progress": 0,
    "message": "Ready to start analysis"
}

def archive_existing_reports():
    """Archive existing reports to timestamped archive directory"""
    import os
    import shutil
    from datetime import datetime
    
    reports_dir = "reports/generated"
    archive_base_dir = "reports/archive"
    
    # Check if there are any reports to archive
    if not os.path.exists(reports_dir):
        return []
    
    # Get list of existing reports
    report_files = []
    for file in os.listdir(reports_dir):
        if file.endswith('.html'):
            report_files.append(file)
    
    if not report_files:
        return []
    
    # Create timestamped archive directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = os.path.join(archive_base_dir, f"archive_{timestamp}")
    os.makedirs(archive_dir, exist_ok=True)
    
    # Move reports to archive
    archived_files = []
    for report_file in report_files:
        src_path = os.path.join(reports_dir, report_file)
        dst_path = os.path.join(archive_dir, report_file)
        try:
            shutil.move(src_path, dst_path)
            archived_files.append(report_file)
        except Exception as e:
            print(f"Warning: Could not archive {report_file}: {e}")
    
    if archived_files:
        print(f"📁 Archived {len(archived_files)} reports to {archive_dir}")
    
    return archived_files

def clear_analysis_cache(cache_options):
    """Clear cached response files based on user selections"""
    import os
    import glob
    
    # Archive existing reports before clearing cache
    archived_files = archive_existing_reports()
    
    cache_files = {
        "clear_bias_cache": "results/responses/bias_fairness.jsonl",
        "clear_consistency_cache": "results/responses/consistency.jsonl", 
        "clear_robustness_cache": "results/responses/robustness.jsonl",
        "clear_transparency_cache": "results/responses/transparency.jsonl",
        "clear_data_quality_cache": "results/responses/all_responses.jsonl"
    }
    
    cleared_files = []
    
    # Clear all cache if requested
    if cache_options.get("clear_all_cache", False):
        cache_dir = "results/responses"
        if os.path.exists(cache_dir):
            jsonl_files = glob.glob(os.path.join(cache_dir, "*.jsonl"))
            for file in jsonl_files:
                try:
                    os.remove(file)
                    cleared_files.append(os.path.basename(file))
                except OSError:
                    pass
        return {"cleared_files": cleared_files, "archived_files": archived_files}
    
    # Clear specific caches
    for option, file_path in cache_files.items():
        if cache_options.get(option, False) and os.path.exists(file_path):
            try:
                os.remove(file_path)
                cleared_files.append(os.path.basename(file_path))
            except OSError:
                pass
    
    return {"cleared_files": cleared_files, "archived_files": archived_files}

def run_analysis_background(form_data):
    """Run the analysis in the background and update status"""
    global analysis_status
    
    try:
        # Reset response collector at the start of new analysis session
        reset_collector()
        
        # Clear cached data if requested
        cache_result = clear_analysis_cache(form_data)
        
        # Handle the response based on whether it's the old format (list) or new format (dict)
        if isinstance(cache_result, dict):
            cleared_files = cache_result.get("cleared_files", [])
            archived_files = cache_result.get("archived_files", [])
        else:
            # Backward compatibility with old format
            cleared_files = cache_result
            archived_files = []
        
        # Create status message
        message_parts = []
        if archived_files:
            message_parts.append(f"Archived {len(archived_files)} reports")
        if cleared_files:
            message_parts.append(f"Cleared cache files: {', '.join(cleared_files)}")
        
        if message_parts:
            analysis_status["message"] = " | ".join(message_parts)
            time.sleep(2)  # Brief pause to show the message
        
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
        total_analyses = sum([form_data["run_bias"], form_data["run_accuracy"], form_data["run_robustness"], form_data["run_consistency"], form_data["run_transparency"], form_data["run_data_quality"]])
        
        # Define realistic progress ranges based on actual analysis time
        # These percentages reflect the relative time each analysis takes
        progress_ranges = {
            "bias_fairness": (10, 55),      # 45% of total time (many API calls)
            "robustness": (55, 72),         # 17% of total time (200+ API calls) 
            "transparency": (72, 83),       # 11% of total time (LIME + analysis)
            "consistency": (83, 89),        # 6% of total time (~30 API calls)
            "accuracy": (89, 94),           # 5% of total time (mostly data analysis)
            "data_quality": (94, 98)        # 4% of total time (analysis only)
        }
        
        current_analysis = 0
        
        # Run bias analysis if selected
        if form_data["run_bias"]:
            current_analysis += 1
            start_progress, end_progress = progress_ranges["bias_fairness"]
            analysis_status["progress"] = start_progress
            analysis_status["message"] = f"Running bias analysis ({current_analysis}/{total_analyses})..."
            
            # Pass status reference to bias analysis with progress range
            from analysis.bias_fairness import set_status_reference
            set_status_reference(analysis_status, start_progress, end_progress - start_progress)
            
            bias_results = run_bias_analysis()
            results["bias_fairness"] = bias_results
            
            # Build bias report
            analysis_status["progress"] = end_progress - 2
            analysis_status["message"] = f"Building bias fairness report..."
            build_bias_fairness_report(bias_results)
        
        # Run accuracy analysis if selected
        if form_data["run_accuracy"]:
            current_analysis += 1
            start_progress, end_progress = progress_ranges["accuracy"]
            analysis_status["progress"] = start_progress
            analysis_status["message"] = f"Running accuracy analysis ({current_analysis}/{total_analyses})..."
            
            # Pass status reference to accuracy analysis
            from analysis.accuracy import set_status_reference
            set_status_reference(analysis_status)
            
            accuracy_results = run_accuracy_analysis()
            results["accuracy"] = accuracy_results
            
            # Build accuracy report
            analysis_status["progress"] = end_progress - 1
            analysis_status["message"] = f"Building accuracy report..."
            build_accuracy_report(accuracy_results)
        
        # Run robustness analysis if selected
        if form_data["run_robustness"]:
            current_analysis += 1
            start_progress, end_progress = progress_ranges["robustness"]
            analysis_status["progress"] = start_progress
            analysis_status["message"] = f"Running robustness analysis ({current_analysis}/{total_analyses})..."
            
            # Pass status reference to robustness analysis
            from analysis.robustness import set_status_reference
            set_status_reference(analysis_status)
            
            robustness_results = run_robustness_analysis()
            results["robustness"] = robustness_results
            
            # Build robustness report
            analysis_status["progress"] = end_progress - 1
            analysis_status["message"] = f"Building robustness report..."
            build_robustness_report(robustness_results)
        
        # Run consistency analysis if selected
        if form_data["run_consistency"]:
            current_analysis += 1
            start_progress, end_progress = progress_ranges["consistency"]
            analysis_status["progress"] = start_progress
            analysis_status["message"] = f"Running consistency analysis ({current_analysis}/{total_analyses})..."
            
            # Pass status reference to consistency analysis
            from analysis.consistency import set_status_reference
            set_status_reference(analysis_status)
            
            consistency_results = run_consistency_analysis()
            results["consistency"] = consistency_results
            
            # Build consistency report
            analysis_status["progress"] = end_progress - 1
            analysis_status["message"] = f"Building consistency report..."
            build_consistency_report(consistency_results)
        
        # Run transparency analysis if selected
        if form_data["run_transparency"]:
            current_analysis += 1
            start_progress, end_progress = progress_ranges["transparency"]
            analysis_status["progress"] = start_progress
            analysis_status["message"] = f"Running transparency analysis ({current_analysis}/{total_analyses})..."
            
            # Pass status reference to transparency analysis
            from analysis.transparency import set_status_reference
            set_status_reference(analysis_status, start_progress, end_progress - start_progress)
            
            transparency_results = run_transparency_analysis()
            results["transparency"] = transparency_results
            
            # Build transparency report
            analysis_status["progress"] = end_progress - 1
            analysis_status["message"] = f"Building transparency report..."
            build_transparency_report(transparency_results)
        
        # Run comprehensive data quality analysis on all collected responses (if selected)
        if form_data["run_data_quality"]:
            start_progress, end_progress = progress_ranges["data_quality"]
            analysis_status["progress"] = start_progress
            analysis_status["message"] = "Running comprehensive data quality analysis..."
            
            from analysis.data_quality_analyzer import set_status_reference as set_dq_status_reference
            set_dq_status_reference(analysis_status)
            
            data_quality_results = run_comprehensive_data_quality_analysis()
            results["comprehensive_data_quality"] = data_quality_results
            
            # Build comprehensive data quality report
            analysis_status["progress"] = end_progress - 1
            analysis_status["message"] = "Building comprehensive data quality report..."
            build_comprehensive_data_quality_report(data_quality_results)
            
            total_responses = data_quality_results['total_responses_analyzed']
        else:
            # Count responses from other analyses if data quality wasn't run
            total_responses = sum(len(results.get(key, {}).get('responses', [])) for key in results.keys())
        
        analysis_status["progress"] = 100
        analysis_status["message"] = f"All analyses completed! Processed {total_responses} total API responses."
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
        "run_transparency": False,
        "run_data_quality": False,
        "model": "gpt-3.5-turbo-0125",
        # Cache management defaults
        "clear_bias_cache": False,
        "clear_consistency_cache": False,
        "clear_robustness_cache": False,
        "clear_transparency_cache": False,
        "clear_data_quality_cache": False,
        "clear_all_cache": False
    }
    return render_template("index.html", form_data=form_data)


@app.route("/health")
def health_check():
    """Health check endpoint for Render deployment monitoring"""
    return jsonify({
        "status": "healthy",
        "service": "credit-scoring-validator",
        "version": "1.0.0"
    })


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
        "run_transparency": request.form.get("run_transparency") == "on",
        "run_data_quality": request.form.get("run_data_quality") == "on",
        "model": request.form.get("model", "gpt-3.5-turbo-0125"),
        # Cache management options
        "clear_bias_cache": request.form.get("clear_bias_cache") == "on",
        "clear_consistency_cache": request.form.get("clear_consistency_cache") == "on",
        "clear_robustness_cache": request.form.get("clear_robustness_cache") == "on",
        "clear_transparency_cache": request.form.get("clear_transparency_cache") == "on",
        "clear_data_quality_cache": request.form.get("clear_data_quality_cache") == "on",
        "clear_all_cache": request.form.get("clear_all_cache") == "on"
    }
    
    # Validate that at least one analysis is selected
    if not (form_data["run_bias"] or form_data["run_accuracy"] or form_data["run_robustness"] or form_data["run_consistency"] or form_data["run_transparency"] or form_data["run_data_quality"]):
        return jsonify({"error": "Please select at least one analysis to run."}), 400
    
    # Validate required fields for analyses that need API calls
    if (form_data["run_bias"] or form_data["run_robustness"] or form_data["run_consistency"] or form_data["run_transparency"]) and not all([form_data["api_url"], form_data["username"], form_data["password"]]):
        return jsonify({"error": "Please fill in all API configuration fields for bias/robustness/consistency/transparency analysis."}), 400
    
    # For accuracy analysis, we can run it on existing data even without API credentials
    if form_data["run_bias"] or form_data["run_accuracy"] or form_data["run_robustness"] or form_data["run_consistency"] or form_data["run_transparency"]:
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


@app.route("/transparency_report")
def view_transparency_report():
    report_file = "reports/generated/transparency_report.html"
    if not os.path.exists(report_file):
        return "Transparency report not found. Please run the transparency analysis first.", 404
    return send_from_directory("reports/generated", "transparency_report.html")


@app.route("/data_quality_report")
def view_data_quality_report():
    report_file = "reports/generated/comprehensive_data_quality_report.html"
    if not os.path.exists(report_file):
        return "Data quality report not found. Please run the data quality analysis first.", 404
    return send_from_directory("reports/generated", "comprehensive_data_quality_report.html")


@app.route("/generate_test_data", methods=["POST"])
def generate_test_data():
    """Generate test data and save to CSV"""
    try:
        # Get the record count from the request
        data = request.get_json() if request.is_json else {}
        num_records = data.get('record_count', 30)  # Default to 30 if not specified
        
        # Validate the record count
        if not isinstance(num_records, int) or num_records < 1 or num_records > 10000:
            return jsonify({
                'success': False,
                'error': 'Record count must be an integer between 1 and 10,000'
            }), 400
        
        # Import the test data generator functions
        from generator.testdata_generator import generate_test_data as gen_test_data
        import pandas as pd
        
        # Define nationality distribution (copied from the generator file)
        nationality_distribution = {
            'DE': 0.7,  # 70% German
            # EU countries (15%)
            'TR': 0.04, # Turkey (largest immigrant group in Germany)
            'PL': 0.03, # Poland
            'IT': 0.02, # Italy
            'RO': 0.02, # Romania
            'GR': 0.01, # Greece
            'HR': 0.01, # Croatia
            'BG': 0.01, # Bulgaria
            'ES': 0.01, # Spain
            'FR': 0.01, # France
            # Non-EU countries (15%)
            'SY': 0.03, # Syria (large refugee population)
            'RU': 0.02, # Russia
            'UA': 0.02, # Ukraine
            'US': 0.01, # United States
            'CN': 0.01, # China
            'IN': 0.01, # India
            'VN': 0.01, # Vietnam
            'IR': 0.01, # Iran
            'AF': 0.01, # Afghanistan
            'NG': 0.01, # Nigeria
        }
        
        # Generate test data with the specified number of records
        test_data = gen_test_data(
            num_records=num_records, 
            locales=['de_DE'], 
            nationality_distribution=nationality_distribution
        )
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(test_data)
        output_path = 'data/testdata.csv'
        
        # Ensure the data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Save the DataFrame
        df.to_csv(output_path, index=False)
        
        return jsonify({
            'success': True,
            'message': 'Test data generated successfully',
            'records_count': len(test_data),
            'file_path': output_path
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/archives")
def get_archives():
    """Get list of archived reports"""
    import os
    from datetime import datetime
    
    try:
        archive_base_dir = "reports/archive"
        archives = []
        
        if not os.path.exists(archive_base_dir):
            return jsonify({"archives": []})
        
        # Get all archive directories
        archive_dirs = []
        for item in os.listdir(archive_base_dir):
            item_path = os.path.join(archive_base_dir, item)
            if os.path.isdir(item_path) and item.startswith('archive_'):
                archive_dirs.append(item)
        
        # Sort by creation time (newest first)
        archive_dirs.sort(reverse=True)
        
        for archive_dir in archive_dirs:
            archive_path = os.path.join(archive_base_dir, archive_dir)
            
            # Extract timestamp from directory name
            timestamp_str = archive_dir.replace('archive_', '')
            try:
                # Parse timestamp: YYYYMMDD_HHMMSS
                timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                formatted_date = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                formatted_date = timestamp_str
            
            # Get list of reports in this archive
            reports = []
            for file in os.listdir(archive_path):
                if file.endswith('.html'):
                    file_path = os.path.join(archive_path, file)
                    file_size = os.path.getsize(file_path)
                    
                    # Format file size
                    if file_size < 1024:
                        size_str = f"{file_size} B"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"
                    
                    reports.append({
                        "name": file,
                        "size": size_str,
                        "bytes": file_size
                    })
            
            # Sort reports by name for consistent display
            reports.sort(key=lambda x: x['name'])
            
            if reports:  # Only include archives that have reports
                archives.append({
                    "name": archive_dir,
                    "date": formatted_date,
                    "timestamp": timestamp_str,
                    "reports": reports,
                    "total_size": sum(r['bytes'] for r in reports)
                })
        
        return jsonify({"archives": archives})
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to load archives: {str(e)}",
            "archives": []
        }), 500


@app.route("/api/archive/<archive_name>/<report_name>")
def get_archived_report(archive_name, report_name):
    """Serve an archived report file"""
    import os
    from flask import abort
    
    try:
        # Validate archive and report names to prevent directory traversal
        if '..' in archive_name or '..' in report_name:
            abort(400)
        
        # Check if archive exists
        archive_path = os.path.join("reports/archive", archive_name)
        if not os.path.exists(archive_path) or not os.path.isdir(archive_path):
            abort(404)
        
        # Check if report exists
        report_path = os.path.join(archive_path, report_name)
        if not os.path.exists(report_path) or not report_name.endswith('.html'):
            abort(404)
        
        # Serve the file
        return send_from_directory(archive_path, report_name)
        
    except Exception as e:
        abort(500)


if __name__ == "__main__":
    # For local development only
    # In production, gunicorn will run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
