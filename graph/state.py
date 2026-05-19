from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    output_mode: str          # what type of Testcase selenium, python, design doc
    requirement: str          # clarified requirement (set by Analyst)
    test_design: str          # JSON test cases (set by Designer)
    generated_code: str       # framework code (set by Coder)
    review_feedback: str      # reviewer notes (set by Reviewer)
    iteration_count: int      # prevent infinite loops (max 2 retries)
