import time
from pathlib import Path

import streamlit as st

from config import config
from llm import LLMClient
from rag import answer_question, sanitize_input
from retrieval import get_client, get_collection

st.set_page_config(
    page_title="RAG Variance Explainer",
    page_icon="\U0001f4ca",
    layout="wide",
)

# Same palette as the marketing site's globals.css (:root / [data-theme='dark']),
# so the app and the landing page read as one product.
THEME_VARS = {
    "light": {
        "bg": "#FBF9F4", "bg-mist": "#F6EDD3", "surface": "#FFFFFF", "surface-alt": "#FAF6EC",
        "border": "#EBE2CB", "border-strong": "#DCCE9F",
        "accent": "#A9860F", "accent-dark": "#8A6D0C", "accent-light": "#C9A227", "accent-soft": "#F6EDD3",
        "green": "#1FAE73", "green-soft": "#E6F7EF",
        "amber": "#A9860F", "amber-soft": "#F6EDD3",
        "red": "#C1443D", "red-soft": "#FBEAE8",
        "blue": "#3B6FA0", "blue-soft": "#EAF1F8",
        "terracotta": "#B5622E", "terracotta-soft": "#FBEDE3",
        "text": "#22201A", "text-dim": "#62594A", "text-mute": "#93876E",
        "btn-text-on-accent": "#FFFFFF",
        "shadow-lg": "0 4px 20px rgba(27, 24, 48, 0.08)",
        "shadow-md": "0 4px 16px rgba(27, 24, 48, 0.06)",
        "icon-glow": "0 0 20px rgba(169, 134, 15, 0.2)",
        "accent-glow-hover": "0 0 20px rgba(169, 134, 15, 0.12), 0 0 40px rgba(169, 134, 15, 0.06)",
        "accent-glow-sm": "0 0 20px rgba(169, 134, 15, 0.08)",
        "btn-glow": "0 2px 12px rgba(169, 134, 15, 0.25)",
        "btn-glow-hover": "0 6px 20px rgba(169, 134, 15, 0.35)",
        "focus-ring": "0 0 0 3px rgba(169, 134, 15, 0.15)",
    },
    "dark": {
        "bg": "#0B0B0A", "bg-mist": "#12110D", "surface": "#151412", "surface-alt": "#1B1916",
        "border": "#2A2620", "border-strong": "#3A3527",
        "accent": "#C9A227", "accent-dark": "#A9860F", "accent-light": "#E8C766", "accent-soft": "#2B240F",
        "green": "#3DDC97", "green-soft": "#10251A",
        "amber": "#E8C766", "amber-soft": "#2B240F",
        "red": "#FF6B61", "red-soft": "#2B1512",
        "blue": "#7FB2E0", "blue-soft": "#101A24",
        "terracotta": "#D97F4A", "terracotta-soft": "#2B1B10",
        "text": "#F3EFE6", "text-dim": "#B8B0A0", "text-mute": "#7A7364",
        "btn-text-on-accent": "#101208",
        "shadow-lg": "0 4px 24px rgba(0, 0, 0, 0.3)",
        "shadow-md": "0 4px 20px rgba(0, 0, 0, 0.2)",
        "icon-glow": "0 0 24px rgba(201, 162, 39, 0.2)",
        "accent-glow-hover": "0 0 24px rgba(201, 162, 39, 0.12), 0 0 48px rgba(201, 162, 39, 0.06)",
        "accent-glow-sm": "0 0 24px rgba(201, 162, 39, 0.08)",
        "btn-glow": "0 0 20px rgba(201, 162, 39, 0.2)",
        "btn-glow-hover": "0 0 30px rgba(201, 162, 39, 0.3)",
        "focus-ring": "0 0 0 3px rgba(201, 162, 39, 0.15)",
    },
}

if "theme" not in st.session_state:
    st.session_state.theme = "dark"


def _render_css(theme: str) -> str:
    vars_css = "\n".join(f"        --{k}: {v};" for k, v in THEME_VARS[theme].items())
    css_path = Path(__file__).parent / "src" / "styles.css"
    return css_path.read_text(encoding="utf-8").replace("/*__THEME_VARS__*/", vars_css)


st.markdown(_render_css(st.session_state.theme), unsafe_allow_html=True)


@st.cache_resource
def get_llm():
    return LLMClient()


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


SECTOR_MAP = {
    "CMG": "Restaurant",
    "DRI": "Restaurant",
    "CBRL": "Restaurant",
    "WMT": "Retail",
    "TGT": "Retail",
    "JNJ": "Healthcare",
    "XOM": "Energy",
}

_RATE_LIMIT_SECONDS = 10


def _rate_limited() -> str | None:
    last = st.session_state.get("last_ask_time", 0.0)
    elapsed = time.time() - last
    if elapsed < _RATE_LIMIT_SECONDS:
        remaining = int(_RATE_LIMIT_SECONDS - elapsed)
        st.warning(f"Please wait {remaining}s before asking another question.")
        return None
    return "ok"


@st.fragment
def run_analysis(question_text, ticker, top_k, compare_mode):
    st.session_state.processing = True
    st.session_state.last_ask_time = time.time()

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
        if compare_mode:
            with_ce = config.cross_encoder_enabled
            config.cross_encoder_enabled = False
            try:
                before = run_with_progress(
                    lambda on_progress: answer_question(
                        question_text, ticker_filter=ticker, top_k=top_k, llm=get_llm(),
                        on_progress=on_progress),
                    "Without cross-encoder",
                )
            finally:
                config.cross_encoder_enabled = True
            after = run_with_progress(
                lambda on_progress: answer_question(
                    question_text, ticker_filter=ticker, top_k=top_k, llm=get_llm(),
                    on_progress=on_progress),
                "With cross-encoder",
            )
            config.cross_encoder_enabled = with_ce
            st.session_state.last_result = {"compare": True, "before": before, "after": after}
        else:
            result = run_with_progress(
                lambda on_progress: answer_question(
                    question_text, ticker_filter=ticker, top_k=top_k, llm=get_llm(),
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
    is_dark = st.toggle(
        "Dark mode",
        value=(st.session_state.theme == "dark"),
        key="theme_toggle",
    )
    new_theme = "dark" if is_dark else "light"
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

if view == "System Analytics":
    chunk_count, filing_count = _get_db_stats()

    main_col, right_col = st.columns([3, 1])
    with main_col:
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
        st.markdown(
            '<div class="hero-card">'
            f'<div class="hero-label">{FLASK_SVG} Answer Quality</div>'
            '<div class="kpi-stack">'
            '<div class="kpi-stack-card">'
            '<div class="kpi-row-label">Restaurant answers, source-backed</div>'
            '<div class="kpi-row-value"><span class="green">74.2%</span></div>'
            '<div class="kpi-row-sub">weighted 75.3%</div></div>'
            '<div class="kpi-stack-card">'
            '<div class="kpi-row-label">Retail answers, source-backed</div>'
            '<div class="kpi-row-value"><span class="green">69.7%</span></div>'
            '<div class="kpi-row-sub">weighted 80.3%</div></div>'
            '</div></div>',
            unsafe_allow_html=True,
        )
        with st.expander("Technical details \u2013 retrieval metrics"):
            st.markdown(
                '<div class="kpi-stack">'
                '<div class="kpi-stack-card">'
                '<div class="kpi-row-label">Restaurant MRR</div>'
                '<div class="kpi-row-value"><span class="accent">0.66</span></div>'
                '<div class="kpi-row-sub">+28% from baseline</div></div>'
                '<div class="kpi-stack-card">'
                '<div class="kpi-row-label">Retail recall@10</div>'
                '<div class="kpi-row-value"><span class="green">1.00</span></div>'
                '<div class="kpi-row-sub">WMT &middot; TGT — zero degradation</div></div>'
                '</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                "Hybrid retrieval (BM25 + embeddings) with cross-encoder re-ranking, "
                "evaluated per sector against a held-out question set."
            )

    with right_col:
        st.markdown(
            '<div class="about-card">'
            '<div class="about-title">About</div>'
            '<div class="about-text">'
            'Turns SEC filings into plain-language, sourced answers about why a '
            "company's numbers moved — every answer links back to the exact "
            'filing text it came from.'
            '</div></div>',
            unsafe_allow_html=True,
        )
        with st.expander("Technical details"):
            st.caption(
                "Hybrid retrieval (BM25 + embeddings) over indexed MD&A sections "
                "from SEC EDGAR 10-K/10-Q filings, with cross-encoder re-ranking "
                "and configurable top-k."
            )

    st.stop()

main_col, right_col = st.columns([3, 1])

with main_col:
    SEARCH_SVG = (
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>'
        '</svg>'
    )

    st.markdown(
        f'<div class="hero-label">{SEARCH_SVG} Ask a Question</div>',
        unsafe_allow_html=True,
    )

    pending_question = st.session_state.pop("pending_question", None)
    auto_ask = st.session_state.pop("auto_ask", False)

    if pending_question:
        st.session_state.question_input = pending_question

    processing = st.session_state.get("processing", False)

    EXAMPLE_QUESTIONS = {
        "Revenue": [
            "What drove Darden's revenue changes?",
            "How did Walmart's e-commerce sales change?",
            "What drove Target's comparable sales?",
            "How did Johnson & Johnson's pharmaceutical revenue perform?",
        ],
        "Labor": [
            "Why did Chipotle's labor costs change?",
            "How did wage inflation affect Chipotle?",
        ],
        "Margin": [
            "Why did CBRL's operating costs change?",
            "What drove Exxon's upstream earnings changes?",
        ],
    }

    st.markdown('<span class="hint">Try a question:</span>', unsafe_allow_html=True)
    for category, questions in EXAMPLE_QUESTIONS.items():
        st.markdown(f'<span class="category-label">{category}</span>', unsafe_allow_html=True)
        cols = st.columns(len(questions))
        for i, q in enumerate(questions):
            with cols[i]:
                if st.button(q, key=f"ex_{q[:20]}", use_container_width=True, type="secondary",
                             disabled=processing):
                    st.session_state.pending_question = q
                    st.session_state.auto_ask = True
                    st.session_state._saved_compare = st.session_state.get("compare_checkbox", False)
                    st.session_state._saved_topk = st.session_state.get("top_k_slider", 5)
                    st.session_state._saved_ticker = st.session_state.get("ticker_filter", "All")
                    st.rerun()

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
            disabled=processing,
            key="ticker_filter",
        )
    with topk_col:
        top_k = st.slider(
            "Source chunks",
            min_value=1, max_value=15, value=5,
            help="Number of retrieved chunks to include",
            disabled=processing,
            key="top_k_slider",
        )

    compare = st.checkbox(
        "Side-by-side: with vs without cross-encoder",
        value=False,
        help="Compare retrieval with and without cross-encoder re-ranking",
        disabled=processing,
        key="compare_checkbox",
    )

    with st.form("ask_form"):
        col_q, col_btn = st.columns([5, 1])
        with col_q:
            question = st.text_input(
                "Question",
                placeholder="e.g. Why did Chipotle's labor costs change?",
                label_visibility="collapsed",
                key="question_input",
            )
        with col_btn:
            ask = st.form_submit_button(
                "Analyze" if not processing else "Analyzing...",
                use_container_width=True,
                disabled=processing,
            ) or auto_ask

    if auto_ask:
        compare = st.session_state.pop("_saved_compare", compare)
        top_k = st.session_state.pop("_saved_topk", top_k)
        ticker_filter = st.session_state.pop("_saved_ticker", ticker_filter)

    if ask and question.strip() and not processing:
        question = sanitize_input(question)
        if not question:
            st.warning("Question is empty after sanitization.")
        elif _rate_limited() is None:
            pass
        else:
            run_analysis(question, ticker_map[ticker_filter], top_k, compare)

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
        if not question.strip():
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
                 'Ask about revenue, labor, or margin drivers — sourced from SEC '
                 'EDGAR filings for Chipotle, Darden, Cracker Barrel, Walmart, '
                 'Target, Johnson & Johnson, and Exxon Mobil.'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        else:
            pass

    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
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
         f'<div class="kpi-row-value">7</div>'
         f'<div class="kpi-row-sub">CMG &middot; DRI &middot; CBRL &middot; WMT &middot; TGT &middot; JNJ &middot; XOM</div></div>'
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
        '<div class="panel-title">Answer Quality</div>'
        '<div class="kpi-stack">'
        '<div class="kpi-stack-card">'
        '<div class="kpi-row-label">Restaurant, source-backed</div>'
        '<div class="kpi-row-value"><span class="green">74.2%</span></div>'
        '<div class="kpi-row-sub">weighted 75.3%</div></div>'
        '<div class="kpi-stack-card">'
        '<div class="kpi-row-label">Retail, source-backed</div>'
        '<div class="kpi-row-value"><span class="green">69.7%</span></div>'
        '<div class="kpi-row-sub">weighted 80.3%</div></div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    with st.expander("Technical details \u2013 retrieval metrics"):
        st.markdown(
            '<div class="kpi-stack">'
            '<div class="kpi-stack-card">'
            '<div class="kpi-row-label">Restaurant MRR</div>'
            '<div class="kpi-row-value"><span class="accent">0.66</span></div>'
            '<div class="kpi-row-sub">+28% from baseline</div></div>'
            '<div class="kpi-stack-card">'
            '<div class="kpi-row-label">Retail recall@10</div>'
            '<div class="kpi-row-value"><span class="green">1.00</span></div>'
            '<div class="kpi-row-sub">WMT &middot; TGT</div></div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Hybrid retrieval (BM25 + embeddings) with cross-encoder re-ranking, "
            "evaluated per sector against a held-out question set."
        )

    st.markdown(
        '<div class="about-card">'
        '<div class="about-title">About</div>'
        '<div class="about-text">'
        'Turns SEC filings into plain-language, sourced answers about why a '
        "company's numbers moved — every answer links back to the exact "
        'filing text it came from.'
        '</div></div>',
        unsafe_allow_html=True,
    )
    with st.expander("Technical details"):
        st.caption(
            "Hybrid retrieval (BM25 + embeddings) over indexed MD&A sections "
            "from SEC EDGAR 10-K/10-Q filings, with cross-encoder re-ranking "
            "and configurable top-k."
        )