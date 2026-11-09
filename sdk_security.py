import requests
import hmac
import hashlib
import json


BASE_URL = "http://localhost:8000"
SECRET_KEY = "TEMP_SEC_ID"


def generate_signature(payload_dict: dict) -> str:
    """ Helper to generate the correct signature """
    body_bytes = json.dumps(
        payload_dict, separators=(",", ":")).encode('utf-8')
    return hmac.new(SECRET_KEY.encode('utf-8'), body_bytes, hashlib.sha256).hexdigest()


def test_valid_request():
    print("\n--- Test 1: Valid Signed Request ---")
    payload = {
        "device_id": "dev_sim_1",
        "user_id": "user_sim_1",
        "session_id": "sess_1",
        "event_type": "login"
    }

    headers = {
        "X-Signature": generate_signature(payload),
        "Content-Type": "application/json"
    }

    response = requests.post(f"{BASE_URL}/events",
                             json=payload, headers=headers)
    print(f"Status: {response.status_code} | {response.json()}")


def test_missing_signature():
    print("\n--- Test 2: SDK Error - Missing Signature Header ---")
    payload = {
        "device_id": "dev_sim_2",
        "user_id": "user_sim_2",
        "session_id": "sess_2",
        "event_type": "login"
    }
    # Intentionally omitting the X-Signature header
    response = requests.post(f"{BASE_URL}/events", json=payload)
    print(f"Status: {response.status_code} | Response: {response.json()}")


def test_tampered_payload():
    print("\n--- Test 3: SDK Error - Tampered Payload (Signature Mismatch) ---")
    payload = {
        "device_id": "dev_sim_3",
        "user_id": "user_sim_3",
        "session_id": "sess_3",
        "event_type": "login"
    }
    # Generate signature for the original payload
    headers = {
        "X-Signature": generate_signature(payload),
        "Content-Type": "application/json"
    }
    # "Simulating" -> change the payload before sending! (Simulates a man-in-the-middle or buggy SDK)
    payload["user_id"] = "hacker_user"

    response = requests.post(f"{BASE_URL}/events",
                             json=payload, headers=headers)
    print(f"Status: {response.status_code} | Response: {response.json()}")


if __name__ == "__main__":
    """ Self Remainder: Run the main app before running!.. """
    test_valid_request()
    test_missing_signature()
    test_tampered_payload()
