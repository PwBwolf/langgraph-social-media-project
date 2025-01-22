"""Define the state structures for the agent."""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl


class GeneratePostState(BaseModel):
    url: HttpUrl  # This will validate the URL format
    links: Optional[List[str]] = []
    page_contents: Optional[Dict[str, Any]] = {}