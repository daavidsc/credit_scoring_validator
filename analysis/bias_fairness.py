# analysis/bias_fairness.py

import pandas as pd
import json
import os
from api.client import send_request
from config import RESPONSE_DIR
from utils.logger import setup_logger

logger = setup_logger("bias_fairness", "results/logs/bias_fairness.log")


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

    for i, row in df.iterrows():
        input_data = row.to_dict()
        prediction = send_request(input_data)
        responses.append({
            "input": input_data,
            "output": prediction
        })

        logger.info(f"Processed row {i + 1}/{len(df)}")

    save_jsonl(responses, output_path)
    logger.info(f"Saved responses to {output_path}")


def demographic_parity(responses, protected_attr, positive_class="Approved"):
    groups = {}
    for entry in responses:
        group = entry["input"][protected_attr]
        pred = entry["output"].get("credit_decision", None)
        if pred is None:
            continue

        if group not in groups:
            groups[group] = {"total": 0, "positive": 0}

        groups[group]["total"] += 1
        if pred == positive_class:
            groups[group]["positive"] += 1

    logger.info(f"Demographic Parity by {protected_attr}")
    for group, values in groups.items():
        rate = values["positive"] / values["total"] if values["total"] > 0 else 0
        logger.info(f"  {group}: {rate:.2%}")

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


def equal_opportunity(responses, protected_attr, label_field="actual_approved", positive_class="Approved"):
    """
    Calculate TPR (True Positive Rate) per group.
    """
    group_stats = {}

    for entry in responses:
        group = entry["input"][protected_attr]
        label = entry["input"].get(label_field)
        pred = entry["output"].get("credit_decision")

        if label is None or pred is None:
            continue

        if group not in group_stats:
            group_stats[group] = {"actual_positive": 0, "true_positive": 0}

        if label:  # actual label is positive
            group_stats[group]["actual_positive"] += 1
            if pred == positive_class:
                group_stats[group]["true_positive"] += 1

    for group, stats in group_stats.items():
        tpr = stats["true_positive"] / stats["actual_positive"] if stats["actual_positive"] > 0 else 0
        logger.info(f"Equal Opportunity (TPR) for {group}: {tpr:.2%}")

    return group_stats


def counterfactual_fairness(df, protected_attr, values=("male", "female", "non-binary")):
    """
    Generate counterfactuals by flipping the protected attribute to other possible values.
    Count how often the decision changes.
    """
    total_rows = 0
    total_violations = 0

    for _, row in df.iterrows():
        input_data = row.to_dict()
        original_value = input_data.get(protected_attr)
        if original_value not in values:
            continue

        original_response = send_request(input_data)
        original_decision = original_response.get("credit_decision")
        if original_decision is None:
            continue

        # Generate counterfactuals
        for alt_value in values:
            if alt_value == original_value:
                continue

            cf_input = input_data.copy()
            cf_input[protected_attr] = alt_value
            cf_response = send_request(cf_input)
            cf_decision = cf_response.get("credit_decision")

            if cf_decision != original_decision:
                logger.info(f"Counterfactual violation: {original_value} -> {alt_value}")
                total_violations += 1

        total_rows += 1

    total_tests = total_rows * (len(values) - 1)
    ratio = total_violations / total_tests if total_tests > 0 else 0.0
    logger.info(f"Counterfactual Fairness Violation Rate: {ratio:.2%} ({total_violations}/{total_tests})")

    return {
        "total_rows": total_rows,
        "total_tests": total_tests,
        "violations": total_violations,
        "violation_ratio": ratio
    }


PROTECTED_ATTRIBUTES = ["gender", "ethnicity", "nationality", "disability_status", "marital_status"]


def run_bias_analysis():
    dataset_path = "data/testdata.csv"
    response_path = f"{RESPONSE_DIR}/bias_fairness.jsonl"

    df = pd.read_csv(dataset_path)

    # Collect API responses (only once)
    if not os.path.exists(response_path):
        responses = []
        for i, row in df.iterrows():
            input_data = row.to_dict()
            prediction = send_request(input_data)
            responses.append({
                "input": input_data,
                "output": prediction
            })
        save_jsonl(responses, response_path)
    else:
        responses = load_jsonl(response_path)

    results = {}

    for attr in PROTECTED_ATTRIBUTES:
        logger.info(f"🔍 Analyzing fairness for: {attr}")

        dp_groups = demographic_parity(responses, protected_attr=attr)
        di_ratio = disparate_impact_ratio(dp_groups)

        eo_stats = equal_opportunity(
            responses,
            protected_attr=attr,
            label_field="actual_approved"
        )

        unique_vals = df[attr].dropna().unique().tolist()
        if len(unique_vals) >= 2:
            cf_result = counterfactual_fairness(df, protected_attr=attr, values=unique_vals)
        else:
            cf_result = {
                "violation_ratio": None,
                "note": "Not enough distinct values for counterfactuals"
            }

        results[attr] = {
            "demographic_parity": dp_groups,
            "disparate_impact_ratio": di_ratio,
            "equal_opportunity": eo_stats,
            "counterfactual_fairness": cf_result
        }

    return results



if __name__ == "__main__":
    results = run_bias_analysis()
    print(json.dumps(results, indent=2))
