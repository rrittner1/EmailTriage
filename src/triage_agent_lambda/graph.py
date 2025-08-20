from langgraph.graph import StateGraph, END
from state import EmailState
from nodes import score_email, fetch_profile, store_grade, mark_as_read

def build_graph():
    workflow = StateGraph(EmailState)
    workflow.add_node("fetch_profile", fetch_profile)
    workflow.add_node("score_email", score_email)
    workflow.add_node("store_grade", store_grade)
    workflow.add_node("mark_as_read", mark_as_read)
    workflow.set_entry_point("fetch_profile")
    workflow.add_edge("fetch_profile", "score_email")
    workflow.add_edge("score_email", "store_grade")
    workflow.add_edge("store_grade", "mark_as_read")
    workflow.add_edge("mark_as_read", END)
    return workflow.compile()