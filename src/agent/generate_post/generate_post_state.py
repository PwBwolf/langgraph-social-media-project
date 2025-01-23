"""Define the state structures for the agent."""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field


class GeneratePostState(BaseModel):
    url: HttpUrl  # This will validate the URL format
    links: Optional[List[str]] = []
    page_contents: Optional[Dict[str, Any]] = {}
    relevant_links: Optional[List[str]] = []  
    report: Optional[str] = Field(
        default=None,
        description="The report generated on the content of the message. Used as context for generating the post."
    )