import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
profile_table = "StructuredUserProfiles"  # Can be changed to UserProfiles

def lambda_handler(event, context):
    """
    Lambda to create or update a user profile in DynamoDB.
    Expects `user_email` and `profile` in the request body.
    Example profile: {"role": "Project Manager", "interests": ["AI", "Healthcare"]}
    """

    try:
        body = json.loads(event.get("body", "{}"))
        user_id = body.get("user_email")
        profile = body.get("profile")

        if not user_id or not profile:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields: user_id, profile"})
            }

        table = dynamodb.Table(profile_table)

        # PutItem will insert or replace the existing item with the same user_id
        table.put_item(
            Item={
                "user_id": user_id,
                "profile": profile,
                "updated_at": datetime.now()
            }
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
