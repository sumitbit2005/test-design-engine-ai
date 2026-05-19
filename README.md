# Test Design Engine AI

An AI-powered multi-agent test design system built with LangGraph and OpenAI. Four specialized agents collaborate to analyze requirements, design test cases, generate automation code, and review coverage — all from natural language input via a chat-style CLI.

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INPUT                           │
│            "generate login test cases"                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      main.py                                │
│           Chat CLI with /commands                           │
│           Conversation memory across turns                   │
│           Real-time progress indicators per agent           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   graph/builder.py                           │
│               LangGraph StateGraph                          │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌────────┐    ┌────────┐ │
│  │ Analyst  │───▶│ Designer │───▶│ Coder  │───▶│Reviewer│ │
│  │  Agent   │    │  Agent   │    │ Agent  │    │ Agent  │ │
│  └────┬─────┘    └────┬─────┘    └───┬────┘    └───┬────┘ │
│       │               │              │              │      │
│       ▼               ▼              ▼              ▼      │
│  ┌──────────┐    ┌──────────┐    ┌────────┐    ┌────────┐ │
│  │ Analyst  │    │ Designer │    │ Coder  │    │Reviewer│ │
│  │  Tools   │    │  Tools   │    │ Tools  │    │ Tools  │ │
│  └──────────┘    └──────────┘    └────────┘    └────────┘ │
│                                                             │
│  Reviewer can loop back to Designer (max 2 iterations)     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                             │
│                                                             │
│   ┌──────────────┐         ┌────────────────────────┐      │
│   │  SQLite DB   │         │   output/ directory     │      │
│   │ (results.db) │         │   .json / .java / .py   │      │
│   └──────────────┘         └────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Multi-Agent Pipeline

```
┌───────────────────────────────────────────────────────────────────┐
│                        ANALYST AGENT                               │
│  🔍 Analyzing requirement...                                      │
│                                                                   │
│  Role: Clarify vague requirements, ask questions, structure input │
│  Tools: read_requirement_file                                     │
│  Output: Structured requirement prefixed with CLEAR:              │
│  Routing: Clear → Designer | Vague → ask user (END)              │
│  Safety: Forces CLEAR after 2+ user messages (no infinite loops) │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                       DESIGNER AGENT                               │
│  ✏️  Designing test cases...                                       │
│                                                                   │
│  Role: Generate test cases, edge cases, Gherkin scenarios         │
│  Tools: validate_json_output, search_history                      │
│  Output: Structured JSON test design (test_cases + gherkin)       │
│  Routing: Always passes to Coder                                  │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                        CODER AGENT                                 │
│  💻 Generating code/output...                                     │
│                                                                   │
│  Role: Convert test design into framework-specific code           │
│        Reads output_mode to decide framework                      │
│  Tools: save_to_db, save_test_output                              │
│  Output: Executable code (.java / .py / .json) saved to file + DB │
│  Routing: Always passes to Reviewer                               │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                       REVIEWER AGENT                               │
│  🔎 Reviewing coverage...                                         │
│                                                                   │
│  Role: Check coverage gaps, suggest improvements                  │
│  Tools: search_history (check duplicates)                         │
│  Output: Review summary (coverage score, missing scenarios)       │
│  Routing: Gaps → loop back to Designer | Approved → END          │
│  Safety: Max 2 iterations to prevent infinite loops               │
└───────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
test-design-engine-ai/
├── main.py                  # Chat CLI with streaming progress indicators
├── config.py                # Environment config (API keys, model)
├── requirements.txt         # Python dependencies
├── .env.example             # Template for environment variables
├── results.db               # SQLite database (auto-created)
├── output/                  # Generated test files (auto-created)
│   └── <project>/           # Organized by project name
│       ├── design_only_*.json
│       ├── rest_assured_*.java
│       └── selenium_python_*.py
├── graph/
│   ├── state.py             # AgentState TypedDict (multi-agent state)
│   ├── nodes.py             # Agent nodes, prompts, routing functions
│   └── builder.py           # StateGraph wiring and compilation
└── tools/
    ├── __init__.py           # Tool registry (scoped per agent)
    ├── read_requirement_file.py   # Read requirements from file
    ├── save_test_output.py        # Save output to file
    ├── save_to_db.py              # Save to SQLite + write output file
    ├── search_db.py               # Search past results by keyword/mode
    └── validate_json_output.py    # Validate JSON structure
```

## Output Modes

| Mode | Output |
|------|--------|
| `design_only` | Structured JSON with test cases + Gherkin scenarios |
| `rest_assured` | Java code — JUnit 5 + RestAssured |
| `selenium_java` | Java code — JUnit 5 + Selenium 4 + Page Object Model |
| `selenium_python` | Python code — pytest + Selenium + POM |
| `pytest` | Python code — pytest + requests for API testing |

## Progress Indicators

The CLI shows real-time progress as each agent executes:

```
You > login page with username and password

⏳ Generating tests (mode: design_only)...

  🔍 Analyzing requirement...
  ✏️  Designing test cases...
  📂 Designer using tools...
  ✏️  Designing test cases...
  💻 Generating code/output...
  📂 Coder using tools...
  💻 Generating code/output...
  🔎 Reviewing coverage...

<final output>
```

## Why Use This?

### The Problem

- Writing test cases manually is repetitive and time-consuming
- QA engineers spend hours translating requirements into test scenarios
- Test coverage gaps slip through when done manually under deadline pressure
- Switching between frameworks (RestAssured, Selenium, pytest) means rewriting the same logic differently each time

### What This Solves

| Benefit | Description |
|---------|-------------|
| **Speed** | Generate 10+ test cases in seconds instead of hours of manual writing |
| **Consistency** | Every output follows the same structure — no more inconsistent test docs across team members |
| **Coverage** | Multi-agent review catches gaps — positive, negative, edge case, and security scenarios |
| **Multi-framework** | One requirement → output in any framework. No need to manually translate between RestAssured, Selenium, pytest |
| **Self-validating** | The agent validates its own JSON output before returning, reducing broken/malformed results |
| **Self-reviewing** | Reviewer agent checks coverage and loops back to Designer if gaps are found |
| **Persistent storage** | All results saved to SQLite + files — searchable history, never lose generated tests |
| **Conversation memory** | Ask follow-up questions, refine results, search history — all in one session |
| **Extensible** | Add new output modes, agents, or tools without changing the core graph logic |

### Who It's For

- **QA Engineers** — accelerate test design from requirements
- **Dev Teams** — generate test scaffolding alongside feature development
- **Tech Leads** — ensure consistent test coverage standards across the team
- **Solo Developers** — get QA-level test thinking without a dedicated QA resource

### Compared to Just Using ChatGPT

| | ChatGPT / Raw LLM | Test Design Engine |
|---|---|---|
| Structured output | Inconsistent | Enforced JSON schema |
| Requirement analysis | None | Dedicated Analyst agent |
| Coverage review | None | Dedicated Reviewer agent |
| Tool use (save/validate) | Manual copy-paste | Automated via agent loop |
| Framework-specific code | Requires re-prompting | One mode switch |
| Batch processing | Not possible | Read from files |
| Reproducible | Depends on prompt | Same prompt every time |
| Self-correction | None | Validates own output, retries |
| History & search | None | SQLite + file storage |
| Conversation memory | Per-session only | Multi-turn within session |

## Tool Isolation

Each agent only has access to its own tools — enforced at both the LLM binding level and the ToolNode level:

| Agent | Tools | Purpose |
|-------|-------|---------|
| Analyst | `read_requirement_file` | Load requirements from files |
| Designer | `validate_json_output`, `search_history` | Validate output, check for duplicates |
| Coder | `save_to_db`, `save_test_output` | Persist results to DB and files |
| Reviewer | `search_history` | Check for duplicate/existing coverage |

## Setup

```bash
# Clone the repo
git clone https://github.com/sumitbit2005/test-design-engine-ai.git
cd test-design-engine-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Usage

```bash
python main.py
```

```
🤖 Sumi - Test Design Agent
────────────────────────────────────────
Just type your requirement and I'll generate tests.

Commands:
  /mode <name>  - Switch output mode
  /modes        - List available modes
  /help         - Show this help
  /clear        - Reset conversation
  exit          - Quit
────────────────────────────────────────
Current mode: design_only

You > /mode selenium_java
✅ Mode: selenium_java

You > login page with username, password, and ADFS authentication

⏳ Generating tests (mode: selenium_java)...

  🔍 Analyzing requirement...
  ✏️  Designing test cases...
  📂 Designer using tools...
  ✏️  Designing test cases...
  💻 Generating code/output...
  📂 Coder using tools...
  💻 Generating code/output...
  🔎 Reviewing coverage...

[Generated Selenium Java code saved to output/]
```

## Tech Stack

- **LangGraph** — Multi-agent orchestration with stateful graph
- **LangChain** — LLM integration and tool framework
- **OpenAI GPT-4o** — Language model for test generation
- **SQLite** — Lightweight persistent storage (zero setup)
- **Python 3.9+** — Runtime

## License

MIT
