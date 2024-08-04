from googleapiclient.http import BatchHttpRequest

def batch_callback(request_id, response, exception):
    if exception:
        print(f"Error fetching message: {exception}")
    else:
        headers = response['payload']['headers']
        message_id = next((header['value'] for header in headers if header['name'] == 'Message-ID'), None)
        gmail_message_id = response['id']
        print(f'Gmail Message ID: {gmail_message_id}, Email Message-ID: {message_id}')

batch = BatchHttpRequest(callback=batch_callback)
for message in messages:
    batch.add(service.users().messages().get(userId='me', id=message['id'], format='full'))

batch.execute()
