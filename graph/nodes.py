import httpx
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from config import OPENAI_MODEL, OPENAI_API_KEY
from graph.state import AgentState
from tools import tool_analyst, tool_design, tool_code, tool_review


http_client = httpx.Client(verify=False)

#Analyst Tool Node
analyst_model = ChatOpenAI(
    model=OPENAI_MODEL,
    api_key=OPENAI_API_KEY,
    http_client=http_client,
).bind_tools(tool_analyst)

analyst_tool_node = ToolNode(tools=tool_analyst)


#Design Tool Node
design_model = ChatOpenAI(
    model=OPENAI_MODEL,
    api_key=OPENAI_API_KEY,
    http_client=http_client,
).bind_tools(tool_design)

design_tool_node = ToolNode(tools=tool_design)


#Code Tool Node
code_model = ChatOpenAI(
    model=OPENAI_MODEL,
    api_key=OPENAI_API_KEY,
    http_client=http_client,
).bind_tools(tool_code)

code_tool_node = ToolNode(tools=tool_code)


#Review Tool Node
review_model = ChatOpenAI(
    model=OPENAI_MODEL,
    api_key=OPENAI_API_KEY,
    http_client=http_client,
).bind_tools(tool_review)

review_tool_node = ToolNode(tools=tool_review)


ANALYST_PROMPT = (
    "You are a Requirements Analyst for a QA team.\n\n"
    "Your job is to analyze the user's requirement and ensure it is clear, complete, and testable.\n\n"
    "## What you do:\n"
    "- If the requirement is extremely vague (one or two words with no context), ask ONE round of clarifying questions (then stop, wait for answer)\n"
    "- If a file path is mentioned, use read_requirement_file to load it\n"
    "- Once the requirement is clear enough to generate test cases, rewrite it in a structured format and prefix your response with CLEAR:\n\n"
    "## IMPORTANT — When to mark as CLEAR:\n"
    "- If the user has described a feature with at least: what it does, basic inputs, and one expected behavior — mark it CLEAR\n"
    "- If the user has already answered a clarifying question — DO NOT ask more questions. Mark it CLEAR with what you have\n"
    "- You do NOT need every edge case spelled out. The Designer will handle coverage gaps\n"
    "- After at most 1 round of questions, you MUST produce a CLEAR: output on the next turn\n"
    "- Err on the side of proceeding rather than asking more questions\n\n"
    "## Output format when clear:\n"
    "CLEAR:\n"
    "Feature: <feature name>\n"
    "Description: <what it does>\n"
    "Actors: <who uses it>\n"
    "Inputs: <what data is involved>\n"
    "Expected behavior: <what should happen>\n"
    "Edge cases to consider: <list>\n\n"
    "## Rules:\n"
    "- Do NOT generate test cases — that's the Designer's job\n"
    "- Do NOT write code — that's the Coder's job\n"
    "- If requirement is already clear and detailed, just prefix with CLEAR: and pass it through\n"
    "- NEVER ask more than one round of clarifying questions\n"
)

DESIGNER_PROMPT = (
    "You are a Senior Test Designer.\n\n"
    "You receive a clarified requirement and generate comprehensive test coverage.\n\n"
    "## What you do:\n"
    "- Generate test cases (positive, negative, edge case, security)\n"
    "- Generate Gherkin scenarios (Given/When/Then)\n"
    "- Use search_history to check if similar tests already exist\n"
    "- Use validate_json_output to verify your JSON before responding\n"
    "- Generate at least 5 test cases\n\n"
    "## Output:\n"
    "Prefix your final response with DONE:\n"
    "Then provide the test design JSON.\n\n"
    "## Rules:\n"
    "- Do NOT write automation code — that's the Coder's job\n"
    "- Do NOT ask the user questions — that was the Analyst's job\n"
    "- Use realistic test data, not placeholders\n"
    "- Prioritize: security issues are always high priority\n"
)

CODER_PROMPT = (
    "You are a Test Automation Engineer.\n\n"
    "You receive test cases/scenarios and convert them into executable automation code.\n\n"
    "## What you do:\n"
    "- Read the test design from the conversation\n"
    "- Generate executable test code based on the output_mode\n"
    "- Save the output using save_to_db tool\n"
    "- Prefix your final response with DONE:\n\n"
    "## Rules:\n"
    "- Do NOT redesign the test cases — just implement what the Designer gave you\n"
    "- Do NOT ask questions — just generate code\n"
    "- After saving, give a brief summary (file path, number of test methods)\n"
    "- Only show full code if user explicitly asks\n"
)


REVIEWER_PROMPT = (
    "You are a QA Review Lead.\n\n"
    "You review generated test cases and code for coverage gaps.\n\n"
    "## What you check:\n"
    "- Are positive, negative, edge case, and security scenarios covered?\n"
    "- Are boundary values tested?\n"
    "- Is error handling covered?\n"
    "- Are there duplicate tests (use search_history to check)?\n"
    "- Is the test data realistic?\n\n"
    "## Output:\n"
    "- If gaps found: prefix with GAPS: and list what's missing\n"
    "- If approved: give a brief coverage summary (score, what's covered)\n\n"
    "## Rules:\n"
    "- Do NOT generate test cases yourself — send feedback to Designer\n"
    "- Do NOT write code — that's the Coder's job\n"
    "- Be specific about what's missing\n"
)


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



def analyst_agent(state: AgentState) -> AgentState:
    """Clarifies vague requirements. Asks questions if needed.
    Prefixes with CLEAR: when requirement is understood."""
    system_message = SystemMessage(content=ANALYST_PROMPT)
    response = analyst_model.invoke([system_message] + list(state["messages"]))
    result = {"messages": [response]}
    if "CLEAR:" in response.content:
        result["requirement"] = response.content  
    return result


def design_agent(state: AgentState) -> AgentState:
    """Generates test cases and Gherkin scenarios from clarified requirement.
    Prefixes with DONE: when test design is complete."""
    system_message = SystemMessage(content=DESIGNER_PROMPT)
    response = design_model.invoke([system_message] + list(state["messages"]))
    result = {"messages": [response]}
    if "DONE:" in response.content:
        result["test_design"] = response.content  
    return result



def code_agent(state: AgentState) -> AgentState:
    """Converts test design into framework-specific code based on output_mode.
    Saves to DB and file. Prefixes with DONE: when complete."""
    mode = state.get("output_mode", "design_only")
    framework_instruction = FRAMEWORK_INSTRUCTIONS.get(
        mode, FRAMEWORK_INSTRUCTIONS["design_only"]
    )
    system_prompt = (
        f"{CODER_PROMPT}\n\n## Output Mode: {mode}\n\n{framework_instruction}"
    )
    system_message = SystemMessage(content=system_prompt)
    response = code_model.invoke([system_message] + list(state["messages"]))
    result = {"messages": [response]}
    if "DONE:" in response.content:
        result["generated_code"] = response.content  
    return result


def review_agent(state: AgentState) -> AgentState:
    """Reviews test coverage for gaps. Returns GAPS: if issues found,
    otherwise approves with a coverage summary."""
    system_message = SystemMessage(content=REVIEWER_PROMPT)
    response = review_model.invoke([system_message] + list(state["messages"]))
    result = {"messages": [response]}
    if "GAPS:" in response.content:
        result["review_feedback"] = response.content
        result["iteration_count"] = state.get("iteration_count", 0) + 1
    return result


def analyst_router(state: AgentState):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    # If analyst determined requirement is clear
    if "CLEAR:" in last.content:
        return "clear"
    from langchain_core.messages import HumanMessage as HM
    human_count = sum(1 for m in state["messages"] if isinstance(m, HM))
    if human_count >= 2:
        last.content = "CLEAR:\n" + last.content
        return "clear"
    return "need_input"


def reviewer_router(state: AgentState):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    if state.get("iteration_count", 0) >= 2:
        return "approved"  # prevent infinite loops
    if "GAPS:" in last.content:
        return "gaps"
    return "approved"


def code_router(state: AgentState):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "done"

def designer_router(state: AgentState):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "done"
