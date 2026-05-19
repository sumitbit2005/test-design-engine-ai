from langgraph.graph import START, END, StateGraph

from graph.state import AgentState
from graph.nodes import (
    analyst_agent, design_agent, code_agent, review_agent,
    analyst_tool_node, design_tool_node, code_tool_node, review_tool_node,
    analyst_router, designer_router, code_router, reviewer_router,
)
workflow = StateGraph(AgentState)


#Nodes

workflow.add_node("analyst_agent", analyst_agent)
workflow.add_node("tool_analyst", analyst_tool_node)

workflow.add_node("design_agent", design_agent)
workflow.add_node("tool_design", design_tool_node)

workflow.add_node("code_agent", code_agent)
workflow.add_node("tool_code", code_tool_node)

workflow.add_node("review_agent", review_agent)
workflow.add_node("tool_review", review_tool_node)


# Flow1
workflow.add_edge(START, "analyst_agent")
workflow.add_conditional_edges("analyst_agent", analyst_router, {
    "tools": "tool_analyst",
    "clear": "design_agent",
    "need_input": END,
})

workflow.add_edge("tool_analyst", "analyst_agent")

# Flow2
workflow.add_conditional_edges("design_agent", designer_router, {
    "tools": "tool_design",
    "done": "code_agent",
})
workflow.add_edge("tool_design", "design_agent")


#flow 3

workflow.add_conditional_edges("code_agent", code_router, {
    "tools": "tool_code",
    "done": "review_agent",
})
workflow.add_edge("tool_code", "code_agent")


#flow 4

workflow.add_conditional_edges("review_agent", reviewer_router, {
    "tools": "tool_review",
    "gaps": "design_agent",
    "approved": END
})
workflow.add_edge("tool_review", "review_agent")



agent = workflow.compile()
