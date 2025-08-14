import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
PROFILE_TABLE = "StructuredUserProfiles"  # Can be changed to UserProfiles

def lambda_handler(event, context):
    """
    Lambda to create or update a user profile in DynamoDB.
    Expects `user_email` and `profile` in the request body.
    Example profile: {"age": 22, "education": "Purdue 2025 BS in Computer Science"}
    """

    try:
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body)

        user_email = body.get("user_email")
        profile = body.get("profile")

        if not user_email or not profile:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields: user_email, profile"})
            }

        table = dynamodb.Table(PROFILE_TABLE)

        new_item = {
            "user_email": user_email,
            "updated_at": datetime.now().isoformat()
        }
        if PROFILE_TABLE == "StructuredUserProfiles":
            for key in profile:
                new_item[key] = profile[key]
        else:
            new_item["profile"] = profile

        # PutItem will insert or replace the existing item with the same user_id
        table.put_item(
            Item=new_item
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Profile created/updated successfully"})
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
