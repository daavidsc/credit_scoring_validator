#!/usr/bin/env python3
"""
Debug script to test API calls and identify issues
"""

import sys
import pandas as pd
from api.client import send_request, construct_payload
import json

def test_single_record():
    """Test with a single record from the CSV"""
    df = pd.read_csv('data/testdata.csv')
    
    print("=" * 60)
    print("TESTING FIRST RECORD FROM CSV")
    print("=" * 60)
    
    first_row = df.iloc[0].to_dict()
    print("Raw CSV data:")
    for key, value in first_row.items():
        print(f"  {key}: {value} (type: {type(value)})")
    
    print("\n" + "=" * 60)
    print("CONSTRUCTED PAYLOAD")
    print("=" * 60)
    
    payload = construct_payload(first_row)
    print(json.dumps(payload, indent=2, default=str))
    
    print("\n" + "=" * 60)
    print("API RESPONSE")
    print("=" * 60)
    
    response = send_request(first_row)
    print(json.dumps(response, indent=2, default=str))
    
    return response

def test_postal_code_formatting():
    """Test postal code formatting specifically"""
    print("\n" + "=" * 60)
    print("TESTING POSTAL CODE FORMATTING")
    print("=" * 60)
    
    df = pd.read_csv('data/testdata.csv')
    
    print("Postal codes in dataset:")
    for i, row in df.head(10).iterrows():
        postal = row['postal_code']
        postal_str = str(postal)
        print(f"  Row {i}: '{postal}' -> '{postal_str}' (original type: {type(postal)})")
        
        # Test if leading zeros are preserved
        if len(postal_str) < 5:
            print(f"    ⚠️  WARNING: Postal code too short! Should be 5 digits.")

def test_working_payload():
    """Test with a known working payload"""
    print("\n" + "=" * 60)
    print("TESTING KNOWN WORKING PAYLOAD")
    print("=" * 60)
    
    test_data = {
        "name": "Test User",
        "income": 50000,
        "employment_status": "employed",
        "employment_duration_years": 5,
        "existing_loans": 1,
        "loan_amount": 10000,
        "credit_limit": 20000,
        "used_credit": 5000,
        "payment_defaults": 0,
        "credit_inquiries_last_6_months": 1,
        "housing_status": "owner",
        "address_stability_years": 3,
        "household_size": 2,
        "age": 30,
        "gender": "male",
        "nationality": "DE",  # Using ISO code
        "ethnicity": "white",
        "disability_status": "none",
        "education_level": "bachelor_degree",
        "marital_status": "single",
        "postal_code": "12345",  # Proper 5-digit postal code
        "language_preference": "de"
    }
    
    print("Test payload:")
    payload = construct_payload(test_data)
    print(json.dumps(payload, indent=2))
    
    print("\nAPI Response:")
    response = send_request(test_data)
    print(json.dumps(response, indent=2, default=str))

if __name__ == "__main__":
    print("🔍 API DEBUG SCRIPT")
    print("=" * 60)
    
    # Test postal code formatting first
    test_postal_code_formatting()
    
    # Test with known working payload
    test_working_payload()
    
    # Test with actual CSV data
    test_single_record()
