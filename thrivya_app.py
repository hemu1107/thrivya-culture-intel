import streamlit as st
import json
import requests
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta
import uuid
import pandas as pd

# --- Configuration ---
st.set_page_config(
    page_title="Thrivya | Culture Intelligence Platform",
    layout="wide",
    page_icon="🌸",
    initial_sidebar_state="collapsed"
)

# --- Enhanced Styling ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f8f9fa; }
        .main-container { max-width: 1200px; margin: 0 auto; padding: 1rem; }
        .main-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2.5rem 1.5rem; border-radius: 15px; margin-bottom: 2rem; text-align: center; color: white; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
        .main-title { font-size: 2.5rem; font-weight: 700; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .main-subtitle { font-size: 1.2rem; font-weight: 400; margin-top: 0.75rem; opacity: 0.9; }
        .pillar-card { background: white; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-left: 4px solid; transition: transform 0.3s ease; }
        .pillar-card:hover { transform: translateY(-3px); box-shadow: 0 6px 25px rgba(0,0,0,0.12); }
        .culture-card { border-left-color: #ff6b6b; } .wellness-card { border-left-color: #4ecdc4; } .growth-card { border-left-color: #45b7d1; }
        .metric-card { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 10px; padding: 1.5rem; text-align: center; margin: 1rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .score-excellent { color: #27ae60; font-weight: 600; } .score-good { color: #f39c12; font-weight: 600; } .score-needs-improvement { color: #e74c3c; font-weight: 600; }
        .recommendation-box { background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%); border-radius: 10px; padding: 1.5rem; margin: 1.5rem 0; border-left: 4px solid #e17055; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .progress-indicator { background: linear-gradient(90deg, #00d2ff 0%, #3a47d5 100%); height: 6px; border-radius: 3px; margin: 1.5rem 0; }
        .question-card { background: white; border-radius: 10px; padding: 1.5rem; margin: 1.5rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border: 1px solid #e1e8ed; }
        .brand-footer { text-align: center; margin-top: 3rem; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; }
        .stButton > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; padding: 0.75rem 2rem; font-weight: 600; transition: all 0.3s ease; }
        .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        .intro-features { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin: 2rem 0; }
        .feature-item { background: white; padding: 2rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08); transition: transform 0.3s ease; }
        .feature-item:hover { transform: translateY(-3px); }
        .feature-icon { font-size: 2.5rem; margin-bottom: 1rem; }
        @media (max-width: 768px) { .main-title { font-size: 2rem; } .main-subtitle { font-size: 1rem; } .intro-features { grid-template-columns: 1fr; } .metric-card, .pillar-card { margin: 0.75rem 0; } }
    </style>
""", unsafe_allow_html=True)

# --- Load Questions ---
@st.cache_data
def load_questions():
    file_path = Path("culture_questions.json")
    if not file_path.exists():
        st.error("❌ Questions file not found. Please ensure culture_questions.json exists.")
        st.stop()
    try:
        with open(file_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        st.error("❌ Invalid JSON format in questions file.")
        st.stop()

questions = load_questions()

# --- Constants ---
pillar_map = {
    "Leadership & Vision": "Culture", "Inclusivity & Belonging": "Culture", "Recognition & Motivation": "Culture",
    "Well-being & Work-Life": "Wellness", "Feedback & Communication": "Wellness",
    "Learning & Growth": "Growth", "Team Dynamics & Trust": "Growth", "Autonomy & Empowerment": "Growth"
}
pillar_colors = {"Culture": "#ff6b6b", "Wellness": "#4ecdc4", "Growth": "#45b7d1"}
SLIDER_LEVELS = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
LEVEL_SCORE = {lvl: i for i, lvl in enumerate(SLIDER_LEVELS)}

# --- Session State Initialization ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "intro",
        "responses": {},
        "org_info": {
            'name': '', 'industry': '', 'location': '', 'size': '', 'years_active': 5,
            'remote_work': '', 'culture_focus': [], 'current_challenges': []
        },
        "assessment_start_time": None,
        "report_generated": False
    })

# --- Utility Functions ---
def get_score_interpretation(score):
    if score >= 3.5: return "Excellent", "score-excellent", "🌟"
    elif score >= 2.5: return "Good", "score-good", "👍"
    return "Needs Improvement", "score-needs-improvement", "⚠️"

def calculate_completion_percentage():
    total = len(questions)
    answered = len([q['id'] for q in questions if q['id'] in st.session_state.responses])
    return min(int((answered / total) * 100), 100)

def show_progress_bar():
    progress = calculate_completion_percentage()
    st.markdown(f"""
    <div style="margin: 1.5rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
            <span style="font-weight: 600; color: #2c3e50;">Progress</span>
            <span style="font-weight: 600; color: #667eea;">{progress}%</span>
        </div>
        <div style="background: #ecf0f1; border-radius: 10px; height: 10px;">
            <div style="width: {progress}%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; transition: width 0.5s;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_enhanced_slider(q, idx, total, category):
    category_color = pillar_colors[category]
    st.markdown(f"""
    <div class="question-card">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="background: {category_color}; color: white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-weight: 600; margin-right: 1rem;">
                {idx + 1}
            </div>
            <div style="flex: 1;">
                <div style="font-size: 0.9rem; color: #7f8c8d;">Q{idx + 1} of {total}</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #2c3e50;">{q['question']}</div>
            </div>
        </div>
        <div style="text-align: center; padding: 0.75rem; background: #ecf0f1; color: #2c3e50; border-radius: 8px;">
            Scale: Strongly Disagree to Strongly Agree
        </div>
    </div>
    """, unsafe_allow_html=True)
    return st.slider(f"Q{idx + 1}", 0, 4, 2, format="", key=f"slider_{q['id']}_{uuid.uuid4()}", label_visibility="collapsed")

def export_report(scores, responses, org):
    data = {
        "Organization": org,
        "Scores": scores,
        "Responses": {q['id']: resp for q, resp in zip(questions, [responses.get(q['id'], 'N/A') for q in questions])},
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.download_button("📥 Export Report", data=json.dumps(data), file_name="thrivya_report.json", mime="application/json")

# --- Page Functions ---
def render_intro():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="main-header"><h1 class="main-title">Welcome to Thrivya 🌸</h1><p class="main-subtitle">Culture Intelligence Platform</p></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="intro-features">
        <div class="feature-item culture-card"><div class="feature-icon">🎯</div><h3>Culture Analysis</h3><p>Leadership, inclusion, recognition insights</p></div>
        <div class="feature-item wellness-card"><div class="feature-icon">🧘</div><h3>Wellness Metrics</h3><p>Mental health, work-life balance</p></div>
        <div class="feature-item growth-card"><div class="feature-icon">📈</div><h3>Growth Tracking</h3><p>Learning, team dynamics</p></div>
    </div>
    <div class="pillar-card"><h3 style="color: #2c3e50;">🚀 Why Thrivya?</h3><div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem;">
        <div><strong>🔄 Continuous:</strong> Track progress</div><div><strong>📊 Data-Driven:</strong> Actionable metrics</div><div><strong>🎯 HR-Focused:</strong> Practical tools</div>
    </div></div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Start Assessment", use_container_width=True):
        st.session_state.page = "details"
        st.session_state.assessment_start_time = datetime.now()
        st.rerun()
    st.markdown('<div class="brand-footer"><p style="margin: 0;">Crafted by Hemaang Patkar</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_details():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="main-header"><h1 class="main-title">🏢 Organization Profile</h1><p class="main-subtitle">Provide your details</p></div>', unsafe_allow_html=True)
    show_progress_bar()
    with st.form("org_form"):
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            st.session_state.org_info['name'] = st.text_input("🏢 Name", st.session_state.org_info['name'], placeholder="e.g., TechCorp")
            st.session_state.org_info['industry'] = st.selectbox("🏭 Industry", ["Technology", "Healthcare", "Finance", "Other"], index=0)
            st.session_state.org_info['location'] = st.text_input("📍 Location", st.session_state.org_info['location'], placeholder="e.g., Mumbai")
        with col2:
            st.session_state.org_info['size'] = st.selectbox("👥 Size", ["1-50", "51-200", "201-1000", "1000+"], index=0)
            st.session_state.org_info['years_active'] = st.slider("📅 Years Active", 0, 100, st.session_state.org_info['years_active'])
            st.session_state.org_info['remote_work'] = st.selectbox("🏠 Work Model", ["Remote", "Hybrid", "In-Office"], index=0)
        st.session_state.org_info['culture_focus'] = st.multiselect("🎯 Priorities", ["Transparency", "Wellbeing", "Inclusion"], default=st.session_state.org_info['culture_focus'])
        st.session_state.org_info['current_challenges'] = st.multiselect("⚠️ Challenges", ["Turnover", "Engagement", "Burnout"], default=st.session_state.org_info['current_challenges'])
        col1, col2 = st.columns(2)
        if col1.form_submit_button("← Back"): st.session_state.page = "intro"; st.rerun()
        if col2.form_submit_button("Next →"): 
            if st.session_state.org_info['name'] and st.session_state.org_info['industry']:
                st.session_state.page = "culture"; st.rerun()
            else: st.error("Please fill Name and Industry.")
    st.markdown('</div>', unsafe_allow_html=True)

def render_assessment(category, next_page):
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="main-header"><h1 class="main-title">{{"Culture": "🎯 Culture", "Wellness": "🧘 Wellness", "Growth": "📈 Growth"}[category]} Assessment</h1><p class="main-subtitle">Evaluate {category}</p></div>', unsafe_allow_html=True)
    show_progress_bar()
    questions_category = [q for q in questions if pillar_map[q['pillar']] == category]
    with st.form(f"{category}_form"):
        responses = {}
        for i, q in enumerate(questions_category):
            responses[q['id']] = show_enhanced_slider(q, i, len(questions_category), category)
        st.session_state.responses.update(responses)
        if not all(q['id'] in st.session_state.responses for q in questions_category):
            st.warning("⚠️ Please answer all questions before proceeding.")
        col1, col2 = st.columns(2)
        if col1.form_submit_button("← Back"): 
            st.session_state.page = {"culture": "details", "wellness": "culture", "growth": "wellness"}[category]; st.rerun()
        if col2.form_submit_button(f"Next: {next_page} →") and all(q['id'] in st.session_state.responses for q in questions_category):
            st.session_state.page = next_page; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def render_results():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="main-header"><h1 class="main-title">📊 Culture Intelligence Report</h1><p class="main-subtitle">Your analysis</p></div>', unsafe_allow_html=True)
    responses = st.session_state.responses
    org = st.session_state.org_info

    # Score Calculation
    scores = {'Culture': 0, 'Wellness': 0, 'Growth': 0}
    counts = {'Culture': 0, 'Wellness': 0, 'Growth': 0}
    detailed_scores = {}
    for q in questions:
        resp = responses.get(q['id'])
        if resp:
            pillar = q['pillar']
            category = pillar_map[pillar]
            score = LEVEL_SCORE[resp]
            scores[category] += score
            counts[category] += 1
            detailed_scores.setdefault(pillar, []).append(score)
    avg_scores = {p: round(scores[p] / counts[p], 2) if counts[p] else 0 for p in scores}
    overall_score = round(sum(avg_scores.values()) / 3, 2) if counts['Culture'] + counts['Wellness'] + counts['Growth'] else 0

    # Executive Summary
    st.markdown("### 🎯 Executive Summary")
    cols = st.columns(4, gap="medium")
    with cols[0]:
        status, _, icon = get_score_interpretation(overall_score)
        st.markdown(f'<div class="metric-card"><div style="font-size: 2.5rem;">{icon}</div><div style="font-size: 1.5rem; font-weight: 700;">{overall_score}/4.0</div><div style="font-size: 0.9rem; color: #7f8c8d;">Overall</div></div>', unsafe_allow_html=True)
    for i, (cat, score) in enumerate(avg_scores.items()):
        with cols[i + 1]:
            status, _, icon = get_score_interpretation(score)
            st.markdown(f'<div class="metric-card {cat.lower()}-card"><div style="font-size: 2.5rem;">{icon}</div><div style="font-size: 1.5rem; font-weight: 700; color: {pillar_colors[cat]};">{score}/4.0</div><div style="font-size: 0.9rem; color: #7f8c8d;">{cat}</div></div>', unsafe_allow_html=True)

    # Charts
    st.markdown("### 📊 Visual Insights")
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=list(avg_scores.values()), theta=list(avg_scores.keys()), fill='toself', name='Your Org', fillcolor='rgba(102,126,234,0.3)', line=dict(color='rgba(102,126,234,1)')))
    fig_radar.add_trace(go.Scatterpolar(r=[3.2, 2.8, 3.0], theta=list(avg_scores.keys()), fill='toself', name='Benchmark', fillcolor='rgba(255,107,107,0.2)', line=dict(color='rgba(255,107,107,1)', dash='dash')))
    fig_radar.update_layout(polar=dict(radialaxis=dict(range=[0, 4], tickvals=[0, 1, 2, 3, 4])), showlegend=True, height=500)
    st.plotly_chart(fig_radar, use_container_width=True)

    response_counts = pd.Series(responses).value_counts().reindex(SLIDER_LEVELS, fill_value=0)
    fig_dist = px.bar(x=response_counts.index, y=response_counts.values, title="Response Distribution", color=response_counts.values, color_continuous_scale="RdYlGn")
    fig_dist.update_layout(height=400)
    st.plotly_chart(fig_dist, use_container_width=True)

    # Detailed Analysis
    st.markdown("### 🔍 Detailed Breakdown")
    cols = st.columns(3, gap="medium")
    for i, (cat, pillars) in enumerate([("Culture", [p for p in detailed_scores if pillar_map[p] == "Culture"]), ("Wellness", [p for p in detailed_scores if pillar_map[p] == "Wellness"]), ("Growth", [p for p in detailed_scores if pillar_map[p] == "Growth"])]):
        with cols[i]:
            st.markdown(f"#### {{\"Culture\": \"🎯\", \"Wellness\": \"🧘\", \"Growth\": \"📈\"}[cat]} {cat}")
            for pillar in pillars:
                avg = round(np.mean(detailed_scores[pillar]), 2)
                status, _, _ = get_score_interpretation(avg)
                st.markdown(f'<div class="pillar-card {cat.lower()}-card"><div style="display: flex; justify-content: space-between;"><div><div style="font-weight: 600;">{pillar}</div><div style="font-size: 0.9rem; color: #7f8c8d;">{status}</div></div><div style="font-size: 1.5rem; font-weight: 700; color: {pillar_colors[cat]};">{avg}</div></div></div>', unsafe_allow_html=True)

    # Recommendations
    st.markdown("### 🤖 AI Recommendations")
    if st.button("Generate Report") and not st.session_state.report_generated:
        try:
            detailed_answers = [f"• {q['pillar']} - {q['question']}: {responses.get(q['id'], 'N/A')} ({LEVEL_SCORE.get(responses.get(q['id'], 'Neutral'))}/4)" for q in questions]
            prompt = f"""
You are a Culture Consultant with 15+ years of experience.

## ORGANIZATION: {org['name']} | {org['industry']} | {org['size']} | {org['location']}
## YEARS: {org['years_active']} | MODEL: {org['remote_work']}
## PRIORITIES: {', '.join(org['culture_focus'])}
## CHALLENGES: {', '.join(org['current_challenges'])}
## SCORES: Overall {overall_score}/4, Culture {avg_scores['Culture']}/4, Wellness {avg_scores['Wellness']}/4, Growth {avg_scores['Growth']}/4
## RESPONSES: {'\n'.join(detailed_answers)}

Provide:
1. 🎯 Executive Summary (150 words) with strengths and areas for improvement.
2. 🚀 Action Plan: 3 immediate (0-30 days), 3 short-term (30-90 days), 2 long-term (90-365 days) steps.
3. 🛠️ Tools: Suggest 3 HR tools for challenges.
4. 📈 KPIs: 3 measurable metrics per pillar.
"""
            with st.spinner("🔄 Generating..."):
                if st.secrets.get("cohere_api_key"):
                    response = requests.post("https://api.cohere.ai/v1/chat", headers={"Authorization": f"Bearer {st.secrets['cohere_api_key']}", "Content-Type": "application/json"}, json={"model": "command-r-plus", "message": prompt, "temperature": 0.7, "max_tokens": 2000}, timeout=180)
                    if response.status_code == 200:
                        result = response.json().get("text", "No response.")
                        st.session_state.report_generated = True
                        st.markdown(f'<div class="recommendation-box"><h3>🤖 Report</h3><p style="margin-bottom: 0; color: #7f8c8d;">Generated: {datetime.now().strftime("%B %d, %Y %I:%M %p IST")}</p></div>', unsafe_allow_html=True)
                        st.markdown(result)
                    else: st.error(f"❌ API Error: {response.status_code} - {response.text}")
                else: st.warning("⚠️ Configure Cohere API key.")
        except Exception as e: st.error(f"❌ Error: {str(e)}")
    elif st.session_state.report_generated:
        st.info("Report already generated. Refresh to start over.")

    # Summary Table
    st.markdown("### 📋 Response Summary")
    summary_data = {q['pillar']: responses.get(q['id'], 'N/A') for q in questions}
    df_summary = pd.DataFrame(list(summary_data.items()), columns=["Pillar", "Response"])
    st.table(df_summary)

    # Export
    export_report(avg_scores, responses, org)

    # Assessment Summary
    time_taken = datetime.now() - st.session_state.assessment_start_time if st.session_state.assessment_start_time else timedelta(minutes=10)
    st.markdown(f'<div class="pillar-card"><h4>📊 Assessment Stats</h4><div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;"><div><strong>Questions:</strong> {len(questions)}</div><div><strong>Responses:</strong> {len(responses)}</div><div><strong>Time:</strong> {int(time_taken.total_seconds() / 60)}m</div><div><strong>Completion:</strong> {calculate_completion_percentage()}%</div></div></div>', unsafe_allow_html=True)

    st.markdown('<div class="brand-footer"><p>Thrivya by Hemaang Patkar</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Main App Logic ---
pages = {
    "intro": render_intro,
    "details": render_details,
    "culture": lambda: render_assessment("Culture", "wellness"),
    "wellness": lambda: render_assessment("Wellness", "growth"),
    "growth": lambda: render_assessment("Growth", "results"),
    "results": render_results
}
pages[st.session_state.page]()
