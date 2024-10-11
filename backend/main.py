import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from src.gcal.upload import handleCalendar
from src.llm.models import QueryBody
from src.llm.request import scheduleEvent
from src.gcal.scopecalls import generate_auth_url, auth_callback, get_events, TOKEN_FILE, TokenData  # Import methods from scopecalls.py
from fastapi.middleware.cors import CORSMiddleware

# Define the FastAPI app
app = FastAPI()

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"Welcome to": "My first FastAPI deployment"}

@app.post("/scheduleEvent")
def scheduleEventAPI(query: QueryBody):
    result = scheduleEvent(query.prompt)
    if result["verbalStatus"] == "MISSING":
        return JSONResponse(status_code=400, content={'status': 400, "message": result["missingFields"]})
    elif result["verbalStatus"] == "SUCCESS":
        handleCalendar(result["details"], query.accessToken)
        return JSONResponse(status_code=200, content={'status': 200, "eventDetails": result["details"]})

@app.get("/generate-auth-url")
async def generate_auth_url_api():
    try:
        auth_url = await generate_auth_url()  # Call the method from scopecalls.py
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate auth URL")

@app.get("/callback")
async def callback_api(request: Request):
    return await auth_callback(request)  # Call the callback handling method from scopecalls.py

@app.get("/get-events")
async def get_events_api():
    try:
        events = await get_events()  # Call the method to get events from scopecalls.py
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve events: {e}")

@app.post("/store-token")
async def store_token(token_data: TokenData):
    try:
        token_info = token_data.token
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(token_info)  # Store the token
        return {"message": "Token saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save token")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
