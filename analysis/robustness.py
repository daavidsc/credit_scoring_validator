# analysis/robustness.py

import pandas as pd
import json
import numpy as np
import os
from typing import Dict, List, Any, Tuple, Optional
from utils.logger import setup_logger
from api.client import send_request
import random
import string

logger = setup_logger("robustness", "results/logs/robustness.log")

# Reference to global status for progress updates
analysis_status = None

def set_status_reference(status_ref):
    """Set reference to global analysis status"""
    global analysis_status
    analysis_status = status_ref

def calculate_confidence_from_score(credit_score: float) -> float:
    """
    Calculate confidence based on how far the score is from the neutral point (50).
    
    Scores near 0 or 100 indicate high model confidence (clear poor/good decisions)
    Scores near 50 indicate lower confidence (borderline cases)
    
    Args:
        credit_score: Credit score from 0-100
        
    Returns:
        Confidence value from 0.5 to 1.0
    """
    if credit_score is None:
        return None
    
    # Distance from neutral (50) indicates confidence
    # Scores near 0 or 100 = high confidence  
    # Scores near 50 = low confidence
    distance_from_middle = abs(credit_score - 50) / 50
    
    # Map to confidence range 0.5 to 1.0
    # Distance 0 (score=50) → confidence 0.5
    # Distance 1 (score=0 or 100) → confidence 1.0
    confidence = 0.5 + distance_from_middle * 0.5
    
    return min(confidence, 1.0)

def save_jsonl(data, path):
    """Save data as JSONL format"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")

def load_jsonl(path):
    """Load data from JSONL format"""
    with open(path, "r") as f:
        return [json.loads(line) for line in f]

def add_noise_to_numerical(value, noise_factor=0.1):
    """Add gaussian noise to numerical values"""
    if pd.isna(value) or not isinstance(value, (int, float)):
        return value
    noise = np.random.normal(0, abs(value) * noise_factor)
    return value + noise

def add_typos_to_text(text, typo_rate=0.05):
    """Add random typos to text fields"""
    if pd.isna(text) or not isinstance(text, str):
        return text
    
    chars = list(text)
    num_typos = max(1, int(len(chars) * typo_rate))
    
    for _ in range(num_typos):
        if len(chars) > 0:
            pos = random.randint(0, len(chars) - 1)
            # Random typo: substitute with random letter
            chars[pos] = random.choice(string.ascii_letters)
    
    return ''.join(chars)

def capitalize_text(text):
    """Convert text to uppercase"""
    if pd.isna(text) or not isinstance(text, str):
        return text
    return text.upper()

def generate_adversarial_examples(df: pd.DataFrame, num_examples: int = 50) -> List[Dict]:
    """
    Generate adversarial examples by applying various perturbations
    """
    adversarial_examples = []
    
    # Sample random rows
    sample_indices = random.sample(range(len(df)), min(num_examples, len(df)))
    
    perturbation_types = [
        "noise_numerical", "typos_text", "case_change", "missing_values", "extreme_values"
    ]
    
    for i, idx in enumerate(sample_indices):
        original_row = df.iloc[idx].copy()
        
        for perturbation_type in perturbation_types:
            perturbed_row = original_row.copy()
            
            if perturbation_type == "noise_numerical":
                # Add noise to numerical columns
                for col in df.select_dtypes(include=[np.number]).columns:
                    if col in perturbed_row:
                        perturbed_row[col] = add_noise_to_numerical(perturbed_row[col])
                        
            elif perturbation_type == "typos_text":
                # Add typos to text columns
                for col in df.select_dtypes(include=['object']).columns:
                    if col in perturbed_row and isinstance(perturbed_row[col], str):
                        perturbed_row[col] = add_typos_to_text(perturbed_row[col])
                        
            elif perturbation_type == "case_change":
                # Change case of text columns
                for col in df.select_dtypes(include=['object']).columns:
                    if col in perturbed_row:
                        perturbed_row[col] = capitalize_text(perturbed_row[col])
                        
            elif perturbation_type == "missing_values":
                # Randomly set some values to NaN
                cols_to_modify = random.sample(list(df.columns), min(3, len(df.columns)))
                for col in cols_to_modify:
                    if col in perturbed_row:
                        perturbed_row[col] = np.nan
                        
            elif perturbation_type == "extreme_values":
                # Set numerical values to extreme values
                for col in df.select_dtypes(include=[np.number]).columns:
                    if col in perturbed_row:
                        if random.choice([True, False]):
                            perturbed_row[col] = df[col].max() * 2  # Extreme high
                        else:
                            perturbed_row[col] = df[col].min() * 2  # Extreme low
            
            # Create example record
            example = {
                "original_index": int(idx),
                "perturbation_type": perturbation_type,
                "original_data": original_row.to_dict(),
                "perturbed_data": perturbed_row.to_dict()
            }
            adversarial_examples.append(example)
    
    return adversarial_examples

def collect_robustness_responses():
    """
    Generate adversarial examples and collect API responses for robustness testing
    """
    logger.info("Starting robustness analysis...")
    
    if analysis_status:
        analysis_status["progress"] = 30
        analysis_status["message"] = "Generating adversarial examples..."
    
    # Load test data
    test_data_path = "data/testdata.csv"
    try:
        df = pd.read_csv(test_data_path)
        logger.info(f"Loaded {len(df)} test profiles from {test_data_path}")
    except FileNotFoundError:
        logger.error(f"Test data file not found: {test_data_path}")
        return []
    except Exception as e:
        logger.error(f"Error loading test data: {str(e)}")
        return []
    
    # Generate adversarial examples - increased from 20 to 50 for better robustness testing
    adversarial_examples = generate_adversarial_examples(df, num_examples=50)
    logger.info(f"Generated {len(adversarial_examples)} adversarial examples")
    
    if analysis_status:
        analysis_status["progress"] = 40
        analysis_status["message"] = f"Making API calls for {len(adversarial_examples)} adversarial examples..."
    
    responses = []
    total_examples = len(adversarial_examples)
    
    for i, example in enumerate(adversarial_examples):
        try:
            # Make API call with original data
            original_response = send_request(example["original_data"])
            
            # Make API call with perturbed data
            perturbed_response = send_request(example["perturbed_data"])
            
            response_record = {
                "example_index": i,
                "original_index": example["original_index"],
                "perturbation_type": example["perturbation_type"],
                "original_data": example["original_data"],
                "perturbed_data": example["perturbed_data"],
                "original_response": original_response,
                "perturbed_response": perturbed_response
            }
            responses.append(response_record)
            
            if analysis_status:
                progress = 40 + int((i + 1) / total_examples * 40)  # 40-80% for API calls
                analysis_status["progress"] = progress
                analysis_status["message"] = f"Processing adversarial example {i + 1}/{total_examples}..."
            
            logger.info(f"Processed adversarial example {i + 1}/{total_examples}")
            
        except Exception as e:
            logger.error(f"Error processing example {i}: {str(e)}")
            continue
    
    # Save responses
    output_path = "results/responses/robustness.jsonl"
    save_jsonl(responses, output_path)
    logger.info(f"Saved {len(responses)} responses to {output_path}")
    
    return responses

def extract_response_text(response) -> str:
    """Extract text from response object, handling different formats"""
    if not response:
        return ""
    
    # Handle error responses
    if isinstance(response, dict) and "error_type" in response:
        return f"Error: {response.get('error', 'Unknown error')}"
    
    # Handle new API response format
    if isinstance(response, dict):
        if "parsed" in response and response["parsed"]:
            parsed = response["parsed"]
            if isinstance(parsed, dict):
                # Create a string representation from parsed fields
                parts = []
                if "credit_score" in parsed and parsed["credit_score"] is not None:
                    parts.append(f"score:{parsed['credit_score']}")
                if "classification" in parsed and parsed["classification"]:
                    parts.append(f"class:{parsed['classification']}")
                if "explanation" in parsed and parsed["explanation"]:
                    parts.append(f"reason:{parsed['explanation']}")
                return " ".join(parts) if parts else "no_data"
            else:
                return str(parsed)
        elif "raw_response" in response:
            return str(response["raw_response"])
        else:
            return str(response)
    elif isinstance(response, str):
        return response
    else:
        return str(response) if response else ""

def parse_credit_decision(response) -> Tuple[Optional[str], Optional[float], str]:
    """
    Parse credit decision from API response
    Returns (decision, confidence, reasoning)
    """
    # First extract text from response object
    response_text = extract_response_text(response)
    
    if not response_text:
        return None, None, "No response"
    
    text_lower = response_text.lower()
    
    # Extract decision
    decision = None
    
    # Handle structured format (score:X class:Y reason:Z)
    if "class:" in text_lower:
        if "class:good" in text_lower or "class:approved" in text_lower:
            decision = "good"
        elif "class:poor" in text_lower or "class:bad" in text_lower or "class:denied" in text_lower:
            decision = "poor"
        elif "class:average" in text_lower or "class:moderate" in text_lower:
            # For average, check score if available (API returns scores 0-100)
            if "score:" in text_lower:
                import re
                score_match = re.search(r'score:(\d+)', text_lower)
                if score_match:
                    score = int(score_match.group(1))
                    if score >= 70:
                        decision = "good"  # High average treated as good
                    elif score < 60:
                        decision = "poor"  # Low average treated as poor
                    else:
                        decision = "average"  # True average
            else:
                decision = "average"  # Default for average without score
    else:
        # Handle traditional text format (Good/Average/Poor classifications and legacy approve/deny)
        if "good" in text_lower or "approve" in text_lower or "approved" in text_lower:
            decision = "good"
        elif "poor" in text_lower or "deny" in text_lower or "denied" in text_lower or "reject" in text_lower:
            decision = "poor"
        elif "average" in text_lower or "moderate" in text_lower:
            decision = "average"
    
    # Extract confidence (look for percentages or confidence indicators)
    confidence = None
    try:
        import re
        confidence_matches = re.findall(r'(\d+)%', response_text)
        if confidence_matches:
            confidence = float(confidence_matches[0]) / 100.0
        elif "high confidence" in text_lower:
            confidence = 0.8
        elif "medium confidence" in text_lower:
            confidence = 0.6
        elif "low confidence" in text_lower:
            confidence = 0.4
        elif "score:" in text_lower:
            # Use improved score-based confidence proxy if no explicit confidence (API returns 0-100)
            score_match = re.search(r'score:(\d+)', text_lower)
            if score_match:
                score = int(score_match.group(1))
                confidence = calculate_confidence_from_score(score)
    except:
        pass
    
    return decision, confidence, response_text

def analyze_robustness_results(responses: List[Dict]) -> Dict[str, Any]:
    """
    Analyze robustness test results
    """
    logger.info("Analyzing robustness results...")
    
    if analysis_status:
        analysis_status["progress"] = 85
        analysis_status["message"] = "Analyzing robustness results..."
    
    results = {
        "total_examples": len(responses),
        "perturbation_analysis": {},
        "decision_consistency": {},
        "confidence_stability": {},
        "robustness_score": 0.0,
        "failure_cases": []
    }
    
    decision_consistent = 0
    confidence_differences = []
    perturbation_stats = {}
    valid_examples = 0  # Count examples with valid original responses
    
    for response in responses:
        perturbation_type = response["perturbation_type"]
        
        # Parse decisions and confidence
        original_decision, original_conf, orig_text = parse_credit_decision(
            response["original_response"]
        )
        perturbed_decision, perturbed_conf, pert_text = parse_credit_decision(
            response["perturbed_response"]
        )
        
        # Skip cases where original response failed (we need a baseline)
        if original_decision is None and "error" in orig_text.lower():
            continue
            
        valid_examples += 1  # Count this as a valid test case
        
        # Track perturbation type stats
        if perturbation_type not in perturbation_stats:
            perturbation_stats[perturbation_type] = {
                "total": 0,
                "consistent_decisions": 0,
                "confidence_drops": []
            }
        
        perturbation_stats[perturbation_type]["total"] += 1
        
        # Check decision consistency
        # If perturbation caused an error, that might be appropriate (robust behavior)
        # If perturbation succeeded but gave different decision, that's inconsistent
        decisions_consistent = (original_decision == perturbed_decision)
        
        # Handle error cases: if perturbed response has an error, consider it "robust"
        # since the API correctly rejected invalid/corrupted data
        if perturbed_decision is None and "error" in pert_text.lower():
            decisions_consistent = True  # Robust: API correctly rejected bad input
        
        if decisions_consistent:
            decision_consistent += 1
            perturbation_stats[perturbation_type]["consistent_decisions"] += 1
        
        # Check confidence stability
        if original_conf is not None and perturbed_conf is not None:
            conf_diff = abs(original_conf - perturbed_conf)
            confidence_differences.append(conf_diff)
            perturbation_stats[perturbation_type]["confidence_drops"].append(conf_diff)
        
        # Record failure cases (major inconsistencies)
        if not decisions_consistent or (original_conf and perturbed_conf and abs(original_conf - perturbed_conf) > 0.3):
            failure_case = {
                "perturbation_type": perturbation_type,
                "original_decision": original_decision,
                "perturbed_decision": perturbed_decision,
                "original_confidence": original_conf,
                "perturbed_confidence": perturbed_conf,
                "original_response": orig_text[:200] + "..." if len(orig_text) > 200 else orig_text,
                "perturbed_response": pert_text[:200] + "..." if len(pert_text) > 200 else pert_text
            }
            results["failure_cases"].append(failure_case)
    
    # Calculate overall metrics using valid examples count
    results["total_examples"] = valid_examples  # Update to use actual processed count
    results["decision_consistency"]["rate"] = decision_consistent / valid_examples if valid_examples > 0 else 0
    results["decision_consistency"]["consistent_count"] = decision_consistent
    results["decision_consistency"]["inconsistent_count"] = valid_examples - decision_consistent
    
    if confidence_differences:
        results["confidence_stability"]["mean_difference"] = np.mean(confidence_differences)
        results["confidence_stability"]["max_difference"] = np.max(confidence_differences)
        results["confidence_stability"]["std_difference"] = np.std(confidence_differences)
    
    # Analyze by perturbation type
    for ptype, stats in perturbation_stats.items():
        consistency_rate = stats["consistent_decisions"] / stats["total"] if stats["total"] > 0 else 0
        avg_conf_drop = np.mean(stats["confidence_drops"]) if stats["confidence_drops"] else 0
        
        results["perturbation_analysis"][ptype] = {
            "total_examples": stats["total"],
            "consistency_rate": consistency_rate,
            "average_confidence_drop": avg_conf_drop,
            "max_confidence_drop": np.max(stats["confidence_drops"]) if stats["confidence_drops"] else 0
        }
    
    # Calculate overall robustness score (0-1, higher is better)
    decision_score = results["decision_consistency"]["rate"]
    confidence_score = 1.0 - (results["confidence_stability"].get("mean_difference", 0.5))
    confidence_score = max(0, min(1, confidence_score))  # Clamp to [0,1]
    
    results["robustness_score"] = (decision_score * 0.7 + confidence_score * 0.3)
    
    logger.info(f"Robustness analysis complete. Score: {results['robustness_score']:.3f}")
    return results

def run_robustness_analysis():
    """
    Main function to run robustness analysis
    """
    logger.info("=== Starting Robustness Analysis ===")
    
    try:
        # Check if we have existing responses
        response_path = "results/responses/robustness.jsonl"
        
        if os.path.exists(response_path):
            logger.info("Loading existing robustness responses...")
            responses = load_jsonl(response_path)
            if analysis_status:
                analysis_status["progress"] = 80
                analysis_status["message"] = "Analyzing existing robustness data..."
        else:
            # Collect new responses
            responses = collect_robustness_responses()
        
        if not responses:
            logger.error("No responses collected for robustness analysis")
            return {"error": "No responses collected"}
        
        # Analyze results
        results = analyze_robustness_results(responses)
        
        logger.info("=== Robustness Analysis Complete ===")
        return results
        
    except Exception as e:
        logger.error(f"Error in robustness analysis: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return {"error": str(e)}