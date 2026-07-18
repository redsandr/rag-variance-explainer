import re
import time
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
def _startup_check():
    try:
        client = get_client()
        collection = get_collection(client)
        collection.count()
    except Exception as e:
        st.warning(f"ChromaDB connection issue: {e}. Some features may be unavailable.")
    try:
        get_llm()
    except Exception as e:
        st.warning(f"LLM initialization issue: {e}. Answer generation will fail.")

_startup_check()


@st.cache_resource
def _get_db_stats():
    client = get_client()
    collection = get_collection(client)
    all_meta = collection.get(include=["metadatas"])
    chunk_count = len(all_meta["metadatas"])
    filings = set(m["accession_number"] for m in all_meta["metadatas"] if "accession_number" in m)
    return chunk_count, len(filings)


LOGO_SVG = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>'
    '<line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/>'
    '<line x1="15" y1="21" x2="15" y2="9"/>'
    '</svg>'
)

ANALYTICS_SVG = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>'
    '<line x1="6" y1="20" x2="6" y2="14"/>'
    '</svg>'
)

TARGET_SVG = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/>'
    '<circle cx="12" cy="12" r="2"/>'
    '</svg>'
)

FLASK_SVG = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M9 3h6v5l4 11H5l4-11V3"/>'
    '<line x1="9" y1="3" x2="15" y2="3"/>'
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


SECTOR_MAP = {
    "CMG": "Restaurant",
    "DRI": "Restaurant",
    "CBRL": "Restaurant",
    "WMT": "Retail",
    "TGT": "Retail",
    "JNJ": "Healthcare",
    "XOM": "Energy",
}

MAX_QUESTION_LENGTH = 256
_RATE_LIMIT_SECONDS = 10


def _sanitize_question(raw: str) -> str:
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', raw)
    return cleaned[:MAX_QUESTION_LENGTH]


def _rate_limited() -> str | None:
    last = st.session_state.get("last_ask_time", 0.0)
    elapsed = time.time() - last
    if elapsed < _RATE_LIMIT_SECONDS:
        remaining = int(_RATE_LIMIT_SECONDS - elapsed)
        st.warning(f"Please wait {remaining}s before asking another question.")
        return None
    return "ok"


with st.sidebar:
    view = st.radio(
        "Navigation",
        ["Ask a Question", "System Analytics"],
        index=0,
        label_visibility="collapsed",
    )

with st.sidebar:
    st.divider()
    st.link_button(
        "Documentation \u2197",
        "https://github.com/redsandr/rag-variance-explainer",
        use_container_width=True,
    )

if view == "System Analytics":
    st.markdown('<div class="dashboard-grid">', unsafe_allow_html=True)
    st.markdown('<div class="main-col">', unsafe_allow_html=True)

    chunk_count, filing_count = _get_db_stats()
    st.markdown(
        f'<div class="hero-card">'
        f'<div class="hero-label">{ANALYTICS_SVG} System Analytics</div>'
        f'<div class="kpi-stack">'
        '<div class="kpi-stack-card">'
        '<div class="kpi-row-label">Companies</div>'
        '<div class="kpi-row-value">7</div>'
        '<div class="kpi-row-sub">CMG &middot; DRI &middot; CBRL &middot; WMT &middot; TGT &middot; JNJ &middot; XOM</div>'
        '</div>'
        '<div class="kpi-stack-card">'
        '<div class="kpi-row-label">Sectors</div>'
        '<div class="kpi-row-value">4</div>'
        '<div class="kpi-row-sub">'
        '<span class="sector-badge restaurant">Restaurant</span> '
        '<span class="sector-badge retail">Retail</span> '
        '<span class="sector-badge healthcare">Healthcare</span> '
        '<span class="sector-badge energy">Energy</span>'
        '</div></div>'
        '<div class="kpi-stack-card">'
        '<div class="kpi-row-label">Filings Indexed</div>'
        f'<div class="kpi-row-value">{filing_count}</div>'
        '<div class="kpi-row-sub">10-K &amp; 10-Q combined</div></div>'
        '<div class="kpi-stack-card">'
        '<div class="kpi-row-label">Knowledge Base</div>'
        f'<div class="kpi-row-value">{chunk_count}</div>'
        '<div class="kpi-row-sub">MD&A text chunks</div></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-label">{TARGET_SVG} Retrieval Performance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="kpi-stack">'
        '<div class="kpi-stack-card">'
        '<div class="kpi-row-label">Restaurant MRR</div>'
        '<div class="kpi-row-value"><span class="purple">0.66</span></div>'
        '<div class="kpi-row-sub">+28% from baseline</div></div>'
        '<div class="kpi-stack-card">'
        '<div class="kpi-row-label">Retail recall@10</div>'
        '<div class="kpi-row-value"><span class="green">1.00</span></div>'
        '<div class="kpi-row-sub">WMT &middot; TGT — zero degradation</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-label">{FLASK_SVG} Faithfulness</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="kpi-stack">'
        '<div class="kpi-stack-card">'
        '<div class="kpi-row-label">Restaurant (strict)</div>'
        '<div class="kpi-row-value"><span class="green">74.2%</span></div>'
        '<div class="kpi-row-sub">weighted 75.3%</div></div>'
        '<div class="kpi-stack-card">'
        '<div class="kpi-row-label">Retail (strict)</div>'
        '<div class="kpi-row-value"><span class="green">69.7%</span></div>'
        '<div class="kpi-row-sub">weighted 80.3%</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="right-col">', unsafe_allow_html=True)
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
    st.stop()

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
    processing = st.session_state.get("processing", False)
    ask = st.button(
        "Analyze" if not processing else "Analyzing...",
        type="primary",
        use_container_width=True,
        disabled=processing,
    )

EXAMPLE_QUESTIONS = [
    "Why did Chipotle's labor costs change?",
    "What drove Darden's revenue changes?",
    "How did wage inflation affect Chipotle?",
    "Why did CBRL's operating costs change?",
    "How did Walmart's e-commerce sales change?",
    "What drove Target's comparable sales?",
    "How did Johnson & Johnson's pharmaceutical revenue perform?",
    "What drove Exxon's upstream earnings changes?",
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
    "JNJ (Johnson & Johnson)": "JNJ",
    "XOM (Exxon Mobil)": "XOM",
}

filter_col, topk_col = st.columns(2)
with filter_col:
    ticker_filter = st.selectbox(
        "Company",
        options=[
            "All", "CMG (Chipotle)", "DRI (Darden)", "CBRL (Cracker Barrel)",
            "WMT (Walmart)", "TGT (Target)", "JNJ (Johnson & Johnson)", "XOM (Exxon Mobil)",
        ],
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

if ask and question.strip() and not st.session_state.get("processing", False):
    question = _sanitize_question(question)
    if not question:
        st.warning("Question is empty after sanitization.")
    elif _rate_limited() is None:
        pass
    else:
        st.session_state.processing = True
        st.session_state.last_ask_time = time.time()
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
                with_ce = config.cross_encoder_enabled
                config.cross_encoder_enabled = False
                try:
                    before = run_with_progress(
                        lambda on_progress: answer_question(
                            question, ticker_filter=ticker, top_k=top_k, llm=get_llm(),
                            on_progress=on_progress),
                        "Without cross-encoder",
                    )
                finally:
                    config.cross_encoder_enabled = True
                after = run_with_progress(
                    lambda on_progress: answer_question(
                        question, ticker_filter=ticker, top_k=top_k, llm=get_llm(),
                        on_progress=on_progress),
                    "With cross-encoder",
                )
                config.cross_encoder_enabled = with_ce
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
        finally:
            st.session_state.processing = False
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

def _sector_tag(ticker: str) -> str:
    sector = SECTOR_MAP.get(ticker, "")
    css_class = sector.lower() if sector else ""
    return f'<span class="sector-tag {css_class}">{sector}</span>'

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
            f'{_sector_tag(meta["ticker"])}'
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
            '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#6B7280" '
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
    else:
        pass

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="right-col">', unsafe_allow_html=True)

try:
    chunk_count, filing_count = _get_db_stats()
except Exception:
    chunk_count, filing_count = 0, 0

refresh = st.button("Refresh Stats", key="refresh_kpi", use_container_width=True)
if refresh:
    st.cache_resource.clear()
    st.rerun()

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
    f'</div></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="kpi-panel">'
    '<div class="panel-title">Retrieval</div>'
    '<div class="kpi-stack">'
    '<div class="kpi-stack-card">'
    '<div class="kpi-row-label">Restaurant MRR</div>'
    '<div class="kpi-row-value"><span class="purple">0.66</span></div>'
    '<div class="kpi-row-sub">+28% from baseline</div></div>'
    '<div class="kpi-stack-card">'
    '<div class="kpi-row-label">Retail recall@10</div>'
    '<div class="kpi-row-value"><span class="green">1.00</span></div>'
    '<div class="kpi-row-sub">WMT &middot; TGT</div></div>'
    '</div></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="kpi-panel">'
    '<div class="panel-title">Faithfulness</div>'
    '<div class="kpi-stack">'
    '<div class="kpi-stack-card">'
    '<div class="kpi-row-label">Restaurant</div>'
    '<div class="kpi-row-value"><span class="green">74.2%</span> <span class="kpi-row-sub">strict</span></div>'
    '<div class="kpi-row-sub">weighted 75.3%</div></div>'
    '<div class="kpi-stack-card">'
    '<div class="kpi-row-label">Retail</div>'
    '<div class="kpi-row-value"><span class="green">69.7%</span> <span class="kpi-row-sub">strict</span></div>'
    '<div class="kpi-row-sub">weighted 80.3%</div></div>'
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
