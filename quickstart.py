from __future__ import print_function
import datetime
import pickle
import os.path
from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pytz


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendar:
    home = str(Path.home())
    tokenpath = os.path.join(home, '.google', 'token.pickle')
    creds = None
    def __init__(self):
        if os.path.exists(self.tokenpath):
            self.creds = self._load_token();
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join(self.home, '.google', 'credentials.json'), SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.tokenpath, 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('calendar', 'v3', credentials=self.creds)

    def _load_token(self):
        with open(self.tokenpath, 'rb') as token:
            return pickle.load(token)

    def get_todays_events(self):
        now = datetime.datetime.now()
        # TODO: fix '-04:00' hack; replace with real timezone logic
        this_morning = datetime.datetime(now.year, now.month, now.day).isoformat() + '-04:00' # + 'Z'
        midnight = datetime.datetime(now.year, now.month, now.day, 23, 59).isoformat() + '-04:00' #  'Z'
        now = now.isoformat() + '-04:00' #  + 'Z'
        # TODO: consolidate duplicate events().list() logic
        events_result = self.service.events().list(calendarId='primary', timeMin=this_morning,
                                            timeMax=midnight, singleEvents=True,
                                            orderBy='startTime').execute()
        return events_result.get('items', [])
        

    def get_current_events(self):
        now = datetime.datetime.now(pytz.utc)
        todays_events = self.get_todays_events()
        events_occurring_now = list(filter(lambda event: datetime.datetime.fromisoformat(event['start'].get('dateTime')) < now and datetime.datetime.fromisoformat(event['end'].get('dateTime')) > now, todays_events))
        return events_occurring_now

    def get_upcoming_events(self):
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        # TODO: consolidate duplicate events().list() logic
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        return events_result.get('items', [])

    def print_events(self, events):
        if not events:
            print('No events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"{start} {event['summary']}")
        
        return events

def main():
    c = GoogleCalendar() 
    # upcoming_events = c.get_upcoming_events()
    current_events = c.get_current_events()
    c.print_events(current_events)
    
  
if __name__ == '__main__':
    main()
