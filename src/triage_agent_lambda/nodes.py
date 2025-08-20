import json
import boto3
import re
from state import EmailState
from prompts import email_scoring_prompt
from utils import get_gmail_service, score_function
from langchain_google_genai import ChatGoogleGenerativeAI
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# DynamoDB setup
dynamodb = boto3.resource("dynamodb")
PROFILE_TABLE = "StructuredUserProfiles" # Can change between UserProfiles and StructuredUserProfiles for testing
profile_table = dynamodb.Table(PROFILE_TABLE)
INBOX_TABLE = "UserInboxes"
inbox_table = dynamodb.Table(INBOX_TABLE)


# Don't initialize llm in global scope because GOOGLE_API_KEY won't be set yet
llm = None

# Initialize Gemini LLM
def llm_init():
    global llm
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

def fetch_profile(state: EmailState) -> EmailState:
    """Fetch user profile from DynamoDB and add it to state."""
    response = profile_table.get_item(Key={"user_email": state["user_email"]})
    profile = response.get("Item", {})
    state["user_profile"] = profile
    return state

def score_email(state: EmailState) -> EmailState:
    """Prompt llm to score email on importance and urgency"""
    if not llm:
        llm_init()

    prompt = email_scoring_prompt.format_messages(
        sender=state["sender"],
        subject=state["subject"],
        body=state["body"],
        user_profile=state["user_profile"],
        email_date=state["email_date"].isoformat(),
        current_date=state["current_date"].isoformat()
    )

    response = llm.invoke(prompt)

    # strip markdown formatting
    content = re.sub(r"^```(?:json)?\n|\n```$", "", response.content.strip())

    try:
        scores = json.loads(content)
        state["importance"] = scores["importance"]
        state["urgency"] = scores["urgency"]
        state["justification"] = scores["justification"]
    except Exception:
        state["importance"] = 50
        state["urgency"] = 50
        state["justification"] = "Processing error"

    print(state)
    return state

def store_grade(state: EmailState) -> EmailState:
    print(state)
    print("email_id" in state)
    """store graded+scored email in db"""
    score = score_function(state["importance"], state["urgency"])
    item = {
        "email_id": state["email_id"],
        "user_email": state["user_email"],
        "subject": state["subject"],
        "sender": state["sender"],
        "email_date": state["email_date"].isoformat(),
        "current_date": state["current_date"].isoformat(),
        "body": state["body"],
        "score": score,
        "importance": state["importance"],
        "urgency": state["urgency"],
        "justification": state["justification"]
    }
    inbox_table.put_item(TableName="UserInboxes", Item=item)
    return state

def mark_as_read(state: EmailState) -> EmailState:
    """mark email as read in gmail inbox"""
    email_id = state["email_id"]
    user_email = state["user_email"]

    service = get_gmail_service(["https://www.googleapis.com/auth/gmail.modify"])

    service.users().messages().modify(
        userId="me",
        id=email_id,
        body={"removeLabelIds": ["UNREAD"]}
    ).execute()

    return {**state, "marked_as_read": True}