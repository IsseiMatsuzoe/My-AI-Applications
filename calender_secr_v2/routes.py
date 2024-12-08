from flask import Blueprint, jsonify, render_template, url_for, redirect
from .calendar import get_calendar_service
from datetime import datetime, timedelta

routes = Blueprint('routes', __name__)

def list_events(service):
    now = datetime.utcnow().isoformat() + 'Z'
    week_later = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now, timeMax=week_later, maxResults=5, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    return events

@routes.route('/')
def index():
    service = get_calendar_service()
    events_raw = list_events(service)
    events = []
    for event in events_raw:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        events.append({
            'start': start,
            'end': end,
            'summary': event['summary']})
    return render_template('index.html', events=events)
