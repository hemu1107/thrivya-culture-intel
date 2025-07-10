# --- Thrivya | Culture Intelligence Tool for HRs ---
# MVP Version with Score Threshold Logic, AI Recommendations, and Benchmarks

import streamlit as st
import json
import requests
import plotly.graph_objects as go
from pathlib import Path

# --- App Configuration ---
st.set_page_config(page_title="Thrivya | Culture Intelligence", layout="centered", page_icon="💼")

# --- Styling ---
st.markdown("""
    <style>
        .title-style {font-size: 32px; font-weight: bold; color: #4B0082;}
        .section-title {font-size: 20px; font-weight: 600; margin-top: 20px;}
        .note {font-size: 13px; color: gray; font-style: italic;}
    </style>
""", unsafe_allow_html=True)

# --- Load Questions ---
@st.cache_data
def load_questions():
    with open("culture_questions.json") as f:
        return json.load(f)

questions = load_questions()

# --- Categorize Questions by Pillar ---
def categorize(questions):
    data = {}
    for q in questions:
        data.setdefault(q["pillar"], []).append(q)
    return data

pillars = categorize(questions)

# --- Session State Init ---
if "page" not in st.session_state:
    st.session_state.page = "intro"
    st.session_state.responses = []
    st.session_state.submissions = []

# --- Helper: Score Calculation ---
def calculate_scores(submissions):
    total = 0
    pillar_scores = {p: 0 for p in pillars}
    pillar_counts = {p: 0 for p in pillars}

    for submission in submissions:
        for i, q in enumerate(questions):
            score = submission[i]
            p = q["pillar"]
            pillar_scores[p] += score
            pillar_counts[p] += 1
            total += score

    total_possible = len(questions) * 4 * len(submissions)  # 4 = max score
    score_pct = round((total / total_possible) * 100)
    avg_scores = {p: round((pillar_scores[p] / pillar_counts[p]), 2) for p in pillars}
    return score_pct, avg_scores

# --- Helper: AI Prompt ---
def generate_prompt(score, avg_scores):
    return f"""
You are a leading People & Culture Consultant helping HRs make data-driven decisions.
Based on this anonymous culture pulse survey, generate a crisp report in markdown with:

### 1. Summary
- Overall Thrivya Score: {score}/100
- Pillar-wise Scores: {json.dumps(avg_scores)}
- Include a sentence comparing to global benchmarks (e.g., ideal avg score > 3.5)

### 2. Quick Diagnosis
- Which pillars need focus? (Below 3.0?)
- Which are strengths? (>3.5?)

### 3. Recommendations
- 3 bullet points per weak pillar
- Use action verbs: "Launch", "Introduce", "Facilitate"
- Keep advice tactical, no fluff

### 4. Retest Reminder
- Close with: “Run this survey again in 90 days to track improvement.”

Tone: Clear, HR-friendly, instructional.
"""

# --- Pages ---
if st.session_state.page == "intro":
    st.markdown("<div class='title-style'>Welcome to Thrivya 💼</div>", unsafe_allow_html=True)
    st.subheader("Your Culture Intelligence Snapshot")
    st.markdown("""
    Thrivya helps HRs and Team Leads uncover how employees *truly* feel.

    ✅ 15 Questions  •  🎯 5 Culture Pillars  •  💡 AI Recommendations

    **Use Cases:**
    - Onboarding Culture Check
    - Quarterly Team Pulse
    - Pre/Post HR Initiatives

    *Results are anonymized and aggregated.*

    Crafted by Hemaang Patkar
    """)
    if st.button("Start Team Submission ➔"):
        st.session_state.page = "survey"
        st.rerun()

elif st.session_state.page == "survey":
    st.title("📝 Employee Culture Survey")
    st.markdown("""
    Please respond honestly. Your answers are anonymous and will help improve the team culture.
    """)
    responses = []
    with st.form("response_form"):
        for i, q in enumerate(questions):
            score = st.radio(f"{q['id']}: {q['question']}",
                             ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                             index=2, key=f"q{i}")
            responses.append([0,1,2,3,4][["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"].index(score)])
        submitted = st.form_submit_button("Submit Response")
        if submitted:
            st.session_state.submissions.append(responses)
            st.success("Thank you! Your response has been recorded.")
            st.balloons()
            st.session_state.page = "intro"
            st.rerun()

elif len(st.session_state.submissions) >= 5:
    st.title("📊 Team Culture Insights")
    score_pct, avg_scores = calculate_scores(st.session_state.submissions)

    st.metric("Thrivya Score", f"{score_pct}/100")

    st.markdown("""
    **Benchmarks:**
    - ✅ >75: Strong Culture
    - ⚠️ 50–74: Growth Zone
    - ❗ <50: Culture Risk
    """)

    # Spider chart
    fig = go.Figure(data=go.Scatterpolar(
        r=list(avg_scores.values()),
        theta=list(avg_scores.keys()),
        fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # AI Insight
    prompt = generate_prompt(score_pct, avg_scores)
    with st.spinner("Analyzing with Thrivya Intelligence..."):
        cohere_key = st.secrets.get("cohere_api_key")
        response = requests.post(
            url="https://api.cohere.ai/v1/chat",
            headers={
                "Authorization": f"Bearer {cohere_key}",
                "Content-Type": "application/json"
            },
            json={"model": "command-r-plus", "message": prompt}
        )
        result = response.json()
        insight = result.get("text") or result.get("response") or "No AI insight generated."
    st.subheader("💡 Recommendations")
    st.markdown(insight)

else:
    st.warning("Waiting for at least 5 responses to generate insights.")
    st.info(f"Current Responses: {len(st.session_state.submissions)}")
