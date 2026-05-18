from pathlib import Path

from langchain_core.tools import tool


@tool
def read_requirement_file(file_path: str) -> str:
    """Read a requirement document from disk and return its content."""
    path = Path(file_path)
    if not path.exists():
        return f"Error: File not found: {file_path}"
    return path.read_text(encoding="utf-8")
