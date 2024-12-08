from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']

def  get_calendar_service():
    flow = InstalledAppFlow.from_client_secrets_file(r"C:\Users\Issei\Documents\API Tokens\CalenderSecretary\client_secret_630503106817-im66k9rhjgpu3us9b8dvkhsi4j9qku7d.apps.googleusercontent.com.json", 
    SCOPES)
    creds = flow.run_local_server(port=8080)
    return build('calendar', 'v3', credentials=creds)

