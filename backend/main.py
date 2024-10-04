import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.gcal.upload import handleCalendar
from src.llm.models import QueryBody
from src.llm.request import scheduleEvent

app = FastAPI()

@app.get("/")
def read_root():
   return {"Welcome to": "My first FastAPI depolyment"}

@app.post("/scheduleEvent")
def scheduleEventAPI(query: QueryBody):
    result = scheduleEvent(query.prompt)
    # The API would return the missing fields, and then the FE would handle asking follow ups
    # After all follow ups have been asked, the new event prompt would be passed to the API
    if result["verbalStatus"] == "MISSING":
        return JSONResponse(status_code=400, content={'status': 400, "message": result["missingFields"]})
    elif result["verbalStatus"] == "SUCCESS":
        handleCalendar(result["details"], query.accessToken)
        return JSONResponse(status_code=200, content={'status': 200, "eventDetails": result["details"]})

if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8080)

