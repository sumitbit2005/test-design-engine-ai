# Next Steps - Test Design Engine AI

## Completed ✅

### Multi-Agent Workflow (v0.3.0)

- [x] Split single agent into 4 specialized agents (Analyst, Designer, Coder, Reviewer)
- [x] Tool isolation per agent (separate ToolNodes)
- [x] Conditional routing with loop-back from Reviewer → Designer
- [x] Iteration cap to prevent infinite loops
- [x] Analyst safeguard — forces CLEAR after 2+ user messages
- [x] Real-time progress indicators showing active agent
- [x] Streaming execution via `agent.stream()`

---

## TODO: Performance Optimizations (v0.3.1)

### Skip Analyst for Clear Requirements
- If the user's first message is detailed enough (contains feature + inputs + expected behavior), skip the Analyst and go directly to Designer
- Add a lightweight classifier or heuristic check before entering the graph

### Skip Reviewer for `design_only` Mode
- In `design_only` mode, the Reviewer adds overhead without much value since there's no code to review
- Add a conditional edge that skips Reviewer when `output_mode == "design_only"`

### Parallel Tool Calls
- When Designer calls both `validate_json_output` and `search_history`, execute them in parallel
- LangGraph supports this natively with multiple tool calls in a single response

---

## TODO: Web UI (v0.4.0)

| Feature | Description |
|---------|-------------|
| Streamlit/Gradio interface | Chat UI with mode selector dropdown |
| Progress visualization | Show agent pipeline with active step highlighted |
| History sidebar | Browse and re-run past generations |
| Download buttons | Export generated code as files |
| Diff view | Compare new vs existing test cases |

---

## TODO: Integrations (v0.5.0)

| Feature | Description |
|---------|-------------|
| Jira Integration | Pull requirements from Jira tickets directly |
| OpenAPI/Swagger Input | Feed API spec → auto-generate contract tests |
| GitHub Action | Auto-generate tests on PR with requirement docs |
| Export to TestRail/Xray | Push generated test cases to test management tools |
| Confluence Input | Read requirement pages from Confluence |

---

## TODO: Advanced Features (v0.6.0)

| Feature | Description |
|---------|-------------|
| Custom Prompt Templates | Let users define output format per project |
| Test Data Generation | Generate realistic test data sets alongside test cases |
| Visual Regression Tests | Generate Playwright/Cypress visual test scripts |
| API Contract Testing | Generate Pact/contract tests from OpenAPI specs |
| Load Test Generation | Generate k6/Locust scripts from requirements |
| Multi-language Support | Add C#/NUnit, TypeScript/Jest output modes |

---

## Architecture Notes

### Current State (v0.3.0)

```
User → Analyst → Designer → Coder → Reviewer → END
                    ▲                    │
                    └── (gaps found) ────┘
```

### Tool Distribution

| Agent | Tools | Enforcement |
|-------|-------|-------------|
| Analyst | `read_requirement_file` | `.bind_tools()` + `ToolNode` |
| Designer | `validate_json_output`, `search_history` | `.bind_tools()` + `ToolNode` |
| Coder | `save_to_db`, `save_test_output` | `.bind_tools()` + `ToolNode` |
| Reviewer | `search_history` | `.bind_tools()` + `ToolNode` |

### State Schema

```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    output_mode: str          # framework selection
    requirement: str          # clarified requirement (set by Analyst)
    test_design: str          # JSON test cases (set by Designer)
    generated_code: str       # framework code (set by Coder)
    review_feedback: str      # reviewer notes (set by Reviewer)
    iteration_count: int      # prevent infinite loops (max 2 retries)
```

### Key Design Decisions

1. **Separate ToolNodes per agent** — prevents tool leakage between agents (LLM can't call what it can't see)
2. **CLEAR: prefix protocol** — simple string-based routing signal from Analyst to Designer
3. **DONE: prefix protocol** — signals completion from Designer and Coder
4. **GAPS: prefix protocol** — signals coverage issues from Reviewer back to Designer
5. **Streaming with updates mode** — enables real-time progress without changing agent logic
6. **Conversation accumulation** — full message history passed on each invocation for multi-turn context
