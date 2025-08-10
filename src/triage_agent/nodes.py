import json
import os
from datetime import datetime
import re
from triage_agent.state import EmailState
from triage_agent.prompts import email_scoring_prompt
from langchain_google_genai import ChatGoogleGenerativeAI

# Don't initialize llm in global scope because GOOGLE_API_KEY won't be set yet
llm = None

# Initialize Gemini LLM

def llm_init():
    global llm
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

def score_email(state: EmailState) -> EmailState:
    if not llm:
        llm_init()

    prompt = email_scoring_prompt.format_messages(
        sender=state["sender"],
        subject=state["subject"],
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

    return state