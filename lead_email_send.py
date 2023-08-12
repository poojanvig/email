import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Function to send invitations via email
def send_invitations(email_list, subject, body):
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.login("your-email@example.com", "your-password")

    for email in email_list:
        msg = MIMEMultipart()
        msg['From'] = 'your-email-id'
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        smtp_server.send_message(msg)

    smtp_server.quit()

st.title('Lead Email Sender')

# Option to upload leads CSV
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    leads_df = pd.read_csv(uploaded_file)
    st.dataframe(leads_df)

    # Option to enter email subject and body
    email_subject = st.text_input('Enter Email Subject')
    email_body = st.text_area('Enter Email Body')

    if st.button('Send Emails'):
        # Extracting email addresses from the DataFrame
        email_list = leads_df['Email'].tolist()

        # Sending emails
        send_invitations(email_list, email_subject, email_body)
        st.write('Emails sent successfully!')
