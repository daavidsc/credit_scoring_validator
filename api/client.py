# api/client.py

import requests
from requests.auth import HTTPBasicAuth
from config import API_URL, USERNAME, PASSWORD
from utils.logger import setup_logger

logger = setup_logger("api_client", "results/logs/api_client.log")


def send_request(payload: dict) -> dict:
    """
    Sends a single data row to the credit scoring API and returns the response.

    :param payload: A dictionary representing one credit scoring input
    :return: A dictionary with the API's response or error info
    """
    try:
        response = requests.post(
            API_URL,
            json=payload,
            auth=HTTPBasicAuth(USERNAME, PASSWORD)
        )
        response.raise_for_status()
        logger.info(f"Successfully sent request for: {payload}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API error for payload {payload}: {e}")
        return {"error": str(e)}
