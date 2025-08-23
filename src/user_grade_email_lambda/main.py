import base64
from decimal import Decimal
import json
import os
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
from utils import score_function

dynamodb = boto3.resource("dynamodb")
GRADED_TABLE = "UserGradedEmails"
bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION","us-east-1"))

def lambda_handler(event, context):
    try:
        body = event.get("body", {})
        if isinstance(body, str):
            if event.get("isBase64Encoded"):
                body = base64.b64decode(body).decode("utf-8")
            body = json.loads(body)

        user_email = body.get("user_email")
        email_id = body.get("email_id")
        email_body = body.get("body")
        email_date = body.get("email_date")
        current_date = body.get("current_date")
        subject = body.get("subject")
        sender = body.get("sender")
        importance = body.get("importance")
        urgency = body.get("urgency")
        justification = body.get("justification")
        score = score_function(importance, urgency)

        if not user_email or not email_id or not email_date or not current_date or not sender or not importance or not urgency or not justification:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required one or more required fields: user_email, email_id, email_date, current_date, email_date, sender, importance, urgency, justification"})
            }

        table = dynamodb.Table(GRADED_TABLE)

        new_item = {
            "user_email": user_email,
            "email_id": email_id,
            "email_date": email_date,
            "current_date": current_date,
            "body": email_body,
            "subject": subject,
            "sender": sender,
            "importance": importance,
            "urgency": urgency,
            "justification": justification,
            "score": score,
            "embedding": embed(f"{sender}\n{subject}\n{email_body}")
        }

        table.put_item(TableName=GRADED_TABLE, Item=new_item)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Email grade stored"})
        }

    except ClientError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
    
def embed(text: str):
    payload = {"inputText": text}
    resp = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps(payload)
    )
    vec = json.loads(resp["body"].read())["embedding"]
    return [Decimal(str(x)) for x in vec]
