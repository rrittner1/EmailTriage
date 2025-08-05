import json
import os.path
import boto3
from botocore.exceptions import ClientError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Gmail scope is readonly for the time being
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def lambda_handler(event, context):
    print("Polling Gmail and running LangChain agent...")
    list_recent_emails()
    return {
        'statusCode': 200,
        'body': 'Function ran successfully!'
    }

def get_gmail_service():
    cred_string = json.loads(json.loads(get_secret())["GmailToken"])
    creds = Credentials.from_authorized_user_info(cred_string)

    # build api service
    service = build('gmail', 'v1', credentials=creds)
    return service

def list_recent_emails():
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=5).execute()
    messages = results.get('messages', [])

    for msg in messages:
        full_message = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = full_message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
        print(f"Subject: {subject}")

def get_secret():

    secret_name = "GmailCreds"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    return get_secret_value_response['SecretString']