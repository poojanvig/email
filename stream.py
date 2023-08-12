from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os.path
import pickle

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('calendar', 'v3', credentials=creds)

# Call the Calendar API
now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

print('Getting the upcoming 10 events')
events_result = service.events().list(calendarId='primary', timeMin=now,
                                      maxResults=10, singleEvents=True,
                                      orderBy='startTime').execute()
events = events_result.get('items', [])

if not events:
    print('No upcoming events found.')
for event in events:
    start = event['start'].get('dateTime', event['start'].get('date'))
    print(start, event['summary'])
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pickle


# Load the credentials from the 'token.pickle' file
with open('token.pickle', 'rb') as token:
    creds = pickle.load(token)

# Build the service
service = build('calendar', 'v3', credentials=creds)

# Define the start and end times
start_time = datetime(2023, 7, 28, 19, 30)  # July 30, 2023, 14:30
end_time = datetime(2023, 7, 28, 21, 30)  # July 30, 2023, 15:30

# Create the event
event = {
    'summary': 'Demo Event', # add your event data
    'start': {
        'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': 'UTC+5:30',
    },
    'end': {
        'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': 'UTC+5:30',
    },
    'conferenceData': {
        'createRequest': {
            'requestId': 'sample123',  # You can generate or increment this for unique requests
            'conferenceSolutionKey': {
                'type': 'hangoutsMeet'
            }
        }
    },
    'attendees': [
        {'email': 'poojanvig.pv@gmail.com'},
        {'email': 'poojan.vig15991@sakec.ac.in'},
    ],
    'reminders': {
        'useDefault': False,
        'overrides': [
            {'method': 'email', 'minutes': 36 * 60},
            {'method': 'popup', 'minutes': 10},
        ],
    },
}

# Insert the event
event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()

print('Event created: %s' % (event.get('htmlLink')))
event_link = event.get('htmlLink')
event_summary = event.get('summary')
start_time = event['start'].get('dateTime')
end_time = event['end'].get('dateTime')
attendees = [attendee['email'] for attendee in event.get('attendees', [])]

import openai
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Your OpenAI API key
openai.api_key = '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'

# Create a connection to the SMTP server
smtp_server = smtplib.SMTP('smtp.gmail.com', 587)

# Start TLS for security
smtp_server.starttls()

# Authentication
smtp_server.login("poojanvig.pv@gmail.com", "zkvhzejitfndpclh")

# List of email addresses to send to
email_list = attendees
# File to attach
file_path = ''  # replace with the path to your file

# Loop through the list of emails
for email in email_list:
    # Generate the email body using the OpenAI API
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt="Greeting for the event.",
        temperature=0.5,
        max_tokens=100
    )
    from dateutil.parser import parse

    # Parse the start and end times into datetime objects
    start_time_obj = parse(start_time)
    end_time_obj = parse(end_time)

    # Format the datetime objects into a more human-readable format
    formatted_start_time = start_time_obj.strftime('%A, %B %d, %Y, %I:%M %p')
    formatted_end_time = end_time_obj.strftime('%A, %B %d, %Y, %I:%M %p')

    # Create the email body with the event link and event time
    email_body = response.choices[0].text.strip() + \
    f"\n\nYou can join the meeting using this link: {event_link}." + \
    f"\nThe meeting is scheduled from {formatted_start_time} to {formatted_end_time}."


    # Create the email
    msg = MIMEMultipart()
    msg['From'] = 'your-email-id'
    msg['To'] = email
    msg['Subject'] = 'Email automation'
    msg.attach(MIMEText(email_body, 'plain'))

    # If a file path is provided, attach the file to the email
    if file_path:
        # Open the file in binary mode
        binary_file = open(file_path, 'rb')

        # Create a MIMEBase object
        mime_base = MIMEBase('application', 'octet-stream')

        # Add the contents of the attachment to this object
        mime_base.set_payload(binary_file.read())

        # Encode the data in base64 format
        encoders.encode_base64(mime_base)

        # Add header
        mime_base.add_header('Content-Disposition', f'attachment; filename= {file_path}')

        # Attach the MIMEBase object to the email
        msg.attach(mime_base)

        # Close the binary file
        binary_file.close()

    # Send the email
    smtp_server.send_message(msg)

# Close the connection to the SMTP server
smtp_server.quit()