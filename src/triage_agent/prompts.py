from langchain_core.prompts import ChatPromptTemplate

email_scoring_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an assistant that scores emails for importance and urgency on a scale from 1 to 100."),
    ("user", 
     "Email sender: {sender}\n"
     "Email subject: {subject}\n"
     "Email date: {email_date}\n"
     "Current date: {current_date}\n\n"
     "Respond with JSON: {{'importance': <int>, 'urgency': <int>}}")
])