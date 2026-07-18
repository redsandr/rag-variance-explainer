from pathlib import Path

import streamlit as st

from config import config
from llm import LLMClient
from rag import answer_question
from retrieval import get_client, get_collection

st.set_page_config(
    page_title="RAG Variance Explainer",
    page_icon="\U0001f4ca",
    layout="wide",
)

css_path = Path(__file__).parent / "src" / "styles.css"
st.markdown(css_path.read_text(encoding="utf-8"), unsafe_allow_html=True)


@st.cache_resource
def _get_db_stats():
    client = get_client()
    collection = get_collection(client)
    count = collection.count()
    all_meta = collection.get(include=["metadatas"])
    filings = set(m["accession_number"] for m in all_meta["metadatas"] if "accession_number" in m)
    return count, len(filings)


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
    "How did Walmart's e-commerce sales change?",
    "What drove Target's comparable sales?",
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
    "WMT (Walmart)": "WMT",
    "TGT (Target)": "TGT",
}

filter_col, topk_col = st.columns(2)
with filter_col:
    ticker_filter = st.selectbox(
        "Company",
        options=["All", "CMG (Chipotle)", "DRI (Darden)", "CBRL (Cracker Barrel)", "WMT (Walmart)", "TGT (Target)"],
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
             f'across Chipotle, Darden, Cracker Barrel, Walmart, and Target.'
            f'</div></div>',
            unsafe_allow_html=True,
        )

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="right-col">', unsafe_allow_html=True)

try:
    chunk_count, filing_count = _get_db_stats()
except Exception:
    chunk_count, filing_count = 0, 0

st.markdown(
    f'<div class="kpi-panel">'
    f'<div class="panel-title">System Overview</div>'
    f'<div class="kpi-stack">'
    f'<div class="kpi-stack-card">'
    f'<div class="kpi-row-label">Companies</div>'
     f'<div class="kpi-row-value">5</div>'
     f'<div class="kpi-row-sub">CMG &middot; DRI &middot; CBRL &middot; WMT &middot; TGT</div></div>'
    f'<div class="kpi-stack-card">'
    f'<div class="kpi-row-label">Filings Indexed</div>'
    f'<div class="kpi-row-value">{filing_count}</div>'
    f'<div class="kpi-row-sub">10-K &amp; 10-Q combined</div></div>'
    f'<div class="kpi-stack-card">'
    f'<div class="kpi-row-label">Knowledge Base</div>'
    f'<div class="kpi-row-value">{chunk_count}</div>'
    f'<div class="kpi-row-sub">MD&A text chunks</div></div>'
    f'<div class="kpi-stack-card">'
    f'<div class="kpi-row-label">Retrieval MRR</div>'
    f'<div class="kpi-row-value"><span class="purple">0.66</span></div>'
    f'<div class="kpi-row-sub">+28% from baseline</div></div>'
    f'<div class="kpi-stack-card">'
    f'<div class="kpi-row-label">Faithfulness</div>'
f'<div class="kpi-row-value"><span class="green">74.2%</span></div>'
     f'<div class="kpi-row-sub">strict · 75.3% weighted</div></div>'
    f'</div></div>',
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
