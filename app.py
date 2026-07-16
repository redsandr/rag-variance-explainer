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
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

    * { font-family: 'IBM Plex Sans', sans-serif; }

    .stApp {
        background: #020617;
    }

    .main-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 1.5rem 0 0.25rem 0;
    }
    .main-header .logo-icon {
        width: 42px;
        height: 42px;
        background: linear-gradient(135deg, #3B82F6, #22C55E);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        flex-shrink: 0;
    }
    .main-header h1 {
        font-size: 1.6rem;
        font-weight: 600;
        color: #F8FAFC;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .main-header .subtitle {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 400;
        margin: 0;
    }

    .kpi-row {
        display: flex;
        gap: 16px;
        margin: 1.25rem 0 1.5rem 0;
        flex-wrap: wrap;
    }
    .kpi-card {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 0.85rem 1.25rem;
        min-width: 130px;
        flex: 1;
    }
    .kpi-card .kpi-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748B;
        font-weight: 500;
        margin-bottom: 4px;
    }
    .kpi-card .kpi-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.2;
    }
    .kpi-card .kpi-value .accent-green { color: #22C55E; }
    .kpi-card .kpi-value .accent-blue { color: #3B82F6; }
    .kpi-card .kpi-sub {
        font-size: 0.75rem;
        color: #64748B;
        margin-top: 2px;
    }

    .search-area {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .search-area .search-label {
        font-size: 0.85rem;
        font-weight: 500;
        color: #94A3B8;
        margin-bottom: 10px;
    }

    .example-chips {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 12px;
    }
    .example-chips .chip-label {
        font-size: 0.78rem;
        color: #64748B;
        margin-right: 4px;
        align-self: center;
    }

    .answer-section {
        margin-top: 0.5rem;
    }
    .answer-card {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .answer-card h3 {
        font-size: 1rem;
        font-weight: 600;
        color: #F8FAFC;
        margin: 0 0 0.75rem 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .answer-card h3 .badge {
        font-size: 0.65rem;
        background: rgba(34, 197, 94, 0.15);
        color: #22C55E;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 500;
    }
    .answer-card .answer-content {
        font-size: 0.92rem;
        line-height: 1.7;
        color: #E2E8F0;
    }
    .answer-card .answer-content ul { padding-left: 1.25rem; }
    .answer-card .answer-content li { margin-bottom: 6px; }
    .answer-card .answer-content strong { color: #F8FAFC; }

    .sources-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 1rem 0 0.75rem 0;
    }
    .sources-header h4 {
        font-size: 0.9rem;
        font-weight: 600;
        color: #94A3B8;
        margin: 0;
    }
    .sources-header .count-badge {
        font-size: 0.7rem;
        background: #1E293B;
        color: #64748B;
        padding: 2px 8px;
        border-radius: 10px;
    }

    .source-grid {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .source-card {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-left: 3px solid #3B82F6;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        transition: border-color 0.15s ease;
    }
    .source-card:hover {
        border-color: #3B82F6;
    }
    .source-card .meta-row {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 6px;
    }
    .source-card .ticker-tag {
        font-size: 0.7rem;
        font-weight: 600;
        background: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        padding: 2px 8px;
        border-radius: 4px;
    }
    .source-card .form-tag {
        font-size: 0.7rem;
        font-weight: 500;
        background: rgba(148, 163, 184, 0.12);
        color: #94A3B8;
        padding: 2px 8px;
        border-radius: 4px;
    }
    .source-card .date-tag {
        font-size: 0.7rem;
        color: #64748B;
    }
    .source-card .score-tag {
        font-size: 0.7rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        margin-left: auto;
    }
    .score-high { color: #22C55E; }
    .score-mid { color: #EAB308; }
    .score-low { color: #EF4444; }
    .source-card .chunk-text {
        font-family: 'IBM Plex Mono', 'Courier New', monospace;
        font-size: 0.78rem;
        line-height: 1.55;
        color: #CBD5E1;
        white-space: pre-wrap;
        overflow-x: auto;
    }
    .source-card .chunk-text .highlight {
        background: rgba(59, 130, 246, 0.15);
        padding: 0 2px;
        border-radius: 2px;
    }

    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #64748B;
    }
    .empty-state .empty-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
        opacity: 0.5;
    }
    .empty-state .empty-title {
        font-size: 1.05rem;
        font-weight: 500;
        color: #94A3B8;
        margin-bottom: 6px;
    }
    .empty-state .empty-desc {
        font-size: 0.85rem;
        color: #64748B;
    }

    .compare-section {
        margin-top: 0.5rem;
    }
    .compare-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1rem;
    }
    .compare-header .vs-badge {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748B;
        background: #1E293B;
        padding: 4px 10px;
        border-radius: 6px;
    }

    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        border: none;
        font-weight: 500;
        height: 44px;
    }
    .stButton button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
    }
    .stButton button[kind="secondary"] {
        border: 1px solid #334155;
        background: transparent;
        color: #94A3B8;
        font-size: 0.78rem;
        height: auto;
        padding: 4px 12px;
        border-radius: 20px;
        transition: all 0.15s ease;
    }
    .stButton button[kind="secondary"]:hover {
        border-color: #3B82F6;
        color: #60A5FA;
        background: rgba(59, 130, 246, 0.08);
    }

    div[data-testid="stSidebar"] {
        background: #0A0F20;
        border-right: 1px solid #1E293B;
    }
    div[data-testid="stSidebar"] .sidebar-content {
        padding: 1.25rem 1rem;
    }
    .sidebar-section-title {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #475569;
        font-weight: 600;
        margin: 1.25rem 0 0.75rem 0;
    }
    .sidebar-section-title:first-child { margin-top: 0; }

    div[data-testid="stMetricValue"] {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #64748B !important;
    }

    .stStatusWidget {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 8px;
    }

    .stTextInput input {
        background: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #F8FAFC !important;
        font-size: 0.92rem !important;
        padding: 0.65rem 1rem !important;
        height: 44px;
    }
    .stTextInput input:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }
    .stTextInput input::placeholder {
        color: #475569 !important;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        background: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }

    div.stSlider [data-baseweb="slider"] div {
        background: #334155 !important;
    }

    hr {
        border-color: #1E293B !important;
        margin: 1rem 0 !important;
    }

    .stAlert {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 8px;
    }
    .stAlert [data-testid="stAlertContainer"] {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-header">'
    '<div class="logo-icon">\U0001f4ca</div>'
    '<div><h1>RAG Variance Explainer</h1>'
    '<p class="subtitle">AI-powered financial variance analysis from SEC filings</p></div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="kpi-row">'
    '<div class="kpi-card"><div class="kpi-label">Companies</div><div class="kpi-value">3</div><div class="kpi-sub">CMG · DRI · CBRL</div></div>'
    '<div class="kpi-card"><div class="kpi-label">Filings Indexed</div><div class="kpi-value">24</div><div class="kpi-sub">10-K &amp; 10-Q</div></div>'
    '<div class="kpi-card"><div class="kpi-label">Knowledge Chunks</div><div class="kpi-value">432</div><div class="kpi-sub">MD&A sections</div></div>'
    '<div class="kpi-card"><div class="kpi-label">Retrieval MRR</div><div class="kpi-value"><span class="accent-green">0.66</span></div><div class="kpi-sub">+28% from baseline</div></div>'
    '<div class="kpi-card"><div class="kpi-label">Faithfulness</div><div class="kpi-value"><span class="accent-blue">65.8%</span></div><div class="kpi-sub">strict weighted</div></div>'
    '</div>',
    unsafe_allow_html=True,
)


@st.cache_resource
def get_llm():
    return LLMClient()

with st.sidebar:
    st.markdown('<div class="sidebar-section-title">Filters</div>', unsafe_allow_html=True)

    ticker_filter = st.selectbox(
        "Company",
        options=["All", "CMG (Chipotle)", "DRI (Darden)", "CBRL (Cracker Barrel)"],
        index=0,
        help="Filter sources by company ticker",
    )

    top_k = st.slider(
        "Source chunks",
        min_value=1,
        max_value=15,
        value=5,
        help="Number of retrieved chunks to include",
    )

    compare = st.checkbox(
        "Side-by-side comparison",
        value=False,
        help="Show retrieval with and without cross-encoder re-ranking",
    )

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">About</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:0.8rem;color:#64748B;line-height:1.6;">'
        'Retrieves MD&A sections from SEC EDGAR filings '
        '(Chipotle, Darden Restaurants, Cracker Barrel) '
        'and generates sourced answers about financial variance drivers.</p>',
        unsafe_allow_html=True,
    )

ticker_map = {
    "All": None,
    "CMG (Chipotle)": "CMG",
    "DRI (Darden)": "DRI",
    "CBRL (Cracker Barrel)": "CBRL",
}

EXAMPLE_QUESTIONS = [
    "Why did Chipotle's labor costs change?",
    "What drove Darden's revenue changes?",
    "How did wage inflation affect Chipotle?",
    "Why did CBRL's operating costs change?",
]

if "pending_question" in st.session_state:
    st.session_state.question_input = st.session_state.pop("pending_question")

st.markdown('<div class="search-area">', unsafe_allow_html=True)
st.markdown(
    '<div class="search-label">\U0001f50d Ask a question about financial variance drivers</div>',
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

st.markdown('<div class="example-chips">', unsafe_allow_html=True)
st.markdown('<span class="chip-label">Try asking:</span>', unsafe_allow_html=True)
for q in EXAMPLE_QUESTIONS:
    if st.button(q, key=f"ex_{q[:20]}", use_container_width=False, type="secondary"):
        st.session_state.pending_question = q
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

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
    st.warning("Please enter a question.", icon="⚠️")

def _score_class(score: float) -> str:
    if score >= 0.7:
        return "score-high"
    elif score >= 0.4:
        return "score-mid"
    return "score-low"

def _render_sources(sources, label="Source Chunks"):
    if not sources:
        return
    st.markdown(
        f'<div class="sources-header"><h4>{label}</h4>'
        f'<span class="count-badge">{len(sources)}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="source-grid">', unsafe_allow_html=True)
    for i, src in enumerate(sources):
        meta = src["metadata"]
        score = src.get("hybrid_score", src.get("relevance", 0))
        score_cls = _score_class(score)
        text_preview = src["text"][:500]
        if len(src["text"]) > 500:
            text_preview += "..."
        st.markdown(
            f'<div class="source-card">'
            f'<div class="meta-row">'
            f'<span class="ticker-tag">{meta["ticker"]}</span>'
            f'<span class="form-tag">{meta["form"]}</span>'
            f'<span class="date-tag">{meta["filing_date"]}</span>'
            f'<span class="score-tag {score_cls}">score: {score:.2f}</span>'
            f'</div>'
            f'<div class="chunk-text">{text_preview}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

def _render_answer(answer_text):
    st.markdown(
        f'<div class="answer-card">'
        f'<h3>Answer <span class="badge">sourced</span></h3>'
        f'<div class="answer-content">{answer_text}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

if "last_result" in st.session_state:
    _r = st.session_state.last_result
    st.markdown('<div class="answer-section">', unsafe_allow_html=True)

    if _r.get("compare"):
        before, after = _r["before"], _r["after"]
        st.markdown(
            '<div class="compare-header">'
            '<h3 style="font-size:1rem;font-weight:600;color:#F8FAFC;margin:0;">Comparison</h3>'
            '<span class="vs-badge">VS</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown(
                '<p style="font-size:0.8rem;color:#64748B;font-weight:500;margin-bottom:4px;">'
                'Bi-Encoder Only</p>',
                unsafe_allow_html=True,
            )
            _render_answer(before["answer"])
            with st.expander(f"Sources ({len(before['sources'])})", expanded=False):
                _render_sources(before["sources"])
        with col_right:
            st.markdown(
                '<p style="font-size:0.8rem;color:#64748B;font-weight:500;margin-bottom:4px;">'
                'With Cross-Encoder Reranking</p>',
                unsafe_allow_html=True,
            )
            _render_answer(after["answer"])
            with st.expander(f"Sources ({len(after['sources'])})", expanded=False):
                _render_sources(after["sources"])
    else:
        _render_answer(_r["answer"])
        with st.expander(f"Source Chunks ({len(_r['sources'])})", expanded=True):
            _render_sources(_r["sources"])

    st.markdown('</div>', unsafe_allow_html=True)

else:
    if not (ask and question.strip()):
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-icon">\U0001f4ca</div>'
            '<div class="empty-title">Ask a question to get started</div>'
            '<div class="empty-desc">'
            'Query financial variance drivers from SEC filing MD&A sections '
            'across Chipotle, Darden Restaurants, and Cracker Barrel.'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
