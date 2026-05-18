import httpx
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from config import OPENAI_MODEL, OPENAI_API_KEY
from graph.state import AgentState
from tools import tools

http_client = httpx.Client(verify=False)

model = ChatOpenAI(
    model=OPENAI_MODEL,
    api_key=OPENAI_API_KEY,
    http_client=http_client,
).bind_tools(tools)

tool_node = ToolNode(tools=tools)

FRAMEWORK_INSTRUCTIONS = {
    "design_only": (
        "Return a single JSON object with this exact structure:\n\n"
        "{\n"
        '  "requirement_summary": "Brief one-line summary of the requirement",\n'
        '  "test_cases": [\n'
        "    {\n"
        '      "id": "TC-001",\n'
        '      "title": "Short descriptive title",\n'
        '      "type": "positive | negative | edge_case | security | performance",\n'
        '      "priority": "high | medium | low",\n'
        '      "preconditions": ["list of preconditions"],\n'
        '      "steps": ["step 1", "step 2"],\n'
        '      "expected_result": "what should happen",\n'
        '      "test_data": "relevant input data if applicable"\n'
        "    }\n"
        "  ],\n"
        '  "gherkin_scenarios": [\n'
        "    {\n"
        '      "id": "SC-001",\n'
        '      "feature": "Feature name",\n'
        '      "scenario": "Scenario title",\n'
        '      "tags": ["@smoke", "@regression"],\n'
        '      "steps": "Given ...\\nWhen ...\\nThen ..."\n'
        "    }\n"
        "  ],\n"
        '  "coverage_notes": {\n'
        '    "total_cases": 0,\n'
        '    "by_type": {"positive": 0, "negative": 0, "edge_case": 0, "security": 0},\n'
        '    "uncovered_areas": ["anything you couldn\'t cover without more info"]\n'
        "  }\n"
        "}\n\n"
        "Rules:\n"
        "- Return ONLY valid JSON, no markdown fences, no explanations outside the JSON\n"
        "- Use the validate_json_output tool to verify your output before responding"
    ),
    "rest_assured": (
        "Generate executable RestAssured (Java) test code using:\n"
        "- JUnit 5 + RestAssured\n"
        "- Use given()/when()/then() fluent API\n"
        "- Include proper imports\n"
        "- Use @Test, @DisplayName annotations\n"
        "- Parameterize test data where appropriate\n"
        "- Include assertions for status code, response body, headers\n"
        "- Structure: one test class per feature, methods per scenario\n"
        "- Return the complete Java file content, ready to compile"
    ),
    "selenium_java": (
        "Generate executable Selenium WebDriver test code in Java using:\n"
        "- JUnit 5 + Selenium 4\n"
        "- Page Object Model pattern\n"
        "- Use @BeforeEach for driver setup, @AfterEach for teardown\n"
        "- Use explicit waits (WebDriverWait), never Thread.sleep\n"
        "- Include proper locator strategies (By.id, By.cssSelector, By.xpath)\n"
        "- Add assertions with JUnit assertions\n"
        "- Return the complete Java file content, ready to compile"
    ),
    "selenium_python": (
        "Generate executable Selenium WebDriver test code in Python using:\n"
        "- pytest + selenium\n"
        "- Page Object Model pattern\n"
        "- Use explicit waits (WebDriverWait + expected_conditions)\n"
        "- Use @pytest.fixture for driver setup/teardown\n"
        "- Include proper locator strategies\n"
        "- Add assertions with assert statements\n"
        "- Return the complete Python file content, ready to run with pytest"
    ),
    "pytest": (
        "Generate executable pytest test code for API testing using:\n"
        "- pytest + requests/httpx\n"
        "- Use fixtures for setup\n"
        "- Parametrize with @pytest.mark.parametrize for data-driven tests\n"
        "- Include proper assertions\n"
        "- Group by feature using classes\n"
        "- Return the complete Python file content, ready to run with pytest"
    ),
}

BASE_SYSTEM_PROMPT = (
    "You are a Senior QA Automation Engineer specializing in test design and automation.\n\n"
    "Given a requirement from the user, generate comprehensive test coverage.\n\n"
    "## General Rules\n"
    "- Cover positive, negative, edge case, and security scenarios\n"
    "- Generate at least 5 test cases/methods\n"
    "- Use realistic test data, not placeholders\n"
    "- Prioritize: security and data integrity issues are always high priority\n"
    "- Use the save_test_output tool if the user specifies an output file\n"
    "- If the user provides a file path, use read_requirement_file to load it first\n"
)


def test_design_process(state: AgentState) -> AgentState:
    """Main agent node — builds the system prompt based on output_mode
    and invokes the LLM with the user's requirement."""
    mode = state.get("output_mode", "design_only")
    framework_instruction = FRAMEWORK_INSTRUCTIONS.get(
        mode, FRAMEWORK_INSTRUCTIONS["design_only"]
    )
    system_prompt = (
        f"{BASE_SYSTEM_PROMPT}\n\n## Output Mode: {mode}\n\n{framework_instruction}"
    )
    system_message = SystemMessage(content=system_prompt)
    response = model.invoke([system_message] + list(state["messages"]))
    return {"messages": [response]}


def use_tool_or_agent(state: AgentState):
    """Routing function — checks if the LLM response contains tool calls.
    Returns 'continue' to execute tools, or 'end' to finish."""
    messages = state["messages"]
    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"
    return "end"
