from __future__ import print_function
import datetime
import pickle
import os.path
from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendar:
    home = str(Path.home())
    tokenpath = os.path.join(home, '.google', 'token.pickle')
    creds = None
    def __init__(self):
        if os.path.exists(self.tokenpath):
            with open(self.tokenpath, 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join(self.home, '.google', 'credentials.json'), SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(tokenpath, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=self.creds)

    def get_upcoming_events(self, verbose=False):
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])
        
        if verbose:
            if not events:
                print('No upcoming events found.')
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(start, event['summary'])
        
        return events

def main():
    c = GoogleCalendar() 
    c.get_upcoming_events()
    print(c)

if __name__ == '__main__':
    main()
