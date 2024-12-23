from __future__ import print_function
import os.path
import pickle
import google.auth
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
import os
from twilio.rest import Client


def send_text(msg):
    print('Sending text message...')
    try:
        # Find your Account SID and Auth Token at twilio.com/console
        # and set the environment variables. See http://twil.io/secure
        # account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        # auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        account_sid = "AC42716dcbc821ae61735f79b13e36f9e7"
        auth_token = "a1aa2b32799802904f83c1ca9e21e337"
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body= f'{msg}',
            from_="whatsapp:+14155238886",
            to="whatsapp:+19512137850",
        )

        print(f'Message sent: {message.sid}')
    except KeyError as e:
        print(f'Environment variable not set: {e}')
    except Exception as e:
        print(f'An error occurred: {e}')

    print(message.body)


# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    """Shows basic usage of the Gmail API.
    Searches for emails with a specific subject.
    """
    creds = None
    try:
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

        service = build('gmail', 'v1', credentials=creds)

        # Get the current date
        now = datetime.now()
        # Calculate the first day of the current month
        first_day_of_month = now.replace(day=1)
        # Calculate the first day of the next month
        first_day_of_next_month = (first_day_of_month + timedelta(days=32)).replace(day=1)

        after_date = first_day_of_month.strftime('%Y/%m/%d')
        before_date = first_day_of_next_month.strftime('%Y/%m/%d')

        # Print the dates for debugging
        print(f'After date: {after_date}')
        print(f'Before date: {before_date}')

        # Search for emails with a specific subject within the current month
        query = f'subject:"You made a payment" from:alerts@notify.wellsfargo.com  after:{after_date} before:{before_date}'

        print(f'query: {query}')
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])


        if not messages:
            print('No messages found.')
            send_text('Did not receive any payment notifications from Wells Fargo this month.')
        
        else:
            send_text('Received payment notifications from Wells Fargo this month.')
            print('Messages:')
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                print(f"Message snippet: {msg['snippet']}")

    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure 'credentials.json' file is present.")
    except HttpError as error:
        print(f'An error occurred: {error}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')

if __name__ == '__main__':
    main()