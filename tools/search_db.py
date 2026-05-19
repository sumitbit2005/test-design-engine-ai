import sqlite3
from pathlib import Path

from langchain_core.tools import tool

DB_PATH = Path(__file__).parent.parent / "results.db"


@tool
def search_history(keyword: str, output_mode: str = "") -> str:
    """Search past test generation results by keyword. Optionally filter by output_mode (design_only, rest_assured, selenium_java, selenium_python, pytest). Searches each word independently for better matching."""
    conn = sqlite3.connect(DB_PATH)

    # Split keyword into individual words for broader matching
    words = keyword.strip().split()

    # Build WHERE clause — match ANY word in requirement or output
    conditions = []
    params = []
    for word in words:
        conditions.append("(requirement LIKE ? OR output LIKE ?)")
        params.extend([f"%{word}%", f"%{word}%"])

    where_clause = " OR ".join(conditions)

    if output_mode:
        query = (
            f"SELECT id, created_at, requirement, output_mode, file_path FROM test_results "
            f"WHERE ({where_clause}) AND output_mode = ? "
            f"ORDER BY created_at DESC LIMIT 10"
        )
        params.append(output_mode)
    else:
        query = (
            f"SELECT id, created_at, requirement, output_mode, file_path FROM test_results "
            f"WHERE {where_clause} "
            f"ORDER BY created_at DESC LIMIT 10"
        )

    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No matching results found."

    results = []
    for row in rows:
        results.append(
            f"[ID: {row[0]}] {row[1]} | Mode: {row[3]} | Requirement: {row[2][:60]} | File: {row[4]}"
        )
    return "\n".join(results)
