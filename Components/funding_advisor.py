# funding_advisor.py

import os
from langchain_groq import ChatGroq
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import ast
import re
load_dotenv()


# Setup environment
os.environ["SERPER_API_KEY"] = st.secrets("SERPER_API_KEY")
os.environ["GROQ_API_KEY"] = st.secrets("GROQ_API_KEY")

# Initialize LLM
llm = ChatGroq(
    groq_api_key=os.environ["GROQ_API_KEY"],
    model_name="meta-llama/llama-4-scout-17b-16e-instruct"
)

# Setup search tool
search_tool = GoogleSerperAPIWrapper()

tools = [
    Tool(
        name="Google Search",
        func=search_tool.run,
        description="Use to find investors on LinkedIn or Crunchbase for the startup idea."
    )
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False
)

# Prompt to extract domain (industry)
domain_extraction_prompt = PromptTemplate(
    input_variables=["idea"],
    template="Given this startup idea: {idea}\nWhat is its main domain or industry in one word? E.g. EdTech, FinTech, HealthTech"
)
domain_chain = domain_extraction_prompt | llm

def extract_domain(startup_idea: str) -> str:
    """Extracts the one-word domain/industry name from the startup idea."""
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

# Main function to search investors
def find_investors(startup_idea: str, domain: str) -> list:
    # persona = extract_investor_persona(startup_idea)#{persona}
    query = f' {domain} investor site:linkedin.com/in OR site:crunchbase.com/person'

    raw_results = search_tool.run(query)
    
    # Try extracting simplified investors list from result
    investor_extract_prompt = PromptTemplate(
        input_variables=["results"],
        template="""
Extract up to 5 investor names with short intros and links from the following search result:

{results}

Format:
[
    {{
        "name": "...",
        "intro": "...",
        "link": "..."
    }},
    ...
]
"""
    )
    extract_chain = investor_extract_prompt | llm
    parsed = extract_chain.invoke({"results": raw_results})
    print(parsed)

   
    try:
        # Extract JSON-like list inside ``` block (if present)
        match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", parsed.content, re.DOTALL)
        content_to_parse = match.group(1) if match else parsed.content

        # Fallback: extract first [ ... ] block in text
        if not match:
            match = re.search(r"(\[\s*{.*?}\s*\])", parsed.content, re.DOTALL)
            if match:
                content_to_parse = match.group(1)

        investor_list = ast.literal_eval(content_to_parse)
    except Exception as e:
        print("Parsing failed:", e)
        investor_list = []
    return investor_list

# Email generation
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
