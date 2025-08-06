# tests/test_bias_fairness.py

import pytest
import json
import os
from analysis.bias_fairness import run_bias_analysis, load_jsonl, PROTECTED_ATTRIBUTES

RESPONSES_PATH = "results/responses/bias_fairness.jsonl"
LOG_PATH = "results/logs/api_calls.log"

def test_bias_analysis_structure():
    results = run_bias_analysis()

    # Check top-level structure
    assert isinstance(results, dict)
    assert len(results) > 0

    for attr in PROTECTED_ATTRIBUTES:
        assert attr in results
        attr_result = results[attr]

        assert "demographic_parity" in attr_result
        assert "disparate_impact_ratio" in attr_result

        dp = attr_result["demographic_parity"]
        assert isinstance(dp, dict)
        for group, stats in dp.items():
            assert "total" in stats
            assert "positive" in stats
            assert isinstance(stats["total"], int)
            assert isinstance(stats["positive"], int)

        dir_value = attr_result["disparate_impact_ratio"]
        assert isinstance(dir_value, float)

    print("✅ Bias analysis structure test passed.")

def test_log_api_requests_and_responses_to_file():
    responses = load_jsonl(RESPONSES_PATH)
    assert len(responses) > 0, "No responses loaded from JSONL file."

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    with open(LOG_PATH, "w") as f:
        f.write(f"📄 Logged {len(responses)} API calls\n\n")

        for i, entry in enumerate(responses):
            f.write(f"\n🔹 API Call #{i+1}\n")
            f.write("Input:\n")
            f.write(json.dumps(entry["input"], indent=2))
            f.write("\nOutput:\n")
            f.write(json.dumps(entry["output"], indent=2))
            f.write("\n" + "-"*80 + "\n")

    print(f"✅ API calls logged to {LOG_PATH}")
