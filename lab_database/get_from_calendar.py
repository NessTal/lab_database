"""
Shows basic usage of the Google Calendar API. Creates a Google Calendar API
service object and outputs a list of the next 10 events on the user's calendar.
"""
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
#import datetime

from back_end import *

# Setup the Calendar API
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))

def calender_to_db():
    # Call the Calendar API
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_start = tomorrow.isoformat() + 'T00:00:00.000000Z'
    tomorrow_end = tomorrow.isoformat() + 'T23:59:59.999999Z'
    #now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    #print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='m1bqm0kctr5olblnutmshnvs4k@group.calendar.google.com',
                                          timeMin=tomorrow_start, timeMax=tomorrow_end,
                                          singleEvents=True,orderBy='startTime').execute()

    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        L = event['summary'].split(' - ') + event['description'].split(' - ')
        if len(L) == 4:
            D = {'experiment_name': L[0], 'first_name': L[1].split(' ')[0], 'last_name': L[1].split(' ')[1],
                 'subject_ID': L[2], 'mail': L[3]}
            start = event['start'].get('dateTime', event['start'].get('date'))
            D['date'] = start.split('T')[0]
            D['scheduled_time'] = start.split('T')[1].split('+')[0][:5]
            add_or_update(D)
            print(D)

