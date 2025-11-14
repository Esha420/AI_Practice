# run_agent.py
from agent import mini_agent

def main():
    print("Mini-Agent with LLM-style reasoning is running. Type 'exit' or 'quit' to stop.")
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        response = mini_agent(user_input)
        print("Agent:", response)

if __name__ == "__main__":
    main()
