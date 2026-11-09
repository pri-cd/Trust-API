import hmac
import hashlib
import json
from fastapi import HTTPException, Request


SECRET_KEY = "TEMP_SEC_ID"

async def verify_signature(request: Request, body: bytes):
    """
    > Verifies that the incoming request has a valid HMAC-SHA256 signature.
        > Gets signature from headers,
        > Generate an expected signature on our end using request body & secret
        > Compare them securely.
    """

    client_signature = request.headers.get('X-Signature')

    if not client_signature:
        raise HTTPException(status_code=401, detail="Missing X-Signature header")

    expected_signature = hmac.new(SECRET_KEY.encode('utf-8'), body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(client_signature, expected_signature): 
        raise HTTPException(status_code=403, detail="Invalid signature, Request tampered!")

    return True