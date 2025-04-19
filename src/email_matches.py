import base64
import os
import pandas as pd
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def gmail_authenticate():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('resources/cupidmatch-oauth.json.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_email(service, sender, to, subject, body_text):
    message = create_message(sender, to, subject, body_text)
    sent = service.users().messages().send(userId="me", body=message).execute()
    print(f"✅ Email sent to {to} | Message ID: {sent['id']}")

# -------- Main Script --------
if __name__ == "__main__":
    # Load participant emails
    df = pd.read_csv("data/sheet_data.csv")  # Assumes this has 'Full Name' and 'Email Address'
    email_lookup = dict(zip(df['Full Name'], df['Email Address']))

    # Read matches from text file
    matches = []
    with open("data/matches.txt", "r") as f:
        for line in f:
            parts = [x.strip() for x in line.strip().split(",")]
            if len(parts) == 3:
                matches.append((parts[0], parts[1], int(parts[2])))

    service = gmail_authenticate()
    sender_email = "me"  # Gmail API magic word

    for p1, p2, score in matches:
        email1 = email_lookup.get(p1)
        email2 = email_lookup.get(p2)

        if not email1 or not email2:
            print(f"⚠️ Missing email for: {p1} or {p2}")
            continue

        for person, match, recipient in [(p1, p2, email1), (p2, p1, email2)]:
            subject = "🎉 You've Been Matched!"
            body = f"""
Hi {person},

Great news! Based on your shared values and preferences, we've found someone who could be a great fit for you. 💫

💞 Your match is: {match}  
💡 Compatibility Score: {score}/25

Feel free to reach out, spark a convo, and see where things go. We’re rooting for you! 🥂

— The CupidMatch Team 💖
            """
            send_email(service, sender_email, recipient, subject, body.strip())
