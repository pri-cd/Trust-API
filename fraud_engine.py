import redis
from db import is_new_device

CODE_NEW_DEVICE = "NEW_DEVICE_001"
CODE_HIGH_VELOCITY = "HIGH_VELOCITY_002"

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def evaluate_fraud_rules(user_id: str, device_id: str) -> list[str]:
    """
    > Evaluate income events against fraud rules
    > Return a list of reason codes (If any?)
    """

    reason_codes = []
    if (is_new_device(device_id=device_id)):
        reason_codes.append(CODE_NEW_DEVICE)

    velocity_key = f"velocity:{user_id}"
    current_count = redis_client.incr(velocity_key)

    if (current_count == 1):
        """ If this is the first time user is in the window? Set an expiration"""
        redis_client.expire(velocity_key, 60)

    if (current_count > 3):
        """ Flag if the user is performing > 3 events.. """
        reason_codes.append(CODE_HIGH_VELOCITY)
    return reason_codes
