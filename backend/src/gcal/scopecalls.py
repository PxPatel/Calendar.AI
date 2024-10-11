import datetime
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import BaseModel
import json

# Define SCOPES for Google Calendar API
SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.events"]

# Define the FastAPI app
app = FastAPI()

# Path to store the token.json on the user's local machine
TOKEN_FILE = "token.json"
CLIENT_SECRETS_FILE = "credentials.json"  # Make sure you have this file in your project directory

# A model to represent token data
class TokenData(BaseModel):
    token: str

# Google Calendar API token management for web flow
def get_credentials():
    creds = None
    # If token.json exists, use it to create credentials
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid credentials available, start the login flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            raise HTTPException(status_code=401, detail="User not authenticated. Please authenticate.")
    
    return creds

# Route to generate Google authentication URL for web-based flow
@app.get("/generate-auth-url")
async def generate_auth_url():
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri="http://localhost:8000/callback"  # Ensure this matches your Google app's authorized redirect URI
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate auth URL")

# Route to handle the callback from Google and store the token
# Route to handle the callback from Google and store the token
@app.get("/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return {"error": "No authorization code provided"}

    try:
        # Initialize the Flow object
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri="http://localhost:8000/callback"
        )
        
        # Exchange authorization code for access token
        flow.fetch_token(code=code)
        
        # Get credentials
        creds = flow.credentials
        
        # Save the credentials for future use
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())

        # Ensure you are using the correct property to get the token
        access_token = creds.token

        # Redirect to the frontend with the access token properly encoded
        frontend_url = f"http://localhost:3000/chatbot?access_token={access_token}"
        print("Redirecting to:", frontend_url)  # Log the URL
        return RedirectResponse(url=frontend_url)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during callback: {e}")
    
# Route to get the next 10 events from Google Calendar
@app.get("/get-events")
async def get_events():
    try:
        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API to get events
        now = datetime.datetime.utcnow().isoformat() + "Z"
        events_result = service.events().list(
            calendarId="primary", timeMin=now, maxResults=10, singleEvents=True, orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])

        if not events:
            return {"message": "No upcoming events found"}

        # Format the events
        event_list = [{"start": event["start"].get("dateTime", event["start"].get("date")), "summary": event["summary"]} for event in events]

        return {"events": event_list}

    except HttpError as error:
        raise HTTPException(status_code=500, detail=f"An error occurred: {error}")

# Optional route for testing token storage (for web token persistence)
@app.post("/store-token")
async def store_token(token_data: TokenData):
    try:
        token_info = token_data.token
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(json.dumps(token_info))
        return {"message": "Token saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save token")
