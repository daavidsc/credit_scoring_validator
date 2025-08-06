# reports/report_builder.py

import json
import os
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = "reports/templates"
OUTPUT_DIR = "reports/generated"

def load_analysis_results(path):
    with open(path, "r") as f:
        return json.load(f)

def build_bias_fairness_report(data, output_filename="bias_report.html"):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("report_template.html")

    rendered = template.render(results=data)

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, "w") as f:
        f.write(rendered)

    print(f"✅ Report saved to {output_path}")
