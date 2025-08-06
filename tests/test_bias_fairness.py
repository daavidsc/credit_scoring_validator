# tests/test_bias_fairness.py

import pytest
from analysis.bias_fairness import run_bias_analysis, PROTECTED_ATTRIBUTES

def test_bias_analysis_structure():
    results = run_bias_analysis()

    # Check top-level structure
    assert isinstance(results, dict)
    assert len(results) > 0

    for attr in PROTECTED_ATTRIBUTES:
        assert attr in results
        attr_result = results[attr]

        # Check required keys
        assert "demographic_parity" in attr_result
        assert "disparate_impact_ratio" in attr_result

        # Check demographic parity structure
        dp = attr_result["demographic_parity"]
        assert isinstance(dp, dict)
        for group, stats in dp.items():
            assert "total" in stats
            assert "positive" in stats
            assert isinstance(stats["total"], int)
            assert isinstance(stats["positive"], int)

        # Check disparate impact ratio is float
        dir_value = attr_result["disparate_impact_ratio"]
        assert isinstance(dir_value, float)

    print("✅ Bias analysis test passed.")
