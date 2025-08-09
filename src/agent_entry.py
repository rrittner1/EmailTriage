import json
import boto3
import os
from botocore.exceptions import ClientError
from datetime import datetime
from triage_agent.graph import build_graph
from triage_agent.state import EmailState

lambda_client = boto3.client("lambda")

def lambda_handler(event, context):
    os.environ["GOOGLE_API_KEY"] = get_secret()
    
    print(event)
    print(type(event))

    app = build_graph()

    emails = event["emails"]
    for e in emails:
        sender = e["sender"]
        subject = e["subject"]
        email_date = e["date"]

        print(sender)
        print(subject)
        print(email_date)

        email_input = EmailState(
            sender=sender,
            subject=subject,
            email_date=datetime.strptime(email_date, "%a, %d %b %Y %H:%M:%S %z (%Z)"),
            current_date=datetime.now()
        )

        result = app.invoke(email_input)
        print(result)

def get_secret(): # Code from aws
    secret_name = "Google_Gemini_flash-2.0_key"
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

    return json.loads(get_secret_value_response["SecretString"])["GeminiKey"]
