from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import datetime
from datetime import timedelta, datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import logging
from google.oauth2.credentials import Credentials
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# initilize the flask app
app = Flask(__name__)

# Load OpenAI API key
with open(r"C:\Users\Issei\Documents\API Tokens\ChatGPT.txt", 'r') as file:
    OPENAI_API_KEY = file.read().rstrip()

client = OpenAI(api_key=OPENAI_API_KEY)

# Load Google Calendar API credentials
creds = None

flow = InstalledAppFlow.from_client_secrets_file(
    r"C:\Users\Issei\Documents\API Tokens\CalenderSecretary\client_secret_630503106817-im66k9rhjgpu3us9b8dvkhsi4j9qku7d.apps.googleusercontent.com.json",
    scopes=['https://www.googleapis.com/auth/calendar']
)
creds = flow.run_local_server(port=8080)
with open('token.json', 'w') as token:
    token.write(creds.to_json())

# Create a service object for interacting with the API
service = build('calendar', 'v3', credentials=creds)

# Schedule parsing
def parse_schedule(user_input):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                'role': 'system',
                'content': f"""
                Extract the event details from input and 'today' is {datetime.today().strftime('%Y-%m-%d')}.
                Output Format: {{"date": "YYYY-MM-DD", "time": "HH:MM:SS", "event": "Event Name"}}
                """
            },
            {
                'role': 'user',
                'content': str(user_input)
            }
        ],
        max_tokens=100
    )
    try:
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

# Add event to Google Calendar  
def add_event(date, time, event_name):
    start_time = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M:%S')
    end_time = start_time + timedelta(hours=1)
    event = {
        'summary': event_name,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Asia/Tokyo'
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Asia/Tokyo'
        }
    }
    return service.events().insert(calendarId='primary', body=event).execute()
    
# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Api endpoint for chatbot
@app.route('/schedule', methods=['POST'])
def schedule():
    data = request.json
    user_input = data.get('input')

    # Parse the schedule
    parsed = parse_schedule(user_input)
    if 'error' in parsed:
        return jsonify({'error': parsed['error']})
    
    # Add event to Google Calendar
    try:
        created_event = add_event(parsed['date'], parsed['time'], parsed['event'])
        return jsonify({'response': f"Event '{parsed['event']}' added to your calendar on {parsed['date']} at {parsed['time']}."})
    except Exception as e:
        return jsonify({'error': str(e)})
    
if __name__ == '__main__':
    app.run(debug=True)