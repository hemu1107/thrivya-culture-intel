# --- Thrivya | Culture Intelligence Platform ---
import streamlit as st
import json
import requests
import plotly.graph_objects as go
from pathlib import Path

# --- Configuration ---
st.set_page_config(page_title="Thrivya | Culture Intelligence", layout="centered", page_icon="🌸")

# --- Styling ---
st.markdown("""
    <style>
        .title-style {font-size: 36px; font-weight: bold; color: #d63384;}
        .section-title {font-size: 22px; font-weight: 600; margin-top: 20px;}
    </style>
""", unsafe_allow_html=True)

# --- Load Questions ---
@st.cache_data
def load_questions():
    file_path = Path("culture_questions.json")
    if not file_path.exists():
        st.error("Questions file not found.")
        st.stop()
    with open(file_path) as f:
        return json.load(f)

questions = load_questions()

# --- Mapping for simplified categories ---
pillar_map = {
    "Leadership & Vision": "Culture",
    "Inclusivity & Belonging": "Culture",
    "Recognition & Motivation": "Culture",
    "Well-being & Work-Life": "Wellness",
    "Feedback & Communication": "Wellness",
    "Learning & Growth": "Growth",
    "Team Dynamics & Trust": "Growth",
    "Autonomy & Empowerment": "Growth"
}

# --- Session State ---
if "page" not in st.session_state:
    st.session_state.page = "intro"
    st.session_state.responses = {}
    st.session_state.org_info = {}

SLIDER_LEVELS = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
LEVEL_SCORE = {lvl: i for i, lvl in enumerate(SLIDER_LEVELS)}

# --- Show Question Slider ---
def show_slider(q, idx, total):
    st.markdown(f"**{q['id']}: {q['question']}**")
    val = st.slider(f"Question {idx + 1} of {total}", 0, 4, 2, format="%s", key=q['id'])
    st.session_state.responses[q['id']] = SLIDER_LEVELS[val]
    st.markdown("---")

# --- Pages ---
if st.session_state.page == "intro":
    st.markdown("<div class='title-style'>Welcome to Thrivya 🌸</div>", unsafe_allow_html=True)
    st.subheader("Culture Intelligence for the Modern Workplace")
    st.caption("Crafted by Hemaang Patkar")
    st.markdown("""
Thrivya helps HRs understand and act on workplace culture by gathering structured inputs across:
- 🎯 Culture (Leadership, Inclusion, Recognition)
- 🧘 Wellness (Mental Health, Feedback, Workload)
- 📈 Growth (Learning, Empowerment, Teamwork)

Receive an instant AI-generated report tailored to your organization's needs.
""")
    if st.button("Start Assessment ➔"):
        st.session_state.page = "details"
        st.rerun()

elif st.session_state.page == "details":
    st.title("🏢 Organization Details")
    with st.form("org_form"):
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.org_info['name'] = st.text_input("Organization Name")
            st.session_state.org_info['industry'] = st.text_input("Industry")
            st.session_state.org_info['location'] = st.text_input("City")
        with c2:
            st.session_state.org_info['size'] = st.selectbox("Team Size", ["1-10", "11-50", "51-200", "201-500", "500+"])
            st.session_state.org_info['culture_focus'] = st.multiselect("Cultural Priorities", ["Transparency", "Flexibility", "Diversity", "Wellbeing", "Recognition"])
        st.session_state.org_info['years_active'] = st.slider("Years Active", 0, 100, 5)
        if st.form_submit_button("Next: Culture ➔"):
            st.session_state.page = "culture"
            st.rerun()

elif st.session_state.page == "culture":
    st.title("🎯 Culture Assessment")
    questions_culture = [q for q in questions if pillar_map[q['pillar']] == "Culture"]
    with st.form("culture_form"):
        for i, q in enumerate(questions_culture):
            show_slider(q, i, len(questions_culture))
        if st.form_submit_button("Next: Wellness ➔"):
            st.session_state.page = "wellness"
            st.rerun()

elif st.session_state.page == "wellness":
    st.title("🧘 Wellness Assessment")
    questions_wellness = [q for q in questions if pillar_map[q['pillar']] == "Wellness"]
    with st.form("wellness_form"):
        for i, q in enumerate(questions_wellness):
            show_slider(q, i, len(questions_wellness))
        if st.form_submit_button("Next: Growth ➔"):
            st.session_state.page = "growth"
            st.rerun()

elif st.session_state.page == "growth":
    st.title("📈 Growth Assessment")
    questions_growth = [q for q in questions if pillar_map[q['pillar']] == "Growth"]
    with st.form("growth_form"):
        for i, q in enumerate(questions_growth):
            show_slider(q, i, len(questions_growth))
        if st.form_submit_button("✔️ Generate Culture Intelligence Report"):
            st.session_state.page = "results"
            st.rerun()

elif st.session_state.page == "results":
    st.title("📊 Culture Intelligence Summary")
    responses = st.session_state.responses
    org = st.session_state.org_info

    scores = {'Culture': 0, 'Wellness': 0, 'Growth': 0}
    counts = {'Culture': 0, 'Wellness': 0, 'Growth': 0}

    for q in questions:
        resp = responses.get(q['id'])
        if not resp: continue
        p = pillar_map[q['pillar']]
        scores[p] += LEVEL_SCORE[resp]
        counts[p] += 1

    avg_scores = {p: round(scores[p] / counts[p], 2) if counts[p] else 0 for p in scores}

    fig = go.Figure(data=go.Scatterpolar(r=list(avg_scores.values()), theta=list(avg_scores.keys()), fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 4])), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    try:
        detailed_answers = "\n".join([f"- {qid}: {responses[qid]}" for qid in responses])
        prompt = f"""
You are a Culture & People Strategy Consultant with expertise in organization design. Based on the input below, generate:

1. **Pulse Summary** — Overall trends by Culture, Wellness, Growth. Identify strengths and key gaps.
2. **HR Action Plan** — Recommend practical, low-cost steps the HR can take in 30–90 days.
3. **Useful Tools** — Suggest any helpful templates or software tools aligned to current needs.

---
🏢 Org: {org.get('name')} | Industry: {org.get('industry')} | Size: {org.get('size')} | City: {org.get('location')}
Years Active: {org.get('years_active')}, Focus: {', '.join(org.get('culture_focus', []))}

📊 Scores: {avg_scores}

🧠 Responses:
{detailed_answers}
"""

        with st.spinner("Analyzing responses and preparing expert insights..."):
            cohere_api_key = st.secrets.get("cohere_api_key")
            if cohere_api_key:
                response = requests.post(
                    url="https://api.cohere.ai/v1/chat",
                    headers={
                        "Authorization": f"Bearer {cohere_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={"model": "command-r-plus", "message": prompt}
                )
                result = response.json().get("text") or "No AI response returned."
                st.subheader("📘 AI Recommendations")
                st.markdown(result)
            else:
                st.warning("Cohere API key not found in secrets.")

        st.caption("Crafted by Hemaang Patkar")

    except Exception as e:
        st.error(f"❌ Error generating recommendations: {e}")
