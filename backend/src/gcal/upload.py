import json
import os
from fastapi import HTTPException
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

calendarName = "Kale"

def getCalendarId(service):
    if not service:
      raise HTTPException(status_code=400, detail="API Service is required.")

    calendarList = service.calendarList().list().execute()

    # Check if the 'items' key exists and contains calendars
    if "items" in calendarList and len(calendarList["items"]) > 0:
        for calendar in calendarList["items"]:
            if calendar["summary"] == calendarName:
                return calendar["id"]
            
    calendar = {
    'summary': calendarName,
    'timeZone': 'America/New_York'
    }

    createdCalendar = service.calendars().insert(body=calendar).execute()
    service.calendarList().insert(body = {"id": createdCalendar["id"]}).execute()
    return createdCalendar["id"]

def createEvent(service, calendarId, event):
  if not service:
    raise HTTPException(status_code=400, detail="Service is required.")

  try:
    # Call the Calendar API to create the event
    event = service.events().insert(calendarId=calendarId, body=event).execute()

    return {
        "eventId": event['id'],
        "status": "Event created successfully",
        "event": event
    }

  except HttpError as e:
      raise HTTPException(status_code=e.resp.status, detail=f"An error occurred: {e}")
  except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
  

def handleCalendar(event, accessToken):
    # Create Credentials object using the access token
   creds = Credentials(token=accessToken)

   # Build the Google Calendar service
   service = build('calendar', 'v3', credentials=creds)
   calendarId = getCalendarId(service)

   res = createEvent(service, calendarId, event)
