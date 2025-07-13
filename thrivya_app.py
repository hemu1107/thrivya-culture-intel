import streamlit as st
import json
import requests
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import uuid

# --- Configuration ---
st.set_page_config(
    page_title="Thrivya | Culture Intelligence",
    layout="wide",
    page_icon="🌸",
    initial_sidebar_state="collapsed"
)

# --- Enhanced Styling ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global Styles */
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f8f9fa;
        }

        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
        }

        /* Header Styles */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2.5rem 1.5rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            color: white;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }

        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .main-subtitle {
            font-size: 1.2rem;
            font-weight: 400;
            margin-top: 0.75rem;
            opacity: 0.9;
        }

        /* Card Styles */
        .pillar-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border-left: 4px solid;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .pillar-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 25px rgba(0,0,0,0.12);
        }

        .culture-card { border-left-color: #ff6b6b; }
        .wellness-card { border-left-color: #4ecdc4; }
        .growth-card { border-left-color: #45b7d1; }

        .metric-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 10px;
            padding: 1.5rem;
            text-align: center;
            margin: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }

        .score-excellent { color: #27ae60; font-weight: 600; }
        .score-good { color: #f39c12; font-weight: 600; }
        .score-needs-improvement { color: #e74c3c; font-weight: 600; }

        .recommendation-box {
            background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-left: 4px solid #e17055;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .progress-indicator {
            background: linear-gradient(90deg, #00d2ff 0%, #3a47d5 100%);
            height: 6px;
            border-radius: 3px;
            margin: 1.5rem 0;
        }

        .question-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border: 1px solid #e1e8ed;
        }

        .brand-footer {
            text-align: center;
            margin-top: 3rem;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            color: white;
        }

        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        .intro-features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }

        .feature-item {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }

        .feature-item:hover {
            transform: translateY(-3px);
        }

        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }

        /* Responsive Adjustments */
        @media (max-width: 768px) {
            .main-title { font-size: 2rem; }
            .main-subtitle { font-size: 1rem; }
            .intro-features { grid-template-columns: 1fr; }
            .metric-card { margin: 0.75rem 0; }
            .pillar-card { margin: 0.75rem 0; }
        }
    </style>
""", unsafe_allow_html=True)

# --- Load Questions ---
@st.cache_data
def load_questions():
    file_path = Path("culture_questions.json")
    if not file_path.exists():
        st.error("❌ Questions file not found. Please ensure culture_questions.json exists in the project directory.")
        st.stop()
    try:
        with open(file_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        st.error("❌ Invalid JSON format in questions file.")
        st.stop()

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

# --- Color Mapping ---
pillar_colors = {
    "Culture": "#ff6b6b",
    "Wellness": "#4ecdc4",
    "Growth": "#45b7d1"
}

# --- Session State Initialization ---
if "page" not in st.session_state:
    st.session_state.page = "intro"
    st.session_state.responses = {}
    st.session_state.org_info = {
        'name': '',
        'industry': '',
        'location': '',
        'size': '',
        'years_active': 5,
        'remote_work': '',
        'culture_focus': [],
        'current_challenges': []
    }
    st.session_state.assessment_start_time = None
    st.session_state.current_question = 0

SLIDER_LEVELS = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
LEVEL_SCORE = {lvl: i for i, lvl in enumerate(SLIDER_LEVELS)}
LEVEL_COLORS = ["#e74c3c", "#f39c12", "#95a5a6", "#27ae60", "#2ecc71"]

# --- Utility Functions ---
def get_score_interpretation(score):
    """Enhanced score interpretation with detailed insights"""
    if score >= 3.5:
        return "Excellent", "score-excellent", "🌟"
    elif score >= 2.5:
        return "Good", "score-good", "👍"
    else:
        return "Needs Improvement", "score-needs-improvement", "⚠️"

def calculate_completion_percentage():
    """Calculate assessment completion percentage"""
    total_questions = len(questions)
    answered = len([q['id'] for q in questions if q['id'] in st.session_state.responses])
    return min(int((answered / total_questions) * 100), 100)

def show_progress_bar():
    """Display enhanced progress indicator"""
    progress = calculate_completion_percentage()
    st.markdown(f"""
    <div style="margin: 1.5rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem;">
            <span style="font-weight: 600; color: #2c3e50;">Assessment Progress</span>
            <span style="font-weight: 600; color: #667eea;">{progress}% Complete</span>
        </div>
        <div style="background: #ecf0f1; border-radius: 10px; height: 10px; overflow: hidden;">
            <div style="width: {progress}%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; transition: width 0.5s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_enhanced_slider(q, idx, total, category):
    """Enhanced question display with better UX"""
    category_color = pillar_colors[category]
    st.markdown(f"""
    <div class="question-card">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="background: {category_color}; color: white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-weight: 600; margin-right: 1rem;">
                {idx + 1}
            </div>
            <div style="flex: 1;">
                <div style="font-size: 0.9rem; color: #7f8c8d; font-weight: 500;">Question {idx + 1} of {total}</div>
                <div style="font-size: 1.1rem; font-weight: 600; color: #2c3e50; margin-top: 0.25rem;">{q['question']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    current_val = 2  # Default to neutral
    if q['id'] in st.session_state.responses:
        current_val = LEVEL_SCORE[st.session_state.responses[q['id']]]

    col1, col2 = st.columns([3, 1])
    with col1:
        val = st.slider(
            f"Response for Question {idx + 1}",
            0, 4, current_val,
            format="",
            key=f"slider_{q['id']}_{uuid.uuid4()}",
            label_visibility="collapsed"
        )

    with col2:
        color = LEVEL_COLORS[val]
        st.markdown(f"""
        <div style="text-align: center; padding: 0.75rem; background: {color}; color: white; border-radius: 8px; font-weight: 600; margin-top: 1rem;">
            Disagree to Agree
        </div>
        """, unsafe_allow_html=True)

    return SLIDER_LEVELS[val]  # Return the selected level for form handling

# --- Page Navigation ---
if st.session_state.page == "intro":
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">Welcome to Thrivya 🌸</h1>
        <p class="main-subtitle">Culture Intelligence for the Modern Workplace</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="intro-features">
        <div class="feature-item culture-card">
            <div class="feature-icon">🎯</div>
            <h3>Culture Analysis</h3>
            <p>Deep insights into leadership, inclusion, and recognition patterns</p>
        </div>
        <div class="feature-item wellness-card">
            <div class="feature-icon">🧘</div>
            <h3>Wellness Metrics</h3>
            <p>Mental health, feedback culture, and workload balance assessment</p>
        </div>
        <div class="feature-item growth-card">
            <div class="feature-icon">📈</div>
            <h3>Growth Tracking</h3>
            <p>Learning opportunities, empowerment, and team dynamics evaluation</p>
        </div>
        <div class="feature-item growth-card">
            <div class="feature-icon">⚡</div>
            <h3>Instant AI Insights</h3>
            <p>Tailored to your organization's needs</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="pillar-card">
        <h3 style="color: #2c3e50; margin-bottom: 1.25rem;">🚀 Why Thrivya?</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem;">
            <div>
                <strong>🔄 Continuous:</strong> Track progress and measure cultural transformation over time
            </div>
            <div>
                <strong>📊 Data-Driven:</strong> Evidence-based culture assessment with actionable metrics
            </div>
            <div>
                <strong>🎯 HR-Focused:</strong> Practical tools and templates for immediate implementation
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Your Culture Assessment", use_container_width=True):
            st.session_state.page = "details"
            st.session_state.assessment_start_time = datetime.now()
            st.rerun()

    st.markdown("""
    <div class="brand-footer">
        <p style="margin: 0; font-size: 0.9rem; opacity: 0.8;">Crafted by Hemaang Patkar</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; opacity: 0.7;">Empowering HR professionals with culture intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "details":
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🏢 Organization Profile</h1>
        <p class="main-subtitle">Help us understand your organization better</p>
    </div>
    """, unsafe_allow_html=True)

    show_progress_bar()

    with st.form("org_form"):
        st.markdown("### 📋 Basic Information")
        col1, col2 = st.columns([1, 1], gap="medium")
        with col1:
            st.session_state.org_info['name'] = st.text_input("🏢 Organization Name", value=st.session_state.org_info['name'], placeholder="e.g., TechCorp Inc.")
            st.session_state.org_info['industry'] = st.selectbox("🏭 Industry", [
                "Technology", "Healthcare", "Finance", "Education", "Manufacturing",
                "Retail", "Consulting", "Media", "Government", "Non-Profit", "Other"
            ], index=0 if not st.session_state.org_info['industry'] else ["Technology", "Healthcare", "Finance", "Education", "Manufacturing", "Retail", "Consulting", "Media", "Government", "Non-Profit", "Other"].index(st.session_state.org_info['industry']))
            st.session_state.org_info['location'] = st.text_input("📍 Primary Location", value=st.session_state.org_info['location'], placeholder="e.g., Mumbai, India")

        with col2:
            st.session_state.org_info['size'] = st.selectbox("👥 Organization Size", [
                "1-10 (Startup)", "11-50 (Small)", "51-200 (Medium)",
                "201-500 (Large)", "501-1000 (Enterprise)", "1000+ (Corporation)"
            ], index=0 if not st.session_state.org_info['size'] else ["1-10 (Startup)", "11-50 (Small)", "51-200 (Medium)", "201-500 (Large)", "501-1000 (Enterprise)", "1000+ (Corporation)"].index(st.session_state.org_info['size']))
            st.session_state.org_info['years_active'] = st.slider("📅 Years in Operation", 0, 100, st.session_state.org_info['years_active'])
            st.session_state.org_info['remote_work'] = st.selectbox("🏠 Work Model", [
                "Fully Remote", "Hybrid", "Fully In-Office", "Flexible"
            ], index=0 if not st.session_state.org_info['remote_work'] else ["Fully Remote", "Hybrid", "Fully In-Office", "Flexible"].index(st.session_state.org_info['remote_work']))

        st.markdown("### 🎯 Cultural Focus Areas")
        st.session_state.org_info['culture_focus'] = st.multiselect(
            "Select your top cultural priorities:",
            ["Transparency", "Flexibility", "Diversity & Inclusion", "Employee Wellbeing",
             "Recognition & Rewards", "Innovation", "Collaboration", "Work-Life Balance",
             "Career Development", "Performance Excellence"],
            default=st.session_state.org_info['culture_focus'],
            help="Choose 3-5 areas that are most important to your organization"
        )

        st.session_state.org_info['current_challenges'] = st.multiselect(
            "What are your current HR challenges?",
            ["High Turnover", "Low Engagement", "Poor Communication", "Lack of Growth Opportunities",
             "Burnout", "Remote Work Challenges", "Diversity Issues", "Leadership Gaps",
             "Feedback Culture", "Change Management"],
            default=st.session_state.org_info['current_challenges']
        )

        col1, col2 = st.columns([1, 1], gap="medium")
        with col1:
            back_btn = st.form_submit_button("← Back to Home")
        with col2:
            next_btn = st.form_submit_button("Next: Culture Assessment →", use_container_width=True)

        if back_btn:
            st.session_state.page = "intro"
            st.rerun()
        if next_btn:
            if st.session_state.org_info['name'] and st.session_state.org_info['industry']:
                st.session_state.page = "culture"
                st.rerun()
            else:
                st.error("Please fill in at least Organization Name and Industry to continue.")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "culture":
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🎯 Culture Assessment</h1>
        <p class="main-subtitle">Leadership, Inclusion & Recognition</p>
    </div>
    """, unsafe_allow_html=True)

    show_progress_bar()

    questions_culture = [q for q in questions if pillar_map[q['pillar']] == "Culture"]

    with st.form("culture_form"):
        responses = {}
        for i, q in enumerate(questions_culture):
            responses[q['id']] = show_enhanced_slider(q, i, len(questions_culture), "Culture")
        st.session_state.responses.update(responses)

        col1, col2 = st.columns([1, 1], gap="medium")
        with col1:
            back_btn = st.form_submit_button("← Back to Details")
        with col2:
            next_btn = st.form_submit_button("Next: Wellness Assessment →", use_container_width=True)

        if back_btn:
            st.session_state.page = "details"
            st.rerun()
        if next_btn:
            st.session_state.page = "wellness"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "wellness":
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🧘 Wellness Assessment</h1>
        <p class="main-subtitle">Mental Health, Feedback & Work-Life Balance</p>
    </div>
    """, unsafe_allow_html=True)

    show_progress_bar()

    questions_wellness = [q for q in questions if pillar_map[q['pillar']] == "Wellness"]

    with st.form("wellness_form"):
        responses = {}
        for i, q in enumerate(questions_wellness):
            responses[q['id']] = show_enhanced_slider(q, i, len(questions_wellness), "Wellness")
        st.session_state.responses.update(responses)

        col1, col2 = st.columns([1, 1], gap="medium")
        with col1:
            back_btn = st.form_submit_button("← Back to Culture")
        with col2:
            next_btn = st.form_submit_button("Next: Growth Assessment →", use_container_width=True)

        if back_btn:
            st.session_state.page = "culture"
            st.rerun()
        if next_btn:
            st.session_state.page = "growth"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "growth":
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">📈 Growth Assessment</h1>
        <p class="main-subtitle">Learning, Empowerment & Team Dynamics</p>
    </div>
    """, unsafe_allow_html=True)

    show_progress_bar()

    questions_growth = [q for q in questions if pillar_map[q['pillar']] == "Growth"]

    with st.form("growth_form"):
        responses = {}
        for i, q in enumerate(questions_growth):
            responses[q['id']] = show_enhanced_slider(q, i, len(questions_growth), "Growth")
        st.session_state.responses.update(responses)

        col1, col2 = st.columns([1, 1], gap="medium")
        with col1:
            back_btn = st.form_submit_button("← Back to Wellness")
        with col2:
            generate_btn = st.form_submit_button("🎯 Generate Culture Intelligence Report", use_container_width=True)

        if back_btn:
            st.session_state.page = "wellness"
            st.rerun()
        if generate_btn:
            st.session_state.page = "results"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "results":
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">📊 Culture Intelligence Report</h1>
        <p class="main-subtitle">Your comprehensive workplace culture analysis</p>
    </div>
    """, unsafe_allow_html=True)

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

            if pillar not in detailed_scores:
                detailed_scores[pillar] = []
            detailed_scores[pillar].append(score)

    avg_scores = {p: round(scores[p] / counts[p], 2) if counts[p] else 0 for p in scores}
    overall_score = round(sum(avg_scores.values()) / len(avg_scores), 2)

    # Executive Summary Cards
    st.markdown("### 🎯 Executive Summary")
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="medium")

    with col1:
        overall_status, overall_class, overall_icon = get_score_interpretation(overall_score)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2.5rem;">{overall_icon}</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #2c3e50;">{overall_score}/4.0</div>
            <div style="font-size: 0.9rem; color: #7f8c8d;">Overall Culture Score</div>
        </div>
        """, unsafe_allow_html=True)

    for category, score in avg_scores.items():
        status, class_name, icon = get_score_interpretation(score)
        card_class = f"{category.lower()}-card"

        if category == "Culture":
            col = col2
        elif category == "Wellness":
            col = col3
        else:
            col = col4

        with col:
            st.markdown(f"""
            <div class="metric-card {card_class}">
                <div style="font-size: 2.5rem;">{icon}</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {pillar_colors[category]};">{score}/4.0</div>
                <div style="font-size: 0.9rem; color: #7f8c8d;">{category}</div>
            </div>
            """, unsafe_allow_html=True)

    # Enhanced Radar Chart
    st.markdown("### 📊 Culture Intelligence Radar")
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=list(avg_scores.values()),
        theta=list(avg_scores.keys()),
        fill='toself',
        name='Your Organization',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='rgba(102, 126, 234, 1)', width=3)
    ))

    benchmark_scores = [3.2, 2.8, 3.0]  # Simulated industry averages
    fig.add_trace(go.Scatterpolar(
        r=benchmark_scores,
        theta=list(avg_scores.keys()),
        fill='toself',
        name='Industry Benchmark',
        fillcolor='rgba(255, 107, 107, 0.2)',
        line=dict(color='rgba(255, 107, 107, 1)', width=2, dash='dash')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 4],
                tickvals=[0, 1, 2, 3, 4],
                ticktext=['0', '1', '2', '3', '4']
            )
        ),
        showlegend=True,
        height=500,
        font=dict(size=12),
        margin=dict(l=50, r=50, t=50, b=50)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Detailed Breakdown
    st.markdown("### 🔍 Detailed Analysis")
    culture_pillars = [p for p in detailed_scores.keys() if pillar_map[p] == "Culture"]
    wellness_pillars = [p for p in detailed_scores.keys() if pillar_map[p] == "Wellness"]
    growth_pillars = [p for p in detailed_scores.keys() if pillar_map[p] == "Growth"]

    col1, col2, col3 = st.columns([1, 1, 1], gap="medium")

    with col1:
        st.markdown("#### 🎯 Culture Pillars")
        for pillar in culture_pillars:
            pillar_avg = round(np.mean(detailed_scores[pillar]), 2)
            status, class_name, icon = get_score_interpretation(pillar_avg)
            st.markdown(f"""
            <div class="pillar-card culture-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; color: #2c3e50;">{pillar}</div>
                        <div style="font-size: 0.9rem; color: #7f8c8d;">{status}</div>
                    </div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: {pillar_colors['Culture']};">{pillar_avg}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### 🧘 Wellness Pillars")
        for pillar in wellness_pillars:
            pillar_avg = round(np.mean(detailed_scores[pillar]), 2)
            status, class_name, icon = get_score_interpretation(pillar_avg)
            st.markdown(f"""
            <div class="pillar-card wellness-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; color: #2c3e50;">{pillar}</div>
                        <div style="font-size: 0.9rem; color: #7f8c8d;">{status}</div>
                    </div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: {pillar_colors['Wellness']};">{pillar_avg}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        st.markdown("#### 📈 Growth Pillars")
        for pillar in growth_pillars:
            pillar_avg = round(np.mean(detailed_scores[pillar]), 2)
            status, class_name, icon = get_score_interpretation(pillar_avg)
            st.markdown(f"""
            <div class="pillar-card growth-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; color: #2c3e50;">{pillar}</div>
                        <div style="font-size: 0.9rem; color: #7f8c8d;">{status}</div>
                    </div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: {pillar_colors['Growth']};">{pillar_avg}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # AI-Generated Recommendations
    st.markdown("### 🤖 AI-Powered Recommendations")
    try:
        detailed_answers = []
        for q in questions:
            if q['id'] in responses:
                detailed_answers.append(f"• {q['pillar']} - {q['question']}: {responses[q['id']]} ({LEVEL_SCORE[responses[q['id']]]}/4)")

        detailed_answers_str = "\n".join(detailed_answers)

        enhanced_prompt = f"""
You are a senior Culture & People Analytics Consultant with 15+ years of experience helping organizations transform their workplace culture. You've worked with Fortune 500 companies and startups across various industries.

Based on the comprehensive culture intelligence data below, provide a detailed strategic analysis and action plan:

## ORGANIZATION PROFILE:
🏢 **Company**: {org.get('name', 'N/A')} | **Industry**: {org.get('industry', 'N/A')} | **Size**: {org.get('size', 'N/A')} | **Location**: {org.get('location', 'N/A')}
📅 **Years Active**: {org.get('years_active', 'N/A')} | **Work Model**: {org.get('remote_work', 'N/A')}
🎯 **Cultural Priorities**: {', '.join(org.get('culture_focus', []))}
⚠️ **Current Challenges**: {', '.join(org.get('current_challenges', []))}

## CULTURE INTELLIGENCE SCORES:
📊 **Overall Score**: {overall_score}/4.0 ({get_score_interpretation(overall_score)[0]})
- 🎯 **Culture**: {avg_scores['Culture']}/4.0 ({get_score_interpretation(avg_scores['Culture'])[0]})
- 🧘 **Wellness**: {avg_scores['Wellness']}/4.0 ({get_score_interpretation(avg_scores['Wellness'])[0]})
- 📈 **Growth**: {avg_scores['Growth']}/4.0 ({get_score_interpretation(avg_scores['Growth'])[0]})

## DETAILED PILLAR ANALYSIS:
{detailed_answers_str}

## REQUIRED DELIVERABLES:

### 1. 🎯 EXECUTIVE SUMMARY (150 words)
Provide a high-level strategic overview of the organization's culture health. Highlight the top 3 strengths and top 3 critical areas needing attention. Include industry-specific insights and benchmarking context.

### 2. 📊 DEEP DIVE ANALYSIS
**Culture Pillar Analysis:**
- Leadership & Vision effectiveness
- Inclusivity & Belonging assessment
- Recognition & Motivation patterns

**Wellness Pillar Analysis:**
- Well-being & Work-Life balance status
- Feedback & Communication effectiveness

**Growth Pillar Analysis:**
- Learning & Development opportunities
- Team Dynamics & Trust levels
- Autonomy & Empowerment culture

### 3. 🚀 STRATEGIC ACTION PLAN
**Immediate Actions (0-30 days):**
- List 3-5 quick wins that can be implemented immediately
- Focus on high-impact, low-cost initiatives
- Include specific steps and responsible parties

**Short-term Initiatives (30-90 days):**
- 3-5 medium-term projects with clear timelines
- Include resource requirements and success metrics
- Focus on addressing the lowest scoring pillars

**Long-term Strategy (90-365 days):**
- 2-3 transformational initiatives
- Include change management considerations
- Focus on sustainable culture transformation

### 4. 🛠️ RECOMMENDED TOOLS & RESOURCES
**HR Tech Stack:**
- Suggest specific software/platforms for the identified challenges
- Include employee engagement platforms, feedback tools, learning management systems

**Templates & Frameworks:**
- Provide specific templates for implementation
- Include measurement frameworks and KPIs
- Suggest industry-specific best practices

**Training & Development:**
- Recommend specific training programs
- Include leadership development initiatives
- Suggest both internal and external resources

### 5. 📈 SUCCESS METRICS & KPIs
**Culture Metrics:**
- Define specific, measurable KPIs for each pillar
- Include baseline measurements and target improvements
- Suggest measurement frequency and methods

**ROI Indicators:**
- Link culture improvements to business outcomes
- Include engagement, retention, and productivity metrics
- Suggest cost-benefit analysis frameworks

### 6. 🎭 INDUSTRY-SPECIFIC CONSIDERATIONS
Provide {org.get('industry', 'industry')}-specific insights:
- Common culture challenges in this industry
- Industry benchmarks and best practices
- Regulatory/compliance considerations if applicable

### 7. 🚨 RISK MITIGATION
**Change Management Risks:**
- Identify potential resistance points
- Suggest mitigation strategies
- Include communication plans

**Implementation Risks:**
- Highlight resource constraints
- Suggest phased implementation approaches
- Include contingency plans

FORMAT: Use clear headings, bullet points, and actionable language. Make recommendations specific, measurable, and time-bound. Include relevant emojis for visual appeal and readability.

TONE: Professional yet accessible, data-driven but human-centered, optimistic but realistic about challenges.
"""

        with st.spinner("🔄 Generating your comprehensive culture intelligence report..."):
            cohere_api_key = st.secrets.get("cohere_api_key")
            if cohere_api_key:
                try:
                    response = requests.post(
                        url="https://api.cohere.ai/v1/chat",
                        headers={
                            "Authorization": f"Bearer {cohere_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "command-r-plus",
                            "message": enhanced_prompt,
                            "temperature": 0.7,
                            "max_tokens": 4096
                        },
                        timeout=180
                    )

                    if response.status_code == 200:
                        result = response.json().get("text", "No AI response returned.")
                        st.markdown(f"""
                        <div class="recommendation-box">
                            <h3 style="margin-top: 0; color: #2c3e50;">🤖 AI-Generated Culture Intelligence Report</h3>
                            <p style="margin-bottom: 0; color: #7f8c8d; font-size: 0.9rem;">
                                Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p IST')}
                                | Based on {len(responses)} responses
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(result)
                    else:
                        st.error(f"❌ API Error: {response.status_code} - {response.text}")
                except requests.exceptions.Timeout:
                    st.error("❌ Request timeout. Please try again.")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Network error: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
            else:
                st.warning("⚠️ Cohere API key not found in secrets. Please configure your API key to generate AI recommendations.")
                st.markdown("""
                <div class="recommendation-box">
                    <h3 style="margin-top: 0;">📋 Basic Culture Analysis</h3>
                    <p>Based on your responses, here are some general observations:</p>
                </div>
                """, unsafe_allow_html=True)
                if overall_score >= 3.5:
                    st.success("🌟 Your organization shows excellent cultural health across all dimensions!")
                elif overall_score >= 2.5:
                    st.info("👍 Your organization has a solid cultural foundation with room for targeted improvements.")
                else:
                    st.warning("⚠️ Your organization has significant opportunities for cultural enhancement.")
                lowest_score = min(avg_scores.items(), key=lambda x: x[1])
                st.markdown(f"""
                **Priority Focus Area:** {lowest_score[0]} (Score: {lowest_score[1]}/4.0)

                **General Recommendations:**
                - Focus on improving {lowest_score[0].lower()} initiatives
                - Conduct focus groups to understand specific pain points
                - Implement regular pulse surveys to track progress
                - Consider leadership training programs
                - Review and update policies related to your lowest-scoring areas
                """)

        # Additional Analytics
        st.markdown("### 📊 Additional Insights")
        col1, col2 = st.columns([1, 1], gap="medium")

        with col1:
            response_counts = {level: 0 for level in SLIDER_LEVELS}
            for resp in responses.values():
                response_counts[resp] += 1

            fig_dist = px.bar(
                x=list(response_counts.keys()),
                y=list(response_counts.values()),
                title="Response Distribution",
                color=list(response_counts.values()),
                color_continuous_scale="RdYlGn"
            )
            fig_dist.update_layout(height=400, margin=dict(l=50, r=50, t=50, b=50))
            st.plotly_chart(fig_dist, use_container_width=True)

        with col2:
            pillar_scores = {}
            for pillar, scores_list in detailed_scores.items():
                pillar_scores[pillar] = round(np.mean(scores_list), 2)

            fig_pillar = px.bar(
                x=list(pillar_scores.values()),
                y=list(pillar_scores.keys()),
                orientation='h',
                title="Pillar-wise Scores",
                color=list(pillar_scores.values()),
                color_continuous_scale="RdYlGn"
            )
            fig_pillar.update_layout(height=400, margin=dict(l=50, r=50, t=50, b=50))
            st.plotly_chart(fig_pillar, use_container_width=True)

        # Assessment Summary
        assessment_time = datetime.now() - st.session_state.assessment_start_time if st.session_state.assessment_start_time else timedelta(minutes=10)
        st.markdown(f"""
        <div class="pillar-card">
            <h4 style="margin-top: 0; color: #2c3e50;">📋 Assessment Summary</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; margin-top: 1.25rem;">
                <div><strong>📊 Total Questions:</strong> {len(questions)}</div>
                <div><strong>✅ Responses Collected:</strong> {len(responses)}</div>
                <div><strong>⏱️ Time Taken:</strong> ~{int(assessment_time.total_seconds() / 60)} minutes</div>
                <div><strong>📈 Completion Rate:</strong> {calculate_completion_percentage()}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error generating recommendations: {str(e)}")
        st.info("Please try refreshing the page or contact support if the issue persists.")

    # Brand Footer
    st.markdown("""
    <div class="brand-footer">
        <p style="margin: 0; font-size: 1rem; font-weight: 600;">Thrivya Culture Intelligence Platform</p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.8;">Crafted by Hemaang Patkar</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
