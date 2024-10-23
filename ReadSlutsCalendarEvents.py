import os
import pickle
import os.path
import asyncio
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from telegram import Bot
from telegram.constants import ParseMode


# Load environment variables from .env file
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = './client_credentials.json'

def get_calendar_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": CLIENT_ID,
                        "client_secret": CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
                    }
                },
                SCOPES
            )            
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service

async def list_calendar_events():
    service = get_calendar_service()
    
    # Get events for the current week
    time_min = datetime.now(timezone.utc).isoformat()
    time_max = (datetime.now(timezone.utc) + timedelta(weeks=1)).isoformat()
    events_result = service.events().list(calendarId='primary', timeMin=time_min, timeMax=time_max).execute()    
    events = events_result.get('items', [])
    # Sort events by start time
    events.sort(key=lambda event: event['start'].get('dateTime', event['start'].get('date')))
    await print_events(events, f"\nUpcoming events for this week:\n----------------------------------------------------\n\n")

    # shift time window to next week
    time_min = time_max
    time_max = (datetime.now(timezone.utc) + timedelta(weeks=2)).isoformat()
    events_result = service.events().list(calendarId='primary', timeMin=time_min, timeMax=time_max).execute()    

    events = events_result.get('items', [])
    # Sort events by start time
    events.sort(key=lambda event: event['start'].get('dateTime', event['start'].get('date')))
    await print_events(events, f"\nUpcoming events for the next week:\n-----------------------------------------------------------\n\n")

async def print_events(events, headermessage):
    message = headermessage
    for event in events:
        # convert start and end time to human-readable format
        stringStarttime = event['start'].get('dateTime', event['start'].get('date'))
        starttime = datetime.strptime(stringStarttime, '%Y-%m-%dT%H:%M:%S%z')
        friendlyStarttime = starttime.strftime(f'%A, %B {starttime.day}{get_ordinal_suffix(starttime.day)}, %#I:%M%p')
        stringEndTime = event['end'].get('dateTime', event['end'].get('date'))
        endtime = datetime.strptime(stringEndTime, '%Y-%m-%dT%H:%M:%S%z')
        friendlyEndtime = endtime.strftime(f'%A, %B {endtime.day}{get_ordinal_suffix(endtime.day)}, %#I:%M%p')
        # get location if available
        location = event.get('location', 'Location not specified')
        # add event details to message, separated by newline
        message += f"Event: {event['summary']}; Start: {friendlyStarttime}; End: {friendlyEndtime}; Location: {location} \n\n" 
        
    # send message to Telegram
    await send_telegram_message(message)

async def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.HTML)
    
# Helper function to determine ordinal suffix
def get_ordinal_suffix(day):
    if 10 <= day % 100 <= 20:
        return 'th'
    else:
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    

if __name__ == '__main__':
    asyncio.run(list_calendar_events())


# friendly_format = now.strftime(f'%A, %B {now.day}{get_ordinal_suffix(now.day)}, %#I:%M%p')
