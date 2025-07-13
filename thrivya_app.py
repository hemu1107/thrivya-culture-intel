# --- Thrivya | Culture Intelligence Platform ---
import streamlit as st
import json
import requests
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# --- Configuration ---
st.set_page_config(
    page_title="Thrivya | Culture Intelligence", 
    layout="centered", 
    page_icon="🌸",
    initial_sidebar_state="collapsed"
)

# --- Enhanced Styling ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        body {
            font-family: 'Inter', sans-serif;
            color: #2c3e50; /* Darker text for better readability */
            background-color: #f8f9fa; /* Light background */
        }

        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2.5rem 1.5rem; /* Increased padding */
            border-radius: 18px; /* Slightly more rounded */
            margin-bottom: 2.5rem; /* More space below header */
            text-align: center;
            color: white;
            box-shadow: 0 10px 35px rgba(0,0,0,0.15); /* Stronger shadow */
            position: relative; /* For the subtle pattern */
            overflow: hidden;
        }

        .main-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: url('data:image/svg+xml;utf8,<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="10" fill="%23ffffff" opacity="0.1"/><circle cx="20" cy="80" r="8" fill="%23ffffff" opacity="0.05"/><circle cx="80" cy="20" r="12" fill="%23ffffff" opacity="0.07"/></svg>');
            background-size: 20px 20px;
            opacity: 0.1;
            pointer-events: none;
        }
        
        .main-title {
            font-family: 'Inter', sans-serif;
            font-size: 2.8rem; /* Larger title */
            font-weight: 700;
            margin: 0;
            text-shadow: 2px 3px 5px rgba(0,0,0,0.4); /* More pronounced shadow */
        }
        
        .main-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 1.2rem; /* Slightly larger subtitle */
            font-weight: 400;
            margin-top: 0.75rem; /* More space below title */
            opacity: 0.95;
        }
        
        .pillar-card {
            background: white;
            border-radius: 15px; /* More rounded */
            padding: 1.75rem; /* Increased padding */
            margin: 1rem 0;
            box-shadow: 0 6px 25px rgba(0,0,0,0.1); /* Stronger shadow */
            border-left: 5px solid; /* Thicker border */
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            display: flex; /* For better content alignment */
            flex-direction: column;
            justify-content: space-between;
            min-height: 120px; /* Ensure consistent height */
        }
        
        .pillar-card:hover {
            transform: translateY(-5px); /* More noticeable lift */
            box-shadow: 0 10px 30px rgba(0,0,0,0.15); /* Even stronger shadow on hover */
        }
        
        .culture-card { border-left-color: #ff6b6b; } /* Vibrant red */
        .wellness-card { border-left-color: #4ecdc4; } /* Teal */
        .growth-card { border-left-color: #45b7d1; } /* Sky blue */

        /* Specific styles for score cards */
        .metric-card {
            background: white; /* Changed to white for consistency */
            border-radius: 12px;
            padding: 1.2rem;
            text-align: center;
            margin: 0.75rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: transform 0.2s ease;
        }

        .metric-card:hover {
            transform: translateY(-2px);
        }
        
        .score-excellent { color: #27ae60; font-weight: 600; } /* Emerald Green */
        .score-good { color: #f39c12; font-weight: 600; } /* Orange */
        .score-needs-improvement { color: #e74c3c; font-weight: 600; } /* Alizarin Red */
        
        .recommendation-box {
            background: linear-gradient(135deg, #e0f7fa 0%, #bbdefb 100%); /* Lighter, more professional gradient */
            border-radius: 15px;
            padding: 2rem;
            margin: 2rem 0;
            border-left: 5px solid #2196f3; /* Blue border */
            box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        }
        
        .progress-indicator {
            background: linear-gradient(90deg, #00d2ff 0%, #3a47d5 100%);
            height: 4px;
            border-radius: 2px;
            margin: 1rem 0;
        }
        
        .question-card {
            background: white;
            border-radius: 12px; /* More rounded */
            padding: 1.75rem; /* Increased padding */
            margin: 1.5rem 0; /* More vertical space between questions */
            box-shadow: 0 4px 15px rgba(0,0,0,0.06); /* Softer shadow */
            border: 1px solid #e9ecef; /* Lighter border */
            transition: box-shadow 0.2s ease;
        }

        .question-card:hover {
            box-shadow: 0 6px 20px rgba(0,0,0,0.09);
        }
        
        .brand-footer {
            text-align: center;
            margin-top: 4rem; /* More space before footer */
            padding: 2.5rem; /* More padding */
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 18px;
            color: white;
            box-shadow: 0 -5px 25px rgba(0,0,0,0.1);
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px; /* More rounded buttons */
            padding: 0.9rem 2.2rem; /* Larger padding */
            font-weight: 600;
            font-size: 1.05rem; /* Slightly larger text */
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .stButton > button:hover {
            transform: translateY(-3px); /* More pronounced lift */
            box-shadow: 0 6px 20px rgba(0,0,0,0.25); /* Stronger shadow on hover */
        }
        
        .intro-features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); /* Adjusted min-width for features */
            gap: 1.5rem; /* Increased gap */
            margin: 2.5rem 0;
        }
        
        .feature-item {
            background: white;
            padding: 2rem; /* More padding */
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-bottom: 4px solid; /* Added bottom border for subtle color */
        }
        
        .feature-item:hover {
            transform: translateY(-5px); /* More pronounced lift */
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        }

        .feature-item:nth-child(1) { border-bottom-color: #ff6b6b; }
        .feature-item:nth-child(2) { border-bottom-color: #4ecdc4; }
        .feature-item:nth-child(3) { border-bottom-color: #45b7d1; }
        .feature-item:nth-child(4) { border-bottom-color: #a276b2; } /* New color for the 4th item */
        
        .feature-icon {
            font-size: 3rem; /* Larger icon */
            margin-bottom: 1.2rem; /* More space below icon */
        }

        /* Adjustments for Streamlit default elements */
        .stTextInput > div > div > input, .stSelectbox > div > div > div > div, .stMultiSelect > div > div > div {
            border-radius: 8px;
            border: 1px solid #ced4da;
            padding: 0.6rem 1rem;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
        }
        .stTextInput > div > div > input:focus, .stSelectbox > div > div > div > div:focus, .stMultiSelect > div > div > div:focus-within {
            border-color: #80bdff;
            box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
        }

        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            font-family: 'Inter', sans-serif;
            font-weight: 700;
        }

        .stAlert {
            border-radius: 10px;
            padding: 1rem 1.5rem;
        }

        .stSpinner > div > div > div {
            color: #667eea;
        }
    </style>
""", unsafe_allow_html=True)

# --- Load Questions ---
@st.cache_data
def load_questions():
    file_path = Path("culture_questions.json")
    if not file_path.exists():
        st.error("❌ Questions file not found. Please ensure `culture_questions.json` exists in the project directory.")
        st.stop()
    try:
        with open(file_path) as f:
            return json.load(f)
    except json.JSONDecodeError:
        st.error("❌ Invalid JSON format in questions file. Please check `culture_questions.json` for errors.")
        st.stop()

questions = load_questions()

# --- Enhanced Mapping ---
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

# --- Enhanced Session State ---
if "page" not in st.session_state:
    st.session_state.page = "intro"
    st.session_state.responses = {}
    st.session_state.org_info = {
        'name': '', 'industry': 'Technology', 'location': '', 'size': '1-10 (Startup)',
        'years_active': 5, 'remote_work': 'Hybrid', 'culture_focus': [], 'current_challenges': []
    }
    st.session_state.assessment_start_time = None
    st.session_state.current_question = 0 # Not directly used for page navigation, but kept for context

SLIDER_LEVELS = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
LEVEL_SCORE = {lvl: i for i, lvl in enumerate(SLIDER_LEVELS)}
LEVEL_COLORS = ["#e74c3c", "#f39c12", "#95a5a6", "#2ecc71", "#27ae60"] # Added more distinct green

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
    # Ensure all questions for the current and previous sections are considered
    answered_count = 0
    if st.session_state.page == "culture":
        questions_current_section = [q for q in questions if pillar_map[q['pillar']] == "Culture"]
        answered_count = sum(1 for q in questions_current_section if q['id'] in st.session_state.responses)
    elif st.session_state.page == "wellness":
        questions_culture = [q for q in questions if pillar_map[q['pillar']] == "Culture"]
        questions_current_section = [q for q in questions if pillar_map[q['pillar']] == "Wellness"]
        answered_count = sum(1 for q in questions_culture if q['id'] in st.session_state.responses) + \
                         sum(1 for q in questions_current_section if q['id'] in st.session_state.responses)
    elif st.session_state.page == "growth":
        questions_culture = [q for q in questions if pillar_map[q['pillar']] == "Culture"]
        questions_wellness = [q for q in questions if pillar_map[q['pillar']] == "Wellness"]
        questions_current_section = [q for q in questions if pillar_map[q['pillar']] == "Growth"]
        answered_count = sum(1 for q in questions_culture if q['id'] in st.session_state.responses) + \
                         sum(1 for q in questions_wellness if q['id'] in st.session_state.responses) + \
                         sum(1 for q in questions_current_section if q['id'] in st.session_state.responses)
    elif st.session_state.page == "results":
        answered_count = len(st.session_state.responses) # For results, count all responses

    return min(int((answered_count / total_questions) * 100), 100)

def show_progress_bar():
    """Display enhanced progress indicator"""
    progress = calculate_completion_percentage()
    st.markdown(f"""
    <div style="margin: 1.5rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.6rem;">
            <span style="font-weight: 600; color: #2c3e50; font-size: 1.05rem;">Assessment Progress</span>
            <span style="font-weight: 600; color: #667eea; font-size: 1.05rem;">{progress}% Complete</span>
        </div>
        <div style="background: #e0e6ec; border-radius: 10px; height: 10px; overflow: hidden;">
            <div style="width: {progress}%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; transition: width 0.4s ease-out;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Enhanced Question Display ---
def show_enhanced_slider(q, idx, total, category_color="#667eea"):
    """Enhanced question display with better UX"""
    st.markdown(f"""
    <div class="question-card">
        <div style="display: flex; align-items: flex-start; margin-bottom: 1.2rem;">
            <div style="background: {category_color}; color: white; border-radius: 50%; min-width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; font-weight: 600; margin-right: 1.2rem; font-size: 1.1rem;">
                {idx + 1}
            </div>
            <div style="flex: 1;">
                <div style="font-size: 0.95rem; color: #7f8c8d; font-weight: 500;">Question {idx + 1} of {total}</div>
                <div style="font-size: 1.15rem; font-weight: 600; color: #2c3e50; margin-top: 0.4rem; line-height: 1.4;">{q['question']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced slider with color coding
    current_val = 2  # Default to neutral
    if q['id'] in st.session_state.responses:
        current_val = LEVEL_SCORE[st.session_state.responses[q['id']]]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        val = st.slider(
            f"Response for Question {idx + 1}",
            0, 4, current_val,
            format="",
            key=f"slider_{q['id']}",
            label_visibility="collapsed"
        )
    
    with col2:
        color = LEVEL_COLORS[val]
        st.markdown(f"""
        <div style="text-align: center; padding: 0.9rem; background: {color}; color: white; border-radius: 10px; font-weight: 600; margin-top: 1rem; font-size: 0.95rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            {SLIDER_LEVELS[val]}
        </div>
        """, unsafe_allow_html=True)
    
    st.session_state.responses[q['id']] = SLIDER_LEVELS[val]

# --- Enhanced Pages ---
if st.session_state.page == "intro":
    # Main Header
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">Welcome to Thrivya 🌸</h1>
        <p class="main-subtitle">Culture Intelligence for the Modern Workplace</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Grid
    st.markdown("""
    <div class="intro-features">
        <div class="feature-item">
            <div class="feature-icon">🎯</div>
            <h3>Culture Analysis</h3>
            <p style="font-size: 0.95rem;">Deep insights into leadership, inclusion, and recognition patterns</p>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🧘</div>
            <h3>Wellness Metrics</h3>
            <p style="font-size: 0.95rem;">Mental health, feedback culture, and workload balance assessment</p>
        </div>
        <div class="feature-item">
            <div class="feature-icon">📈</div>
            <h3>Growth Tracking</h3>
            <p style="font-size: 0.95rem;">Learning opportunities, empowerment, and team dynamics evaluation</p>
        </div>
        <div class="feature-item">
            <div class="feature-icon">⚡</div>
            <h3>Instant AI Insights</h3>
            <p style="font-size: 0.95rem;">Tailored, actionable recommendations for your organization</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Value Proposition
    st.markdown("""
    <div class="pillar-card" style="border-left-color: #667eea; margin-top: 3rem;">
        <h3 style="color: #2c3e50; margin-bottom: 1rem;">🚀 Why Thrivya?</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; font-size: 0.95rem;">
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
    
    # Start Assessment Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Your Culture Assessment", use_container_width=True):
            st.session_state.page = "details"
            st.session_state.assessment_start_time = datetime.now()
            st.rerun()
    
    # Brand Footer
    st.markdown("""
    <div class="brand-footer">
        <p style="margin: 0; font-size: 0.95rem; opacity: 0.8;">Crafted by Hemaang Patkar</p>
        <p style="margin: 0.6rem 0 0 0; font-size: 0.85rem; opacity: 0.7;">Empowering HR professionals with culture intelligence</p>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "details":
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🏢 Organization Profile</h1>
        <p class="main-subtitle">Help us understand your organization better</p>
    </div>
    """, unsafe_allow_html=True)
    
    show_progress_bar()
    
    with st.form("org_form", clear_on_submit=False): # Keep form values on re-run
        st.markdown("### 📋 Basic Information")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.org_info['name'] = st.text_input("🏢 Organization Name", value=st.session_state.org_info['name'], placeholder="e.g., TechCorp Inc.")
            st.session_state.org_info['industry'] = st.selectbox("🏭 Industry", [
                "Technology", "Healthcare", "Finance", "Education", "Manufacturing",
                "Retail", "Consulting", "Media", "Government", "Non-Profit", "Other"
            ], index=["Technology", "Healthcare", "Finance", "Education", "Manufacturing",
                "Retail", "Consulting", "Media", "Government", "Non-Profit", "Other"].index(st.session_state.org_info['industry']))
            st.session_state.org_info['location'] = st.text_input("📍 Primary Location", value=st.session_state.org_info['location'], placeholder="e.g., Mumbai, India")
        
        with col2:
            st.session_state.org_info['size'] = st.selectbox("👥 Organization Size", [
                "1-10 (Startup)", "11-50 (Small)", "51-200 (Medium)", 
                "201-500 (Large)", "501-1000 (Enterprise)", "1000+ (Corporation)"
            ], index=["1-10 (Startup)", "11-50 (Small)", "51-200 (Medium)", 
                "201-500 (Large)", "501-1000 (Enterprise)", "1000+ (Corporation)"].index(st.session_state.org_info['size']))
            st.session_state.org_info['years_active'] = st.slider("📅 Years in Operation", 0, 100, st.session_state.org_info['years_active'])
            st.session_state.org_info['remote_work'] = st.selectbox("🏠 Work Model", [
                "Fully Remote", "Hybrid", "Fully In-Office", "Flexible"
            ], index=["Fully Remote", "Hybrid", "Fully In-Office", "Flexible"].index(st.session_state.org_info['remote_work']))
        
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
        
        col1, col2 = st.columns(2)
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
                st.error("Please fill in at least **Organization Name** and **Industry** to continue.")

elif st.session_state.page == "culture":
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🎯 Culture Assessment</h1>
        <p class="main-subtitle">Leadership, Inclusion & Recognition</p>
    </div>
    """, unsafe_allow_html=True)
    
    show_progress_bar()
    
    questions_culture = [q for q in questions if pillar_map[q['pillar']] == "Culture"]
    
    with st.form("culture_form", clear_on_submit=False):
        for i, q in enumerate(questions_culture):
            show_enhanced_slider(q, i, len(questions_culture), "#ff6b6b")
        
        col1, col2 = st.columns(2)
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

elif st.session_state.page == "wellness":
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🧘 Wellness Assessment</h1>
        <p class="main-subtitle">Mental Health, Feedback & Work-Life Balance</p>
    </div>
    """, unsafe_allow_html=True)
    
    show_progress_bar()
    
    questions_wellness = [q for q in questions if pillar_map[q['pillar']] == "Wellness"]
    
    with st.form("wellness_form", clear_on_submit=False):
        for i, q in enumerate(questions_wellness):
            show_enhanced_slider(q, i, len(questions_wellness), "#4ecdc4")
        
        col1, col2 = st.columns(2)
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

elif st.session_state.page == "growth":
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">📈 Growth Assessment</h1>
        <p class="main-subtitle">Learning, Empowerment & Team Dynamics</p>
    </div>
    """, unsafe_allow_html=True)
    
    show_progress_bar()
    
    questions_growth = [q for q in questions if pillar_map[q['pillar']] == "Growth"]
    
    with st.form("growth_form", clear_on_submit=False):
        for i, q in enumerate(questions_growth):
            show_enhanced_slider(q, i, len(questions_growth), "#45b7d1")
        
        col1, col2 = st.columns(2)
        with col1:
            back_btn = st.form_submit_button("← Back to Wellness")
        with col2:
            generate_btn = st.form_submit_button("🎯 Generate Culture Intelligence Report", use_container_width=True)
        
        if back_btn:
            st.session_state.page = "wellness"
            st.rerun()
        if generate_btn:
            # Check if all questions are answered before proceeding
            total_questions_answered = len(st.session_state.responses)
            if total_questions_answered == len(questions):
                st.session_state.page = "results"
                st.rerun()
            else:
                st.warning(f"Please answer all questions to generate the report. You have answered {total_questions_answered} out of {len(questions)}.")

elif st.session_state.page == "results":
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">📊 Culture Intelligence Report</h1>
        <p class="main-subtitle">Your comprehensive workplace culture analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    responses = st.session_state.responses
    org = st.session_state.org_info
    
    # Enhanced Score Calculation
    scores = {'Culture': 0, 'Wellness': 0, 'Growth': 0}
    counts = {'Culture': 0, 'Wellness': 0, 'Growth': 0}
    detailed_scores = {} # Stores list of scores for each specific pillar
    
    for q in questions:
        resp = responses.get(q['id'])
        if resp is None: # Handle unanswered questions for robustness
            continue
        pillar = q['pillar']
        category = pillar_map[pillar]
        score = LEVEL_SCORE[resp]
        
        scores[category] += score
        counts[category] += 1
        
        if pillar not in detailed_scores:
            detailed_scores[pillar] = []
        detailed_scores[pillar].append(score)
    
    avg_scores = {p: round(scores[p] / counts[p], 2) if counts[p] else 0 for p in scores}
    overall_score = round(sum(avg_scores.values()) / len(avg_scores) if avg_scores else 0, 2)
    
    # Executive Summary Cards
    st.markdown("### 🎯 Executive Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        overall_status, overall_class, overall_icon = get_score_interpretation(overall_score)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2.2rem;">{overall_icon}</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #2c3e50; margin-top: 0.5rem;">{overall_score}/4.0</div>
            <div style="font-size: 0.95rem; color: #7f8c8d; margin-top: 0.2rem;">Overall Culture Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    for category, score in avg_scores.items():
        status, class_name, icon = get_score_interpretation(score)
        colors = {"Culture": "#ff6b6b", "Wellness": "#4ecdc4", "Growth": "#45b7d1"}
        
        if category == "Culture":
            col = col2
        elif category == "Wellness":
            col = col3
        else: # Growth
            col = col4
        
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2.2rem;">{icon}</div>
                <div style="font-size: 1.6rem; font-weight: 700; color: {colors[category]}; margin-top: 0.5rem;">{score}/4.0</div>
                <div style="font-size: 0.95rem; color: #7f8c8d; margin-top: 0.2rem;">{category}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced Radar Chart
    st.markdown("---") # Horizontal line for separation
    st.markdown("### 📊 Culture Intelligence Radar")
    
    # Create radar chart with enhanced styling
    fig = go.Figure()
    
    # Dynamically get categories to ensure correct order for radar chart
    radar_categories = list(avg_scores.keys())
    radar_values = [avg_scores[cat] for cat in radar_categories]

    fig.add_trace(go.Scatterpolar(
        r=radar_values,
        theta=radar_categories,
        fill='toself',
        name='Your Organization',
        fillcolor='rgba(102, 126, 234, 0.4)', # Softer fill
        line=dict(color='rgba(102, 126, 234, 1)', width=4), # Thicker line
        hovertemplate="<b>%{theta}</b>: %{r:.2f}/4.0<extra></extra>"
    ))
    
    # Add industry benchmark (simulated) - make it slightly dynamic based on overall score
    # If overall score is good, benchmark is slightly lower, if bad, benchmark is higher
    benchmark_base = 3.0
    if overall_score >= 3.5:
        benchmark_scores = [benchmark_base - 0.2, benchmark_base - 0.4, benchmark_base - 0.3]
    elif overall_score >= 2.5:
        benchmark_scores = [benchmark_base, benchmark_base - 0.2, benchmark_base + 0.1]
    else:
        benchmark_scores = [benchmark_base + 0.3, benchmark_base + 0.2, benchmark_base + 0.4]
    
    # Ensure benchmark scores are within 0-4 range
    benchmark_scores = [max(0, min(4, s)) for s in benchmark_scores]

    fig.add_trace(go.Scatterpolar(
        r=benchmark_scores,
        theta=radar_categories,
        fill='toself',
        name='Simulated Industry Benchmark',
        fillcolor='rgba(255, 107, 107, 0.25)', # Softer fill
        line=dict(color='rgba(255, 107, 107, 0.8)', width=2, dash='dash'),
        hovertemplate="<b>%{theta}</b>: %{r:.2f}/4.0 (Benchmark)<extra></extra>"
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 4],
                tickvals=[0, 1, 2, 3, 4],
                ticktext=['0', '1', '2', '3', '4'],
                gridcolor='#e0e0e0', # Lighter grid lines
                linecolor='#e0e0e0'
            ),
            angularaxis=dict(
                rotation=90, # Start labels from the top
                direction="clockwise",
                linecolor='#e0e0e0',
                tickfont=dict(size=14, color='#34495e') # Larger, darker labels
            )
        ),
        showlegend=True,
        height=550, # Slightly taller chart
        font=dict(size=13, family='Inter'),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5) # Legend below chart
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Breakdown
    st.markdown("---") # Horizontal line for separation
    st.markdown("### 🔍 Detailed Analysis")
    
    # Filter pillars based on their main category for structured display
    culture_pillars = [p for p in detailed_scores.keys() if pillar_map[p] == "Culture"]
    wellness_pillars = [p for p in detailed_scores.keys() if pillar_map[p] == "Wellness"]
    growth_pillars = [p for p in detailed_scores.keys() if pillar_map[p] == "Growth"]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🎯 Culture Pillars")
        for pillar in culture_pillars:
            pillar_avg = round(np.mean(detailed_scores[pillar]), 2) if detailed_scores[pillar] else 0 # Handle empty list
            status, class_name, icon = get_score_interpretation(pillar_avg)
            st.markdown(f"""
            <div class="pillar-card culture-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; color: #2c3e50; font-size: 1.05rem;">{pillar}</div>
                        <div style="font-size: 0.9rem; color: #7f8c8d; margin-top: 0.2rem;">{status} {icon}</div>
                    </div>
                    <div style="font-size: 1.6rem; font-weight: 700; color: #ff6b6b;">{pillar_avg}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🧘 Wellness Pillars")
        for pillar in wellness_pillars:
            pillar_avg = round(np.mean(detailed_scores[pillar]), 2) if detailed_scores[pillar] else 0
            status, class_name, icon = get_score_interpretation(pillar_avg)
            st.markdown(f"""
            <div class="pillar-card wellness-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; color: #2c3e50; font-size: 1.05rem;">{pillar}</div>
                        <div style="font-size: 0.9rem; color: #7f8c8d; margin-top: 0.2rem;">{status} {icon}</div>
                    </div>
                    <div style="font-size: 1.6rem; font-weight: 700; color: #4ecdc4;">{pillar_avg}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("#### 📈 Growth Pillars")
        for pillar in growth_pillars:
            pillar_avg = round(np.mean(detailed_scores[pillar]), 2) if detailed_scores[pillar] else 0
            status, class_name, icon = get_score_interpretation(pillar_avg)
            st.markdown(f"""
            <div class="pillar-card growth-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-weight: 600; color: #2c3e50; font-size: 1.05rem;">{pillar}</div>
                        <div style="font-size: 0.9rem; color: #7f8c8d; margin-top: 0.2rem;">{status} {icon}</div>
                    </div>
                    <div style="font-size: 1.6rem; font-weight: 700; color: #45b7d1;">{pillar_avg}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # AI-Generated Recommendations
    st.markdown("---") # Horizontal line for separation
    st.markdown("### 🤖 AI-Powered Recommendations")
    
    try:
        # Enhanced detailed response analysis
        detailed_answers = []
        for q in questions:
            resp = responses.get(q['id'])
            if resp is not None:
                detailed_answers.append(f"• **{q['pillar']}** - {q['question']}: **{resp}** ({LEVEL_SCORE[resp]}/4)")
        
        detailed_answers_str = "\n".join(detailed_answers)
        
        # Enhanced AI Prompt
        enhanced_prompt = f"""
You are a senior Culture & People Analytics Consultant with 15+ years of experience helping organizations transform their workplace culture. You've worked with Fortune 500 companies and startups across various industries.

Based on the comprehensive culture intelligence data below, provide a detailed strategic analysis and action plan. Be extremely thorough, insightful, and actionable in your recommendations.

## ORGANIZATION PROFILE:
🏢 **Company**: {org.get('name', 'N/A')}
🏭 **Industry**: {org.get('industry', 'N/A')}
👥 **Size**: {org.get('size', 'N/A')}
📍 **Primary Location**: {org.get('location', 'N/A')}
📅 **Years in Operation**: {org.get('years_active', 'N/A')}
🏠 **Work Model**: {org.get('remote_work', 'N/A')}
🎯 **Top Cultural Priorities**: {', '.join(org.get('culture_focus', ['Not specified']))}
⚠️ **Current HR Challenges**: {', '.join(org.get('current_challenges', ['Not specified']))}

## CULTURE INTELLIGENCE SCORES:
📊 **Overall Culture Health Score**: {overall_score}/4.0 ({get_score_interpretation(overall_score)[0]})
- 🎯 **Culture Pillar Average**: {avg_scores['Culture']}/4.0 ({get_score_interpretation(avg_scores['Culture'])[0]})
- 🧘 **Wellness Pillar Average**: {avg_scores['Wellness']}/4.0 ({get_score_interpretation(avg_scores['Wellness'])[0]})
- 📈 **Growth Pillar Average**: {avg_scores['Growth']}/4.0 ({get_score_interpretation(avg_scores['Growth'])[0]})

## DETAILED PILLAR ANALYSIS:
Here is a breakdown of responses to individual questions, categorized by their respective pillars:
{detailed_answers_str}

## REQUIRED DELIVERABLES:

### 1. 🎯 EXECUTIVE SUMMARY
Provide a concise, high-level strategic overview (approximately 150-200 words) of the organization's current culture health. Identify the **top 3 strengths** that should be leveraged and the **top 3 critical areas** that urgently need attention. Incorporate insights specific to the {org.get('industry', 'industry')} industry and benchmark context.

### 2. 📊 DEEP DIVE ANALYSIS
Provide a thorough analysis for each main pillar and its sub-pillars, identifying specific areas of strength and weakness based on the detailed responses.
#### Culture Pillar Analysis:
- **Leadership & Vision Effectiveness:** Analyze scores related to leadership clarity, trust, and alignment with organizational goals.
- **Inclusivity & Belonging Assessment:** Evaluate how inclusive the environment is perceived and the sense of belonging among employees.
- **Recognition & Motivation Patterns:** Discuss the effectiveness and frequency of employee recognition and its impact on motivation.

#### Wellness Pillar Analysis:
- **Well-being & Work-Life Balance Status:** Assess the perception of employee well-being, stress levels, and support for work-life integration.
- **Feedback & Communication Effectiveness:** Analyze the openness of communication channels and the perceived value and actionability of feedback.

#### Growth Pillar Analysis:
- **Learning & Development Opportunities:** Examine the availability and perceived value of professional development and growth paths.
- **Team Dynamics & Trust Levels:** Evaluate inter-team collaboration, psychological safety, and mutual trust within teams.
- **Autonomy & Empowerment Culture:** Assess the degree to which employees feel empowered to make decisions and have control over their work.

### 3. 🚀 STRATEGIC ACTION PLAN
Develop a phased, actionable plan with specific initiatives, estimated timelines, and responsible parties.
#### Immediate Actions (0-30 days): Quick Wins
- Identify 3-5 high-impact, low-effort initiatives that can yield quick results and build momentum.
- Example: Implement a "Kudos" system for peer recognition.
- Assign clear ownership (e.g., HR Team Lead, Department Manager).

#### Short-term Initiatives (30-90 days): Foundation Building
- Outline 3-5 medium-term projects that address key pain points identified in the lowest-scoring pillars.
- Include estimated resource requirements (budget, personnel) and clear success metrics.
- Example: Launch a "Manager as Coach" training program focusing on feedback skills.

#### Long-term Strategy (90-365 days and beyond): Sustainable Transformation
- Propose 2-3 transformational initiatives aimed at fundamental cultural shifts.
- Include considerations for change management, communication strategies, and integration into overall business strategy.
- Example: Develop a comprehensive "Employee Growth Framework" integrated with performance reviews.

### 4. 🛠️ RECOMMENDED TOOLS & RESOURCES
Suggest specific HR tech solutions, templates, and training programs.
#### HR Tech Stack:
- Recommend relevant software platforms (e.g., employee engagement surveys, performance management systems, learning management systems, internal communication tools).
- Justify why each tool is suitable for the identified challenges.

#### Templates & Frameworks:
- Suggest practical templates (e.g., 1-on-1 meeting templates, recognition program guidelines, career development plans, pulse survey questions).
- Propose relevant frameworks (e.g., OKRs for cultural initiatives, feedback models like SBI).

#### Training & Development:
- Recommend specific training programs for different employee levels (e.g., leadership development for managers, unconscious bias training for all staff, resilience workshops).
- Suggest both internal resource development and external partnerships.

### 5. 📈 SUCCESS METRICS & KPIs
Define clear, measurable Key Performance Indicators (KPIs) to track progress and demonstrate ROI.
#### Culture-Specific Metrics:
- For each main pillar (Culture, Wellness, Growth), define 2-3 specific KPIs.
- Include baseline measurements (current scores) and target improvements (e.g., increase Wellness score by 0.5 points within 6 months).
- Suggest measurement frequency (e.g., quarterly pulse surveys, annual engagement surveys, exit interviews).

#### Business ROI Indicators:
- Link culture improvements to tangible business outcomes.
- Suggest metrics like employee retention rates, absenteeism rates, productivity gains, talent acquisition success rates, and Glassdoor ratings.
- Outline a basic framework for a cost-benefit analysis of cultural investments.

### 6. 🎭 INDUSTRY-SPECIFIC CONSIDERATIONS
Provide insights specifically tailored to the {org.get('industry', 'industry')} industry.
- What are common culture challenges or unique cultural dynamics often observed in this industry?
- Highlight industry benchmarks or best practices from leading organizations in the {org.get('industry', 'industry')} sector.
- If applicable, mention any regulatory or compliance considerations that might influence HR and culture strategies in this industry.

### 7. 🚨 RISK MITIGATION
Identify potential risks to successful culture transformation and propose mitigation strategies.
#### Change Management Risks:
- Anticipate potential resistance from employees or leadership.
- Suggest strategies to build buy-in, manage expectations, and communicate transparently.

#### Implementation Risks:
- Address potential resource constraints (time, budget, personnel).
- Propose phased implementation approaches and contingency plans for unforeseen challenges.
- How to ensure leadership commitment throughout the process?

FORMAT: Use clear, hierarchical markdown headings (###, ####), bullet points, and bold text for emphasis. Ensure all recommendations are specific, measurable, achievable, relevant, and time-bound (SMART).

TONE: Professional, authoritative, empathetic, and highly actionable.
"""

        with st.spinner("🔄 Generating your comprehensive culture intelligence report... This may take a moment."):
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
                            "max_tokens": 4096,
                            "connectors": [{"id": "web_search"}] # Enable web search for more current/contextual info
                        },
                        timeout=240 # Increased timeout for comprehensive response
                    )
                    
                    if response.status_code == 200:
                        result = response.json().get("text", "No AI response returned.")
                        
                        # Display AI recommendations in an enhanced format
                        st.markdown(f"""
                        <div class="recommendation-box">
                            <h3 style="margin-top: 0; color: #2c3e50;">🤖 AI-Generated Culture Intelligence Report</h3>
                            <p style="margin-bottom: 0; color: #7f8c8d; font-size: 0.95rem;">
                                Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | 
                                Based on {len(responses)} responses across {len(set(pillar_map.values()))} culture pillars
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(result)
                        
                        # Additional Analytics
                        st.markdown("---") # Horizontal line for separation
                        st.markdown("### 📊 Additional Insights")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Response Distribution
                            response_counts = {level: 0 for level in SLIDER_LEVELS}
                            for resp_val in responses.values():
                                response_counts[resp_val] += 1
                            
                            fig_dist = px.bar(
                                x=list(response_counts.keys()),
                                y=list(response_counts.values()),
                                title="Distribution of Responses",
                                color=list(response_counts.values()),
                                color_continuous_scale="Viridis", # More appealing color scale
                                labels={"x": "Response Level", "y": "Number of Responses"},
                                text=list(response_counts.values())
                            )
                            fig_dist.update_traces(texttemplate='%{text}', textposition='outside')
                            fig_dist.update_layout(height=400, showlegend=False, xaxis_title="", yaxis_title="Count")
                            st.plotly_chart(fig_dist, use_container_width=True)
                        
                        with col2:
                            # Pillar Comparison
                            pillar_scores = {}
                            for pillar, scores_list in detailed_scores.items():
                                pillar_scores[pillar] = round(np.mean(scores_list), 2) if scores_list else 0
                            
                            # Sort pillars by score for better visualization
                            sorted_pillars = sorted(pillar_scores.items(), key=lambda item: item[1], reverse=True)
                            sorted_names = [item[0] for item in sorted_pillars]
                            sorted_values = [item[1] for item in sorted_pillars]

                            fig_pillar = px.bar(
                                x=sorted_values,
                                y=sorted_names,
                                orientation='h',
                                title="Average Scores by Sub-Pillar",
                                color=sorted_values,
                                color_continuous_scale="Plasma", # Different appealing color scale
                                labels={"x": "Average Score", "y": "Sub-Pillar"},
                                text=[f"{val:.2f}" for val in sorted_values]
                            )
                            fig_pillar.update_traces(texttemplate='%{text}', textposition='outside')
                            fig_pillar.update_layout(height=400, showlegend=False, yaxis={'categoryorder':'total ascending'})
                            st.plotly_chart(fig_pillar, use_container_width=True)
                        
                        # Assessment Summary
                        assessment_time = datetime.now() - st.session_state.assessment_start_time if st.session_state.assessment_start_time else timedelta(minutes=0)
                        
                        st.markdown(f"""
                        <div class="pillar-card" style="border-left-color: #667eea; margin-top: 2rem;">
                            <h4 style="margin-top: 0; color: #2c3e50;">📋 Assessment Summary</h4>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem; font-size: 0.95rem;">
                                <div><strong>📊 Total Questions:</strong> {len(questions)}</div>
                                <div><strong>✅ Responses Collected:</strong> {len(responses)}</div>
                                <div><strong>⏱️ Time Taken:</strong> ~{int(assessment_time.total_seconds() / 60)} minutes</div>
                                <div><strong>📈 Completion Rate:</strong> {calculate_completion_percentage()}%</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    else:
                        st.error(f"❌ API Error: Failed to generate report. Status Code: {response.status_code} - Response: {response.text}")
                        st.info("Please ensure your Cohere API key is valid and you have sufficient credits.")
                        
                except requests.exceptions.Timeout:
                    st.error("❌ The request to the AI service timed out. This might happen with large prompts or slow connections. Please try again.")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Network error while connecting to the AI service: {str(e)}. Please check your internet connection.")
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred during AI report generation: {str(e)}. Please try again or contact support.")
            else:
                st.warning("⚠️ **Cohere API key not found in Streamlit secrets.** AI recommendations cannot be generated. Please configure your API key to enable this feature.")
                
                # Fallback static recommendations for development/no API key scenario
                st.markdown("""
                <div class="recommendation-box" style="background: linear-gradient(135deg, #fceabb 0%, #f8b500 100%); border-left-color: #e09400;">
                    <h3 style="margin-top: 0; color: #2c3e50;">⚠️ Basic Culture Analysis (AI Offline)</h3>
                    <p style="margin-bottom: 0; color: #7f8c8d; font-size: 0.95rem;">
                        The AI recommendation engine is currently offline or the API key is not configured.
                        Here are some general observations based on your scores:
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Simple analysis based on scores
                if overall_score >= 3.5:
                    st.success("🌟 Your organization appears to have **excellent cultural health** across most dimensions! Keep nurturing this positive environment.")
                elif overall_score >= 2.5:
                    st.info("👍 Your organization has a **solid cultural foundation** with clear strengths, but there's room for targeted improvements in certain areas.")
                else:
                    st.warning("⚠️ Your organization has **significant opportunities for cultural enhancement**. Addressing key areas will lead to substantial positive impact.")
                
                # Basic recommendations focusing on the lowest score
                if avg_scores:
                    lowest_score_pillar = min(avg_scores.items(), key=lambda x: x[1])[0]
                    lowest_pillar_score = min(avg_scores.items(), key=lambda x: x[1])[1]
                    
                    st.markdown(f"""
                    ---
                    **💡 Priority Focus Area:** Your analysis indicates **{lowest_score_pillar}** is a primary area for improvement (Average Score: {lowest_pillar_score}/4.0).
                    
                    **General Recommendations to Consider:**
                    * **Targeted Interventions:** Deep dive into specific questions related to **{lowest_score_pillar.lower()}** to understand root causes. Conduct anonymous surveys or focus groups.
                    * **Leadership Alignment:** Ensure leadership is visibly committed to improving **{lowest_score_pillar.lower()}** and actively participates in initiatives.
                    * **Communication Strategy:** Develop clear and consistent communication plans for any new initiatives, explaining the 'why' and expected impact.
                    * **Continuous Feedback:** Implement regular, lightweight pulse surveys to track progress on key culture indicators and make agile adjustments.
                    * **Resource Allocation:** Identify and allocate necessary resources (time, budget, personnel) to support cultural initiatives.
                    * **Celebrate Small Wins:** Recognize and communicate progress, no matter how small, to maintain momentum and morale.
                    """)
                else:
                    st.info("Please complete the assessment to get initial insights.")

    except Exception as e:
        st.error(f"❌ An unhandled error occurred in the results page: {str(e)}")
        st.info("Please refresh the page and try again. If the issue persists, contact support.")
    
    # Action Buttons (only Retake Assessment)
    st.markdown("---") # Horizontal line for separation
    st.markdown("### 🔄 Ready for Your Next Step?")
    
    col_recenter, _, _ = st.columns([1, 1, 1]) # Use columns to center
    with col_recenter:
        if st.button("🔄 **Retake Assessment**", use_container_width=True):
            # Reset session state completely
            for key in st.session_state.keys():
                del st.session_state[key]
            st.session_state.page = "intro" # Go back to intro
            st.rerun()
    
    # Enhanced Brand Footer
    st.markdown("""
    <div class="brand-footer">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <p style="margin: 0; font-size: 1rem; font-weight: 600;">Thrivya Culture Intelligence Platform</p>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.8;">Crafted by Hemaang Patkar</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
