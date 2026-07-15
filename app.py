import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st
from config import config
from llm import LLMClient
from rag import answer_question


@st.cache_resource
def get_llm():
    return LLMClient()

st.set_page_config(
    page_title="RAG Variance Explainer",
    page_icon="\U0001f4ca",
    layout="wide",
)

st.title("RAG Variance Explainer")
st.markdown(
    "Ask a question about financial variance drivers from SEC "
    "filing MD&A sections (CMG, DRI, CBRL)."
)

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
            st.session_state.question_input = q
            st.rerun()

if ask and question.strip():
    ticker = None if ticker_filter == "All" else ticker_filter

    def run_with_progress(fn, label):
        status = st.status(label, expanded=True)
        def on_progress(_phase, msg):
            status.update(label=msg, state="running")
        result = fn(on_progress=on_progress)
        status.update(label="Complete!", state="complete")
        return result

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

    st.rerun()

elif ask and not question.strip():
    st.warning("Please enter a question.")

if "last_result" in st.session_state:
    _r = st.session_state.last_result
    if _r.get("compare"):
        before, after = _r["before"], _r["after"]
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("Before (bi-encoder only)")
            st.markdown(before["answer"])
            with st.expander(f"Sources ({len(before['sources'])})"):
                for i, src in enumerate(before["sources"]):
                    meta = src["metadata"]
                    score = src.get("hybrid_score", src.get("relevance", 0))
                    st.markdown(
                        f"**{i+1}. [{meta['ticker']} {meta['form']} "
                        f"filed {meta['filing_date']}] "
                        f"(score: {score:.2f})**"
                    )
                    st.text(src["text"])
                    if i < len(before["sources"]) - 1:
                        st.divider()
        with col_right:
            st.subheader("After (with cross-encoder)")
            st.markdown(after["answer"])
            with st.expander(f"Sources ({len(after['sources'])})"):
                for i, src in enumerate(after["sources"]):
                    meta = src["metadata"]
                    score = src.get("hybrid_score", src.get("relevance", 0))
                    st.markdown(
                        f"**{i+1}. [{meta['ticker']} {meta['form']} "
                        f"filed {meta['filing_date']}] "
                        f"(score: {score:.2f})**"
                    )
                    st.text(src["text"])
                    if i < len(after["sources"]) - 1:
                        st.divider()
    else:
        st.subheader("Answer")
        st.markdown(_r["answer"])
        with st.expander(f"Source chunks ({len(_r['sources'])})"):
            for i, src in enumerate(_r["sources"]):
                meta = src["metadata"]
                score = src.get("hybrid_score", src.get("relevance", 0))
                st.markdown(
                    f"**{i+1}. [{meta['ticker']} {meta['form']} "
                    f"filed {meta['filing_date']}] "
                    f"(score: {score:.2f})**"
                )
                st.text(src["text"])
                if i < len(_r["sources"]) - 1:
                    st.divider()
