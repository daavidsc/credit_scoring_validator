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

def hash_input_data(data: dict) -> str:
    """Create a hash of input data for tracking"""
    # Sort keys to ensure consistent hashing
    sorted_data = {k: data[k] for k in sorted(data.keys())}
    data_str = json.dumps(sorted_data, sort_keys=True, default=str)
    return hashlib.md5(data_str.encode()).hexdigest()

def normalize_response_text(response) -> str:
    """Normalize response text for comparison"""
    # Handle different response formats
    if isinstance(response, dict):
        # New API response format
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
                    parts.append(f"reason:{parsed['explanation'][:100]}")  # Truncate long explanations
                response_text = " ".join(parts) if parts else "no_data"
            else:
                response_text = str(parsed)
        elif "raw_response" in response:
            response_text = str(response["raw_response"])
        else:
            response_text = str(response)
    elif isinstance(response, str):
        response_text = response
    else:
        response_text = str(response) if response else ""
    
    if not response_text:
        return ""
    
    # Convert to lowercase and strip whitespace
    normalized = response_text.lower().strip()
    
    # Remove extra whitespace
    normalized = ' '.join(normalized.split())
    
    return normalized

def extract_decision_and_confidence(response) -> Tuple[Optional[str], Optional[float]]:
    """Extract decision and confidence from response"""
    if not response:
        return None, None
    
    # Handle different response formats
    if isinstance(response, dict):
        # New API response format
        if "parsed" in response and response["parsed"]:
            parsed = response["parsed"]
            if isinstance(parsed, dict):
                # Extract from structured data
                classification = parsed.get("classification", "").lower()
                credit_score = parsed.get("credit_score")
                explanation = parsed.get("explanation", "").lower()
                
                # Map classification to decision (handles Good/Average/Poor from API)
                decision = None
                if classification in ["good", "approved", "approve"]:
                    decision = "good"
                elif classification in ["poor", "bad", "denied", "deny", "reject"]:
                    decision = "poor"
                elif classification in ["average", "moderate"]:
                    # Use credit score if available (API returns scores 0-100)
                    if credit_score is not None:
                        if credit_score >= 70:
                            decision = "good"  # High average treated as good
                        elif credit_score < 60:
                            decision = "poor"  # Low average treated as poor
                        else:
                            decision = "average"  # True average
                    else:
                        decision = "average"  # Default for average without score
                
                # Extract confidence from explanation or use improved score-based proxy
                confidence = None
                if explanation:
                    import re
                    confidence_matches = re.findall(r'(\d+(?:\.\d+)?)%', explanation)
                    if confidence_matches:
                        confidence = float(confidence_matches[0]) / 100.0
                    elif "high confidence" in explanation:
                        confidence = 0.9
                    elif "medium confidence" in explanation:
                        confidence = 0.7
                    elif "low confidence" in explanation:
                        confidence = 0.5
                
                # Use improved score-based confidence proxy if no explicit confidence
                if confidence is None and credit_score is not None:
                    confidence = calculate_confidence_from_score(credit_score)
                
                return decision, confidence
            else:
                # Parsed content is not a dict, treat as string
                response_text = str(parsed)
        else:
            # No parsed content, use raw response
            response_text = str(response.get("raw_response", response))
    else:
        response_text = str(response)
    
    # Fallback to text-based extraction
    text_lower = response_text.lower()
    
    # Extract decision (handles both legacy approve/deny and Good/Average/Poor classifications)
    decision = None
    if "good" in text_lower or "approve" in text_lower or "approved" in text_lower:
        decision = "good"
    elif "poor" in text_lower or "deny" in text_lower or "denied" in text_lower or "reject" in text_lower:
        decision = "poor"
    elif "average" in text_lower or "moderate" in text_lower:
        decision = "average"
    
    # Extract confidence (look for percentages)
    confidence = None
    try:
        import re
        confidence_matches = re.findall(r'(\d+(?:\.\d+)?)%', response_text)
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

def collect_consistency_responses(num_repeats: int = 3, delay_seconds: float = 1.0, sample_size: Optional[int] = 50):
    """
    Collect multiple responses for the same inputs to test consistency
    
    Args:
        num_repeats: Number of times to repeat each request
        delay_seconds: Delay between repeat requests
        sample_size: Maximum number of samples to test (default: 50)
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
    
    # Select samples for consistency testing - use configurable sample size for better statistical validity
    num_samples = min(sample_size, len(df)) if sample_size else len(df)
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
        response_texts = [normalize_response_text(r["response"]) for r in responses]
        normalized_responses = response_texts
        decisions = []
        confidences = []
        
        for r in responses:
            decision, confidence = extract_decision_and_confidence(r["response"])
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

def run_consistency_analysis(num_repeats: int = 3, delay_seconds: float = 1.0, sample_size: Optional[int] = 50):
    """
    Main function to run consistency analysis
    
    Args:
        num_repeats: Number of times to repeat each request (default: 3)
        delay_seconds: Delay between repeat requests (default: 1.0)
        sample_size: Maximum number of samples to test (default: 50, None for all data)
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
            consistency_data = collect_consistency_responses(num_repeats, delay_seconds, sample_size)
        
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
