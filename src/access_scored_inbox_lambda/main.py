import base64
import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
SCORED_TABLE = "ScoredEmails" 

def lambda_handler(event, context):
    try:
        body = event.get("body", {})
        if isinstance(body, str):
            if event.get("isBase64Encoded"):
                body = base64.b64decode(body).decode("utf-8")
            body = json.loads(body)

        user_email = body.get("user_email")

        if not user_email:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields: user_email"})
            }
        
        table = dynamodb.Table(SCORED_TABLE)

        response = table.query(
            KeyConditionExpression=Key("user_email").eq(user_email)
        )
        # May still need to sort by score

        items = response.get("Items", [])
        inbox = []
        for e in items:
            e["importance"] = float(e["importance"])
            e["urgency"] = float(e["urgency"])
            e["score"] = float(e["score"])
            inbox.append(e)
            
        return {
            "statusCode": 200,
            "body": json.dumps(inbox)
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