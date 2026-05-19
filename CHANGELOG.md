# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2026-05-21

### Added
- **Multi-agent architecture** — 4 specialized agents (Analyst, Designer, Coder, Reviewer) replace the single monolithic agent
- **Real-time progress indicators** — CLI shows which agent is currently executing (🔍 ✏️ 💻 🔎)
- **Streaming execution** — uses `agent.stream()` with `stream_mode="updates"` for live node-by-node feedback
- **Analyst agent** — clarifies vague requirements before generating tests
- **Designer agent** — generates structured test cases and Gherkin scenarios
- **Coder agent** — converts test designs into framework-specific code
- **Reviewer agent** — checks coverage gaps and loops back to Designer if needed
- **Tool isolation** — each agent has its own scoped ToolNode (double enforcement via `.bind_tools()` + `ToolNode`)
- **Infinite loop prevention** — analyst forces CLEAR after 2+ user messages; reviewer caps at 2 iterations
- **Iteration tracking** — `iteration_count` in state prevents unbounded reviewer loops

### Changed
- `main.py` rewritten to use `agent.stream()` instead of `agent.invoke()` for progress visibility
- `graph/nodes.py` split into 4 agent functions with dedicated prompts and routing
- `graph/builder.py` wires 4 agents with conditional edges and tool nodes
- `graph/state.py` expanded with `requirement`, `test_design`, `generated_code`, `review_feedback`, `iteration_count`
- Analyst prompt updated to be more decisive — stops asking questions after one round of clarification



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
