import os
from datetime import datetime, timedelta
import instructor
import google.generativeai as genai
from pydantic import BaseModel
from dotenv import load_dotenv


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
Pydantic Models
---------------
"""

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

"""
LLM Request Handling
---------------------
"""

def make_llm_request(prompt: str, response_model=LLMResponse) -> LLMResponse:
    """
    Makes an LLM request using the provided prompt and expects a response of type LLMResponse.
    """
    messages = [{
        'role': 'system',
        'content': '''You are an Event Scheduling Assistant. Your job is to analyze user input related to scheduling tasks, meetings, and reminders, and extract relevant information like event name, date, time, location, attendees, time zone, and optional description.

        Required fields:
        - Event title (eventName)
        - Start date (eventDate)
        - Start time (eventStartTime)
        - End time (eventEndTime)
        - Location (location)
        - Time zone (timeZone)

        Optional fields:
        - Description (description)
        - Attendees (attendees)

        Example Input: 
        "Schedule a meeting with John tomorrow at 7 PM at the office."


        Example Output:
        [
            {"eventName": "Meeting with John", "eventDate": "2024-09-02", "eventTime": "19:00", "location": "Office", "description": "Discuss project updates."}
        ]

        "Bad" Example Input:
        "Midterm"

        - This does not give enough context: The output should be:
        Example Output:
        [
            {"eventName": "Midterm", "eventDate": "", "eventTime": "", "location": "", "description": ""}
        ]         
        assume the time zone is New York's timezone, whatever that may be, unless otherwise stated 
        **if there is not fields present in the user's response, leave that portion empty instead of autofilling it***
        If the user does not provide enough input for a reasonable output, output empty portions

        '''
        
    }]
    
    messages.append({
        'role': 'user',
        'content': prompt
    })
    
    # Send request to the LLM
    resp = client.chat.completions.create(
        messages=messages,
        response_model=response_model
    )
    return resp

def ask_for_missing_fields(event_data: dict) -> dict:
    """
    Check if any required fields are missing from the user-provided event data.
    Prompt the user for missing information until all required fields are fulfilled.
    """
    required_fields = ['eventName', 'eventDate', 'eventStartTime', 'eventEndTime', 'location', 'timeZone']
    print("accessing askformissingfields")
    
    while True:
        missing_fields = [field for field in required_fields if not event_data.get(field)]
        
        if not missing_fields:
            print("Not missing fields.")
            break

        for field in missing_fields:
            if field == 'eventName':
                event_data['eventName'] = input("What is the event title? ")

            elif field == 'eventDate':
                date_input = input("When is the event taking place? (e.g., 'October 5, 2024') ")
                event_data['eventDate'] = date_input

            elif field == 'eventStartTime':
                time_input = input("What time does the event start? (e.g., '19:00') ")
                event_data['eventStartTime'] = time_input
            elif field == 'eventEndTime':
                time_input = input("What time does the event end? (e.g., '21:00') ")
                event_data['eventEndTime'] = time_input

            elif field == 'location':
                event_data['location'] = input("Where is the event taking place? ")

            elif field == 'timeZone':
                event_data['timeZone'] = input("What is the time zone of the event? (e.g., 'America/New_York') ")

    return event_data

def update_event_with_llm(original_event: EventDetails, updated_data: dict) -> EventDetails:
    """
    Sends the original event and updated information to the LLM for modification.
    """
    prompt = f"Update the following event details based on new information:\n" \
             f"Original Event: {original_event}\n" \
             f"New Details: {updated_data}\n" \
             f"Please provide the updated event details. Also, update all categories of information in a way that will be legible to Google Calendar API"
    
    updated_event_response = make_llm_request(prompt, LLMResponse)

    return updated_event_response.response[0]

def format_event_for_google_calendar(llm_response: LLMResponse) -> dict:
    if not llm_response.response:
        raise ValueError("No event details found in the LLM response.")
    
    event = llm_response.response[0]  

    start_time_str = f"{event.eventDate}T{event.eventStartTime}:00" 
    end_time_str = f"{event.eventDate}T{event.eventEndTime}:00"      

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
Event Scheduling Function
--------------------------
"""

def schedule_event(user_input: str) -> LLMResponse:
    """
    Prepares the prompt and schedules the event using the LLM.
    """
    # Create the LLM prompt with the user input
    prompt = user_input
    
    # Call the LLM to generate the initial event details
    llm_response = make_llm_request(prompt, LLMResponse)
    
    # Check for missing fields and ask the user repeatedly until all required fields are filled
    for event in llm_response.response:
        event_data = event.model_dump()
        event_data = ask_for_missing_fields(event_data)
        
        # Update the event details using the LLM
        updated_event = update_event_with_llm(event, event_data)
        
        # Replace the old event in the response with the updated event
        llm_response.response[llm_response.response.index(event)] = updated_event

    return llm_response

def format_event_for_google_calendar(LLMResponse: LLMResponse) -> dict:
    # Create the start and end datetime objects using the updated fields
    event = LLMResponse.response[0]

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

def display_event_details(llm_response: LLMResponse):
    """
    Displays the suggested event details.
    """
    for event in llm_response.response:
        print(f"Event: {event.eventName}")
        print(f"  Date: {event.eventDate}")
        print(f"  Start: {event.eventStartTime}")
        print(f"  End: {event.eventEndTime}")

        print(f"  Location: {event.location}")
        if event.description:
            print(f"  Description: {event.description}")
        if event.attendees:
            print(f"  Attendees: {', '.join(event.attendees)}")
        print(f"  Time Zone: {event.timeZone}")


"""
Main Execution Flow
-------------------
"""

if __name__ == "__main__":
    # Example user input for scheduling a generic event
    user_input = input("Enter an event to schedule (e.g., 'Schedule a meeting with John at 7 PM tomorrow at the office'): ")
    
    # Schedule the event with the LLM
    llm_response = schedule_event(user_input)
    
    # Display the event details
    display_event_details(llm_response)

    print(format_event_for_google_calendar(llm_response))
