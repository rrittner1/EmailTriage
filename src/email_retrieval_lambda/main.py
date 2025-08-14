import base64
import json
import os.path
import boto3
from email import message_from_bytes
from botocore.exceptions import ClientError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Gmail scope is readonly for the time being
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

lambda_client = boto3.client("lambda")

live = True

def lambda_handler(event, context):
    print("Polling Gmail and running LangChain agent...")
    emails = get_unread_emails()
    if not live:
        return
    response = lambda_client.invoke(
            FunctionName=os.environ["AGENT_FUNCTION"],
            InvocationType="Event",
            Payload=json.dumps({"emails": emails})
        )
    return {
        "statusCode": 200,
        "body": "Function ran successfully!"
    }

# A long term functionality to allow more users than just me would involve making this process not use hard coded values 
def get_gmail_service():
    cred_string = json.loads(json.loads(get_secret())["GmailToken"])
    creds = Credentials.from_authorized_user_info(cred_string)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            print(creds.to_json())
    

    service = build("gmail", "v1", credentials=creds)
    return service

def get_unread_emails():
    service = get_gmail_service()
    results = service.users().messages().list(userId="me", labelIds=["INBOX"], q="is:unread", maxResults=1).execute()
    messages = results.get("messages", [])

    # passing senders, subjects, and times
    email_outputs = []

    for msg in messages:
        full_message = service.users().messages().get(userId="me", id=msg["id"]).execute()
        full_raw = service.users().messages().get(userId="me", id=msg["id"], format="raw").execute()
        body = get_email_body(full_raw)
        headers = full_message["payload"]["headers"]
        email_outputs.append({
            "subject": next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)"),
            "sender": next((h["value"] for h in headers if h["name"] == "From"), "(No Sender)"),
            "user_email": "rdrittner@gmail.com",
            "date": next((h["value"] for h in headers if h["name"] == "Date"), "(No Date)"),
            "body": body
        })
    return email_outputs

def get_secret(): # Code from aws
    secret_name = "GmailCreds"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    return get_secret_value_response["SecretString"]

def get_email_body(email):
    raw_bytes = base64.urlsafe_b64decode(email['raw'].encode('ASCII'))
    mime_msg = message_from_bytes(raw_bytes)
    return get_plain_text_body(mime_msg)

def get_plain_text_body(msg):
    """
    Recursively extract and return the plain-text body from an email.message.Message.
    """
    if msg.is_multipart():
        for part in msg.get_payload():
            text = get_plain_text_body(part)
            if text:
                return text
    else:
        ctype = msg.get_content_type()
        if ctype == 'text/plain':
            return msg.get_payload(decode=True).decode(errors='replace')
    return None