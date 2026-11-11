import logging
import time
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st

from constants import SECTORS, TICKER_OPTIONS
from constants import TICKER_MAP as _TICKER_MAP
from llm import LLMClient
from rag import MAX_QUESTION_LENGTH, answer_question, sanitize_input
from retrieval import get_client, get_collection

logger = logging.getLogger(__name__)

_HTML_ESCAPE_TABLE = str.maketrans({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#x27;"})


def _html_escape(text: str) -> str:
    return str(text).translate(_HTML_ESCAPE_TABLE)


def _sec_filing_url(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = urlparse(value)
        if parsed.scheme == "https" and parsed.hostname == "www.sec.gov" and parsed.path.startswith("/Archives/edgar/data/"):
            return _html_escape(value)
    except ValueError:
        pass
    return None


st.set_page_config(page_title="RAG Variance Explainer", page_icon=":material/analytics:", layout="wide")

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

palette = {
    "dark": {"bg": "#11120f", "surface": "#1c1e19", "raised": "#242720", "rule": "#41443b",
             "text": "#f5f2e9", "secondary": "#c6c8bc", "muted": "#aaaFA1", "gold": "#ead2a0", "gold-soft": "#322e20"},
    "light": {"bg": "#f5f2e9", "surface": "#ffffff", "raised": "#eeeae0", "rule": "#c7c2b7",
              "text": "#20231d", "secondary": "#393e36", "muted": "#555c50", "gold": "#704c1e", "gold-soft": "#ede4d2"},
}[st.session_state.theme]
tokens = "\n".join(f"    --{name}: {value};" for name, value in palette.items())
styles = (Path(__file__).parent / "src" / "styles.css").read_text(encoding="utf-8")
st.markdown(styles.replace("/*__THEME_VARS__*/", tokens), unsafe_allow_html=True)


@st.cache_resource
def get_llm():
    return LLMClient()


@st.cache_data(ttl=120)
def _get_db_stats():
    collection = get_collection(get_client())
    metadata = collection.get(include=["metadatas"])["metadatas"]
    return len(metadata), len({item["accession_number"] for item in metadata if "accession_number" in item})


def _analyze(question: str, ticker: str | None, top_k: int, compare: bool) -> None:
    st.session_state.processing = True
    st.session_state.last_ask_time = time.time()
    st.session_state.pop("last_error", None)
    try:
        with st.status("Retrieving filing evidence", expanded=True) as status:
            st.caption("This can take several minutes. Keep this page open while the model responds.")

            def on_progress(_phase: str, message: str) -> None:
                status.update(label=message, state="running")

            with st.spinner("Analysis in progress", show_time=True):
                if compare:
                    before = answer_question(question, ticker_filter=ticker, top_k=top_k, llm=get_llm(),
                                             on_progress=on_progress, cross_encoder_enabled=False)
                    after = answer_question(question, ticker_filter=ticker, top_k=top_k, llm=get_llm(),
                                            on_progress=on_progress, cross_encoder_enabled=True)
                    st.session_state.last_result = {"compare": True, "before": before, "after": after}
                else:
                    result = answer_question(question, ticker_filter=ticker, top_k=top_k, llm=get_llm(),
                                             on_progress=on_progress)
                    st.session_state.last_result = {"compare": False, **result}
            status.update(label="Analysis complete", state="complete", expanded=False)
    except Exception:
        logger.exception("Analysis failed")
        st.session_state.pop("last_result", None)
        st.session_state.last_error = "Analysis could not finish. Check the local model server and index, then try again."
        status.update(label="Analysis unavailable", state="error", expanded=False)
    finally:
        st.session_state.processing = False


def _render_sources(sources: list[dict]) -> None:
    if not sources:
        st.caption("No filing passages were retrieved for this question.")
        return
    for index, source in enumerate(sources, 1):
        meta = source["metadata"]
        ticker = _html_escape(meta.get("ticker", "Unknown"))
        form = _html_escape(meta.get("form", "Filing"))
        date = _html_escape(meta.get("filing_date", "Date unavailable"))
        sector = _html_escape(SECTORS.get(meta.get("ticker", ""), ""))
        filing_url = _sec_filing_url(meta.get("filing_url"))
        link = (f'<a href="{filing_url}" target="_blank" rel="noopener noreferrer">Open SEC filing ↗</a>'
                if filing_url else "SEC filing link unavailable for this indexed chunk")
        with st.expander(f"{index:02d} · {ticker} · {form} · {date}"):
            st.markdown(
                f'<div class="source-meta">{sector} · {form} · Filed {date}</div>'
                f'<div class="source-body">{_html_escape(source.get("text", ""))}</div>'
                f'<div class="source-link">{link}</div>',
                unsafe_allow_html=True,
            )


def _render_result(result: dict, heading: str = "Research finding") -> None:
    claims = result.get("claims", [])
    checked = result.get("structured") is True and bool(claims) and not result.get("verification_errors")
    st.subheader("No verified finding" if not checked and heading == "Research finding" else heading)
    if result.get("question"):
        st.caption(f'Question analyzed: {result["question"]}')
    if checked:
        st.markdown('<span class="evidence-status">Quote matched in retrieved text</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="evidence-status unverified">No checked quote</span>', unsafe_allow_html=True)
        if result.get("verification_errors"):
            st.warning("The generated claims did not match their cited passages. No sourced finding is shown.")
            for error in result["verification_errors"]:
                st.text(f"Validation: {error}")

    answer = ("I cannot verify the generated claims against the retrieved SEC filing excerpts."
              if result.get("verification_errors") else result["answer"])
    st.markdown(f'<div class="finding-text">{_html_escape(answer)}</div>', unsafe_allow_html=True)
    if checked:
        st.markdown("#### Matched quotations")
        for claim in claims:
            st.caption(f'Source {claim["source_chunk_index"] + 1}')
            st.text(claim["source_quote"])
    st.caption("A quote match confirms text presence in a retrieved passage, not the cause or arithmetic. Check the original filing.")
    st.markdown("#### Filing passages")
    _render_sources(result.get("sources", []))


with st.sidebar:
    st.markdown("**RAG Variance Explainer**")
    view = st.radio("Navigation", ["Ask a Question", "System Analytics"], label_visibility="collapsed")
    st.divider()
    dark = st.toggle("Dark mode", value=st.session_state.theme == "dark", key="theme_toggle")
    if dark != (st.session_state.theme == "dark"):
        st.session_state.theme = "dark" if dark else "light"
        st.rerun()
    st.link_button("Documentation", "https://github.com/redsandr/rag-variance-explainer", width="stretch")
    st.caption("Local research prototype · SEC 10-K / 10-Q")

if view == "System Analytics":
    st.title("Index overview")
    st.caption("Local index coverage. These counts are not measures of answer accuracy.")
    try:
        chunks, filings = _get_db_stats()
    except Exception:
        st.error("Index unavailable. Build or reconnect the SEC index to see its coverage.")
    else:
        one, two, three = st.columns(3)
        one.metric("Indexed companies", len(SECTORS))
        two.metric("SEC filings", filings)
        three.metric("Passages", chunks)
        st.info("Answer quality has not been independently verified on the current index. Review each quote and claim against its original SEC filing.")
        if st.button("Refresh index counts", icon=":material/refresh:"):
            _get_db_stats.clear()
            st.rerun()
else:
    st.title("Ask the filings")
    st.markdown("Ask freely about the indexed SEC filings. Inspect the source passages before relying on an answer.")

    if "question_input" not in st.session_state:
        st.session_state.question_input = ""
    if "processing" not in st.session_state:
        st.session_state.processing = False

    question = st.text_area("Research question", placeholder="Ask anything about the indexed filings…",
                            key="question_input", height=118, max_chars=MAX_QUESTION_LENGTH,
                            disabled=st.session_state.processing)
    with st.expander("Scope and comparison options"):
        first, second = st.columns(2)
        with first:
            ticker_filter = st.selectbox("Company", TICKER_OPTIONS, key="ticker_filter", disabled=st.session_state.processing)
        with second:
            top_k = st.slider("Source passages", 1, 15, 5, key="top_k_slider", disabled=st.session_state.processing)
        compare = st.checkbox("Compare retrieval with and without reranking", key="compare_checkbox",
                              disabled=st.session_state.processing)

    ask = st.button("Analyze filings", type="primary", icon=":material/search:",
                    disabled=st.session_state.processing)
    if ask:
        cleaned = sanitize_input(question.strip())
        if not cleaned:
            st.warning("Enter a question before analyzing filings.")
        elif time.time() - st.session_state.get("last_ask_time", 0) < 10:
            st.warning("Please wait a few seconds before asking another question.")
        else:
            _analyze(cleaned, _TICKER_MAP[ticker_filter], top_k, compare)

    result = st.session_state.get("last_result")
    if result:
        st.divider()
        if result.get("compare"):
            left, right = st.columns(2)
            with left:
                _render_result(result["before"], "Without reranking")
            with right:
                _render_result(result["after"], "With reranking")
        else:
            _render_result(result)
    elif st.session_state.get("last_error"):
        st.error(st.session_state.last_error)
    else:
        st.markdown('<div class="empty-note">Your question and evidence will appear here. Sources must be checked before a finding is trusted.</div>',
                    unsafe_allow_html=True)
