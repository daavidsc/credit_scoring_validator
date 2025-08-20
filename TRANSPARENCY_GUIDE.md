# Transparency Analysis - Implementation Guide

## Overview

The transparency analysis feature evaluates how interpretable and explainable the credit scoring model's decisions are through LIME analysis and comprehensive explanation quality assessment. This analysis ensures that model decisions can be understood, validated, and audited for regulatory compliance and stakeholder trust.

## What is Transparency Analysis?

Transparency analysis assesses the explainability and interpretability of machine learning models through systematic evaluation of their explanations. For credit scoring models, this is essential because:

- **Regulatory Requirements**: GDPR Article 22, FCRA, and ECOA require explainable AI for financial decisions
- **Customer Rights**: Applicants have the right to understand credit decisions
- **Risk Management**: Understanding model logic helps identify potential risks and biases
- **Model Validation**: Transparent models are easier to validate and audit
- **Business Trust**: Stakeholders need to understand and trust automated decisions

## Transparency Analysis: Technical Deep Dive

### LIME (Local Interpretable Model-agnostic Explanations) Framework

LIME creates locally faithful interpretable explanations by learning an interpretable model locally around the prediction:

**1. Core LIME Implementation**
```python
def generate_lime_explanation(profile: Dict, api_client, n_samples: int = 1000, 
                             n_features: int = 10) -> Dict:
    """
    Generate LIME explanation for a credit scoring decision
    
    Args:
        profile: Input credit profile
        api_client: Credit scoring API client
        n_samples: Number of perturbed samples for local model
        n_features: Number of top features to include in explanation
    """
    # Create feature perturbation generator
    perturbation_generator = CreditProfilePerturbator(profile)
    
    # Generate perturbed samples around the instance
    perturbed_samples = []
    similarity_weights = []
    
    for _ in range(n_samples):
        # Create perturbed version of the profile
        perturbed_profile = perturbation_generator.perturb()
        
        # Get model prediction
        prediction = api_client.predict(perturbed_profile)
        score = extract_credit_score(prediction)
        
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
    lime_model = WeightedLinearRegression()
    lime_model.fit(X, y, sample_weight=weights)
    
    # Extract feature importances
    feature_names = get_feature_names()
    coefficients = lime_model.coef_
    
    # Sort by absolute importance
    importance_pairs = list(zip(feature_names, coefficients))
    importance_pairs.sort(key=lambda x: abs(x[1]), reverse=True)
    
    top_features = importance_pairs[:n_features]
    
    return {
        'local_model_r2': lime_model.score(X, y, sample_weight=weights),
        'feature_importance': dict(top_features),
        'top_positive_features': [(name, coef) for name, coef in top_features if coef > 0],
        'top_negative_features': [(name, coef) for name, coef in top_features if coef < 0],
        'original_prediction': api_client.predict(profile),
        'explanation_fidelity': calculate_explanation_fidelity(lime_model, profile)
    }
```

### Explanation Text Analysis Framework

**Comprehensive 8-Dimensional Analysis:**

1. **Faithfulness to Inputs (Groundedness)** - 25% weight
2. **LIME Alignment (Coverage + Direction)** - 25% weight  
3. **Specificity & Actionability** - 15% weight
4. **Completeness** - 15% weight
5. **Consistency (Stability)** - 10% weight
6. **Counterfactual Sensitivity** - 5% weight
7. **Compliance & Safety** - Gate (fail → cap to 20)
8. **Structure & Readability** - 5% weight

**Final Score Calculation:**
```
Score = 25*faithfulness + 25*lime_alignment + 15*specificity + 15*completeness + 10*stability + 5*counterfactual + 5*readability
If compliance fails → cap score to 20
```

### Integration Pipeline

```python
def run_transparency_analysis(sample_size: int = 50):
    """Main transparency analysis pipeline"""
    
    # Load test data
    df = pd.read_csv("data/testdata.csv")
    sample_profiles = df.sample(n=sample_size, random_state=42)
    
    transparency_results = []
    
    for idx, profile in sample_profiles.iterrows():
        profile_dict = profile.to_dict()
        
        # Get API response with explanation
        api_response = send_request(profile_dict)
        explanation_text = extract_explanation_text(api_response)
        
        # Generate LIME explanation
        lime_results = generate_lime_explanation(profile_dict, api_client)
        
        # Run 8-dimensional analysis
        analysis_results = {
            'faithfulness': analyze_explanation_faithfulness(explanation_text, profile_dict),
            'lime_alignment': analyze_lime_alignment(explanation_text, lime_results),
            'specificity': analyze_specificity_actionability(explanation_text),
            'completeness': analyze_explanation_completeness(explanation_text, lime_results),
            'consistency': analyze_explanation_consistency(profile_dict, api_client),
            'counterfactual': analyze_counterfactual_sensitivity(profile_dict, api_client, 
                                                               ['income', 'age', 'employment_status']),
            'compliance': analyze_compliance_safety(explanation_text),
            'readability': analyze_structure_readability(explanation_text)
        }
        
        # Calculate aggregate quality score
        quality_score = calculate_explanation_quality_score(analysis_results)
        
        transparency_record = {
            'profile': profile_dict,
            'api_response': api_response,
            'explanation_text': explanation_text,
            'lime_results': lime_results,
            'analysis_results': analysis_results,
            'quality_score': quality_score
        }
        
        transparency_results.append(transparency_record)
    
    return analyze_aggregate_transparency_results(transparency_results)
```

## How It Works

### 1. LIME-Based Feature Importance Analysis

The system generates local explanations using LIME for each credit decision:

- **Profile Perturbation**: Creates 1000+ variations of input profiles around each decision
- **Local Model Training**: Fits interpretable linear models to approximate local behavior
- **Feature Ranking**: Identifies top positive and negative drivers for each decision
- **Explanation Validation**: Measures local model fidelity and explanation quality

### 2. Comprehensive Explanation Text Analysis

For each explanation provided by the credit scoring API:

- **Fact Extraction**: Builds canonical fact tables from input profiles
- **Claim Analysis**: Extracts and verifies factual claims in explanations
- **Feature Alignment**: Compares mentioned features with LIME importance rankings
- **Quality Assessment**: Evaluates specificity, completeness, and actionability

### 3. Multi-Dimensional Quality Scoring

**8-Dimensional Analysis Framework:**
1. **Faithfulness** (25%): Groundedness to input facts
2. **LIME Alignment** (25%): Agreement with feature importance
3. **Specificity** (15%): Concrete values and actionable advice
4. **Completeness** (15%): Coverage of important drivers
5. **Stability** (10%): Consistency across repeated calls
6. **Counterfactual Sensitivity** (5%): Appropriate response to changes
7. **Compliance** (Gate): Legal and safety requirements
8. **Readability** (5%): Structure and clarity

### 4. Compliance and Safety Monitoring

**Automated Compliance Checking:**
- Protected attribute detection
- Sensitive inference identification
- Harmful advice prevention
- Regulatory requirement validation

## Quality Score Interpretation

**Excellent (90-100)**: Production-ready explanations
- High faithfulness and LIME alignment
- Specific and actionable
- Fully compliant and consistent

**Good (80-89)**: Acceptable quality with minor issues
- Generally faithful and aligned
- Mostly specific with some actionable advice
- Compliant with good consistency

**Fair (70-79)**: Needs improvement
- Some faithfulness or alignment issues
- Vague or incomplete explanations
- Minor compliance concerns

**Poor (<70)**: Not production-ready
- Major faithfulness or compliance issues
- Vague, inconsistent, or incomplete
- Significant improvement required

## Best Practices

### Production Deployment
- Target quality score ≥ 80 for production use
- Monitor daily for compliance violations
- Set up alerts for score degradation
- Regular review of explanation patterns

### Model Development
- Design APIs to provide structured explanations
- Include confidence scores and feature attributions
- Ensure deterministic explanation generation
- Test explanations across diverse demographics

### Compliance Management
- Regular audit of explanation content
- Training on protected attribute avoidance
- Documentation of explanation methodology
- Monitoring for regulatory requirement changes

This comprehensive transparency analysis ensures that credit scoring models not only make accurate decisions but can explain those decisions in a faithful, complete, consistent, and legally compliant manner.

## Overview

The transparency analysis feature evaluates how interpretable and explainable the credit scoring model's decisions are through LIME analysis and comprehensive explanation quality assessment. This analysis ensures that model decisions can be understood, validated, and audited for regulatory compliance and stakeholder trust.

## What is Transparency Analysis?

Transparency analysis assesses the explainability and interpretability of machine learning models through systematic evaluation of their explanations. For credit scoring models, this is essential because:

- **Regulatory Requirements**: GDPR Article 22, FCRA, and ECOA require explainable AI for financial decisions
- **Customer Rights**: Applicants have the right to understand credit decisions
- **Risk Management**: Understanding model logic helps identify potential risks and biases
- **Model Validation**: Transparent models are easier to validate and audit
- **Business Trust**: Stakeholders need to understand and trust automated decisions

## Transparency Analysis: Technical Deep Dive

### LIME (Local Interpretable Model-agnostic Explanations) Framework

LIME creates locally faithful interpretable explanations by learning an interpretable model locally around the prediction:

**1. Core LIME Implementation**
```python
def generate_lime_explanation(profile: Dict, api_client, n_samples: int = 1000, 
                             n_features: int = 10) -> Dict:
    """
    Generate LIME explanation for a credit scoring decision
    
    Args:
        profile: Input credit profile
        api_client: Credit scoring API client
        n_samples: Number of perturbed samples for local model
        n_features: Number of top features to include in explanation
    """
    # Create feature perturbation generator
    perturbation_generator = CreditProfilePerturbator(profile)
    
    # Generate perturbed samples around the instance
    perturbed_samples = []
    similarity_weights = []
    
    for _ in range(n_samples):
        # Create perturbed version of the profile
        perturbed_profile = perturbation_generator.perturb()
        
        # Get model prediction
        prediction = api_client.predict(perturbed_profile)
        score = extract_credit_score(prediction)
        
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
    lime_model = WeightedLinearRegression()
    lime_model.fit(X, y, sample_weight=weights)
    
    # Extract feature importances
    feature_names = get_feature_names()
    coefficients = lime_model.coef_
    
    # Sort by absolute importance
    importance_pairs = list(zip(feature_names, coefficients))
    importance_pairs.sort(key=lambda x: abs(x[1]), reverse=True)
    
    top_features = importance_pairs[:n_features]
    
    return {
        'local_model_r2': lime_model.score(X, y, sample_weight=weights),
        'feature_importance': dict(top_features),
        'top_positive_features': [(name, coef) for name, coef in top_features if coef > 0],
        'top_negative_features': [(name, coef) for name, coef in top_features if coef < 0],
        'original_prediction': api_client.predict(profile),
        'explanation_fidelity': calculate_explanation_fidelity(lime_model, profile)
    }

class CreditProfilePerturbator:
    """Handles intelligent perturbation of credit profiles for LIME"""
    
    def __init__(self, original_profile: Dict):
        self.original = original_profile
        self.categorical_features = ['employment_status', 'housing_status', 'education_level']
        self.numerical_features = ['age', 'income', 'credit_limit', 'used_credit']
        
    def perturb(self) -> Dict:
        """Create a perturbed version of the profile"""
        perturbed = self.original.copy()
        
        # Perturb numerical features with Gaussian noise
        for feature in self.numerical_features:
            if feature in perturbed:
                original_value = perturbed[feature]
                # Add noise proportional to the value (5-15% variation)
                noise_factor = np.random.uniform(0.05, 0.15)
                noise = np.random.normal(0, original_value * noise_factor)
                perturbed[feature] = max(0, original_value + noise)
        
        # Perturb categorical features by random selection
        for feature in self.categorical_features:
            if feature in perturbed and np.random.random() < 0.3:  # 30% chance to change
                possible_values = get_categorical_values(feature)
                perturbed[feature] = np.random.choice(possible_values)
        
        return perturbed
```

### Explanation Text Analysis Framework

**1. Faithfulness to Inputs (Groundedness)**
```python
def analyze_explanation_faithfulness(explanation_text: str, input_profile: Dict) -> Dict:
    """
    Analyze how well explanation sticks to facts present in input
    """
    # Build canonical fact table from input
    fact_table = build_fact_table(input_profile)
    
    # Extract claims from explanation text
    extracted_claims = extract_claims_from_explanation(explanation_text)
    
    # Categorize each claim
    claim_analysis = {
        'supported': [],
        'contradicted': [],
        'not_in_input': [],
        'hallucinated': []
    }
    
    for claim in extracted_claims:
        verification_result = verify_claim_against_facts(claim, fact_table)
        
        if verification_result['status'] == 'supported':
            claim_analysis['supported'].append(claim)
        elif verification_result['status'] == 'contradicted':
            claim_analysis['contradicted'].append(claim)
        elif verification_result['status'] == 'new_fact':
            claim_analysis['hallucinated'].append(claim)
        else:
            claim_analysis['not_in_input'].append(claim)
    
    # Calculate faithfulness score
    total_claims = len(extracted_claims)
    supported_claims = len(claim_analysis['supported'])
    
    faithfulness_score = supported_claims / total_claims if total_claims > 0 else 0.0
    
    return {
        'faithfulness_score': faithfulness_score,
        'total_claims': total_claims,
        'supported_claims': supported_claims,
        'contradicted_claims': len(claim_analysis['contradicted']),
        'hallucinated_claims': len(claim_analysis['hallucinated']),
        'claim_analysis': claim_analysis,
        'critical_flags': claim_analysis['contradicted'] + claim_analysis['hallucinated']
    }

def extract_claims_from_explanation(explanation: str) -> List[Dict]:
    """Extract factual claims from explanation text"""
    claims = []
    
    # Numerical claim patterns
    numerical_patterns = [
        r'income (?:of |is )?(\$?[\d,]+)',
        r'age (?:of |is )?(\d+)',
        r'credit score (?:of |is )?(\d+)',
        r'DTI (?:of |is |ratio )?(\d+%?)',
        r'utilization (?:of |is |rate )?(\d+%?)'
    ]
    
    # Categorical claim patterns
    categorical_patterns = [
        r'employment status (?:is |of )?([a-zA-Z\s]+)',
        r'housing (?:status )?(?:is |of )?([a-zA-Z\s]+)',
        r'education (?:level )?(?:is |of )?([a-zA-Z\s]+)'
    ]
    
    # Extract numerical claims
    for pattern in numerical_patterns:
        matches = re.finditer(pattern, explanation.lower())
        for match in matches:
            claims.append({
                'type': 'numerical',
                'text': match.group(0),
                'value': match.group(1),
                'feature': pattern.split()[0]  # Extract feature name
            })
    
    # Extract categorical claims
    for pattern in categorical_patterns:
        matches = re.finditer(pattern, explanation.lower())
        for match in matches:
            claims.append({
                'type': 'categorical',
                'text': match.group(0),
                'value': match.group(1).strip(),
                'feature': pattern.split()[0]
            })
    
    return claims
```

**2. LIME Alignment Analysis**
```python
def analyze_lime_alignment(explanation_text: str, lime_results: Dict, k: int = 5) -> Dict:
    """
    Analyze how well explanation aligns with LIME feature importance
    """
    # Get top-k features from LIME
    top_features = lime_results['feature_importance']
    top_k_features = dict(list(top_features.items())[:k])
    
    # Extract features mentioned in explanation
    mentioned_features = extract_mentioned_features(explanation_text)
    
    # Calculate coverage
    mentioned_topk = set(mentioned_features.keys()) & set(top_k_features.keys())
    coverage_at_k = len(mentioned_topk) / k if k > 0 else 0
    
    # Check direction agreement
    direction_agreements = []
    for feature in mentioned_topk:
        lime_direction = 'positive' if top_k_features[feature] > 0 else 'negative'
        text_direction = analyze_feature_direction_in_text(feature, explanation_text)
        
        if lime_direction == text_direction:
            direction_agreements.append(True)
        else:
            direction_agreements.append(False)
    
    direction_agreement = np.mean(direction_agreements) if direction_agreements else 0.0
    
    # Identify missing important features
    missing_features = set(top_k_features.keys()) - set(mentioned_features.keys())
    
    return {
        'coverage_at_k': coverage_at_k,
        'direction_agreement': direction_agreement,
        'mentioned_features': mentioned_features,
        'missing_important_features': list(missing_features),
        'lime_alignment_score': (coverage_at_k * 0.7 + direction_agreement * 0.3),
        'flags': {
            'low_coverage': coverage_at_k < 0.7,
            'direction_contradictions': direction_agreement < 0.8
        }
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
```

**3. Specificity & Actionability Analysis**
```python
def analyze_specificity_actionability(explanation_text: str) -> Dict:
    """
    Analyze how specific and actionable the explanation is
    """
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
```

**4. Completeness Analysis**
```python
def analyze_explanation_completeness(explanation_text: str, lime_results: Dict, 
                                   importance_threshold: float = 0.1) -> Dict:
    """
    Analyze how completely the explanation covers important drivers
    """
    # Get high-importance features from LIME
    high_importance_features = {}
    for feature, importance in lime_results['feature_importance'].items():
        if abs(importance) >= importance_threshold:
            high_importance_features[feature] = importance
    
    # Separate positive and negative drivers
    positive_drivers = {f: imp for f, imp in high_importance_features.items() if imp > 0}
    negative_drivers = {f: imp for f, imp in high_importance_features.items() if imp < 0}
    
    # Check what's mentioned in explanation
    mentioned_features = extract_mentioned_features(explanation_text)
    
    # Calculate coverage for each type
    mentioned_positive = set(mentioned_features.keys()) & set(positive_drivers.keys())
    mentioned_negative = set(mentioned_features.keys()) & set(negative_drivers.keys())
    
    positive_coverage = len(mentioned_positive) / len(positive_drivers) if positive_drivers else 1.0
    negative_coverage = len(mentioned_negative) / len(negative_drivers) if negative_drivers else 1.0
    
    # Overall completeness
    total_high_importance = len(high_importance_features)
    mentioned_high_importance = len(set(mentioned_features.keys()) & set(high_importance_features.keys()))
    overall_completeness = mentioned_high_importance / total_high_importance if total_high_importance > 0 else 1.0
    
    return {
        'overall_completeness': overall_completeness,
        'positive_driver_coverage': positive_coverage,
        'negative_driver_coverage': negative_coverage,
        'missing_positive_drivers': list(set(positive_drivers.keys()) - mentioned_positive),
        'missing_negative_drivers': list(set(negative_drivers.keys()) - mentioned_negative),
        'mentioned_high_importance': mentioned_high_importance,
        'total_high_importance': total_high_importance,
        'flags': {
            'incomplete_coverage': overall_completeness < 0.6,
            'missing_positives': positive_coverage < 0.5 and len(positive_drivers) > 0,
            'missing_negatives': negative_coverage < 0.5 and len(negative_drivers) > 0
        }
    }
```

**5. Consistency Analysis**
```python
def analyze_explanation_consistency(profile: Dict, api_client, 
                                  num_runs: int = 5) -> Dict:
    """
    Analyze consistency of explanations across multiple runs
    """
    explanations = []
    
    # Collect multiple explanations for the same input
    for run in range(num_runs):
        response = api_client.predict(profile)
        explanation = extract_explanation_text(response)
        explanations.append(explanation)
    
    # Calculate semantic similarity using sentence-BERT
    similarity_matrix = calculate_semantic_similarity_matrix(explanations)
    
    # Token overlap analysis
    token_overlaps = calculate_token_overlaps(explanations)
    
    # Key claims consistency
    claim_consistency = analyze_claim_consistency(explanations)
    
    # Calculate mean similarity
    upper_triangle = similarity_matrix[np.triu_indices_from(similarity_matrix, k=1)]
    mean_similarity = np.mean(upper_triangle)
    
    return {
        'mean_semantic_similarity': mean_similarity,
        'similarity_matrix': similarity_matrix.tolist(),
        'token_overlap_stats': {
            'mean_overlap': np.mean(token_overlaps),
            'std_overlap': np.std(token_overlaps)
        },
        'claim_consistency': claim_consistency,
        'stability_score': mean_similarity,
        'flags': {
            'low_consistency': mean_similarity < 0.85,
            'high_variance': np.std(upper_triangle) > 0.15
        }
    }

def calculate_semantic_similarity_matrix(explanations: List[str]) -> np.ndarray:
    """Calculate semantic similarity matrix using sentence-BERT"""
    from sentence_transformers import SentenceTransformer
    
    # Load pre-trained sentence-BERT model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Encode explanations
    embeddings = model.encode(explanations)
    
    # Calculate cosine similarity matrix
    similarity_matrix = np.zeros((len(explanations), len(explanations)))
    
    for i in range(len(explanations)):
        for j in range(len(explanations)):
            similarity = np.dot(embeddings[i], embeddings[j]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
            )
            similarity_matrix[i][j] = similarity
    
    return similarity_matrix
```

**6. Counterfactual Sensitivity Analysis**
```python
def analyze_counterfactual_sensitivity(profile: Dict, api_client, 
                                     perturbation_features: List[str]) -> Dict:
    """
    Analyze how explanations change when features are perturbed
    """
    original_response = api_client.predict(profile)
    original_explanation = extract_explanation_text(original_response)
    original_score = extract_credit_score(original_response)
    
    counterfactual_results = []
    
    for feature in perturbation_features:
        # Create perturbed profile
        perturbed_profile = profile.copy()
        
        # Apply meaningful perturbation based on feature type
        if feature in ['income', 'age', 'credit_limit']:
            # Increase numerical features by 20%
            perturbed_profile[feature] = profile[feature] * 1.2
        elif feature in ['employment_status', 'housing_status']:
            # Change to more favorable category
            perturbed_profile[feature] = get_better_category(feature, profile[feature])
        
        # Get new prediction and explanation
        perturbed_response = api_client.predict(perturbed_profile)
        perturbed_explanation = extract_explanation_text(perturbed_response)
        perturbed_score = extract_credit_score(perturbed_response)
        
        # Calculate score impact
        score_impact = abs(perturbed_score - original_score)
        
        # Check if changed feature is mentioned in new explanation
        feature_mentioned = feature in extract_mentioned_features(perturbed_explanation)
        
        # Calculate explanation similarity
        explanation_similarity = calculate_semantic_similarity([original_explanation, perturbed_explanation])[0, 1]
        
        counterfactual_results.append({
            'perturbed_feature': feature,
            'score_impact': score_impact,
            'feature_mentioned_in_new_explanation': feature_mentioned,
            'explanation_similarity': explanation_similarity,
            'appropriate_change': score_impact > 5 and feature_mentioned  # High impact should be mentioned
        })
    
    # Calculate overall alignment
    high_impact_perturbations = [r for r in counterfactual_results if r['score_impact'] > 10]
    appropriate_mentions = [r for r in high_impact_perturbations if r['feature_mentioned_in_new_explanation']]
    
    alignment_score = len(appropriate_mentions) / len(high_impact_perturbations) if high_impact_perturbations else 1.0
    
    return {
        'counterfactual_alignment': alignment_score,
        'perturbation_results': counterfactual_results,
        'high_impact_perturbations': len(high_impact_perturbations),
        'appropriate_mentions': len(appropriate_mentions),
        'flags': {
            'low_alignment': alignment_score < 0.6
        }
    }
```

**7. Compliance & Safety Analysis**
```python
def analyze_compliance_safety(explanation_text: str) -> Dict:
    """
    Analyze explanation for compliance and safety issues
    """
    violations = []
    
    # Protected attribute patterns
    protected_patterns = {
        'gender': r'\b(male|female|man|woman|gender)\b',
        'race_ethnicity': r'\b(black|white|hispanic|asian|african|european|race|ethnicity)\b',
        'religion': r'\b(christian|muslim|jewish|religious|religion)\b',
        'age_discrimination': r'\b(old|young|elderly|senior|age)\b',
        'disability': r'\b(disabled|disability|handicap)\b',
        'marital_status': r'\b(married|single|divorced|widowed)\b',
        'family_status': r'\b(pregnant|children|family size|single mother)\b'
    }
    
    # Sensitive inference patterns
    sensitive_inferences = {
        'immigration_status': r'\b(immigrant|foreign|citizen|visa)\b',
        'sexual_orientation': r'\b(gay|lesbian|straight|sexual orientation)\b',
        'political_affiliation': r'\b(democrat|republican|political|liberal|conservative)\b'
    }
    
    text_lower = explanation_text.lower()
    
    # Check for protected attribute usage
    for attribute, pattern in protected_patterns.items():
        if re.search(pattern, text_lower):
            violations.append({
                'type': 'protected_attribute',
                'attribute': attribute,
                'severity': 'CRITICAL',
                'description': f'Explanation references protected attribute: {attribute}'
            })
    
    # Check for sensitive inferences
    for inference, pattern in sensitive_inferences.items():
        if re.search(pattern, text_lower):
            violations.append({
                'type': 'sensitive_inference',
                'inference': inference,
                'severity': 'HIGH',
                'description': f'Explanation makes sensitive inference: {inference}'
            })
    
    # Check for harmful advice
    harmful_patterns = [
        r'falsify|lie about|hide|conceal',
        r'discrimination|unfair|bias',
        r'illegal|unlawful|against the law'
    ]
    
    for pattern in harmful_patterns:
        if re.search(pattern, text_lower):
            violations.append({
                'type': 'harmful_advice',
                'pattern': pattern,
                'severity': 'CRITICAL',
                'description': f'Explanation contains potentially harmful advice'
            })
    
    # Determine overall compliance status
    critical_violations = [v for v in violations if v['severity'] == 'CRITICAL']
    compliance_status = 'FAIL' if critical_violations else 'PASS'
    
    return {
        'compliance_status': compliance_status,
        'violations': violations,
        'critical_violations': len(critical_violations),
        'total_violations': len(violations),
        'passes_compliance': compliance_status == 'PASS'
    }
```

**8. Structure & Readability Analysis**
```python
def analyze_structure_readability(explanation_text: str) -> Dict:
    """
    Analyze explanation structure and readability
    """
    # Grammar and spelling check (simplified)
    grammar_score = check_grammar_spelling(explanation_text)
    
    # Structure analysis
    sentences = explanation_text.split('.')
    has_summary = check_for_summary_sentence(sentences[0] if sentences else "")
    
    # Bullet point or structured reasons
    structured_reasons = count_structured_reasons(explanation_text)
    
    # Actionable next steps
    actionable_steps = count_actionable_steps(explanation_text)
    
    # Readability metrics
    readability = calculate_readability_score(explanation_text)
    
    # Calculate overall structure score (0-5)
    structure_score = 0
    
    # Grammar and spelling (0-2 points)
    structure_score += min(2, grammar_score * 2)
    
    # Clear structure (0-2 points)
    if has_summary:
        structure_score += 1
    if structured_reasons >= 3:
        structure_score += 1
    
    # Actionable steps (0-1 point)
    if actionable_steps > 0:
        structure_score += 1
    
    return {
        'structure_score': structure_score,
        'normalized_score': structure_score / 5.0,
        'grammar_score': grammar_score,
        'has_summary': has_summary,
        'structured_reasons': structured_reasons,
        'actionable_steps': actionable_steps,
        'readability_score': readability,
        'flags': {
            'poor_structure': structure_score < 3,
            'no_summary': not has_summary,
            'no_actionable_steps': actionable_steps == 0
        }
    }
```

### Aggregate Explanation Quality Score

```python
def calculate_explanation_quality_score(analysis_results: Dict) -> Dict:
    """
    Calculate overall explanation quality score (0-100)
    
    Weighted combination:
    - Faithfulness: 25%
    - LIME Alignment (Coverage + Direction): 25%
    - Specificity & Actionability: 15%
    - Completeness: 15%
    - Stability: 10%
    - Counterfactual Sensitivity: 5%
    - Readability: 5%
    - Compliance & Safety: Gate (if fail → cap to 20)
    """
    
    # Extract component scores
    faithfulness = analysis_results['faithfulness']['faithfulness_score']
    
    # LIME alignment (average of coverage and direction)
    lime_coverage = analysis_results['lime_alignment']['coverage_at_k']
    lime_direction = analysis_results['lime_alignment']['direction_agreement']
    lime_alignment = (lime_coverage + lime_direction) / 2
    
    specificity = analysis_results['specificity']['normalized_score']
    completeness = analysis_results['completeness']['overall_completeness']
    stability = analysis_results['consistency']['stability_score']
    counterfactual = analysis_results['counterfactual']['counterfactual_alignment']
    readability = analysis_results['readability']['normalized_score']
    
    # Check compliance gate
    compliance_pass = analysis_results['compliance']['passes_compliance']
    
    # Calculate weighted score
    weighted_score = (
        faithfulness * 0.25 +
        lime_alignment * 0.25 +
        specificity * 0.15 +
        completeness * 0.15 +
        stability * 0.10 +
        counterfactual * 0.05 +
        readability * 0.05
    )
    
    # Apply compliance gate
    if not compliance_pass:
        final_score = min(20, weighted_score * 100)  # Cap at 20 if compliance fails
    else:
        final_score = weighted_score * 100
    
    # Generate quality level
    if final_score >= 90:
        quality_level = "EXCELLENT"
        quality_color = "#27ae60"
    elif final_score >= 80:
        quality_level = "GOOD"
        quality_color = "#f39c12"
    elif final_score >= 70:
        quality_level = "FAIR"
        quality_color = "#e67e22"
    else:
        quality_level = "POOR"
        quality_color = "#e74c3c"
    
    # Collect all critical flags
    critical_flags = []
    if not compliance_pass:
        critical_flags.extend(['compliance_violation'])
    if analysis_results['faithfulness'].get('critical_flags'):
        critical_flags.extend(['contradictions', 'hallucinations'])
    if analysis_results['lime_alignment']['flags']['low_coverage']:
        critical_flags.extend(['poor_lime_alignment'])
    
    return {
        'overall_score': final_score,
        'quality_level': quality_level,
        'quality_color': quality_color,
        'component_scores': {
            'faithfulness': faithfulness * 100,
            'lime_alignment': lime_alignment * 100,
            'specificity': specificity * 100,
            'completeness': completeness * 100,
            'stability': stability * 100,
            'counterfactual_sensitivity': counterfactual * 100,
            'readability': readability * 100
        },
        'compliance_status': 'PASS' if compliance_pass else 'FAIL',
        'critical_flags': critical_flags,
        'recommendations': generate_improvement_recommendations(analysis_results)
    }

def generate_improvement_recommendations(analysis_results: Dict) -> List[str]:
    """Generate specific recommendations for improving explanation quality"""
    recommendations = []
    
    # Faithfulness recommendations
    if analysis_results['faithfulness']['faithfulness_score'] < 0.9:
        recommendations.append("Improve explanation faithfulness by ensuring all claims are grounded in input data")
    
    # LIME alignment recommendations
    if analysis_results['lime_alignment']['flags']['low_coverage']:
        recommendations.append("Include more of the top important features identified by LIME analysis")
    
    # Specificity recommendations
    if analysis_results['specificity']['flags']['too_vague']:
        recommendations.append("Add specific values, thresholds, and actionable advice to explanations")
    
    # Completeness recommendations
    if analysis_results['completeness']['flags']['incomplete_coverage']:
        recommendations.append("Ensure explanations cover both positive and negative decision drivers")
    
    # Consistency recommendations
    if analysis_results['consistency']['flags']['low_consistency']:
        recommendations.append("Improve explanation stability across multiple API calls")
    
    # Compliance recommendations
    if not analysis_results['compliance']['passes_compliance']:
        recommendations.append("CRITICAL: Remove references to protected attributes and ensure legal compliance")
    
    return recommendations
```

## How It Works
- Measures feature importance by analyzing prediction changes
- Model-agnostic approach
- Provides global feature rankings

**Counterfactual Explanations:**
- Shows minimal changes needed for different outcomes
- Actionable insights for applicants
- Helps understand decision boundaries

## Key Features (Planned)

### 1. Feature Attribution Analysis

```python
def analyze_feature_importance(responses):
    """Analyze which features most influence credit decisions"""
    
    # Extract features and predictions from responses
    features = extract_features(responses)
    predictions = extract_predictions(responses)
    
    # Calculate various importance metrics
    importance_scores = {
        'permutation': calculate_permutation_importance(features, predictions),
        'shap': calculate_shap_values(features, predictions),
        'correlation': calculate_correlation_importance(features, predictions)
    }
    
    # Rank features by importance
    feature_rankings = rank_features(importance_scores)
    
    return {
        'importance_scores': importance_scores,
        'feature_rankings': feature_rankings,
        'top_features': get_top_features(feature_rankings, n=10)
    }
```

### 2. Decision Pathway Analysis

```python
def trace_decision_pathways(model_responses):
    """Trace how inputs lead to final decisions"""
    
    pathways = []
    for response in model_responses:
        pathway = {
            'input_features': response['input'],
            'intermediate_scores': extract_intermediate_scores(response),
            'final_decision': response['output']['decision'],
            'confidence': response['output']['confidence'],
            'decision_factors': identify_key_factors(response)
        }
        pathways.append(pathway)
    
    return analyze_pathway_patterns(pathways)
```

### 3. Explanation Generation

```python
def generate_explanations(individual_case):
    """Generate human-readable explanations for credit decisions"""
    
    explanation = {
        'decision': individual_case['decision'],
        'confidence': individual_case['confidence'],
        'key_factors': {
            'positive': identify_positive_factors(individual_case),
            'negative': identify_negative_factors(individual_case),
            'neutral': identify_neutral_factors(individual_case)
        },
        'counterfactuals': generate_counterfactual_scenarios(individual_case),
        'similar_cases': find_similar_cases(individual_case),
        'explanation_text': generate_natural_language_explanation(individual_case)
    }
    
    return explanation
```

## Transparency Metrics (Planned)

### 1. Explanation Quality Scores

**Completeness Score (0-100%):**
- Percentage of decision factors explained
- Coverage of all relevant input features
- Identification of key decision drivers

**Consistency Score (0-100%):**
- Similar cases receive similar explanations
- Explanation stability across time
- Coherent explanation logic

**Accuracy Score (0-100%):**
- How well explanations reflect actual model behavior
- Correlation between explanation weights and true importance
- Validation against ground truth explanations

### 2. Interpretability Metrics

**Feature Importance Stability:**
- Consistency of feature rankings across samples
- Temporal stability of importance scores
- Robustness to input perturbations

**Decision Boundary Clarity:**
- How clear the decision boundaries are
- Separation between different decision regions
- Ease of understanding decision logic

**Counterfactual Quality:**
- Realism of counterfactual scenarios
- Minimal changes required for different outcomes
- Actionability of suggested changes

## Implementation Roadmap

### Phase 1: Foundation (Planned)

1. **Basic Structure Setup**
   - Create transparency analysis module structure
   - Implement basic explanation interfaces
   - Set up testing framework

2. **Feature Importance Analysis**
   - Implement permutation importance
   - Add correlation-based importance
   - Create feature ranking system

3. **Simple Explanations**
   - Generate basic decision explanations
   - Create feature contribution summaries
   - Implement explanation templates

### Phase 2: Advanced Explanations (Planned)

1. **SHAP Integration**
   - Implement SHAP value calculations
   - Create SHAP-based visualizations
   - Add local explanation generation

2. **LIME Integration**
   - Implement LIME explanations
   - Create interpretable local models
   - Add explanation quality assessment

3. **Counterfactual Analysis**
   - Generate counterfactual examples
   - Create actionable recommendations
   - Implement scenario analysis

### Phase 3: Compliance and Quality (Planned)

1. **Regulatory Compliance**
   - Implement GDPR compliance checks
   - Add FCRA explanation requirements
   - Create compliance reporting

2. **Explanation Quality Assessment**
   - Implement explanation quality metrics
   - Add consistency validation
   - Create quality dashboards

3. **User Interface Integration**
   - Add explanation display to web interface
   - Create interactive explanation tools
   - Implement explanation export functionality

## Usage (When Implemented)

### Through Web Interface

```html
<!-- Planned UI integration -->
<div class="analysis-options">
    <input type="checkbox" id="transparency" name="transparency">
    <label for="transparency">Transparency Analysis</label>
</div>

<div id="transparency-results" class="results-section">
    <h3>Model Transparency Report</h3>
    <div class="feature-importance">...</div>
    <div class="explanations">...</div>
    <div class="compliance-status">...</div>
</div>
```

### Programmatic Usage

```python
from analysis.transparency import run_transparency_analysis

# Run transparency analysis (when implemented)
results = run_transparency_analysis()

# Access explanation components
feature_importance = results['feature_importance']
explanations = results['explanations']
compliance_status = results['compliance_status']

# Generate explanation for specific case
case_explanation = generate_case_explanation(individual_case)
```

## Report Features (Planned)

### Executive Summary
- Overall transparency score (0-100%)
- Model interpretability rating
- Regulatory compliance status
- Key transparency findings

### Feature Importance Analysis
- **Global Importance**: Most influential features across all decisions
- **Local Variations**: How importance varies across different cases
- **Temporal Stability**: How feature importance changes over time
- **Interaction Effects**: How features interact to influence decisions

### Individual Case Explanations
- **Decision Breakdown**: Why each decision was made
- **Contributing Factors**: Positive and negative influences
- **Counterfactual Scenarios**: What would change the decision
- **Confidence Assessment**: How certain the model is

### Compliance Assessment
- **GDPR Compliance**: Right to explanation requirements
- **FCRA Compliance**: Adverse action explanation requirements
- **Regulatory Gaps**: Areas needing improvement
- **Audit Trail**: Documentation for regulatory review

## Best Practices (When Implementing)

### For Model Developers

1. **Design for Interpretability**: Build models with transparency in mind
2. **Feature Engineering**: Create interpretable features when possible
3. **Model Selection**: Balance accuracy with interpretability
4. **Documentation**: Thoroughly document model architecture and logic
5. **Validation**: Validate explanations against domain expertise

### For Compliance Officers

1. **Regulatory Mapping**: Map transparency features to regulatory requirements
2. **Documentation Standards**: Establish explanation documentation standards
3. **Audit Preparation**: Maintain explanation records for regulatory review
4. **Training**: Train staff on transparency requirements and tools
5. **Continuous Monitoring**: Regularly assess explanation quality

### for Business Stakeholders

1. **Explanation Standards**: Define acceptable explanation quality levels
2. **User Communication**: Develop customer-facing explanation formats
3. **Training Materials**: Create materials for staff explanation training
4. **Feedback Systems**: Implement systems for explanation quality feedback
5. **Business Integration**: Integrate explanations into business processes

## Challenges and Considerations

### Technical Challenges

**Model Complexity:**
- Black-box models are inherently difficult to explain
- Deep learning models require sophisticated explanation techniques
- Ensemble models complicate explanation generation

**Computational Overhead:**
- Explanation generation can be computationally expensive
- Real-time explanation requirements
- Scalability for high-volume applications

**Explanation Quality:**
- Ensuring explanation accuracy and reliability
- Balancing simplicity with completeness
- Validating explanation correctness

### Regulatory Challenges

**Compliance Requirements:**
- Different jurisdictions have different requirements
- Evolving regulatory landscape
- Balancing compliance with business needs

**Legal Liability:**
- Responsibility for explanation accuracy
- Legal implications of incorrect explanations
- Documentation and audit trail requirements

## Future Considerations

### Emerging Technologies

**Neural Network Interpretability:**
- Attention mechanisms for explanation
- Layer-wise relevance propagation
- Integrated gradients

**Automated Explanation Generation:**
- Natural language generation for explanations
- Automated explanation quality assessment
- Personalized explanation formats

**Real-time Explanation Services:**
- On-demand explanation generation
- Explanation caching and optimization
- Interactive explanation interfaces

### Regulatory Evolution

**AI Governance Frameworks:**
- Emerging AI regulation requirements
- Industry-specific transparency standards
- International harmonization efforts

**Audit and Compliance Tools:**
- Automated compliance checking
- Regulatory reporting automation
- Audit trail generation

## Implementation Priority

### High Priority (Immediate Need)
1. Basic feature importance analysis
2. Simple decision explanations
3. Compliance framework setup

### Medium Priority (Next Phase)
1. Advanced explanation methods (SHAP, LIME)
2. Counterfactual analysis
3. Explanation quality assessment

### Lower Priority (Future Enhancement)
1. Advanced visualization tools
2. Interactive explanation interfaces
3. Automated compliance reporting

## Conclusion

The transparency analysis feature will provide essential explainability capabilities for credit scoring models, ensuring regulatory compliance and building stakeholder trust. While currently in placeholder status, the planned implementation will follow industry best practices for model interpretability and provide comprehensive transparency assessment capabilities.

The implementation will be developed incrementally, starting with basic explanation capabilities and progressing to advanced interpretability methods. This approach will ensure that the most critical transparency needs are addressed first while building a foundation for future enhancements.
