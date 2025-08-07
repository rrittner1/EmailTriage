import json
import boto3
import os
from botocore.exceptions import ClientError
from datetime import datetime
from agent.graph import build_graph
from agent.schema import EmailMetadata

lambda_client = boto3.client("lambda")

def lambda_handler(event, context):
    print(event)
    print(type(event))

    sender = event["email"]["sender"]
    subject = event["email"]["subject"]
    email_date = event["email"]["date"]
    print(sender)
    print(subject)
    print(email_date)

    os.environ["GOOGLE_API_KEY"] = get_secret()

    app = build_graph()

    state = EmailMetadata(
        sender="ceo@company.com",
        subject="Urgent: Need Q3 report ASAP",
        date_sent=datetime.strptime(email_date, "%a, %d %b %Y %H:%M:%S %z"),
        current_date=datetime.now()
    )

    result = app.invoke(state)
    print("Result:", result)

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

    return json.loads(get_secret_value_response["SecretString"])
