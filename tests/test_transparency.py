#!/usr/bin/env python3
"""
Test script for transparency analysis functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock
from analysis.transparency import (
    analyze_explanation_faithfulness,
    analyze_lime_alignment,
    analyze_specificity_actionability,
    analyze_explanation_completeness,
    analyze_compliance_safety,
    analyze_structure_readability,
    calculate_explanation_quality_score,
    extract_mentioned_features,
    build_canonical_facts,
    CreditProfilePerturbator
)

class TestTransparencyAnalysis(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.sample_profile = {
            'age': 35,
            'income': 75000,
            'credit_score': 720,
            'employment_status': 'employed',
            'employment_length': 5,
            'debt_to_income': 0.3,
            'credit_utilization': 0.25,
            'housing_status': 'own',
            'loan_purpose': 'personal'
        }
        
        self.sample_explanation = """
        Based on your credit profile, you qualify for a loan with favorable terms. 
        Your credit score of 720 is excellent and demonstrates responsible credit management. 
        Your income of $75,000 provides sufficient capacity for loan repayment. 
        Your employment status as employed with 5 years experience adds stability. 
        However, your debt-to-income ratio of 30% is at the upper limit of our preferred range.
        To improve your profile, consider reducing existing debt or increasing income.
        """
        
        self.sample_lime_results = {
            'feature_importance': {
                'credit_score': 0.45,
                'income': 0.32,
                'debt_to_income': -0.28,
                'employment_length': 0.15,
                'age': 0.08
            },
            'top_positive_features': [
                ('credit_score', 0.45),
                ('income', 0.32),
                ('employment_length', 0.15)
            ],
            'top_negative_features': [
                ('debt_to_income', -0.28)
            ],
            'local_model_r2': 0.78
        }
    
    def test_build_canonical_facts(self):
        """Test building canonical facts from profile"""
        facts = build_canonical_facts(self.sample_profile)
        
        self.assertIn('age', facts)
        self.assertIn('income', facts)
        self.assertIn('credit_score', facts)
        self.assertEqual(facts['age']['value'], 35)
        self.assertEqual(facts['income']['value'], 75000)
        self.assertEqual(facts['credit_score']['value'], 720)
        self.assertEqual(facts['age']['type'], 'numerical')
        self.assertEqual(facts['employment_status']['type'], 'categorical')
    
    def test_extract_mentioned_features(self):
        """Test extracting mentioned features from explanation"""
        mentioned = extract_mentioned_features(self.sample_explanation)
        
        self.assertIn('credit_score', mentioned)
        self.assertIn('income', mentioned)
        self.assertIn('employment_status', mentioned)
        self.assertIn('debt_to_income', mentioned)
    
    def test_analyze_explanation_faithfulness(self):
        """Test faithfulness analysis"""
        result = analyze_explanation_faithfulness(self.sample_explanation, self.sample_profile)
        
        self.assertIn('faithfulness_score', result)
        self.assertIn('mentioned_facts_ratio', result)
        self.assertIn('factual_errors', result)
        self.assertIsInstance(result['faithfulness_score'], float)
        self.assertGreaterEqual(result['faithfulness_score'], 0)
        self.assertLessEqual(result['faithfulness_score'], 1)
    
    def test_analyze_lime_alignment(self):
        """Test LIME alignment analysis"""
        result = analyze_lime_alignment(self.sample_explanation, self.sample_lime_results)
        
        self.assertIn('alignment_score', result)
        self.assertIn('coverage_score', result)
        self.assertIn('direction_agreement', result)
        self.assertIsInstance(result['alignment_score'], float)
        self.assertGreaterEqual(result['alignment_score'], 0)
        self.assertLessEqual(result['alignment_score'], 1)
    
    def test_analyze_specificity_actionability(self):
        """Test specificity and actionability analysis"""
        result = analyze_specificity_actionability(self.sample_explanation)
        
        self.assertIn('specificity_score', result)
        self.assertIn('category', result)
        self.assertIn('signals', result)
        self.assertIn('normalized_score', result)
        self.assertIsInstance(result['specificity_score'], (int, float))
        self.assertGreaterEqual(result['normalized_score'], 0)
        self.assertLessEqual(result['normalized_score'], 1)
    
    def test_analyze_explanation_completeness(self):
        """Test completeness analysis"""
        result = analyze_explanation_completeness(self.sample_explanation, self.sample_lime_results)
        
        self.assertIn('completeness_score', result)
        self.assertIn('important_features_covered', result)
        self.assertIn('total_important_features', result)
        self.assertIsInstance(result['completeness_score'], float)
        self.assertGreaterEqual(result['completeness_score'], 0)
        self.assertLessEqual(result['completeness_score'], 1)
    
    def test_analyze_compliance_safety(self):
        """Test compliance and safety analysis"""
        # Test compliant explanation
        compliant_result = analyze_compliance_safety(self.sample_explanation)
        self.assertIn('compliant', compliant_result)
        self.assertIn('protected_violations', compliant_result)
        self.assertIn('harmful_violations', compliant_result)
        self.assertTrue(compliant_result['compliant'])
        
        # Test non-compliant explanation
        non_compliant_explanation = "Your loan was denied because you are a woman and we prefer male applicants."
        non_compliant_result = analyze_compliance_safety(non_compliant_explanation)
        self.assertFalse(non_compliant_result['compliant'])
        self.assertGreater(len(non_compliant_result['protected_violations']), 0)
    
    def test_analyze_structure_readability(self):
        """Test structure and readability analysis"""
        result = analyze_structure_readability(self.sample_explanation)
        
        self.assertIn('readability_score', result)
        self.assertIn('avg_sentence_length', result)
        self.assertIn('word_count', result)
        self.assertIn('structure_signals', result)
        self.assertIsInstance(result['readability_score'], float)
        self.assertGreaterEqual(result['readability_score'], 0)
        self.assertLessEqual(result['readability_score'], 1)
    
    def test_calculate_explanation_quality_score(self):
        """Test overall quality score calculation"""
        # Create mock analysis results
        analysis_results = {
            'faithfulness': {'faithfulness_score': 0.8},
            'lime_alignment': {'alignment_score': 0.7},
            'specificity': {'normalized_score': 0.6},
            'completeness': {'completeness_score': 0.9},
            'consistency': {'consistency_score': 0.8},
            'counterfactual': {'sensitivity_score': 0.5},
            'compliance': {'compliant': True},
            'readability': {'readability_score': 0.7}
        }
        
        result = calculate_explanation_quality_score(analysis_results)
        
        self.assertIn('overall_score', result)
        self.assertIn('category', result)
        self.assertIn('dimension_scores', result)
        self.assertIn('is_compliant', result)
        self.assertIsInstance(result['overall_score'], (int, float))
        self.assertGreaterEqual(result['overall_score'], 0)
        self.assertLessEqual(result['overall_score'], 100)
        self.assertTrue(result['is_compliant'])
    
    def test_calculate_quality_score_with_compliance_gate(self):
        """Test quality score with compliance gate applied"""
        # Create analysis results with non-compliance
        analysis_results = {
            'faithfulness': {'faithfulness_score': 0.9},
            'lime_alignment': {'alignment_score': 0.9},
            'specificity': {'normalized_score': 0.9},
            'completeness': {'completeness_score': 0.9},
            'consistency': {'consistency_score': 0.9},
            'counterfactual': {'sensitivity_score': 0.9},
            'compliance': {'compliant': False},  # Non-compliant
            'readability': {'readability_score': 0.9}
        }
        
        result = calculate_explanation_quality_score(analysis_results)
        
        # Score should be capped at 20 due to compliance gate
        self.assertLessEqual(result['overall_score'], 20)
        self.assertFalse(result['is_compliant'])
        self.assertTrue(result['compliance_gate_applied'])
    
    def test_credit_profile_perturbator(self):
        """Test credit profile perturbation for LIME"""
        perturbator = CreditProfilePerturbator(self.sample_profile)
        
        # Test perturbation
        perturbed = perturbator.perturb()
        
        # Check that all original keys are present
        for key in self.sample_profile.keys():
            self.assertIn(key, perturbed)
        
        # Check that some values have changed (with high probability)
        differences = 0
        for key in self.sample_profile.keys():
            if perturbed[key] != self.sample_profile[key]:
                differences += 1
        
        # Should have at least some differences
        self.assertGreater(differences, 0)
    
    def test_quality_categories(self):
        """Test quality score categorization"""
        test_cases = [
            (95, 'excellent'),
            (85, 'good'),
            (75, 'fair'),
            (65, 'poor')
        ]
        
        for score, expected_category in test_cases:
            analysis_results = {
                'faithfulness': {'faithfulness_score': score/100},
                'lime_alignment': {'alignment_score': score/100},
                'specificity': {'normalized_score': score/100},
                'completeness': {'completeness_score': score/100},
                'consistency': {'consistency_score': score/100},
                'counterfactual': {'sensitivity_score': score/100},
                'compliance': {'compliant': True},
                'readability': {'readability_score': score/100}
            }
            
            result = calculate_explanation_quality_score(analysis_results)
            self.assertEqual(result['category'], expected_category)

def run_tests():
    """Run all transparency analysis tests"""
    print("🧪 Running Transparency Analysis Tests")
    print("=" * 40)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTransparencyAnalysis)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print(f"\n✅ All {result.testsRun} tests passed!")
    else:
        print(f"\n❌ {len(result.failures)} failures, {len(result.errors)} errors out of {result.testsRun} tests")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_tests()
