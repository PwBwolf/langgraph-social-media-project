"""Define a simple chatbot agent.

This agent returns a predefined response without using an actual LLM.
"""

from typing import Any, Dict, Literal

from langgraph.graph import StateGraph, END

from src.agent.generate_post.configuration import Configuration
from src.agent.generate_post.generate_post_state import GeneratePostState
from src.agent.generate_post.nodes.verify_general import verifyGeneralContent
from src.agent.generate_post.nodes.generate_report import generate_content_report

def generate_report_or_end_conditional_edge(state: GeneratePostState) -> Literal["generate_content_report", "END"]:
    print(f"State relevant_links: {state.relevant_links}")  # Debugging
    return "generate_content_report" if state.relevant_links else "END"

# Define a new graph
workflow = StateGraph(GeneratePostState, config_schema=Configuration)

# Add the node to the graph
workflow.add_node("verify_general_content", verifyGeneralContent)
workflow.add_node("generate_content_report", generate_content_report)

# Set the entrypoint as `call_model`
workflow.add_edge("__start__", "verify_general_content")
workflow.add_conditional_edges(
    "verify_general_content",
    generate_report_or_end_conditional_edge,
    {
        "generate_content_report": "generate_content_report",
        "END": END
    }
)

# Compile the workflow into an executable graph
graph = workflow.compile()
graph.name = "New Graph"  # This defines the custom name in LangSmith
