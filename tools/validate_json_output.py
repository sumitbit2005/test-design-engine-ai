import json

from langchain_core.tools import tool


@tool
def validate_json_output(json_string: str) -> str:
    """Validate that a string is valid JSON. Returns 'valid' or the error."""
    try:
        json.loads(json_string)
        return "valid"
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {e}"
