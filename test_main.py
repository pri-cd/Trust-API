from fastapi.testclient import TestClient
from main import app
import redis
from fraud_engine import EventCode

client = TestClient(app)

redis_client = redis.Redis(host='localhost', port=6379,
                           db=0, decode_responses=True)


def setup_module():
    """ Runs once before the tests.. (delete DB so we can test the create event valid) """
    redis_client.flushdb()
    return


def test_create_event_valid():
    """
    > Test Case 1:
    Valid Payload should return 201 & NEW_DEVICE reason..
    """
    payload = {
        "device_id": "dev2_id",
        "user_id": "userX_id",
        "session_id": "sessionY_id",
        "event_type": "register"
    }

    response = client.post('/events', json=payload)

    assert response.status_code == 201
    data = response.json()
    print("Respone (TC1): \n", data)
    assert data["status"] == "success"
    assert EventCode.CODE_NEW_DEVICE.value in data["reason_codes"]
    return


def test_create_event_invalid_missing_field():
    """
    > Test Case 2:
    Missing required field should return 422 unprocessable entry.
    """
    payload = {
        """ Missing device ID.. """
        "user_id": "userX_id",
        "session_id": "sessionY_id",
        "event_type": "register"
    }

    response = client.post('/events', json=payload)

    """
    > Response Code : 422,
    > Check for missing "device_id" key?
    """
    assert response.status_code == 422
    assert "device_id" in response.text
    return


def test_create_event_high_velocity_boundary():
    """
    > Test Case 3:
    > Boundary Case: 4th event from every user will trigger HIGH_VELOCITY reason code.
    """
    user_id = "HIGH_VELOCITY_UID"

    for i in range(3):
        payload = {
            "device_id": "dev_vel{i}_id",
            "user_id": user_id,
            "session_id": f"session{i}X_id",
            "event_type": "click"
        }

        response = client.post('/events', json=payload)
        assert response.status_code == 201
        assert EventCode.CODE_HIGH_VELOCITY.value not in response.json()[
            'reason_codes']

    """ 4th event that should trigger high-velocity code! """
    payload4 = {
        "device_id": "dev_vel4_id",
        "user_id": user_id,
        "session_id": f"session{4}X_id",
        "event_type": "click"
    }

    response4 = client.post('/events', json=payload4)
    assert response4.status_code == 201
    assert EventCode.CODE_HIGH_VELOCITY.value in response4.json()['reason_codes'], "Expected HIGH_VELOCITY on 4th request"
