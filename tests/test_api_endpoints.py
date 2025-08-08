#!/usr/bin/env python3
"""
Test API endpoints to find the correct one
"""

import requests
from requests.auth import HTTPBasicAuth
import json

# API configuration
API_URL = "https://verbose-space-journey-7x4gr9xx4xwfw4r7-8000.app.github.dev"
USERNAME = "FS_Group4"
PASSWORD = "ExpLearn123"

def test_endpoints():
    """Test various possible API endpoints"""
    
    endpoints_to_test = [
        "/score",
        "/predict/score", 
        "/api/score",
        "/v1/score",
        "/scoring",
        "/predict",
        "/",
        "/health",
        "/docs"
    ]
    
    print("🔍 Testing API endpoints...")
    print(f"Base URL: {API_URL}")
    print(f"Auth: {USERNAME} / {PASSWORD}")
    print("=" * 60)
    
    for endpoint in endpoints_to_test:
        url = f"{API_URL}{endpoint}"
        print(f"\n🔗 Testing: {endpoint}")
        
        try:
            # Try GET first
            response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), timeout=10)
            print(f"  GET {response.status_code}: {response.reason}")
            if response.status_code == 200:
                try:
                    content = response.text[:200] + "..." if len(response.text) > 200 else response.text
                    print(f"  Content: {content}")
                except:
                    print(f"  Content length: {len(response.text)} bytes")
            
        except requests.RequestException as e:
            print(f"  GET ERROR: {e}")
        
        # Try POST for scoring endpoints
        if "score" in endpoint or endpoint in ["/predict", "/"]:
            try:
                test_payload = {
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
                
                response = requests.post(
                    url, 
                    json=test_payload,
                    auth=HTTPBasicAuth(USERNAME, PASSWORD), 
                    timeout=30
                )
                print(f"  POST {response.status_code}: {response.reason}")
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        print(f"  ✅ SUCCESS! Response: {json.dumps(result, indent=2)[:300]}...")
                        return url  # Return successful endpoint
                    except:
                        print(f"  Response not JSON: {response.text[:200]}...")
                elif response.status_code == 422:
                    print(f"  ⚠️  Validation error: {response.text[:200]}...")
                else:
                    print(f"  Response: {response.text[:200]}...")
                    
            except requests.RequestException as e:
                print(f"  POST ERROR: {e}")
    
    return None

def test_minimal_payload():
    """Test with a minimal payload to see what's required"""
    print("\n" + "=" * 60)
    print("🧪 Testing minimal payloads")
    print("=" * 60)
    
    base_url = f"{API_URL}/score"  # Try the most likely endpoint
    
    minimal_payloads = [
        # Very minimal
        {
            "name": "Test User",
            "income": 50000
        },
        # Basic financial data
        {
            "name": "Test User", 
            "income": 50000,
            "employment_status": "employed",
            "age": 30
        },
        # With protected attributes
        {
            "name": "Test User",
            "income": 50000,
            "employment_status": "employed",
            "protected_attributes": {
                "age": 30,
                "gender": "male",
                "nationality": "DE"
            }
        }
    ]
    
    for i, payload in enumerate(minimal_payloads):
        print(f"\n📋 Testing payload {i+1}:")
        print(json.dumps(payload, indent=2))
        
        try:
            response = requests.post(
                base_url,
                json=payload,
                auth=HTTPBasicAuth(USERNAME, PASSWORD),
                timeout=30
            )
            print(f"Response: {response.status_code} - {response.reason}")
            print(f"Content: {response.text[:300]}...")
            
        except requests.RequestException as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 API ENDPOINT DISCOVERY")
    print("=" * 60)
    
    successful_endpoint = test_endpoints()
    
    if not successful_endpoint:
        print("\n❌ No working endpoints found. Trying minimal payloads...")
        test_minimal_payload()
    else:
        print(f"\n✅ Found working endpoint: {successful_endpoint}")
