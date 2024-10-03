import os
from datetime import datetime
import instructor
import google.generativeai as genai
from dotenv import load_dotenv

from src.llm.gemini import makeLLMRequest
from src.llm.models import EventDetails, LLMResponse

# Load environment variables
load_dotenv()

# Configure Google Generative AI with your API key
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
client = instructor.from_gemini(
    client=genai.GenerativeModel(
        model_name="models/gemini-1.5-flash-latest",
    ),
    mode=instructor.Mode.GEMINI_JSON,
)

"""
Event Scheduling Function
--------------------------
"""
def scheduleEvent(user_prompt: str) -> LLMResponse:
    """
    Prepares the prompt and schedules the event using the LLM.
    """
    # Create the LLM prompt with the user input
    prompt = user_prompt
    # Call the LLM to generate the initial event details
    llm_response = makeLLMRequest(prompt, client, LLMResponse)

    if not llm_response.response:
        raise ValueError("No event details found in the LLM response.")

    event_data = llm_response.response[0].model_dump()

    required_fields = ['eventName', 'eventDate', 'eventStartTime', 'eventEndTime', 'location', 'timeZone']
    missing_fields = [field for field in required_fields if not event_data.get(field)]

    if len(missing_fields) > 0:
        return {"verbalStatus": "MISSING", "missingFields": missing_fields}
    else:
        return {"verbalStatus": "SUCCESS", "details": formatEventForGCal(llm_response.response[0])}

    
def formatEventForGCal(event: EventDetails) -> dict:
    start_time_str = f"{event.eventDate}T{event.eventStartTime}:00"  # Using eventStartTime
    end_time_str = f"{event.eventDate}T{event.eventEndTime}:00"      # Using eventEndTime

    start_time = datetime.fromisoformat(start_time_str)
    end_time = datetime.fromisoformat(end_time_str)

    # Structure the event data according to Google Calendar API
    google_event = {
        "summary": event.eventName,
        "start": {
            "dateTime": start_time.isoformat(),  # ISO format required
            "timeZone": event.timeZone
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": event.timeZone
        },
        "description": event.description,
        "location": event.location,
        "attendees": [{"email": attendee} for attendee in event.attendees] if event.attendees else []
    }

    return google_event

"""
Main Execution Flow
-------------------
"""

if __name__ == "__main__":
    # Example user input for scheduling a generic event
    user_input = input("Enter an event to schedule (e.g., 'Schedule a meeting with John at 7 PM tomorrow at the office'): ")
    
    # Schedule the event with the LLM
    llm_response = scheduleEvent(user_input)