# tests/test_consistency.py

import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from analysis.consistency import (
    hash_input_data, normalize_response_text, extract_decision_and_confidence,
    analyze_consistency_results, run_consistency_analysis
)


class TestConsistencyAnalysis(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.test_df = pd.DataFrame({
            'age': [25, 35, 45],
            'income': [50000, 75000, 100000],
            'credit_score': [650, 750, 800],
            'employment_status': ['employed', 'employed', 'self-employed']
        })
    
    def test_hash_input_data(self):
        """Test input data hashing"""
        data1 = {'age': 25, 'income': 50000, 'name': 'John'}
        data2 = {'name': 'John', 'age': 25, 'income': 50000}  # Different order
        data3 = {'age': 26, 'income': 50000, 'name': 'John'}  # Different value
        
        hash1 = hash_input_data(data1)
        hash2 = hash_input_data(data2)
        hash3 = hash_input_data(data3)
        
        # Same data should produce same hash regardless of order
        self.assertEqual(hash1, hash2)
        
        # Different data should produce different hash
        self.assertNotEqual(hash1, hash3)
        
        # Hash should be consistent
        self.assertEqual(hash_input_data(data1), hash_input_data(data1))
    
    def test_normalize_response_text(self):
        """Test response text normalization"""
        self.assertEqual(normalize_response_text("  Hello World  "), "hello world")
        self.assertEqual(normalize_response_text("Hello\n\tWorld"), "hello world")
        self.assertEqual(normalize_response_text("HELLO   WORLD"), "hello world")
        self.assertEqual(normalize_response_text(""), "")
        self.assertEqual(normalize_response_text(None), "")
    
    def test_extract_decision_and_confidence(self):
        """Test decision and confidence extraction"""
        # Test approval with percentage
        decision, confidence = extract_decision_and_confidence("I approve this application with 85% confidence")
        self.assertEqual(decision, "approve")
        self.assertEqual(confidence, 0.85)
        
        # Test denial
        decision, confidence = extract_decision_and_confidence("I deny this application")
        self.assertEqual(decision, "deny")
        self.assertIsNone(confidence)
        
        # Test with confidence level keywords
        decision, confidence = extract_decision_and_confidence("Approve with high confidence")
        self.assertEqual(decision, "approve")
        self.assertEqual(confidence, 0.8)
        
        # Test empty response
        decision, confidence = extract_decision_and_confidence("")
        self.assertIsNone(decision)
        self.assertIsNone(confidence)
        
        # Test with decimal percentage
        decision, confidence = extract_decision_and_confidence("Approve with 72.5% confidence")
        self.assertEqual(decision, "approve")
        self.assertEqual(confidence, 0.725)
    
    def test_analyze_consistency_results(self):
        """Test consistency results analysis"""
        # Create mock consistency data
        consistency_data = [
            {
                "input_hash": "hash1",
                "input_data": {"age": 25, "income": 50000},
                "responses": [
                    {"response": "Approve with 80% confidence"},
                    {"response": "Approve with 80% confidence"},  # Perfect match
                    {"response": "Approve with 80% confidence"}
                ]
            },
            {
                "input_hash": "hash2", 
                "input_data": {"age": 35, "income": 75000},
                "responses": [
                    {"response": "Approve with 85% confidence"},
                    {"response": "Deny this application"},  # Inconsistent decision
                    {"response": "Approve with 90% confidence"}  # Different confidence
                ]
            }
        ]
        
        results = analyze_consistency_results(consistency_data)
        
        # Check basic structure
        self.assertIn('total_inputs', results)
        self.assertIn('overall_consistency_score', results)
        self.assertIn('perfect_consistency', results)
        self.assertIn('decision_consistency', results)
        self.assertIn('inconsistent_cases', results)
        
        self.assertEqual(results['total_inputs'], 2)
        self.assertEqual(results['total_responses'], 6)
        
        # First input should be perfectly consistent
        # Second input should be inconsistent
        self.assertEqual(results['perfect_consistency'], 0.5)  # 1 out of 2
        
        # Should have at least one inconsistent case
        self.assertGreater(len(results['inconsistent_cases']), 0)
    
    def test_analyze_empty_responses(self):
        """Test handling of empty response data"""
        responses = []
        results = analyze_consistency_results(responses)
        
        # Should handle empty data gracefully - default to perfect consistency
        self.assertEqual(results['overall_consistency_score'], 1.0)
        self.assertEqual(results['total_inputs'], 0)
        self.assertEqual(results['total_responses'], 0)
        self.assertEqual(len(results['consistency_by_input']), 0)
    
    def test_analyze_single_response(self):
        """Test handling of single responses (no comparison possible)"""
        consistency_data = [
            {
                "input_hash": "hash1",
                "input_data": {"age": 25},
                "responses": [
                    {"response": "Approve with 80% confidence"}
                ]
            }
        ]
        
        results = analyze_consistency_results(consistency_data)
        
        # Should handle single response gracefully
        self.assertEqual(results['total_inputs'], 1)
        self.assertEqual(results['total_responses'], 1)
        
        # No consistency metrics should be calculated for single responses
        # This tests the robustness of the analysis
        self.assertIsInstance(results['overall_consistency_score'], (int, float))
    
    @patch('analysis.consistency.save_jsonl')
    @patch('analysis.consistency.send_request')
    @patch('pandas.read_csv')
    @patch('os.path.exists')
    def test_run_consistency_analysis(self, mock_exists, mock_read_csv, mock_send_request, mock_save_jsonl):
        """Test full consistency analysis run"""
        # Mock CSV data
        mock_read_csv.return_value = self.test_df
        mock_exists.return_value = False  # Force new data collection
        
        # Mock consistent API responses
        mock_send_request.return_value = "Approve with 80% confidence"
        
        results = run_consistency_analysis(num_repeats=2)
        
        # Should return analysis results
        self.assertIsInstance(results, dict)
        self.assertIn('overall_consistency_score', results)
        
        # Should have called API multiple times (samples * repeats)
        self.assertTrue(mock_send_request.called)
        
        # Should have saved results
        mock_save_jsonl.assert_called()
    
    @patch('pandas.read_csv')
    @patch('os.path.exists')
    def test_run_consistency_analysis_with_existing_data(self, mock_exists, mock_read_csv):
        """Test consistency analysis with existing data"""
        mock_exists.return_value = True  # Simulate existing data
        
        # Mock existing consistency data
        existing_data = [
            {
                "input_hash": "hash1",
                "responses": [
                    {"response": "Approve"},
                    {"response": "Approve"}
                ]
            }
        ]
        
        with patch('analysis.consistency.load_jsonl', return_value=existing_data):
            results = run_consistency_analysis()
        
        # Should use existing data
        self.assertIsInstance(results, dict)
        self.assertIn('overall_consistency_score', results)


class TestConsistencyIntegration(unittest.TestCase):
    """Integration tests for consistency analysis"""
    
    @patch('analysis.consistency.send_request')
    @patch('pandas.read_csv')
    @patch('os.path.exists')
    def test_full_consistency_workflow_perfect_consistency(self, mock_exists, mock_read_csv, mock_send_request):
        """Test complete workflow with perfectly consistent responses"""
        # Setup test data
        test_df = pd.DataFrame({
            'age': [30, 40],
            'income': [60000, 80000]
        })
        
        mock_read_csv.return_value = test_df
        mock_exists.return_value = False
        
        # Mock perfectly consistent responses
        mock_send_request.return_value = "Approve with 80% confidence"
        
        results = run_consistency_analysis(num_repeats=3)
        
        # Should achieve perfect consistency
        self.assertNotIn('error', results)
        self.assertEqual(results['perfect_consistency'], 1.0)
        self.assertEqual(results['decision_consistency'], 1.0)
        self.assertGreaterEqual(results['overall_consistency_score'], 0.9)
    
    @patch('analysis.consistency.send_request')
    @patch('pandas.read_csv')
    @patch('os.path.exists')
    def test_full_consistency_workflow_inconsistent_responses(self, mock_exists, mock_read_csv, mock_send_request):
        """Test complete workflow with inconsistent responses"""
        test_df = pd.DataFrame({
            'age': [30],
            'income': [60000]
        })
        
        mock_read_csv.return_value = test_df
        mock_exists.return_value = False
        
        # Mock inconsistent responses
        responses = [
            "Approve with 80% confidence",
            "Deny this application",
            "Approve with 70% confidence"
        ]
        mock_send_request.side_effect = responses
        
        results = run_consistency_analysis(num_repeats=3)
        
        # Should detect inconsistency
        self.assertNotIn('error', results)
        self.assertLess(results['perfect_consistency'], 1.0)
        self.assertLess(results['decision_consistency'], 1.0)
        self.assertGreater(len(results['inconsistent_cases']), 0)


if __name__ == '__main__':
    unittest.main()
