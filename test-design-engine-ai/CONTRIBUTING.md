# Contributing

Thanks for your interest in contributing!

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests to verify everything works
5. Commit with a clear message
6. Push and open a Pull Request

## Adding a New Tool

1. Create a new file in `tools/`
2. Use the `@tool` decorator from `langchain_core.tools`
3. Add a clear docstring — the LLM uses it to decide when to call your tool
4. Register it in `tools/__init__.py`
5. Test it independently before running the full agent

## Code Style

- Keep functions focused and small
- Use type hints for tool parameters
- Handle errors gracefully — return error dicts, don't crash the agent
- Never hardcode URLs, tokens, or project-specific values

## Environment

- Python 3.9+
- All secrets go in `.env` (never commit this file)
- Use `.env.example` as a template
