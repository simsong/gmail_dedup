# https://developers.google.com/gmail/api/quickstart/python

import os.path
from  collections import defaultdict
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import BatchHttpRequest


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_body(msg):
    # Extract the body
    body = ""
    if "parts" in msg["payload"]:
        for part in msg["payload"]["parts"]:
            if part["mimeType"] == "text/plain":
                body = part["body"]["data"]
                break
            elif part["mimeType"] == "text/html":
                body = part["body"]["data"]
                break
    else:
        body = msg["payload"]["body"]["data"]

    if body:
        import base64
        body = base64.urlsafe_b64decode(body).decode("utf-8")
    else:
        body = "No Body"


def delete_message(service, user_id, msg_id):
    try:
        service.users().messages().delete(userId=user_id, id=msg_id).execute()
        print(f"Message with ID {msg_id} deleted successfully.")
    except Exception as error:
        print(f"An error occurred: {error}")


# List all messages that do not have the "INBOX" label
#results = service.users().messages().list(userId='me', q='-label:INBOX').execute()
#messages = results.get('messages', [])


# Thanks ChatGPT!


def get_dups(service,label_id):

    messages_by_messageid = defaultdict(list)
    page_token = None
    count = 0

    while True:
        # Limit to 50 per batching documentation
        messages = service.users().messages().list(userId="me", labelIds=[label_id], pageToken=page_token, maxResults=50).execute()
        print(json.dumps(messages,indent=4))
        messages_list = messages.get("messages", [])

        if not messages_list:
            break

        def batch_callback(request_id, response, exception):
            if exception:
                print(f"Error fetching message: {exception}")
            else:
                headers = response['payload']['headers']
                message_id = next((header['value'] for header in headers if header['name'] == 'Message-ID'), None)
                gmail_message_id = response['id']
                print(f'Gmail Message ID: {gmail_message_id}, Email Message-ID: {message_id}')

        # batch = BatchHttpRequest(callback=batch_callback)
        batch = service.new_batch_http_request(callback=batch_callback)
        for message in messages_list:
            batch.add(service.users().messages().get(userId='me', id=message['id'], format='metadata', metadataHeaders=["subject", "date", "message-id"]))
        batch.execute()
        page_token = messages.get('nextPageToken')
        if not page_token:
            break

def get_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def get_labels(service):
    """Return a dictionary of all labels and their label_id by name"""
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])
    if not labels:
        raise RuntimeError("No labels found.")
    return {label['name'] : label for label in labels}


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = get_creds()
    service = build("gmail", "v1", credentials=creds)
    labels = get_labels(service)
    print("labels:","\n".join(labels.keys()))

    what = '[Gmail]/Sent Messages'

    all_mail_id = labels[what]['id']
    print("all_mail_id:",all_mail_id)

    get_dups(service, all_mail_id)


if __name__ == "__main__":
    main()
