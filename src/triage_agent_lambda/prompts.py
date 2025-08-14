from langchain_core.prompts import ChatPromptTemplate

email_scoring_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an assistant that scores emails for importance and urgency on a scale from 1 to 100."),
    ("user", 
     "Email sender: {sender}\n"
     "Email subject: {subject}\n"
     "Email body:\n{body}\n"
     "User profile:\n{user_profile}\n\n"
     "Email date: {email_date}\n"
     "Current date: {current_date}\n\n"
     "Respond ONLY in valid JSON, in the format:\n"
     "{{\n"
     "  \"importance\": <int>,\n"
     "  \"urgency\": <int>,\n"
     "  \"justification\": \"<short explanation for both scores>\"\n"
     "}}")
])