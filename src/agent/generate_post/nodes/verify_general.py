"""Define the my_node function for the generate post graph."""

from typing import Any, Dict, Literal, cast
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel
from src.agent.generate_post.configuration import Configuration
from src.agent.generate_post.generate_post_state import GeneratePostState
from src.agent.generate_post.nodes.scrape_node import scrape_website
from src.shared.utils import load_chat_model

class Grader(BaseModel):
    """Schema for the relevance check response."""
    relevant: Literal["yes", "no"]
    reasoning: str

SYSTEM_PROMPT = """You are a highly regarded marketing employee.
You're provided with a webpage containing content a third party submitted to you claiming it's relevant and implements your company's products.
Your task is to carefully read over the entire page, and determine whether or not the content actually implements and is relevant to your company's products.
You're doing this to ensure the content is relevant to your company, and it can be used as marketing material to promote your company.

{business_context}

Given this context, examine the webpage content closely, and determine if the content implements your company's products.
You should provide reasoning as to why or why not the content implements your company's products, then a simple relevant yes or no for whether or not it implements some.
"""

async def verifyGeneralContent(state: GeneratePostState, config: RunnableConfig) -> Dict[str, Any]: # You can make this configurable
    configuration = Configuration.from_runnable_config(config)
    
    # Convert URL to string if it's an HttpUrl object
    url = str(state.url)
    print(f"Processing URL: {url}")
    print(state.links)  
    page_contents = scrape_website(url)
    print("Page contents:", page_contents)  # Add this debug line
    
    llm = load_chat_model(configuration.grader_model)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(
                business_context=configuration.business_context
            )
        },
        {
            "role": "user",
            "content": page_contents.get("text", "No content found")  # Use .get() for safer access
        }
    ]
    
    relevant = cast(Grader, await llm.with_structured_output(Grader).ainvoke(messages))
    print(relevant)
    
    if relevant.relevant == "yes":
        print("Relevant")
        state.page_contents = page_contents
        return {
            "relevant_links": [state.url],
            "page_contents": [page_contents],
        }
    return {
        "relevant_links": [],
        "page_contents": []
    }
