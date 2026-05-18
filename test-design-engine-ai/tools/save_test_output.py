from pathlib import Path

from langchain_core.tools import tool


@tool
def save_test_output(file_path: str, content: str) -> str:
    """Save generated test cases or Gherkin scenarios to a file."""
    Path(file_path).write_text(content, encoding="utf-8")
    return f"Saved to {file_path}"
