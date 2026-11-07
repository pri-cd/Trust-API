from fastapi import FastAPI, HTTPException
from models import EventPayload, EventResponse
from contextlib import asynccontextmanager
from db import init_db, save_event
from fraud_engine import evaluate_fraud_rules


@asynccontextmanager
async def startup_event(app: FastAPI):
    """ Runs on startup of the app. (Initialising DB, etc.) """
    init_db()
    print("Initialising Database [Done]")

    """ Halt the function until shutdown.. (Instead of depreciated .on_event() I was using earlier) """
    yield

    print("Shutting down")

app = FastAPI(title="TrustScore Fraud API", version="1.0.0", lifespan=startup_event)


@app.post("/events", response_model=EventResponse, status_code=201)
async def create_event(payload: EventPayload):
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
