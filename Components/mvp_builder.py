from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import os
from openai import OpenAI
from langchain.chat_models import ChatOpenAI

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

mvp_prompt = PromptTemplate(
    input_variables=["startup_name", "problem", "solution","report"],
    template="""
You are a technical cofounder. Based on the following startup idea, generate a complete MVP plan.

Startup Name: {startup_name}
Problem: {problem}
Solution: {solution}
Report: {report}

Return the plan in the following format in markdown:
### ✅ MVP Feature Plan
- List 4-5 key features in V1

### 🛠 Tech Stack
- Frontend:
- Backend:
- Database:
- ML/AI (if needed):
- APIs/3rd party services:

### 📆 Timeline (8-12 weeks)
| Week | Task |
|------|------|
| 1-2  | ...  |
| 3-4  | ...  |
...

### 👥 Team / Resources Needed
- Roles required with brief responsibility

### 🧱 Architecture Diagram (Text-based)
- Describe system components and how they interact
"""
)

mvp_chain = mvp_prompt | llm

def generate_mvp_plan(startup_name: str, problem: str, solution: str, report: str) -> str:
    return mvp_chain.invoke({
        "startup_name": startup_name,
        "problem": problem,
        "solution": solution,
        "report": report
    }).content.strip()
