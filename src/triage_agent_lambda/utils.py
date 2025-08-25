from decimal import Decimal
import json
import math
import os
import boto3
from botocore.exceptions import ClientError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Function to determine ranking of emails based on importance and urgency
def score_function(importance: int, urgency: int) -> int:
    return importance + urgency

# embed text into vector
def embed(text: str):
    bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION","us-east-1"))
    payload = {"inputText": text}
    resp = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps(payload)
    )
    vec = json.loads(resp["body"].read())["embedding"]
    return vec

# Determine cosine similarity of 2 vectors
def cosine(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(y*y for y in b))
    return 0.0 if na==0 or nb==0 else dot/(na*nb)

# get secret from aws secrets manager
def get_secret(secret_name): # Code from aws
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
        return "{}"

    return get_secret_value_response["SecretString"]

def get_gmail_service(SCOPES):
    scope_names = {
        "https://www.googleapis.com/auth/gmail.modify": "Modify",
        "https://www.googleapis.com/auth/gmail.readonly": "Read",
    }

    scope = scope_names[SCOPES[0]]

    cred_obj = json.loads(get_secret("Gmail" + scope + "Creds"))

    if "Gmail" + scope + "Token" in cred_obj:
        cred_string = json.loads(cred_obj["Gmail" + scope + "Token"])
        creds = Credentials.from_authorized_user_info(cred_string)
    else:
        creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open("gmail_secrets/" + scope.lower() + ".json", "w") as token:
                token.write(creds.to_json())
            print(creds.to_json())
    

    service = build("gmail", "v1", credentials=creds)
    return service