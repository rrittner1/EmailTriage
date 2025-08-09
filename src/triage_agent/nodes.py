import json
import os
from datetime import datetime
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

    try:
        scores = json.loads(response.content)
        state["importance"] = scores["importance"]
        state["urgency"] = scores["urgency"]
    except Exception:
        state["importance"] = 50
        state["urgency"] = 50

    return state