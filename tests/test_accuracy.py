# tests/test_accuracy.py

import sys
import os
import json
import tempfile
import pytest
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.accuracy import (
    run_accuracy_analysis,
    extract_predictions_and_ground_truth,
    calculate_ground_truth,
    calculate_regression_metrics,
    calculate_classification_metrics,
    calculate_confusion_matrix,
    analyze_score_distribution,
    load_jsonl
)


class TestAccuracyAnalysis:
    """Test suite for accuracy analysis functionality"""
    
    def test_calculate_ground_truth_high_score(self):
        """Test ground truth calculation for a high-quality profile"""
        input_data = {
            "income": 120000,  # High income (+20)
            "employment_duration_years": 15,  # Long employment (+15)
            "payment_defaults": 0,  # No defaults (0)
            "credit_limit": 50000,
            "used_credit": 10000,  # Low utilization (+10)
            "credit_inquiries_last_6_months": 0,  # No inquiries (0)
            "housing_status": "owner",  # Homeowner (+5)
            "address_stability_years": 15,  # Stable address (+5)
            "existing_loans": 1  # Few loans (0)
        }
        
        score, classification = calculate_ground_truth(input_data)
        
        # Expected: 50 (base) + 20 + 15 + 10 + 5 + 5 = 105, capped at 100
        assert score >= 85, f"Expected high score, got {score}"
        assert classification == "Good", f"Expected 'Good' classification, got {classification}"
    
    def test_calculate_ground_truth_low_score(self):
        """Test ground truth calculation for a low-quality profile"""
        input_data = {
            "income": 25000,  # Low income (+5)
            "employment_duration_years": 0.5,  # Short employment (0)
            "payment_defaults": 3,  # Multiple defaults (-45)
            "credit_limit": 10000,
            "used_credit": 9500,  # High utilization (-10)
            "credit_inquiries_last_6_months": 5,  # Many inquiries (-10)
            "housing_status": "renter",  # Renter (0)
            "address_stability_years": 1,  # Unstable address (0)
            "existing_loans": 5  # Many loans (-5)
        }
        
        score, classification = calculate_ground_truth(input_data)
        
        # Expected: 50 + 5 - 45 - 10 - 10 - 5 = -15, floored at 0
        assert score <= 20, f"Expected low score, got {score}"
        assert classification == "Poor", f"Expected 'Poor' classification, got {classification}"
    
    def test_calculate_ground_truth_average_score(self):
        """Test ground truth calculation for an average profile"""
        input_data = {
            "income": 55000,  # Medium income (+10)
            "employment_duration_years": 7,  # Medium employment (+10)
            "payment_defaults": 1,  # One default (-15)
            "credit_limit": 30000,
            "used_credit": 18000,  # Medium utilization (+5)
            "credit_inquiries_last_6_months": 2,  # Some inquiries (-4)
            "housing_status": "renter",  # Renter (0)
            "address_stability_years": 8,  # Medium stability (+3)
            "existing_loans": 2  # Few loans (0)
        }
        
        score, classification = calculate_ground_truth(input_data)
        
        # Expected: 50 + 10 + 10 - 15 + 5 - 4 + 3 = 59
        assert 45 <= score <= 75, f"Expected average score (45-75), got {score}"
        assert classification in ["Average", "Good"], f"Expected 'Average' or 'Good' classification, got {classification}"
    
    def test_extract_predictions_and_ground_truth_valid(self):
        """Test extraction of predictions from valid responses"""
        responses = [
            {
                "input": {
                    "income": 50000,
                    "employment_duration_years": 5,
                    "payment_defaults": 0,
                    "credit_limit": 20000,
                    "used_credit": 8000,
                    "credit_inquiries_last_6_months": 1,
                    "housing_status": "owner",
                    "address_stability_years": 10,
                    "existing_loans": 1
                },
                "output": {
                    "parsed": {
                        "credit_score": "75",
                        "classification": "Good"
                    }
                }
            },
            {
                "input": {
                    "income": 30000,
                    "employment_duration_years": 2,
                    "payment_defaults": 2,
                    "credit_limit": 15000,
                    "used_credit": 12000,
                    "credit_inquiries_last_6_months": 3,
                    "housing_status": "renter",
                    "address_stability_years": 3,
                    "existing_loans": 3
                },
                "output": {
                    "parsed": {
                        "credit_score": "35",
                        "classification": "Poor"
                    }
                }
            }
        ]
        
        pred_scores, pred_classes, true_scores, true_classes = extract_predictions_and_ground_truth(responses)
        
        assert len(pred_scores) == 2
        assert len(pred_classes) == 2
        assert len(true_scores) == 2
        assert len(true_classes) == 2
        
        assert pred_scores[0] == 75.0
        assert pred_classes[0] == "Good"
        assert pred_scores[1] == 35.0
        assert pred_classes[1] == "Poor"
        
        # Ground truth should be calculated correctly
        assert isinstance(true_scores[0], float)
        assert true_classes[0] in ["Poor", "Average", "Good"]
    
    def test_extract_predictions_and_ground_truth_with_errors(self):
        """Test extraction handles error responses correctly"""
        responses = [
            {
                "input": {"income": 50000},
                "error": "API error"
            },
            {
                "input": {"income": 40000},
                "output": {
                    "parsed": {
                        "credit_score": "invalid_score",
                        "classification": "Good"
                    }
                }
            },
            {
                "input": {"income": 60000, "employment_duration_years": 5, "payment_defaults": 0},
                "output": {
                    "parsed": {
                        "credit_score": "80",
                        "classification": "Good"
                    }
                }
            }
        ]
        
        pred_scores, pred_classes, true_scores, true_classes = extract_predictions_and_ground_truth(responses)
        
        # Should only extract the valid response
        assert len(pred_scores) == 1
        assert pred_scores[0] == 80.0
        assert pred_classes[0] == "Good"
    
    def test_calculate_regression_metrics(self):
        """Test regression metrics calculation"""
        predicted_scores = [75.0, 60.0, 45.0, 85.0]
        true_scores = [80.0, 55.0, 50.0, 90.0]
        
        metrics = calculate_regression_metrics(predicted_scores, true_scores)
        
        assert "mae" in metrics
        assert "mse" in metrics
        assert "rmse" in metrics
        assert "mape" in metrics
        assert "r2" in metrics
        assert "correlation" in metrics
        
        # MAE should be reasonable
        assert 0 <= metrics["mae"] <= 20
        assert metrics["rmse"] >= metrics["mae"]  # RMSE >= MAE
        assert -1 <= metrics["correlation"] <= 1  # Correlation in valid range
    
    def test_calculate_regression_metrics_empty(self):
        """Test regression metrics with empty inputs"""
        metrics = calculate_regression_metrics([], [])
        assert metrics == {}
        
        # Mismatched lengths
        metrics = calculate_regression_metrics([75.0], [80.0, 85.0])
        assert metrics == {}
    
    def test_calculate_classification_metrics(self):
        """Test classification metrics calculation"""
        predicted_classes = ["Good", "Average", "Poor", "Good", "Average"]
        true_classes = ["Good", "Good", "Poor", "Average", "Average"]
        
        metrics = calculate_classification_metrics(predicted_classes, true_classes)
        
        assert "accuracy" in metrics
        assert "macro_avg" in metrics
        assert "weighted_avg" in metrics
        assert "class_metrics" in metrics
        assert "confusion_matrix" in metrics
        
        # Accuracy should be between 0 and 1
        assert 0 <= metrics["accuracy"] <= 1
        
        # Check class-specific metrics
        for class_name in ["Poor", "Average", "Good"]:
            assert class_name in metrics["class_metrics"]
            class_metrics = metrics["class_metrics"][class_name]
            assert "precision" in class_metrics
            assert "recall" in class_metrics
            assert "f1_score" in class_metrics
            assert "support" in class_metrics
            
            # Metrics should be in valid ranges
            assert 0 <= class_metrics["precision"] <= 1
            assert 0 <= class_metrics["recall"] <= 1
            assert 0 <= class_metrics["f1_score"] <= 1
    
    def test_confusion_matrix(self):
        """Test confusion matrix calculation"""
        pred_array = np.array(["Good", "Average", "Poor"])
        true_array = np.array(["Good", "Good", "Poor"])
        classes = ["Poor", "Average", "Good"]
        
        cm = calculate_confusion_matrix(pred_array, true_array, classes)
        
        assert "Poor" in cm
        assert "Average" in cm
        assert "Good" in cm
        
        # Check diagonal elements (correct predictions)
        assert cm["Poor"]["Poor"] == 1  # Correctly predicted Poor
        assert cm["Good"]["Good"] == 1  # Correctly predicted Good
        
        # Check off-diagonal elements (incorrect predictions)
        assert cm["Good"]["Average"] == 1  # True Good predicted as Average
    
    def test_analyze_score_distribution(self):
        """Test score distribution analysis"""
        predicted_scores = [25.0, 45.0, 65.0, 85.0, 95.0]
        true_scores = [30.0, 40.0, 70.0, 80.0, 90.0]
        
        distribution = analyze_score_distribution(predicted_scores, true_scores)
        
        assert "predicted_stats" in distribution
        assert "true_stats" in distribution
        assert "range_analysis" in distribution
        
        pred_stats = distribution["predicted_stats"]
        assert "mean" in pred_stats
        assert "std" in pred_stats
        assert "min" in pred_stats
        assert "max" in pred_stats
        assert "median" in pred_stats
        
        # Check range analysis
        range_analysis = distribution["range_analysis"]
        expected_ranges = ["0-30", "30-50", "50-70", "70-100"]
        for range_name in expected_ranges:
            assert range_name in range_analysis
            assert "predicted_count" in range_analysis[range_name]
            assert "true_count" in range_analysis[range_name]
            assert "predicted_percentage" in range_analysis[range_name]
            assert "true_percentage" in range_analysis[range_name]
    
    def test_analyze_score_distribution_empty(self):
        """Test score distribution with empty inputs"""
        distribution = analyze_score_distribution([], [])
        assert distribution == {}
    
    def test_load_jsonl_valid_file(self):
        """Test loading a valid JSONL file"""
        test_data = [
            {"input": {"name": "John"}, "output": {"score": 75}},
            {"input": {"name": "Jane"}, "output": {"score": 85}}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for item in test_data:
                f.write(json.dumps(item) + '\n')
            temp_path = f.name
        
        try:
            loaded_data = load_jsonl(temp_path)
            assert len(loaded_data) == 2
            assert loaded_data[0]["input"]["name"] == "John"
            assert loaded_data[1]["output"]["score"] == 85
        finally:
            os.unlink(temp_path)
    
    def test_run_accuracy_analysis_integration(self):
        """Integration test for the full accuracy analysis"""
        # Create test JSONL data
        test_responses = [
            {
                "input": {
                    "name": "Alice",
                    "income": 75000,
                    "employment_duration_years": 8,
                    "payment_defaults": 0,
                    "credit_limit": 25000,
                    "used_credit": 12000,
                    "credit_inquiries_last_6_months": 1,
                    "housing_status": "owner",
                    "address_stability_years": 12,
                    "existing_loans": 2
                },
                "output": {
                    "parsed": {
                        "credit_score": "78",
                        "classification": "Good"
                    }
                }
            },
            {
                "input": {
                    "name": "Bob",
                    "income": 40000,
                    "employment_duration_years": 3,
                    "payment_defaults": 1,
                    "credit_limit": 15000,
                    "used_credit": 10000,
                    "credit_inquiries_last_6_months": 2,
                    "housing_status": "renter",
                    "address_stability_years": 4,
                    "existing_loans": 1
                },
                "output": {
                    "parsed": {
                        "credit_score": "55",
                        "classification": "Average"
                    }
                }
            },
            {
                "input": {"name": "Charlie"},
                "error": "API timeout"
            }
        ]
        
        # Write test data to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for item in test_responses:
                f.write(json.dumps(item) + '\n')
            temp_path = f.name
        
        try:
            # Run analysis
            results = run_accuracy_analysis(temp_path)
            
            # Check structure
            assert "summary" in results
            assert "regression_metrics" in results
            assert "classification_metrics" in results
            assert "distribution_analysis" in results
            
            # Check summary
            summary = results["summary"]
            assert summary["total_predictions"] == 2  # Only 2 valid predictions
            assert summary["total_responses"] == 3
            assert summary["valid_prediction_rate"] == 2/3
            
            # Check regression metrics exist and are reasonable
            reg_metrics = results["regression_metrics"]
            assert "mae" in reg_metrics
            assert "rmse" in reg_metrics
            assert "r2" in reg_metrics
            
            # Check classification metrics
            class_metrics = results["classification_metrics"]
            assert "accuracy" in class_metrics
            assert "class_metrics" in class_metrics
            assert 0 <= class_metrics["accuracy"] <= 1
            
        finally:
            os.unlink(temp_path)
    
    def test_run_accuracy_analysis_file_not_found(self):
        """Test accuracy analysis with non-existent file"""
        results = run_accuracy_analysis("non_existent_file.jsonl")
        assert "error" in results
        assert "not found" in results["error"].lower()
    
    def test_run_accuracy_analysis_no_valid_predictions(self):
        """Test accuracy analysis with no valid predictions"""
        test_responses = [
            {"input": {"name": "Alice"}, "error": "API error"},
            {"input": {"name": "Bob"}, "error_type": "timeout"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for item in test_responses:
                f.write(json.dumps(item) + '\n')
            temp_path = f.name
        
        try:
            results = run_accuracy_analysis(temp_path)
            assert "error" in results
            assert "No valid predictions" in results["error"]
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__])
