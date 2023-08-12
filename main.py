import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os.path
import pickle
import openai
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

openai.api_key = 'sk-vrfAOiVKA6M33NdKnMMBT3BlbkFJiQLFJyc9ktZ2mwH3MXu'

# Define Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Function to authenticate with Google
def authenticate():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

# Function to get upcoming events
def get_upcoming_events(service, max_results=10):
    # Call the Calendar API
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=max_results, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    upcoming_events = []
    if not events:
        print('No upcoming events found.')
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event['summary']
            upcoming_events.append((start, summary))

    return upcoming_events


# Function to create a new event
def create_event(service, event_data, attendees):
    event = {
        'summary': event_data['summary'],
        'start': {
            'dateTime': event_data['start_time'].strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'UTC+5:30',
        },
        'end': {
            'dateTime': event_data['end_time'].strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': 'UTC+5:30',
        },
        'attendees': [{'email': email.strip()} for email in attendees.split(',')],
        # Add additional event fields as needed
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    event_link = event.get('htmlLink')
    event_summary = event.get('summary')
    start_time = event['start'].get('dateTime')
    end_time = event['end'].get('dateTime')

    return event_link, event_summary, start_time, end_time, attendees



# Function to send invitations via email
def send_invitations(email_list, event_link, start_time, end_time, summary):
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.login("poojanvig.pv@gmail.com", "zkvhzejitfndpcl")

    for email in email_list:
        prompt_text = f"Greeting for the event with the following summary: {summary}."
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt_text,
            temperature=0.5,
            max_tokens=100
        )
        formatted_start_time = start_time.strftime('%A, %B %d, %Y, %I:%M %p')
        formatted_end_time = end_time.strftime('%A, %B %d, %Y, %I:%M %p')
        email_body = response.choices[0].text.strip() + \
            f"\n\nYou can join the meeting using this link: {event_link}." + \
            f"\nThe meeting is scheduled from {formatted_start_time} to {formatted_end_time}."

        msg = MIMEMultipart()
        msg['From'] = 'your-email-id'
        msg['To'] = email
        msg['Subject'] = 'Email automation'
        msg.attach(MIMEText(email_body, 'plain'))

        smtp_server.send_message(msg)

    smtp_server.quit()

# ... (Previous imports and functions) ...
# Streamlit App
st.title('Google Calendar Integration')

# Authentication with Google
service = authenticate()
st.write('Authenticated successfully!')

# Section to get upcoming events
if st.button('Get Upcoming Events'):
    events = get_upcoming_events(service)
    for start, summary in events:
        st.write(start, summary)

# Section to create a new event
summary = st.text_input('Event Summary', key='event_summary')
start_date = st.date_input('Start Date', key='start_date')
start_time = st.time_input('Start Time', key='start_time')
end_date = st.date_input('End Date', key='end_date')
end_time = st.time_input('End Time', key='end_time')
attendees_input = st.text_area('Attendees (comma-separated email addresses)', key='attendees')

# Combine date and time into datetime objects
start_datetime = datetime.combine(start_date, start_time)
end_datetime = datetime.combine(end_date, end_time)

# Create a dictionary to hold the event details
event_data = {
    'summary': summary,
    'start_time': start_datetime,
    'end_time': end_datetime,
}

if st.button('Create New Event'):
    event_link, event_summary, start_time, end_time, _ = create_event(service, event_data, attendees_input)
    st.session_state['event_link'] = event_link  # Save to session state
    st.write(f'Event created: {event_link}')

# Optional: Section to send invitations (if needed)
if st.button('Send Invitations') and 'event_link' in st.session_state:
    send_invitations(attendees_input.split(','), st.session_state['event_link'], start_datetime, end_datetime,summary)
    st.write('Invitations sent successfully!')
else:
    st.write('Please create an event before sending invitations.')
oh