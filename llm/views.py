from typing import TypedDict, Dict


class LLMResponse(TypedDict):
    """LLM response structure"""
    content: str
    token_usage: Dict
    model_version: str
