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
        try:
            result = agent.invoke({
                "messages": conversation,
                "output_mode": mode,
            })
            response = result["messages"][-1].content
            conversation = result["messages"]  
            print(f"{response}\n")
        except Exception as e:
            print(f" Error: {e}\n")


if __name__ == "__main__":
    main()
