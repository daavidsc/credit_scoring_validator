# api/client.py

import requests
from requests.auth import HTTPBasicAuth
from config import API_URL, USERNAME, PASSWORD
from utils.logger import setup_logger
import json

logger = setup_logger("api_client", "results/logs/api_client.log")


def construct_payload(row: dict) -> dict:
    # Import config each time to get updated model value
    from config import MODEL
    
    scoring_parameters = {
        "model": MODEL,
        "temperature": 1,
        "top_p": 1,
        "max_tokens": 512,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "seed": 0
    }
    
    return {
        "name": row.get("name"),
        "income": row.get("income"),
        "employment_status": row.get("employment_status"),
        "employment_duration_years": row.get("employment_duration_years"),
        "existing_loans": row.get("existing_loans"),
        "loan_amount": row.get("loan_amount"),
        "credit_limit": row.get("credit_limit"),
        "used_credit": row.get("used_credit"),
        "payment_defaults": row.get("payment_defaults"),
        "credit_inquiries_last_6_months": row.get("credit_inquiries_last_6_months"),
        "housing_status": row.get("housing_status"),
        "address_stability_years": row.get("address_stability_years"),
        "household_size": row.get("household_size"),
        "protected_attributes": {
            "age": row.get("age"),
            "gender": row.get("gender"),
            "nationality": row.get("nationality"),
            "ethnicity": row.get("ethnicity"),
            "disability_status": row.get("disability_status"),
            "education_level": row.get("education_level"),
            "marital_status": row.get("marital_status"),
            "postal_code": str(row.get("postal_code")),
            "language_preference": row.get("language_preference"),
        },
        "scoring_parameters": scoring_parameters
    }


def send_request(row: dict) -> dict:
    payload = construct_payload(row)
    logger.info(f"🔍 Sending request for row: {row.get('name')} with payload: {payload}")
    try:
        # Import config each time to get updated values from Flask app
        from config import API_URL, USERNAME, PASSWORD
        
        response = requests.post(
            f"{API_URL}/score",
            json=payload,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            timeout=30
            #verify="github_codespaces.crt"
        )
        response.raise_for_status()
        data = response.json()

        # Handle the new API response format
        if "credit_score" in data:
            # New format: direct response with credit_score, classification, explanation
            parsed_content = {
                "credit_score": data.get("credit_score"),
                "classification": data.get("classification"),
                "explanation": data.get("explanation")
            }
        else:
            # Try old format if available
            try:
                content = data["metadata"]["choices"][0]["message"]["content"]
                parsed_content = eval(content)  # ⚠️ Assumes it's JSON string in string form
            except Exception as e:
                logger.warning(f"Could not parse content from message: {e}")
                parsed_content = {}

        # Log core info
        logger.info(f"[{row.get('name')}] → Score: {parsed_content.get('credit_score')} | "
                    f"Class: {parsed_content.get('classification')} | "
                    f"Reason: {parsed_content.get('explanation')}")

        return {
            "raw_response": data,
            "parsed": parsed_content,
            "status": "success",
            "status_code": response.status_code
        }

    except requests.HTTPError as e:
        error_details = {
            "error_type": "http_error",
            "error": str(e),
            "status_code": getattr(e.response, 'status_code', None),
            "payload": payload
        }
        logger.error(f"HTTP error for row {row.get('name')}: {e} (Status: {error_details['status_code']})")
        return error_details
    
    except requests.Timeout as e:
        error_details = {
            "error_type": "timeout",
            "error": str(e),
            "payload": payload
        }
        logger.error(f"Timeout error for row {row.get('name')}: {e}")
        return error_details
    
    except requests.ConnectionError as e:
        error_details = {
            "error_type": "connection_error",
            "error": str(e),
            "payload": payload
        }
        logger.error(f"Connection error for row {row.get('name')}: {e}")
        return error_details
    
    except requests.RequestException as e:
        error_details = {
            "error_type": "request_error",
            "error": str(e),
            "payload": payload
        }
        logger.error(f"Request error for row {row.get('name')}: {e}")
        return error_details
    
    except Exception as e:
        error_details = {
            "error_type": "unknown_error",
            "error": str(e),
            "payload": payload
        }
        logger.error(f"Unexpected error for row {row.get('name')}: {e}")
        return error_details
