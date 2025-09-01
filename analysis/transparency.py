# analysis/transparency.py

import pandas as pd
import json
import numpy as np
import os
import re
import time
from typing import Dict, List, Any, Tuple, Optional
from utils.logger import setup_logger
from api.client import send_request
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

logger = setup_logger("transparency", "results/logs/transparency.log")

# Reference to global status for progress updates
analysis_status = None
progress_start = 0
progress_range = 100

def set_status_reference(status_ref, start_progress=0, progress_span=100):
    """Set reference to global analysis status and progress range"""
    global analysis_status, progress_start, progress_range
    analysis_status = status_ref
    progress_start = start_progress
    progress_range = progress_span

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

class CreditProfilePerturbator:
    """Generate perturbed versions of credit profiles for LIME analysis"""
    
    def __init__(self, original_profile: Dict):
        self.original = original_profile.copy()
        self.feature_ranges = self._get_feature_ranges()
    
    def _get_feature_ranges(self) -> Dict:
        """Define perturbation ranges for different features"""
        return {
            'age': (18, 80),
            'income': (20000, 200000),
            'credit_score': (300, 850),
            'employment_length': (0, 40),
            'debt_to_income': (0.0, 1.0),
            'credit_utilization': (0.0, 1.0),
            'savings_account': (0, 100000),
            'housing_status': ['rent', 'own', 'mortgage'],
            'employment_status': ['employed', 'unemployed', 'self_employed', 'retired'],
            'loan_purpose': ['personal', 'auto', 'home', 'education', 'business']
        }
    
    def perturb(self, perturbation_strength: float = 0.2) -> Dict:
        """Create a perturbed version of the profile"""
        perturbed = self.original.copy()
        
        for feature, value in self.original.items():
            if feature in self.feature_ranges:
                if isinstance(self.feature_ranges[feature], tuple):
                    # Numerical feature
                    min_val, max_val = self.feature_ranges[feature]
                    if isinstance(value, (int, float)):
                        # Add gaussian noise
                        noise_std = (max_val - min_val) * perturbation_strength
                        new_val = value + np.random.normal(0, noise_std)
                        perturbed[feature] = max(min_val, min(max_val, new_val))
                elif isinstance(self.feature_ranges[feature], list):
                    # Categorical feature
                    if np.random.random() < perturbation_strength:
                        perturbed[feature] = np.random.choice(self.feature_ranges[feature])
        
        return perturbed

def calculate_profile_distance(profile1: Dict, profile2: Dict) -> float:
    """Calculate normalized distance between two profiles"""
    distances = []
    
    # Numerical features
    numerical_features = ['age', 'income', 'credit_score', 'employment_length', 
                         'debt_to_income', 'credit_utilization', 'savings_account']
    
    for feature in numerical_features:
        if feature in profile1 and feature in profile2:
            val1 = float(profile1[feature])
            val2 = float(profile2[feature])
            
            # Normalize by feature range
            if feature == 'age':
                norm_dist = abs(val1 - val2) / 62  # age range 18-80
            elif feature == 'income':
                norm_dist = abs(val1 - val2) / 180000  # income range
            elif feature == 'credit_score':
                norm_dist = abs(val1 - val2) / 550  # credit score range
            elif feature in ['debt_to_income', 'credit_utilization']:
                norm_dist = abs(val1 - val2)  # already 0-1
            else:
                norm_dist = abs(val1 - val2) / max(val1, val2, 1)
            
            distances.append(norm_dist)
    
    # Categorical features
    categorical_features = ['housing_status', 'employment_status', 'loan_purpose']
    for feature in categorical_features:
        if feature in profile1 and feature in profile2:
            distances.append(0 if profile1[feature] == profile2[feature] else 1)
    
    return np.sqrt(np.mean(np.array(distances) ** 2))

def vectorize_profile(profile: Dict) -> List[float]:
    """Convert profile to numerical vector for LIME model"""
    vector = []
    
    # Numerical features
    numerical_features = ['age', 'income', 'credit_score', 'employment_length', 
                         'debt_to_income', 'credit_utilization', 'savings_account']
    
    for feature in numerical_features:
        vector.append(float(profile.get(feature, 0)))
    
    # One-hot encode categorical features
    housing_map = {'rent': [1,0,0], 'own': [0,1,0], 'mortgage': [0,0,1]}
    employment_map = {'employed': [1,0,0,0], 'unemployed': [0,1,0,0], 
                     'self_employed': [0,0,1,0], 'retired': [0,0,0,1]}
    
    housing = profile.get('housing_status', 'rent')
    vector.extend(housing_map.get(housing, [0,0,0]))
    
    employment = profile.get('employment_status', 'employed')
    vector.extend(employment_map.get(employment, [0,0,0,0]))
    
    return vector

def extract_credit_score(api_response: Dict) -> float:
    """Extract credit score from API response"""
    try:
        if isinstance(api_response, dict):
            # Try different possible keys
            for key in ['credit_score', 'score', 'prediction', 'result']:
                if key in api_response:
                    return float(api_response[key])
            
            # Try nested structures
            if 'response' in api_response:
                return extract_credit_score(api_response['response'])
                
        return 650.0  # Default fallback
    except:
        return 650.0

def get_feature_names() -> List[str]:
    """Get ordered list of feature names for LIME model"""
    return [
        'age', 'income', 'credit_score', 'employment_length', 
        'debt_to_income', 'credit_utilization', 'savings_account',
        'housing_rent', 'housing_own', 'housing_mortgage',
        'employment_employed', 'employment_unemployed', 
        'employment_self_employed', 'employment_retired'
    ]

def generate_lime_explanation(profile: Dict, n_samples: int = 500, 
                             n_features: int = 10) -> Dict:
    """Generate LIME explanation for a credit scoring decision"""
    
    try:
        # Create feature perturbation generator
        perturbation_generator = CreditProfilePerturbator(profile)
        
        # Generate perturbed samples around the instance
        perturbed_samples = []
        similarity_weights = []
        
        for i in range(n_samples):
            # Create perturbed version of the profile
            perturbed_profile = perturbation_generator.perturb()
            
            # Get model prediction
            try:
                prediction = send_request(perturbed_profile)
                score = extract_credit_score(prediction)
            except:
                score = 650.0  # Default score if API fails
            
            # Calculate similarity weight (exponential kernel)
            distance = calculate_profile_distance(profile, perturbed_profile)
            weight = np.exp(-(distance ** 2) / (2 * 0.75 ** 2))  # RBF kernel
            
            perturbed_samples.append({
                'features': vectorize_profile(perturbed_profile),
                'score': score,
                'weight': weight
            })
            similarity_weights.append(weight)
        
        # Fit interpretable linear model with weighted samples
        X = np.array([sample['features'] for sample in perturbed_samples])
        y = np.array([sample['score'] for sample in perturbed_samples])
        weights = np.array(similarity_weights)
        
        # Weighted linear regression
        lime_model = LinearRegression()
        lime_model.fit(X, y, sample_weight=weights)
        
        # Calculate R² score
        y_pred = lime_model.predict(X)
        r2 = r2_score(y, y_pred, sample_weight=weights)
        
        # Extract feature importances
        feature_names = get_feature_names()
        coefficients = lime_model.coef_
        
        # Sort by absolute importance
        importance_pairs = list(zip(feature_names, coefficients))
        importance_pairs.sort(key=lambda x: abs(x[1]), reverse=True)
        
        top_features = importance_pairs[:n_features]
        
        # Get original prediction
        original_prediction = send_request(profile)
        
        return {
            'local_model_r2': r2,
            'feature_importance': dict(top_features),
            'top_positive_features': [(name, coef) for name, coef in top_features if coef > 0],
            'top_negative_features': [(name, coef) for name, coef in top_features if coef < 0],
            'original_prediction': original_prediction,
            'samples_generated': len(perturbed_samples),
            'mean_similarity_weight': np.mean(similarity_weights)
        }
        
    except Exception as e:
        logger.error(f"Error generating LIME explanation: {str(e)}")
        return {
            'error': str(e),
            'local_model_r2': 0.0,
            'feature_importance': {},
            'top_positive_features': [],
            'top_negative_features': [],
            'original_prediction': {},
            'samples_generated': 0,
            'mean_similarity_weight': 0.0
        }

def extract_explanation_text(api_response: Dict) -> str:
    """Extract explanation text from API response"""
    try:
        if isinstance(api_response, dict):
            # Try different possible keys for explanation
            for key in ['explanation', 'reasoning', 'rationale', 'justification', 'details']:
                if key in api_response:
                    return str(api_response[key])
            
            # Try nested structures
            if 'response' in api_response:
                return extract_explanation_text(api_response['response'])
            
            # Convert entire response to string if no explanation field found
            return json.dumps(api_response, indent=2)
            
        return str(api_response)
    except:
        return "No explanation available"

def build_canonical_facts(profile: Dict) -> Dict[str, Any]:
    """Build canonical fact table from profile"""
    facts = {}
    
    # Numerical facts
    numerical_fields = ['age', 'income', 'credit_score', 'employment_length', 
                       'debt_to_income', 'credit_utilization', 'savings_account']
    
    for field in numerical_fields:
        if field in profile:
            facts[field] = {
                'value': profile[field],
                'type': 'numerical',
                'mentioned': False
            }
    
    # Categorical facts
    categorical_fields = ['housing_status', 'employment_status', 'loan_purpose']
    
    for field in categorical_fields:
        if field in profile:
            facts[field] = {
                'value': profile[field],
                'type': 'categorical',
                'mentioned': False
            }
    
    return facts

def analyze_explanation_faithfulness(explanation_text: str, profile: Dict) -> Dict:
    """Analyze how faithful the explanation is to input facts"""
    
    canonical_facts = build_canonical_facts(profile)
    explanation_lower = explanation_text.lower()
    
    # Check for factual mentions
    mentioned_facts = 0
    total_facts = len(canonical_facts)
    factual_errors = []
    
    for fact_name, fact_data in canonical_facts.items():
        fact_value = fact_data['value']
        
        # Check if fact is mentioned
        if fact_name.replace('_', ' ') in explanation_lower:
            fact_data['mentioned'] = True
            mentioned_facts += 1
            
            # Check for value accuracy if numerical
            if fact_data['type'] == 'numerical':
                # Look for the actual value in explanation
                value_pattern = rf'\b{fact_value}\b'
                if not re.search(value_pattern, explanation_text):
                    # Check for approximate values (within 10%)
                    tolerance = abs(float(fact_value)) * 0.1
                    found_approx = False
                    
                    # Extract numbers from explanation
                    numbers = re.findall(r'\b\d+\.?\d*\b', explanation_text)
                    for num_str in numbers:
                        try:
                            num_val = float(num_str)
                            if abs(num_val - float(fact_value)) <= tolerance:
                                found_approx = True
                                break
                        except:
                            continue
                    
                    if not found_approx:
                        factual_errors.append(f"Mentioned {fact_name} but value {fact_value} not found")
    
    # Calculate faithfulness score
    mention_ratio = mentioned_facts / max(total_facts, 1)
    error_penalty = len(factual_errors) * 0.1
    faithfulness_score = max(0, mention_ratio - error_penalty)
    
    return {
        'faithfulness_score': faithfulness_score,
        'mentioned_facts_ratio': mention_ratio,
        'factual_errors': factual_errors,
        'canonical_facts': canonical_facts,
        'total_facts': total_facts,
        'mentioned_facts': mentioned_facts
    }

def extract_mentioned_features(explanation_text: str) -> Dict[str, str]:
    """Extract features mentioned in explanation text"""
    feature_mentions = {}
    
    # Feature detection patterns
    feature_patterns = {
        'income': r'income|salary|earnings',
        'age': r'\bage\b|years old',
        'credit_score': r'credit score|score|rating',
        'employment_status': r'employment|job|work|employed|unemployed',
        'debt_to_income': r'debt.to.income|DTI|debt ratio',
        'credit_utilization': r'utilization|balance|credit usage',
        'payment_history': r'payment|history|defaults|late payments',
        'housing_status': r'housing|rent|own|mortgage'
    }
    
    text_lower = explanation_text.lower()
    
    for feature, pattern in feature_patterns.items():
        if re.search(pattern, text_lower):
            # Extract context around the mention
            match = re.search(f'([^.]*{pattern}[^.]*)', text_lower)
            if match:
                feature_mentions[feature] = match.group(1).strip()
    
    return feature_mentions

def analyze_lime_alignment(explanation_text: str, lime_results: Dict) -> Dict:
    """Analyze alignment between explanation and LIME feature importance"""
    
    if 'error' in lime_results:
        return {
            'alignment_score': 0.0,
            'coverage_score': 0.0,
            'direction_agreement': 0.0,
            'error': 'LIME analysis failed'
        }
    
    mentioned_features = extract_mentioned_features(explanation_text)
    lime_importance = lime_results.get('feature_importance', {})
    
    if not lime_importance:
        return {
            'alignment_score': 0.0,
            'coverage_score': 0.0,
            'direction_agreement': 0.0,
            'error': 'No LIME importance available'
        }
    
    # Get top LIME features
    top_lime_features = sorted(lime_importance.items(), 
                              key=lambda x: abs(x[1]), reverse=True)[:5]
    
    # Calculate coverage (how many top LIME features are mentioned)
    covered_features = 0
    for feature_name, importance in top_lime_features:
        if any(feature_name.replace('_', ' ') in mention.lower() 
               for mention in mentioned_features.values()):
            covered_features += 1
    
    coverage_score = covered_features / max(len(top_lime_features), 1)
    
    # Calculate direction agreement
    direction_agreements = 0
    total_directional_mentions = 0
    
    for feature_name, importance in top_lime_features:
        feature_context = None
        for mention_key, mention_text in mentioned_features.items():
            if feature_name.replace('_', ' ') in mention_text.lower():
                feature_context = mention_text
                break
        
        if feature_context:
            total_directional_mentions += 1
            
            # Check if direction matches
            is_positive_lime = importance > 0
            has_positive_language = any(word in feature_context.lower() 
                                     for word in ['increase', 'improve', 'boost', 'higher', 'better'])
            has_negative_language = any(word in feature_context.lower() 
                                      for word in ['decrease', 'reduce', 'lower', 'worse', 'hurt'])
            
            if (is_positive_lime and has_positive_language) or \
               (not is_positive_lime and has_negative_language):
                direction_agreements += 1
    
    direction_agreement = direction_agreements / max(total_directional_mentions, 1)
    
    # Overall alignment score
    alignment_score = (coverage_score + direction_agreement) / 2
    
    return {
        'alignment_score': alignment_score,
        'coverage_score': coverage_score,
        'direction_agreement': direction_agreement,
        'mentioned_features': mentioned_features,
        'top_lime_features': dict(top_lime_features),
        'covered_features': covered_features,
        'total_lime_features': len(top_lime_features)
    }

def count_actual_values(text: str) -> int:
    """Count mentions of actual numerical values"""
    # Look for patterns like "your income of $45,000" or "credit score is 720"
    patterns = [
        r'\$[\d,]+',  # Dollar amounts
        r'\b\d{3,4}\b',  # 3-4 digit numbers (likely scores/ages)
        r'\b\d+\.\d+%',  # Percentages
        r'\b\d+%',  # Percentages without decimal
    ]
    
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text))
    
    return count

def count_threshold_mentions(text: str) -> int:
    """Count mentions of thresholds or criteria"""
    threshold_patterns = [
        r'above \d+|below \d+|over \d+|under \d+',
        r'threshold|criteria|requirement|minimum|maximum',
        r'at least \d+|no more than \d+'
    ]
    
    count = 0
    text_lower = text.lower()
    for pattern in threshold_patterns:
        count += len(re.findall(pattern, text_lower))
    
    return count

def count_feature_interactions(text: str) -> int:
    """Count mentions of feature interactions"""
    interaction_patterns = [
        r'combined with|along with|together with',
        r'ratio|compared to|relative to',
        r'given your|considering your|because of your'
    ]
    
    count = 0
    text_lower = text.lower()
    for pattern in interaction_patterns:
        count += len(re.findall(pattern, text_lower))
    
    return count

def count_actionable_advice(text: str) -> int:
    """Count actionable advice pieces in explanation"""
    actionable_patterns = [
        r'reduce.*below|increase.*above|maintain.*under',
        r'pay.*on time|avoid.*late payments',
        r'lower.*utilization|decrease.*balance',
        r'consider.*consolidation|refinance',
        r'improve.*history|build.*credit'
    ]
    
    count = 0
    text_lower = text.lower()
    
    for pattern in actionable_patterns:
        if re.search(pattern, text_lower):
            count += 1
    
    return count

def analyze_specificity_actionability(explanation_text: str) -> Dict:
    """Analyze how specific and actionable the explanation is"""
    specificity_signals = {
        'actual_values': count_actual_values(explanation_text),
        'thresholds_mentioned': count_threshold_mentions(explanation_text),
        'feature_interactions': count_feature_interactions(explanation_text),
        'actionable_advice': count_actionable_advice(explanation_text)
    }
    
    # Calculate specificity score (0-5 scale)
    score = 0
    
    # Points for actual values/thresholds (up to 2 points)
    value_mentions = specificity_signals['actual_values'] + specificity_signals['thresholds_mentioned']
    score += min(2, value_mentions * 0.5)
    
    # Points for feature interactions (up to 1 point)
    score += min(1, specificity_signals['feature_interactions'] * 0.5)
    
    # Points for actionable advice (up to 2 points)
    score += min(2, specificity_signals['actionable_advice'])
    
    # Determine category
    if score <= 1:
        category = "vague_boilerplate"
    elif score <= 3:
        category = "somewhat_specific"
    else:
        category = "highly_specific"
    
    return {
        'specificity_score': score,
        'category': category,
        'signals': specificity_signals,
        'normalized_score': score / 5.0,  # 0-1 scale
        'flags': {
            'too_vague': score <= 2,
            'no_actionable_advice': specificity_signals['actionable_advice'] == 0
        }
    }

def analyze_explanation_completeness(explanation_text: str, lime_results: Dict, 
                                   importance_threshold: float = 0.1) -> Dict:
    """Analyze completeness of explanation coverage"""
    
    if 'error' in lime_results:
        return {
            'completeness_score': 0.0,
            'important_features_covered': 0,
            'total_important_features': 0,
            'error': 'LIME analysis failed'
        }
    
    lime_importance = lime_results.get('feature_importance', {})
    mentioned_features = extract_mentioned_features(explanation_text)
    
    # Find important features (above threshold)
    important_features = [name for name, importance in lime_importance.items() 
                         if abs(importance) >= importance_threshold]
    
    # Check coverage of important features
    covered_important = 0
    for feature in important_features:
        if any(feature.replace('_', ' ') in mention.lower() 
               for mention in mentioned_features.values()):
            covered_important += 1
    
    completeness_score = covered_important / max(len(important_features), 1)
    
    return {
        'completeness_score': completeness_score,
        'important_features_covered': covered_important,
        'total_important_features': len(important_features),
        'important_features': important_features,
        'coverage_ratio': completeness_score
    }

def analyze_explanation_consistency(profile: Dict, num_samples: int = 3) -> Dict:
    """Analyze consistency of explanations across repeated calls"""
    
    explanations = []
    
    # Get multiple explanations for the same profile
    for i in range(num_samples):
        try:
            response = send_request(profile)
            explanation = extract_explanation_text(response)
            explanations.append(explanation)
            time.sleep(0.5)  # Brief delay between requests
        except:
            explanations.append("Error getting explanation")
    
    # Analyze similarity between explanations
    if len(explanations) < 2:
        return {
            'consistency_score': 0.0,
            'explanations': explanations,
            'error': 'Insufficient explanations for consistency analysis'
        }
    
    # Extract features mentioned in each explanation
    feature_sets = []
    for explanation in explanations:
        features = set(extract_mentioned_features(explanation).keys())
        feature_sets.append(features)
    
    # Calculate feature overlap
    if len(feature_sets) >= 2:
        intersection = set.intersection(*feature_sets)
        union = set.union(*feature_sets)
        overlap_score = len(intersection) / max(len(union), 1)
    else:
        overlap_score = 0.0
    
    # Calculate text similarity (simple word overlap)
    all_words = []
    for explanation in explanations:
        words = set(explanation.lower().split())
        all_words.append(words)
    
    if len(all_words) >= 2:
        word_intersection = set.intersection(*all_words)
        word_union = set.union(*all_words)
        word_similarity = len(word_intersection) / max(len(word_union), 1)
    else:
        word_similarity = 0.0
    
    consistency_score = (overlap_score + word_similarity) / 2
    
    return {
        'consistency_score': consistency_score,
        'feature_overlap_score': overlap_score,
        'word_similarity_score': word_similarity,
        'explanations': explanations,
        'num_samples': len(explanations)
    }

def analyze_counterfactual_sensitivity(profile: Dict, features_to_test: List[str] = None) -> Dict:
    """Analyze how explanations change when key features are modified"""
    
    if features_to_test is None:
        features_to_test = ['income', 'age', 'employment_status']
    
    # Get baseline explanation
    try:
        baseline_response = send_request(profile)
        baseline_explanation = extract_explanation_text(baseline_response)
    except:
        return {
            'sensitivity_score': 0.0,
            'error': 'Could not get baseline explanation'
        }
    
    sensitive_changes = 0
    total_tests = 0
    
    for feature in features_to_test:
        if feature not in profile:
            continue
            
        # Create modified profile
        modified_profile = profile.copy()
        
        if feature == 'income':
            # Increase income by 50%
            modified_profile[feature] = float(profile[feature]) * 1.5
        elif feature == 'age':
            # Increase age by 10 years
            modified_profile[feature] = min(80, int(profile[feature]) + 10)
        elif feature == 'employment_status':
            # Change employment status
            current = profile[feature]
            if current == 'employed':
                modified_profile[feature] = 'unemployed'
            else:
                modified_profile[feature] = 'employed'
        
        # Get explanation for modified profile
        try:
            modified_response = send_request(modified_profile)
            modified_explanation = extract_explanation_text(modified_response)
            
            # Check if explanation changed meaningfully
            baseline_features = set(extract_mentioned_features(baseline_explanation).keys())
            modified_features = set(extract_mentioned_features(modified_explanation).keys())
            
            # Consider it sensitive if feature mentions changed
            if baseline_features != modified_features:
                sensitive_changes += 1
            
            total_tests += 1
            time.sleep(0.5)  # Brief delay
            
        except:
            continue
    
    sensitivity_score = sensitive_changes / max(total_tests, 1)
    
    return {
        'sensitivity_score': sensitivity_score,
        'sensitive_changes': sensitive_changes,
        'total_tests': total_tests,
        'features_tested': features_to_test[:total_tests]
    }

def analyze_compliance_safety(explanation_text: str) -> Dict:
    """Analyze compliance and safety of explanation"""
    
    # Protected attributes that should not be mentioned
    protected_patterns = [
        r'\brace\b|\bethnic|\bnational',
        r'\bgender\b|\bmale\b|\bfemale\b',
        r'\breligion\b|\bchristian\b|\bmuslim\b|\bjewish\b',
        r'\bmarriage\b|\bmarried\b|\bsingle\b|\bdivorced\b',
        r'\bdisabilit\b|\bhandicap\b'
    ]
    
    # Harmful advice patterns
    harmful_patterns = [
        r'lie about|falsify|hide',
        r'discriminat|bias|unfair',
        r'illegal|unlawful'
    ]
    
    text_lower = explanation_text.lower()
    
    # Check for protected attribute mentions
    protected_violations = []
    for pattern in protected_patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            protected_violations.extend(matches)
    
    # Check for harmful advice
    harmful_violations = []
    for pattern in harmful_patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            harmful_violations.extend(matches)
    
    # Compliance score
    total_violations = len(protected_violations) + len(harmful_violations)
    compliant = total_violations == 0
    
    return {
        'compliant': compliant,
        'protected_violations': protected_violations,
        'harmful_violations': harmful_violations,
        'total_violations': total_violations,
        'compliance_score': 1.0 if compliant else 0.0
    }

def analyze_structure_readability(explanation_text: str) -> Dict:
    """Analyze structure and readability of explanation"""
    
    # Basic readability metrics
    sentences = explanation_text.split('.')
    words = explanation_text.split()
    
    avg_sentence_length = len(words) / max(len(sentences), 1)
    
    # Structure signals
    has_paragraphs = '\n' in explanation_text
    has_bullet_points = any(marker in explanation_text for marker in ['•', '-', '*'])
    has_numbers = bool(re.search(r'\d', explanation_text))
    
    # Readability score (0-1)
    readability_score = 0.5  # Base score
    
    # Adjust for sentence length
    if 10 <= avg_sentence_length <= 20:
        readability_score += 0.2
    elif avg_sentence_length > 30:
        readability_score -= 0.2
    
    # Adjust for structure
    if has_paragraphs:
        readability_score += 0.1
    if has_bullet_points:
        readability_score += 0.1
    if has_numbers:
        readability_score += 0.1
    
    readability_score = max(0, min(1, readability_score))
    
    return {
        'readability_score': readability_score,
        'avg_sentence_length': avg_sentence_length,
        'word_count': len(words),
        'sentence_count': len(sentences),
        'structure_signals': {
            'has_paragraphs': has_paragraphs,
            'has_bullet_points': has_bullet_points,
            'has_numbers': has_numbers
        }
    }

def calculate_explanation_quality_score(analysis_results: Dict) -> Dict:
    """Calculate aggregate explanation quality score"""
    
    # Weight configuration (must sum to 100)
    weights = {
        'faithfulness': 25,
        'lime_alignment': 25,
        'specificity': 15,
        'completeness': 15,
        'consistency': 10,
        'counterfactual': 5,
        'readability': 5
    }
    
    # Extract scores
    scores = {
        'faithfulness': analysis_results.get('faithfulness', {}).get('faithfulness_score', 0),
        'lime_alignment': analysis_results.get('lime_alignment', {}).get('alignment_score', 0),
        'specificity': analysis_results.get('specificity', {}).get('normalized_score', 0),
        'completeness': analysis_results.get('completeness', {}).get('completeness_score', 0),
        'consistency': analysis_results.get('consistency', {}).get('consistency_score', 0),
        'counterfactual': analysis_results.get('counterfactual', {}).get('sensitivity_score', 0),
        'readability': analysis_results.get('readability', {}).get('readability_score', 0)
    }
    
    # Calculate weighted score
    weighted_score = sum(scores[dim] * weights[dim] for dim in weights.keys())
    
    # Check compliance gate
    compliance_result = analysis_results.get('compliance', {})
    is_compliant = compliance_result.get('compliant', True)
    
    # Apply compliance gate (cap to 20 if not compliant)
    if not is_compliant:
        weighted_score = min(weighted_score, 20)
    
    # Determine quality category
    if weighted_score >= 90:
        category = "excellent"
    elif weighted_score >= 80:
        category = "good"
    elif weighted_score >= 70:
        category = "fair"
    else:
        category = "poor"
    
    return {
        'overall_score': weighted_score,
        'category': category,
        'dimension_scores': scores,
        'weights': weights,
        'compliance_gate_applied': not is_compliant,
        'is_compliant': is_compliant
    }

def collect_transparency_responses(sample_size: int = 50) -> List[Dict]:
    """Collect API responses for transparency analysis"""
    
    logger.info(f"Starting transparency response collection with sample size: {sample_size}")
    
    # Check for cached responses
    cache_path = "results/responses/transparency.jsonl"
    if os.path.exists(cache_path):
        try:
            cached_responses = load_jsonl(cache_path)
            if len(cached_responses) >= sample_size:
                logger.info(f"Using {len(cached_responses)} cached transparency responses")
                return cached_responses[:sample_size]
        except Exception as e:
            logger.warning(f"Could not load cached responses: {e}")
    
    # Load test data
    test_data_path = "data/testdata.csv"
    try:
        df = pd.read_csv(test_data_path)
        logger.info(f"Loaded {len(df)} test profiles from {test_data_path}")
    except FileNotFoundError:
        logger.error(f"Test data file not found: {test_data_path}")
        return []
    
    # Sample profiles
    sample_profiles = df.sample(n=min(sample_size, len(df)), random_state=42)
    
    responses = []
    total_profiles = len(sample_profiles)
    
    for i, (idx, profile) in enumerate(sample_profiles.iterrows()):
        if analysis_status:
            progress = progress_start + int((i / total_profiles) * progress_range * 0.7)  # 70% for collection
            analysis_status["progress"] = progress
            analysis_status["message"] = f"Collecting transparency responses... ({i+1}/{total_profiles})"
        
        profile_dict = profile.to_dict()
        
        try:
            # Get API response
            api_response = send_request(profile_dict)
            
            response_record = {
                'profile': profile_dict,
                'api_response': api_response,
                'explanation_text': extract_explanation_text(api_response),
                'timestamp': time.time()
            }
            
            responses.append(response_record)
            
        except Exception as e:
            logger.error(f"Error getting response for profile {i}: {str(e)}")
            continue
    
    # Save responses to cache
    try:
        save_jsonl(responses, cache_path)
        logger.info(f"Saved {len(responses)} transparency responses to cache")
    except Exception as e:
        logger.warning(f"Could not save responses to cache: {e}")
    
    return responses

def run_transparency_analysis(sample_size: int = 50) -> Dict:
    """Main transparency analysis pipeline"""
    
    logger.info("Starting transparency analysis")
    
    try:
        # Collect responses
        responses = collect_transparency_responses(sample_size)
        
        if not responses:
            return {
                'error': 'No responses collected for transparency analysis',
                'summary': {'total_responses': 0}
            }
        
        transparency_results = []
        total_responses = len(responses)
        
        for i, response_record in enumerate(responses):
            if analysis_status:
                # Analysis phase takes 30% of progress range
                progress = progress_start + int(0.7 * progress_range + (i / total_responses) * 0.3 * progress_range)
                analysis_status["progress"] = progress
                analysis_status["message"] = f"Analyzing transparency... ({i+1}/{total_responses})"
            
            profile = response_record['profile']
            api_response = response_record['api_response']
            explanation_text = response_record['explanation_text']
            
            # Generate LIME explanation
            lime_results = generate_lime_explanation(profile, n_samples=200)  # Smaller sample for speed
            
            # Run 8-dimensional analysis
            analysis_results = {
                'faithfulness': analyze_explanation_faithfulness(explanation_text, profile),
                'lime_alignment': analyze_lime_alignment(explanation_text, lime_results),
                'specificity': analyze_specificity_actionability(explanation_text),
                'completeness': analyze_explanation_completeness(explanation_text, lime_results),
                'consistency': analyze_explanation_consistency(profile, num_samples=2),  # Reduced for speed
                'counterfactual': analyze_counterfactual_sensitivity(profile, ['income', 'age']),  # Reduced features
                'compliance': analyze_compliance_safety(explanation_text),
                'readability': analyze_structure_readability(explanation_text)
            }
            
            # Calculate aggregate quality score
            quality_results = calculate_explanation_quality_score(analysis_results)
            
            transparency_record = {
                'profile': profile,
                'api_response': api_response,
                'explanation_text': explanation_text,
                'lime_results': lime_results,
                'analysis_results': analysis_results,
                'quality_score': quality_results['overall_score'],
                'quality_category': quality_results['category'],
                'is_compliant': quality_results['is_compliant'],
                'quality_details': quality_results
            }
            
            transparency_results.append(transparency_record)
        
        # Aggregate analysis
        aggregate_results = analyze_aggregate_transparency_results(transparency_results)
        
        return {
            'summary': aggregate_results,
            'detailed_results': transparency_results,
            'total_responses': len(transparency_results)
        }
        
    except Exception as e:
        logger.error(f"Error in transparency analysis: {str(e)}")
        return {
            'error': str(e),
            'summary': {'total_responses': 0}
        }

def analyze_aggregate_transparency_results(transparency_results: List[Dict]) -> Dict:
    """Analyze aggregate transparency results"""
    
    if not transparency_results:
        return {'total_analyzed': 0}
    
    # Extract scores and categories
    quality_scores = [r['quality_score'] for r in transparency_results]
    categories = [r['quality_category'] for r in transparency_results]
    compliance_flags = [r['is_compliant'] for r in transparency_results]
    
    # Calculate summary statistics
    summary = {
        'total_analyzed': len(transparency_results),
        'average_quality_score': np.mean(quality_scores),
        'median_quality_score': np.median(quality_scores),
        'std_quality_score': np.std(quality_scores),
        'min_quality_score': np.min(quality_scores),
        'max_quality_score': np.max(quality_scores),
        'compliance_rate': np.mean(compliance_flags),
        'total_compliant': sum(compliance_flags),
        'total_non_compliant': len(compliance_flags) - sum(compliance_flags)
    }
    
    # Category distribution
    category_counts = {}
    for category in ['excellent', 'good', 'fair', 'poor']:
        category_counts[category] = categories.count(category)
    
    summary['category_distribution'] = category_counts
    
    # Dimension analysis
    dimension_scores = {
        'faithfulness': [],
        'lime_alignment': [],
        'specificity': [],
        'completeness': [],
        'consistency': [],
        'counterfactual': [],
        'readability': []
    }
    
    for result in transparency_results:
        quality_details = result.get('quality_details', {})
        dimension_scores_dict = quality_details.get('dimension_scores', {})
        
        for dim in dimension_scores.keys():
            if dim in dimension_scores_dict:
                dimension_scores[dim].append(dimension_scores_dict[dim])
    
    # Calculate dimension averages
    dimension_averages = {}
    for dim, scores in dimension_scores.items():
        if scores:
            dimension_averages[dim] = {
                'average': np.mean(scores),
                'std': np.std(scores),
                'min': np.min(scores),
                'max': np.max(scores)
            }
    
    summary['dimension_analysis'] = dimension_averages
    
    # LIME analysis summary
    lime_r2_scores = []
    for result in transparency_results:
        lime_results = result.get('lime_results', {})
        if 'local_model_r2' in lime_results:
            lime_r2_scores.append(lime_results['local_model_r2'])
    
    if lime_r2_scores:
        summary['lime_quality'] = {
            'average_r2': np.mean(lime_r2_scores),
            'median_r2': np.median(lime_r2_scores),
            'std_r2': np.std(lime_r2_scores)
        }
    
    # Quality recommendations
    recommendations = []
    
    if summary['average_quality_score'] < 70:
        recommendations.append("Overall transparency quality is poor - significant improvements needed")
    elif summary['average_quality_score'] < 80:
        recommendations.append("Transparency quality is fair - moderate improvements recommended")
    
    if summary['compliance_rate'] < 1.0:
        recommendations.append(f"Compliance issues detected in {summary['total_non_compliant']} explanations")
    
    # Dimension-specific recommendations
    for dim, stats in dimension_averages.items():
        if stats['average'] < 0.6:
            if dim == 'faithfulness':
                recommendations.append("Explanations often lack grounding in actual input values")
            elif dim == 'lime_alignment':
                recommendations.append("Explanations poorly aligned with feature importance")
            elif dim == 'specificity':
                recommendations.append("Explanations are too vague - need more specific details")
            elif dim == 'completeness':
                recommendations.append("Explanations miss important factors identified by LIME")
            elif dim == 'consistency':
                recommendations.append("Explanations lack consistency across repeated calls")
    
    summary['recommendations'] = recommendations
    
    return summary