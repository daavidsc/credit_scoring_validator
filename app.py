# app.py

from flask import Flask, request, render_template
import json

from analysis.bias_fairness import run_bias_analysis
import config

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    results = None

    if request.method == "POST":
        # Get form inputs
        api_url = request.form.get("api_url")
        username = request.form.get("username")
        password = request.form.get("password")
        selected_analyses = request.form.getlist("analysis")

        # Inject into config (or set globally if preferred)
        config.API_URL = api_url
        config.API_USERNAME = username
        config.API_PASSWORD = password

        # Run selected analyses
        if "bias_fairness" in selected_analyses:
            results = run_bias_analysis()

    return render_template("index.html", results=json.dumps(results, indent=2) if results else None)


if __name__ == "__main__":
    app.run(debug=True)
