from fastapi import FastAPI, HTTPException, Request, Depends
from contextlib import asynccontextmanager

from models import EventPayload, EventResponse
from db import init_db, save_event
from fraud_engine import evaluate_fraud_rules
from security import verify_signature


@asynccontextmanager
async def startup_event(app: FastAPI):
    """ Runs on startup of the app. (Initialising DB, etc.) """
    init_db()
    print("Initialising Database [Done]")

    """ Halt the function until shutdown.. (Instead of depreciated .on_event() I was using earlier) """
    yield

    print("Shutting down")

app = FastAPI(title="TrustScore Fraud API", version="1.0.0", lifespan=startup_event)

async def get_raw_body(request: Request) -> bytes:
    return await request.body()

@app.post("/events", response_model=EventResponse, status_code=201)
async def create_event(
    payload: EventPayload,
    request: Request,
    raw_body: bytes = Depends(get_raw_body),
    is_valid: bool = Depends(lambda r, b: verify_signature(r, b))
    ):
    """ Endpoint: Receive/Validate session events. """
    try:

        """
        > Convert model to average dict,
        > 
        """
        reasons = evaluate_fraud_rules(payload.user_id, payload.device_id)
        event_dict = payload.model_dump()
        event_id = save_event(event_dict)
        print ("Event Recieved: \n ", event_dict)

        return EventResponse(
            status='success',
            message='Event recorded successfully',
            event_id=event_id,
            reason_codes=reasons)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")



    