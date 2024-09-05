#user model for database
from typing import List, Optional
from pydantic import BaseModel

class Event(BaseModel):
    id: str
    summary: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start: dict  # Should include fields like 'dateTime' or 'date'
    end: dict    # Should include fields like 'dateTime' or 'date'
    attendees: Optional[List[dict]] = None
    organizer: Optional[dict] = None
    recurrence: Optional[List[str]] = None
    reminders: Optional[dict] = None
    type: str

class EventList(BaseModel):
    events: List[Event]
