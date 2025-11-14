from agent import simulated_llm_function_call

def main():
    print("Mini-Agent with simulated LLM function calling is running. Type 'exit' or 'quit' to stop.")
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        response = simulated_llm_function_call(user_input)
        print("Agent:", response)

if __name__ == "__main__":
    main()
