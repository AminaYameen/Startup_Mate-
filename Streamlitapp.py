import streamlit as st
from Components.validator import generate_ideas, extract_idea_names, research_idea_with_agent
from Components.business_plan import generate_problem_statements, generate_solution, create_pitch_deck
from Components.funding_advisor import find_investors, generate_investor_email
from Components.funding_advisor import (
        extract_domain,
        find_investors,
        generate_investor_email
    )

st.set_page_config(page_title="Startup Toolkit", page_icon="🚀")

# Sidebar Navigation
st.sidebar.title("🧭 Navigation")
main_section = st.sidebar.radio(
    "Choose a Module",
    ["🚀 Idea Creation", "📊 Pitch Deck Creation", "🛠 MVP Builder", "💰 Funding Advisor"]
)

# Session state init
for key in ["refined_text", "ideas_list", "selected_idea", "research_report", "selected_problem"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# --------------------------
# 🚀 Idea Creation Module
# --------------------------
if main_section == "🚀 Idea Creation":
    st.title("🚀 Idea Creation")

    idea_input = st.text_area("💡 Enter your rough startup idea:")

    if idea_input:
        if st.button("✨ Generate Refined Startup Ideas"):
            with st.spinner("Generating..."):
                refined = generate_ideas(idea_input)
                st.session_state.refined_text = refined
                st.markdown(refined)
                st.session_state.ideas_list = extract_idea_names(refined)

    if st.session_state.ideas_list:
        st.session_state.selected_idea = st.radio(
            "📌 Select an idea to validate:",
            st.session_state.ideas_list,
            key="selected_idea_radio"
        )

        if st.button("🔍 Run Market Research"):
            with st.spinner("Researching..."):
                report = research_idea_with_agent(st.session_state.selected_idea)
                st.session_state.research_report = report
                st.markdown(report)

# --------------------------
# 📊 Pitch Deck Creation
# --------------------------
elif main_section == "📊 Pitch Deck Creation":
    st.title("📊 Pitch Deck Creation")

    if st.session_state.research_report:
        st.markdown("Based on market research, here are suggested problem statements:")

        # Generate problem statements once and save to session (avoid regenerating every rerun)
        if "problem_options" not in st.session_state:
            st.session_state.problem_options = generate_problem_statements(st.session_state.research_report)

        # Display radio with saved key
        st.radio(
            "🎯 Select a problem statement:",
            st.session_state.problem_options,
            key="pitch_problem"  # stored here automatically
        )

        # Use selected radio value and show it
        selected_problem = st.session_state.pitch_problem
        st.success(f"Selected Problem: {selected_problem}")

        # Save the selected problem if needed
        st.session_state.selected_problem = selected_problem

        # Button to create PPT
        if st.button("🎯 Create PPT"):
            with st.spinner("Generating solution and pitch deck..."):
                solution = generate_solution(selected_problem)
                ppt_path = create_pitch_deck(
                    startup_name=st.session_state.selected_idea or "My Startup",
                    problem=selected_problem,
                    solution=solution,
                    report=st.session_state.research_report,
                    # unique_angle="We'll use AI + community + virtual events to dominate this space."
                )
                with open(ppt_path, "rb") as f:
                    st.download_button("📥 Download Pitch Deck", f, file_name="pitch_deck.pptx")
    else:
        st.warning("Please complete the 'Idea Creation' module first.")




# --------------------------
# 🛠 MVP Builder
# --------------------------
elif main_section == "🛠 MVP Builder":
    st.title("🛠 MVP Builder")
    if st.session_state.selected_problem and st.session_state.research_report:
        if st.button("⚙️ Generate MVP Plan"):
            with st.spinner("Generating MVP Plan..."):
                from Components.mvp_builder import generate_mvp_plan
                mvp_report = generate_mvp_plan(
                    startup_name=st.session_state.selected_idea or "My Startup",
                    problem=st.session_state.selected_problem,
                    solution=generate_solution(st.session_state.selected_problem),
                    report=st.session_state.research_report
                )
                st.session_state.mvp_report = mvp_report
                st.markdown(mvp_report)

        # if st.session_state.get("mvp_report"):
        #     st.markdown(st.session_state.mvp_report)

    else:
        st.warning("Please complete the Pitch Deck step first.")

# --------------------------
# 💰 Funding Advisor
# --------------------------

elif main_section == "💰 Funding Advisor":
    st.title("💰 Funding Advisor")

    # Get or extract startup idea
    startup_idea = st.session_state.get("startup_idea", st.session_state.research_report)
    domain = st.session_state.get("startup_domain", "")

    if not startup_idea:
        st.warning("Please generate your startup idea first using the Idea Generator or MVP Builder.")
    else:
        if not domain:
            with st.spinner("Extracting domain..."):
                domain = extract_domain(startup_idea)
                st.session_state["startup_domain"] = domain

        st.markdown("### Domain")
        st.code(domain)


        if st.button("🔍 Find Investors / Funding Sources"):
            with st.spinner(f"Searching using Google..."):
                investors = find_investors(startup_idea, domain)
                st.session_state["funding_investors"] = investors

        if "funding_investors" in st.session_state:
            investors = st.session_state["funding_investors"]
            if investors:
                st.markdown("### 🔗 Suggested Contacts / Sources")
                for investor in investors:
                    st.markdown(f"**{investor['name']}**")
                    st.write(investor['intro'])
                    st.markdown(f"[🔗 Profile]({investor['Website-link']})")

                if st.button("✉️ Generate Cold Emails"):
                    for investor in investors:
                        email = generate_investor_email(startup_idea, investor["name"])
                        st.markdown(f"#### Email to {investor['name']}")
                        st.code(email)
            else:
                st.info("No investors were found or parsing failed.")
