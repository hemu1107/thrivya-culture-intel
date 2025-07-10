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

# --- Load Culture Questions JSON ---
@st.cache_data
def load_questions():
    file_path = Path("culture_questions.json")
    if not file_path.exists():
        st.error("Questions file not found.")
        st.stop()
    with open(file_path) as f:
        return json.load(f)

questions = load_questions()

# --- Pillar Mapping ---
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
if 'page' not in st.session_state:
    st.session_state.page = 'intro'
    st.session_state.responses = {}
    st.session_state.org_info = {}

SLIDER_LEVELS = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
LEVEL_SCORE = {lvl: i for i, lvl in enumerate(SLIDER_LEVELS)}

# --- Display Slider ---
def show_slider(q, idx, total):
    st.markdown(f"**{q['id']}: {q['question']}**")
    value = st.slider(f"Question {idx + 1} of {total}", 0, 4, 2, format="%d", key=q['id'])
    st.session_state.responses[q['id']] = SLIDER_LEVELS[value]
    st.markdown("---")

# --- Sidebar Navigation ---
if st.session_state.page != 'intro':
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        st.button("🏠 Intro", on_click=lambda: st.session_state.update({'page': 'intro'}))
        st.button("🏢 Org Details", on_click=lambda: st.session_state.update({'page': 'details'}))
        st.button("🎯 Culture", on_click=lambda: st.session_state.update({'page': 'culture'}))
        st.button("🧘 Wellness", on_click=lambda: st.session_state.update({'page': 'wellness'}))
        st.button("📈 Growth", on_click=lambda: st.session_state.update({'page': 'growth'}))
        st.button("✅ Submit", on_click=lambda: st.session_state.update({'page': 'results'}))

# --- Page Logic ---
if st.session_state.page == 'intro':
    st.markdown("<div class='title-style'>Welcome to Thrivya 🌸</div>", unsafe_allow_html=True)
    st.subheader("Culture Intelligence for the Modern Workplace")
    st.caption("Crafted by Hemaang Patkar")
    st.markdown("""
Thrivya enables HR leaders to assess and visualize employee sentiments across core workplace pillars:

- 🎯 Culture (Trust, Inclusivity, Leadership)
- 🧘 Wellness (Mental Health, Workload, Safety)
- 📈 Growth (Recognition, Upskilling, Autonomy)

💡 Gain instant recommendations from AI on improving your internal culture metrics.
""")
    if st.button("Start Assessment ➔"):
        st.session_state.page = 'details'
        st.rerun()

elif st.session_state.page == 'details':
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
            st.session_state.page = 'culture'
            st.rerun()

elif st.session_state.page == 'culture':
    st.header("🎯 Culture Assessment")
    culture_qs = [q for q in questions if pillar_map[q['pillar']] == 'Culture']
    with st.form("culture_form"):
        for i, q in enumerate(culture_qs):
            show_slider(q, i, len(culture_qs))
        st.form_submit_button("Save & Continue")

elif st.session_state.page == 'wellness':
    st.header("🧘 Wellness Assessment")
    wellness_qs = [q for q in questions if pillar_map[q['pillar']] == 'Wellness']
    with st.form("wellness_form"):
        for i, q in enumerate(wellness_qs):
            show_slider(q, i, len(wellness_qs))
        st.form_submit_button("Save & Continue")

elif st.session_state.page == 'growth':
    st.header("📈 Growth Assessment")
    growth_qs = [q for q in questions if pillar_map[q['pillar']] == 'Growth']
    with st.form("growth_form"):
        for i, q in enumerate(growth_qs):
            show_slider(q, i, len(growth_qs))
        st.form_submit_button("Save & Continue")

elif st.session_state.page == 'results':
    st.title("📊 Culture Intelligence Summary")
    responses = st.session_state.responses
    org = st.session_state.org_info

    # --- Scoring ---
    scores = {'Culture': 0, 'Wellness': 0, 'Growth': 0}
    counts = {'Culture': 0, 'Wellness': 0, 'Growth': 0}
    for q in questions:
        pillar = pillar_map[q['pillar']]
        val = LEVEL_SCORE[responses[q['id']]]
        scores[pillar] += val
        counts[pillar] += 1
    avg_scores = {k: round(v / counts[k], 2) if counts[k] else 0 for k, v in scores.items()}

    fig = go.Figure(data=go.Scatterpolar(r=list(avg_scores.values()), theta=list(avg_scores.keys()), fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 4])), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    try:
        detailed_answers = "\n".join([f"- {qid}: {responses[qid]}" for qid in responses])
        prompt = f"""
You are a professional Culture and HR Consultant with a focus on people analytics. Based on the inputs below from a Culture Intelligence tool (Thrivya), provide a clear, confident and structured 3-part output:

1. **Pulse Summary** – What are the overall observations? Where are strengths and weaknesses by pillar?
2. **HR Recommendations** – For each of the 3 pillars (Culture, Wellness, Growth), give specific, low-cost, practical actions HR can implement in the next 90 days.
3. **Tools & Templates** – Suggest relevant HR templates, software, or frameworks (like DEI dashboards, wellbeing pulse surveys, growth trackers).

Be sharp, clear and realistic. Avoid generalities. Avoid repeating input. Work only from data below:

🏢 Organization: {org.get('name')}, Industry: {org.get('industry')}, Size: {org.get('size')}, City: {org.get('location')}, Years Active: {org.get('years_active')}
🎯 Cultural Priorities: {', '.join(org.get('culture_focus', [])) or 'None'}

📊 Scores: {avg_scores}

🧠 Responses:
{detailed_answers}
"""

        with st.spinner("Analyzing culture data and preparing expert insights..."):
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
                output = response.json()
                result = output.get("text") or output.get("response") or "No AI response returned."
                st.subheader("📘 AI Recommendations")
                st.markdown(result)
            else:
                st.warning("Cohere API key not found in secrets.")

        st.caption("Crafted by Hemaang Patkar")

    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
