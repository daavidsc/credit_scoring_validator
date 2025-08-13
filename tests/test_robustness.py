# tests/test_robustness.py

import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from analysis.robustness import (
    add_noise_to_numerical, add_typos_to_text, capitalize_text,
    generate_adversarial_examples, parse_credit_decision,
    analyze_robustness_results, run_robustness_analysis
)


class TestRobustnessAnalysis(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.test_df = pd.DataFrame({
            'age': [25, 35, 45, 55],
            'income': [50000, 75000, 100000, 125000],
            'credit_score': [650, 750, 800, 850],
            'employment_status': ['employed', 'employed', 'self-employed', 'retired'],
            'gender': ['M', 'F', 'M', 'F']
        })
    
    def test_add_noise_to_numerical(self):
        """Test numerical noise addition"""
        # Test with valid number
        value = 100.0
        noisy_value = add_noise_to_numerical(value, noise_factor=0.1)
        self.assertIsInstance(noisy_value, (int, float))
        self.assertNotEqual(value, noisy_value)  # Should be different
        
        # Test with NaN
        nan_result = add_noise_to_numerical(np.nan)
        self.assertTrue(pd.isna(nan_result))
        
        # Test with non-numerical
        text_result = add_noise_to_numerical("text")
        self.assertEqual(text_result, "text")
    
    def test_add_typos_to_text(self):
        """Test typo addition to text"""
        text = "employed"
        typo_text = add_typos_to_text(text, typo_rate=0.5)
        self.assertIsInstance(typo_text, str)
        self.assertEqual(len(typo_text), len(text))  # Length should be same
        
        # Test with NaN
        nan_result = add_typos_to_text(np.nan)
        self.assertTrue(pd.isna(nan_result))
        
        # Test with non-string
        num_result = add_typos_to_text(123)
        self.assertEqual(num_result, 123)
    
    def test_capitalize_text(self):
        """Test text capitalization"""
        self.assertEqual(capitalize_text("hello"), "HELLO")
        self.assertEqual(capitalize_text("Hello World"), "HELLO WORLD")
        self.assertTrue(pd.isna(capitalize_text(np.nan)))
        self.assertEqual(capitalize_text(123), 123)
    
    def test_generate_adversarial_examples(self):
        """Test adversarial example generation"""
        examples = generate_adversarial_examples(self.test_df, num_examples=2)
        
        # Should generate examples for each perturbation type
        perturbation_types = set(ex['perturbation_type'] for ex in examples)
        expected_types = {'noise_numerical', 'typos_text', 'case_change', 'missing_values', 'extreme_values'}
        self.assertTrue(perturbation_types.issubset(expected_types))
        
        # Each example should have required fields
        for example in examples:
            self.assertIn('original_index', example)
            self.assertIn('perturbation_type', example)
            self.assertIn('original_data', example)
            self.assertIn('perturbed_data', example)
    
    def test_parse_credit_decision(self):
        """Test credit decision parsing"""
        # Test approval
        decision, conf, reasoning = parse_credit_decision("I approve this application with 80% confidence")
        self.assertEqual(decision, "approve")
        self.assertEqual(conf, 0.8)
        
        # Test denial
        decision, conf, reasoning = parse_credit_decision("I deny this application")
        self.assertEqual(decision, "deny")
        
        # Test empty response
        decision, conf, reasoning = parse_credit_decision("")
        self.assertIsNone(decision)
        self.assertIsNone(conf)
        
        # Test high confidence indicator
        decision, conf, reasoning = parse_credit_decision("Approve with high confidence")
        self.assertEqual(decision, "approve")
        self.assertEqual(conf, 0.8)
    
    def test_analyze_robustness_results(self):
        """Test robustness results analysis"""
        # Create mock responses
        responses = [
            {
                "perturbation_type": "noise_numerical",
                "original_response": "Approve with 90% confidence",
                "perturbed_response": "Approve with 85% confidence"
            },
            {
                "perturbation_type": "typos_text", 
                "original_response": "Deny this application",
                "perturbed_response": "Approve with 70% confidence"
            }
        ]
        
        results = analyze_robustness_results(responses)
        
        # Check basic structure
        self.assertIn('total_examples', results)
        self.assertIn('decision_consistency', results)
        self.assertIn('perturbation_analysis', results)
        self.assertIn('robustness_score', results)
        self.assertIn('failure_cases', results)
        
        self.assertEqual(results['total_examples'], 2)
        
        # Should have one consistent and one inconsistent decision
        self.assertEqual(results['decision_consistency']['consistent_count'], 1)
        self.assertEqual(results['decision_consistency']['inconsistent_count'], 1)
        
        # Should have failure case for the inconsistent decision
        self.assertEqual(len(results['failure_cases']), 1)
    
    @patch('analysis.robustness.save_jsonl')
    @patch('analysis.robustness.send_request')
    @patch('pandas.read_csv')
    def test_run_robustness_analysis(self, mock_read_csv, mock_send_request, mock_save_jsonl):
        """Test full robustness analysis run"""
        # Mock CSV data
        mock_read_csv.return_value = self.test_df
        
        # Mock API responses
        mock_send_request.side_effect = [
            "Approve with 90% confidence",  # Original
            "Approve with 85% confidence",  # Perturbed
        ] * 50  # Enough responses for all adversarial examples
        
        # Mock file existence check
        with patch('os.path.exists', return_value=False):
            results = run_robustness_analysis()
        
        # Should return analysis results
        self.assertIsInstance(results, dict)
        self.assertIn('total_examples', results)
        self.assertIn('robustness_score', results)
        
        # Should have called API multiple times
        self.assertTrue(mock_send_request.called)
        
        # Should have saved results
        mock_save_jsonl.assert_called()


class TestRobustnessIntegration(unittest.TestCase):
    """Integration tests for robustness analysis"""
    
    @patch('analysis.robustness.send_request')
    @patch('pandas.read_csv')
    @patch('os.path.exists')
    def test_full_robustness_workflow(self, mock_exists, mock_read_csv, mock_send_request):
        """Test the complete robustness analysis workflow"""
        # Setup test data
        test_df = pd.DataFrame({
            'age': [30, 40],
            'income': [60000, 80000],
            'credit_score': [700, 750],
            'employment_status': ['employed', 'employed']
        })
        
        mock_read_csv.return_value = test_df
        mock_exists.return_value = False  # Force new data collection
        
        # Mock consistent API responses
        mock_send_request.return_value = "Approve with 80% confidence"
        
        results = run_robustness_analysis()
        
        # Should complete successfully
        self.assertNotIn('error', results)
        self.assertIn('robustness_score', results)
        
        # High consistency should result in good robustness score
        self.assertGreater(results['robustness_score'], 0.7)


if __name__ == '__main__':
    unittest.main()
