from datetime import datetime, timedelta
import json
import os
from fastapi import HTTPException
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

calendarName = "ProcrastiNot"

def create_event_times(event_details):
    # Extract details
    start_date = event_details["suggestedStartDate"]
    start_time = event_details["suggestedStartTime"]
    duration_minutes = event_details["duration"]

    # Combine date and time into a datetime object
    start_datetime_str = f"{start_date} {start_time}"
    start_datetime = datetime.strptime(start_datetime_str, "%Y-%m-%d %H:%M")

    # Calculate the end time by adding the duration
    end_datetime = start_datetime + timedelta(minutes=duration_minutes)

    # Convert both to RFC3339 format with timezone (assuming UTC for simplicity)
    start_time_rfc3339 = start_datetime.isoformat() + "Z"  # Add 'Z' for UTC timezone
    end_time_rfc3339 = end_datetime.isoformat() + "Z"

    return {
        "start": {
            "dateTime": start_time_rfc3339,
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": end_time_rfc3339,
            "timeZone": "UTC"
        }
    }



def getToken(path):
       # Check if the token.json file exists
    if os.path.exists(path):
        with open(path, "r") as token_file:
            # Load the JSON data from the file
            token_data = json.load(token_file)
            
            # Extract the access token
            access_token = token_data.get('token')  # Change this key based on your token.json structure

            if access_token:
                # Call the generateController function with the access token
              return access_token
            else:
                raise Exception("Access token not found in token.json.")
    else:
        raise Exception("token.json file not found.")

def createOrClearCalender(service):
    if not service:
      raise HTTPException(status_code=400, detail="API Service is required.")

    calendarList = service.calendarList().list().execute()

    # Check if the 'items' key exists and contains calendars
    if "items" in calendarList and len(calendarList["items"]) > 0:
        print("Items in list:", len(calendarList["items"]))
        # Iterate through the list of calendars
        for calendar in calendarList["items"]:
            print(calendar["summary"])
            # Check if the calendar summary matches "Test"
            if calendar["summary"] == calendarName:
                print(calendar["id"])
                service.calendars().delete(calendarId=calendar["id"]).execute()

    calendar = {
    'summary': calendarName,
    'timeZone': 'America/New_York'
    }

    createdCalendar = service.calendars().insert(body=calendar).execute()
    service.calendarList().insert(body = {"id": createdCalendar["id"]}).execute()
    return createdCalendar["id"]

def createEvent(service, calendarId, events):
  if not service:
    raise HTTPException(status_code=400, detail="Service is required.")

  try:
    # Call the Calendar API to create the event
    event = service.events().insert(calendarId=calendarId, body=events).execute()

    return {
        "eventId": event['id'],
        "status": "Event created successfully",
        "event": event
    }

  except HttpError as e:
      raise HTTPException(status_code=e.resp.status, detail=f"An error occurred: {e}")
  except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))