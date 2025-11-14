from mini_agent_gemini import MiniAgent

def main():
    agent = MiniAgent()
    print("Mini-Agent (Google Gemini) is running. Type 'exit' or 'quit' to stop.")

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        response = agent.run(user_input)
        print("Agent:", response)

if __name__ == "__main__":
    main()
