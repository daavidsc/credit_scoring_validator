# analysis/bias_fairness.py

import pandas as pd
import json
import os
from api.client import send_request
from config import RESPONSE_DIR
from utils.logger import setup_logger

logger = setup_logger("bias_fairness", "results/logs/bias_fairness.log")

PROTECTED_ATTRIBUTES = ["gender", "ethnicity", "nationality", "disability_status", "marital_status"]

# Reference to global status for progress updates
analysis_status = None

def set_status_reference(status_ref):
    """Set reference to global analysis status"""
    global analysis_status
    analysis_status = status_ref


def save_jsonl(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")


def load_jsonl(path):
    with open(path, "r") as f:
        return [json.loads(line) for line in f]


def collect_responses(input_path, output_path):
    df = pd.read_csv(input_path)
    responses = []
    total_rows = len(df)

    if analysis_status:
        analysis_status["progress"] = 30
        analysis_status["message"] = f"Starting API calls for {total_rows} profiles..."

    for i, row in df.iterrows():
        input_data = row.to_dict()
        
        if analysis_status:
            progress = 30 + int((i + 1) / total_rows * 50)  # 30-80% for API calls
            analysis_status["progress"] = progress
            analysis_status["message"] = f"Making API call {i + 1}/{total_rows}: {input_data.get('name', 'Unknown')}..."
        
        prediction = send_request(input_data)
        responses.append({
            "input": input_data,
            "output": prediction
        })
            
        logger.info(f"Processed row {i + 1}/{len(df)}")

    save_jsonl(responses, output_path)
    logger.info(f"Saved responses to {output_path}")
    
    if analysis_status:
        analysis_status["progress"] = 80
        analysis_status["message"] = "All API calls completed successfully! Starting bias pattern analysis..."


def demographic_parity(responses, protected_attr, positive_class="Good"):
    """
    Analyze demographic parity based on credit score classifications.
    positive_class can be 'Good', 'Average', 'Poor', or a specific score threshold.
    """
    groups = {}
    total_processed = 0
    errors_encountered = 0
    
    for entry in responses:
        total_processed += 1
        
        # Skip entries with errors - check for error keys in the entry
        has_error = "error" in entry or "error_type" in entry
        if has_error or "output" not in entry:
            errors_encountered += 1
            continue
            
        group = entry["input"].get(protected_attr)
        # Look for the parsed response structure
        parsed_output = entry["output"].get("parsed", {})
        classification = parsed_output.get("classification")
        credit_score = parsed_output.get("credit_score")
        
        if group is None or (classification is None and credit_score is None):
            errors_encountered += 1
            continue

        if group not in groups:
            groups[group] = {
                "total": 0, 
                "positive": 0, 
                "scores": [], 
                "classifications": {"Poor": 0, "Average": 0, "Good": 0},
                "errors": 0
            }

        groups[group]["total"] += 1
        
        # Add score to list for later analysis
        if credit_score is not None:
            try:
                score_val = float(credit_score)
                groups[group]["scores"].append(score_val)
            except (ValueError, TypeError):
                groups[group]["errors"] += 1
        
        # Track classification distribution
        if classification and classification in groups[group]["classifications"]:
            groups[group]["classifications"][classification] += 1
        
        # Determine if this is a "positive" outcome
        is_positive = False
        if classification:
            # Treat specified classification as positive outcome
            is_positive = classification == positive_class
        elif credit_score is not None:
            # If no classification, use score threshold (e.g., >= 70 is positive for 0-100 scale)
            try:
                score_val = float(credit_score)
                is_positive = score_val >= 70  # Threshold for 0-100 scale
            except (ValueError, TypeError):
                groups[group]["errors"] += 1
        
        if is_positive:
            groups[group]["positive"] += 1

    # Calculate and log statistics
    logger.info(f"Demographic Parity by {protected_attr}: "
                f"Processed {total_processed}, Errors {errors_encountered}")
    for group, values in groups.items():
        rate = values["positive"] / values["total"] if values["total"] > 0 else 0
        avg_score = sum(values["scores"]) / len(values["scores"]) if values["scores"] else 0
        
        # Classification breakdown
        class_dist = []
        for class_name in ["Poor", "Average", "Good"]:
            count = values["classifications"][class_name]
            pct = (count / values["total"] * 100) if values["total"] > 0 else 0
            class_dist.append(f"{class_name}: {pct:.1f}%")
        
        logger.info(f"  {group}: {rate:.2%} '{positive_class}' rate, avg score: {avg_score:.1f}, n={values['total']}")
        logger.info(f"    Classifications - {', '.join(class_dist)}")

    return groups


def disparate_impact_ratio(groups):
    rates = {
        group: values["positive"] / values["total"]
        for group, values in groups.items()
        if values["total"] > 0
    }
    if not rates:
        return 0.0

    max_rate = max(rates.values())
    min_rate = min(rates.values())
    ratio = min_rate / max_rate if max_rate > 0 else 0
    logger.info(f"Disparate Impact Ratio: {ratio:.2f}")
    return ratio


def counterfactual_fairness(df, protected_attr, values, sample_size=100):
    """
    Test for disparate treatment by changing only the protected attribute.
    Takes a sample of rows and tests what happens when we only change the protected attribute.
    """
    total_rows = 0
    total_violations = 0
    
    # Sample a subset for more focused testing
    sample_df = df.sample(n=min(sample_size, len(df)), random_state=42)
    total_sample_rows = len(sample_df)

    for idx, (_, row) in enumerate(sample_df.iterrows()):
        if analysis_status:
            # More granular progress within counterfactual testing
            cf_progress = int((idx / total_sample_rows) * 100)
            analysis_status["message"] = f"Counterfactual testing {protected_attr}: {idx+1}/{total_sample_rows} profiles ({cf_progress}%)"
        
        input_data = row.to_dict()
        original_value = input_data.get(protected_attr)
        if original_value not in values:
            continue

        original_response = send_request(input_data)
        parsed_original = original_response.get("parsed", {})
        original_classification = parsed_original.get("classification")
        original_score = parsed_original.get("credit_score")
        
        if original_classification is None and original_score is None:
            continue

        for alt_value in values:
            if alt_value == original_value:
                continue

            # Create counterfactual by ONLY changing the protected attribute
            cf_input = input_data.copy()
            cf_input[protected_attr] = alt_value
            cf_response = send_request(cf_input)
            parsed_cf = cf_response.get("parsed", {})
            cf_classification = parsed_cf.get("classification")
            cf_score = parsed_cf.get("credit_score")

            # Check for classification differences
            classification_changed = (original_classification != cf_classification)
            
            # Check for significant score differences (>= 10 points for 0-100 scale)
            score_changed = False
            score_diff = 0
            if original_score is not None and cf_score is not None:
                try:
                    score_diff = abs(float(original_score) - float(cf_score))
                    score_changed = score_diff >= 10  # Significant difference for 0-100 scale
                except (ValueError, TypeError):
                    pass

            if classification_changed or score_changed:
                logger.info(f"🚨 BIAS DETECTED: {protected_attr} = {original_value} → {alt_value}")
                logger.info(f"  Profile: Income={input_data.get('income')}, Age={input_data.get('age')}, Employment={input_data.get('employment_status')}")
                logger.info(f"  Classification: {original_classification} → {cf_classification}")
                logger.info(f"  Score: {original_score} → {cf_score} (diff: {score_diff:.1f})")
                logger.info("  ⚠️  This suggests disparate treatment based on protected attribute!")
                total_violations += 1

        total_rows += 1

    total_tests = total_rows * (len(values) - 1)
    ratio = total_violations / total_tests if total_tests > 0 else 0.0

    logger.info(f"Counterfactual Fairness for {protected_attr}: {ratio:.2%} ({total_violations}/{total_tests})")
    if ratio > 0.05:  # More than 5% violations
        logger.warning(f"⚠️  HIGH BIAS RISK: {ratio:.2%} of counterfactual tests show different outcomes for {protected_attr}")

    return {
        "total_rows": total_rows,
        "total_tests": total_tests,
        "violations": total_violations,
        "violation_ratio": ratio,
        "sample_size": len(sample_df),
        "bias_level": "HIGH" if ratio > 0.05 else "LOW" if ratio > 0.01 else "MINIMAL"
    }


def run_bias_analysis():
    dataset_path = "data/testdata.csv"
    response_path = f"{RESPONSE_DIR}/bias_fairness.jsonl"

    # Always load original dataset (needed for counterfactuals)
    df = pd.read_csv(dataset_path)
    total_attributes = len(PROTECTED_ATTRIBUTES)

    if analysis_status:
        analysis_status["progress"] = 25
        analysis_status["message"] = f"Loaded {len(df)} records, checking for existing API responses..."

    if not os.path.exists(response_path):
        if analysis_status:
            analysis_status["progress"] = 30
            analysis_status["message"] = "No existing responses found, making API calls..."
        collect_responses(dataset_path, response_path)
    else:
        if analysis_status:
            analysis_status["progress"] = 80
            analysis_status["message"] = "Found existing API responses, starting bias analysis..."

    responses = load_jsonl(response_path)

    if analysis_status:
        analysis_status["progress"] = 82
        analysis_status["message"] = f"Loaded {len(responses)} API responses, starting bias pattern analysis..."

    results = {}

    for i, attr in enumerate(PROTECTED_ATTRIBUTES):
        if analysis_status:
            progress = 85 + int((i / total_attributes) * 12)  # 85-97% for bias analysis
            analysis_status["progress"] = progress
            analysis_status["message"] = f"Analyzing bias patterns for {attr} ({i+1}/{total_attributes})..."
        
        logger.info(f"🔍 Analyzing demographic parity for: {attr}")

        dp_groups = demographic_parity(responses, protected_attr=attr)
        di_ratio = disparate_impact_ratio(dp_groups)

        results[attr] = {
            "demographic_parity": dp_groups,
            "disparate_impact_ratio": di_ratio
        }

        # Counterfactual fairness (only if enough values)
        unique_vals = df[attr].dropna().unique().tolist()
        if len(unique_vals) >= 2:
            if analysis_status:
                analysis_status["message"] = f"Running counterfactual tests for {attr} with {len(unique_vals)} different values..."
            # Use smaller sample size for focused bias testing
            cf_result = counterfactual_fairness(df, protected_attr=attr, values=unique_vals, sample_size=200)
        else:
            cf_result = {
                "violation_ratio": None,
                "note": "Not enough distinct values for counterfactuals"
            }

        results[attr]["counterfactual_fairness"] = cf_result

    if analysis_status:
        analysis_status["progress"] = 98
        analysis_status["message"] = "Bias analysis complete, finalizing results..."

    return results


if __name__ == "__main__":
    results = run_bias_analysis()
    print(json.dumps(results, indent=2))
