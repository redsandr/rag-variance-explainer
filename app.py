import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st
from config import config
from llm import LLMClient
from rag import answer_question


st.set_page_config(
    page_title="RAG Variance Explainer",
    page_icon="\U0001f4ca",
    layout="wide",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }

    * { font-family: 'Inter', sans-serif; }

    .stApp { background: #0F0F0F; }

    .app-container {
        max-width: 1440px;
        margin: 0 auto;
        padding: 0 24px;
    }

    .top-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 0;
        border-bottom: 1px solid #2D2D2D;
        margin-bottom: 24px;
    }
    .top-header .brand {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .top-header .brand-icon {
        width: 38px;
        height: 38px;
        background: linear-gradient(135deg, #8B5CF6, #A78BFA);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 24px rgba(139, 92, 246, 0.25);
        flex-shrink: 0;
    }
    .top-header .brand-icon svg { display: block; }
    .top-header .brand-text h1 {
        font-size: 1.15rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -0.01em;
    }
    .top-header .brand-text .breadcrumb {
        font-size: 0.72rem;
        font-weight: 400;
        margin: 1px 0 0 0;
    }
    .top-header .brand-text .breadcrumb,
    .top-header .brand-text .breadcrumb span { color: #6B7280; }
    .top-header .brand-text .breadcrumb .active { color: #9CA3AF; }

    .dashboard-grid {
        display: grid;
        grid-template-columns: 1fr 260px;
        gap: 24px;
        align-items: start;
    }
    .main-col { min-width: 0; }
    .right-col { position: sticky; top: 24px; }

    .hero-card {
        background: linear-gradient(135deg, #1A1A1A 0%, #242424 100%);
        border: 1px solid #2D2D2D;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    }
    .hero-card .hero-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #6B7280;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .hero-card .hero-input-row { display: flex; gap: 12px; }

    .kpi-panel { margin-bottom: 24px; }
    .kpi-panel .panel-title {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #6B7280;
        margin-bottom: 12px;
    }
    .kpi-stack { display: flex; flex-direction: column; gap: 10px; }
    .kpi-stack-card {
        background: #1A1A1A;
        border: 1px solid #2D2D2D;
        border-radius: 12px;
        padding: 14px 16px;
        transition: border-color 0.2s ease;
    }
    .kpi-stack-card:hover {
        border-color: #8B5CF6;
        box-shadow: 0 0 24px rgba(139, 92, 246, 0.08);
    }
    .kpi-stack-card .kpi-row-label {
        font-size: 0.7rem;
        font-weight: 500;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }
    .kpi-stack-card .kpi-row-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.2;
    }
    .kpi-stack-card .kpi-row-sub {
        font-size: 0.7rem;
        color: #6B7280;
        margin-top: 2px;
    }
    .kpi-stack-card .kpi-row-value .purple { color: #A78BFA; }
    .kpi-stack-card .kpi-row-value .green { color: #10B981; }

    .about-card {
        background: #1A1A1A;
        border: 1px solid #2D2D2D;
        border-radius: 12px;
        padding: 16px;
    }
    .about-card .about-title {
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #6B7280;
        margin-bottom: 8px;
    }
    .about-card .about-text {
        font-size: 0.78rem;
        color: #6B7280;
        line-height: 1.6;
    }

    .example-row {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 16px;
        align-items: center;
    }
    .example-row .hint {
        font-size: 0.75rem;
        color: #6B7280;
        font-weight: 500;
    }

    .answer-section { margin-top: 4px; }

    .answer-card {
        background: linear-gradient(135deg, #1A1A1A 0%, #242424 100%);
        border: 1px solid #2D2D2D;
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    .answer-card .answer-head {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 14px;
    }
    .answer-card .answer-head h3 {
        font-size: 0.95rem;
        font-weight: 600;
        color: #FFFFFF;
        margin: 0;
    }
    .answer-card .answer-head .badge {
        font-size: 0.62rem;
        font-weight: 600;
        background: rgba(139, 92, 246, 0.15);
        color: #A78BFA;
        padding: 3px 10px;
        border-radius: 20px;
        border: 1px solid rgba(139, 92, 246, 0.2);
    }
    .answer-card .answer-head .badge.green {
        background: rgba(16, 185, 129, 0.12);
        color: #10B981;
        border-color: rgba(16, 185, 129, 0.2);
    }
    .answer-card .answer-body {
        font-size: 0.88rem;
        line-height: 1.7;
        color: #D1D5DB;
    }
    .answer-card .answer-body ul { padding-left: 1.25rem; }
    .answer-card .answer-body li { margin-bottom: 6px; }
    .answer-card .answer-body strong { color: #F9FAFB; }

    .sources-panel { margin-top: 8px; }
    .sources-panel .sources-head {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 14px;
    }
    .sources-panel .sources-head h4 {
        font-size: 0.82rem;
        font-weight: 600;
        color: #9CA3AF;
        margin: 0;
    }
    .sources-panel .sources-head .count-badge {
        font-size: 0.65rem;
        background: #242424;
        color: #6B7280;
        padding: 2px 10px;
        border-radius: 20px;
        border: 1px solid #2D2D2D;
    }

    .source-grid { display: flex; flex-direction: column; gap: 10px; }
    .source-card {
        background: #1A1A1A;
        border: 1px solid #2D2D2D;
        border-left: 3px solid #8B5CF6;
        border-radius: 10px;
        padding: 14px 16px;
        transition: border-color 0.2s ease;
    }
    .source-card:hover {
        border-color: #8B5CF6;
        box-shadow: 0 0 24px rgba(139, 92, 246, 0.06);
    }
    .source-card .meta-row {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 8px;
    }
    .source-card .ticker-tag {
        font-size: 0.65rem;
        font-weight: 700;
        background: rgba(139, 92, 246, 0.12);
        color: #A78BFA;
        padding: 2px 10px;
        border-radius: 4px;
        border: 1px solid rgba(139, 92, 246, 0.15);
    }
    .source-card .form-tag {
        font-size: 0.65rem;
        font-weight: 500;
        background: rgba(156, 163, 175, 0.1);
        color: #9CA3AF;
        padding: 2px 8px;
        border-radius: 4px;
    }
    .source-card .date-tag { font-size: 0.65rem; color: #6B7280; }
    .source-card .score-tag {
        font-size: 0.65rem;
        font-weight: 600;
        padding: 2px 10px;
        border-radius: 12px;
        margin-left: auto;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .sc-high { background: rgba(16, 185, 129, 0.12); color: #10B981; }
    .sc-mid { background: rgba(245, 158, 11, 0.12); color: #F59E0B; }
    .sc-low { background: rgba(239, 68, 68, 0.12); color: #EF4444; }
    .source-card .chunk-text {
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 0.72rem;
        line-height: 1.55;
        color: #9CA3AF;
        white-space: pre-wrap;
        overflow-x: auto;
    }

    .empty-state {
        text-align: center;
        padding: 48px 24px;
    }
    .empty-state .empty-icon {
        margin-bottom: 12px;
        display: flex;
        justify-content: center;
    }
    .empty-state .empty-title {
        font-size: 1rem;
        font-weight: 600;
        color: #D1D5DB;
        margin-bottom: 6px;
    }
    .empty-state .empty-desc {
        font-size: 0.82rem;
        color: #6B7280;
        max-width: 400px;
        margin: 0 auto;
        line-height: 1.6;
    }

    .compare-vs {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
    }
    .compare-vs .vs-badge {
        font-size: 0.65rem;
        font-weight: 700;
        color: #6B7280;
        background: #242424;
        padding: 4px 12px;
        border-radius: 20px;
        border: 1px solid #2D2D2D;
    }
    .compare-vs h3 {
        font-size: 0.95rem;
        font-weight: 600;
        color: #FFFFFF;
        margin: 0;
    }
    .compare-label {
        font-size: 0.75rem;
        font-weight: 500;
        color: #6B7280;
        margin-bottom: 6px;
    }

    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
        border: none;
        font-weight: 600;
        font-size: 0.85rem;
        height: 44px;
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.2);
        transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.1s ease;
    }
    .stButton button[kind="primary"]:hover {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
        box-shadow: 0 0 30px rgba(139, 92, 246, 0.3);
    }
    .stButton button[kind="primary"]:focus-visible {
        outline: 2px solid #A78BFA;
        outline-offset: 2px;
    }
    .stButton button[kind="secondary"] {
        border: 1px solid #2D2D2D;
        background: transparent;
        color: #9CA3AF;
        font-size: 0.72rem;
        height: auto;
        padding: 5px 14px;
        border-radius: 20px;
        transition: border-color 0.2s ease, color 0.2s ease;
        font-weight: 500;
    }
    .stButton button[kind="secondary"]:hover {
        border-color: #8B5CF6;
        color: #A78BFA;
        background: rgba(139, 92, 246, 0.06);
    }
    .stButton button[kind="secondary"]:focus-visible {
        outline: 2px solid #A78BFA;
        outline-offset: 2px;
    }

    div[data-testid="stSidebar"] {
        background: #0A0A0A !important;
        border-right: 1px solid #2D2D2D !important;
        min-width: 64px !important;
        width: 64px !important;
    }
    div[data-testid="stSidebar"] .sidebar-content { display: none; }
    div[data-testid="stSidebarCollapsedButton"] { display: none; }

    .sidebar-nav {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding-top: 20px;
        gap: 6px;
    }
    .sidebar-nav .nav-item {
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        cursor: pointer;
        transition: background 0.15s ease, color 0.15s ease;
        color: #4B5563;
        position: relative;
        border: none;
        background: transparent;
        padding: 0;
    }
    .sidebar-nav .nav-item:hover {
        background: rgba(139, 92, 246, 0.1);
        color: #A78BFA;
    }
    .sidebar-nav .nav-item:focus-visible {
        outline: 2px solid #A78BFA;
        outline-offset: 2px;
    }
    .sidebar-nav .nav-item.active {
        background: rgba(139, 92, 246, 0.15);
        color: #A78BFA;
    }
    .sidebar-nav .nav-item svg { display: block; }
    .sidebar-nav .nav-divider {
        width: 24px;
        height: 1px;
        background: #2D2D2D;
        margin: 6px 0;
    }

    .stTextInput input {
        background: #242424 !important;
        border: 1px solid #2D2D2D !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        font-size: 0.88rem !important;
        padding: 0.6rem 1rem !important;
        height: 44px;
        font-family: 'Inter', sans-serif !important;
        transition: border-color 0.2s ease;
    }
    .stTextInput input:focus {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15) !important;
    }
    .stTextInput input::placeholder { color: #4B5563 !important; }

    .stSelectbox div[data-baseweb="select"] > div {
        background: #242424 !important;
        border: 1px solid #2D2D2D !important;
        border-radius: 8px !important;
        color: #D1D5DB !important;
        transition: border-color 0.2s ease;
    }
    .stSelectbox div[data-baseweb="select"] > div:hover {
        border-color: #8B5CF6 !important;
    }

    div.stSlider [data-baseweb="slider"] div { background: #2D2D2D !important; }
    div.stSlider [data-baseweb="slider"] div[role="slider"] { background: #8B5CF6 !important; }
    div.stSlider [data-baseweb="slider"] div[role="slider"]:focus-visible {
        outline: 2px solid #A78BFA;
        outline-offset: 2px;
    }

    .stCheckbox label { color: #9CA3AF !important; font-size: 0.82rem !important; }
    .stCheckbox label:hover { color: #D1D5DB !important; }

    hr { border-color: #2D2D2D !important; margin: 12px 0 !important; }

    .stAlert {
        background: #1A1A1A;
        border: 1px solid #2D2D2D;
        border-radius: 10px;
    }
    .stAlert [data-testid="stAlertContainer"] { background: transparent !important; }
    .stAlert [data-testid="stAlertContainer"] div:first-child { color: #D1D5DB !important; }

    .stStatusWidget {
        background: #1A1A1A !important;
        border: 1px solid #2D2D2D !important;
        border-radius: 10px !important;
    }

    .stSpinner > div { border-color: #8B5CF6 !important; }

    div.stExpander {
        background: transparent;
        border: none;
    }
    div.stExpander > details {
        background: transparent;
        border: 1px solid #2D2D2D;
        border-radius: 10px;
    }
    div.stExpander > details > summary {
        background: transparent;
        color: #9CA3AF;
        font-size: 0.82rem;
        font-weight: 500;
        padding: 10px 14px;
        border-radius: 10px;
        cursor: pointer;
    }
    div.stExpander > details > summary:hover { color: #D1D5DB; }
    div.stExpander > details > summary:focus-visible {
        outline: 2px solid #A78BFA;
        outline-offset: 2px;
    }
</style>
""", unsafe_allow_html=True)

LOGO_SVG = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>'
    '<line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/>'
    '<line x1="15" y1="21" x2="15" y2="9"/>'
    '</svg>'
)

st.markdown(
    f'<div class="app-container">'
    f'<div class="top-header">'
    f'<div class="brand">'
    f'<div class="brand-icon" role="img" aria-label="RAG Variance Explainer logo">{LOGO_SVG}</div>'
    f'<div class="brand-text">'
    f'<h1>RAG Variance Explainer</h1>'
    f'<p class="breadcrumb">Dashboard <span>/</span> <span class="active">Financial Analysis</span></p>'
    f'</div></div>'
    f'</div>',
    unsafe_allow_html=True,
)


@st.cache_resource
def get_llm():
    return LLMClient()


SIDEBAR_ICONS = {
    "dashboard": (
        "dashboard",
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>'
        '<rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>'
        '</svg>'
    ),
    "analytics": (
        "analytics",
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>'
        '<line x1="6" y1="20" x2="6" y2="14"/>'
        '</svg>'
    ),
    "ai": (
        "ai",
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 '
        '7 14.14 2 9.27 8.91 8.26 12 2"/>'
        '</svg>'
    ),
    "docs": (
        "docs",
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
        '<polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/>'
        '<line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>'
        '</svg>'
    ),
    "settings": (
        "settings",
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 '
        '2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 '
        '2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 '
        '2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 '
        '2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 '
        '2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 '
        '2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 '
        '2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 '
        '2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>'
        '</svg>'
    ),
}

with st.sidebar:
    sidebar_html = '<div class="sidebar-nav" role="navigation" aria-label="Main navigation">'
    sidebar_html += (
        f'<button class="nav-item active" title="Dashboard" aria-label="Dashboard">'
        f'{SIDEBAR_ICONS["dashboard"][1]}</button>'
    )
    sidebar_html += (
        f'<button class="nav-item" title="Analytics" aria-label="Analytics">'
        f'{SIDEBAR_ICONS["analytics"][1]}</button>'
    )
    sidebar_html += (
        f'<button class="nav-item" title="AI Analysis" aria-label="AI Analysis">'
        f'{SIDEBAR_ICONS["ai"][1]}</button>'
    )
    sidebar_html += '<div class="nav-divider" role="separator"></div>'
    sidebar_html += (
        f'<button class="nav-item" title="Documents" aria-label="Documents">'
        f'{SIDEBAR_ICONS["docs"][1]}</button>'
    )
    sidebar_html += (
        f'<button class="nav-item" title="Settings" aria-label="Settings">'
        f'{SIDEBAR_ICONS["settings"][1]}</button>'
    )
    sidebar_html += '</div>'
    st.markdown(sidebar_html, unsafe_allow_html=True)

st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
st.markdown('<div class="main-col">', unsafe_allow_html=True)

SEARCH_SVG = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>'
    '</svg>'
)

st.markdown(
    f'<div class="hero-card">'
    f'<div class="hero-label">{SEARCH_SVG} Ask a Question</div>'
    f'<div class="hero-input-row">',
    unsafe_allow_html=True,
)

col_q, col_btn = st.columns([5, 1])
with col_q:
    question = st.text_input(
        "Question",
        placeholder="e.g. Why did Chipotle's labor costs change?",
        label_visibility="collapsed",
        key="question_input",
    )
with col_btn:
    ask = st.button("Analyze", type="primary", use_container_width=True)

EXAMPLE_QUESTIONS = [
    "Why did Chipotle's labor costs change?",
    "What drove Darden's revenue changes?",
    "How did wage inflation affect Chipotle?",
    "Why did CBRL's operating costs change?",
]

st.markdown('<div class="example-row">', unsafe_allow_html=True)
st.markdown('<span class="hint">Try:</span>', unsafe_allow_html=True)
for q in EXAMPLE_QUESTIONS:
    if st.button(q, key=f"ex_{q[:20]}", use_container_width=False, type="secondary"):
        st.session_state.pending_question = q
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

ticker_map = {
    "All": None,
    "CMG (Chipotle)": "CMG",
    "DRI (Darden)": "DRI",
    "CBRL (Cracker Barrel)": "CBRL",
}

filter_col, topk_col = st.columns(2)
with filter_col:
    ticker_filter = st.selectbox(
        "Company",
        options=["All", "CMG (Chipotle)", "DRI (Darden)", "CBRL (Cracker Barrel)"],
        index=0,
        help="Filter sources by company ticker",
    )
with topk_col:
    top_k = st.slider(
        "Source chunks",
        min_value=1, max_value=15, value=5,
        help="Number of retrieved chunks to include",
    )

compare = st.checkbox(
    "Side-by-side: with vs without cross-encoder",
    value=False,
    help="Compare retrieval with and without cross-encoder re-ranking",
)

if "pending_question" in st.session_state:
    st.session_state.question_input = st.session_state.pop("pending_question")

if ask and question.strip():
    ticker = ticker_map[ticker_filter]

    def run_with_progress(fn, label):
        status = st.status(label, expanded=True)
        def on_progress(_phase, msg):
            status.update(label=msg, state="running")
        try:
            result = fn(on_progress=on_progress)
            status.update(label="Complete", state="complete")
            return result
        except Exception as e:
            status.update(label=f"Error: {e}", state="error")
            raise

    try:
        if compare:
            orig = config.cross_encoder_enabled
            config.cross_encoder_enabled = False
            before = run_with_progress(
                lambda on_progress: answer_question(
                    question, ticker_filter=ticker, top_k=top_k, llm=get_llm(),
                    on_progress=on_progress),
                "Without cross-encoder",
            )
            config.cross_encoder_enabled = True
            after = run_with_progress(
                lambda on_progress: answer_question(
                    question, ticker_filter=ticker, top_k=top_k, llm=get_llm(),
                    on_progress=on_progress),
                "With cross-encoder",
            )
            config.cross_encoder_enabled = orig
            st.session_state.last_result = {"compare": True, "before": before, "after": after}
        else:
            result = run_with_progress(
                lambda on_progress: answer_question(
                    question, ticker_filter=ticker, top_k=top_k, llm=get_llm(),
                    on_progress=on_progress),
                "Analyzing filings",
            )
            st.session_state.last_result = {"compare": False, **result}
    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.session_state.pop("last_result", None)

    st.rerun()

elif ask and not question.strip():
    st.warning("Please enter a question.")

def _score_class(score: float) -> str:
    if score >= 0.7:
        return "sc-high"
    elif score >= 0.4:
        return "sc-mid"
    return "sc-low"

def _score_icon(score: float) -> str:
    if score >= 0.7:
        return "\u25B2"
    elif score >= 0.4:
        return "\u25C6"
    return "\u25BC"

def _render_sources(sources):
    if not sources:
        return
    st.markdown(
        f'<div class="sources-panel">'
        f'<div class="sources-head"><h4>Source Chunks</h4>'
        f'<span class="count-badge">{len(sources)}</span></div>'
        f'<div class="source-grid">',
        unsafe_allow_html=True,
    )
    for src in sources:
        meta = src["metadata"]
        score = src.get("hybrid_score", src.get("relevance", 0))
        score_cls = _score_class(score)
        text_preview = src["text"][:400]
        if len(src["text"]) > 400:
            text_preview += "..."
        st.markdown(
            f'<div class="source-card">'
            f'<div class="meta-row">'
            f'<span class="ticker-tag">{meta["ticker"]}</span>'
            f'<span class="form-tag">{meta["form"]}</span>'
            f'<span class="date-tag">{meta["filing_date"]}</span>'
            f'<span class="score-tag {score_cls}">{_score_icon(score)} {score:.2f}</span>'
            f'</div>'
            f'<div class="chunk-text">{text_preview}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div></div>', unsafe_allow_html=True)

def _render_answer(answer_text, label="Answer", badge_type=""):
    badge_cls = f'badge {badge_type}' if badge_type else 'badge'
    st.markdown(
        f'<div class="answer-card">'
        f'<div class="answer-head"><h3>{label}</h3>'
        f'<span class="{badge_cls}">sourced</span></div>'
        f'<div class="answer-body">{answer_text}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="answer-section">', unsafe_allow_html=True)

if "last_result" in st.session_state:
    _r = st.session_state.last_result
    if _r.get("compare"):
        before, after = _r["before"], _r["after"]
        st.markdown(
            '<div class="compare-vs"><h3>Comparison</h3>'
            '<span class="vs-badge">VS</span></div>',
            unsafe_allow_html=True,
        )
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown('<p class="compare-label">Bi-Encoder Only</p>', unsafe_allow_html=True)
            _render_answer(before["answer"], label="Before", badge_type="")
            with st.expander(f"Sources ({len(before['sources'])})"):
                _render_sources(before["sources"])
        with col_right:
            st.markdown('<p class="compare-label">With Cross-Encoder Reranking</p>', unsafe_allow_html=True)
            _render_answer(after["answer"], label="After", badge_type="green")
            with st.expander(f"Sources ({len(after['sources'])})"):
                _render_sources(after["sources"])
    else:
        _render_answer(_r["answer"], label="AI Analysis", badge_type="green")
        with st.expander(f"Source Chunks ({len(_r['sources'])})", expanded=True):
            _render_sources(_r["sources"])
else:
    if not (ask and question.strip()):
        EMPTY_SVG = (
            '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#4B5563" '
            'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>'
            '</svg>'
        )
        st.markdown(
            f'<div class="empty-state" role="status">'
            f'<div class="empty-icon" aria-hidden="true">{EMPTY_SVG}</div>'
            f'<div class="empty-title">Ask a question to get started</div>'
            f'<div class="empty-desc">'
            f'Query financial variance drivers from SEC EDGAR MD&A sections '
            f'across Chipotle, Darden Restaurants, and Cracker Barrel.'
            f'</div></div>',
            unsafe_allow_html=True,
        )

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="right-col">', unsafe_allow_html=True)

st.markdown(
    '<div class="kpi-panel">'
    '<div class="panel-title">System Overview</div>'
    '<div class="kpi-stack">'
    '<div class="kpi-stack-card">'
    '<div class="kpi-row-label">Companies</div>'
    '<div class="kpi-row-value">3</div>'
    '<div class="kpi-row-sub">CMG &middot; DRI &middot; CBRL</div></div>'
    '<div class="kpi-stack-card">'
    '<div class="kpi-row-label">Filings Indexed</div>'
    '<div class="kpi-row-value">24</div>'
    '<div class="kpi-row-sub">10-K &amp; 10-Q combined</div></div>'
    '<div class="kpi-stack-card">'
    '<div class="kpi-row-label">Knowledge Base</div>'
    '<div class="kpi-row-value">432</div>'
    '<div class="kpi-row-sub">MD&A text chunks</div></div>'
    '<div class="kpi-stack-card">'
    '<div class="kpi-row-label">Retrieval MRR</div>'
    '<div class="kpi-row-value"><span class="purple">0.66</span></div>'
    '<div class="kpi-row-sub">+28% from baseline</div></div>'
    '<div class="kpi-stack-card">'
    '<div class="kpi-row-label">Faithfulness</div>'
    '<div class="kpi-row-value"><span class="green">65.8%</span></div>'
    '<div class="kpi-row-sub">strict weighted score</div></div>'
    '</div></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="about-card">'
    '<div class="about-title">About</div>'
    '<div class="about-text">'
    'Retrieves MD&A sections from SEC EDGAR filings and generates '
    'sourced answers about financial variance drivers using a RAG pipeline '
    'with cross-encoder re-ranking and configurable retrieval settings.'
    '</div></div>',
    unsafe_allow_html=True,
)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
