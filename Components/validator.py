import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
import streamlit as st

# Load env vars
load_dotenv()

# Set keys
os.environ["SERPER_API_KEY"] = st.secrets("SERPER_API_KEY")
os.environ["GROQ_API_KEY"] = st.secrets("GROQ_API_KEY")

# Initialize LLM
llm = ChatGroq(
    groq_api_key=os.environ["GROQ_API_KEY"],
    model_name="meta-llama/llama-4-scout-17b-16e-instruct"
)

# Google search tool
search_tool = GoogleSerperAPIWrapper()

# Agent setup
tools = [
    Tool(
        name="Google Search",
        func=search_tool.run,
        description="Use to find competitors, market need, and trends for a startup idea."
    )
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Prompt for generating refined ideas
idea_prompt = PromptTemplate(
    input_variables=["idea"],
    template="""
You are a startup idea generator.

A user gave this rough startup idea: "{idea}"

Suggest 3 realistic, mature startup ideas with clear unique angles. Each idea should be 2-3 sentences max.

Format:
### Idea 1
**Name**: ...
**Description**: ...
**Unique Angle**: ...

### Idea 2
...
"""
)

idea_chain = idea_prompt | llm

# -----------------------------
# FUNCTIONS
# -----------------------------

def generate_ideas(user_idea: str) -> str:
    """Generates 3 refined startup ideas using the idea_chain."""
    response = idea_chain.invoke({"idea": user_idea})
    return response.content

def extract_idea_names(text: str) -> list:
    """Parses idea names from the generated text."""
    names = []
    for line in text.splitlines():
        if line.startswith("**Name**"):
            name = line.split("**Name**:")[-1].strip()
            names.append(name)
    return names

def research_idea_with_agent(idea: str) -> str:
    """Uses agent to fetch real-time researched markdown report."""
    agent_prompt = f"""
You are a startup researcher.

Startup Idea: {idea}

Create a professional report in Markdown format including:

Project Summary according to the idea 

### 🏢 Competitors

| Name | Description | Website |
|------|-------------|---------|
| ...  | ...         | ...     |

### 📈 Market Need

- Bullet points showing demand or trends
- Mention pain points in current solutions

### 💡 Unique Angle / Gap

- What is missing in the market?
- How can this idea fill the gap?

Keep it clean and structured.

"""
    return agent.run(agent_prompt)
