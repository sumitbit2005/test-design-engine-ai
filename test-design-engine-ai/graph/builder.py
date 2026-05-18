from langgraph.graph import START, END, StateGraph

from graph.state import AgentState
from graph.nodes import test_design_process, use_tool_or_agent, tool_node

workflow = StateGraph(AgentState)

workflow.add_node("agent", test_design_process)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    use_tool_or_agent,
    {"continue": "tools", "end": END},
)
workflow.add_edge("tools", "agent")

agent = workflow.compile()
