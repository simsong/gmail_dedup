# https://developers.google.com/gmail/api/quickstart/python

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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

def list_label(service,label_id):
    page_token = None

    while True:
        messages = service.users().messages().list(userId="me", labelIds=[label_id], pageToken=page_token).execute()
        messages_list = messages.get("messages", [])

        if not messages_list:
            break

        for message in messages_list:
            # format='full' to get the full body
            msg = service.users().messages().get(userId="me", id=message["id"], format="metadata", metadataHeaders=["subject", "date", "message-id"]).execute()
            headers = msg["payload"]["headers"]
            subject = next((header["value"] for header in headers if header["name"] == "Subject"), "No Subject")
            date = next((header["value"] for header in headers if header["name"] == "Date"), "No Date")
            message_id = next((header["value"] for header in headers if header["name"] == "Message-ID"), "No Message-ID")
            print(f"Subject: {subject}, Date: {date}, Message-ID: {message_id}")

            #print(dir(message))
            #print(message["id"])

        page_token = message.get('nextPageToken')
        if not page_token:
            break

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
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

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        if not labels:
            print("No labels found.")
            return
        all_mail_id = None
        print("Labels:")
        for label in labels:
            print(label["name"],label['id'])
            if label['name']=='INBOX':
                all_mail_id = label['id']
        if all_mail_id:
            list_label(service,all_mail_id)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
