import base64
import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
INBOX_TABLE = "UserInboxes" 

def lambda_handler(event, context):
    try:
        body = event.get("body", {})
        if isinstance(body, str):
            if event.get("isBase64Encoded"):
                body = base64.b64decode(body).decode("utf-8")
            body = json.loads(body)

        email_id = body.get("email_id")
        user_email = body.get("user_email")

        if not email_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields: email_id, user_email"})
            }
        
        table = dynamodb.Table(INBOX_TABLE)

        response = table.delete_item(
            Key={
                "user_email": user_email,
                "email_id": email_id
            },
            ReturnValues="ALL_OLD"
        )

        # Also archive in Gmail?

        response["Attributes"]["importance"] = float(response["Attributes"]["importance"])
        response["Attributes"]["urgency"] = float(response["Attributes"]["urgency"])
        response["Attributes"]["score"] = float(response["Attributes"]["score"])

        if "Attributes" in response:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Item deleted",
                    "deleted_item": response["Attributes"]
                })
            }
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Item not found"})
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