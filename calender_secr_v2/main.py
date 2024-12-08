from calender_secr_v2 import app
from flask import Blueprint, jsonify, render_template, url_for, redirect, request
from .calendar import get_calendar_service
from datetime import datetime, timedelta
import json
from openai import OpenAI

with open(r"C:\Users\Issei\Documents\API Tokens\ChatGPT.txt", 'r') as file:
    OPENAI_API_KEY = file.read().rstrip()

client = OpenAI(api_key=OPENAI_API_KEY)

def list_events(service):
    now = datetime.utcnow().isoformat() + 'Z'
    week_later = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now, timeMax=week_later, maxResults=5, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events

def add_event(service, title, start_time, end_time):
    event = {
        'summary': title,
        'start': {'dateTime': start_time, 'timeZone': 'UTC'},
        'end': {'dateTime': end_time, 'timeZone': 'UTC'}
    }
    service.events().insert(calendarId='primary', body=event).execute()

@app.route('/')
def index():
    service = get_calendar_service()
    events_raw = list_events(service)
    events = []
    for event in events_raw:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        events.append({'start': start, 'end': end, 'summary': event['summary']})

    return render_template('index.html', events=events)

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/schedule', methods=['POST'])
def add_schedule():
    user_input = request.form['schedule']
    response = client.chat.create()