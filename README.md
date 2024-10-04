curl -X POST "http://127.0.0.1:8000/scheduleEvent" \
-H "Content-Type: application/json" \
-d '{"prompt": "schedule a meeting with John on 10/04/2024, from 10am to 11am, at the office.", "accessToken": "your_token_here"}'
