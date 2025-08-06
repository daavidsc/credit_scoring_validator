# api/client.py

import requests
from requests.auth import HTTPBasicAuth
from config import API_URL, USERNAME, PASSWORD
from utils.logger import setup_logger

logger = setup_logger("api_client", "results/logs/api_client.log")


SCORING_PARAMETERS = {
    "model": "openrouter/horizon-beta",
    "temperature": 1,
    "top_p": 1,
    "max_tokens": 512,
    "presence_penalty": 0,
    "frequency_penalty": 0,
    "seed": 0
}


def construct_payload(row: dict) -> dict:
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
            "postal_code": row.get("postal_code"),
            "language_preference": row.get("language_preference"),
        },
        "scoring_parameters": SCORING_PARAMETERS
    }


def send_request(row: dict) -> dict:
    payload = construct_payload(row)
    try:
        response = requests.post(
            f"{API_URL}/score",
            json=payload,
            auth=HTTPBasicAuth(USERNAME, PASSWORD)
            #verify="github_codespaces.crt"
        )
        response.raise_for_status()
        data = response.json()

        # Try extracting core prediction
        try:
            content = data["metadata"]["choices"][0]["message"]["content"]
            parsed_content = eval(content)  # ⚠️ Assumes it’s JSON string in string form
        except Exception as e:
            logger.warning(f"Could not parse content from message: {e}")
            parsed_content = {}

        # Log core info
        logger.info(f"[{row.get('name')}] → Score: {parsed_content.get('credit_score')} | "
                    f"Class: {parsed_content.get('classification')} | "
                    f"Reason: {parsed_content.get('explanation')}")

        return {
            "raw_response": data,
            "parsed": parsed_content
        }

    except requests.RequestException as e:
        logger.error(f"API error for row {row.get('name')}: {e}")
        return {
            "error": str(e),
            "payload": payload
        }
