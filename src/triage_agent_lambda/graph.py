from langgraph.graph import StateGraph, END
from triage_agent.state import EmailState
from triage_agent.nodes import score_email, fetch_profile

def build_graph():
    workflow = StateGraph(EmailState)
    workflow.add_node("fetch_profile", fetch_profile)
    workflow.add_node("score_email", score_email)
    workflow.set_entry_point("fetch_profile")
    workflow.add_edge("fetch_profile", "score_email")
    workflow.add_edge("score_email", END)
    return workflow.compile()