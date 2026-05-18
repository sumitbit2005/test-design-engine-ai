from langchain_core.messages import HumanMessage

from graph.builder import agent


def run(requirement: str, mode: str = "design_only"):
    result = agent.invoke({
        "messages": [HumanMessage(content=requirement)],
        "output_mode": mode,
    })
    return result["messages"][-1].content


if __name__ == "__main__":
    print("Output modes: design_only, rest_assured, selenium_java, selenium_python, pytest")
    mode = input("Select mode:\n> ").strip() or "design_only"
    user_input = input("Enter your requirement:\n> ")
    output = run(user_input, mode)
    print("\n--- Generated Test Design ---\n")
    print(output)
