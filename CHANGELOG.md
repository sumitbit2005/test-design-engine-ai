# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-05-19

### Added
- **Chat-style CLI** — conversational interface, just type your requirement
- **Conversation memory** — agent remembers context within a session
- **SQLite storage** — all generated results saved to `results.db`
- **File output** — generated code saved as `.json`, `.java`, `.py` in `output/` directory
- **Search history** — search past results by keyword and output mode
- **`/mode` command** — switch output framework without restarting
- **`/modes` command** — list all available output modes
- **`/clear` command** — reset conversation history
- **`/help` command** — show usage instructions
- New tools: `save_to_db`, `search_history`

### Changed
- `main.py` rewritten from single-shot to interactive chat loop
- System prompt updated to save results automatically and show summaries
- Search uses word-level matching for better results


## [0.1.0] - 2026-05-18

### Added
- Initial release
- LangGraph agent with GPT-4o for test case generation
- Output modes: `design_only`, `rest_assured`, `selenium_java`, `selenium_python`, `pytest`
- Tools: `read_requirement_file`, `save_test_output`, `validate_json_output`
- Structured JSON output with test cases and Gherkin scenarios
- Framework-specific code generation (Java, Python)
- `.env` configuration for API keys
