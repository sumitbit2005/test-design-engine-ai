from langchain_core.messages import HumanMessage

from graph.builder import agent

MODES = ["design_only", "rest_assured", "selenium_java", "selenium_python", "pytest"]


def main():
    print("\n🤖 Sumi - Test Design Agent")
    print("─" * 40)
    print("Just type your requirement and I'll generate tests.")
    print("")
    print("Commands:")
    print("  /mode <name>  - Switch output mode")
    print("  /modes        - List available modes")
    print("  /help         - Show this help")
    print("  exit          - Quit")
    print("─" * 40)

    mode = "design_only"
    print(f"Current mode: {mode}\n")

    conversation = []  # keeps message history

    while True:
        user_input = input("You > ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("👋 Bye!")
            break

        # Commands
        if user_input == "/help":
            print("\nJust type any requirement. Examples:")
            print('  "Login page with email and password"')
            print('  "REST API for user registration"')
            print('  "Shopping cart checkout flow"')
            print(f"\nCurrent mode: {mode}")
            print("Use /mode <name> to switch output format.")
            print("Use /clear to reset conversation history.\n")
            continue

        if user_input == "/modes":
            print("\nAvailable modes:")
            for m in MODES:
                marker = " ← current" if m == mode else ""
                print(f"  • {m}{marker}")
            print("")
            continue

        if user_input.startswith("/mode"):
            new_mode = user_input.replace("/mode", "").strip()
            if new_mode in MODES:
                mode = new_mode
                print(f"✅ Mode: {mode}\n")
            else:
                print(f" Unknown mode. Available: {', '.join(MODES)}\n")
            continue

        if user_input == "/clear":
            conversation = []
            print("🗑️  Conversation cleared.\n")
            continue

        conversation.append(HumanMessage(content=user_input))
        print(f"\n⏳ Generating tests (mode: {mode})...\n")

        NODE_LABELS = {
            "analyst_agent": "🔍 Analyzing requirement...",
            "tool_analyst": "📂 Analyst using tools...",
            "design_agent": "✏️  Designing test cases...",
            "tool_design": "📂 Designer using tools...",
            "code_agent": "💻 Generating code/output...",
            "tool_code": "📂 Coder using tools...",
            "review_agent": "🔎 Reviewing coverage...",
            "tool_review": "📂 Reviewer using tools...",
        }

        try:
            last_response = None
            for event in agent.stream(
                {"messages": conversation, "output_mode": mode},
                stream_mode="updates",
            ):
                for node_name, node_output in event.items():
                    label = NODE_LABELS.get(node_name, f"⚙️  {node_name}...")
                    print(f"  {label}")
                    # Capture the latest messages for final output
                    if "messages" in node_output:
                        last_response = node_output["messages"][-1]

            if last_response:
                conversation.append(last_response)
                print(f"\n{last_response.content}\n")
            else:
                print("\n⚠️  No response generated.\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
