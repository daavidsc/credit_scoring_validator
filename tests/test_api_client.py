# tests/test_api_client.py

import pytest
import logging
from api.client import send_request

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_send_request_valid():
    # Simulated row dict (same format as a row from your CSV)
    sample_row = {
        "name": "Test User",
        "income": 50000,
        "employment_status": "employed",
        "employment_duration_years": 3,
        "existing_loans": 1,
        "loan_amount": 10000,
        "credit_limit": 15000,
        "used_credit": 5000,
        "payment_defaults": 0,
        "credit_inquiries_last_6_months": 1,
        "housing_status": "owner",
        "address_stability_years": 2,
        "household_size": 2,
        "age": 32,
        "gender": "male",
        "nationality": "german",
        "ethnicity": "white",
        "disability_status": "none",
        "education_level": "no_formal_education",
        "marital_status": "single",
        "postal_code": "12345",
        "language_preference": "de"
    }

    logger.info(f"🔍 Test input data: {sample_row}")
    
    result = send_request(sample_row)

    logger.info(f"🔍 API raw result: {result}")

    assert "parsed" in result
    parsed = result["parsed"]

    assert isinstance(parsed, dict)
    assert "credit_score" in parsed
    assert "classification" in parsed
    assert "explanation" in parsed

    logger.info(f"✅ API parsed response: {parsed}")
    print("✅ API response:", parsed)
