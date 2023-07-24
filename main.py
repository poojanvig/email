import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Create a connection to the SMTP server
smtp_server = smtplib.SMTP('smtp.gmail.com', 587)

# Start TLS for security
smtp_server.starttls()

# Authentication
smtp_server.login("poojanvig.pv@gmail.com", "gkok yius oglw sweh")  # replace with your App Password

# Create a test message
msg = MIMEMultipart()
msg['From'] = 'poojanvig.pv@gmail.com'
msg['To'] = 'poojan.pvig@gmail.com'  # replace with your test email address
msg['Subject'] = 'Test Email'
msg.attach(MIMEText('This is a test email.', 'plain'))

# Send the email
smtp_server.send_message(msg)

# Close the connection to the SMTP server
smtp_server.quit()
