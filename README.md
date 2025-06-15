# 🚀 Startup Mate – AI-Powered Startup Assistant

This project was developed as part of the **TRAE AI Hackathon 2025** to empower aspiring entrepreneurs by giving them an end-to-end assistant for validating startup ideas, building business plans, suggesting MVPs, and finding funding opportunities — all powered by AI.

---

## 🧠 What It Does

This app helps users go from **idea to investor-ready** using powerful AI tools. The pipeline:

1. **Idea Validation (RAG-based)**  
   Scrapes market data from Google, Crunchbase, Reddit, etc., and gives a validation report with competitors and market gaps.

2. **Business Plan Generator**  
   Uses LLMs to create a mini pitch deck (problem, solution, market, monetization). Downloadable in PPT or PDF.

3. **MVP Builder**  
   Assists with defining tech stack, user stories, DB schema, and roadmap.

4. **Funding Advisor**  
   Recommends investors/accelerators using live search. Auto-drafts cold outreach emails.

---

## 🗂️ Project Structure

.
├── Components/
│ ├── business_plan.py # Logic for business plan generation
│ ├── funding_advisor.py # Investor search + email generation
│ ├── mvp_builder.py # MVP feature planner
│ └── validator.py # RAG-based idea validator
├── presentations/ # (Optional) Pitch deck outputs
├── app.py # App launcher (optional)
├── Streamlitapp.py # Main Streamlit interface
├── research.ipynb # Notebook for early data exploration/testing
├── requirements.txt # Dependencies list
├── README.md # You're reading it!
└── .env / .gitignore # Local config / exclusions


---

## ⚙️ How to Run

1. **Clone the repo**  
   ```bash
   git clone https://github.com/AhsanBilal157/Startup_Mate.git
   cd Startup_Mate

2. **Create Virtual Envronment**

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt

4. **Set up environment**
    Create a .streamlit/secrets.toml file and paste your keys:
    ```bash
    SERPER_API_KEY = "your_serper_api_key"
GROQ_API_KEY = "your_groq_api_key"
NOVITA_API_KEY = "your_novita_api_key"

4. **Run the app**
    ```bash
    streamlit run Streamlitapp.py```

---
## Tech Stack
- Streamlit – UI and user flow

- LangChain + OpenAI-compatible LLMs (Novita, Groq) – Idea reasoning & planning

- Google Serper API – Real-time search data

- Python (modular structure) – Reusable logic components

## 📌 Hackathon Project Goal
This project was created to enable non-technical founders to shape their idea into something fundable in less than 30 minutes using the power of AI and automation.

## 🤝 Contributing
If you want to improve components or add integrations, feel free to fork and submit a PR!


