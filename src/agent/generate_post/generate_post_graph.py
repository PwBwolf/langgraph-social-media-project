"""Define a simple chatbot agent.

This agent returns a predefined response without using an actual LLM.
"""

from typing import Any, Dict

from langgraph.graph import StateGraph

from src.agent.generate_post.configuration import Configuration
from src.agent.generate_post.generate_post_state import GeneratePostState
from src.agent.generate_post.nodes.verify_general import verifyGeneralContent

# Define a new graph
workflow = StateGraph(GeneratePostState, config_schema=Configuration)

# Add the node to the graph
workflow.add_node("verify_general_content", verifyGeneralContent)

# Set the entrypoint as `call_model`
workflow.add_edge("__start__", "verify_general_content")

# Compile the workflow into an executable graph
graph = workflow.compile()
graph.name = "New Graph"  # This defines the custom name in LangSmith
