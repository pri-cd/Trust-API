from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime



class EventPayload(BaseModel):
    """ Using this to define the basic structure for the JSON that Pydantic should allow.. """
    device_id: str = Field(..., description="Unique identifier for the device")
    user_id: str = Field(..., description="Unique identifier for the user")
    session_id: str
    event_type: str = Field(..., description="e.g., 'login', 'transaction', 'page_view'")

    """ Optional Fields (Set Default to None..)"""
    ip_address: Optional[str] = None 
    timestamp: Optional[str] = None


class EventResponse(BaseModel):
    status: str
    message: str
    event_id: Optional[int] = None