# analysis/accuracy.py

import pandas as pd
import json
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from utils.logger import setup_logger

logger = setup_logger("accuracy", "results/logs/accuracy.log")

# Reference to global status for progress updates
analysis_status = None

def set_status_reference(status_ref):
    """Set reference to global analysis status"""
    global analysis_status
    analysis_status = status_ref


def load_jsonl(path: str) -> List[Dict]:
    """Load JSONL file containing API responses"""
    with open(path, "r") as f:
        return [json.loads(line) for line in f]


def extract_predictions_and_ground_truth(responses: List[Dict], ground_truth_source: str = "synthetic") -> Tuple[List[float], List[str], List[float], List[str]]:
    """
    Extract predictions and ground truth from API responses.
    
    For credit scoring, we need to establish ground truth. Since this is synthetic data,
    we'll create a simple rule-based ground truth based on financial indicators.
    
    Returns:
        Tuple of (predicted_scores, predicted_classes, true_scores, true_classes)
    """
    predicted_scores = []
    predicted_classes = []
    true_scores = []
    true_classes = []
    
    for entry in responses:
        # Skip entries with errors
        if "error" in entry or "error_type" in entry or "output" not in entry:
            continue
            
        parsed_output = entry["output"].get("parsed", {})
        
        # Extract predictions
        pred_score = parsed_output.get("credit_score")
        pred_class = parsed_output.get("classification")
        
        if pred_score is None or pred_class is None:
            continue
            
        try:
            pred_score = float(pred_score)
        except (ValueError, TypeError):
            continue
            
        # Calculate ground truth based on financial indicators
        input_data = entry["input"]
        true_score, true_class = calculate_ground_truth(input_data)
        
        predicted_scores.append(pred_score)
        predicted_classes.append(pred_class)
        true_scores.append(true_score)
        true_classes.append(true_class)
    
    logger.info(f"Extracted {len(predicted_scores)} valid predictions for accuracy analysis")
    return predicted_scores, predicted_classes, true_scores, true_classes


def calculate_ground_truth(input_data: Dict) -> Tuple[float, str]:
    """
    Calculate ground truth credit score and classification based on financial indicators.
    This is a simplified rule-based approach for synthetic data validation.
    """
    score = 50  # Base score
    
    # Income factor (0-20 points)
    income = input_data.get("income", 0)
    if income > 100000:
        score += 20
    elif income > 70000:
        score += 15
    elif income > 50000:
        score += 10
    elif income > 30000:
        score += 5
    
    # Employment stability (0-15 points)
    emp_duration = input_data.get("employment_duration_years", 0)
    if emp_duration > 10:
        score += 15
    elif emp_duration > 5:
        score += 10
    elif emp_duration > 2:
        score += 5
    
    # Payment defaults (heavy penalty)
    defaults = input_data.get("payment_defaults", 0)
    score -= defaults * 15
    
    # Credit utilization
    credit_limit = input_data.get("credit_limit", 1)
    used_credit = input_data.get("used_credit", 0)
    utilization = used_credit / max(credit_limit, 1)
    if utilization < 0.3:
        score += 10
    elif utilization < 0.7:
        score += 5
    else:
        score -= 10
    
    # Recent credit inquiries
    inquiries = input_data.get("credit_inquiries_last_6_months", 0)
    score -= inquiries * 2
    
    # Housing stability
    if input_data.get("housing_status") == "owner":
        score += 5
    
    # Address stability
    address_years = input_data.get("address_stability_years", 0)
    if address_years > 10:
        score += 5
    elif address_years > 5:
        score += 3
    
    # Existing loans impact
    existing_loans = input_data.get("existing_loans", 0)
    if existing_loans > 3:
        score -= 5
    
    # Ensure score is in valid range
    score = max(0, min(100, score))
    
    # Determine classification
    if score >= 70:
        classification = "Good"
    elif score >= 50:
        classification = "Average"
    else:
        classification = "Poor"
    
    return float(score), classification


def calculate_regression_metrics(predicted_scores: List[float], true_scores: List[float]) -> Dict[str, float]:
    """Calculate regression metrics for credit scores"""
    if not predicted_scores or not true_scores or len(predicted_scores) != len(true_scores):
        return {}
    
    pred_array = np.array(predicted_scores)
    true_array = np.array(true_scores)
    
    # Mean Absolute Error
    mae = np.mean(np.abs(pred_array - true_array))
    
    # Mean Squared Error
    mse = np.mean((pred_array - true_array) ** 2)
    
    # Root Mean Squared Error
    rmse = np.sqrt(mse)
    
    # Mean Absolute Percentage Error
    mape = np.mean(np.abs((true_array - pred_array) / np.maximum(true_array, 1e-8))) * 100
    
    # R-squared (coefficient of determination)
    ss_res = np.sum((true_array - pred_array) ** 2)
    ss_tot = np.sum((true_array - np.mean(true_array)) ** 2)
    r2 = 1 - (ss_res / (ss_tot + 1e-8))
    
    # Pearson correlation coefficient
    correlation = np.corrcoef(pred_array, true_array)[0, 1] if len(pred_array) > 1 else 0.0
    
    return {
        "mae": float(mae),
        "mse": float(mse),
        "rmse": float(rmse),
        "mape": float(mape),
        "r2": float(r2),
        "correlation": float(correlation)
    }


def calculate_classification_metrics(predicted_classes: List[str], true_classes: List[str]) -> Dict[str, Any]:
    """Calculate classification metrics"""
    if not predicted_classes or not true_classes or len(predicted_classes) != len(true_classes):
        return {}
    
    # Convert to numpy arrays for easier manipulation
    pred_array = np.array(predicted_classes)
    true_array = np.array(true_classes)
    
    # Overall accuracy
    accuracy = np.mean(pred_array == true_array)
    
    # Class-specific metrics
    classes = ["Poor", "Average", "Good"]
    class_metrics = {}
    
    for class_name in classes:
        # True positives, false positives, false negatives, true negatives
        tp = np.sum((pred_array == class_name) & (true_array == class_name))
        fp = np.sum((pred_array == class_name) & (true_array != class_name))
        fn = np.sum((pred_array != class_name) & (true_array == class_name))
        tn = np.sum((pred_array != class_name) & (true_array != class_name))
        
        # Precision, Recall, F1-score
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        class_metrics[class_name] = {
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "support": int(np.sum(true_array == class_name))
        }
    
    # Macro averages
    macro_precision = np.mean([metrics["precision"] for metrics in class_metrics.values()])
    macro_recall = np.mean([metrics["recall"] for metrics in class_metrics.values()])
    macro_f1 = np.mean([metrics["f1_score"] for metrics in class_metrics.values()])
    
    # Weighted averages
    total_support = sum(metrics["support"] for metrics in class_metrics.values())
    if total_support > 0:
        weighted_precision = sum(metrics["precision"] * metrics["support"] for metrics in class_metrics.values()) / total_support
        weighted_recall = sum(metrics["recall"] * metrics["support"] for metrics in class_metrics.values()) / total_support
        weighted_f1 = sum(metrics["f1_score"] * metrics["support"] for metrics in class_metrics.values()) / total_support
    else:
        weighted_precision = weighted_recall = weighted_f1 = 0.0
    
    return {
        "accuracy": float(accuracy),
        "macro_avg": {
            "precision": float(macro_precision),
            "recall": float(macro_recall),
            "f1_score": float(macro_f1)
        },
        "weighted_avg": {
            "precision": float(weighted_precision),
            "recall": float(weighted_recall),
            "f1_score": float(weighted_f1)
        },
        "class_metrics": class_metrics,
        "confusion_matrix": calculate_confusion_matrix(pred_array, true_array, classes)
    }


def calculate_confusion_matrix(pred_array: np.ndarray, true_array: np.ndarray, classes: List[str]) -> Dict[str, Dict[str, int]]:
    """Calculate confusion matrix"""
    confusion_matrix = {}
    
    for true_class in classes:
        confusion_matrix[true_class] = {}
        for pred_class in classes:
            count = np.sum((true_array == true_class) & (pred_array == pred_class))
            confusion_matrix[true_class][pred_class] = int(count)
    
    return confusion_matrix


def analyze_score_distribution(predicted_scores: List[float], true_scores: List[float]) -> Dict[str, Any]:
    """Analyze the distribution of predicted vs true scores"""
    if not predicted_scores or not true_scores:
        return {}
    
    pred_array = np.array(predicted_scores)
    true_array = np.array(true_scores)
    
    # Statistical summaries
    pred_stats = {
        "mean": float(np.mean(pred_array)),
        "std": float(np.std(pred_array)),
        "min": float(np.min(pred_array)),
        "max": float(np.max(pred_array)),
        "median": float(np.median(pred_array))
    }
    
    true_stats = {
        "mean": float(np.mean(true_array)),
        "std": float(np.std(true_array)),
        "min": float(np.min(true_array)),
        "max": float(np.max(true_array)),
        "median": float(np.median(true_array))
    }
    
    # Distribution comparison
    score_ranges = [(0, 30), (30, 50), (50, 70), (70, 100)]
    range_analysis = {}
    
    for low, high in score_ranges:
        range_name = f"{low}-{high}"
        pred_in_range = np.sum((pred_array >= low) & (pred_array < high))
        true_in_range = np.sum((true_array >= low) & (true_array < high))
        
        range_analysis[range_name] = {
            "predicted_count": int(pred_in_range),
            "true_count": int(true_in_range),
            "predicted_percentage": float(pred_in_range / len(pred_array) * 100),
            "true_percentage": float(true_in_range / len(true_array) * 100)
        }
    
    return {
        "predicted_stats": pred_stats,
        "true_stats": true_stats,
        "range_analysis": range_analysis
    }


def run_accuracy_analysis(response_path: str = "results/responses/bias_fairness.jsonl") -> Dict[str, Any]:
    """
    Run comprehensive accuracy analysis on credit scoring predictions
    
    Args:
        response_path: Path to JSONL file containing API responses
        
    Returns:
        Dictionary containing accuracy metrics and analysis
    """
    logger.info("Starting accuracy analysis...")
    
    if analysis_status:
        analysis_status["progress"] = 10
        analysis_status["message"] = "Loading API responses for accuracy analysis..."
    
    # Load responses
    try:
        responses = load_jsonl(response_path)
        logger.info(f"Loaded {len(responses)} API responses")
    except FileNotFoundError:
        logger.error(f"Response file not found: {response_path}")
        return {"error": f"Response file not found: {response_path}"}
    except Exception as e:
        logger.error(f"Error loading responses: {str(e)}")
        return {"error": f"Error loading responses: {str(e)}"}
    
    if analysis_status:
        analysis_status["progress"] = 30
        analysis_status["message"] = f"Extracting predictions from {len(responses)} responses..."
    
    # Extract predictions and ground truth
    predicted_scores, predicted_classes, true_scores, true_classes = extract_predictions_and_ground_truth(responses)
    
    if not predicted_scores:
        logger.warning("No valid predictions found for accuracy analysis")
        return {"error": "No valid predictions found"}
    
    logger.info(f"Extracted {len(predicted_scores)} valid predictions for analysis")
    
    if analysis_status:
        analysis_status["progress"] = 50
        analysis_status["message"] = f"Calculating regression metrics for {len(predicted_scores)} predictions..."
    
    # Calculate regression metrics (for credit scores)
    regression_metrics = calculate_regression_metrics(predicted_scores, true_scores)
    
    if analysis_status:
        analysis_status["progress"] = 70
        analysis_status["message"] = "Calculating classification metrics..."
    
    # Calculate classification metrics
    classification_metrics = calculate_classification_metrics(predicted_classes, true_classes)
    
    if analysis_status:
        analysis_status["progress"] = 85
        analysis_status["message"] = "Analyzing score distributions..."
    
    # Analyze score distribution
    distribution_analysis = analyze_score_distribution(predicted_scores, true_scores)
    
    if analysis_status:
        analysis_status["progress"] = 95
        analysis_status["message"] = "Finalizing accuracy analysis..."
    
    # Compile results
    results = {
        "summary": {
            "total_predictions": len(predicted_scores),
            "total_responses": len(responses),
            "valid_prediction_rate": len(predicted_scores) / len(responses) if responses else 0,
        },
        "regression_metrics": regression_metrics,
        "classification_metrics": classification_metrics,
        "distribution_analysis": distribution_analysis,
        "ground_truth_method": "rule_based_synthetic",
        "timestamp": pd.Timestamp.now().isoformat()
    }
    
    # Log summary
    if regression_metrics:
        logger.info(f"Regression Metrics - MAE: {regression_metrics.get('mae', 0):.2f}, "
                   f"RMSE: {regression_metrics.get('rmse', 0):.2f}, "
                   f"R²: {regression_metrics.get('r2', 0):.3f}")
    
    if classification_metrics:
        logger.info(f"Classification Metrics - Accuracy: {classification_metrics.get('accuracy', 0):.3f}, "
                   f"Macro F1: {classification_metrics.get('macro_avg', {}).get('f1_score', 0):.3f}")
    
    if analysis_status:
        analysis_status["progress"] = 100
        analysis_status["message"] = "Accuracy analysis completed successfully!"
    
    return results


if __name__ == "__main__":
    results = run_accuracy_analysis()
    print(json.dumps(results, indent=2))