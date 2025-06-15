import streamlit as st
import os
import ast
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_core.prompts import PromptTemplate
from openai import OpenAI
from langchain.chat_models import ChatOpenAI


# Load environment variables
load_dotenv()
os.environ["SERPER_API_KEY"] = st.secrets["SERPER_API_KEY"]
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
os.environ["NOVITA_API_KEY"] = st.secrets["NOVITA_API_KEY"]

# Initialize LLM
# llm = ChatGroq(
#     groq_api_key=os.environ["GROQ_API_KEY"],
#     model_name="meta-llama/llama-4-scout-17b-16e-instruct"
# )
client = OpenAI(
    base_url="https://api.novita.ai/v3/openai",
    api_key=os.environ["NOVITA_API_KEY"],
)

# LangChain-compatible wrapper using Novita model
llm = ChatOpenAI(
    openai_api_base="https://api.novita.ai/v3/openai",
    openai_api_key=os.environ["NOVITA_API_KEY"],
    model="meta-llama/llama-4-maverick-17b-128e-instruct-fp8",
    temperature=0.7
)

# Setup search tool
search_tool = GoogleSerperAPIWrapper()
tools = [
    Tool(
        name="Google Search",
        func=search_tool.run,
        description="Use to find investors, funding agencies, or pitch submission portals"
    )
]
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    verbose=False
)

# Extract main domain of startup idea
domain_extraction_prompt = PromptTemplate(
    input_variables=["idea"],
    template="Given this startup idea: {idea}\nWhat is its main domain or industry in one word? E.g. EdTech, FinTech, HealthTech"
)
domain_chain = domain_extraction_prompt | llm

def extract_domain(startup_idea: str) -> str:
    result = domain_chain.invoke({"idea": startup_idea})
    return result.content.strip()

# Optional: Extract ideal investor persona
investor_persona_prompt = PromptTemplate(
    input_variables=["idea"],
    template="""
You are an investment analyst. Given the startup idea below, what type of investors would be ideal (e.g., Seed-stage AI-focused, HealthTech impact investors)?

Startup Idea: {idea}

Output just one short sentence describing the ideal investor type.
"""
)
investor_persona_chain = investor_persona_prompt | llm

def extract_investor_persona(startup_idea: str) -> str:
    result = investor_persona_chain.invoke({"idea": startup_idea})
    return result.content.strip()

# === Main Investor Search Function ===
def find_investors(startup_idea: str, domain: str, mode: str = "vc_firms") -> list:
    
    # if mode == "vc_firms":
    query = f"{domain} startup investors and funding opportunities 2024 / 2025"
    # elif mode == "accelerators":
    #     query = f"{domain} startup accelerator 2025 application site:techstars.com OR site:ycombinator.com"
    # elif mode == "pitch_links":
    #     query = f"submit pitch deck {domain} site:vcfirm.com OR site:crunchbase.com"
    # else:
    #     query = f"{domain} startup investor contacts"

    raw_results = search_tool.run(query)

    extract_prompt = PromptTemplate(
        input_variables=["results"],
        template="""
Extract up to 5 entities with name, short description, and relevant link from the result:

{results}

Format:
[
    {{
        "name": "...",
        "intro": "...",
        "Website-link": "...",
        "Contact":"..."
    }},
    ...
]
"""
    )
    extract_chain = extract_prompt | llm
    parsed = extract_chain.invoke({"results": raw_results})

    try:
        match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", parsed.content, re.DOTALL)
        content_to_parse = match.group(1) if match else parsed.content
        if not match:
            match = re.search(r"(\[\s*{.*?}\s*\])", parsed.content, re.DOTALL)
            if match:
                content_to_parse = match.group(1)

        investor_list = ast.literal_eval(content_to_parse)
    except Exception as e:
        print("Parsing failed:", e)
        investor_list = []
    return investor_list

# === Email Generation ===
email_prompt = PromptTemplate(
    input_variables=["idea", "investor"],
    template="""
You are a startup founder writing to an investor.

Startup Idea: {idea}
Investor Name: {investor}

Write a short and compelling cold email with:
- Warm intro line (not fake flattery)
- Clear pitch (1-2 lines)
- Call to action to connect or meet

Keep it under 6 lines.
"""
)
email_chain = email_prompt | llm

def generate_investor_email(idea: str, investor_name: str) -> str:
    return email_chain.invoke({"idea": idea, "investor": investor_name}).content.strip()
