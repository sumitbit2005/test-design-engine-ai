# Test Design Engine AI

An AI-powered test design agent built with LangGraph and OpenAI. It generates test cases, Gherkin scenarios, and executable automation code from natural language requirements.

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INPUT                           │
│         (requirement + output_mode selection)               │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      main.py                                │
│              Entrypoint / CLI Runner                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   graph/builder.py                           │
│               LangGraph StateGraph                          │
│                                                             │
│   ┌───────┐      ┌───────────────┐      ┌──────────┐      │
│   │ START │─────▶│  agent node   │─────▶│   END    │      │
│   └───────┘      │ (LLM + prompt)│      └──────────┘      │
│                  └───────┬───────┘           ▲              │
│                          │                   │              │
│                 has tool calls?               │              │
│                    yes │              no ─────┘              │
│                        ▼                                    │
│                  ┌───────────┐                              │
│                  │tools node │                              │
│                  │(ToolNode) │──────── loops back ──┐       │
│                  └───────────┘                      │       │
│                        ▲                            │       │
│                        └────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## Agent Loop Detail

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  ┌─────────┐    ┌──────────────────┐    ┌───────────┐   │
│  │  START  │───▶│  test_design_    │───▶│ use_tool_ │   │
│  │         │    │  process()       │    │ or_agent()│   │
│  └─────────┘    │                  │    └─────┬─────┘   │
│                 │ • Reads mode     │          │          │
│                 │ • Builds prompt  │     ┌────┴────┐    │
│                 │ • Calls GPT-4o   │     │         │    │
│                 └──────────────────┘  "continue" "end"  │
│                         ▲                │         │    │
│                         │                ▼         ▼    │
│                  ┌──────┴───────┐   ┌────────┐  ┌───┐  │
│                  │  tool_node   │   │ tools  │  │END│  │
│                  │              │◀──┤ node   │  └───┘  │
│                  │ Executes:    │   └────────┘         │
│                  │ • validate   │                       │
│                  │ • save       │                       │
│                  │ • read file  │                       │
│                  └──────────────┘                       │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Project Structure

```
test-design-engine-ai/
├── main.py                  # CLI entrypoint
├── config.py                # Environment config (API keys, model)
├── requirements.txt         # Python dependencies
├── .env.example             # Template for environment variables
├── graph/
│   ├── state.py             # AgentState TypedDict definition
│   ├── nodes.py             # LLM node, routing logic, prompts
│   └── builder.py           # StateGraph wiring and compilation
└── tools/
    ├── __init__.py           # Tool registry (exports tools list)
    ├── read_requirement_file.py   # Read requirements from file
    ├── save_test_output.py        # Save output to file
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
| **Coverage** | AI systematically covers positive, negative, edge case, and security scenarios — less likely to miss blind spots |
| **Multi-framework** | One requirement → output in any framework. No need to manually translate between RestAssured, Selenium, pytest |
| **Self-validating** | The agent validates its own JSON output before returning, reducing broken/malformed results |
| **File I/O** | Read requirements from docs, save output directly to files — fits into CI/CD or batch workflows |
| **Extensible** | Add new output modes or tools without changing the core agent logic |

### Who It's For

- **QA Engineers** — accelerate test design from requirements
- **Dev Teams** — generate test scaffolding alongside feature development
- **Tech Leads** — ensure consistent test coverage standards across the team
- **Solo Developers** — get QA-level test thinking without a dedicated QA resource

### Compared to Just Using ChatGPT

| | ChatGPT / Raw LLM | Test Design Engine |
|---|---|---|
| Structured output | Inconsistent | Enforced JSON schema |
| Tool use (save/validate) | Manual copy-paste | Automated via agent loop |
| Framework-specific code | Requires re-prompting | One mode switch |
| Batch processing | Not possible | Read from files |
| Reproducible | Depends on prompt | Same prompt every time |
| Self-correction | None | Validates own output, retries |

## Setup

```bash
# Clone the repo
git clone <repo-url>
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
Output modes: design_only, rest_assured, selenium_java, selenium_python, pytest
Select mode:
> rest_assured
Enter your requirement:
> User login API with email and password, returns JWT token
```

## Tools

The agent has access to these tools during execution:

| Tool | Purpose |
|------|---------|
| `read_requirement_file` | Load requirements from a `.txt`, `.md`, or `.feature` file |
| `save_test_output` | Persist generated output to disk |
| `validate_json_output` | Self-check that JSON output is valid (used in `design_only` mode) |

## Tech Stack

- **LangGraph** — Agent orchestration with stateful graph
- **LangChain** — LLM integration and tool framework
- **OpenAI GPT-4o** — Language model for test generation
- **Python 3.10+** — Runtime

## License

MIT
