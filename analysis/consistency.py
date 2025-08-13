# analysis/consistency.py

"""
Consistency Analysis Module

Tests whether the same input data produces consistent responses from the API.
This helps identify non-deterministic behavior, caching issues, or other
sources of inconsistency in the credit scoring model.
"""

import pandas as pd
import json
import numpy as np
import os
from typing import Dict, List, Any, Tuple, Optional
from utils.logger import setup_logger
from api.client import send_request
import time
import hashlib

logger = setup_logger("consistency", "results/logs/consistency.log")

# Reference to global status for progress updates
analysis_status = None

def set_status_reference(status_ref):
    """Set reference to global analysis status"""
    global analysis_status
    analysis_status = status_ref

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

def hash_input_data(data: dict) -> str:
    """Create a hash of input data for tracking"""
    # Sort keys to ensure consistent hashing
    sorted_data = {k: data[k] for k in sorted(data.keys())}
    data_str = json.dumps(sorted_data, sort_keys=True, default=str)
    return hashlib.md5(data_str.encode()).hexdigest()

def normalize_response_text(response: str) -> str:
    """Normalize response text for comparison"""
    if not response:
        return ""
    
    # Convert to lowercase and strip whitespace
    normalized = response.lower().strip()
    
    # Remove extra whitespace
    normalized = ' '.join(normalized.split())
    
    return normalized

def extract_decision_and_confidence(response: str) -> Tuple[Optional[str], Optional[float]]:
    """Extract decision and confidence from response"""
    if not response:
        return None, None
    
    text_lower = response.lower()
    
    # Extract decision
    decision = None
    if "approve" in text_lower or "approved" in text_lower:
        decision = "approve"
    elif "deny" in text_lower or "denied" in text_lower or "reject" in text_lower:
        decision = "deny"
    
    # Extract confidence (look for percentages)
    confidence = None
    try:
        import re
        confidence_matches = re.findall(r'(\d+(?:\.\d+)?)%', response)
        if confidence_matches:
            confidence = float(confidence_matches[0]) / 100.0
        elif "high confidence" in text_lower:
            confidence = 0.8
        elif "medium confidence" in text_lower:
            confidence = 0.6
        elif "low confidence" in text_lower:
            confidence = 0.4
    except:
        pass
    
    return decision, confidence

def collect_consistency_responses(num_repeats: int = 3, delay_seconds: float = 1.0):
    """
    Collect multiple responses for the same inputs to test consistency
    """
    logger.info("Starting consistency analysis...")
    
    if analysis_status:
        analysis_status["progress"] = 30
        analysis_status["message"] = "Loading test data for consistency analysis..."
    
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
    
    # Select a subset for consistency testing (to avoid too many API calls)
    num_samples = min(10, len(df))  # Test with 10 samples
    sample_df = df.sample(n=num_samples, random_state=42)
    
    if analysis_status:
        analysis_status["progress"] = 40
        analysis_status["message"] = f"Testing consistency with {num_samples} samples, {num_repeats} repeats each..."
    
    consistency_data = []
    total_calls = num_samples * num_repeats
    call_count = 0
    
    for idx, (_, row) in enumerate(sample_df.iterrows()):
        input_data = row.to_dict()
        input_hash = hash_input_data(input_data)
        
        logger.info(f"Testing consistency for sample {idx + 1}/{num_samples}")
        
        responses_for_input = []
        
        # Make multiple API calls with the same input
        for repeat in range(num_repeats):
            try:
                if delay_seconds > 0 and repeat > 0:
                    time.sleep(delay_seconds)  # Small delay between calls
                
                response = send_request(input_data)
                call_count += 1
                
                response_record = {
                    "input_hash": input_hash,
                    "input_data": input_data,
                    "repeat_number": repeat + 1,
                    "response": response,
                    "timestamp": time.time(),
                    "call_order": call_count
                }
                
                responses_for_input.append(response_record)
                
                if analysis_status:
                    progress = 40 + int((call_count / total_calls) * 40)  # 40-80% for API calls
                    analysis_status["progress"] = progress
                    analysis_status["message"] = f"API call {call_count}/{total_calls}: Sample {idx+1}, repeat {repeat+1}"
                
                logger.info(f"Completed call {call_count}/{total_calls}")
                
            except Exception as e:
                logger.error(f"Error making API call for sample {idx}, repeat {repeat}: {str(e)}")
                continue
        
        if responses_for_input:
            consistency_record = {
                "input_hash": input_hash,
                "input_data": input_data,
                "sample_index": idx,
                "responses": responses_for_input,
                "num_responses": len(responses_for_input)
            }
            consistency_data.append(consistency_record)
    
    # Save consistency data
    output_path = "results/responses/consistency.jsonl"
    save_jsonl(consistency_data, output_path)
    logger.info(f"Saved consistency data for {len(consistency_data)} inputs to {output_path}")
    
    return consistency_data

def analyze_consistency_results(consistency_data: List[Dict]) -> Dict[str, Any]:
    """
    Analyze consistency test results
    """
    logger.info("Analyzing consistency results...")
    
    if analysis_status:
        analysis_status["progress"] = 85
        analysis_status["message"] = "Analyzing consistency results..."
    
    results = {
        "total_inputs": len(consistency_data),
        "total_responses": 0,
        "perfect_consistency": 0,
        "decision_consistency": 0,
        "confidence_consistency": 0,
        "text_similarity_scores": [],
        "consistency_by_input": [],
        "inconsistent_cases": [],
        "overall_consistency_score": 0.0,
        "statistics": {}
    }
    
    perfect_consistent_count = 0
    decision_consistent_count = 0
    confidence_consistent_count = 0
    all_text_similarities = []
    
    for input_record in consistency_data:
        input_hash = input_record["input_hash"]
        responses = input_record["responses"]
        results["total_responses"] += len(responses)
        
        if len(responses) < 2:
            continue  # Need at least 2 responses to check consistency
        
        # Extract responses for analysis
        response_texts = [r["response"] for r in responses]
        normalized_responses = [normalize_response_text(r) for r in response_texts]
        decisions = []
        confidences = []
        
        for response_text in response_texts:
            decision, confidence = extract_decision_and_confidence(response_text)
            decisions.append(decision)
            confidences.append(confidence)
        
        # Check perfect text consistency
        perfect_consistent = len(set(normalized_responses)) == 1
        if perfect_consistent:
            perfect_consistent_count += 1
        
        # Check decision consistency
        decision_consistent = len(set(filter(None, decisions))) <= 1
        if decision_consistent:
            decision_consistent_count += 1
        
        # Check confidence consistency (within 5% tolerance)
        confidence_values = [c for c in confidences if c is not None]
        confidence_consistent = False
        if confidence_values:
            confidence_range = max(confidence_values) - min(confidence_values)
            confidence_consistent = confidence_range <= 0.05  # 5% tolerance
            if confidence_consistent:
                confidence_consistent_count += 1
        
        # Calculate text similarity scores
        text_similarities = []
        for i in range(len(response_texts)):
            for j in range(i + 1, len(response_texts)):
                # Simple similarity based on common words
                words1 = set(normalized_responses[i].split())
                words2 = set(normalized_responses[j].split())
                if words1 or words2:
                    similarity = len(words1.intersection(words2)) / len(words1.union(words2))
                else:
                    similarity = 1.0  # Both empty
                text_similarities.append(similarity)
                all_text_similarities.append(similarity)
        
        avg_text_similarity = np.mean(text_similarities) if text_similarities else 1.0
        
        # Record per-input analysis
        input_analysis = {
            "input_hash": input_hash,
            "num_responses": len(responses),
            "perfect_consistent": perfect_consistent,
            "decision_consistent": decision_consistent,
            "confidence_consistent": confidence_consistent,
            "avg_text_similarity": avg_text_similarity,
            "unique_responses": len(set(normalized_responses)),
            "decisions": decisions,
            "confidences": confidences,
            "response_texts": response_texts[:3]  # Store first 3 for display
        }
        results["consistency_by_input"].append(input_analysis)
        
        # Record inconsistent cases
        if not perfect_consistent:
            inconsistent_case = {
                "input_hash": input_hash,
                "input_data": input_record["input_data"],
                "responses": response_texts,
                "decisions": decisions,
                "confidences": confidences,
                "issues": []
            }
            
            if not decision_consistent:
                inconsistent_case["issues"].append("decision_inconsistency")
            if not confidence_consistent and confidence_values:
                inconsistent_case["issues"].append("confidence_inconsistency")
            if avg_text_similarity < 0.8:
                inconsistent_case["issues"].append("text_dissimilarity")
            
            results["inconsistent_cases"].append(inconsistent_case)
    
    # Calculate overall metrics
    total_inputs = len(consistency_data)
    if total_inputs > 0:
        results["perfect_consistency"] = perfect_consistent_count / total_inputs
        results["decision_consistency"] = decision_consistent_count / total_inputs
        results["confidence_consistency"] = confidence_consistent_count / total_inputs
    else:
        # No data to analyze - default to perfect consistency
        results["perfect_consistency"] = 1.0
        results["decision_consistency"] = 1.0
        results["confidence_consistency"] = 1.0
    
    if all_text_similarities:
        results["text_similarity_scores"] = all_text_similarities
        avg_text_similarity = np.mean(all_text_similarities)
    else:
        avg_text_similarity = 1.0
    
    # Calculate overall consistency score (weighted average)
    decision_weight = 0.5
    confidence_weight = 0.3  
    text_weight = 0.2
    
    # Handle empty data case
    if total_inputs == 0:
        results["overall_consistency_score"] = 1.0  # Perfect consistency when no data
    else:
        results["overall_consistency_score"] = (
            results["decision_consistency"] * decision_weight +
            results["confidence_consistency"] * confidence_weight +
            avg_text_similarity * text_weight
        )
    
    # Statistical analysis
    results["statistics"] = {
        "mean_text_similarity": np.mean(all_text_similarities) if all_text_similarities else 1.0,
        "std_text_similarity": np.std(all_text_similarities) if all_text_similarities else 0.0,
        "min_text_similarity": np.min(all_text_similarities) if all_text_similarities else 1.0,
        "max_text_similarity": np.max(all_text_similarities) if all_text_similarities else 1.0,
        "perfect_consistency_rate": results["perfect_consistency"],
        "decision_consistency_rate": results["decision_consistency"],
        "confidence_consistency_rate": results["confidence_consistency"]
    }
    
    logger.info(f"Consistency analysis complete. Overall score: {results['overall_consistency_score']:.3f}")
    return results

def run_consistency_analysis(num_repeats: int = 3, delay_seconds: float = 1.0):
    """
    Main function to run consistency analysis
    """
    logger.info("=== Starting Consistency Analysis ===")
    
    try:
        # Check if we have existing consistency data
        response_path = "results/responses/consistency.jsonl"
        
        if os.path.exists(response_path):
            logger.info("Loading existing consistency responses...")
            consistency_data = load_jsonl(response_path)
            if analysis_status:
                analysis_status["progress"] = 80
                analysis_status["message"] = "Analyzing existing consistency data..."
        else:
            # Collect new consistency data
            consistency_data = collect_consistency_responses(num_repeats, delay_seconds)
        
        if not consistency_data:
            logger.error("No consistency data collected")
            return {"error": "No consistency data collected"}
        
        # Analyze results
        results = analyze_consistency_results(consistency_data)
        
        logger.info("=== Consistency Analysis Complete ===")
        return results
        
    except Exception as e:
        logger.error(f"Error in consistency analysis: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return {"error": str(e)}
