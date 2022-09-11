import os
from time import time
from exchangelib import Credentials, Account

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as gcreds
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import datetime
import argparse
import pytz

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def get_calendar_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = gcreds.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())


    service = build('calendar', 'v3', credentials=creds)
    return service


def already_exists(events, meeting, s) -> bool:
    for event in events:
        evStart = event['start'].get('dateTime', event['start'].get('date'))
        if evStart == s and event['summary'] == meeting.subject and event['location'] == meeting.location:
            print(f'Event "{meeting.subject}" already synced')
            return True

    return False

def to_timezone(date, timezone):
    d = datetime.datetime(date.year, date.month, date.day, date.hour, date.minute)
    p = pytz.utc.localize(d)

    return timezone.normalize(p)

def main():
    parser = argparse.ArgumentParser(description='Sync events from Microsoft Exchange to Google Calendar')
    parser.add_argument('-e', '--email', help='exchange email', required=True)
    parser.add_argument('-p', '--password', help='exchange password', required=True)
    parser.add_argument('--tz', help="timezone", default="Europe/Moscow")

    args = parser.parse_args()

    owa_creds = Credentials(args.email, args.password)
    account = Account(args.email, credentials=owa_creds, autodiscover=True)

    timezone = pytz.timezone(args.tz)
    start = datetime.datetime.now(timezone)

    end = start + datetime.timedelta(days=7)


    service = get_calendar_service()

    try:
        events_result = service.events().list(
            calendarId='primary', timeMin=start.isoformat(),
            timeMax=end.isoformat(), singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])

        for meeting in account.calendar.view(start=start, end=end):
            s = to_timezone(meeting.start, timezone).isoformat()
            e = to_timezone(meeting.end, timezone).isoformat()

            if already_exists(events, meeting, s):
                continue
                         
            event_result = service.events().insert(calendarId='primary',
                body={
                    "summary": meeting.subject,
                    "description": meeting.text_body,
                    "start": {"dateTime": s},
                    "end": {"dateTime": e},
                    "location": meeting.location,
                    "organizer": {"email": meeting.organizer.email_address, "displayName": meeting.organizer.email_address},
            }).execute()

            print(f'Event created = [id: {event_result["id"]}, summary: {event_result["summary"]}, starts: {event_result["start"]["dateTime"]}, ends: {event_result["end"]["dateTime"]}, location: {event_result["location"]}]')

    except HttpError as error:
        print('An error occurred: %s' % error)

if __name__=="__main__":
    main()
