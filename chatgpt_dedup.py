from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Assuming 'creds' is already set with the necessary credentials
creds = Credentials.from_authorized_user_info(info, scopes=['https://www.googleapis.com/auth/gmail.readonly'])

# Build the Gmail API service
service = build("gmail", "v1", credentials=creds)

def get_all_messages(service, label_id):
    all_messages = []
    page_token = None

    while True:
        messages = service.users().messages().list(userId="me", labelIds=[label_id], maxResults=100, pageToken=page_token).execute()
        all_messages.extend(messages.get("messages", []))
        page_token = messages.get("nextPageToken")
        if not page_token:
            break

    return all_messages

def get_message_details(service, msg_id):
    msg = service.users().messages().get(userId="me", id=msg_id, format="metadata", metadataHeaders=["message-id", "date"]).execute()
    headers = msg["payload"]["headers"]
    message_id = next((header["value"] for header in headers if header["name"] == "Message-ID"), None)
    date = next((header["value"] for header in headers if header["name"] == "Date"), None)
    return message_id, date, msg_id

def delete_message(service, user_id, msg_id):
    try:
        service.users().messages().delete(userId=user_id, id=msg_id).execute()
        print(f"Message with ID {msg_id} deleted successfully.")
    except Exception as error:
        print(f"An error occurred: {error}")

# List all messages in "[Gmail]/All Mail" label
results = service.users().labels().list(userId="me").execute()
labels = results.get("labels", [])

label_id = None
for label in labels:
    if label["name"] == "[Gmail]/All Mail":
        label_id = label["id"]
        break

if label_id:
    messages = get_all_messages(service, label_id)

    # Group messages by Message-ID
    grouped_messages = {}
    for message in messages:
        message_id, date, msg_id = get_message_details(service, message["id"])
        if message_id:
            if message_id not in grouped_messages:
                grouped_messages[message_id] = []
            grouped_messages[message_id].append((date, msg_id))

    # Delete all but the last message in each group
    for message_id, message_list in grouped_messages.items():
        # Sort messages by date
        sorted_messages = sorted(message_list, key=lambda x: x[0])
        # Keep the last message and delete the rest
        for date, msg_id in sorted_messages[:-1]:
            delete_message(service, 'me', msg_id)
else:
    print("Label '[Gmail]/All Mail' not found.")
