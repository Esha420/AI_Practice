#agents.py
import os
from crewai import Agent, LLM  # <-- Import LLM from crewai
from tools import tool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# We no longer need this import, as we are using crewai's native LLM class:
# from langchain_google_genai import ChatGoogleGenerativeAI 


# --- Define the LLM using the native crewai.LLM class ---
# Use the 'gemini/' prefix to tell LiteLLM (which is built into crewai) 
# how to connect to the Google Gemini provider.
# It will automatically pick up the GOOGLE_API_KEY environment variable.
llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.5,
    # verbose=True, # Verbosity is often handled by agent/crew config in crewAI
    # If the key is not in the environment, you can pass it here:
    api_key=os.getenv("GOOGLE_API_KEY") 
)


# Creating a senior researcher agent with memory and verbose mode
news_researcher=Agent(
    role="Senior Researcher",
    goal='Unccover ground breaking technologies in {topic}',
    verbose=True,
    memory=True,
    backstory=(
        "Driven by curiosity, you're at the forefront of"
        "innovation, eager to explore and share knowledge that could change"
        "the world."

    ),
    tools=[tool],
    llm=llm, # Pass the crewai.LLM instance
    allow_delegation=True

)

## creating a write agent with custom tools responsible in writing news blog
news_writer = Agent(
  role='Writer',
  goal='Narrate compelling tech stories about {topic}',
  verbose=True,
  memory=True,
  backstory=(
    "With a flair for simplifying complex topics, you craft"
    "engaging narratives that captivate and educate, bringing new"
    "discoveries to light in an accessible manner."
  ),
  tools=[tool],
  llm=llm, # Pass the crewai.LLM instance
  allow_delegation=False
)