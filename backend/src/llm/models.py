from pydantic import BaseModel

class EventDetails(BaseModel):
    eventName: str
    eventDate: str
    eventStartTime: str
    eventEndTime: str
    description: str = None
    location: str = None  # Added for location
    attendees: list = None      # Added for attendees
    timeZone: str = None  # Added for time zone

class LLMResponse(BaseModel):
    response: list[EventDetails]

class QueryBody(BaseModel):
    prompt: str
    accessToken: str
