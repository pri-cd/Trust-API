from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime



class EventPayload(BaseModel):
    """ Using this to define the basic structure for the JSON that Pydantic should allow.. """
    deviceID: str = Field(..., description="UID for device")
    userID: str = Field(..., description="UID for user")
    sessionID: str
    eventType: str = Field(..., description="e.g., 'login', 'transaction', 'pageView'")

    """ Optional Fields (Set Default to None..)"""
    ipAddr : Optional[str] = None
    timestamp: Optional[str] = None


class EventResponse(BaseModel):
    status: str
    message: str
    eventID: Optional[int] = None