import sqlite3
import json
from datetime import datetime
from pathlib import Path

from langchain_core.tools import tool

DB_PATH = Path(__file__).parent.parent / "results.db"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

FILE_EXTENSIONS = {
    "design_only": ".json",
    "rest_assured": ".java",
    "selenium_java": ".java",
    "selenium_python": ".py",
    "pytest": ".py",
}


def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            requirement TEXT NOT NULL,
            output_mode TEXT NOT NULL,
            output TEXT NOT NULL,
            file_path TEXT,
            project TEXT,
            tags TEXT
        )
    """)
    conn.commit()
    return conn


@tool
def save_to_db(requirement: str, output_mode: str, output: str, project: str = "", tags: str = "") -> str:
    """Save generated test output to SQLite database and write the output file (.json/.java/.py)."""
    # Create output directory
    project_dir = OUTPUT_DIR / (project or "default")
    project_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = FILE_EXTENSIONS.get(output_mode, ".txt")
    filename = f"{output_mode}_{timestamp}{ext}"
    file_path = project_dir / filename

    # Write file
    file_path.write_text(output, encoding="utf-8")

    # Save to DB
    conn = _get_connection()
    conn.execute(
        "INSERT INTO test_results (requirement, output_mode, output, file_path, project, tags) VALUES (?, ?, ?, ?, ?, ?)",
        (requirement, output_mode, output, str(file_path), project, tags),
    )
    conn.commit()
    conn.close()

    return f"Saved to database and file: {file_path}"