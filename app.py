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
    .main-header { margin-bottom: 0.5rem; }
    .source-card {
        background: var(--secondary-background-color);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.75rem;
        border-left: 3px solid var(--primary-color);
    }
    .source-card .meta {
        font-size: 0.85rem;
        color: var(--text-color);
        opacity: 0.75;
        margin-bottom: 0.4rem;
    }
    .source-card .meta strong { color: var(--primary-color); }
    .source-card .text {
        font-family: 'Fira Code', 'Courier New', monospace;
        font-size: 0.8rem;
        line-height: 1.5;
        white-space: pre-wrap;
    }
    .score-high { color: #22c55e; font-weight: 600; }
    .score-mid { color: #eab308; font-weight: 600; }
    .score-low { color: #ef4444; font-weight: 600; }
    .answer-box {
        background: var(--secondary-background-color);
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .answer-box h3 { margin-top: 0; }
</style>
""", unsafe_allow_html=True)

st.title("RAG Variance Explainer")
st.markdown(
    "Ask a question about financial variance drivers from SEC "
    "filing MD&A sections (CMG, DRI, CBRL)."
)


@st.cache_resource
def get_llm():
    return LLMClient()

with st.sidebar:
    st.header("Settings")
    ticker_filter = st.selectbox(
        "Ticker filter",
        options=["All", "CMG", "DRI", "CBRL"],
        index=0,
    )
    top_k = st.slider("Number of source chunks", min_value=1, max_value=15, value=5)
    compare = st.checkbox(
        "Side-by-side: before vs after cross-encoder",
        value=False,
        help="Shows retrieval results without cross-encoder (before) and with (after)",
    )

EXAMPLE_QUESTIONS = [
    "Why did Chipotle's labor costs change?",
    "Why did marketing costs change at Darden?",
    "What drove Chipotle's revenue changes?",
    "How did wage inflation affect Chipotle's labor costs?",
]

if "pending_question" in st.session_state:
    st.session_state.question_input = st.session_state.pop("pending_question")

st.subheader("Your Question")
question = st.text_input(
    "Question",
    placeholder="e.g. Why did Chipotle's labor costs change?",
    label_visibility="collapsed",
    key="question_input",
)

col1, col2 = st.columns([1, 5])
with col1:
    ask = st.button("Ask", type="primary", use_container_width=True)

st.markdown("#### Try:")
cols = st.columns(len(EXAMPLE_QUESTIONS))
for col, q in zip(cols, EXAMPLE_QUESTIONS):
    with col:
        if st.button(q, use_container_width=True, type="tertiary"):
            st.session_state.pending_question = q
            st.rerun()

if ask and question.strip():
    ticker = None if ticker_filter == "All" else ticker_filter

    def run_with_progress(fn, label):
        status = st.status(label, expanded=True)
        def on_progress(_phase, msg):
            status.update(label=msg, state="running")
        try:
            result = fn(on_progress=on_progress)
            status.update(label="Complete!", state="complete")
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
                "Processing",
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
        return "score-high"
    elif score >= 0.4:
        return "score-mid"
    return "score-low"

def _render_sources(sources):
    for i, src in enumerate(sources):
        meta = src["metadata"]
        score = src.get("hybrid_score", src.get("relevance", 0))
        st.markdown(
            f'<div class="source-card">'
            f'<div class="meta"><strong>{meta["ticker"]}</strong> {meta["form"]} '
            f'&middot; filed {meta["filing_date"]} '
            f'&middot; <span class="{_score_class(score)}">score: {score:.2f}</span></div>'
            f'<div class="text">{src["text"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

if "last_result" in st.session_state:
    _r = st.session_state.last_result
    if _r.get("compare"):
        before, after = _r["before"], _r["after"]
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("Before (bi-encoder only)")
            st.markdown(f'<div class="answer-box">{before["answer"]}</div>', unsafe_allow_html=True)
            with st.expander(f"Sources ({len(before['sources'])})"):
                _render_sources(before["sources"])
        with col_right:
            st.subheader("After (with cross-encoder)")
            st.markdown(f'<div class="answer-box">{after["answer"]}</div>', unsafe_allow_html=True)
            with st.expander(f"Sources ({len(after['sources'])})"):
                _render_sources(after["sources"])
    else:
        st.subheader("Answer")
        st.markdown(f'<div class="answer-box">{_r["answer"]}</div>', unsafe_allow_html=True)
        with st.expander(f"Source chunks ({len(_r['sources'])})"):
            _render_sources(_r["sources"])
