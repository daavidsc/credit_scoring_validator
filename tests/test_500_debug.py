#!/usr/bin/env python3
"""
Test API with minimal payloads to isolate 500 errors
"""

import requests
from requests.auth import HTTPBasicAuth
import json

API_URL = "https://verbose-space-journey-7x4gr9xx4xwfw4r7-8000.app.github.dev"
USERNAME = "FS_Group4"
PASSWORD = "ExpLearn123"

def test_minimal_request():
    """Test with the most minimal possible payload"""
    
    # Start with the successful payload from earlier
    minimal_payload = {
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
        "protected_attributes": {
            "age": 30,
            "gender": "male",
            "nationality": "DE",
            "ethnicity": "white",
            "disability_status": "none",
            "education_level": "bachelor_degree",
            "marital_status": "single",
            "postal_code": "12345",
            "language_preference": "de"
        }
        # NOTE: Removed scoring_parameters to see if that's causing the issue
    }
    
    print("🔍 Testing minimal payload (without scoring_parameters)...")
    print(json.dumps(minimal_payload, indent=2))
    
    try:
        response = requests.post(
            f"{API_URL}/score",
            json=minimal_payload,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=30
        )
        
        print(f"\n✅ Response: {response.status_code} - {response.reason}")
        print(f"Content: {response.text[:500]}...")
        
        if response.status_code == 200:
            result = response.json()
            print("\n🎉 SUCCESS!")
            print(json.dumps(result, indent=2))
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_with_scoring_params():
    """Test with scoring parameters included"""
    
    payload_with_params = {
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
        "protected_attributes": {
            "age": 30,
            "gender": "male",
            "nationality": "DE",
            "ethnicity": "white",
            "disability_status": "none",
            "education_level": "bachelor_degree",
            "marital_status": "single",
            "postal_code": "12345",
            "language_preference": "de"
        },
        "scoring_parameters": {
            "model": "gpt-4.1-mini-2025-04-14",
            "temperature": 1,
            "top_p": 1,
            "max_tokens": 512,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "seed": 0
        }
    }
    
    print("\n🔍 Testing with scoring_parameters...")
    
    try:
        response = requests.post(
            f"{API_URL}/score",
            json=payload_with_params,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=30
        )
        
        print(f"\n✅ Response: {response.status_code} - {response.reason}")
        print(f"Content: {response.text[:500]}...")
        
        if response.status_code == 200:
            result = response.json()
            print("\n🎉 SUCCESS!")
            print(json.dumps(result, indent=2))
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 API 500 ERROR DEBUGGING")
    print("=" * 60)
    
    # Try minimal first
    success1 = test_minimal_request()
    
    if success1:
        print("\n✅ Minimal payload works, trying with scoring parameters...")
        success2 = test_with_scoring_params()
    else:
        print("\n❌ Even minimal payload fails - API server may be down")
